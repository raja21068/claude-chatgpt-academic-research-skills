"""
report.py
=========
Report rendering — converts SlopReport → human-readable terminal output.
Entirely separated from computation so the library is usable without printing.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from .colors import RED, YELLOW, GREEN, RESET, BOLD
from .constants import STDEV_THRESHOLD, HEDGE_THRESHOLD

if TYPE_CHECKING:
    from .analysis    import SlopReport
from .linguistic  import LinguisticReport


def render_report(report: "SlopReport", detailed: bool = False) -> str:
    """Return the full terminal report as a string (use print() yourself)."""
    lines = []
    score = report.score
    r     = report.rhythm
    colour = GREEN if score >= 75 else (YELLOW if score >= 50 else RED)

    lines.append(f"\n{BOLD}══ Slop Score Report ══{RESET}")
    lines.append(
        f"  {colour}Overall: {score}/100{RESET}  "
        f"({'clean' if score >= 75 else 'borderline' if score >= 50 else 'AI-like'})\n"
    )

    lines.append(f"{BOLD}Dimension scores (20 = perfect):{RESET}")
    for dim, val in report.dimensions.items():
        bar = "█" * val + "░" * (20 - val)
        c   = GREEN if val >= 15 else (YELLOW if val >= 10 else RED)
        lines.append(f"  {dim:<14} {c}{val:>2}/20  {bar}{RESET}")

    lines.append(f"\n{BOLD}Issues found:{RESET}")
    any_issue = False

    for label, hits in report.phrase_hits.items():
        if hits:
            any_issue = True
            lines.append(f"  {RED}[{label.upper()} PHRASES]{RESET} {len(hits)} hit(s):")
            for h in hits[:5]:
                lines.append(f'    • "{h}"')
            if len(hits) > 5:
                lines.append(f"    … and {len(hits) - 5} more")

    if r.stdev_flag:
        any_issue = True
        lines.append(
            f"  {RED}[RHYTHM]{RESET} Mean sentence StdDev = {r.mean_stdev} "
            f"(threshold {STDEV_THRESHOLD}). Prose is metronomically uniform."
        )

    if r.hedge_sentences:
        any_issue = True
        lines.append(
            f"  {RED}[HEDGING]{RESET} {len(r.hedge_sentences)} sentence(s) with "
            f"≥{HEDGE_THRESHOLD} hedge words:"
        )
        for h in r.hedge_sentences[:3]:
            preview = h["sentence"][:100] + "…" if len(h["sentence"]) > 100 else h["sentence"]
            lines.append(f"    [{h['hedge_count']} hedges] \"{preview}\"")

    if r.echo_paragraphs:
        any_issue = True
        lines.append(
            f"  {YELLOW}[ECHO]{RESET} {len(r.echo_paragraphs)} paragraph(s) where "
            "last sentence mirrors first."
        )

    if r.shape_uniform:
        any_issue = True
        lines.append(
            f"  {YELLOW}[SHAPE]{RESET} Paragraph sentence counts are uniform "
            f"(CV={r.shape_cv}). Vary paragraph lengths."
        )

    if r.zombie_nouns:
        any_issue = True
        lines.append(
            f"  {RED}[ZOMBIE NOUNS]{RESET}: "
            + ", ".join(f'"{z}"' for z in r.zombie_nouns[:5])
        )

    if r.context_free_comparisons:
        any_issue = True
        lines.append(
            f"  {YELLOW}[CONTEXT-FREE COMPARE]{RESET}: "
            f"{r.context_free_comparisons} comparison(s) without named metric/baseline"
        )

    if r.synonym_drift:
        any_issue = True
        lines.append(
            f"  {YELLOW}[SYNONYM DRIFT]{RESET}: "
            + ", ".join(f'"our {w}"' for w in r.synonym_drift)
            + " — pick one name for your system"
        )

    if r.starter_entropy is not None and r.starter_entropy < 2.0:
        any_issue = True
        dominated = (
            f" Dominant: {r.starter_dominated}" if r.starter_dominated else ""
        )
        lines.append(
            f"  {YELLOW}[STARTERS]{RESET} Low sentence-initial entropy "
            f"({r.starter_entropy:.2f} bits).{dominated}"
        )

    for issue in r.punctuation_issues:
        any_issue = True
        lines.append(f"  {YELLOW}[PUNCTUATION]{RESET} {issue}")

    # linguistic findings (passive voice, tense, agency)
    if report.linguistic:
        ling = report.linguistic
        method_tag = f"[spaCy]" if ling.method == "spacy" else "[regex fallback]"
        if ling.passive_hits:
            any_issue = True
            lines.append(
                f"  {RED}[PASSIVE VOICE]{RESET} {method_tag} "
                f"{len(ling.passive_hits)} passive sentence(s):"
            )
            for h in ling.passive_hits[:3]:
                preview = h.sentence[:100] + "…" if len(h.sentence) > 100 else h.sentence
                verb    = f" ({h.verb})" if h.verb else ""
                lines.append(f'    • "{preview}"{verb}')
        if ling.tense_issues:
            any_issue = True
            lines.append(
                f"  {YELLOW}[TENSE]{RESET} {method_tag} "
                f"{len(ling.tense_issues)} tense inconsistency(ies):"
            )
            for t in ling.tense_issues[:3]:
                preview = t.sentence[:100] + "…" if len(t.sentence) > 100 else t.sentence
                lines.append(f'    • [{t.detected_tense} ≠ expected {t.expected_tense}] "{preview}"')
        if ling.method == "regex":
            lines.append(
                f"  {YELLOW}[TIP]{RESET} Install spaCy for 95% accurate passive/tense detection: "
                f"pip install spacy && python -m spacy download en_core_web_sm"
            )

    # AI pattern findings
    ai_any = _render_ai_patterns(report, lines)
    if ai_any:
        any_issue = True

    # Humanizer findings
    hum_any = _render_humanizer(report, lines)
    if hum_any:
        any_issue = True

    if not any_issue:
        lines.append(f"  {GREEN}No issues detected.{RESET}")

    if detailed and r.hedge_sentences:
        lines.append(f"\n{BOLD}Hedge rewrite hints:{RESET}")
        for i, h in enumerate(r.hedge_sentences[:4], 1):
            lines.append(f"\n  [{i}] {h['sentence'][:120]}")
            lines.append("      → State what the evidence shows + one scope qualifier if needed.")
            lines.append("         Pattern: '[Subject] [verb] [specific result] in [specific setting].'")

    lines.append("")
    return "\n".join(lines)


def print_report(report: "SlopReport", detailed: bool = False) -> None:
    print(render_report(report, detailed))


def _render_ai_patterns(report, lines):
    """Append AI pattern findings to lines list."""
    from .colors import RED, YELLOW, GREEN, RESET
    if not report.ai_patterns:
        return False
    ap = report.ai_patterns
    any_issue = False

    if ap.passive_worst > 0.25:
        any_issue = True
        pct = f"{ap.passive_worst*100:.0f}%"
        colour = RED if ap.passive_worst > 0.40 else YELLOW
        label = "very high" if ap.passive_worst > 0.55 else ("high" if ap.passive_worst > 0.40 else "elevated")
        lines.append(
            f"  {colour}[PASSIVE RATIO]{RESET} {label} — worst section {pct} passive "
            f"(overall {ap.passive_overall*100:.0f}%). "
            "AI writes methods in passive. Rewrite: 'We measured X' not 'X was measured'."
        )
        for sec, info in ap.passive_sections.items():
            if isinstance(info, dict) and info.get("ratio", 0) > 0.35:
                lines.append(
                    f"    → {sec}: {info['ratio']*100:.0f}% passive "
                    f"({info['passive_count']} of {info['sent_count']} sentences)"
                )

    if ap.methods_verb_count > 10:
        any_issue = True
        colour = RED if ap.methods_verb_count > 20 else YELLOW
        examples = ", ".join(f'"{v}"' for v in ap.methods_verb_examples[:5])
        extra = f" +{ap.methods_verb_count-5} more" if ap.methods_verb_count > 5 else ""
        lines.append(
            f"  {colour}[AI METHODS VERBS]{RESET} {ap.methods_verb_count} passive procedure verbs: "
            f"{examples}{extra}"
        )

    for label, data in ap.formulaic_phrases.items():
        if data["count"] >= 3:
            any_issue = True
            label_str = label.replace("_", " ").upper()
            examples = ", ".join(f'"{e}"' for e in data["examples"][:4])
            lines.append(f"  {YELLOW}[{label_str}]{RESET} {data['count']} hit(s): {examples}")

    return any_issue


def _render_humanizer(report, lines) -> bool:
    """Append humanizer findings to lines list."""
    from .colors import RED, YELLOW, GREEN, RESET
    if not report.humanizer:
        return False
    h = report.humanizer
    any_issue = False

    if h.ai_vocab_count > 3:
        any_issue = True
        colour = RED if h.ai_vocab_count > 15 else YELLOW
        examples = ", ".join(f'"{w}"' for w in h.ai_vocab_examples[:6])
        lines.append(
            f"  {colour}[AI VOCABULARY]{RESET} {h.ai_vocab_count} hit(s): {examples}\n"
            f"    → Replace with plainer alternatives (e.g. 'crucial'→'important', "
            f"'showcase'→'show', 'leverage'→'use')."
        )

    if h.ai_phrase_count > 1:
        any_issue = True
        colour = RED if h.ai_phrase_count > 8 else YELLOW
        examples = ", ".join(f'"{p}"' for p in h.ai_phrase_examples[:5])
        lines.append(
            f"  {colour}[AI PHRASES]{RESET} {h.ai_phrase_count} formulaic phrase(s): {examples}\n"
            f"    → These are statistical AI fingerprints. Rewrite to be specific."
        )

    if h.em_dash_count > 2:
        any_issue = True
        lines.append(
            f"  {YELLOW}[EM DASHES]{RESET} {h.em_dash_count} spaced em dashes — "
            f"humans use commas/semicolons. Auto-fixed by rewriter."
        )

    if h.autofix_count > 0:
        any_issue = True
        lines.append(
            f"  {YELLOW}[FILLER PATTERNS]{RESET} {h.autofix_count} removable filler phrase(s) found "
            f"(e.g. 'It is important to note that', 'In order to'). "
            f"Run rewriter to auto-fix."
        )

    return any_issue
