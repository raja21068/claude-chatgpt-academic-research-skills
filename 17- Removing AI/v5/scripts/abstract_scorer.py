#!/usr/bin/env python3
"""
abstract_scorer.py
==================
Score an abstract against required components and anti-patterns.

Checks:
  1. Four required components: Problem, Gap, Method, Result
  2. At least one specific number
  3. Named benchmark/dataset/baseline
  4. Word count against venue limit
  5. No announcement openers
  6. No citations (for double-blind venues)
  7. Abstract scope matches experiment scope signals

Usage:
    python abstract_scorer.py <abstract.txt>
    python abstract_scorer.py <abstract.txt> --limit 150   # word limit
    python abstract_scorer.py <abstract.txt> --json
"""

import re
import sys
import json
import argparse
from pathlib import Path

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    RED = Fore.RED + Style.BRIGHT; YELLOW = Fore.YELLOW + Style.BRIGHT
    GREEN = Fore.GREEN + Style.BRIGHT; RESET = Style.RESET_ALL; BOLD = Style.BRIGHT
except ImportError:
    RED = YELLOW = GREEN = RESET = BOLD = ""

try:
    import nltk
    nltk.download("punkt", quiet=True); nltk.download("punkt_tab", quiet=True)
    from nltk.tokenize import sent_tokenize
except ImportError:
    def sent_tokenize(t): return [s.strip() for s in re.split(r'(?<=[.!?])\s+', t) if s.strip()]


# Component detection patterns
COMPONENT_SIGNALS = {
    "problem": {
        "positive": [
            r"\b(is challenging|remains difficult|is a fundamental|is critical|important problem|"
            r"has been widely|major challenge|existing methods|current approaches|recent years)\b",
            r"\b(lack|fail|cannot|unable|limited|insufficient|struggle|suffer)\b",
        ],
        "negative": [],
    },
    "gap": {
        "positive": [
            r"\b(however|nevertheless|unfortunately|despite|yet|still|but|"
            r"previous work|prior work|existing method|current method)\b",
            r"\b(gap|limitation|shortcoming|drawback|issue|problem|challenge) (of|in|with)\b",
        ],
        "negative": [],
    },
    "method": {
        "positive": [
            r"\b(we propose|we present|we introduce|we develop|we design|we formulate|"
            r"our (method|model|approach|framework|system|algorithm))\b",
            r"\b(novel|new) (method|model|approach|framework|architecture)\b",
        ],
        "negative": [],
    },
    "result": {
        "positive": [
            r"\b(achieve|attain|outperform|surpass|improve|gain|boost|"
            r"demonstrate|show|yield|obtain)\b",
            r'\d+\.?\d*\s*(%|points?|BLEU|ROUGE|F1|accuracy|improvement)',
            r'\b(state.of.the.art|best|competitive|strong|superior)\b',
        ],
        "negative": [],
    },
}

# Announcement openers to flag
ANNOUNCEMENT_OPENERS = [
    r'^in this paper,?\s+we',
    r'^in this work,?\s+we',
    r'^this paper (presents?|introduces?|proposes?|describes?)',
    r'^this work (presents?|introduces?|proposes?|describes?)',
    r'^we present a (novel|new)',
    r'^we propose a (novel|new)',
]

# Overclaim signals
OVERCLAIM_SIGNALS = [
    r'\b(all|any|every|universal|always|never|any domain|all domains|arbitrary)\b',
    r'\b(revolutionary|groundbreaking|unprecedented|remarkable|transformative)\b',
    r'\bstate-of-the-art\b(?!.*\d)',  # state-of-the-art without a number nearby
]


def count_words(text):
    return len(re.findall(r'\b\w+\b', text))


def detect_component(text, component):
    signals = COMPONENT_SIGNALS[component]["positive"]
    for pattern in signals:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def check_announcement_opener(text):
    sentences = sent_tokenize(text)
    if not sentences:
        return False
    first = sentences[0].lower().strip()
    return any(re.search(p, first) for p in ANNOUNCEMENT_OPENERS)


def check_numbers(text):
    number_pattern = r'\d+\.?\d*\s*(%|points?|BLEU|ROUGE|F1|accuracy|speed|×|faster|smaller)'
    return bool(re.search(number_pattern, text, re.IGNORECASE))


def check_named_entity(text):
    # Named datasets, benchmarks, baselines (simple heuristic: ALL-CAPS or known patterns)
    named = r'\b([A-Z]{2,}|ImageNet|GLUE|SQuAD|WMT|COCO|CIFAR|PTB|WikiText|arXiv)\b'
    return bool(re.search(named, text))


