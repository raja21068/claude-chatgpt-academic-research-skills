#!/usr/bin/env python3
"""
rewrite_ai.py
=============
Rewrite a paper through the Claude API to remove AI writing patterns.

Usage:
    python run.py rewrite-ai paper.txt
    python run.py rewrite-ai paper.txt --section methods
    python run.py rewrite-ai paper.txt --chunk-size 800
    python run.py rewrite-ai paper.txt --model claude-opus-4-6
    python run.py rewrite-ai paper.txt --dry-run

How it works
------------
1. Score the paper with the local checker (fast, no API call).
2. Split the text into chunks of ~N words at paragraph boundaries.
3. Send each chunk to Claude with the full humanizer system prompt.
4. Re-score the rewritten output.
5. Save to output/<stem>_ai_rewritten.txt and print a before/after summary.

The system prompt encodes all 25 humanizer pattern rules so Claude
fixes things regex cannot: passive voice, sentence structure, rhythm.

Requires: pip install anthropic
API key:  set ANTHROPIC_API_KEY environment variable
          OR create a file called .api_key in the project root
"""

import sys
import os
import re
import json
import time
import argparse
from pathlib import Path

HERE = Path(__file__).parent.parent
sys.path.insert(0, str(HERE))

from slop_lib import analyse, load_banned_phrases, load_exceptions
from slop_lib.text import strip_latex


# ─────────────────────────────────────────────────────────────────────────────
# SYSTEM PROMPT  (encodes all 25 humanizer rules)
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an academic writing editor. Rewrite the text to remove AI writing patterns while keeping the meaning, all citations, all numbers, all equations, and all technical terms exactly intact.

WHAT TO FIX — apply every rule below:

1. FILLER OPENERS — remove entirely:
   "It is important to note that", "It should be noted that", "It is worth noting that",
   "It was found that", "It has been shown that", "It is generally accepted that",
   "To the best of our knowledge", "As far as we are aware", "We believe that",
   "One can observe that", "We can see that", "Notably,", "Importantly,", "Interestingly,"

2. FILLER PHRASES — compress:
   "in order to" → "to"
   "due to the fact that" → "because"
   "at this point in time" → "now"
   "in the event that" → "if"
   "has the ability to" → "can"
   "is able to" → "can"

3. COPULA AVOIDANCE — use simple verbs:
   "serves as a/an/the" → "is a/an/the"
   "stands as a/an/the" → "is a/an/the"
   "functions as a/an" → "acts as a/an"
   "boasts a/an" → "has a/an"

4. AI VOCABULARY — replace with plainer alternatives:
   robust → strong / reliable (context-dependent)
   comprehensive → complete / full / thorough
   novel → new
   innovative → new / improved
   leveraging → using
   leverage → use
   holistic → overall
   paradigm → approach / framework
   synergy / synergistic → combined / joint
   transformative → significant
   groundbreaking → new
   seamless → smooth
   cutting-edge → recent / latest
   state-of-the-art → current best / top-performing
   vibrant → active
   pivotal → key
   crucial → important / critical
   showcase → show / demonstrate
   delve → examine / explore
   tapestry → mix / combination (when used abstractly)
   testament → proof / evidence
   underscore / underscores → show / highlight
   enduring → lasting
   impactful → significant / effective

5. CONNECTORS — reduce over-use of sentence-initial:
   "Furthermore," → use only once per 3 paragraphs; otherwise restructure
   "Moreover," → same
   "Additionally," → same
   Prefer restructuring the logic so the connector isn't needed.

6. PASSIVE VOICE — convert to active where the agent is clear:
   "X was measured by us" → "We measured X"
   "Results were obtained" → "We obtained results"
   "The model was trained on" → "We trained the model on"
   "Performance was evaluated" → "We evaluated performance"
   Keep passive only when: the agent is genuinely unknown, or when passive is the field norm
   (e.g. "Samples were collected" is fine if who collected them is irrelevant).

7. EM DASH OVERUSE — replace " — " (spaced em dash) with ", " or rewrite the clause.

8. SIGNIFICANCE INFLATION — remove:
   "marks a pivotal moment", "represents a major breakthrough",
   "setting the stage for", "indelible mark", "reflects broader trends"
   Just state the fact directly.

