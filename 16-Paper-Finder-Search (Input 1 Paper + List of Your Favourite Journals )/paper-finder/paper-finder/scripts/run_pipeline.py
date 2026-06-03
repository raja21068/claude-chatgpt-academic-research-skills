#!/usr/bin/env python3
"""
Orchestrator: runs all paper-finder stages in order.

Stages run:
  0. resolve_venues.py    (skipped if venue_map.json already covers venues.csv)
  2. search_openalex.py
  3. rerank.py            (uses --api if ANTHROPIC_API_KEY is set, else --batches)
  4. expand_citations.py  (if --expand passed)
  3. rerank.py            (re-rank after expansion, only if --expand)
  5. export_bibtex.py

Requires $out/queries.json to exist beforehand. If using the skill inside Claude,
ask Claude to generate queries.json from your topic first (see SKILL.md Stage 1).
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
QUERIES = ROOT / "$out" / "queries.json"
VENUE_MAP = ROOT / "inputs" / "venue_map.json"


def run(name: str, *args: str) -> int:
    print(f"\n{'=' * 70}\n▶ {name} {' '.join(args)}\n{'=' * 70}")
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / name), *args],
        cwd=ROOT,
    )
    if result.returncode != 0:
        print(f"\n❌ {name} exited with status {result.returncode}")
    return result.returncode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--expand", action="store_true",
                    help="Run citation graph expansion (Stage 4) after initial re-rank")
    args = ap.parse_args()

    if not QUERIES.exists():
        print(f"❌ {QUERIES} not found.")
        print("   Create it first with your research topic and expanded queries.")
        print("   See SKILL.md Stage 1 for the recipe.")
        sys.exit(1)

    # Stage 0
    if not VENUE_MAP.exists():
        if run("resolve_venues.py") != 0:
            sys.exit(1)
    else:
        print(f"✓ Skipping resolve_venues — {VENUE_MAP.name} already exists.")

    # Stage 2
    if run("search_openalex.py") != 0:
        sys.exit(1)

    # Stage 3
    mode = "--api" if os.environ.get("ANTHROPIC_API_KEY") else "--batches"
    if run("rerank.py", mode) != 0:
        sys.exit(1)

    if mode == "--batches":
        print("\n" + "=" * 70)
        print("⏸  PAUSED for in-chat re-ranking.")
        print("=" * 70)
        print("Now hand the prompt files in $out/rerank_batches/ to Claude.")
        print("Save Claude's JSON responses to $out/rerank_responses/")
        print("Then run:")
        print("   python scripts/rerank.py --merge")
        if args.expand:
            print("   python scripts/expand_citations.py")
            print("   python scripts/rerank.py --batches    # re-rank expanded pool")
            print("   ...repeat the in-chat scoring step...")
            print("   python scripts/rerank.py --merge")
        print("   python scripts/export_bibtex.py")
        sys.exit(0)

    # Stage 4 (optional)
    if args.expand:
        if run("expand_citations.py") != 0:
            sys.exit(1)
        if run("rerank.py", "--api") != 0:
            sys.exit(1)

    # Stage 5
    if run("export_bibtex.py") != 0:
        sys.exit(1)

    print("\n" + "=" * 70)
    print("✅ Pipeline complete.")
    print("=" * 70)
    print(f"   BibTeX: {ROOT}/$out/final.bib")
    print(f"   CSV:    {ROOT}/$out/final.csv")


if __name__ == "__main__":
    main()
