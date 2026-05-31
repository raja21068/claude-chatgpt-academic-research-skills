"""
rewrite_runner.py  (v6)
=======================
Applies safe automatic rewrites to academic paper text.

v6 CHANGES vs v5:
  - Removed rewrite_zombie_noun()   — was cutting sentence content via regex groups
  - Removed rewrite_passive()       — was cutting sentence content via regex groups
  - Removed rewrite_context_free()  — was injecting [BASELINE] placeholder text
  - Added humanize_text() as first pass — 30+ safe phrase-level substitutions
  - Simplified extract_issues() — only uses safe rewrite targets
  - rewrite_paper() is now the clear single entry point

DESIGN RULE: Only phrase-level substitutions are applied automatically.
             Anything requiring sentence restructuring is flagged for manual review.
"""

import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from slop_lib import analyse, load_banned_phrases, load_exceptions, humanize_text
from slop_lib.constants import HEDGE_WORDS
from slop_lib.config import get_threshold
from slop_lib.humanizer import count_autofix_hits


# ─────────────────────────────────────────────────────────────────────────────
# TEXT HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def normalise(text: str) -> str:
    """Join hard line breaks that split sentences mid-way (common in PDFs)."""
    lines = text.splitlines()
    joined = []
    for line in lines:
        line = line.strip()
        if not line:
            joined.append("")
            continue
        if joined and joined[-1] and not re.search(r'[.!?:]\s*$', joined[-1]):
            joined[-1] = joined[-1] + " " + line
        else:
            joined.append(line)
    return "\n".join(joined)


def split_sentences(text: str) -> list:
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if len(s.strip()) > 20]


# ─────────────────────────────────────────────────────────────────────────────
# SAFE REWRITE RULES
# (phrase-level only — no group capturing, no sentence reconstruction)
# ─────────────────────────────────────────────────────────────────────────────

_HEDGE_RE = re.compile(
    r'\b(' + '|'.join(re.escape(h) for h in sorted(HEDGE_WORDS, key=len, reverse=True)) + r')\b',
    re.IGNORECASE,
)

def rewrite_hedge_stack(sentence: str) -> str:
    """
    When a sentence has ≥3 hedge words, remove all but the first.
    Safe: only removes words, never restructures.
    """
    matches = list(_HEDGE_RE.finditer(sentence))
    if len(matches) < 2:
        return ""
    result = sentence
    for m in reversed(matches[1:]):
        result = result[:m.start()] + result[m.end():]
    result = re.sub(r'\s{2,}', ' ', result).strip()
    if result and result[0].islower():
        result = result[0].upper() + result[1:]
    return result


_ACADEMIC_FILLERS = [
    (r'\bNotably,?\s+',                         ''),
    (r'\bInterestingly,?\s+',                   ''),
    (r'\bImportantly,?\s+',                     ''),
    (r'\bThe results clearly show that\b',      'Results show that'),
    (r'\bIn this (?:paper|work),\s*we (?:propose|present|introduce|describe)\b', 'We'),
    (r'\bThis (?:paper|work) (?:presents?|proposes?|introduces?|investigates?)\b', ''),
    (r'\bIn this section,\s*we (?:describe|present|introduce)\b', ''),
    (r'\bWe now present our method\b',          ''),
]

_COMPILED_ACADEMIC = [
    (re.compile(p, re.IGNORECASE), r) for p, r in _ACADEMIC_FILLERS
]

def rewrite_academic_phrase(sentence: str) -> str:
    """Remove academic filler openers. Safe: only removes prefixes."""
    for pattern, replacement in _COMPILED_ACADEMIC:
        if pattern.search(sentence):
            r = pattern.sub(replacement, sentence)
            r = re.sub(r'\s{2,}', ' ', r).strip().lstrip(",; ")
            if r and r[0].islower():
                r = r[0].upper() + r[1:]
            if r and r != sentence:
                return r
    return ""


# ─────────────────────────────────────────────────────────────────────────────
# ISSUE EXTRACTOR  (v6: only extracts issues with safe rewrites)
# ─────────────────────────────────────────────────────────────────────────────

