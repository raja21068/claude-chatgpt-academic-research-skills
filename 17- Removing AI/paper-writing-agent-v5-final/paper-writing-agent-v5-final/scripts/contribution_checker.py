#!/usr/bin/env python3
"""
contribution_checker.py
=======================
Analyse contribution bullet lists for AI structural uniformity.

Checks:
  - All bullets start with "We" + gerund
  - All bullets similar length
  - Exactly 3 bullets (most common AI formula)
  - Bullets that mirror the abstract
  - Missing numbers or named baselines in contribution claims

Usage:
    python contribution_checker.py <draft.txt>
    python contribution_checker.py <draft.txt> --abstract <abstract.txt>
    python contribution_checker.py <draft.txt> --json
"""

import re
import sys
import json
import math
import argparse
from pathlib import Path
from collections import Counter

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    RED = Fore.RED + Style.BRIGHT; YELLOW = Fore.YELLOW + Style.BRIGHT
    GREEN = Fore.GREEN + Style.BRIGHT; RESET = Style.RESET_ALL; BOLD = Style.BRIGHT
except ImportError:
    RED = YELLOW = GREEN = RESET = BOLD = ""


def stdev(vals):
    if len(vals) < 2: return 0.0
    m = sum(vals) / len(vals)
    return math.sqrt(sum((v - m)**2 for v in vals) / len(vals))


def extract_bullets(text: str):
    """Extract bullet/contribution list items from text."""
    bullets = []

    # LaTeX \item patterns
    items = re.findall(r'\\item\s+(.+?)(?=\\item|\\end\{|$)', text, re.DOTALL)
    for item in items:
        cleaned = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', '', item)
        cleaned = re.sub(r'[{}\\]', '', cleaned).strip()
        if 10 < len(cleaned) < 300:
            bullets.append(cleaned)

    # Markdown bullet patterns
    if not bullets:
        md_items = re.findall(r'^[-•*]\s+(.+)$', text, re.MULTILINE)
        bullets.extend(i.strip() for i in md_items if 10 < len(i.strip()) < 300)

    # Numbered list patterns
    if not bullets:
        num_items = re.findall(r'^\d+[.)]\s+(.+)$', text, re.MULTILINE)
        bullets.extend(i.strip() for i in num_items if 10 < len(i.strip()) < 300)

    return bullets


def analyse_bullets(bullets, abstract_text=None):
    if not bullets:
        return {"error": "No contribution bullets found"}

    n = len(bullets)
    lengths = [len(re.findall(r'\b\w+\b', b)) for b in bullets]
    avg_len = sum(lengths) / len(lengths)
    len_stdev = stdev(lengths)

    # Grammatical structure of each bullet
    structures = []
    for b in bullets:
        words = re.findall(r'\b\w+\b', b)
        if not words:
            structures.append("empty")
            continue
        first = words[0].lower()
        second = words[1].lower() if len(words) > 1 else ""
        # detect "We + verb/gerund"
        if first == "we":
            if second.endswith("ing"):
                structures.append("We+gerund")
            elif second.endswith("e") or second.endswith("ed"):
                structures.append("We+verb")
            else:
                structures.append("We+other")
        elif first in ("a", "an", "the"):
            structures.append("article+noun")
        else:
            structures.append(f"other:{first}")

    struct_counts = Counter(structures)
    dominant_struct = struct_counts.most_common(1)[0]
    all_same_struct = dominant_struct[1] == n

    # check for numbers in each bullet
    has_number = [bool(re.search(r'\d', b)) for b in bullets]

    # check for named baselines/benchmarks
    has_specific = [bool(re.search(
        r'\b([A-Z]{2,}|Table|Figure|benchmark|dataset|baseline|\d+\s*%|\d+\.\d+)\b', b
    )) for b in bullets]

    # abstract overlap (if provided)
    abstract_overlaps = []
    if abstract_text:
        abs_words = set(re.findall(r'\b\w{4,}\b', abstract_text.lower()))
        for b in bullets:
            bwords = set(re.findall(r'\b\w{4,}\b', b.lower()))
            overlap = len(bwords & abs_words) / (len(bwords) + 1e-9)
            abstract_overlaps.append(round(overlap, 2))

    flags = []
    suggestions = []

    if n == 3 and all_same_struct:
        flags.append(f"FORMULA: Exactly 3 bullets, all '{dominant_struct[0]}' — classic AI template")
        suggestions.append("Break the formula: vary the first word and sentence structure across bullets")

    if n == 3 and not any(has_number):
        flags.append("NO NUMBERS: None of the 3 contribution bullets contains a quantified claim")
        suggestions.append("Add a specific number to at least one bullet (metric, improvement, dataset size)")

    if all_same_struct and n >= 2:
        flags.append(f"UNIFORM STRUCTURE: All bullets share '{dominant_struct[0]}' form")
        suggestions.append("Use different grammatical forms: a direct claim, a quantified result, and a named contribution")

    if len_stdev < 3 and n >= 3:
        flags.append(f"UNIFORM LENGTH: All bullets are {avg_len:.0f}±{len_stdev:.1f} words — same length")
        suggestions.append("Vary bullet lengths: one short claim (5-8 words), one detailed (12-18 words)")

    if abstract_overlaps and all(o > 0.6 for o in abstract_overlaps):
        flags.append("ABSTRACT ECHO: Contribution bullets closely mirror the abstract — they repeat rather than claim")
        suggestions.append("Reframe bullets as verifiable claims ('X improves Y by Z'), not abstract summaries")

    not_specific = [i for i, s in enumerate(has_specific) if not s]
    if len(not_specific) >= n // 2:
        flags.append(f"VAGUE BULLETS: {len(not_specific)}/{n} bullets lack specific names, numbers, or baselines")
        suggestions.append("Name the dataset, metric, or baseline for each contribution claim")

    score = max(0, 100 - len(flags) * 20)

    return {
        "bullet_count":      n,
        "lengths":           lengths,
        "avg_length":        round(avg_len, 1),
        "length_stdev":      round(len_stdev, 2),
        "structures":        structures,
        "all_same_structure": all_same_struct,
        "dominant_structure": dominant_struct[0],
        "has_numbers":       has_number,
        "abstract_overlaps": abstract_overlaps,
        "flags":             flags,
        "suggestions":       suggestions,
        "score":             score,
        "bullets":           bullets,
    }


