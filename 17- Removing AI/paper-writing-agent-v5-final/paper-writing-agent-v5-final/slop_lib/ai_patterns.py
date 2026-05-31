"""
ai_patterns.py
==============
Three new detection signals that close the gap between our tool and Turnitin:

1. Passive voice RATIO  — Turnitin's #1 signal for AI-written methods sections.
   A 71% passive rate in methods is a near-certain AI fingerprint.
   Count-based detection missed this; ratio-based detection catches it.

2. AI methods verbs     — Formulaic passive constructions AI uses to write
   methods sections: "was performed", "was calculated", "were measured", etc.
   These appear 35+ times in AI-written methods vs ~5 in human-written.

3. Formulaic AI phrases — Sentence-level constructions AI overuses throughout:
   impersonal "it" constructions, connector density, formulaic evaluations.
"""

import re
from dataclasses import dataclass
from typing import List, Tuple

from .constants import RE_WORDS


# ── 1. Passive voice ratio ────────────────────────────────────────────────────

# Covers simple passive, perfect passive, and progressive passive
_RE_PASSIVE_FULL = re.compile(
    r'\b(was|were|is|are|been|being|has been|have been|had been)\s+\w+ed\b',
    re.IGNORECASE,
)

# Irregular past participles AI also uses in passive constructions
_RE_PASSIVE_IRREGULAR = re.compile(
    r'\b(was|were|is|are|has been|have been)\s+'
    r'(done|shown|found|seen|known|given|taken|made|built|set|run|written|'
    r'chosen|grown|drawn|driven|begun|broken|chosen|frozen|spoken|stolen|'
    r'understood|undertaken|undertaken|known|known)\b',
    re.IGNORECASE,
)


def passive_voice_ratio(text: str) -> Tuple[float, int, int]:
    """
    Returns (ratio, passive_count, total_sentences).
    ratio = passive_count / total_sentences.
    """
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if len(s.strip()) > 20]
    if not sentences:
        return 0.0, 0, 0
    passive = sum(
        1 for s in sentences
        if _RE_PASSIVE_FULL.search(s) or _RE_PASSIVE_IRREGULAR.search(s)
    )
    return passive / len(sentences), passive, len(sentences)


# ── 2. AI methods verbs (passive constructions specific to methods sections) ──

AI_METHODS_VERBS: List[str] = [
    # Procedure verbs — AI writes methods almost exclusively in passive
    "was performed", "were performed",
    "was conducted", "were conducted",
    "was carried out", "were carried out",
    "was calculated", "were calculated",
    "was measured", "were measured",
    "was determined", "were determined",
    "was obtained", "were obtained",
    "was prepared", "were prepared",
    "was fabricated", "were fabricated",
    "was constructed", "were constructed",
    "was assembled", "were assembled",
    "was used", "were used",
    "was employed", "were employed",
    "was adjusted", "were adjusted",
    "was confirmed", "were confirmed",
    "was verified", "were verified",
    "was validated", "were validated",
    "was selected", "were selected",
    "was chosen", "were chosen",
    "was normalized", "were normalized",
    "was divided", "were divided",
    "was separated", "were separated",
    "was recorded", "were recorded",
    "was observed", "were observed",
    "was dissolved", "were dissolved",
    "was dispersed", "were dispersed",
    "was collected", "were collected",
    "was removed", "were removed",
    "was stored", "were stored",
    "was washed", "were washed",
    "was dried", "were dried",
    "was mixed", "were mixed",
    "was added", "were added",
    "was compared", "were compared",
    "was evaluated", "were evaluated",
    "was assessed", "were assessed",
    "was analyzed", "were analyzed",
    "was tested", "were tested",
    "was trained", "were trained",
    "was implemented", "were implemented",
    "was applied", "were applied",
    "was introduced", "were introduced",
    "was initialized", "were initialized",
    "was terminated", "were terminated",
    "was retained", "were retained",
]

