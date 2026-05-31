#!/usr/bin/env python3
"""
_runner.py
==========
Called by run.bat (Windows) and run.sh (macOS/Linux).
Users never edit this file — it is the engine behind double-click operation.

What it does:
  1. Auto-installs missing dependencies
  2. Shows a clear menu on first run (no papers yet / style not set up)
  3. Scans input/ for .txt and .tex files
  4. Runs the full slop check on each paper
  5. Writes a plain-text report to output/<paper_name>_report.txt
  6. Prints a summary with score and next-step instructions
"""

import sys
import os
import re
import subprocess
import importlib
from pathlib import Path

HERE    = Path(__file__).parent.resolve()
INPUT   = HERE / "input"
OUTPUT  = HERE / "output"
SCRIPTS = HERE / "scripts"
PDFS    = SCRIPTS / "pdfs"
REFS    = SCRIPTS / "reference_papers"
CORPUS  = SCRIPTS / "corpus"


# ── colour helpers ────────────────────────────────────────────────────────────

def green(t):  return f"\033[1;32m{t}\033[0m" if sys.stdout.isatty() else t
def red(t):    return f"\033[1;31m{t}\033[0m" if sys.stdout.isatty() else t
def yellow(t): return f"\033[1;33m{t}\033[0m" if sys.stdout.isatty() else t
def bold(t):   return f"\033[1m{t}\033[0m"    if sys.stdout.isatty() else t
def cyan(t):   return f"\033[1;36m{t}\033[0m" if sys.stdout.isatty() else t
def dim(t):    return f"\033[2m{t}\033[0m"    if sys.stdout.isatty() else t

def hr(char="─"):
    print(char * 58)


# ── step 1: auto-install dependencies ────────────────────────────────────────

REQUIRED = ["colorama", "nltk"]

def ensure_deps():
    missing = [p for p in REQUIRED if not _importable(p)]
    if missing:
        print(bold(f"Installing: {', '.join(missing)} ..."))
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--quiet"] + missing
        )

    try:
        import nltk
        nltk.data.find("tokenizers/punkt")
    except Exception:
        import nltk
        nltk.download("punkt",     quiet=True)
        nltk.download("punkt_tab", quiet=True)

    if str(HERE) not in sys.path:
        sys.path.insert(0, str(HERE))


def _importable(name):
    try:
        importlib.import_module(name.replace("-", "_").replace(".", "_"))
        return True
    except ImportError:
        return False


# ── step 2: first-run guide ───────────────────────────────────────────────────

def _has_style_profile():
    return (HERE / "references" / "my_writing_style.md").exists() and \
           (HERE / "references" / "my_writing_style.md").stat().st_size > 200

def _has_corpus():
    return any(
        f.suffix == ".txt"
        for f in CORPUS.rglob("*")
        if f.is_file() and not f.name.startswith(".")
    )

def _user_pdfs():
    return [f for f in PDFS.iterdir()
            if f.suffix.lower() in (".pdf", ".txt")
            and not f.name.startswith("PUT_")]

def _ref_pdfs():
    return [f for f in REFS.iterdir()
            if f.suffix.lower() in (".pdf", ".txt")
            and not f.name.startswith("PUT_")]

def show_first_run_guide():
    """Show when the user hasn't set up their style profile yet."""
    print()
    print(bold("┌─────────────────────────────────────────────────┐"))
    print(bold("│          PERSONAL STYLE SETUP (optional)        │"))
    print(bold("└─────────────────────────────────────────────────┘"))
    print()
    print("For the most accurate feedback, add your published papers")
    print("so the tool learns YOUR writing style.")
    print()
    print(bold("Step 1 — Add your published papers:"))
    print(f"  Folder: {cyan(str(PDFS))}")
    print(f"  Format: PDF or .txt   |   Recommended: 3–10 papers")
    print()
    print(bold("Step 2 — Add papers from your target field:"))
    print(f"  Folder: {cyan(str(REFS))}")
    print(f"  Format: PDF or .txt   |   Recommended: 2–3 papers")
    print()
    print(bold("Step 3 — Build the style profile:"))
    print(f"  Run: {cyan('python run.py style')}")
    print()
    print(dim("(You can skip this and check papers now — generic rules apply.)"))
    print()
    hr()


