"""
rewrite_runner.py  —  Rule-based rewriter for paper-writing-agent v5
=====================================================================
Drop this file into the root of paper-writing-agent-v5-final/.

Usage:
    python rewrite_runner.py input/my_paper.txt
    python rewrite_runner.py input/my_paper.tex

What it does:
    1. Runs the existing analyse() — same as run.py check
    2. For every flagged sentence, generates 2-3 rewrite suggestions
       using pure Python rule-based logic (no API, no internet)
    3. Writes output/<paper>_rewrites.txt

No new dependencies — uses only slop_lib which is already installed.
"""

import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from slop_lib import analyse, load_banned_phrases, load_exceptions, get_threshold
from slop_lib.constants import ZOMBIE_NOUNS, HEDGE_WORDS

OUTPUT_DIR = HERE / "output"


# ─────────────────────────────────────────────────────────────────────────────
# TEXT NORMALISER
# Academic PDFs have hard line breaks mid-sentence. Join them before analysis.
# ─────────────────────────────────────────────────────────────────────────────

def normalise(text: str) -> str:
    # Join lines that are broken mid-sentence (no sentence-ending punctuation)
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


def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if len(s.strip()) > 20]


# ─────────────────────────────────────────────────────────────────────────────
# REWRITE RULES
# ─────────────────────────────────────────────────────────────────────────────

# ── 1. Zombie noun ────────────────────────────────────────────────────────────

_ZOMBIE_PHRASE = re.compile(
    r'\b(?:the|a|an|our|their)\s+(' +
    '|'.join(re.escape(z) for z in sorted(ZOMBIE_NOUNS, key=len, reverse=True)) +
    r')\s+of\s+([^,.;]+)',
    re.IGNORECASE,
)
_ZOMBIE_BARE = re.compile(
    r'\b(?:the|a|an)\s+(' +
    '|'.join(re.escape(z) for z in sorted(ZOMBIE_NOUNS, key=len, reverse=True)) +
    r')\b',
    re.IGNORECASE,
)

def rewrite_zombie_noun(sentence: str) -> list[str]:
    rewrites = []

    m = _ZOMBIE_PHRASE.search(sentence)
    if m:
        zombie = m.group(1).lower()
        verb   = ZOMBIE_NOUNS.get(zombie, zombie)
        obj    = m.group(2).strip().rstrip(".,; ")

        a = _ZOMBIE_PHRASE.sub(f"we {verb} {obj}", sentence, count=1)
        a = re.sub(r'\s+', ' ', a).strip()
        a = a[0].upper() + a[1:]

        b = _ZOMBIE_PHRASE.sub(f"{verb}ing {obj}", sentence, count=1)
        b = re.sub(r'\s+', ' ', b).strip()
        b = b[0].upper() + b[1:]

        for r in [a, b]:
            if r != sentence:
                rewrites.append(r)
        return rewrites[:2]

    m2 = _ZOMBIE_BARE.search(sentence)
    if m2:
        zombie = m2.group(1).lower()
        verb   = ZOMBIE_NOUNS.get(zombie, zombie)
        a = _ZOMBIE_BARE.sub(verb + "ing", sentence, count=1)
        a = re.sub(r'\s+', ' ', a).strip()
        a = a[0].upper() + a[1:]
        if a != sentence:
            rewrites.append(a)

    return rewrites


# ── 2. Hedge stacking ─────────────────────────────────────────────────────────

_HEDGE_RE = re.compile(
    r'\b(' + '|'.join(re.escape(h) for h in sorted(HEDGE_WORDS, key=len, reverse=True)) + r')\b',
    re.IGNORECASE,
)

def rewrite_hedge_stack(sentence: str) -> list[str]:
    matches = list(_HEDGE_RE.finditer(sentence))
    if len(matches) < 2:
        return []

    # Rewrite A: keep only first hedge, delete the rest
    result_a = sentence
    for m in reversed(matches[1:]):
        result_a = result_a[:m.start()] + result_a[m.end():]
    result_a = re.sub(r'\s{2,}', ' ', result_a).strip()
    result_a = result_a[0].upper() + result_a[1:]

    # Rewrite B: remove all hedges, state claim directly
    result_b = _HEDGE_RE.sub("", sentence)
    result_b = re.sub(r'\s{2,}', ' ', result_b).strip()
    result_b = result_b[0].upper() + result_b[1:]

    rewrites = []
    for r in [result_a, result_b]:
        if r and r != sentence:
            rewrites.append(r)
    return rewrites[:2]