# Compile as one fast pattern
_RE_METHODS_VERBS = re.compile(
    "|".join(re.escape(p) for p in AI_METHODS_VERBS),
    re.IGNORECASE,
)


def count_ai_methods_verbs(text: str) -> Tuple[int, List[str]]:
    """
    Count AI-style methods verb phrases and return (count, examples).
    >15 occurrences in a paper section is a strong AI-methods signal.
    """
    matches = _RE_METHODS_VERBS.findall(text.lower())
    # Deduplicate for display but count all
    examples = list(dict.fromkeys(m for m in matches))[:8]
    return len(matches), examples


# ── 3. Formulaic AI phrases ───────────────────────────────────────────────────

# Impersonal "it was/is" constructions — AI overuses these
AI_IMPERSONAL: List[str] = [
    "it was found that", "it was observed that", "it was determined that",
    "it was confirmed that", "it was noted that", "it was shown that",
    "it is worth noting", "it is important to note", "it should be noted",
    "it is clear that", "it is evident that", "it can be seen",
    "it is well known", "it has been reported", "it has been shown",
    "it has been demonstrated", "it is generally accepted",
]

# Formulaic sentence-initial connectors AI uses more than humans
AI_CONNECTORS: List[str] = [
    "furthermore,", "moreover,", "additionally,", "in addition,",
    "in contrast,", "on the other hand,", "as a result,",
    "consequently,", "accordingly,", "notably,", "importantly,",
    "specifically,", "in particular,", "in this regard,",
    "with respect to this,", "in this context,",
]

# Formulaic evaluation language
AI_EVALUATION: List[str] = [
    "plays a crucial role", "plays a key role", "plays an important role",
    "is strongly affected", "is directly linked", "is considered a promising",
    "is an effective approach", "is essential for", "is critical for",
    "significantly improves", "substantially improves", "greatly improves",
    "effectively addresses", "successfully demonstrates",
    "provides a comprehensive", "offers a robust", "ensures the",
    "is widely used", "is commonly used", "is frequently used",
]

_AI_PHRASE_SETS = {
    "impersonal_it":   AI_IMPERSONAL,
    "ai_connectors":   AI_CONNECTORS,
    "ai_evaluation":   AI_EVALUATION,
}

_RE_AI_PHRASES: dict = {
    label: re.compile("|".join(re.escape(p) for p in phrases), re.IGNORECASE)
    for label, phrases in _AI_PHRASE_SETS.items()
}


def count_formulaic_phrases(text: str) -> dict:
    """
    Returns {label: (count, [examples])} for each formulaic phrase category.
    """
    lower = text.lower()
    results = {}
    for label, pattern in _RE_AI_PHRASES.items():
        matches = pattern.findall(lower)
        if matches:
            results[label] = {
                "count":    len(matches),
                "examples": list(dict.fromkeys(matches))[:5],
            }
    return results


# ── 4. Section-aware passive detection ───────────────────────────────────────

_METHODS_HEADERS = re.compile(
    r'(materials?\s+and\s+methods?|methodology|methods?|'
    r'experimental\s+(setup|design|methods?)|'
    r'2\.\s*(materials?|methods?|methodology|experimental))',
    re.IGNORECASE,
)

_RESULTS_HEADERS = re.compile(
    r'(results?\s+(and\s+(discussion|analysis))?|'
    r'experiments?\s+(and\s+results?)?|'
    r'3\.\s*(results?|experiments?|discussion))',
    re.IGNORECASE,
)


