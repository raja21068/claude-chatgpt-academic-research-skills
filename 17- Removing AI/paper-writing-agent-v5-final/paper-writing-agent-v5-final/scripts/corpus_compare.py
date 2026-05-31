#!/usr/bin/env python3
"""
corpus_compare.py
=================
Compare your draft's style statistics to your personal corpus baseline.

Usage:
    python corpus_compare.py <draft.txt>
    python corpus_compare.py <draft.txt> --section results
    python corpus_compare.py <draft.txt> --json

Requires: build_corpus.py to have been run first (creates scripts/corpus/).
"""

import re
import sys
import json
import argparse
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from slop_lib.colors    import RED, YELLOW, GREEN, RESET, BOLD
from slop_lib.constants import HEDGE_WORDS
from slop_lib.stats     import mean, stdev, shannon_entropy
from slop_lib.text      import sent_tokenize

try:
    from nltk.tokenize import word_tokenize
except ImportError:
    def word_tokenize(t): return re.findall(r'\b\w+\b', t)

CORPUS_DIR = Path(__file__).parent / "corpus"
SECTIONS   = ["abstract", "introduction", "methods", "results", "discussion", "conclusion"]

TRANSITION_WORDS = [
    "however", "therefore", "moreover", "furthermore", "consequently",
    "in contrast", "thus", "hence", "nonetheless", "specifically",
    "in addition", "accordingly", "meanwhile", "overall",
]


# ── stats computation ─────────────────────────────────────────────────────────

def compute_stats(text: str) -> dict:
    sentences = sent_tokenize(text)
    lengths   = [len(word_tokenize(s)) for s in sentences if len(s) > 10]
    all_words = word_tokenize(text.lower())
    content   = [w for w in all_words if w.isalpha() and len(w) > 2]
    ttr       = len(set(content)) / len(content) if content else 0

    passive = len(re.findall(
        r'\b(was|were|been|being|is|are)\s+\w+ed\b', text, re.IGNORECASE
    ))

    hedge_counts = [
        sum(1 for w in re.findall(r'\b\w+\b', s.lower()) if w in HEDGE_WORDS)
        for s in sentences
    ]

    starters = [
        re.findall(r'\b\w+\b', s)[0].lower()
        for s in sentences if re.findall(r'\b\w+\b', s)
    ]

    trans_hits    = sum(text.lower().count(t) for t in TRANSITION_WORDS)
    trans_density = trans_hits / (len(sentences) + 1e-9)

    return {
        "avg_sentence_length":    round(mean(lengths), 1),
        "stdev_sentence_length":  round(stdev(lengths), 2),
        "type_token_ratio":       round(ttr, 3),
        "passive_per_100":        round(passive / (len(sentences) + 1e-9) * 100, 1),
        "avg_hedge_per_sentence": round(mean(hedge_counts), 2),
        "starter_entropy":        round(shannon_entropy(starters), 2),
        "transition_density":     round(trans_density, 2),
        "sentence_count":         len(sentences),
    }


def load_corpus_stats(section_filter=None) -> dict | None:
    if not CORPUS_DIR.exists():
        return None
    texts = []
    for subdir in sorted(CORPUS_DIR.iterdir()):
        if not subdir.is_dir():
            continue
        for sec in SECTIONS:
            if section_filter and sec != section_filter:
                continue
            f = subdir / f"{sec}.txt"
            if f.exists():
                t = f.read_text(encoding="utf-8", errors="replace").strip()
                if len(t) > 100:
                    texts.append(t)
    if not texts:
        return None
    return compute_stats("\n\n".join(texts))


# ── reporting ─────────────────────────────────────────────────────────────────

