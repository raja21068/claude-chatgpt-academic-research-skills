#!/usr/bin/env python3
"""
slop_diff.py
============
Compare two versions of a section and show exactly what improved or regressed.

Usage:
    python slop_diff.py draft_v1.txt draft_v2.txt
    python slop_diff.py draft_v1.txt draft_v2.txt --json
    python slop_diff.py draft_v1.txt draft_v2.txt --sentences
"""

import sys
import json
import difflib
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from slop_lib import analyse, load_banned_phrases, load_exceptions
from slop_lib.analysis import SlopReport
from slop_lib.colors   import RED, YELLOW, GREEN, RESET, BOLD
from slop_lib.text     import sent_tokenize


def diff_reports(a: SlopReport, b: SlopReport) -> tuple[dict, dict]:
    """Return (fixed, regressed) finding sets between two reports."""
    fixed:     dict = {}
    regressed: dict = {}

    # phrase hits
    for label in set(list(a.phrase_hits) + list(b.phrase_hits)):
        set_a = set(a.phrase_hits.get(label, []))
        set_b = set(b.phrase_hits.get(label, []))
        gone  = set_a - set_b
        new   = set_b - set_a
        if gone: fixed[f"phrases:{label}"]     = sorted(gone)
        if new:  regressed[f"phrases:{label}"] = sorted(new)

    # rhythm: hedge sentences
    h_a = {h["sentence"][:80] for h in a.rhythm.hedge_sentences}
    h_b = {h["sentence"][:80] for h in b.rhythm.hedge_sentences}
    if h_a - h_b: fixed["hedging"]     = sorted(h_a - h_b)
    if h_b - h_a: regressed["hedging"] = sorted(h_b - h_a)

    # zombie nouns
    z_a, z_b = set(a.rhythm.zombie_nouns), set(b.rhythm.zombie_nouns)
    if z_a - z_b: fixed["zombie_nouns"]     = sorted(z_a - z_b)
    if z_b - z_a: regressed["zombie_nouns"] = sorted(z_b - z_a)

    # rhythm stdev
    if a.rhythm.stdev_flag and not b.rhythm.stdev_flag:
        fixed["rhythm"]     = f"StdDev improved {a.rhythm.mean_stdev} → {b.rhythm.mean_stdev}"
    elif not a.rhythm.stdev_flag and b.rhythm.stdev_flag:
        regressed["rhythm"] = f"StdDev worsened {a.rhythm.mean_stdev} → {b.rhythm.mean_stdev}"

    return fixed, regressed


def sentence_diff(text_a: str, text_b: str) -> dict:
    sents_a = sent_tokenize(text_a)
    sents_b = sent_tokenize(text_b)
    sm = difflib.SequenceMatcher(None, sents_a, sents_b)
    added, removed, changed = [], [], []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "insert":
            added.extend(sents_b[j1:j2])
        elif tag == "delete":
            removed.extend(sents_a[i1:i2])
        elif tag == "replace":
            for old, new in zip(sents_a[i1:i2], sents_b[j1:j2]):
                changed.append({"old": old[:100], "new": new[:100]})
    return {"added": added, "removed": removed, "changed": changed}


def print_diff_report(
    a: SlopReport, b: SlopReport,
    fixed: dict, regressed: dict,
    show_sents: bool = False,
    text_a: str = "", text_b: str = "",
) -> None:
    delta  = b.score - a.score
    dc     = GREEN if delta >= 0 else RED
    print(f"\n{BOLD}══ Slop Diff ══{RESET}")
    print(f"  v1 score : {a.score}/100")
    print(f"  v2 score : {b.score}/100  {dc}({delta:+d}){RESET}\n")

    print(f"{BOLD}Dimension changes:{RESET}")
    for dim in a.dimensions:
        v1, v2 = a.dimensions[dim], b.dimensions[dim]
        d  = v2 - v1
        dc = GREEN if d >= 0 else RED
        print(f"  {dim:<14} {v1:>2} → {v2:>2}  {dc}({d:+d}){RESET}")

    if fixed:
        print(f"\n{GREEN}{BOLD}Fixed ✓{RESET}")
        for key, items in fixed.items():
            if isinstance(items, list):
                print(f"  {key}: " + ", ".join(f'"{i}"' for i in items[:5]))
            else:
                print(f"  {key}: {items}")

    if regressed:
        print(f"\n{RED}{BOLD}Regressed ✗{RESET}")
        for key, items in regressed.items():
            if isinstance(items, list):
                print(f"  {key}: " + ", ".join(f'"{i}"' for i in items[:5]))
            else:
                print(f"  {key}: {items}")

    if not fixed and not regressed:
        print(f"\n{YELLOW}No change in detected issues.{RESET}")

    if show_sents and text_a and text_b:
        sd = sentence_diff(text_a, text_b)
        if sd["changed"]:
            print(f"\n{BOLD}Changed sentences:{RESET}")
            for c in sd["changed"][:5]:
                print(f"  - {c['old']}")
                print(f"  + {c['new']}")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Slop diff between two draft versions")
    parser.add_argument("file_a",      help="v1 text file")
    parser.add_argument("file_b",      help="v2 text file")
    parser.add_argument("--json",      action="store_true")
    parser.add_argument("--sentences", action="store_true", help="Show sentence-level diff")
    parser.add_argument("--threshold", type=int, default=70)
    args = parser.parse_args()

    for f in [args.file_a, args.file_b]:
        if not Path(f).exists():
            print(f"ERROR: {f} not found"); sys.exit(1)

    text_a = Path(args.file_a).read_text(encoding="utf-8", errors="replace")
    text_b = Path(args.file_b).read_text(encoding="utf-8", errors="replace")

    banned     = load_banned_phrases()
    exceptions = load_exceptions()

    report_a   = analyse(text_a, banned, exceptions, args.threshold)
    report_b   = analyse(text_b, banned, exceptions, args.threshold)
    fixed, regressed = diff_reports(report_a, report_b)

    if args.json:
        print(json.dumps({
            "v1": report_a.to_dict(), "v2": report_b.to_dict(),
            "fixed": fixed, "regressed": regressed,
        }, indent=2))
    else:
        print_diff_report(report_a, report_b, fixed, regressed,
                          show_sents=args.sentences,
                          text_a=text_a, text_b=text_b)


if __name__ == "__main__":
    main()