def analyse_section_passive(text: str) -> dict:
    """
    Split text into approximate sections and compute passive ratio per section.
    Returns {'methods': ratio, 'results': ratio, 'overall': ratio, 'worst': ratio}.
    """
    # Split on likely section boundaries (lines that look like headers)
    lines = text.split('\n')
    sections = {"preamble": []}
    current = "preamble"

    for line in lines:
        stripped = line.strip()
        if _METHODS_HEADERS.search(stripped) and len(stripped) < 80:
            current = "methods"
            sections.setdefault("methods", [])
        elif _RESULTS_HEADERS.search(stripped) and len(stripped) < 80:
            current = "results"
            sections.setdefault("results", [])
        sections.setdefault(current, []).append(line)

    result = {}
    for sec, sec_lines in sections.items():
        sec_text = "\n".join(sec_lines)
        ratio, passive_count, sent_count = passive_voice_ratio(sec_text)
        if sent_count >= 5:   # ignore tiny sections
            result[sec] = {
                "ratio":         round(ratio, 3),
                "passive_count": passive_count,
                "sent_count":    sent_count,
            }

    # Overall
    overall_ratio, _, _ = passive_voice_ratio(text)
    result["overall"] = round(overall_ratio, 3)

    # Worst section ratio
    section_ratios = [v["ratio"] for k, v in result.items() if isinstance(v, dict)]
    result["worst_section_ratio"] = max(section_ratios) if section_ratios else overall_ratio

    return result


# ── 5. Compound AI score ──────────────────────────────────────────────────────

@dataclass
class AIPatternReport:
    passive_overall:      float      # 0.0–1.0
    passive_worst:        float      # worst single section ratio
    passive_sections:     dict
    methods_verb_count:   int
    methods_verb_examples: List[str]
    formulaic_phrases:    dict       # {label: {count, examples}}
    ai_pattern_penalty:   int        # total penalty points (0–40)

    def to_dict(self) -> dict:
        return {
            "passive_overall":       self.passive_overall,
            "passive_worst_section": self.passive_worst,
            "passive_sections":      self.passive_sections,
            "methods_verb_count":    self.methods_verb_count,
            "methods_verb_examples": self.methods_verb_examples,
            "formulaic_phrases":     self.formulaic_phrases,
            "ai_pattern_penalty":    self.ai_pattern_penalty,
        }


def analyse_ai_patterns(text: str) -> AIPatternReport:
    """
    Run all three AI pattern checks and compute a total penalty.

    Penalty scale:
      passive_worst > 0.55  → -20 pts (AI-written methods section)
      passive_worst > 0.40  → -12 pts
      passive_worst > 0.25  → -6 pts
      methods_verb_count > 20 → -10 pts (AI methods writing)
      methods_verb_count > 10 → -5 pts
      formulaic phrase hits → up to -10 pts
    """
    # 1. Passive ratios
    sections = analyse_section_passive(text)
    overall  = sections.get("overall", 0.0)
    worst    = sections.get("worst_section_ratio", overall)

    if worst > 0.55:
        passive_penalty = 20
    elif worst > 0.40:
        passive_penalty = 12
    elif worst > 0.25:
        passive_penalty = 6
    else:
        passive_penalty = 0

    # 2. AI methods verbs
    verb_count, verb_examples = count_ai_methods_verbs(text)
    if verb_count > 20:
        verb_penalty = 10
    elif verb_count > 10:
        verb_penalty = 5
    else:
        verb_penalty = 0

    # 3. Formulaic phrases
    formulaic = count_formulaic_phrases(text)
    total_formulaic = sum(v["count"] for v in formulaic.values())
    if total_formulaic > 15:
        formulaic_penalty = 10
    elif total_formulaic > 8:
        formulaic_penalty = 6
    elif total_formulaic > 3:
        formulaic_penalty = 3
    else:
        formulaic_penalty = 0

    total_penalty = min(40, passive_penalty + verb_penalty + formulaic_penalty)

    return AIPatternReport(
        passive_overall       = round(overall, 3),
        passive_worst         = round(worst, 3),
        passive_sections      = {k: v for k, v in sections.items()
                                  if k not in ("overall", "worst_section_ratio")},
        methods_verb_count    = verb_count,
        methods_verb_examples = verb_examples,
        formulaic_phrases     = formulaic,
        ai_pattern_penalty    = total_penalty,
    )
