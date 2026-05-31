"""
slop_lib — shared library for the paper-writing-agent slop checkers.

Public API:
    from slop_lib import analyse, SlopReport
    from slop_lib.loaders import load_banned_phrases, load_exceptions
    from slop_lib.report import print_report
"""

from .analysis import analyse, SlopReport, RhythmReport
from .loaders  import load_banned_phrases, load_exceptions
from .config   import get_threshold, get_thresholds

__all__ = [
    "analyse",
    "SlopReport",
    "RhythmReport",
    "load_banned_phrases",
    "load_exceptions",
    "get_threshold",
    "get_thresholds",
]

__version__ = "5.0.0"