9. VAGUE ATTRIBUTIONS — make specific or remove:
   "Experts argue" → cite the actual paper or remove
   "Industry observers note" → same
   "It is widely believed" → same

10. GENERIC CONCLUSIONS — replace with specific findings:
    "The future looks bright" → state what the actual next step is
    "Exciting times lie ahead" → remove
    "Continues this journey toward excellence" → remove

HARD RULES:
- Do NOT change any number, percentage, citation, equation, table, or technical term.
- Do NOT make the writing casual — keep academic register throughout.
- Do NOT add new content or claims.
- Do NOT add explanations or commentary — output ONLY the rewritten text.
- Preserve all paragraph breaks exactly.
- Preserve LaTeX commands and citation keys exactly."""


# ─────────────────────────────────────────────────────────────────────────────
# API CLIENT
# ─────────────────────────────────────────────────────────────────────────────

def get_api_key() -> str:
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if key:
        return key
    keyfile = HERE / ".api_key"
    if keyfile.exists():
        return keyfile.read_text().strip()
    return ""


def rewrite_chunk(text: str, model: str, api_key: str, retries: int = 2) -> str:
    """Send one chunk to Claude and return the rewritten text."""
    try:
        import anthropic
    except ImportError:
        print("  ERROR: anthropic package not installed.")
        print("  Fix:   pip install anthropic")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    for attempt in range(retries + 1):
        try:
            msg = client.messages.create(
                model=model,
                max_tokens=2048,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": f"Rewrite this academic text:\n\n{text}"}],
            )
            return msg.content[0].text.strip()
        except Exception as e:
            if attempt < retries:
                time.sleep(2 ** attempt)
            else:
                print(f"\n  WARNING: API call failed after {retries+1} attempts: {e}")
                return text   # return original on failure


# ─────────────────────────────────────────────────────────────────────────────
# TEXT SPLITTING
# ─────────────────────────────────────────────────────────────────────────────

def split_into_chunks(text: str, max_words: int = 800) -> list[str]:
    """
    Split text into chunks of ≤ max_words at paragraph boundaries.

    Handles both double-newline paragraphs (standard) and single-newline
    paragraphs (common in PDF-extracted text).  Never splits mid-sentence.
    """
    # Detect paragraph separator style
    if "\n\n" in text:
        paragraphs = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
    else:
        # Single-newline text: treat each non-empty line as a paragraph
        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]

    # Merge very short lines (headers, affiliations) with the next paragraph
    merged: list[str] = []
    for para in paragraphs:
        wc = len(para.split())
        if merged and wc < 8:
            merged[-1] += " " + para
        else:
            merged.append(para)

    chunks, current, current_count = [], [], 0

    for para in merged:
        wc = len(para.split())
        if current_count + wc > max_words and current:
            chunks.append("\n\n".join(current))
            current, current_count = [para], wc
        else:
            current.append(para)
            current_count += wc

    if current:
        chunks.append("\n\n".join(current))

    return chunks


# ─────────────────────────────────────────────────────────────────────────────
# SECTION FILTER
# ─────────────────────────────────────────────────────────────────────────────

_SECTION_PATTERNS = {
    "abstract":     re.compile(r"\babstract\b", re.IGNORECASE),
    "introduction": re.compile(r"\bintroduction\b", re.IGNORECASE),
    "methods":      re.compile(r"\b(methods?|methodology|experimental)\b", re.IGNORECASE),
    "results":      re.compile(r"\b(results?|experiments?)\b", re.IGNORECASE),
    "discussion":   re.compile(r"\b(discussion|analysis)\b", re.IGNORECASE),
    "conclusion":   re.compile(r"\b(conclusion|summary)\b", re.IGNORECASE),
}

def extract_section(text: str, section: str) -> tuple[str, int, int]:
    """
    Return (section_text, start_char, end_char) for the named section.
    Falls back to full text if section not found.
    """
    pat = _SECTION_PATTERNS.get(section.lower())
    if not pat:
        return text, 0, len(text)

    lines = text.split("\n")
    start_line = None
    for i, line in enumerate(lines):
        if pat.search(line.strip()) and len(line.strip()) < 60:
            start_line = i
            break

    if start_line is None:
        print(f"  WARNING: section '{section}' not found — rewriting full text.")
        return text, 0, len(text)

    # Find next TOP-LEVEL section header after start (e.g. "3. Results")
    # Subsection headers like "2.1." or "2.1.1." are not section boundaries
    _TOP_SECTION = re.compile(r"^\d+\.\s+[A-Z]", re.MULTILINE)
    _SUBSECTION  = re.compile(r"^\d+\.\d+")

    end_line = len(lines)
    for i in range(start_line + 1, len(lines)):
        stripped = lines[i].strip()
        if not stripped or len(stripped) >= 60:
            continue
        # Skip subsections (2.1, 2.1.1, etc.)
        if _SUBSECTION.match(stripped):
            continue
        # Stop at the next top-level numbered section
        if _TOP_SECTION.match(stripped):
            end_line = i
            break
        # Stop at known section keywords (unnumbered headings)
        if any(p.search(stripped) for k, p in _SECTION_PATTERNS.items()
               if k != section.lower()):
            end_line = i
            break

    section_lines = lines[start_line:end_line]
    section_text  = "\n".join(section_lines)
    start_char    = len("\n".join(lines[:start_line])) + (1 if start_line > 0 else 0)
    end_char      = start_char + len(section_text)

    return section_text, start_char, end_char


# ─────────────────────────────────────────────────────────────────────────────
# COLORS
# ─────────────────────────────────────────────────────────────────────────────

def _c(code, text):
    if sys.stdout.isatty():
        return f"\033[{code}m{text}\033[0m"
    return text

def green(t):  return _c("1;32", t)
def red(t):    return _c("1;31", t)
def yellow(t): return _c("1;33", t)
def bold(t):   return _c("1",    t)
def cyan(t):   return _c("1;36", t)
def dim(t):    return _c("2",    t)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Rewrite a paper through Claude to remove AI writing patterns."
    )
    parser.add_argument("file",         help="Input .txt or .tex file")
    parser.add_argument("--section",    default="",    help="Rewrite one section only (abstract|introduction|methods|results|discussion|conclusion)")
    parser.add_argument("--chunk-size", type=int, default=800, help="Max words per API chunk (default 800)")
    parser.add_argument("--model",      default="claude-sonnet-4-6", help="Claude model (default: claude-sonnet-4-6)")
    parser.add_argument("--dry-run",    action="store_true", help="Show chunks without calling the API")
    parser.add_argument("--json",       action="store_true", help="Print JSON summary")
    args = parser.parse_args()

    # ── Load file ─────────────────────────────────────────────────────────
    path = Path(args.file)
    if not path.exists():
        path = HERE / "input" / args.file
    if not path.exists():
        print(red(f"ERROR: file not found: {args.file}")); sys.exit(1)

    raw = path.read_text(encoding="utf-8", errors="replace")
    if path.suffix.lower() == ".tex":
        raw = strip_latex(raw)

    # ── API key ────────────────────────────────────────────────────────────
    if not args.dry_run:
        api_key = get_api_key()
        if not api_key:
            print(red("ERROR: ANTHROPIC_API_KEY not set."))
            print()
            print("Options:")
            print("  1. Set environment variable:  export ANTHROPIC_API_KEY=sk-ant-...")
            print("  2. Create file in project root: echo 'sk-ant-...' > .api_key")
            sys.exit(1)

    # ── Score before ──────────────────────────────────────────────────────
    print()
    print(bold("╔══════════════════════════════════════════╗"))
    print(bold("║     Paper Writing Agent v6               ║"))
    print(bold("║     Claude AI Rewriter                   ║"))
    print(bold("╚══════════════════════════════════════════╝"))
    print()

    banned     = load_banned_phrases()
    exceptions = load_exceptions()

    print(bold("[ 1/4 ] Scoring original..."))
    report_before = analyse(raw, banned, exceptions, threshold=70)
    score_before  = report_before.score
    colour_before = green if score_before >= 75 else (yellow if score_before >= 50 else red)
    print(f"        Score: {colour_before(str(score_before)+'/100')}  "
          f"({'PASS' if report_before.passed else 'FAIL'})")
    if report_before.ai_patterns:
        ap = report_before.ai_patterns
        print(f"        Passive ratio: {ap.passive_overall*100:.0f}%  |  "
              f"Methods verbs: {ap.methods_verb_count}")
    if report_before.humanizer:
        h = report_before.humanizer
        print(f"        AI vocab density: {h.ai_vocab_count/max(1,len(raw.split()))*1000:.1f}/1000 words  |  "
              f"Filler phrases: {h.autofix_count}")
    print()

    # ── Extract section if requested ──────────────────────────────────────
    if args.section:
        work_text, sec_start, sec_end = extract_section(raw, args.section)
        print(f"        Section '{args.section}': {len(work_text.split())} words")
    else:
        work_text, sec_start, sec_end = raw, 0, len(raw)

    # ── Split into chunks ─────────────────────────────────────────────────
    chunks = split_into_chunks(work_text, args.chunk_size)
    print(bold(f"[ 2/4 ] Split into {len(chunks)} chunk(s) "
               f"(~{args.chunk_size} words each)"))
    if args.dry_run:
        print()
        for i, chunk in enumerate(chunks, 1):
            wc = len(chunk.split())
            print(f"  Chunk {i}: {wc} words")
            print(dim("  " + chunk[:120].replace("\n", " ") + "…"))
            print()
        print(yellow("  DRY RUN — no API calls made."))
        sys.exit(0)
    print()

    # ── Rewrite chunks ────────────────────────────────────────────────────
    print(bold(f"[ 3/4 ] Rewriting with {args.model}..."))
    rewritten_chunks = []
    for i, chunk in enumerate(chunks, 1):
        wc = len(chunk.split())
        print(f"  chunk {i}/{len(chunks)}  ({wc} words)  ", end="", flush=True)
        t0 = time.time()
        result = rewrite_chunk(chunk, args.model, api_key)
        elapsed = time.time() - t0
        print(green(f"✓  {elapsed:.1f}s"))
        rewritten_chunks.append(result)

    rewritten_section = "\n\n".join(rewritten_chunks)

    # ── Reassemble full text ──────────────────────────────────────────────
    if args.section and sec_start < sec_end:
        rewritten_full = raw[:sec_start] + rewritten_section + raw[sec_end:]
    else:
        rewritten_full = rewritten_section

    # ── Score after ───────────────────────────────────────────────────────
    print()
    print(bold("[ 4/4 ] Scoring rewritten text..."))
    report_after = analyse(rewritten_full, banned, exceptions, threshold=70)
    score_after  = report_after.score
    colour_after = green if score_after >= 75 else (yellow if score_after >= 50 else red)
    delta        = score_after - score_before
    arrow        = f"+{delta}" if delta >= 0 else str(delta)
    print(f"        Score: {colour_before(str(score_before))} → "
          f"{colour_after(str(score_after)+'/100')}  "
          f"({green(arrow) if delta > 0 else red(arrow) if delta < 0 else arrow} pts)  "
          f"({'PASS' if report_after.passed else 'FAIL'})")
    if report_after.ai_patterns:
        ap_a = report_after.ai_patterns
        ap_b = report_before.ai_patterns
        passive_delta = ""
        if ap_b:
            pd = round((ap_a.passive_overall - ap_b.passive_overall)*100)
            passive_delta = f"  ({'+' if pd>=0 else ''}{pd}%)"
        print(f"        Passive ratio: {ap_a.passive_overall*100:.0f}%{passive_delta}  |  "
              f"Methods verbs: {ap_a.methods_verb_count}")
    print()

    # ── Save ──────────────────────────────────────────────────────────────
    out_dir = HERE / "output"
    out_dir.mkdir(exist_ok=True)
    stem    = path.stem
    if args.section:
        stem = f"{stem}_{args.section}"
    out_path = out_dir / f"{stem}_ai_rewritten.txt"
    out_path.write_text(rewritten_full, encoding="utf-8")

    print(f"  Saved → {cyan('output/' + out_path.name)}")
    print()

    # ── JSON ──────────────────────────────────────────────────────────────
    if args.json:
        print(json.dumps({
            "file":          str(path),
            "model":         args.model,
            "section":       args.section or "full",
            "chunks":        len(chunks),
            "score_before":  score_before,
            "score_after":   score_after,
            "delta":         delta,
            "passed_before": report_before.passed,
            "passed_after":  report_after.passed,
            "output":        str(out_path),
        }, indent=2))


if __name__ == "__main__":
    main()