# ── 3. Passive voice ──────────────────────────────────────────────────────────
# Strategy: use the past participle as-is — already the correct past tense form.
# "X was evaluated"   → "We evaluated X"
# "X was found by Y"  → "Y found X"
# No verb reconstruction needed.

_PASSIVE_BY = re.compile(
    r'^(.+?)\s+(?:was|were)\s+(\w+(?:ed|en|wn|lt|ght|nt))\s+by\s+(.+?)([,;.].*)?$',
    re.IGNORECASE,
)
_PASSIVE_SIMPLE = re.compile(
    r'^(.+?)\s+(was|were)\s+(\w+(?:ed|en|wn|lt|ght|nt))(.*)',
    re.IGNORECASE,
)

def rewrite_passive(sentence: str) -> list[str]:
    rewrites = []

    # "X was Yed by Z" → "Z Yed X"
    m = _PASSIVE_BY.match(sentence.strip())
    if m:
        subj  = m.group(1).strip()
        pp    = m.group(2)           # past participle — use directly
        agent = m.group(3).strip().rstrip(".,; ")
        tail  = (m.group(4) or "").strip()
        a = f"{agent.capitalize()} {pp} {subj.lower()}{' ' + tail if tail else ''}."
        a = re.sub(r'\s+', ' ', a)
        rewrites.append(a)
        return rewrites

    # "X was Yed [rest]" → "We Yed X [rest]"
    m2 = _PASSIVE_SIMPLE.match(sentence.strip())
    if m2:
        subj = m2.group(1).strip()
        pp   = m2.group(3)
        tail = m2.group(4).strip()

        a = f"We {pp} {subj.lower()}{' ' + tail if tail else ''}."
        a = re.sub(r'\s+', ' ', a)
        rewrites.append(a)

        # Alternative: flip subject to front, active form
        if tail:
            b = f"{subj.capitalize()} {pp}{' ' + tail}."
            b = re.sub(r'\s+', ' ', b)
            if b != sentence:
                rewrites.append(b)

    return rewrites[:2]


# ── 4. Context-free comparison ────────────────────────────────────────────────

_COMPARISON_RE = re.compile(
    r'\b(outperforms?|surpasses?|exceeds?|beats?|better than|superior to|'
    r'improves? (?:over|upon)|achieves? (?:better|higher|lower))\b',
    re.IGNORECASE,
)

def rewrite_context_free(sentence: str) -> list[str]:
    if not _COMPARISON_RE.search(sentence):
        return []
    m = _COMPARISON_RE.search(sentence)
    insert = " [BASELINE] by [N] on [DATASET]"
    a = sentence[:m.end()] + insert + sentence[m.end():]
    b = sentence.rstrip(".") + " ([METRIC]: [OUR_SCORE] vs [BASELINE_SCORE], Table [X])."
    return [r for r in [a, b] if r != sentence]


# ── 5. Academic filler phrases ────────────────────────────────────────────────

_FILLERS = [
    # (pattern, replacement)  — replacement="" means delete the phrase entirely
    (r'\bIt is worth noting that\b',            ""),
    (r'\bIt is important to note that\b',       ""),
    (r'\bWe note that\b',                       ""),
    (r'\bNotably,?\s+',                         ""),
    (r'\bInterestingly,?\s+',                   ""),
    (r'\bImportantly,?\s+',                     ""),
    (r'\bIt can be observed that\b',            ""),
    (r'\bFrom the results,?\s+it is clear that\b', ""),
    (r'\bThe results clearly show that\b',      "Results show that"),
    (r'\bAs can be seen from\b',                ""),
    (r'\bWe can see that\b',                    ""),
    (r'\bOne can observe that\b',               ""),
    (r'\bIn this (?:paper|work),\s*we (?:propose|present|introduce|describe)\b', "We"),
    (r'\bThis (?:paper|work) (?:presents?|proposes?|introduces?|investigates?)\b', ""),
    (r'\bTo the best of our knowledge,?\s*',    ""),
    (r'\bAs far as we are aware,?\s*',          ""),
    (r'\bWe believe that\b',                    ""),
    (r'\bstate-of-the-art (?:results?|performance)\b', "best reported [METRIC] on [DATASET]"),
    (r'\bsignificant improvement\b',            "[N]-point improvement on [BENCHMARK]"),
    (r'\bextensive experiments?\b',             "experiments on [N] benchmarks"),
    (r'\bcomprehensive evaluation\b',           "evaluation across [N] datasets"),
    (r'\bpromising results?\b',                 "[METRIC] of [SCORE] on [DATASET]"),
    (r'\bstrong performance\b',                 "[METRIC]: [SCORE] on [DATASET]"),
    (r'\bsuperior performance\b',               "[MARGIN]-point improvement over [BASELINE]"),
    (r'\bIn this section,\s*we (?:describe|present|introduce)\b', ""),
    (r'\bWe now present our method\b',          ""),
    (r'\bIn (?:this|the) (?:conclusion|summary),\s*we have\b', ""),
]

