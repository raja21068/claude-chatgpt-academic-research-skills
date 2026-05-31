"""
text.py
=======
Text processing helpers: tokenisation, LaTeX stripping, word counting.
One tokenisation pass at the document level feeds every downstream check.
"""

import re
from typing import List, Tuple

from .constants import RE_WORDS, RE_PARA_SPLIT, RE_SENTENCE_SPLIT, STOP_WORDS

# ── sentence tokeniser (NLTK optional) ───────────────────────────────────────

try:
    import nltk
    nltk.download("punkt",     quiet=True)
    nltk.download("punkt_tab", quiet=True)
    from nltk.tokenize import sent_tokenize as _nltk_sent_tokenize

    def sent_tokenize(text: str) -> List[str]:
        return _nltk_sent_tokenize(text)

except ImportError:
    def sent_tokenize(text: str) -> List[str]:
        return [s.strip() for s in RE_SENTENCE_SPLIT.split(text) if s.strip()]


# ── basic helpers ─────────────────────────────────────────────────────────────

def word_count(text: str) -> int:
    return len(RE_WORDS.findall(text))


def split_paragraphs(text: str) -> List[str]:
    """Split on one or more blank lines; drop empty paragraphs."""
    return [p.strip() for p in RE_PARA_SPLIT.split(text) if p.strip()]


def jaccard_overlap(a: str, b: str) -> float:
    """Content-word Jaccard similarity between two strings."""
    wa = {w for w in RE_WORDS.findall(a.lower()) if w not in STOP_WORDS}
    wb = {w for w in RE_WORDS.findall(b.lower()) if w not in STOP_WORDS}
    if not wa or not wb:
        return 0.0
    return len(wa & wb) / len(wa | wb)


def sentence_lengths(paragraph: str) -> Tuple[List[int], List[str]]:
    """Return (lengths_above_3_words, all_sentences) for a paragraph."""
    sents = sent_tokenize(paragraph)
    lengths = [word_count(s) for s in sents if word_count(s) > 3]
    return lengths, sents


# ── LaTeX stripping ───────────────────────────────────────────────────────────

# Replace citations/math with sentinel that won't count as a real word
_CITE_SENTINEL  = ""   # empty — keeps word counts clean
_MATH_SENTINEL  = ""

_RE_BEGIN_END   = re.compile(
    r'\\begin\{(equation|align|figure|table|tabular)[^}]*\}.*?\\end\{\1\}',
    re.DOTALL | re.IGNORECASE,
)
_RE_CITE        = re.compile(r'\\cite[tp]?\*?\{[^}]*\}')
_RE_REF         = re.compile(r'\\(ref|label|eqref)\{[^}]*\}')
_RE_MATH_INLINE = re.compile(r'\$[^$\n]{1,200}\$')
_RE_SECTION     = re.compile(
    r'\\(sub)*section\*?\{([^}]*)\}', re.IGNORECASE
)
_RE_TEXTCMD     = re.compile(
    r'\\(textbf|textit|emph|underline|text|mathrm|mathbf)\{([^}]*)\}'
)
_RE_CMD_NOARG   = re.compile(r'\\[a-zA-Z]+\*?\s*')
_RE_BRACES      = re.compile(r'[{}]')
_RE_WHITESPACE  = re.compile(r'\s+')


def strip_latex(text: str) -> str:
    """
    Remove LaTeX commands from .tex source and return clean prose.

    Strategy:
    1. Drop display math / figure / table environments entirely.
    2. Replace citations and cross-references with the empty sentinel.
    3. Replace inline math with the empty sentinel.
    4. Keep section heading text.
    5. Keep text inside formatting commands (textbf, emph, ...).
    6. Drop remaining commands and bare braces.
    7. Normalise whitespace.
    """
    text = _RE_BEGIN_END.sub("", text)
    text = _RE_CITE.sub(_CITE_SENTINEL, text)
    text = _RE_REF.sub(_CITE_SENTINEL, text)
    text = _RE_MATH_INLINE.sub(_MATH_SENTINEL, text)
    text = _RE_SECTION.sub(r'\2\n\n', text)
    text = _RE_TEXTCMD.sub(r'\2', text)       # keep inner text
    text = _RE_CMD_NOARG.sub(" ", text)
    text = _RE_BRACES.sub("", text)
    text = _RE_WHITESPACE.sub(" ", text)
    return text.strip()
