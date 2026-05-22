"""Structural parser — detects sections, contact info, dates, and skills.

This mirrors how ATS platforms parse extracted resume text. They typically:
  1. Find section headers via a known dictionary.
  2. Extract structured fields (email, phone, URLs).
  3. Walk each section and pull tokens (job titles, dates, skill mentions).
  4. Score the resume against the JD's keyword list.

This module produces a structured `ParsedResume` object that downstream code
can score, render, or audit.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

# Canonical sections recognized across major ATSs
SECTION_ALIASES: dict[str, str] = {
    # Canonical: aliases
    "contact": ["contact", "contact information", "contact details"],
    "summary": ["summary", "professional summary", "profile", "objective", "about me"],
    "experience": [
        "experience", "work experience", "professional experience",
        "employment", "employment history", "work history", "career history",
    ],
    "research_experience": ["research experience", "research"],
    "education": ["education", "academic background", "educational background"],
    "skills": ["skills", "core competencies", "competencies", "key skills"],
    "technical_skills": ["technical skills", "technologies", "tech skills"],
    "projects": ["projects", "selected projects", "key projects", "personal projects"],
    "publications": ["publications", "selected publications", "papers"],
    "certifications": ["certifications", "certificates", "credentials"],
    "awards": ["awards", "honors", "honours", "awards and honors", "recognition"],
    "leadership": ["leadership", "leadership experience", "activities"],
    "languages": ["languages", "spoken languages"],
    "volunteer": ["volunteer", "volunteer experience", "community"],
    "references": ["references"],
}

# Build reverse lookup
_ALIAS_TO_CANONICAL: dict[str, str] = {}
for canon, aliases in SECTION_ALIASES.items():
    for a in aliases:
        _ALIAS_TO_CANONICAL[a.lower()] = canon

EMAIL_RE = re.compile(r"\b[\w._%+-]+@[\w.-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(r"(?:\+?\d{1,3}[\s.-]?)?\(?\d{2,4}\)?[\s.-]?\d{3,4}[\s.-]?\d{3,4}")
URL_RE = re.compile(r"https?://[\w./\-?=&%#:+~]+")
LINKEDIN_RE = re.compile(r"(?:linkedin\.com/in/|/in/)[\w\-]+", re.IGNORECASE)
GITHUB_RE = re.compile(r"github\.com/[\w\-]+", re.IGNORECASE)
ORCID_RE = re.compile(r"\b\d{4}-\d{4}-\d{4}-\d{3}[\dX]\b")

# Date forms
DATE_RANGE_GOOD = re.compile(
    r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}\s*"
    r"[–\-—]+\s*"
    r"(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}|Present|Current|Now|Expected\s+\w+\s*\d{0,4})",
    re.IGNORECASE,
)
DATE_AMBIGUOUS = re.compile(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b|\b(?<!\d)\d{4}\s*[–\-—]\s*\d{4}(?!\d)\b")


@dataclass
class ContactInfo:
    emails: list[str] = field(default_factory=list)
    phones: list[str] = field(default_factory=list)
    urls: list[str] = field(default_factory=list)
    linkedin: Optional[str] = None
    github: Optional[str] = None
    orcid: Optional[str] = None


@dataclass
class Section:
    canonical: str           # e.g. "experience"
    raw_heading: str         # the text as it appeared
    start_line: int
    end_line: int
    body: str


@dataclass
class ParsedResume:
    raw_text: str
    contact: ContactInfo
    sections: list[Section]
    section_canonicals: list[str]   # ordered list of canonical names found
    date_ranges_good: int
    date_ranges_ambiguous: int
    extracted_tokens: list[str]      # for skill matching
    raw_lines: list[str]


def parse(text: str) -> ParsedResume:
    """Parse extracted text into a structured ParsedResume."""
    lines = text.splitlines()
    contact = _extract_contact(text)
    sections = _split_sections(lines)
    good = len(DATE_RANGE_GOOD.findall(text))
    ambig = len(DATE_AMBIGUOUS.findall(text)) - good  # ambiguous regex may overlap good
    ambig = max(0, ambig)
    tokens = _tokenize_for_skill_match(text)
    return ParsedResume(
        raw_text=text,
        contact=contact,
        sections=sections,
        section_canonicals=[s.canonical for s in sections],
        date_ranges_good=good,
        date_ranges_ambiguous=ambig,
        extracted_tokens=tokens,
        raw_lines=lines,
    )


def _extract_contact(text: str) -> ContactInfo:
    # Focus on the top of the document where contact normally lives
    head = "\n".join(text.splitlines()[:30])
    info = ContactInfo()
    info.emails = list(set(EMAIL_RE.findall(head)))
    # Filter clearly-not-phones (years, dates)
    info.phones = [p for p in PHONE_RE.findall(head) if not re.fullmatch(r"\d{4}", p.strip())]
    info.urls = list(set(URL_RE.findall(text)))
    li_match = LINKEDIN_RE.search(text)
    if li_match:
        info.linkedin = li_match.group(0)
    gh_match = GITHUB_RE.search(text)
    if gh_match:
        info.github = gh_match.group(0)
    orcid_match = ORCID_RE.search(text)
    if orcid_match:
        info.orcid = orcid_match.group(0)
    return info


def _looks_like_heading(line: str) -> Optional[str]:
    """Return the canonical section name if this line is a heading, else None."""
    raw = line.strip()
    if not raw:
        return None
    # Strip Markdown ATX heading marks
    cleaned = raw.lstrip("#").strip().rstrip(":").strip().lower()
    # Strip surrounding bold/italic markdown
    cleaned = cleaned.strip("*_ ")
    # ATSs treat all-caps or title-case short lines as headings
    if len(cleaned) > 60:
        return None
    return _ALIAS_TO_CANONICAL.get(cleaned)


def _split_sections(lines: list[str]) -> list[Section]:
    sections: list[Section] = []
    current_canon: Optional[str] = None
    current_raw: str = ""
    current_start = 0
    current_body: list[str] = []

    def _flush(end_line: int) -> None:
        nonlocal current_canon, current_raw, current_start, current_body
        if current_canon is not None:
            sections.append(
                Section(
                    canonical=current_canon,
                    raw_heading=current_raw,
                    start_line=current_start,
                    end_line=end_line,
                    body="\n".join(current_body).strip(),
                )
            )
        current_body = []

    for i, line in enumerate(lines):
        heading = _looks_like_heading(line)
        if heading is not None:
            _flush(i - 1)
            current_canon = heading
            current_raw = line.strip()
            current_start = i
        else:
            if current_canon is not None:
                current_body.append(line)

    _flush(len(lines) - 1)
    return sections


# Word-boundary tokenization for skill matching
# Lowercased, keeps internal hyphens and dots (e.g., "node.js", "c++" tricky — see below)
_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9+#./\-]{1,}")


def _tokenize_for_skill_match(text: str) -> list[str]:
    """Produce a token list for skill matching.

    We keep some punctuation that's meaningful in skill names (`.`, `-`, `+`, `#`)
    so 'node.js', 'c++', 'c#', 'scikit-learn' survive intact.
    """
    return [m.group(0).lower() for m in _TOKEN_RE.finditer(text)]


def find_skill_mentions(parsed: ParsedResume, skill: str) -> list[tuple[int, str]]:
    """Find every line where a skill is mentioned. Case-insensitive, whole-phrase."""
    skill_low = skill.lower()
    hits: list[tuple[int, str]] = []
    for i, line in enumerate(parsed.raw_lines):
        if skill_low in line.lower():
            hits.append((i, line.strip()))
    return hits


def skill_strength(parsed: ParsedResume, skill: str) -> str:
    """Heuristic skill-strength label.

    Returns one of: strong | partial | weak | missing.

    Logic:
      - missing: zero mentions.
      - partial: mentioned only inside a Skills/Technical Skills section.
      - weak: mentioned in summary OR adjacent vocabulary (substring match only).
      - strong: mentioned inside an Experience/Projects/Research bullet.
    """
    hits = find_skill_mentions(parsed, skill)
    if not hits:
        return "missing"

    # Map line numbers to which section they're in
    line_section: dict[int, str] = {}
    for sec in parsed.sections:
        for ln in range(sec.start_line, sec.end_line + 1):
            line_section[ln] = sec.canonical

    saw_strong = False
    saw_partial = False
    saw_weak = False

    for line_no, _ in hits:
        sec = line_section.get(line_no, "")
        if sec in {"experience", "research_experience", "projects", "publications"}:
            saw_strong = True
        elif sec in {"skills", "technical_skills"}:
            saw_partial = True
        else:
            saw_weak = True

    if saw_strong:
        return "strong"
    if saw_partial:
        return "partial"
    if saw_weak:
        return "weak"
    return "missing"