def rewrite_academic_phrase(sentence: str) -> list[str]:
    rewrites = []
    for pattern, replacement in _FILLERS:
        if re.search(pattern, sentence, re.IGNORECASE):
            a = re.sub(pattern, replacement, sentence, flags=re.IGNORECASE)
            a = re.sub(r'\s{2,}', ' ', a).strip().lstrip(",; ")
            if a and a[0].islower():
                a = a[0].upper() + a[1:]
            if a and a != sentence:
                rewrites.append(a)

            # Second alternative: strip just the opener and keep the rest
            m = re.match(pattern, sentence.strip(), re.IGNORECASE)
            if m:
                b = sentence[m.end():].strip().lstrip(",; ")
                if b and b[0].islower():
                    b = b[0].upper() + b[1:]
                if b and b != a and b != sentence:
                    rewrites.append(b)
            break

    return rewrites[:2]


# ── 6. Synonym drift ──────────────────────────────────────────────────────────

def rewrite_synonym_drift(sentence: str, drift_terms: list[str]) -> list[str]:
    if not drift_terms:
        return []
    canonical = drift_terms[0]
    pattern = re.compile(
        r'\bour\s+(' + '|'.join(re.escape(t) for t in drift_terms) + r')\b',
        re.IGNORECASE,
    )
    a = pattern.sub(f"our {canonical}", sentence)
    return [a] if a != sentence else []


# ─────────────────────────────────────────────────────────────────────────────
# ISSUE EXTRACTOR
# ─────────────────────────────────────────────────────────────────────────────

def extract_issues(report, text: str) -> list[dict]:
    sentences = split_sentences(text)
    issues    = []
    seen      = set()

    def add(flag, sent, extra=None):
        key = sent[:80]
        if key not in seen and sent:
            seen.add(key)
            issues.append({"flag": flag, "sentence": sent, "extra": extra})

    r = report.rhythm

    for zombie in r.zombie_nouns[:6]:
        for s in sentences:
            if zombie in s.lower():
                add("zombie_noun", s, zombie)
                break

    for h in r.hedge_sentences[:5]:
        add("hedge_stack", h["sentence"].strip(), f"{h['hedge_count']} hedges")

    if report.linguistic and hasattr(report.linguistic, "passive_hits"):
        for hit in report.linguistic.passive_hits[:6]:
            sent = hit.sentence.strip() if hasattr(hit, "sentence") else str(hit)
            add("passive", sent)

    from slop_lib.constants import RE_SPECIFIC_REF
    for s in sentences:
        if _COMPARISON_RE.search(s) and not RE_SPECIFIC_REF.search(s):
            add("context_free", s)
        if sum(1 for i in issues if i["flag"] == "context_free") >= 3:
            break

    for label, hits in report.phrase_hits.items():
        if label == "academic":
            for phrase in hits[:5]:
                for s in sentences:
                    if phrase.lower() in s.lower():
                        add("academic_phrase", s, phrase)
                        break

    if len(r.synonym_drift) >= 3:
        drift_pattern = re.compile(
            r'\bour\s+(' + '|'.join(re.escape(d) for d in r.synonym_drift) + r')\b',
            re.IGNORECASE,
        )
        for s in sentences:
            if drift_pattern.search(s):
                add("synonym_drift", s, r.synonym_drift)
            if sum(1 for i in issues if i["flag"] == "synonym_drift") >= 2:
                break

    return issues[:15]


# ─────────────────────────────────────────────────────────────────────────────
# DISPATCH
# ─────────────────────────────────────────────────────────────────────────────

def get_rewrites(issue: dict) -> list[str]:
    flag  = issue["flag"]
    sent  = issue["sentence"]
    extra = issue.get("extra")
    if flag == "zombie_noun":      return rewrite_zombie_noun(sent)
    if flag == "hedge_stack":      return rewrite_hedge_stack(sent)
    if flag == "passive":          return rewrite_passive(sent)
    if flag == "context_free":     return rewrite_context_free(sent)
    if flag == "academic_phrase":  return rewrite_academic_phrase(sent)
    if flag == "synonym_drift":    return rewrite_synonym_drift(sent, extra or [])
    return []


