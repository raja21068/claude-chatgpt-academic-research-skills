"""Per-platform ATS simulators.

Each function takes a ParsedResume and returns a list of platform-specific
issues. The rules encode what each ATS is known to mishandle — see
references/17-multi-ats-platform-awareness.md for the documentation.

The simulators are conservative: they flag what is likely to break, not what
might possibly break. Each issue has a severity (BLOCKER | WARNING | INFO).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .parser import ParsedResume


@dataclass
class Issue:
    platform: str
    severity: str  # BLOCKER | WARNING | INFO
    message: str
    fix: str


def _check_universal(parsed: ParsedResume) -> list[Issue]:
    """Issues that break parsing on every major ATS."""
    issues: list[Issue] = []

    if not parsed.contact.emails:
        issues.append(
            Issue(
                platform="universal",
                severity="BLOCKER",
                message="No email address found in the top of the resume.",
                fix="Add a clearly visible email on the first 5 lines of the body.",
            )
        )

    canonicals = set(parsed.section_canonicals)
    if "education" not in canonicals:
        issues.append(
            Issue(
                platform="universal",
                severity="BLOCKER",
                message="No 'Education' section detected.",
                fix="Add a section with a recognized heading: 'Education'.",
            )
        )
    if "experience" not in canonicals and "research_experience" not in canonicals:
        issues.append(
            Issue(
                platform="universal",
                severity="BLOCKER",
                message="No 'Experience' or 'Research Experience' section detected.",
                fix="Add a section with a recognized heading: 'Experience' or 'Research Experience'.",
            )
        )

    if parsed.date_ranges_ambiguous > 0:
        issues.append(
            Issue(
                platform="universal",
                severity="WARNING",
                message=f"{parsed.date_ranges_ambiguous} date range(s) in ambiguous format (e.g. 06/2024 or 2024-2025).",
                fix="Use 'Mon YYYY – Mon YYYY' format consistently (e.g. 'Jun 2024 – Jul 2025').",
            )
        )
    if parsed.date_ranges_good == 0 and parsed.date_ranges_ambiguous == 0:
        issues.append(
            Issue(
                platform="universal",
                severity="WARNING",
                message="No date ranges detected at all. ATSs may fail to build a chronological timeline.",
                fix="Add explicit 'Mon YYYY – Mon YYYY' to every role and degree.",
            )
        )

    return issues


def _check_workday(parsed: ParsedResume) -> list[Issue]:
    issues: list[Issue] = []
    # Workday is strict about standard section names. Project section is fine but not required.
    # It is particularly bad at multi-column layouts (we can't see layout from extracted text,
    # but if extraction interleaves unrelated content we'll see it as scrambled lines).
    # Check the experience section for plausible structure.
    has_experience = "experience" in parsed.section_canonicals
    has_research = "research_experience" in parsed.section_canonicals
    if has_research and not has_experience:
        issues.append(
            Issue(
                platform="workday",
                severity="INFO",
                message="Only 'Research Experience' present — Workday's parser strongly expects 'Experience' as the canonical heading.",
                fix="If this is an industry role on Workday, consider renaming to 'Experience' and keeping research roles inside it.",
            )
        )
    return issues


def _check_greenhouse(parsed: ParsedResume) -> list[Issue]:
    issues: list[Issue] = []
    # Greenhouse parses well — main risk is tokenization of skill names with unusual spacing.
    bad_token_variants = [("py torch", "PyTorch"), ("tensor flow", "TensorFlow"), ("sci kit", "scikit-learn")]
    text_low = parsed.raw_text.lower()
    for bad, good in bad_token_variants:
        if bad in text_low:
            issues.append(
                Issue(
                    platform="greenhouse",
                    severity="WARNING",
                    message=f"Found '{bad}' which tokenizes differently from '{good}'.",
                    fix=f"Use the canonical spelling: '{good}'.",
                )
            )
    return issues


def _check_taleo(parsed: ParsedResume) -> list[Issue]:
    issues: list[Issue] = []
    # Taleo rewards exact-phrase JD matches and is harsh on unexpanded acronyms.
    compliance = ["IRB", "HIPAA", "GCP", "GDPR", "PHI", "BAA", "DUA", "DPIA", "STROBE", "CONSORT", "TRIPOD", "FAIR"]
    for ac in compliance:
        idx = parsed.raw_text.find(ac)
        if idx == -1:
            continue
        # Look for "(AC)" expansion pattern within 80 chars before first use
        window = parsed.raw_text[max(0, idx - 80) : idx + len(ac) + 1]
        if f"({ac})" not in window:
            issues.append(
                Issue(
                    platform="taleo",
                    severity="WARNING",
                    message=f"Compliance acronym '{ac}' used without expansion. Taleo's keyword expander is unreliable.",
                    fix=f"Expand at first use, e.g. 'Institutional Review Board ({ac})'.",
                )
            )
    return issues


def _check_icims(parsed: ParsedResume) -> list[Issue]:
    issues: list[Issue] = []
    # iCIMS prefers a categorized Skills section. Flag if skills section is just a bare comma list.
    skills_sec = next(
        (s for s in parsed.sections if s.canonical in {"skills", "technical_skills"}),
        None,
    )
    if skills_sec and skills_sec.body:
        has_category_markers = ":" in skills_sec.body
        line_count = len([ln for ln in skills_sec.body.splitlines() if ln.strip()])
        if not has_category_markers and line_count <= 2:
            issues.append(
                Issue(
                    platform="icims",
                    severity="INFO",
                    message="Skills section is a flat list. iCIMS parses categorized skills better.",
                    fix="Categorize, e.g. 'Languages: Python, R\\nFrameworks: PyTorch, MONAI'.",
                )
            )
    return issues


def _check_lever_ashby(parsed: ParsedResume) -> list[Issue]:
    issues: list[Issue] = []
    # Lever/Ashby are light parsers; the cover letter weight is higher. INFO only.
    issues.append(
        Issue(
            platform="lever_ashby",
            severity="INFO",
            message="Lever and Ashby reviewers often read the cover letter directly.",
            fix="Make sure the cover letter exists, is specific, and leads with the strongest evidence.",
        )
    )
    return issues


_SIMULATORS: dict[str, Callable[[ParsedResume], list[Issue]]] = {
    "workday": _check_workday,
    "greenhouse": _check_greenhouse,
    "taleo": _check_taleo,
    "icims": _check_icims,
    "lever_ashby": _check_lever_ashby,
}


def simulate_all(parsed: ParsedResume) -> dict[str, list[Issue]]:
    """Run universal checks + every per-platform simulator."""
    result: dict[str, list[Issue]] = {"universal": _check_universal(parsed)}
    for name, fn in _SIMULATORS.items():
        result[name] = fn(parsed)
    return result


def simulate_one(parsed: ParsedResume, platform: str) -> list[Issue]:
    """Run universal checks + one specific platform's checks."""
    issues = _check_universal(parsed)
    fn = _SIMULATORS.get(platform.lower())
    if fn:
        issues.extend(fn(parsed))
    return issues
