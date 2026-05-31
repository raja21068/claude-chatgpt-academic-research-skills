# Section Norms — Context-Aware Rule Application

Some rules apply everywhere. Some rules apply only in specific sections.
This file maps each rule to where it should and should not be enforced.
The style checker and slop scorer load this to avoid false positives.

---

## Rule: Passive voice

| Section | Enforcement |
|---------|-------------|
| Abstract | Strict — find the actor |
| Introduction | Strict |
| Related Work | Strict |
| Method | **Relaxed** — passive acceptable when the actor is genuinely the system or the data ("inputs are tokenized", "gradients are clipped"). Flag passive only when the actor is a person or an unnamed agent. |
| Experimental Setup | Relaxed — "experiments were run on" is acceptable |
| Results | Strict — "results were achieved" is weak; "the model achieves" is better |
| Analysis / Ablation | Strict |
| Scope & Assumptions | Moderate — some passive acceptable in scope statements |
| Conclusion | Strict |

---

## Rule: Hedge density (threshold ≥ 3 per sentence)

| Section | Threshold | Notes |
|---------|-----------|-------|
| Abstract | 1 | Abstract hedges weaken the paper's first impression |
| Introduction | 1 | Claims should be bold here |
| Related Work | 2 | Describing prior work sometimes requires hedged characterisation |
| Method | 1 | Method descriptions should be declarative |
| Results | 1 | Results are stated facts; hedge only when genuinely uncertain |
| Analysis | 2 | Analysis often involves inference; slightly more tolerance |
| Scope & Assumptions | **3** | This section exists to state uncertainty; hedges are appropriate here |
| Conclusion | 1 | Strong ending; minimise hedging |

---

## Rule: "We" as sentence subject frequency

| Section | Guidance |
|---------|----------|
| Abstract | Acceptable once; avoid making every sentence "We X" |
| Introduction | Acceptable for contribution bullets; vary elsewhere |
| Related Work | Avoid — this section is about prior work, not about us |
| Method | Acceptable for design choice explanations; alternate with system as subject |
| Results | Minimize — "the model" or the result itself should be the subject |
| Analysis | Moderate — "we observe that" once per paragraph maximum |
| Conclusion | Acceptable for the core finding restatement |

---

## Rule: Single-number claims (claiming improvement without naming baseline or metric)

| Section | Enforcement |
|---------|-------------|
| Abstract | Strict — must name metric, dataset, and comparison |
| Introduction | Strict — contribution claims must be specific |
| Related Work | Moderate — summarising prior results doesn't always need the comparison point |
| Results | Strict — every reported number needs its context |
| Analysis | Strict |
| Conclusion | Strict — restate the strongest result with full context |

---

## Rule: Forward references ("details in Section X")

| Section | Limit |
|---------|-------|
| Method | ≤ 2 forward references acceptable |
| All other sections | 0 forward references; state the information or use an Appendix reference |

---

## Rule: Tense

| Section | Expected tense | Notes |
|---------|---------------|-------|
| Abstract | Past (findings) + Present (contributions) | "We proposed X, which achieves Y" |
| Introduction | Present for general statements; past for completed work | |
| Related Work | Past for describing prior work | "Smith et al. showed" not "show" |
| Method | Present (describing the method as it stands) | "The encoder processes" |
| Experimental Setup | Past (experiments were conducted) | |
| Results | Past (what happened) | "The model achieved", not "achieves" |
| Analysis | Past (what was observed) | |
| Conclusion | Past for findings; present for implications | |

---

## Rule: Citation required

| Section | Requirement |
|---------|-------------|
| Introduction | Every factual claim about prior work or field state needs a citation |
| Related Work | Every paper described needs a citation; every factual claim about a method |
| Method | Architectural components borrowed from prior work need citations |
| Results | Dataset and baseline papers need citations |
| Analysis | Claims about why something works that aren't proved here need citations |
| Abstract | Usually no citations unless venue requires |
| Conclusion | No new citations |

---

## Summary: strictest sections

**Abstract** and **Results** are the strictest: no hedges, no passive, every number contextualised,
every claim specific.

**Scope & Assumptions** is the most relaxed: hedging is appropriate, some passive acceptable,
the purpose is honest acknowledgment of what the work doesn't cover.

**Related Work** allows slightly more passive and hedge in characterising prior work,
but requires a contrast sentence per paragraph and no chronological organisation.
