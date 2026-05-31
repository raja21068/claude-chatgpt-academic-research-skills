#!/usr/bin/env python3
"""
_runner.py — called by run.bat and run.sh
Double-click to run. No Python knowledge needed.
"""

import sys
import os
import subprocess
import importlib
from pathlib import Path

HERE   = Path(__file__).parent.resolve()
INPUT  = HERE / "input"
OUTPUT = HERE / "output"
PDFS   = HERE / "scripts" / "pdfs"


def green(t):  return f"\033[1;32m{t}\033[0m"
def red(t):    return f"\033[1;31m{t}\033[0m"
def yellow(t): return f"\033[1;33m{t}\033[0m"
def bold(t):   return f"\033[1m{t}\033[0m"
def cyan(t):   return f"\033[1;36m{t}\033[0m"
def hr():      print("─" * 50)


def ensure_deps():
    for pkg in ["colorama", "nltk"]:
        if not _importable(pkg):
            print(f"  Installing {pkg}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", pkg])
    try:
        import nltk; nltk.data.find("tokenizers/punkt")
    except Exception:
        import nltk
        nltk.download("punkt", quiet=True)
        nltk.download("punkt_tab", quiet=True)
    if str(HERE) not in sys.path:
        sys.path.insert(0, str(HERE))

def _importable(name):
    try: importlib.import_module(name); return True
    except ImportError: return False

def _has_user_pdfs():
    return any(
        f.suffix.lower() in (".pdf", ".txt") and not f.name.startswith("PUT_")
        for f in PDFS.iterdir()
    )

def collect_papers():
    return sorted(
        p for p in INPUT.iterdir()
        if p.suffix.lower() in (".txt", ".tex") and not p.name.startswith("PUT_")
    )


def main():
    print()
    print(bold("╔══════════════════════════════════════════╗"))
    print(bold("║       Paper Writing Agent v6             ║"))
    print(bold("║       Auto Rewriter                      ║"))
    print(bold("╚══════════════════════════════════════════╝"))
    print()

    ensure_deps()
    print(green("  ✓ Ready"))
    print()
    hr()
    print()

    papers = collect_papers()

    if not papers:
        print(yellow("  No papers found in the input/ folder."))
        print()
        print(bold("  How to use:"))
        print(f"    1. Copy your paper (.txt or .tex) into:")
        print(f"       {cyan(str(INPUT))}")
        print(f"    2. Double-click run.bat (Windows) or run.sh (Mac/Linux)")
        print(f"    3. Find your rewritten paper in the output/ folder")
        print()
        if not _has_user_pdfs():
            print(yellow("  Tip: add your own published papers to scripts/pdfs/"))
            print(yellow("       for more personalised feedback."))
            print()
        hr()
        input("\nPress Enter to close...")
        return

    print(f"  Found {len(papers)} paper(s): " + ", ".join(p.name for p in papers))
    print()

    from rewrite_runner import rewrite_paper
    from slop_lib.text  import strip_latex

    OUTPUT.mkdir(exist_ok=True)
    results = []

    for i, paper in enumerate(papers, 1):
        print(f"  [{i}/{len(papers)}]  {bold(paper.name)}")
        try:
            raw = paper.read_text(encoding="utf-8", errors="replace")
            if paper.suffix.lower() == ".tex":
                raw = strip_latex(raw)

            rewritten, changed, total, score_p1, score_final = rewrite_paper(raw)

            out = OUTPUT / f"{paper.stem}_rewritten.txt"
            out.write_text(rewritten, encoding="utf-8")

            print(f"          Score before : {score_p1}/100")
            print(f"          Score after  : {score_final}/100")
            print(f"          Changes      : {changed} patterns fixed")
            print(f"          Saved to     : {green('output/' + out.name)}")
            results.append((paper.name, score_p1, score_final, changed, total, True))

        except Exception as e:
            print(red(f"          ERROR: {e}"))
            results.append((paper.name, 0, 0, 0, 0, False))
        print()

    hr()
    print()
    print(bold("DONE"))
    print()

    for name, score_p1, score_final, changed, total, ok in results:
        if ok:
            delta = score_final - score_p1
            arrow = f"+{delta}" if delta >= 0 else str(delta)
            print(f"  {name}")
            print(f"    Score: {score_p1} → {score_final}/100  ({arrow} pts)")
            print(f"    Changes: {changed} patterns fixed")
            print(f"    File:  output/{Path(name).stem}_rewritten.txt")
        else:
            print(f"  {name}  {red('ERROR')}")
        print()

    print(yellow("  Tip: run  python run.py check output/<file>_rewritten.txt"))
    print(yellow("       to see what patterns still remain."))
    print()

    if not _has_user_pdfs():
        print(yellow("  Tip: add your own published papers to scripts/pdfs/"))
        print(yellow("       for more personalised feedback."))
        print()

    hr()
    input("Press Enter to close...")


if __name__ == "__main__":
    main()
