#!/usr/bin/env python3
"""
run.py — cross-platform launcher for paper-writing-agent.
Works on Windows, macOS, and Linux with just:  python run.py <command>

FIRST TIME SETUP
----------------
  python run.py setup       Install dependencies (run once)
  python run.py style       Build your personal writing style profile

    Step 1: Drop your published papers (PDF) into:
              scripts/pdfs/
    Step 2: Drop 2-3 papers from your target field (PDF) into:
              scripts/reference_papers/
    Step 3: Run:  python run.py style

CHECKING YOUR PAPERS
--------------------
  python run.py check  paper.txt      Score a plain-text paper
  python run.py check  paper.tex      Score a LaTeX paper (auto-strips)
  python run.py diff   v1.txt v2.txt  Compare two drafts

  Or just drop files in the input/ folder and double-click run.bat / run.sh

ALL COMMANDS
------------
  setup          Install all dependencies
  style          Build personal writing style from your published papers
  check  <file>  Full slop score report
  rewrite-ai <f> Rewrite with Claude API  (fixes passive voice + all 25 AI patterns)
  diff   <f1> <f2>  Compare two draft versions
  rhythm <file>  Rhythm-only check
  corpus <file>  Compare draft to your personal corpus baseline
  latex  <file>  LaTeX-aware check with section filters
  abstract <f>   Abstract structure and component check
  contrib  <f>   Contribution bullet analysis

REWRITE-AI OPTIONS
------------------
  --section NAME    Rewrite one section (abstract|introduction|methods|results|discussion|conclusion)
  --chunk-size N    Words per Claude API call (default 800)
  --model NAME      Claude model (default: claude-sonnet-4-6)
  --dry-run         Preview chunks without calling the API

  Requires: pip install anthropic  +  ANTHROPIC_API_KEY env var

OPTIONS (work with most commands)
----------------------------------
  --report        Show detailed rewrite hints
  --json          Machine-readable JSON output
  --threshold N   Minimum passing score (default from slop_config.yaml or 70)
  --field NAME    Field profile: cs_ai | biomedical | social_science
  --venue NAME    Venue profile: acl | neurips | arxiv

EXAMPLES
--------
  python run.py check  my_paper.txt
  python run.py check  my_paper.tex --report --field cs_ai
  python run.py check  my_paper.txt --threshold 80 --json
  python run.py diff   draft_v1.txt draft_v2.txt
  python run.py rhythm results_section.txt
  python run.py corpus draft.txt
"""

import sys
import os
import subprocess
from pathlib import Path

HERE     = Path(__file__).parent
SCRIPTS  = HERE / "scripts"
PDFS_DIR = SCRIPTS / "pdfs"
REFS_DIR = SCRIPTS / "reference_papers"
CORPUS   = SCRIPTS / "corpus"


# ── colour helpers (zero dependencies) ───────────────────────────────────────

def _c(code, text):
    if sys.stdout.isatty():
        return f"\033[{code}m{text}\033[0m"
    return text

def green(t):  return _c("1;32", t)
def red(t):    return _c("1;31", t)
def yellow(t): return _c("1;33", t)
def bold(t):   return _c("1",    t)
def cyan(t):   return _c("1;36", t)
def dim(t):    return _c("2",    t)


# ── dependency check ──────────────────────────────────────────────────────────

REQUIRED_PACKAGES = ["colorama", "nltk"]
OPTIONAL_PACKAGES = ["spacy"]
PDF_PACKAGES      = ["pdfminer.six"]   # for reading PDFs in style setup

