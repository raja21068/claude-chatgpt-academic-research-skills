"""
constants.py
============
Single source of truth for every threshold, word set, and compiled regex.
All seven CLI scripts import from here — nothing is defined twice.
"""

import re

# ── thresholds ────────────────────────────────────────────────────────────────
# Defaults — overridden at runtime by slop_config.yaml via slop_lib.config.
# Import get_thresholds() to get the effective values for a given field/venue.

STDEV_THRESHOLD        = 7.0
HEDGE_THRESHOLD        = 3
MIN_PARA_SENTENCES     = 3
SHAPE_CV_THRESH        = 0.25
ECHO_OVERLAP_THRESH    = 0.50
STARTER_ENTROPY_THRESH = 2.0
DEFAULT_PASS_SCORE     = 70


def load_thresholds(field=None, venue=None):
    """
    Return live thresholds from slop_config.yaml (with field/venue overrides).
    Falls back to the module-level defaults when config is unavailable.

    Usage:
        from slop_lib.constants import load_thresholds
        t = load_thresholds(field="biomedical")
        hedge_limit = t["hedge_density"]
    """
    try:
        from slop_lib.config import get_thresholds
        return get_thresholds(field=field, venue=venue)
    except ImportError:
        return {
            "rhythm_stdev":        STDEV_THRESHOLD,
            "hedge_density":       HEDGE_THRESHOLD,
            "paragraph_shape_cv":  SHAPE_CV_THRESH,
            "echo_overlap":        ECHO_OVERLAP_THRESH,
            "min_para_sentences":  MIN_PARA_SENTENCES,
            "starter_entropy":     STARTER_ENTROPY_THRESH,
        }

# ── word sets ─────────────────────────────────────────────────────────────────

HEDGE_WORDS: frozenset = frozenset({
    "may", "might", "could", "potentially", "possibly", "perhaps",
    "appears", "appear", "seems", "seem", "seemingly", "arguably",
    "presumably", "likely", "suggest", "suggests", "suggested",
    "indicate", "indicates", "indicated", "imply", "implies", "implied",
    "somewhat", "relatively", "generally", "typically", "usually",
    "often", "tend", "tends", "tended",
})

ZOMBIE_NOUNS: dict = {
    "utilization":    "use",
    "utilisation":    "use",
    "implementation": "implement",
    "investigation":  "investigate",
    "optimization":   "optimize",
    "optimisation":   "optimize",
    "examination":    "examine",
    "consideration":  "consider",
    "determination":  "determine",
    "establishment":  "establish",
    "evaluation":     "evaluate",
    "demonstration":  "demonstrate",
    "presentation":   "present",
    "exploration":    "explore",
    "formulation":    "formulate",
    "computation":    "compute",
    "approximation":  "approximate",
}

STOP_WORDS: frozenset = frozenset({
    "the", "a", "an", "of", "in", "to", "and", "is", "are", "was",
    "were", "that", "this", "it", "with", "for", "on", "at", "by",
    "we", "our", "its", "be", "have",
})

OUR_SYSTEM_NOUNS: frozenset = frozenset({
    "model", "framework", "system", "approach", "method", "architecture",
    "network", "algorithm", "pipeline", "technique",
})

# ── compiled regexes (built once at import time) ──────────────────────────────

RE_COMPARISON_VERBS = re.compile(
    r'\b(outperforms?|surpasses?|exceeds?|beats?|better than|superior to)\b',
    re.IGNORECASE,
)

RE_SPECIFIC_REF = re.compile(
    r'\b(Table|Figure|\d+\.\d+|\d+\s*(points?|percent|%)|BLEU|ROUGE|F1)\b',
    re.IGNORECASE,
)

RE_PASSIVE = re.compile(
    r'\b(was|were|been|being|is|are)\s+\w+ed\b',
    re.IGNORECASE,
)

RE_WORDS = re.compile(r'\b\w+\b')
RE_PARA_SPLIT = re.compile(r'\n\s*\n')
RE_SENTENCE_SPLIT = re.compile(r'(?<=[.!?])\s+')
