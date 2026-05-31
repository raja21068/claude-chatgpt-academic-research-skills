#!/usr/bin/env python3
"""
latex_slop.py
=============
LaTeX-aware anti-AI slop checker.

Strips LaTeX commands, runs all slop checks on clean text, and maps
findings back to original .tex line numbers.

Usage:
    python latex_slop.py paper.tex
    python latex_slop.py paper.tex --section results
    python latex_slop.py paper.tex --json
    python latex_slop.py paper.tex --report
    python latex_slop.py paper.tex --threshold 75

Supported section filters: abstract, introduction, related_work, method,
                            results, analysis, conclusion, all
"""

import re
import sys
import json
import argparse
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent))

from slop_lib import analyse, load_banned_phrases, load_exceptions
from slop_lib.colors   import RED, YELLOW, GREEN, RESET, BOLD, CYAN
from slop_lib.text     import strip_latex, sent_tokenize
from slop_lib.report   import print_report

# ── section heading patterns ──────────────────────────────────────────────────

SECTION_PATTERNS: Dict[str, List[str]] = {
    "abstract":     [r"\\begin\{abstract\}", r"\\section\*?\{abstract\}"],
    "introduction": [r"\\section\*?\{introduction"],
    "related_work": [r"\\section\*?\{(related.work|background|prior.work|"
                     r"literature.review|related.studies|related.approaches)"],
    "method":       [r"\\section\*?\{(method|approach|model|framework|"
                     r"proposed.method|system|architecture|our.method|technique|"
                     r"methodology|overview|formulation)"],
    "results":      [r"\\section\*?\{(results?|experiments?|experimental|"
                     r"evaluation|empirical|quantitative|performance)"],
    "analysis":     [r"\\section\*?\{(analysis|ablation|discussion|"
                     r"qualitative|error.analysis|further.analysis|insight)"],
    "conclusion":   [r"\\section\*?\{(conclusion|summary|closing)"],
}


# ── section extraction ────────────────────────────────────────────────────────

def extract_sections(raw_tex: str) -> Dict[str, List[Tuple[int, str]]]:
    """Split .tex source into named sections with line numbers."""
    lines           = raw_tex.split("\n")
    sections        = defaultdict(list)
    current_section = "preamble"

    for lineno, line in enumerate(lines, 1):
        stripped_lower = line.strip().lower()

        if re.search(r'\\begin\{abstract\}', line, re.IGNORECASE):
            current_section = "abstract"
        elif re.search(r'\\end\{abstract\}', line, re.IGNORECASE):
            pass  # don't reset; next \section will take over

        for sec_name, patterns in SECTION_PATTERNS.items():
            if any(re.search(p, stripped_lower) for p in patterns):
                current_section = sec_name
                break

        sections[current_section].append((lineno, line))

    return sections


def section_to_sentences(section_lines: List[Tuple[int, str]]) -> List[Tuple[int, str]]:
    """
    Convert [(lineno, tex_line)] to [(lineno, clean_sentence)].
    LaTeX is stripped once per paragraph chunk (not redundantly per sentence).
    """
    result: List[Tuple[int, str]] = []
    current_para: List[Tuple[int, str]] = []
    start_lineno = section_lines[0][0] if section_lines else 1

    def flush(para: List[Tuple[int, str]], lineno: int) -> List[Tuple[int, str]]:
        if not para:
            return []
        raw   = " ".join(line for _, line in para)
        clean = strip_latex(raw)
        return [(lineno, s.strip()) for s in sent_tokenize(clean) if len(s.strip()) > 10]

    for lineno, line in section_lines:
        if line.strip() == "":
            result.extend(flush(current_para, start_lineno))
            current_para = []
        else:
            if not current_para:
                start_lineno = lineno
            current_para.append((lineno, line))

    result.extend(flush(current_para, start_lineno))
    return result


# ── per-section analysis ──────────────────────────────────────────────────────