def cmd_setup(args=None):
    print(bold("╔══════════════════════════════════════════════╗"))
    print(bold("║     Paper Writing Agent v6 — Setup              ║"))
    print(bold("╚══════════════════════════════════════════════╝"))
    print()

    print(bold("[1/4] Installing required packages..."))
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "--upgrade", "--quiet"]
        + REQUIRED_PACKAGES
    )
    print(green("  ✓ colorama, nltk installed"))

    print()
    print(bold("[2/4] Installing PDF reading support (for style setup)..."))
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--quiet"] + PDF_PACKAGES
        )
        print(green("  ✓ pdfminer.six installed"))
    except subprocess.CalledProcessError:
        print(yellow("  ⚠ pdfminer.six failed — PDF reading unavailable."))
        print(yellow("    Style setup will still work if you use .txt files."))

    print()
    print(bold("[3/4] Installing spaCy (optional — upgrades passive/tense accuracy to 95%)..."))
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--quiet"] + OPTIONAL_PACKAGES
        )
        subprocess.check_call(
            [sys.executable, "-m", "spacy", "download", "en_core_web_sm", "--quiet"]
        )
        print(green("  ✓ spaCy installed — passive voice and tense detection upgraded"))
    except subprocess.CalledProcessError:
        print(yellow("  ⚠ spaCy not installed (network issue or optional)."))
        print(yellow("    Regex fallback will be used (~65% accuracy)."))

    print()
    print(bold("[4/4] Downloading NLTK tokeniser data..."))
    subprocess.check_call([sys.executable, "-c",
        "import nltk; "
        "nltk.download('punkt', quiet=True); "
        "nltk.download('punkt_tab', quiet=True)"
    ])
    print(green("  ✓ NLTK data ready"))

    print()
    print(bold("═" * 50))
    print(green("Setup complete!"))
    print()
    print("Next step — build your personal writing style:")
    print()
    print(f"  1. Drop your published papers (PDF) into:")
    print(cyan(f"       {PDFS_DIR}"))
    print()
    print(f"  2. Drop 2-3 papers from your target field (PDF) into:")
    print(cyan(f"       {REFS_DIR}"))
    print()
    print(f"  3. Run:  {bold('python run.py style')}")
    print()
    print("Or skip step 1-3 and start checking papers immediately:")
    print(f"  {bold('python run.py check my_paper.txt')}")
    print(bold("═" * 50))


# ── style setup command ───────────────────────────────────────────────────────