# ─────────────────────────────────────────────────────────────────────────────
# REPORT
# ─────────────────────────────────────────────────────────────────────────────

FLAG_LABELS = {
    "zombie_noun":     "ZOMBIE NOUN",
    "hedge_stack":     "HEDGE STACKING",
    "passive":         "PASSIVE VOICE",
    "context_free":    "CONTEXT-FREE COMPARISON",
    "academic_phrase": "ACADEMIC FILLER",
    "synonym_drift":   "SYNONYM DRIFT",
}
FLAG_TIPS = {
    "zombie_noun":     "Replace the noun phrase with its verb form.",
    "hedge_stack":     "Keep at most 1 hedge per sentence. State scope separately.",
    "passive":         "Name the actor. 'We measured X' not 'X was measured'.",
    "context_free":    "Name the metric, the baseline, and the dataset.",
    "academic_phrase": "Delete the filler. Start with the finding or the method.",
    "synonym_drift":   "Pick one name for your system and use it throughout.",
}

def build_report(paper_name, score, passed, threshold, issues) -> str:
    lines = [
        "REWRITE REPORT",
        "=" * 60,
        f"Paper    : {paper_name}",
        f"Score    : {score}/100  ({'PASS' if passed else 'FAIL'} at threshold {threshold})",
        f"Issues   : {len(issues)} rewritable sentence(s) found",
        "=" * 60,
    ]

    if not issues:
        lines.append("\nNo rewritable issues found.")
        return "\n".join(lines)

    has_placeholder = False

    for i, issue in enumerate(issues, 1):
        rws = get_rewrites(issue)
        lines.append(f"\n{'─' * 60}")
        lines.append(f"Issue {i}/{len(issues)}  —  {FLAG_LABELS.get(issue['flag'], issue['flag'].upper())}")
        lines.append(f"Tip    : {FLAG_TIPS.get(issue['flag'], '')}")
        extra = issue.get("extra")
        if isinstance(extra, str):
            lines.append(f"Detail : {extra}")
        elif isinstance(extra, list):
            lines.append(f"Names  : {', '.join(extra)}  →  pick one")

        lines.append(f"\nOriginal:")
        lines.append(f"  {issue['sentence']}")

        if rws:
            lines.append(f"\nSuggested rewrites:")
            for j, rw in enumerate(rws, 1):
                lines.append(f"  [{chr(64+j)}] {rw}")
                if any(t in rw for t in ["[BASELINE]","[N]","[DATASET]","[METRIC]","[BENCHMARK]","[SCORE]","[MARGIN]"]):
                    has_placeholder = True
        else:
            lines.append(f"\n  → Rewrite manually using the tip above.")

    lines.append(f"\n{'=' * 60}")
    if has_placeholder:
        lines.append(
            "\nNote: tags like [BASELINE], [N], [DATASET], [METRIC] are\n"
            "placeholders — fill them in with the actual values from your results.\n"
        )
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python rewrite_runner.py input/my_paper.txt")
        sys.exit(1)

    paper_path = Path(sys.argv[1])
    if not paper_path.exists():
        paper_path = HERE / "input" / sys.argv[1]
    if not paper_path.exists():
        sys.exit(f"File not found: {sys.argv[1]}")

    print(f"\n  Paper : {paper_path.name}")
    print("  [1/3] Running slop analysis...")

    raw  = paper_path.read_text(encoding="utf-8", errors="replace").strip()
    if paper_path.suffix.lower() == ".tex":
        from slop_lib.text import strip_latex
        raw = strip_latex(raw)

    text      = normalise(raw)
    threshold = get_threshold()
    report    = analyse(text, banned=load_banned_phrases(),
                        exceptions=load_exceptions(), threshold=threshold)

    print(f"  Score : {report.score}/100  ({'PASS' if report.passed else 'FAIL'})")

    print("  [2/3] Extracting issues...")
    issues = extract_issues(report, text)
    print(f"  Found : {len(issues)} rewritable issue(s)")

    print("  [3/3] Writing report...")
    OUTPUT_DIR.mkdir(exist_ok=True)
    out = OUTPUT_DIR / f"{paper_path.stem}_rewrites.txt"
    out.write_text(
        build_report(paper_path.name, report.score, report.passed, threshold, issues),
        encoding="utf-8"
    )
    print(f"\n  Done  → output/{out.name}\n")


if __name__ == "__main__":
    main()
