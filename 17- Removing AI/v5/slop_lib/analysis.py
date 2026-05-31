"""
analysis.py
===========
Core analysis engine.  Pure computation — no I/O, no printing.

Entry point: analyse(text) → SlopReport

All v4 checks are integrated here directly (not monkey-patched on top).
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .constants import (
    STDEV_THRESHOLD, HEDGE_THRESHOLD, MIN_PARA_SENTENCES,
    SHAPE_CV_THRESH, ECHO_OVERLAP_THRESH, STARTER_ENTROPY_THRESH,
    HEDGE_WORDS, ZOMBIE_NOUNS, OUR_SYSTEM_NOUNS,
    RE_COMPARISON_VERBS, RE_SPECIFIC_REF, RE_WORDS,
)
from .stats      import stdev, mean, coeff_of_variation, shannon_entropy
from .text       import sent_tokenize, word_count, split_paragraphs, jaccard_overlap
from .linguistic  import analyse_linguistic, LinguisticReport, spacy_available
from .ai_patterns  import analyse_ai_patterns, AIPatternReport
from .humanizer   import humanizer_report, HumanizerReport


# ── data types ────────────────────────────────────────────────────────────────

@dataclass
class RhythmReport:
    mean_stdev:               float
    stdev_flag:               bool
    shape_cv:                 float
    shape_uniform:            bool
    hedge_sentences:          List[dict]        # [{sentence, hedge_count}]
    echo_paragraphs:          List[str]         # paragraph previews
    zombie_nouns:             List[str]
    context_free_comparisons: int
    synonym_drift:            List[str]
    starter_entropy:          Optional[float]
    starter_dominated:        List[tuple]
    punctuation_issues:       List[str]

    def to_dict(self) -> dict:
        return {
            "mean_stdev":               self.mean_stdev,
            "stdev_flag":               self.stdev_flag,
            "shape_cv":                 self.shape_cv,
            "shape_uniform":            self.shape_uniform,
            "hedge_sentences":          self.hedge_sentences,
            "echo_paragraphs":          self.echo_paragraphs,
            "zombie_nouns":             self.zombie_nouns,
            "context_free_comparisons": self.context_free_comparisons,
            "synonym_drift":            self.synonym_drift,
            "starter_entropy":          self.starter_entropy,
            "starter_dominated":        self.starter_dominated,
            "punctuation_issues":       self.punctuation_issues,
        }


@dataclass
class SlopReport:
    score:       int
    dimensions:  Dict[str, int]
    phrase_hits: Dict[str, List[str]]
    rhythm:      RhythmReport
    linguistic:  Optional["LinguisticReport"] = None
    ai_patterns: Optional["AIPatternReport"] = None
    humanizer:   Optional["HumanizerReport"] = None
    passed:      bool = False

    def to_dict(self) -> dict:
        d = {
            "score":            self.score,
            "passed":           self.passed,
            "dimensions":       self.dimensions,
            "phrase_hits":      self.phrase_hits,
            "rhythm":           self.rhythm.to_dict(),
            "linguistic_method": self.linguistic.method if self.linguistic else None,
        }
        if self.linguistic:
            d["linguistic"] = self.linguistic.to_dict()
        if self.ai_patterns:
            d["ai_patterns"] = self.ai_patterns.to_dict()
        if self.humanizer:
            d["humanizer"] = self.humanizer.to_dict()
        return d


# ── phrase checking ───────────────────────────────────────────────────────────

# Module-level cache for compiled phrase patterns.
# Key: frozenset(phrases) | exceptions → compiled re.Pattern
# This avoids re.compile() on every analyse() call.
_PHRASE_PATTERN_CACHE: Dict[int, "re.Pattern"] = {}


def _get_phrase_pattern(phrases: List[str], exceptions: frozenset) -> "re.Pattern":
    """Return a cached compiled alternation pattern for the given phrases."""
    active  = tuple(p for p in phrases if p not in exceptions)
    cache_key = hash(active)
    if cache_key not in _PHRASE_PATTERN_CACHE:
        _PHRASE_PATTERN_CACHE[cache_key] = re.compile(
            "|".join(re.escape(p) for p in active)
        )
    return _PHRASE_PATTERN_CACHE[cache_key]


def check_phrases(
    text: str,
    banned: Dict[str, List[str]],
    exceptions: frozenset,
) -> Dict[str, List[str]]:
    """
    O(n) phrase scan using a single compiled regex alternation per category.
    Patterns are compiled once and cached — no re.compile on repeated calls.
    """
    lower = text.lower()
    hits: Dict[str, List[str]] = {}
    for label, phrases in banned.items():
        if not phrases:
            continue
        active = [p for p in phrases if p not in exceptions]
        if not active:
            continue
        pattern = _get_phrase_pattern(phrases, exceptions)
        found = list(dict.fromkeys(m.group() for m in pattern.finditer(lower)))
        if found:
            hits[label] = found
    return hits


# ── rhythm analysis ───────────────────────────────────────────────────────────

def analyse_rhythm(text: str) -> RhythmReport:
    """
    Single-pass rhythm analysis.  Tokenises once; feeds all sub-checks.
    Integrates all v4 checks (zombie nouns, comparisons, synonym drift,
    starter entropy, punctuation variety) — not patched after the fact.
    """
    paragraphs = split_paragraphs(text)
    all_stdevs:     List[float] = []
    para_lengths:   List[int]   = []
    hedge_sents:    List[dict]  = []
    echo_paras:     List[str]   = []
    all_sentences:  List[str]   = []

    for para in paragraphs:
        sents = sent_tokenize(para)
        all_sentences.extend(sents)
        lengths = [word_count(s) for s in sents if word_count(s) > 3]
        if not lengths:
            continue
        all_stdevs.append(stdev(lengths))
        para_lengths.append(len(sents))

        for sent in sents:
            h = sum(1 for w in RE_WORDS.findall(sent.lower()) if w in HEDGE_WORDS)
            if h >= HEDGE_THRESHOLD:
                hedge_sents.append({"sentence": sent, "hedge_count": h})

        if (len(sents) >= MIN_PARA_SENTENCES
                and jaccard_overlap(sents[0], sents[-1]) >= ECHO_OVERLAP_THRESH):
            echo_paras.append(para[:120])

    mean_stdev  = mean(all_stdevs)
    stdev_flag  = bool(mean_stdev < STDEV_THRESHOLD and len(all_stdevs) >= 3)
    shape_cv    = coeff_of_variation(para_lengths) if len(para_lengths) >= 3 else 1.0
    shape_unif  = bool(shape_cv < SHAPE_CV_THRESH and len(para_lengths) >= 4)

    # ── v4: zombie nouns ──────────────────────────────────────────────────────
    lower_text = text.lower()
    zombie_hits = [
        z for z in ZOMBIE_NOUNS
        if re.search(r'\b(the|a|an|of|our|their)\s+\w*' + z, lower_text)
    ]

    # ── v4: context-free comparisons ─────────────────────────────────────────
    cf_comparisons = sum(
        1 for s in all_sentences
        if RE_COMPARISON_VERBS.search(s) and not RE_SPECIFIC_REF.search(s)
    )

    # ── v4: synonym drift ────────────────────────────────────────────────────
    our_nouns = re.findall(r'\bour\s+(\w+)', lower_text)
    found_synonyms = {n for n in our_nouns if n in OUR_SYSTEM_NOUNS}
    synonym_drift = sorted(found_synonyms) if len(found_synonyms) >= 3 else []

    # ── v4: sentence-starter entropy ─────────────────────────────────────────
    starters = [
        RE_WORDS.findall(s)[0].lower()
        for s in all_sentences
        if RE_WORDS.findall(s)
    ]
    starter_entropy   = None
    starter_dominated = []
    if len(starters) >= 8:
        starter_entropy = round(shannon_entropy(starters), 2)
        counts = Counter(starters)
        total  = sum(counts.values())
        starter_dominated = [
            (w, c, round(c / total * 100, 1))
            for w, c in counts.most_common(3)
            if c / total > 0.25
        ]

    # ── v4: punctuation variety ───────────────────────────────────────────────
    punct_issues: List[str] = []
    punct_counts  = Counter(c for c in text if c in '.,;:()!')
    punct_total   = sum(punct_counts.values())
    if punct_total > 20:
        comma_ratio = punct_counts.get(',', 0) / punct_total
        if comma_ratio > 0.75:
            punct_issues.append(
                f"Comma-heavy ({comma_ratio:.0%} of punctuation). "
                "Try semicolons or sentence breaks."
            )
    if punct_counts.get(';', 0) == 0 and len(text) > 500:
        punct_issues.append(
            "No semicolons. Academic prose uses them to join related clauses."
        )

    return RhythmReport(
        mean_stdev               = round(mean_stdev, 2),
        stdev_flag               = stdev_flag,
        shape_cv                 = round(shape_cv, 3),
        shape_uniform            = shape_unif,
        hedge_sentences          = hedge_sents,
        echo_paragraphs          = echo_paras,
        zombie_nouns             = zombie_hits,
        context_free_comparisons = cf_comparisons,
        synonym_drift            = synonym_drift,
        starter_entropy          = starter_entropy,
        starter_dominated        = starter_dominated,
        punctuation_issues       = punct_issues,
    )


# ── scoring ───────────────────────────────────────────────────────────────────

def compute_score(
    phrase_hits: Dict[str, List[str]],
    rhythm: RhythmReport,
) -> tuple[int, Dict[str, int]]:
    """
    Score 0–100 across five dimensions (20 pts each), then apply v4 penalties.
    Returns (total_score, dimension_dict).
    """
    academic_hits = len(phrase_hits.get("academic", []))
    generic_hits  = len(phrase_hits.get("generic",  [])) + len(phrase_hits.get("structures", []))
    hedge_count   = len(rhythm.hedge_sentences)
    echo_count    = len(rhythm.echo_paragraphs)

    dims = {
        "directness":   max(0, min(20, 20 - academic_hits * 3 - generic_hits)),
        "rhythm":       max(0, min(20, 20
                            - (10 if rhythm.stdev_flag   else 0)
                            - (5  if rhythm.shape_uniform else 0)
                            - echo_count * 3)),
        "trust":        max(0, min(20, 20 - hedge_count * 4)),
        "authenticity": max(0, min(20, 20 - academic_hits * 2 - generic_hits * 2)),
        "density":      max(0, min(20, 20
                            - (academic_hits + generic_hits)
                            - hedge_count * 2)),
    }
    base = sum(dims.values())

    # v4 additional penalties
    v4_penalty = 0
    v4_penalty += min(15, len(rhythm.zombie_nouns) * 3)
    v4_penalty += min(10, rhythm.context_free_comparisons * 5)
    v4_penalty += min(10, len(rhythm.synonym_drift) * 4)
    if (rhythm.starter_entropy is not None
            and rhythm.starter_entropy < STARTER_ENTROPY_THRESH
            and len(rhythm.starter_dominated) > 0):
        v4_penalty += 10

    total = max(0, base - v4_penalty)
    return total, dims


# ── top-level entry point ─────────────────────────────────────────────────────

def analyse(
    text: str,
    banned: Dict[str, List[str]],
    exceptions: frozenset,
    threshold: int = 70,
    section_name: str = "",
) -> SlopReport:
    """
    Full single-pass analysis.

    Args:
        text:       Plain text to analyse (LaTeX already stripped if needed).
        banned:     Dict from loaders.load_banned_phrases().
        exceptions: Frozenset from loaders.load_exceptions().
        threshold:  Minimum score to pass.

    Returns:
        SlopReport dataclass with all findings.
    """
    phrase_hits = check_phrases(text, banned, exceptions)
    rhythm      = analyse_rhythm(text)
    score, dims = compute_score(phrase_hits, rhythm)

    # Run linguistic analysis (spaCy if installed, else regex fallback)
    all_sentences = []
    for para in split_paragraphs(text):
        all_sentences.extend(sent_tokenize(para))
    linguistic = analyse_linguistic(all_sentences, section_name)

    # spaCy passive voice adds a scoring penalty
    passive_penalty = min(10, len(linguistic.passive_hits) * 2)
    score = max(0, score - passive_penalty)

    # AI pattern analysis (passive ratio, methods verbs, formulaic phrases)
    ai_pat = analyse_ai_patterns(text)
    score  = max(0, score - ai_pat.ai_pattern_penalty)

    # Humanizer analysis (AI vocabulary, formulaic phrases, em dashes)
    h_rep  = humanizer_report(text)
    score  = max(0, score - h_rep.humanizer_penalty)

    return SlopReport(
        score       = score,
        dimensions  = dims,
        phrase_hits = phrase_hits,
        rhythm      = rhythm,
        linguistic  = linguistic,
        ai_patterns = ai_pat,
        humanizer   = h_rep,
        passed      = score >= threshold,
    )
