#!/usr/bin/env python3
"""
rhythm_check.py
===============
Quantitative anti-AI rhythm analyser for academic prose.

Checks:
  1. Sentence-length standard deviation (low = AI)
  2. Hedge word density per sentence
  3. Paragraph shape uniformity
  4. Paragraph echo detection
  5. Sentence-starter entropy          [v4]
  6. Punctuation variety               [v4]
  7. Zombie nouns                      [v4]
  8. Context-free comparisons          [v4]

Usage:
    python rhythm_check.py <text_file>
    python rhythm_check.py <text_file> --json
    python rhythm_check.py <text_file> --fix-hints
"""

import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from slop_lib.analysis import analyse_rhythm
from slop_lib.colors   import RED, YELLOW, GREEN, RESET, BOLD
from slop_lib.constants import STDEV_THRESHOLD, HEDGE_THRESHOLD


def print_rhythm_report(r, show_hints: bool = False) -> None:
    score = max(0, 100
                - (30 if r.stdev_flag else 0)
                - min(25, len(r.hedge_sentences) * 5)
                - (15 if r.shape_uniform else 0)
                - min(15, len(r.echo_paragraphs) * 8)
                - (10 if (r.starter_entropy is not None and r.starter_entropy < 2.0) else 0))

    colour = GREEN if score >= 75 else (YELLOW if score >= 50 else RED)
    print(f"\n{BOLD}══ Rhythm Check Report ══{RESET}")
    print(f"  Mean sentence StdDev : {r.mean_stdev} words  "
          f"{'✓' if not r.stdev_flag else f'{RED}⚠ below {STDEV_THRESHOLD}{RESET}'}")
    print(f"  Hedge sentences      : {len(r.hedge_sentences)}  "
          f"{'✓' if not r.hedge_sentences else f'{RED}⚠{RESET}'}")
    print(f"  Echo paragraphs      : {len(r.echo_paragraphs)}  "
          f"{'✓' if not r.echo_paragraphs else f'{YELLOW}⚠{RESET}'}")
    print(f"  Shape uniformity     : {'uniform ⚠' if r.shape_uniform else 'varied ✓'}  "
          f"(CV={r.shape_cv})")
    if r.starter_entropy is not None:
        flag = f"{YELLOW}⚠{RESET}" if r.starter_entropy < 2.0 else "✓"
        print(f"  Starter entropy      : {r.starter_entropy} bits  {flag}")
    print(f"\n  {colour}Rhythm score: {score}/100{RESET}  "
          f"({'human-sounding' if score >= 75 else 'borderline' if score >= 50 else 'AI-like'})\n")

    issues = []
    if r.stdev_flag:
        issues.append(f"{RED}RHYTHM{RESET} Mean StdDev {r.mean_stdev} < {STDEV_THRESHOLD}. Vary sentence length.")
    for h in r.hedge_sentences[:3]:
        preview = h["sentence"][:100] + "…" if len(h["sentence"]) > 100 else h["sentence"]
        issues.append(f"{RED}HEDGING{RESET} [{h['hedge_count']} hedges] \"{preview}\"")
    for p in r.echo_paragraphs[:2]:
        issues.append(f"{YELLOW}ECHO{RESET} Last sentence mirrors first: \"{p[:80]}…\"")
    if r.shape_uniform:
        issues.append(f"{YELLOW}SHAPE{RESET} Uniform paragraph lengths (CV={r.shape_cv}).")
    for z in r.zombie_nouns[:5]:
        issues.append(f"{RED}ZOMBIE{RESET} \"{z}\" → use \"{__import__('slop_lib.constants', fromlist=['ZOMBIE_NOUNS']).ZOMBIE_NOUNS.get(z, 'simpler verb')}\"")
    for issue in r.punctuation_issues:
        issues.append(f"{YELLOW}PUNCT{RESET} {issue}")

    if issues:
        print(f"{BOLD}Issues:{RESET}")
        for i in issues:
            print(f"  • {i}")
    else:
        print(f"{GREEN}No issues found.{RESET}")

    if show_hints and r.hedge_sentences:
        print(f"\n{BOLD}Fix hints:{RESET}")
        for i, h in enumerate(r.hedge_sentences[:4], 1):
            print(f"\n  [{i}] {h['sentence'][:120]}")
            print( "      → State what the evidence shows, add one scope qualifier if needed.")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Quantitative anti-AI rhythm analyser")
    parser.add_argument("file",        help="Text file to analyse")
    parser.add_argument("--json",      action="store_true")
    parser.add_argument("--fix-hints", action="store_true")
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"ERROR: {path} not found"); sys.exit(1)

    text = path.read_text(encoding="utf-8", errors="replace")
    r    = analyse_rhythm(text)

    if args.json:
        print(json.dumps(r.to_dict(), indent=2))
    else:
        print_rhythm_report(r, show_hints=args.fix_hints)


if __name__ == "__main__":
    main()