_DIVERGENCE_LABELS = {
    "avg_sentence_length":    [(0.8, 1.2, "matches your baseline"),
                               (0.0, 0.8, "shorter than usual"), (1.2, 9, "longer than usual")],
    "stdev_sentence_length":  [(0.7, 1.4, "similar variety to baseline"),
                               (0.0, 0.7, "more uniform than usual"), (1.4, 9, "more varied than usual")],
    "passive_per_100":        [(0.7, 1.5, "similar passive voice"),
                               (0.0, 0.7, "less passive than usual"), (1.5, 9, "MORE passive than usual")],
    "avg_hedge_per_sentence": [(0.8, 1.5, "similar hedging"),
                               (0.0, 0.8, "fewer hedges than usual"), (1.5, 9, "MORE hedging than usual")],
    "transition_density":     [(0.7, 1.4, "similar transition density"),
                               (0.0, 0.7, "fewer transitions"), (1.4, 9, "more transitions than usual")],
    "type_token_ratio":       [(0.8, 1.2, "similar vocabulary variety"),
                               (0.0, 0.8, "less lexical variety (good for precision)"),
                               (1.2, 9, "MORE variety (may signal AI synonymising)")],
    "starter_entropy":        [(0.8, 1.3, "similar starter variety"),
                               (0.0, 0.8, "less starter variety than usual"), (1.3, 9, "more starter variety")],
}


def _flag_colour(key: str, ratio: float) -> str:
    if key in ("passive_per_100", "avg_hedge_per_sentence", "type_token_ratio") and ratio > 2.0:
        return RED
    if key in ("passive_per_100", "avg_hedge_per_sentence", "type_token_ratio") and ratio > 1.5:
        return YELLOW
    if key == "stdev_sentence_length" and ratio < 0.6:
        return RED
    if key == "stdev_sentence_length" and ratio < 0.8:
        return YELLOW
    return GREEN


def print_comparison(draft: dict, corpus: dict) -> None:
    print(f"\n{BOLD}══ Corpus Comparison Report ══{RESET}")
    print("  Comparing draft to your personal writing baseline.\n")

    METRICS = [
        ("avg_sentence_length",    "Avg sentence length"),
        ("stdev_sentence_length",  "Sentence length StdDev"),
        ("type_token_ratio",       "Type-token ratio"),
        ("passive_per_100",        "Passive voice per 100 sents"),
        ("avg_hedge_per_sentence", "Avg hedges per sentence"),
        ("starter_entropy",        "Sentence-starter entropy"),
        ("transition_density",     "Transition word density"),
    ]

    priority_fixes = []
    for key, label in METRICS:
        d, c = draft.get(key, 0), corpus.get(key, 0)
        ratio = d / (c + 1e-9)
        colour = _flag_colour(key, ratio)

        div = f"ratio {ratio:.1f}×"
        for lo, hi, msg in _DIVERGENCE_LABELS.get(key, []):
            if lo <= ratio < hi:
                div = msg
                break

        print(f"  {label:<34} Draft: {str(d):<7} Corpus: {str(c):<7} {colour}{div}{RESET}")
        if colour == RED:
            priority_fixes.append((key, div))

    if priority_fixes:
        print(f"\n{BOLD}Priority fixes:{RESET}")
        HINTS = {
            "passive_per_100":        "Find the actor in passive sentences.",
            "avg_hedge_per_sentence": "Replace hedge clusters with scope statements.",
            "type_token_ratio":       "Pick one name per technical entity; reuse it.",
            "stdev_sentence_length":  "Add short punchy sentences; break long uniform paragraphs.",
        }
        for key, div in priority_fixes:
            hint = HINTS.get(key, "")
            print(f"  • {div}. {hint}")
    else:
        print(f"\n  {GREEN}Draft statistics are within your normal writing range.{RESET}")
    print()


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Compare draft to personal corpus baseline")
    parser.add_argument("draft",     help="Draft text file")
    parser.add_argument("--section", default=None, help="Load only this section from corpus")
    parser.add_argument("--json",    action="store_true")
    args = parser.parse_args()

    path = Path(args.draft)
    if not path.exists():
        print(f"ERROR: {path} not found"); sys.exit(1)

    text = path.read_text(encoding="utf-8", errors="replace").strip()
    if len(text) < 50:
        print("ERROR: file too short"); sys.exit(1)

    corpus = load_corpus_stats(args.section)
    if not corpus:
        print("ERROR: corpus/ not found. Run build_corpus.py first."); sys.exit(1)

    draft = compute_stats(text)

    if args.json:
        print(json.dumps({"draft": draft, "corpus": corpus}, indent=2))
    else:
        print_comparison(draft, corpus)


if __name__ == "__main__":
    main()
