"""
config.py
=========
Load slop_config.yaml at startup.
Falls back to hardcoded defaults when the file is missing or PyYAML not installed.

Usage:
    from slop_lib.config import get_threshold, get_thresholds

    threshold = get_threshold()                      # respects slop_config.yaml
    threshold = get_threshold(field="biomedical")    # field profile
    threshold = get_threshold(venue="acl")           # venue override
"""

from __future__ import annotations
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional


# ── defaults (used when YAML unavailable) ────────────────────────────────────

_DEFAULTS: Dict[str, Any] = {
    "threshold": 70,
    "thresholds": {
        "rhythm_stdev":        7.0,
        "hedge_density":       3,
        "paragraph_shape_cv":  0.25,
        "echo_overlap":        0.50,
        "min_para_sentences":  3,
        "starter_entropy":     2.0,
        "passive_ratio_warn":  0.25,
        "passive_ratio_flag":  0.40,
        "passive_ratio_error": 0.55,
        "methods_verbs_warn":  10,
        "methods_verbs_flag":  20,
    },
    "weights": {
        "directness": 20, "rhythm": 20, "trust": 20,
        "authenticity": 20, "density": 20,
    },
}


def _config_path() -> Path:
    """Walk up from this file to find slop_config.yaml."""
    here = Path(__file__).parent
    for candidate in [here.parent / "slop_config.yaml",
                      here / "slop_config.yaml",
                      Path.cwd() / "slop_config.yaml"]:
        if candidate.exists():
            return candidate
    return here.parent / "slop_config.yaml"   # non-existent default path


@lru_cache(maxsize=None)
def _load_raw() -> Dict[str, Any]:
    """Load and cache the raw YAML config. Returns defaults on any failure."""
    path = _config_path()
    if not path.exists():
        return _DEFAULTS.copy()
    try:
        import yaml
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            return _DEFAULTS.copy()
        # Merge defaults with loaded values
        merged = _DEFAULTS.copy()
        merged.update(data)
        return merged
    except (ImportError, Exception):
        # PyYAML not installed or parse error — use defaults silently
        return _DEFAULTS.copy()


def get_threshold(field: Optional[str] = None, venue: Optional[str] = None) -> int:
    """Return the effective pass threshold, respecting field/venue overrides."""
    cfg = _load_raw()
    base = int(cfg.get("threshold", 70))

    if field:
        override = cfg.get("fields", {}).get(field, {}).get("threshold", base)
        base = int(override)

    if venue:
        override = cfg.get("venues", {}).get(venue, {}).get("threshold", base)
        base = int(override)

    return base


def get_thresholds(field: Optional[str] = None, venue: Optional[str] = None) -> Dict[str, Any]:
    """Return the merged detection thresholds dict."""
    cfg   = _load_raw()
    base  = dict(cfg.get("thresholds", _DEFAULTS["thresholds"]))

    if field:
        base.update(cfg.get("fields", {}).get(field, {}).get("thresholds", {}))

    if venue:
        base.update(cfg.get("venues", {}).get(venue, {}).get("thresholds", {}))

    return base


def get_weights() -> Dict[str, int]:
    """Return the scoring dimension weights."""
    return dict(_load_raw().get("weights", _DEFAULTS["weights"]))
