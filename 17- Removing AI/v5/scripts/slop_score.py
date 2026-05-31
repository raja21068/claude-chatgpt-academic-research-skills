#!/usr/bin/env python3
"""
slop_score.py
=============
Combined anti-AI slop scorer for academic prose.

Usage:
    python slop_score.py <section.txt>
    python slop_score.py <section.txt> --json
    python slop_score.py <section.txt> --report
    python slop_score.py <section.txt> --threshold 75
"""

import sys
import json
import argparse
from pathlib import Path

# Add parent to path so slop_lib resolves when run directly from scripts/
sys.path.insert(0, str(Path(__file__).parent.parent))

from slop_lib import analyse, load_banned_phrases, load_exceptions
from slop_lib.colors import GREEN, RED, RESET
from slop_lib.report import print_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Combined anti-AI slop scorer")
    parser.add_argument("file",        help="Text file to score")
    parser.add_argument("--json",      action="store_true", help="JSON output")
    parser.add_argument("--report",    action="store_true", help="Full detailed report")
    parser.add_argument("--threshold", type=int, default=70,
                        help="Minimum passing score (default 70)")
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"ERROR: {path} not found"); sys.exit(1)

    text = path.read_text(encoding="utf-8", errors="replace").strip()
    if len(text) < 50:
        print("ERROR: file too short"); sys.exit(1)

    report = analyse(
        text,
        banned     = load_banned_phrases(),
        exceptions = load_exceptions(),
        threshold  = args.threshold,
    )

    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print_report(report, detailed=args.report)
        verdict = f"{GREEN}PASS{RESET}" if report.passed else f"{RED}FAIL{RESET}"
        print(f"  Verdict: {verdict} (threshold {args.threshold})\n")

    sys.exit(0 if report.passed else 1)


if __name__ == "__main__":
    main()