def analyse_section(
    section_name: str,
    section_lines: List[Tuple[int, str]],
    banned: Dict[str, List[str]],
    exceptions: frozenset,
    threshold: int = 70,
) -> Optional[dict]:
    if not section_lines:
        return None

    # Join all lines, strip LaTeX once
    raw_text  = "\n".join(line for _, line in section_lines)
    clean     = strip_latex(raw_text)

    # Use the shared library's full analysis on the clean text
    report    = analyse(clean, banned, exceptions, threshold)

    # Also get line-number-annotated sentences for the editor hints
    sentences = section_to_sentences(section_lines)

    return {
        "section":    section_name,
        "score":      report.score,
        "passed":     report.passed,
        "phrase_hits": {k: v[:10] for k, v in report.phrase_hits.items()},
        "rhythm":     report.rhythm.to_dict(),
        # Line-number hints so the user can jump to the right place in their editor
        "line_hints": [
            {"line": ln, "sentence": s[:120]}
            for ln, s in sentences[:5]   # top-5 opening sentences as orientation
        ],
    }


# ── output ────────────────────────────────────────────────────────────────────

def print_section_report(r: dict, detailed: bool = False) -> None:
    score  = r["score"]
    colour = GREEN if score >= 75 else (YELLOW if score >= 50 else RED)
    print(f"\n{BOLD}── {r['section'].upper()} ──{RESET}  {colour}{score}/100{RESET}")

    for label, hits in r["phrase_hits"].items():
        if hits:
            print(f"  {RED}[{label.upper()} PHRASES]{RESET} ({len(hits)}): "
                  + ", ".join(f'"{p}"' for p in hits[:5]))

    rh = r["rhythm"]
    if rh.get("stdev_flag"):
        print(f"  {RED}[RHYTHM]{RESET} Mean StdDev {rh['mean_stdev']} — sentences too uniform.")
    if rh.get("zombie_nouns"):
        print(f"  {RED}[ZOMBIE NOUNS]{RESET}: " + ", ".join(f'"{z}"' for z in rh["zombie_nouns"][:5]))
    if rh.get("context_free_comparisons"):
        print(f"  {YELLOW}[CONTEXT-FREE COMPARE]{RESET}: "
              f"{rh['context_free_comparisons']} claim(s) without a named metric.")
    if rh.get("hedge_sentences"):
        print(f"  {RED}[HEDGING]{RESET} {len(rh['hedge_sentences'])} over-hedged sentence(s).")

    if detailed and r.get("line_hints"):
        print(f"\n  {CYAN}Line hints:{RESET}")
        for h in r["line_hints"]:
            print(f"    L{h['line']:>4}: {h['sentence']}")
    print()


def print_full_report(all_results: List[dict], threshold: int, detailed: bool) -> int:
    scores = [r["score"] for r in all_results]
    overall = sum(scores) // len(scores) if scores else 0

    colour = GREEN if overall >= threshold else RED
    print(f"\n{BOLD}══ LaTeX Slop Report ══{RESET}")
    print(f"  {colour}Overall average: {overall}/100{RESET}  "
          f"({'pass' if overall >= threshold else 'fail'})\n")

    for r in all_results:
        print_section_report(r, detailed)

    return overall


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="LaTeX-aware anti-AI slop checker")
    parser.add_argument("file",        help=".tex file to analyse")
    parser.add_argument("--section",   default="all",
                        help="Section filter: abstract|introduction|related_work|"
                             "method|results|analysis|conclusion|all")
    parser.add_argument("--json",      action="store_true")
    parser.add_argument("--report",    action="store_true", help="Full detail")
    parser.add_argument("--threshold", type=int, default=70)
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"ERROR: {path} not found"); sys.exit(1)

    raw_tex    = path.read_text(encoding="utf-8", errors="replace")
    sections   = extract_sections(raw_tex)
    banned     = load_banned_phrases()
    exceptions = load_exceptions()

    target     = args.section.lower().replace(" ", "_")
    to_analyse = (
        [(n, l) for n, l in sections.items() if n != "preamble"]
        if target == "all"
        else [(target, sections.get(target, []))]
    )

    all_results = []
    for sec_name, sec_lines in to_analyse:
        r = analyse_section(sec_name, sec_lines, banned, exceptions, args.threshold)
        if r:
            all_results.append(r)

    if not all_results:
        print("No content found for the requested section(s)."); sys.exit(0)

    if args.json:
        print(json.dumps(all_results, indent=2)); sys.exit(0)

    overall = print_full_report(all_results, args.threshold, args.report)
    sys.exit(0 if overall >= args.threshold else 1)


if __name__ == "__main__":
    main()