def check_citations(text):
    cite_patterns = [r'\\cite', r'\[\d+\]', r'\([A-Z][a-z]+\s+et\s+al', r'\([A-Z][a-z]+,\s+\d{4}\)']
    return any(re.search(p, text) for p in cite_patterns)


def check_formula_structure(text):
    """Check if abstract is exactly the 4-sentence AI formula."""
    sentences = sent_tokenize(text)
    if len(sentences) != 4:
        return False
    components = [
        detect_component(sentences[0], "problem"),
        detect_component(sentences[1], "gap"),
        detect_component(sentences[2], "method"),
        detect_component(sentences[3], "result"),
    ]
    return all(components)


def check_overclaims(text):
    hits = []
    for p in OVERCLAIM_SIGNALS:
        matches = re.findall(p, text, re.IGNORECASE)
        hits.extend(matches)
    return hits


def score_abstract(text, word_limit=None):
    word_count = count_words(text)

    components = {c: detect_component(text, c) for c in COMPONENT_SIGNALS}
    has_number    = check_numbers(text)
    has_named     = check_named_entity(text)
    has_citation  = check_citations(text)
    is_formula    = check_formula_structure(text)
    announcement  = check_announcement_opener(text)
    overclaims    = check_overclaims(text)

    flags = []
    missing = [c for c, found in components.items() if not found]
    if missing:
        flags.append(f"MISSING COMPONENTS: {', '.join(missing)}")
    if not has_number:
        flags.append("NO NUMBERS: Abstract makes no quantified claim")
    if not has_named:
        flags.append("NO NAMED ENTITY: No dataset, benchmark, or baseline named")
    if has_citation:
        flags.append("CITATIONS: Abstract contains citations (avoid in double-blind)")
    if is_formula:
        flags.append("FORMULA: Exactly 4 sentences matching Problem/Gap/Method/Result — AI template")
    if announcement:
        flags.append("ANNOUNCEMENT OPENER: First sentence announces the paper rather than stating a finding or problem")
    if overclaims:
        flags.append(f"OVERCLAIMS: {', '.join(set(overclaims))}")
    if word_limit and word_count > word_limit:
        flags.append(f"OVER LIMIT: {word_count} words exceeds venue limit of {word_limit}")

    # score
    score = 100
    score -= len(missing) * 15
    score -= 15 if not has_number else 0
    score -= 10 if not has_named else 0
    score -= 10 if has_citation else 0
    score -= 10 if is_formula else 0
    score -= 10 if announcement else 0
    score -= len(overclaims) * 5
    score = max(0, score)

    return {
        "word_count":   word_count,
        "word_limit":   word_limit,
        "components":   components,
        "has_number":   has_number,
        "has_named":    has_named,
        "has_citation": has_citation,
        "is_formula":   is_formula,
        "announcement_opener": announcement,
        "overclaims":   overclaims,
        "flags":        flags,
        "score":        score,
    }


def print_report(r, text):
    score  = r["score"]
    colour = GREEN if score >= 80 else (YELLOW if score >= 60 else RED)
    print(f"\n{BOLD}══ Abstract Scorer ══{RESET}")
    print(f"  Score: {colour}{score}/100{RESET}  |  "
          f"{r['word_count']} words"
          + (f" / {r['word_limit']} limit" if r["word_limit"] else ""))

    print(f"\n{BOLD}Component check:{RESET}")
    for comp, found in r["components"].items():
        c = GREEN if found else RED
        mark = "✓" if found else "✗"
        print(f"  {c}{mark} {comp.capitalize()}{RESET}")

    print(f"\n{BOLD}Specificity:{RESET}")
    print(f"  {'✓' if r['has_number'] else '✗'} Contains a specific number  "
          f"{'✓' if r['has_named'] else '✗'} Names a dataset/benchmark/baseline")

    if r["flags"]:
        print(f"\n{BOLD}Issues:{RESET}")
        for f in r["flags"]:
            c = RED if any(x in f for x in ["MISSING","NO ","FORMULA","ANNOUNCE","OVER"]) else YELLOW
            print(f"  {c}• {f}{RESET}")

    if not r["flags"]:
        print(f"\n  {GREEN}Abstract passes all checks.{RESET}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Score an abstract against required components")
    parser.add_argument("file",      help="Abstract text file")
    parser.add_argument("--limit",   type=int, default=None, help="Venue word limit")
    parser.add_argument("--json",    action="store_true")
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"ERROR: {path} not found"); sys.exit(1)

    text = path.read_text(encoding="utf-8", errors="replace").strip()
    r    = score_abstract(text, args.limit)

    if args.json:
        print(json.dumps(r, indent=2))
        return

    print_report(r, text)
    sys.exit(0 if r["score"] >= 70 else 1)


if __name__ == "__main__":
    main()