def extract_issues(report, text: str) -> list:
    """
    Extract sentences that have a known safe rewrite.
    Only includes: hedge stacks and academic filler openers.
    (Zombie noun / passive / context-free rewrites removed in v6 — they cut content.)
    """
    sentences = split_sentences(text)
    issues, seen = [], set()

    def add(flag, sent, extra=None):
        key = sent[:80]
        if key not in seen and sent:
            seen.add(key)
            issues.append({"flag": flag, "sentence": sent, "extra": extra})

    r = report.rhythm

    # Hedge stacks (≥2 hedge words)
    for h in r.hedge_sentences[:6]:
        add("hedge_stack", h["sentence"].strip(), h["hedge_count"])

    # Academic filler phrases
    for label, hits in report.phrase_hits.items():
        if label == "academic":
            for phrase in hits[:6]:
                for s in sentences:
                    if phrase.lower() in s.lower():
                        add("academic_phrase", s, phrase)
                        break

    return issues


def best_rewrite(issue: dict) -> str:
    flag, sent, extra = issue["flag"], issue["sentence"], issue.get("extra")
    if flag == "hedge_stack":     return rewrite_hedge_stack(sent)
    if flag == "academic_phrase": return rewrite_academic_phrase(sent)
    return ""


# ─────────────────────────────────────────────────────────────────────────────
# MAIN FUNCTION
# ─────────────────────────────────────────────────────────────────────────────

def rewrite_paper(raw_text: str) -> tuple:
    """
    Rewrite a paper in two passes:

    Pass 1 — Humanizer (whole-document phrase substitutions):
        Removes filler openers, chatbot artifacts, compresses filler phrases,
        fixes copula avoidance, removes em dash overuse. Safe by design.

    Pass 2 — Sentence-level rewrites (safe rewrites only):
        Removes hedge stacks and academic filler openers from individual sentences.

    Returns: (rewritten_text, n_changed, n_total_issues, score_before, score_after)
    """
    text = normalise(raw_text)

    # ── Pass 1: Humanizer ──────────────────────────────────────────────────
    hits_before = count_autofix_hits(text)
    text        = humanize_text(text)
    hits_after  = count_autofix_hits(text)
    humanizer_fixed = hits_before - hits_after

    # ── Score before sentence rewrites ────────────────────────────────────
    threshold = get_threshold()
    report    = analyse(
        text,
        banned     = load_banned_phrases(),
        exceptions = load_exceptions(),
        threshold  = threshold,
    )
    score_after_pass1 = report.score

    # ── Pass 2: Sentence-level rewrites ───────────────────────────────────
    issues  = extract_issues(report, text)
    changed = humanizer_fixed

    for issue in issues:
        rw = best_rewrite(issue)
        if rw and rw != issue["sentence"]:
            text    = text.replace(issue["sentence"], rw, 1)
            changed += 1

    # ── Final score ───────────────────────────────────────────────────────
    final_report = analyse(
        text,
        banned     = load_banned_phrases(),
        exceptions = load_exceptions(),
        threshold  = threshold,
    )

    return text, changed, len(issues) + hits_before, score_after_pass1, final_report.score


# ─────────────────────────────────────────────────────────────────────────────
# COMMAND-LINE USE
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python rewrite_runner.py input/my_paper.txt")
        sys.exit(1)

    p = Path(sys.argv[1])
    if not p.exists():
        p = HERE / "input" / sys.argv[1]
    if not p.exists():
        sys.exit(f"File not found: {sys.argv[1]}")

    raw = p.read_text(encoding="utf-8", errors="replace")
    if p.suffix.lower() == ".tex":
        from slop_lib.text import strip_latex
        raw = strip_latex(raw)

    rewritten, changed, total, score_p1, score_final = rewrite_paper(raw)

    out_dir = HERE / "output"
    out_dir.mkdir(exist_ok=True)
    out = out_dir / f"{p.stem}_rewritten.txt"
    out.write_text(rewritten, encoding="utf-8")

    print(f"\n  Score after humanizer pass : {score_p1}/100")
    print(f"  Score after sentence pass  : {score_final}/100")
    print(f"  Total changes applied      : {changed} ({total} patterns found)")
    print(f"  Saved  : output/{out.name}\n")
