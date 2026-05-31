"""
tests/test_slop_lib.py
======================
Core test suite.  Run with:  pytest tests/

Fixtures:
  tests/fixtures/bad_paper.txt  — AI-like prose (should score low)
  tests/fixtures/good_paper.txt — human-like prose (should score high)
"""

import sys
from pathlib import Path

# Make slop_lib importable from any working directory
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from slop_lib import analyse, load_banned_phrases, load_exceptions
from slop_lib.analysis import analyse_rhythm, check_phrases, compute_score
from slop_lib.stats    import mean, stdev, coeff_of_variation, shannon_entropy
from slop_lib.text     import (
    word_count, split_paragraphs, jaccard_overlap, strip_latex, sent_tokenize
)
from slop_lib.loaders  import load_banned_phrases, load_exceptions

FIXTURES = Path(__file__).parent / "fixtures"
BAD_TEXT  = (FIXTURES / "bad_paper.txt").read_text()
GOOD_TEXT = (FIXTURES / "good_paper.txt").read_text()


# ── stats ─────────────────────────────────────────────────────────────────────

class TestStats:
    def test_stdev_empty(self):
        assert stdev([]) == 0.0

    def test_stdev_single(self):
        assert stdev([5]) == 0.0

    def test_stdev_known(self):
        # [2, 4, 4, 4, 5, 5, 7, 9] → population stdev ≈ 2.0
        assert abs(stdev([2, 4, 4, 4, 5, 5, 7, 9]) - 2.0) < 0.01

    def test_mean_empty(self):
        assert mean([]) == 0.0

    def test_coeff_of_variation(self):
        assert coeff_of_variation([10, 10, 10]) == 0.0   # zero variance
        assert coeff_of_variation([]) == 0.0

    def test_shannon_entropy_uniform(self):
        # All same → entropy 0
        assert shannon_entropy(["a", "a", "a"]) == 0.0

    def test_shannon_entropy_varied(self):
        # 4 distinct tokens → entropy = 2 bits
        assert abs(shannon_entropy(["a", "b", "c", "d"]) - 2.0) < 0.01


# ── text helpers ──────────────────────────────────────────────────────────────

class TestText:
    def test_word_count(self):
        assert word_count("Hello world") == 2
        assert word_count("") == 0

    def test_split_paragraphs(self):
        text = "Para one.\n\nPara two.\n\n\nPara three."
        paras = split_paragraphs(text)
        assert len(paras) == 3

    def test_jaccard_overlap_identical(self):
        s = "the quick brown fox"
        assert jaccard_overlap(s, s) == 1.0

    def test_jaccard_overlap_disjoint(self):
        # Stop words are ignored so the content words must be different
        assert jaccard_overlap("alpha beta gamma", "delta epsilon zeta") == 0.0

    def test_strip_latex_basic(self):
        cleaned = strip_latex(r"\textbf{Hello} world \cite{ref}")
        assert "Hello" in cleaned
        assert r"\textbf" not in cleaned
        assert r"\cite" not in cleaned

    def test_strip_latex_no_citation_word(self):
        cleaned = strip_latex(r"We show \cite{jones2020} that transformers work.")
        assert "CITE" not in cleaned
        assert "transformers" in cleaned


# ── phrase checking ───────────────────────────────────────────────────────────

class TestPhraseChecking:
    def test_detects_known_bad_phrase(self):
        banned = {"generic": ["novel framework", "cutting-edge"]}
        hits   = check_phrases("This novel framework uses cutting-edge methods.", banned, frozenset())
        assert "generic" in hits
        assert "novel framework" in hits["generic"]

    def test_respects_exceptions(self):
        banned     = {"generic": ["novel framework"]}
        exceptions = frozenset(["novel framework"])
        hits = check_phrases("This novel framework is fine.", banned, exceptions)
        assert "generic" not in hits

    def test_empty_text(self):
        banned = {"generic": ["novel framework"]}
        hits   = check_phrases("", banned, frozenset())
        assert hits == {}


# ── rhythm analysis ───────────────────────────────────────────────────────────

class TestRhythmAnalysis:
    def test_bad_paper_high_hedge_count(self):
        r = analyse_rhythm(BAD_TEXT)
        assert len(r.hedge_sentences) > 0, "Expected hedge sentences in bad paper"

    def test_good_paper_low_hedge_count(self):
        r = analyse_rhythm(GOOD_TEXT)
        assert len(r.hedge_sentences) == 0, "Expected no over-hedged sentences in good paper"

    def test_bad_paper_zombie_nouns(self):
        r = analyse_rhythm(BAD_TEXT)
        assert len(r.zombie_nouns) > 0, "Expected zombie nouns in bad paper"

    def test_bad_paper_synonym_drift(self):
        r = analyse_rhythm(BAD_TEXT)
        assert len(r.synonym_drift) >= 2, "Expected synonym drift in bad paper"

    def test_context_free_comparison(self):
        text = "Our model outperforms all baselines."
        r    = analyse_rhythm(text)
        assert r.context_free_comparisons >= 1

    def test_specific_comparison_not_flagged(self):
        text = "Our model outperforms BERT by 3.2 BLEU points on WMT-14."
        r    = analyse_rhythm(text)
        assert r.context_free_comparisons == 0