# ── step 3: collect papers to check ──────────────────────────────────────────

def collect_papers():
    return sorted(
        p for p in INPUT.iterdir()
        if p.suffix.lower() in (".txt", ".tex")
        and not p.name.startswith("PUT_")
    )


# ── step 4: analyse one paper ─────────────────────────────────────────────────

def analyse_paper(path: Path) -> tuple:
    from slop_lib        import analyse, load_banned_phrases, load_exceptions
    from slop_lib.text   import strip_latex
    from slop_lib.report import render_report
    from slop_lib.config import get_threshold

    text = path.read_text(encoding="utf-8", errors="replace").strip()
    if not text:
        return 0, "ERROR: file is empty."

    if path.suffix.lower() == ".tex":
        text = strip_latex(text)

    threshold = get_threshold()
    report = analyse(
        text,
        banned       = load_banned_phrases(),
        exceptions   = load_exceptions(),
        threshold    = threshold,
        section_name = "",
    )

    rendered = render_report(report, detailed=True)
    plain    = _strip_ansi(rendered)

    verdict  = "PASS" if report.passed else "FAIL"
    plain   += f"\n  Verdict: {verdict} (threshold {threshold})\n"
    plain   += f"\n{'='*58}\n"
    plain   += "Score breakdown:\n"
    for dim, val in report.dimensions.items():
        bar   = "█" * val + "░" * (20 - val)
        plain += f"  {dim:<14} {val:>2}/20  {bar}\n"

    # Next-step hints tailored to what failed
    plain += _next_steps(report)

    return report.score, plain


def _next_steps(report) -> str:
    lines = ["\n" + "="*58 + "\nWHAT TO FIX NEXT\n" + "="*58]

    r  = report.rhythm
    ai = report.ai_patterns
    lg = report.linguistic

    if r.zombie_nouns:
        lines.append(f"\n• ZOMBIE NOUNS ({len(r.zombie_nouns)} found)")
        lines.append(  "  Replace noun phrases with verbs:")
        for z in r.zombie_nouns[:3]:
            from slop_lib.constants import ZOMBIE_NOUNS
            fix = ZOMBIE_NOUNS.get(z, "verb form")
            lines.append(f"    \"{z}\" → \"{fix}\"")

    if r.hedge_sentences:
        lines.append(f"\n• HEDGE STACKING ({len(r.hedge_sentences)} sentence(s))")
        lines.append(  "  Reduce to 1 hedge per sentence max.")
        lines.append(  "  Pattern: '[Finding]. [Scope if needed.]'")
        for h in r.hedge_sentences[:2]:
            lines.append(f"    [{h['hedge_count']} hedges] {h['sentence'][:80]}")

    if ai and ai.passive_worst > 0.25:
        lines.append(f"\n• PASSIVE VOICE RATIO ({ai.passive_worst*100:.0f}% in worst section)")
        lines.append(  "  Rewrite procedure sentences with active voice:")
        lines.append(  "    Before: 'The model was trained on 100K examples.'")
        lines.append(  "    After:  'We trained the model on 100K examples.'")

    if r.context_free_comparisons:
        lines.append(f"\n• CONTEXT-FREE COMPARISONS ({r.context_free_comparisons} found)")
        lines.append(  "  Always name the metric, dataset, and baseline:")
        lines.append(  "    Before: 'Our model outperforms all baselines.'")
        lines.append(  "    After:  'Our model outperforms BERT by 2.1 BLEU on WMT-22.'")

    if r.synonym_drift:
        lines.append(f"\n• SYNONYM DRIFT: {r.synonym_drift}")
        lines.append(  "  Pick ONE name for your system and use it throughout.")

    if report.phrase_hits.get("academic"):
        lines.append(f"\n• ACADEMIC AI PHRASES ({len(report.phrase_hits['academic'])} found)")
        lines.append(  "  See references/academic_phrases.md for replacements.")

    if not lines[1:]:
        lines.append("\n✓ No priority fixes — review the full report above for minor issues.")

    lines.append("\n" + "="*58)
    return "\n".join(lines)


def _strip_ansi(text: str) -> str:
    return re.sub(r'\x1b\[[0-9;]*m', '', text)


# ── step 5: write output report ───────────────────────────────────────────────

