"""
humanizer.py
============
Safe phrase-level AI writing detection and substitution.

Based on Wikipedia's "Signs of AI writing" guide (humanizer skill v6).

DESIGN RULE: Only phrase-level substitutions — never restructures sentences.
             No group-capturing regex that can drop content.

Two public functions:
    humanize_text(text)          → cleaned text
    humanizer_report(text)       → HumanizerReport with hit counts + score
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Tuple, Dict


# ─────────────────────────────────────────────────────────────────────────────
# DETECTION PATTERNS  (for scoring — not all of these auto-fix)
# ─────────────────────────────────────────────────────────────────────────────

# AI vocabulary words — appear far more in AI text (humanizer skill §7)
AI_VOCABULARY_WORDS: List[str] = [
    # Connectors AI overuses
    "furthermore", "moreover", "additionally",
    # Core AI slop words
    "crucial", "pivotal", "delve", "emphasizing", "enduring",
    "enhance", "enhances", "fostering", "garner", "interplay",
    "intricate", "intricacies", "showcase", "tapestry", "testament",
    "underscore", "underscores", "vibrant",
    # Promotional / superlative
    "groundbreaking", "breathtaking", "nestled", "renowned", "seamless",
    "cutting-edge", "state-of-the-art",
    # Vague academic inflators
    "comprehensive", "robust", "novel", "innovative",
    "leveraging", "leverages", "leverage",
    "holistic", "paradigm", "synergy", "synergistic",
    "transformative", "impactful",
]

# Formulaic AI phrases — sentence-level (humanizer skill §1–6, §19–24)
AI_PHRASES: List[str] = [
    # Significance inflation
    "marks a pivotal", "marking a pivotal", "evolving landscape",
    "enduring testament", "stands as a testament", "serves as a testament",
    "setting the stage for", "focal point", "indelible mark",
    "deeply rooted", "reflects broader",
    # Copula avoidance
    "serves as a", "serves as an", "serves as the",
    "stands as a", "stands as an", "stands as the",
    "functions as a", "functions as an",
    # Promotional
    "vibrant town", "rich cultural heritage", "stunning natural beauty",
    "must-visit", "nestled within", "nestled in",
    # Vague authority
    "experts argue", "experts believe", "industry observers",
    "observers have cited", "some critics argue",
    # Significance/evaluation
    "plays a crucial role", "plays a key role", "plays an important role",
    "is strongly affected", "is considered a promising",
    "is an effective approach", "significantly improves",
    "substantially improves", "provides a comprehensive",
    "is widely used", "is commonly used",
    # Impersonal "it"
    "it is worth noting", "it should be noted",
    "it is important to note",
    "it was found that", "it was observed that",
    "it has been shown", "it has been demonstrated",
    "it is generally accepted",
    # Generic conclusion
    "the future looks bright", "exciting times lie ahead",
    "continues this journey toward excellence",
    # Challenges section
    "despite these challenges", "faces several challenges",
    "future outlook", "challenges and legacy",
    # Em dash (count ≥3 as a flag)
    # Rule of three — detected separately
    # Negative parallelism
    "it's not just about", "it's not merely",
    "not only.*but also",  # regex
    # Collaborative artifacts
    "i hope this helps", "let me know if you",
    "would you like me to", "here is an overview",
]

# ─────────────────────────────────────────────────────────────────────────────
# SAFE AUTO-FIX RULES
# (pattern_string, replacement) — phrase-level only, NO group capturing
# All patterns are case-insensitive. After replacement, sentence start is
# re-capitalised if needed.
# ─────────────────────────────────────────────────────────────────────────────

_AUTO_FIX_RULES: List[Tuple[str, str]] = [

    # ── Filler openers — clearly redundant, safe to delete ────────────────
    (r'It is (?:important|worth) (?:to note|noting) that[,:]?\s+', ''),
    (r'It should be noted that[,:]?\s+', ''),
    (r'It can be (?:observed|seen|noted) that[,:]?\s+', ''),
    (r'It is (?:clear|evident) that[,:]?\s+', ''),
    (r'It (?:was|has been) (?:found|observed|noted|determined|shown|confirmed) that[,:]?\s+', ''),
    (r'It is well[- ]known that[,:]?\s+', ''),
    (r'It has been (?:reported|shown|demonstrated) that[,:]?\s+', ''),
    (r'It is generally accepted that[,:]?\s+', ''),
    (r'To the best of our knowledge,?\s+', ''),
    (r'As far as we are aware,?\s+', ''),
    (r'We believe that\s+', ''),
    (r'We note that\s+', ''),
    (r'One can observe that\s+', ''),
    (r'We can see that\s+', ''),
    (r'From the results,?\s+it is clear that\s+', ''),

    # ── Chatbot artifacts — must not appear in paper text ─────────────────
    (r'I hope this helps\.?\s*', ''),
    (r'Of course!?\s+', ''),
    (r'Certainly!?\s+', ''),
    (r"You're absolutely right!?\s+", ''),
    (r'Here is (?:a|an|the) (?:brief )?overview[^.]*\.\s*', ''),
    (r'Let me know if you(?:\'d| would) like.*?\.', ''),

    # ── Filler phrases — compress without changing meaning ────────────────
    # Use lowercase replacements only; sentence-start re-capitalisation
    # happens in humanize_text() after all rules have run.
    (r'\bin order to\b', 'to'),
    (r'\bdue to the fact that\b', 'because'),
    (r'\bat this point in time\b', 'now'),
    (r'\bin the event that\b', 'if'),
    (r'\bhas the ability to\b', 'can'),
    (r'\bhave the ability to\b', 'can'),
    (r'\bis able to\b', 'can'),
    (r'\bare able to\b', 'can'),

    # ── Copula avoidance — only the clearest cases ────────────────────────
    (r'\bserves as a\b', 'is a'),
    (r'\bserves as an\b', 'is an'),
    (r'\bserves as the\b', 'is the'),
    (r'\bstands as a\b', 'is a'),
    (r'\bstands as an\b', 'is an'),
    (r'\bstands as the\b', 'is the'),
    (r'\bboasts a\b', 'has a'),
    (r'\bboasts an\b', 'has an'),
    (r'\bboasts the\b', 'has the'),

    # ── Em dash overuse — replace spaced em dashes with comma ────────────
    # Only " — " pattern (space–em–space), not compound adjectives
    (r' — ', ', '),

    # ── Knowledge cutoff disclaimers ─────────────────────────────────────
    (r'[Aa]s of (?:my )?(?:last )?(?:knowledge )?(?:cutoff|update|training)[^,]*,?\s*', ''),
    (r'[Bb]ased on available information,?\s*', ''),
    (r'[Ww]hile specific details are (?:limited|scarce)[^,]*,?\s*', ''),

    # ── Sycophantic openers ───────────────────────────────────────────────
    (r'^[Gg]reat question!?\s+', ''),
    (r'^[Gg]ood question!?\s+', ''),
    (r"[Tt]hat'?s? an? (?:excellent|great|good) (?:point|question)\.?\s+", ''),

    # ── Knowledge-cutoff disclaimer ───────────────────────────────────────
    (r'[Uu]p to my (?:last )?training(?: update)?,?\s*', ''),
]

# ─────────────────────────────────────────────────────────────────────────────
# COMPILED PATTERNS
# ─────────────────────────────────────────────────────────────────────────────

_COMPILED_RULES: List[Tuple[re.Pattern, str]] = [
    (re.compile(pat, re.IGNORECASE), repl)
    for pat, repl in _AUTO_FIX_RULES
]

_AI_VOCAB_RE = re.compile(
    r'\b(' + '|'.join(re.escape(w) for w in AI_VOCABULARY_WORDS) + r')\b',
    re.IGNORECASE,
)

_AI_PHRASE_RE = re.compile(
    '|'.join(re.escape(p) if '.*' not in p else p for p in AI_PHRASES),
    re.IGNORECASE,
)

_EM_DASH_RE = re.compile(r' — ')


# ─────────────────────────────────────────────────────────────────────────────
# CORE FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def humanize_text(text: str) -> str:
    """
    Apply all safe phrase-level substitutions to remove AI writing patterns.
    Never restructures sentences — only removes/replaces phrases.
    """
    for pattern, replacement in _COMPILED_RULES:
        text = pattern.sub(replacement, text)

    # Clean up double spaces left by removals
    text = re.sub(r'  +', ' ', text)
    # Clean up leading comma/semicolon after removals e.g. ", results show"
    text = re.sub(r'(?<=\. ),\s*', '', text)
    text = re.sub(r'^,\s*', '', text, flags=re.MULTILINE)
    # Re-capitalise sentence starts that became lowercase after removal
    text = re.sub(
        r'(?<=[.!?]\s)([a-z])',
        lambda m: m.group(1).upper(),
        text,
    )
    # Re-capitalise line starts
    text = re.sub(
        r'(?m)^([a-z])',
        lambda m: m.group(1).upper(),
        text,
    )
    return text.strip()


def count_ai_vocabulary(text: str) -> Tuple[int, List[str]]:
    """Count AI vocabulary word hits. Returns (count, [unique_examples])."""
    matches = _AI_VOCAB_RE.findall(text)
    unique = list(dict.fromkeys(m.lower() for m in matches))
    return len(matches), unique[:8]


def count_ai_phrases(text: str) -> Tuple[int, List[str]]:
    """Count AI formulaic phrase hits. Returns (count, [unique_examples])."""
    matches = _AI_PHRASE_RE.findall(text.lower())
    unique = list(dict.fromkeys(matches))
    return len(matches), unique[:8]


def count_em_dashes(text: str) -> int:
    """Count spaced em dashes (overuse signal)."""
    return len(_EM_DASH_RE.findall(text))


def count_autofix_hits(text: str) -> int:
    """Count how many auto-fix patterns match (before fixing)."""
    total = 0
    for pattern, _ in _COMPILED_RULES:
        total += len(pattern.findall(text))
    return total


# ─────────────────────────────────────────────────────────────────────────────
# REPORT
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class HumanizerReport:
    ai_vocab_count:   int          # total occurrences of AI vocabulary words
    ai_vocab_examples: List[str]   # up to 8 unique examples
    ai_phrase_count:  int          # total formulaic phrase hits
    ai_phrase_examples: List[str]  # up to 8 unique examples
    em_dash_count:    int          # spaced em dash count
    autofix_count:    int          # patterns fixed by humanize_text()
    humanizer_penalty: int         # penalty contribution to overall score (0–30)

    def to_dict(self) -> dict:
        return {
            "ai_vocab_count":    self.ai_vocab_count,
            "ai_vocab_examples": self.ai_vocab_examples,
            "ai_phrase_count":   self.ai_phrase_count,
            "ai_phrase_examples": self.ai_phrase_examples,
            "em_dash_count":     self.em_dash_count,
            "autofix_count":     self.autofix_count,
            "humanizer_penalty": self.humanizer_penalty,
        }


def humanizer_report(text: str) -> HumanizerReport:
    """
    Analyse text for humanizer patterns and compute a penalty score.

    Penalty scale (max 30):
      AI vocabulary >20 occurrences   → -12 pts
      AI vocabulary >10               → -7 pts
      AI vocabulary >3                → -3 pts
      AI formulaic phrases >10        → -10 pts
      AI formulaic phrases >5         → -6 pts
      AI formulaic phrases >1         → -3 pts
      Em dashes >5                    → -5 pts
      Em dashes >2                    → -3 pts
      Autofix hits >10                → -8 pts
      Autofix hits >4                 → -4 pts
      Autofix hits >1                 → -2 pts
    """
    vocab_count, vocab_ex  = count_ai_vocabulary(text)
    phrase_count, phrase_ex = count_ai_phrases(text)
    em_count               = count_em_dashes(text)
    fix_count              = count_autofix_hits(text)

    # Vocab penalty — normalised by word count (per 1000 words)
    # Avoids over-penalising long papers for a few expected uses
    word_count    = max(1, len(text.split()))
    vocab_density = (vocab_count / word_count) * 1000   # hits per 1000 words

    if vocab_density > 8:   vp = 10
    elif vocab_density > 5:  vp = 6
    elif vocab_density > 2:  vp = 3
    else:                    vp = 0

    # Phrase penalty — raw count (these are always suspicious)
    if phrase_count > 10:  pp = 8
    elif phrase_count > 5:  pp = 5
    elif phrase_count > 1:  pp = 3
    else:                   pp = 0

    # Em dash penalty
    if em_count > 5:   ep = 4
    elif em_count > 2:  ep = 2
    else:              ep = 0

    # Autofix penalty — these are unambiguous AI filler patterns
    if fix_count > 10:   fp = 6
    elif fix_count > 4:   fp = 3
    elif fix_count > 1:   fp = 2
    else:                 fp = 0

    penalty = min(20, vp + pp + ep + fp)

    return HumanizerReport(
        ai_vocab_count    = vocab_count,
        ai_vocab_examples = vocab_ex,
        ai_phrase_count   = phrase_count,
        ai_phrase_examples = phrase_ex,
        em_dash_count     = em_count,
        autofix_count     = fix_count,
        humanizer_penalty = penalty,
    )
