#!/usr/bin/env python3
"""
extract_domain_vocabulary.py
============================
Extract current field terminology from 2-3 reference papers (top venue papers in your target field).
Outputs references/domain_vocabulary.md.

Usage:
    python extract_domain_vocabulary.py

Input:  reference_papers/  — drop 2-3 recent top-venue field papers here
Output: ../references/domain_vocabulary.md
"""

import re
from pathlib import Path
from collections import Counter

try:
    from pdfminer.high_level import extract_text as pdf_extract
except ImportError:
    try:
        import fitz
        def pdf_extract(path):
            doc = fitz.open(str(path))
            return "\n".join(page.get_text() for page in doc)
    except ImportError:
        import sys
        print("ERROR: pip install pdfminer.six")
        sys.exit(1)

REF_DIR    = Path("reference_papers")
OUTPUT     = Path("../references/domain_vocabulary.md")
MIN_WORD   = 4   # ignore short words
MIN_COUNT  = 3   # minimum frequency

# Common English stop-words to ignore
STOP = set("""
a about above after again all also am an and any are aren't as at be because been before
being below between both but by can't cannot could couldn't did didn't do does doesn't doing
don't down during each few for from further get got had hadn't has hasn't have haven't having
he he'd he'll he's her here here's hers herself him himself his how how's i i'd i'll i'm i've
if in into is isn't it it's its itself let's me more most mustn't my myself no nor not of off
on once only or other ought our ours ourselves out over own same shan't she she'd she'll she's
should shouldn't so some such than that that's the their theirs them themselves then there
there's these they they'd they'll they're they've this those through to too under until up
very was wasn't we we'd we'll we're we've were weren't what what's when when's where where's
which while who who's whom why why's will with won't would wouldn't you you'd you'll you're
you've your yours yourself yourselves
""".split())


def extract_terms(text):
    words = re.findall(r"\b[a-zA-Z][a-zA-Z\-]+[a-zA-Z]\b", text)
    words = [w.lower() for w in words if len(w) >= MIN_WORD and w.lower() not in STOP]
    # also extract 2-gram phrases
    bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)
               if len(words[i]) > 3 and len(words[i+1]) > 3]
    return Counter(words), Counter(bigrams)


def main():
    if not REF_DIR.exists() or not list(REF_DIR.glob("*.pdf")):
        print(f"Add 2-3 recent field papers to {REF_DIR}/ then re-run.")
        return

    all_unigrams, all_bigrams = Counter(), Counter()
    for pdf in sorted(REF_DIR.glob("*.pdf")):
        print(f"  Reading: {pdf.name}")
        try:
            text = pdf_extract(str(pdf))
            u, b = extract_terms(text)
            all_unigrams += u
            all_bigrams += b
        except Exception as e:
            print(f"    ERROR: {e}")

    top_terms   = [w for w, c in all_unigrams.most_common(80)  if c >= MIN_COUNT]
    top_phrases = [p for p, c in all_bigrams.most_common(50)   if c >= MIN_COUNT]

    lines = [
        "# Domain Vocabulary",
        "",
        "*Auto-generated from reference papers in `scripts/reference_papers/`.*",
        "*Use these terms when drafting to sound native to the field.*",
        "",
        "---",
        "",
        "## High-frequency field terms",
        "",
    ]
    for term in top_terms:
        lines.append(f"- {term}")

    lines += [
        "",
        "## Common phrases / collocations",
        "",
    ]
    for phrase in top_phrases:
        lines.append(f"- {phrase}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text('\n'.join(lines), encoding="utf-8")
    print(f"\n✓ Written: {OUTPUT}")


if __name__ == "__main__":
    main()
