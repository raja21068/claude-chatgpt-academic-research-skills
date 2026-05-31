"""
stats.py
========
Pure statistical helpers — stdev, mean, coefficient of variation, entropy.
No I/O, no side effects.
"""

import math
from collections import Counter
from typing import Sequence


def mean(vals: Sequence[float]) -> float:
    if not vals:
        return 0.0
    return sum(vals) / len(vals)


def stdev(vals: Sequence[float]) -> float:
    if len(vals) < 2:
        return 0.0
    m = mean(vals)
    return math.sqrt(sum((v - m) ** 2 for v in vals) / len(vals))


def coeff_of_variation(vals: Sequence[float]) -> float:
    """Standard deviation / mean, safe against zero mean."""
    m = mean(vals)
    if m < 1e-9:
        return 0.0
    return stdev(vals) / m


def shannon_entropy(items: Sequence[str]) -> float:
    """Shannon entropy in bits over a sequence of string tokens."""
    if not items:
        return 0.0
    counts = Counter(items)
    total = sum(counts.values())
    return -sum((c / total) * math.log2(c / total) for c in counts.values())