def print_report(r):
    score  = r.get("score", 0)
    colour = GREEN if score >= 80 else (YELLOW if score >= 50 else RED)
    print(f"\n{BOLD}══ Contribution Bullet Analysis ══{RESET}")
    print(f"  Score: {colour}{score}/100{RESET}  |  {r['bullet_count']} bullets found\n")

    print(f"{BOLD}Bullets:{RESET}")
    for i, (b, struct, has_num) in enumerate(
        zip(r["bullets"], r["structures"], r["has_numbers"]), 1
    ):
        num_tag = "" if has_num else f" {YELLOW}[no number]{RESET}"
        print(f"  {i}. [{struct}] {b[:100]}{num_tag}")

    print(f"\n  Lengths: {r['lengths']}  (avg {r['avg_length']}, StdDev {r['length_stdev']})")

    if r["flags"]:
        print(f"\n{BOLD}Issues:{RESET}")
        for f in r["flags"]:
            print(f"  {RED}• {f}{RESET}")

    if r["suggestions"]:
        print(f"\n{BOLD}Suggestions:{RESET}")
        for i, s in enumerate(r["suggestions"], 1):
            print(f"  {i}. {s}")

    if not r["flags"]:
        print(f"\n  {GREEN}No structural uniformity issues.{RESET}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Analyse contribution bullet structure")
    parser.add_argument("draft",     help="Draft text file (.txt or .tex)")
    parser.add_argument("--abstract",help="Abstract text file for overlap check")
    parser.add_argument("--json",    action="store_true")
    args = parser.parse_args()

    path = Path(args.draft)
    if not path.exists():
        print(f"ERROR: {path} not found"); sys.exit(1)

    text = path.read_text(encoding="utf-8", errors="replace")
    abstract_text = None
    if args.abstract:
        ap = Path(args.abstract)
        if ap.exists():
            abstract_text = ap.read_text(encoding="utf-8", errors="replace")

    bullets = extract_bullets(text)
    if not bullets:
        print("No contribution bullets found. Check that the file contains \\item, - , or numbered list items.")
        sys.exit(0)

    r = analyse_bullets(bullets, abstract_text)

    if args.json:
        print(json.dumps(r, indent=2))
        return

    print_report(r)
    sys.exit(0 if r["score"] >= 70 else 1)


if __name__ == "__main__":
    main()