def write_report(paper: Path, score: int, report_text: str) -> Path:
    OUTPUT.mkdir(exist_ok=True)
    from slop_lib.config import get_threshold
    threshold = get_threshold()
    out = OUTPUT / f"{paper.stem}_report.txt"
    header = (
        f"SLOP CHECK REPORT\n"
        f"{'='*58}\n"
        f"Paper     : {paper.name}\n"
        f"Score     : {score}/100  "
        f"({'PASS' if score >= threshold else 'FAIL'} at threshold {threshold})\n"
        f"Generated : {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        f"{'='*58}\n\n"
    )
    out.write_text(header + report_text, encoding="utf-8")
    return out


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    print()
    print(bold("╔══════════════════════════════════════════════╗"))
    print(bold("║     Paper Writing Agent — Slop Checker       ║"))
    print(bold("╚══════════════════════════════════════════════╝"))
    print()

    print(bold("[ 1/3 ] Checking dependencies..."))
    ensure_deps()
    print(green("  ✓ Ready"))

    # Show style setup guide if not done yet
    if not _has_style_profile():
        show_first_run_guide()
    else:
        print(green("  ✓ Personal style profile found"))
    print()

    print(bold("[ 2/3 ] Scanning input/ folder..."))
    papers = collect_papers()

    if not papers:
        hr()
        print()
        print(yellow("  No papers found in the input/ folder."))
        print()
        print(bold("  How to check a paper:"))
        print(f"    1. Copy your paper (.txt or .tex) into:  {cyan(str(INPUT))}")
        print(f"    2. Run this script again")
        print()
        print(bold("  Accepted formats:"))
        print("    .txt — plain text (paste your paper text)")
        print("    .tex — LaTeX source (commands stripped automatically)")
        print()
        print(bold("  Example:"))
        print(f"    Copy  my_paper.txt  →  {INPUT}")
        print(f"    Then double-click  run.bat  (Windows) or  ./run.sh  (Mac/Linux)")
        print()
        hr()
        input("\nPress Enter to close...")
        return

    print(f"  Found {len(papers)} paper(s): "
          + ", ".join(p.name for p in papers))
    print()

    print(bold(f"[ 3/3 ] Analysing papers..."))
    print()
    hr()

    results = []
    for i, paper in enumerate(papers, 1):
        print(f"  [{i}/{len(papers)}] {bold(paper.name)}")
        try:
            score, report_text = analyse_paper(paper)
            out_path = write_report(paper, score, report_text)

            from slop_lib.config import get_threshold
            threshold = get_threshold()
            colour  = green if score >= 75 else (yellow if score >= 50 else red)
            verdict = green("PASS ✓") if score >= threshold else red("FAIL ✗")
            print(f"         Score:  {colour(str(score) + '/100')}  {verdict}")
            print(f"         Report: {dim(str(out_path.name))}")
            results.append((paper.name, score, score >= threshold, out_path))
        except Exception as e:
            print(red(f"         ERROR: {e}"))
            results.append((paper.name, 0, False, None))
        print()

    hr()
    print()
    print(bold("SUMMARY"))
    print()
    for name, score, passed, out_path in results:
        colour  = green if score >= 70 else red
        verdict = green("PASS ✓") if passed else red("FAIL ✗")
        print(f"  {name:<38} {colour(f'{score:>3}/100')}  {verdict}")

    print()
    failing = [(n, s, p) for n, s, ok, p in results if not ok]
    if failing:
        print(yellow("Next steps for failing papers:"))
        for name, score, out_path in failing:
            stem = Path(name).stem
            print()
            print(f"  {bold(name)} (score: {score}/100)")
            print(f"    1. Open:  {cyan(f'output/{stem}_report.txt')}")
            print(f"    2. Fix the issues listed under 'WHAT TO FIX NEXT'")
            print(f"    3. Save your paper and run this script again")
    else:
        print(green("All papers passed! ✓"))

    if not _has_style_profile() and _user_pdfs():
        print()
        print(yellow("Tip: You have PDFs in scripts/pdfs/ but haven't built your style profile."))
        print(f"     Run:  {bold('python run.py style')}  for personalised feedback.")

    print()
    hr()
    input("Press Enter to close...")


if __name__ == "__main__":
    main()
