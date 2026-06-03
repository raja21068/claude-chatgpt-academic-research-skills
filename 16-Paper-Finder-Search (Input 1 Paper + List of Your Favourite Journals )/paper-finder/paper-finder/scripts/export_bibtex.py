#!/usr/bin/env python3
"""
Stage 5: Export ranked papers as BibTeX and CSV.

Reads $out/ranked.jsonl, writes $out/final.bib and $out/final.csv.

BibTeX keys: firstauthor_year_firstword  (e.g. "zhu_2020_heterophily").
Compatible with the paper-writing-agent skill's [CITATION_POOL] format.
"""
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RANKED = ROOT / "$out" / "ranked.jsonl"
FINAL_BIB = ROOT / "$out" / "final.bib"
FINAL_CSV = ROOT / "$out" / "final.csv"

STOPWORDS = {
    "a", "an", "the", "of", "and", "or", "for", "to", "in", "on", "with",
    "by", "from", "is", "are", "be", "via", "using", "toward", "towards",
}


def safe_ascii(s: str) -> str:
    """Strip diacritics and non-ASCII for stable BibTeX keys."""
    import unicodedata
    return "".join(
        c for c in unicodedata.normalize("NFKD", s)
        if not unicodedata.combining(c)
    ).encode("ascii", "ignore").decode("ascii")


def first_content_word(title: str) -> str:
    for tok in re.findall(r"[A-Za-z]+", title):
        if tok.lower() not in STOPWORDS and len(tok) > 2:
            return tok.lower()
    return "paper"


def first_author_surname(authors: list[str]) -> str:
    if not authors:
        return "anon"
    name = safe_ascii(authors[0])
    parts = name.strip().split()
    if not parts:
        return "anon"
    surname = parts[-1]
    return re.sub(r"[^A-Za-z]", "", surname).lower() or "anon"


def make_key(rec: dict, taken: set[str]) -> str:
    base = f"{first_author_surname(rec.get('authors', []))}_{rec.get('year', 'nd')}_{first_content_word(rec.get('title', ''))}"
    key = base
    i = 2
    while key in taken:
        key = f"{base}_{i}"
        i += 1
    taken.add(key)
    return key


def latex_escape(s: str) -> str:
    """Minimal escaping for BibTeX field values."""
    if s is None:
        return ""
    s = str(s)
    replacements = [
        ("\\", r"\textbackslash{}"),
        ("&", r"\&"),
        ("%", r"\%"),
        ("$", r"\$"),
        ("#", r"\#"),
        ("_", r"\_"),
        ("{", r"\{"),
        ("}", r"\}"),
        ("~", r"\textasciitilde{}"),
        ("^", r"\textasciicircum{}"),
    ]
    # Do backslash first so subsequent escapes don't double-escape it
    for old, new in replacements:
        s = s.replace(old, new)
    return s


def bibtex_entry(key: str, rec: dict) -> str:
    title = latex_escape(rec.get("title", ""))
    authors = " and ".join(rec.get("authors", []) or ["Anonymous"])
    authors = latex_escape(authors)
    venue = latex_escape(rec.get("venue") or "")
    year = rec.get("year") or ""
    doi = rec.get("doi") or ""

    # Use @inproceedings for conferences, @article otherwise
    venue_lower = (rec.get("venue") or "").lower()
    is_conf = any(
        kw in venue_lower for kw in
        ["conference", "proceedings", "neurips", "icml", "iclr", "cvpr",
         "iccv", "eccv", "acl", "emnlp", "naacl", "aaai", "ijcai", "kdd"]
    )
    entry_type = "inproceedings" if is_conf else "article"
    venue_field = "booktitle" if is_conf else "journal"

    lines = [f"@{entry_type}{{{key},"]
    lines.append(f"  title     = {{{title}}},")
    lines.append(f"  author    = {{{authors}}},")
    lines.append(f"  {venue_field:9s} = {{{venue}}},")
    lines.append(f"  year      = {{{year}}},")
    if doi:
        lines.append(f"  doi       = {{{doi}}},")
    lines.append("}")
    return "\n".join(lines)


def main():
    if not RANKED.exists():
        print(f"❌ {RANKED} not found. Run rerank.py first.")
        sys.exit(1)

    records = [json.loads(line) for line in RANKED.open()]
    if not records:
        print(f"⚠ {RANKED} is empty.")
        sys.exit(0)

    # BibTeX
    taken: set[str] = set()
    entries = []
    keyed = []
    for rec in records:
        key = make_key(rec, taken)
        keyed.append((key, rec))
        entries.append(bibtex_entry(key, rec))

    FINAL_BIB.write_text("\n\n".join(entries) + "\n", encoding="utf-8")
    print(f"💾 Wrote {len(entries)} entries to {FINAL_BIB}")

    # CSV
    with open(FINAL_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "rank", "bibkey", "relevance", "title", "year", "venue",
            "citations", "doi", "url", "authors", "reason",
        ])
        for rank, (key, rec) in enumerate(keyed, 1):
            url = f"https://doi.org/{rec['doi']}" if rec.get("doi") else rec.get("openalex_url", "")
            w.writerow([
                rank, key, rec.get("relevance", ""), rec.get("title", ""),
                rec.get("year", ""), rec.get("venue", ""),
                rec.get("cited_by_count", 0), rec.get("doi", ""), url,
                "; ".join(rec.get("authors", [])),
                rec.get("relevance_reason", ""),
            ])
    print(f"💾 Wrote {len(keyed)} rows to {FINAL_CSV}")


if __name__ == "__main__":
    main()