def cmd_style(args=None):
    print(bold("╔══════════════════════════════════════════════╗"))
    print(bold("║     Paper Writing Agent v6 — Style Setup        ║"))
    print(bold("╚══════════════════════════════════════════════╝"))
    print()

    _check_deps()

    # Check what's available
    pdf_files = [f for f in PDFS_DIR.iterdir()
                 if f.suffix.lower() in (".pdf", ".txt")
                 and not f.name.startswith("PUT_")]

    ref_files = [f for f in REFS_DIR.iterdir()
                 if f.suffix.lower() in (".pdf", ".txt")
                 and not f.name.startswith("PUT_")]

    if not pdf_files and not ref_files:
        print(yellow("No papers found."))
        print()
        print("To build your personal writing style profile:")
        print()
        print(f"  1. Drop your published papers (PDF) into:")
        print(cyan(f"       {PDFS_DIR}"))
        print()
        print(f"  2. Drop 2-3 papers from your target field into:")
        print(cyan(f"       {REFS_DIR}"))
        print()
        print(f"  3. Run this command again:  {bold('python run.py style')}")
        print()
        print(dim("Tip: You can also use .txt files if you don't have PDFs"))
        return

    print(f"Found {len(pdf_files)} personal paper(s)")
    print(f"Found {len(ref_files)} field paper(s)")
    print()

    # Step 1: Build corpus from personal papers
    if pdf_files:
        print(bold("[1/3] Extracting text from your papers..."))
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "build_corpus.py")],
            cwd=str(SCRIPTS),
        )
        if result.returncode != 0:
            print(red("  ✗ build_corpus.py failed."))
            print(yellow("  Tip: Try converting your PDFs to .txt files first."))
        else:
            print(green("  ✓ Corpus built"))
    else:
        print(dim("[1/3] Skipped (no personal papers in scripts/pdfs/)"))

    # Step 2: Extract writing style
    corpus_has_content = any(
        f.suffix == ".txt"
        for f in CORPUS.rglob("*")
        if f.is_file() and not f.name.startswith(".")
    )

    print()
    if corpus_has_content:
        print(bold("[2/3] Generating your personal style profile..."))
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "extract_writing_style.py")],
            cwd=str(SCRIPTS),
        )
        if result.returncode == 0:
            style_path = HERE / "references" / "my_writing_style.md"
            print(green(f"  ✓ Written: references/my_writing_style.md"))
        else:
            print(red("  ✗ extract_writing_style.py failed."))
    else:
        print(dim("[2/3] Skipped (no corpus content — run build_corpus.py first)"))

    # Step 3: Extract domain vocabulary from field papers
    print()
    if ref_files:
        print(bold("[3/3] Generating field vocabulary profile..."))
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "extract_domain_vocabulary.py")],
            cwd=str(SCRIPTS),
        )
        if result.returncode == 0:
            print(green(f"  ✓ Written: references/domain_vocabulary.md"))
        else:
            print(red("  ✗ extract_domain_vocabulary.py failed."))
    else:
        print(dim("[3/3] Skipped (no field papers in scripts/reference_papers/)"))

    print()
    print(bold("═" * 50))
    style_exists = (HERE / "references" / "my_writing_style.md").exists()
    vocab_exists = (HERE / "references" / "domain_vocabulary.md").exists()

    if style_exists or vocab_exists:
        print(green("Style setup complete!"))
        print()
        if style_exists:
            print(f"  ✓ {cyan('references/my_writing_style.md')}")
            print(dim("    Used for: corpus comparison, rewrite agent"))
        if vocab_exists:
            print(f"  ✓ {cyan('references/domain_vocabulary.md')}")
            print(dim("    Used for: field vocabulary matching"))
        print()
        print(f"Now run:  {bold('python run.py check my_paper.txt')}")
        print(f"To compare your draft against your personal corpus baseline:")
        print(f"  {bold('python run.py corpus my_draft.txt')}")
    else:
        print(yellow("No style files were generated."))
        print("Check that your PDFs are readable and try again.")
    print(bold("═" * 50))


# ── file validation ───────────────────────────────────────────────────────────

def _require_file(path_str: str) -> Path:
    p = Path(path_str)
    if not p.exists():
        print(red(f"ERROR: file not found: {p}"))
        print()
        print(f"  Put your paper in the {bold('input/')} folder or give the full path.")
        print(f"  Example: python run.py check input/my_paper.txt")
        sys.exit(1)
    if p.stat().st_size == 0:
        print(red(f"ERROR: file is empty: {p}"))
        sys.exit(1)
    return p


def _check_deps():
    try:
        import colorama  # noqa
    except ImportError:
        print(yellow("WARNING: colorama not installed — no colour output."))
        print(f"  Fix: {bold('python run.py setup')}\n")
    if str(HERE) not in sys.path:
        sys.path.insert(0, str(HERE))


# ── script runner ─────────────────────────────────────────────────────────────

def run_script(script_name: str, extra_args: list):
    _check_deps()
    script = SCRIPTS / script_name
    if not script.exists():
        print(red(f"ERROR: script not found: {script}"))
        sys.exit(1)
    result = subprocess.run(
        [sys.executable, str(script)] + extra_args,
        cwd=str(HERE),
    )
    sys.exit(result.returncode)


# ── individual commands ───────────────────────────────────────────────────────

def cmd_check(args):
    if not args:
        print(red("Usage: python run.py check <paper.txt or paper.tex> [options]"))
        print()
        print("Options:")
        print("  --report          Show detailed rewrite hints")
        print("  --json            Machine-readable JSON")
        print("  --threshold N     Pass score (default 70)")
        print("  --field NAME      cs_ai | biomedical | social_science")
        print("  --venue NAME      acl | neurips | arxiv")
        sys.exit(1)
    _require_file(args[0])
    run_script("slop_score.py", args)


def cmd_diff(args):
    if len(args) < 2:
        print(red("Usage: python run.py diff <v1.txt> <v2.txt> [--sentences] [--json]"))
        sys.exit(1)
    _require_file(args[0])
    _require_file(args[1])
    run_script("slop_diff.py", args)