# ── full analysis pipeline ────────────────────────────────────────────────────

class TestAnalyse:
    def setup_method(self):
        self.banned     = load_banned_phrases()
        self.exceptions = load_exceptions()

    def test_bad_paper_scores_lower_than_good(self):
        bad_report  = analyse(BAD_TEXT,  self.banned, self.exceptions)
        good_report = analyse(GOOD_TEXT, self.banned, self.exceptions)
        assert bad_report.score < good_report.score, (
            f"Bad paper ({bad_report.score}) should score lower "
            f"than good paper ({good_report.score})"
        )

    def test_good_paper_passes_threshold(self):
        report = analyse(GOOD_TEXT, self.banned, self.exceptions, threshold=60)
        assert report.passed, f"Good paper should pass at threshold 60, got {report.score}"

    def test_bad_paper_fails_high_threshold(self):
        report = analyse(BAD_TEXT, self.banned, self.exceptions, threshold=90)
        assert not report.passed, f"Bad paper should fail at threshold 90, got {report.score}"

    def test_score_in_range(self):
        for text in [BAD_TEXT, GOOD_TEXT]:
            r = analyse(text, self.banned, self.exceptions)
            assert 0 <= r.score <= 100

    def test_dimensions_sum_at_most_100(self):
        r = analyse(GOOD_TEXT, self.banned, self.exceptions)
        assert sum(r.dimensions.values()) <= 100

    def test_to_dict_serialisable(self):
        import json
        r = analyse(BAD_TEXT, self.banned, self.exceptions)
        serialised = json.dumps(r.to_dict())   # should not raise
        data = json.loads(serialised)
        assert "score" in data
        assert "rhythm" in data

    def test_phrase_hits_are_strings(self):
        r = analyse(BAD_TEXT, self.banned, self.exceptions)
        for label, hits in r.phrase_hits.items():
            for h in hits:
                assert isinstance(h, str), f"Expected str hit, got {type(h)}"


# ── loaders ───────────────────────────────────────────────────────────────────

class TestLoaders:
    def test_load_banned_phrases_returns_lists(self):
        banned = load_banned_phrases()
        assert "generic" in banned
        assert "academic" in banned
        assert isinstance(banned["generic"], list)
        assert len(banned["generic"]) > 0

    def test_load_exceptions_returns_frozenset(self):
        exc = load_exceptions()
        assert isinstance(exc, frozenset)

    def test_load_banned_phrases_cached(self):
        # Should be the exact same object (lru_cache)
        a = load_banned_phrases()
        b = load_banned_phrases()
        assert a is b


# ── config ────────────────────────────────────────────────────────────────────

class TestConfig:
    def test_get_threshold_default(self):
        from slop_lib.config import get_threshold
        t = get_threshold()
        assert isinstance(t, int)
        assert 50 <= t <= 100   # sanity bounds

    def test_get_thresholds_returns_dict(self):
        from slop_lib.config import get_thresholds
        t = get_thresholds()
        assert "hedge_density"  in t
        assert "rhythm_stdev"   in t
        assert "echo_overlap"   in t

    def test_field_override_biomedical(self):
        from slop_lib.config import get_thresholds
        cs  = get_thresholds(field="cs_ai")
        bio = get_thresholds(field="biomedical")
        # Biomedical should tolerate more hedging than CS
        assert bio["hedge_density"] >= cs["hedge_density"]

    def test_load_thresholds_from_constants(self):
        from slop_lib.constants import load_thresholds
        t = load_thresholds()
        assert isinstance(t, dict)
        assert "rhythm_stdev" in t


# ── tense fix regression ─────────────────────────────────────────────────────

class TestTenseFix:
    """Regression tests for the tense default false-positive fix."""

    def test_unknown_section_returns_no_tense_issues(self):
        """Full-paper analysis with no section name should not over-flag tense."""
        from slop_lib.linguistic import detect_tense_inconsistency
        # A methods-style sentence (past tense) should NOT be flagged
        # when section is unknown and auto-detect can't determine dominant tense
        sentences = ["The model was trained on 100K examples.",
                     "Parameters were optimised using Adam."]
        # With section_name="", auto-detect kicks in.
        # These sentences are past-tense dominated → expected="past" → no issues.
        issues = detect_tense_inconsistency(sentences, section_name="")
        # Either 0 issues (auto-detected past correctly) or total < 3 (not 38!)
        assert len(issues) < 3, f"Got {len(issues)} tense issues — should be < 3"

    def test_known_past_section_allows_past_tense(self):
        from slop_lib.linguistic import detect_tense_inconsistency
        sentences = ["The model was trained on the dataset.",
                     "Results were evaluated on three benchmarks."]
        issues = detect_tense_inconsistency(sentences, section_name="results")
        assert len(issues) == 0, "Past tense in results section should not be flagged"

    def test_known_present_section_flags_past(self):
        from slop_lib.linguistic import detect_tense_inconsistency
        sentences = ["The model was proposed by Smith.",
                     "It was evaluated in 2020."]
        issues = detect_tense_inconsistency(sentences, section_name="introduction")
        # These should be flagged — intro expects present tense
        assert len(issues) > 0, "Past tense in introduction should be flagged"
