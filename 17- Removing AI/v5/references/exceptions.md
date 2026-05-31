# Personal Exceptions — Whitelisted Patterns

Patterns listed here are skipped by `slop_score.py` and `rhythm_check.py`.
Add entries when a rule produces false positives for your writing style or venue conventions.

---

## How to use

Each entry follows the format:

```
PATTERN: <exact phrase or regex>
TYPE: phrase | structure | hedge | passive
REASON: <why this is acceptable for you>
SECTION: all | abstract | introduction | related_work | method | results | analysis | conclusion
```

The scripts load this file and skip any match before counting it as a flag.

---

## Example entries (remove or replace with your own)

```
PATTERN: to the best of our knowledge
TYPE: phrase
REASON: Required by target venue (ACL) as convention for novelty claims
SECTION: introduction

PATTERN: it is worth noting
TYPE: phrase
REASON: Accepted in our lab's house style for drawing attention to non-obvious results
SECTION: results

PATTERN: we note that
TYPE: phrase
REASON: Preferred transition in analysis sections over harder alternatives
SECTION: analysis

PATTERN: may
TYPE: hedge
REASON: Single hedge is acceptable; only stacking (≥3) is flagged anyway
SECTION: all
```

---

## Notes

- Whitelisting a phrase removes it from the phrase-hit count but NOT from the hedge-density count.
  If you whitelist "may" as a phrase, sentences with 3+ hedges including "may" are still flagged.
- Keep this file short. A whitelist longer than 10 entries usually means the rules need recalibration,
  not more exceptions.
- Review exceptions before each submission. A venue exception may not apply to the next venue.
