#!/usr/bin/env python3
"""ATS parser CLI — runs the full extraction + parsing + simulation pipeline.

This replaces the v5 regex-only `ats_parse_simulator.py`. The old script is
kept for backward compatibility but new use should call this one.

Usage:
    python -m scripts.ats_parser.cli <resume.pdf|docx|md|txt>
    python -m scripts.ats_parser.cli <resume.pdf> --platform workday
    python -m scripts.ats_parser.cli <resume.pdf> --json

Exit codes:
    0 — no blocker issues
    1 — at least one BLOCKER detected
    2 — bad usage
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .extractor import extract
from .parser import parse
from .simulator import simulate_all, simulate_one, Issue


def _issues_to_dicts(issues: list[Issue]) -> list[dict]:
    return [
        {"platform": i.platform, "severity": i.severity, "message": i.message, "fix": i.fix}
        for i in issues
    ]


def _print_human(extraction, parsed, by_platform):
    print("=" * 70)
    print(f"ATS Parser Report — extraction via {extraction.method} (fidelity: {extraction.fidelity})")
    print("=" * 70)
    for w in extraction.warnings:
        print(f"  [extraction] {w}")
    print()
    print(f"Sections found       : {parsed.section_canonicals}")
    print(f"Emails               : {parsed.contact.emails}")
    print(f"Phones               : {parsed.contact.phones}")
    print(f"LinkedIn             : {parsed.contact.linkedin}")
    print(f"GitHub               : {parsed.contact.github}")
    print(f"ORCID                : {parsed.contact.orcid}")
    print(f"Date ranges (good)   : {parsed.date_ranges_good}")
    print(f"Date ranges (ambig)  : {parsed.date_ranges_ambiguous}")
    print()

    blocker_count = 0
    for platform, issues in by_platform.items():
        if not issues:
            print(f"[{platform:12}]  no issues")
            continue
        print(f"[{platform:12}]  {len(issues)} issue(s)")
        for i in issues:
            marker = "❌" if i.severity == "BLOCKER" else ("⚠️ " if i.severity == "WARNING" else "ℹ️ ")
            print(f"    {marker} {i.severity}: {i.message}")
            print(f"          fix: {i.fix}")
            if i.severity == "BLOCKER":
                blocker_count += 1
    print()
    print("=" * 70)
    print(f"Summary: {blocker_count} BLOCKER(s) across all platforms.")
    print("=" * 70)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Realistic ATS parser simulator.")
    ap.add_argument("resume", help="Path to resume file (.pdf / .docx / .md / .txt)")
    ap.add_argument(
        "--platform",
        choices=["workday", "greenhouse", "taleo", "icims", "lever_ashby"],
        help="Run only one platform's simulator (default: all).",
    )
    ap.add_argument("--json", action="store_true", help="Emit JSON instead of human report.")
    args = ap.parse_args(argv)

    path = Path(args.resume)
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        return 2

    extraction = extract(path)
    parsed = parse(extraction.text)

    if args.platform:
        by_platform = {args.platform: simulate_one(parsed, args.platform)}
    else:
        by_platform = simulate_all(parsed)

    if args.json:
        out = {
            "extraction": {
                "method": extraction.method,
                "fidelity": extraction.fidelity,
                "warnings": extraction.warnings,
            },
            "sections": parsed.section_canonicals,
            "contact": {
                "emails": parsed.contact.emails,
                "phones": parsed.contact.phones,
                "linkedin": parsed.contact.linkedin,
                "github": parsed.contact.github,
                "orcid": parsed.contact.orcid,
            },
            "dates": {
                "good": parsed.date_ranges_good,
                "ambiguous": parsed.date_ranges_ambiguous,
            },
            "issues_by_platform": {k: _issues_to_dicts(v) for k, v in by_platform.items()},
        }
        print(json.dumps(out, indent=2))
    else:
        _print_human(extraction, parsed, by_platform)

    blocker_count = sum(
        1 for issues in by_platform.values() for i in issues if i.severity == "BLOCKER"
    )
    return 1 if blocker_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