def cmd_rhythm(args):
    if not args:
        print(red("Usage: python run.py rhythm <paper.txt> [--json] [--fix-hints]"))
        sys.exit(1)
    _require_file(args[0])
    run_script("rhythm_check.py", args)


def cmd_corpus(args):
    if not args:
        print(red("Usage: python run.py corpus <draft.txt> [--section results]"))
        sys.exit(1)
    _require_file(args[0])
    corpus_dir = CORPUS
    has_content = any(
        f.suffix == ".txt"
        for f in corpus_dir.rglob("*")
        if f.is_file() and not f.name.startswith(".")
    )
    if not has_content:
        print(yellow("No personal corpus found."))
        print()
        print("Build your corpus first:")
        print(f"  1. Drop your published papers into: {cyan(str(PDFS_DIR))}")
        print(f"  2. Run: {bold('python run.py style')}")
        print()
        print("Then re-run this command.")
        sys.exit(1)
    run_script("corpus_compare.py", args)


def cmd_latex(args):
    if not args:
        print(red("Usage: python run.py latex <paper.tex> [--section results] [--report]"))
        sys.exit(1)
    _require_file(args[0])
    run_script("latex_slop.py", args)


def cmd_abstract(args):
    if not args:
        print(red("Usage: python run.py abstract <abstract.txt> [--limit 150]"))
        sys.exit(1)
    _require_file(args[0])
    run_script("abstract_scorer.py", args)


def cmd_contrib(args):
    if not args:
        print(red("Usage: python run.py contrib <draft.txt> [--abstract abstract.txt]"))
        sys.exit(1)
    _require_file(args[0])
    run_script("contribution_checker.py", args)


# ── rewrite-ai ────────────────────────────────────────────────────────────────

def cmd_rewrite_ai(args):
    if not args:
        print(red("Usage: python run.py rewrite-ai <paper.txt> [options]"))
        print()
        print("Options:")
        print("  --section NAME    Rewrite one section only:")
        print("                    abstract | introduction | methods | results | discussion | conclusion")
        print("  --chunk-size N    Words per API chunk (default 800)")
        print("  --model NAME      Claude model (default: claude-sonnet-4-6)")
        print("  --dry-run         Show chunks without calling the API")
        print("  --json            Print JSON summary")
        print()
        print("Requirements:")
        print("  pip install anthropic")
        print("  export ANTHROPIC_API_KEY=sk-ant-...   (or create .api_key file)")
        sys.exit(1)
    _require_file(args[0])
    run_script("rewrite_ai.py", args)


# ── help ──────────────────────────────────────────────────────────────────────

def cmd_help(args=None):
    print(__doc__)


# ── main ──────────────────────────────────────────────────────────────────────

COMMANDS = {
    "setup":        cmd_setup,
    "style":        cmd_style,
    "check":        cmd_check,
    "rewrite-ai":   cmd_rewrite_ai,
    "diff":         cmd_diff,
    "rhythm":       cmd_rhythm,
    "corpus":       cmd_corpus,
    "build-corpus": lambda a: run_script("build_corpus.py", a),
    "latex":        cmd_latex,
    "abstract":     cmd_abstract,
    "contrib":      cmd_contrib,
    "help":         cmd_help,
    "--help":       cmd_help,
    "-h":           cmd_help,
}

# Commands that take no file arguments
NO_ARG_COMMANDS = {"setup", "help", "--help", "-h"}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        cmd_help()
        if len(sys.argv) >= 2:
            print(red(f"Unknown command: {sys.argv[1]}"))
            print(f"Run  {bold('python run.py help')}  to see all commands.")
        sys.exit(0)

    command  = sys.argv[1]
    fn       = COMMANDS[command]
    cmd_args = sys.argv[2:]

    if command in NO_ARG_COMMANDS:
        fn()
    else:
        fn(cmd_args)


if __name__ == "__main__":
    main()
