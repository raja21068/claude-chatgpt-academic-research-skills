#!/usr/bin/env python3
"""
build_corpus.py
===============
Extract section text from paper PDFs into corpus/ for extract_writing_style.py.

Usage:
    python build_corpus.py

Requirements:
    pip install pdfminer.six
    (or: pip install pymupdf)

Input:  pdfs/         — drop your published papers here
Output: corpus/       — one subfolder per paper, one .txt per section
"""

import re
import sys
from pathlib import Path

# Try pdfminer.six first, fall back to pymupdf
try:
    from pdfminer.high_level import extract_text as pdf_extract
    def read_pdf(path):
        return pdf_extract(str(path))
except ImportError:
    try:
        import fitz  # pymupdf
        def read_pdf(path):
            doc = fitz.open(str(path))
            return "\n".join(page.get_text() for page in doc)
    except ImportError:
        print("ERROR: install pdfminer.six or pymupdf: pip install pdfminer.six")
        sys.exit(1)

SECTION_PATTERNS = {
    "abstract":     [r"\babstract\b"],
    "introduction": [r"\bintroduction\b"],
    "methods":      [r"\b(methods?|methodology|approach)\b"],
    "results":      [r"\bresults?\b"],
    "discussion":   [r"\bdiscussion\b"],
    "conclusion":   [r"\bconclusion(s)?\b"],
}

SECTION_ORDER = ["abstract", "introduction", "methods", "results", "discussion", "conclusion"]

PDF_DIR    = Path("pdfs")
CORPUS_DIR = Path("corpus")
MIN_CHARS  = 200


def detect_sections(text):
    """Split text into rough section chunks by heading detection."""
    lines = text.split('\n')
    sections = {s: [] for s in SECTION_ORDER}
    current = None

    for line in lines:
        stripped = line.strip().lower()
        if len(stripped) < 60:  # headings are short
            for sec, patterns in SECTION_PATTERNS.items():
                if any(re.search(p, stripped, re.IGNORECASE) for p in patterns):
                    current = sec
                    break
        if current:
            sections[current].append(line)

    return {sec: '\n'.join(chunks).strip() for sec, chunks in sections.items()}


def process_pdf(pdf_path: Path, paper_id: str):
    print(f"  Processing: {pdf_path.name}")
    try:
        raw = read_pdf(pdf_path)
    except Exception as e:
        print(f"    ERROR reading {pdf_path.name}: {e}")
        return

    sections = detect_sections(raw)
    out_dir = CORPUS_DIR / paper_id
    out_dir.mkdir(parents=True, exist_ok=True)

    written = 0
    for sec, content in sections.items():
        if len(content) >= MIN_CHARS:
            (out_dir / f"{sec}.txt").write_text(content, encoding="utf-8")
            written += 1

    print(f"    → {written} sections written to corpus/{paper_id}/")


def main():
    if not PDF_DIR.exists():
        print(f"ERROR: {PDF_DIR}/ folder not found. Create it and add your PDF papers.")
        return

    pdfs = sorted(PDF_DIR.glob("*.pdf"))
    if not pdfs:
        print(f"No PDF files found in {PDF_DIR}/. Add your published papers there.")
        return

    CORPUS_DIR.mkdir(exist_ok=True)
    print(f"Found {len(pdfs)} PDFs in {PDF_DIR}/")

    for i, pdf in enumerate(pdfs):
        process_pdf(pdf, f"paper{i+1}")

    print(f"\nDone. Corpus written to {CORPUS_DIR}/")
    print("Next: run extract_writing_style.py")


if __name__ == "__main__":
    main()
