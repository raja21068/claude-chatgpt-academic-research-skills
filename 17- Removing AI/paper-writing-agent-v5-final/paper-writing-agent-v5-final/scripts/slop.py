#!/usr/bin/env python3
"""
slop — unified CLI for the paper-writing-agent slop checkers.

Subcommands:
    slop check  <file.txt>               # full score report
    slop check  <file.tex>  --latex      # LaTeX-aware check
    slop diff   <v1.txt> <v2.txt>        # compare two drafts
    slop rhythm <file.txt>               # rhythm-only analysis
    slop corpus <draft.txt>              # compare to personal corpus

Run  slop <subcommand> --help  for per-command options.
"""

import sys
import argparse
from pathlib import Path

# Allow running as a standalone script
sys.path.insert(0, str(Path(__file__).parent.parent))


def cmd_check(args) -> int:
    from slop_lib import analyse, load_banned_phrases, load_exceptions
    from slop_lib.colors  import GREEN, RED, RESET
    from slop_lib.report  import print_report
    from slop_lib.text    import strip_latex

    path = Path(args.file)
    if not path.exists():
        print(f"ERROR: {path} not found"); return 1

    text = path.read_text(encoding="utf-8", errors="replace").strip()
    if args.latex or path.suffix == ".tex":
        from slop_lib.text import strip_latex
        text = strip_latex(text)

    from slop_lib.config import get_threshold
    threshold = args.threshold if args.threshold is not None else get_threshold(
        field=getattr(args, "field", None),
        venue=getattr(args, "venue", None),
    )
    report = analyse(text, load_banned_phrases(), load_exceptions(), threshold)

    if args.json:
        import json; print(json.dumps(report.to_dict(), indent=2))
    else:
        print_report(report, detailed=args.report)
        verdict = f"{GREEN}PASS{RESET}" if report.passed else f"{RED}FAIL{RESET}"
        print(f"  Verdict: {verdict} (threshold {args.threshold})\n")

    return 0 if report.passed else 1


def cmd_diff(args) -> int:
    import json
    from slop_lib import analyse, load_banned_phrases, load_exceptions

    for f in [args.file_a, args.file_b]:
        if not Path(f).exists():
            print(f"ERROR: {f} not found"); return 1

    text_a = Path(args.file_a).read_text(encoding="utf-8", errors="replace")
    text_b = Path(args.file_b).read_text(encoding="utf-8", errors="replace")
    banned, exceptions = load_banned_phrases(), load_exceptions()
    ra = analyse(text_a, banned, exceptions, args.threshold)
    rb = analyse(text_b, banned, exceptions, args.threshold)

    # Import and run the diff logic from slop_diff.py
    sys.path.insert(0, str(Path(__file__).parent))
    from slop_diff import diff_reports, print_diff_report
    fixed, regressed = diff_reports(ra, rb)

    if args.json:
        print(json.dumps({"v1": ra.to_dict(), "v2": rb.to_dict(),
                          "fixed": fixed, "regressed": regressed}, indent=2))
    else:
        print_diff_report(ra, rb, fixed, regressed,
                          show_sents=args.sentences, text_a=text_a, text_b=text_b)
    return 0


def cmd_rhythm(args) -> int:
    import json
    from slop_lib.analysis import analyse_rhythm

    path = Path(args.file)
    if not path.exists():
        print(f"ERROR: {path} not found"); return 1

    r = analyse_rhythm(path.read_text(encoding="utf-8", errors="replace"))

    if args.json:
        print(json.dumps(r.to_dict(), indent=2))
    else:
        sys.path.insert(0, str(Path(__file__).parent))
        from rhythm_check import print_rhythm_report
        print_rhythm_report(r, show_hints=args.fix_hints)
    return 0


def cmd_corpus(args) -> int:
    import json
    sys.path.insert(0, str(Path(__file__).parent))
    from corpus_compare import compute_stats, load_corpus_stats, print_comparison

    path = Path(args.draft)
    if not path.exists():
        print(f"ERROR: {path} not found"); return 1

    text   = path.read_text(encoding="utf-8", errors="replace").strip()
    corpus = load_corpus_stats(args.section)
    if not corpus:
        print("ERROR: corpus/ not found. Run build_corpus.py first."); return 1

    draft = compute_stats(text)
    if args.json:
        print(json.dumps({"draft": draft, "corpus": corpus}, indent=2))
    else:
        print_comparison(draft, corpus)
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="slop",
        description="Anti-AI slop checker for academic prose.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # ── check ────────────────────────────────────────────────────────────────
    p_check = sub.add_parser("check", help="Full slop score report")
    p_check.add_argument("file",        help="Text or .tex file")
    p_check.add_argument("--latex",     action="store_true", help="Force LaTeX stripping")
    p_check.add_argument("--json",      action="store_true")
    p_check.add_argument("--report",    action="store_true", help="Show detailed rewrite hints")
    p_check.add_argument("--threshold", type=int, default=None,
                        help="Pass score (default from slop_config.yaml or 70)")
    p_check.add_argument("--field",     default=None,
                        help="Field profile: cs_ai | biomedical | social_science")
    p_check.add_argument("--venue",     default=None,
                        help="Venue profile: acl | neurips | arxiv")

    # ── diff ─────────────────────────────────────────────────────────────────
    p_diff = sub.add_parser("diff", help="Compare two draft versions")
    p_diff.add_argument("file_a",     help="v1 text file")
    p_diff.add_argument("file_b",     help="v2 text file")
    p_diff.add_argument("--sentences", action="store_true")
    p_diff.add_argument("--json",      action="store_true")
    p_diff.add_argument("--threshold", type=int, default=70)

    # ── rhythm ───────────────────────────────────────────────────────────────
    p_rhythm = sub.add_parser("rhythm", help="Rhythm-only analysis")
    p_rhythm.add_argument("file")
    p_rhythm.add_argument("--json",      action="store_true")
    p_rhythm.add_argument("--fix-hints", action="store_true")

    # ── corpus ───────────────────────────────────────────────────────────────
    p_corpus = sub.add_parser("corpus", help="Compare draft to personal corpus baseline")
    p_corpus.add_argument("draft")
    p_corpus.add_argument("--section", default=None)
    p_corpus.add_argument("--json",    action="store_true")

    args    = parser.parse_args()
    handler = {"check": cmd_check, "diff": cmd_diff,
               "rhythm": cmd_rhythm, "corpus": cmd_corpus}
    sys.exit(handler[args.command](args))


if __name__ == "__main__":
    main()
