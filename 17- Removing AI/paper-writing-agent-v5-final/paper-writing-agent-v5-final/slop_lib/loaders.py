"""
loaders.py
==========
Reference-file loaders.  Every function is cached so multiple scripts
running in the same process (or multiple checks on the same document)
pay the disk cost only once.
"""

import re
import json
from functools import lru_cache
from pathlib import Path
from typing import Dict, FrozenSet, List


# ── path resolution ───────────────────────────────────────────────────────────

def _ref_dir() -> Path:
    """Return the references/ directory relative to this package."""
    return Path(__file__).parent.parent / "references"


# ── loaders ───────────────────────────────────────────────────────────────────

@lru_cache(maxsize=None)
def load_banned_phrases() -> Dict[str, List[str]]:
    """
    Load banned phrases from phrases.md and academic_phrases.md.
    Returns {'generic': [...], 'academic': [...]}.
    structures.md is intentionally excluded (pattern descriptions, not phrases).
    """
    ref = _ref_dir()
    return {
        "generic":  _extract_phrases(ref / "phrases.md"),
        "academic": _extract_phrases(ref / "academic_phrases.md"),
    }


@lru_cache(maxsize=None)
def load_exceptions() -> FrozenSet[str]:
    """Load allowed-exception patterns from exceptions.md."""
    exc_file = _ref_dir() / "exceptions.md"
    if not exc_file.exists():
        return frozenset()
    text = exc_file.read_text(encoding="utf-8", errors="replace")
    patterns = re.findall(r'PATTERN:\s*(.+)', text, re.IGNORECASE)
    return frozenset(p.strip().lower() for p in patterns)


@lru_cache(maxsize=None)
def load_corpus_stats(corpus_dir: str) -> dict:
    """
    Load pre-built corpus statistics from corpus/stats.json if it exists.
    Returns an empty dict when no corpus has been built yet.
    """
    path = Path(corpus_dir) / "stats.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


# ── internal helpers ──────────────────────────────────────────────────────────

def _extract_phrases(md_path: Path) -> List[str]:
    """
    Pull quoted phrases from a markdown file.
    Handles both "..." and '...' delimiters plus | table-cell | patterns.
    """
    if not md_path.exists():
        return []
    text = md_path.read_text(encoding="utf-8", errors="replace")

    found: List[str] = []
    found += re.findall(r'[\u201c\u201d"]([^\u201c\u201d"]{5,80})[\u201c\u201d"]', text)
    found += re.findall(r"'([^']{5,80})'", text)
    found += re.findall(r'\|\s*"?([A-Z][^|"]{5,80})"?\s*\|', text)

    cleaned: List[str] = []
    seen = set()
    for p in found:
        p = p.strip().rstrip("\u2026").strip()
        low = p.lower()
        if 5 <= len(p) <= 80 and not p.startswith("#") and low not in seen:
            cleaned.append(low)
            seen.add(low)
    return cleaned
