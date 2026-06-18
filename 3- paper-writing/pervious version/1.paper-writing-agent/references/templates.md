# Paper Writing Templates

Use these templates when producing structured outputs during paper writing.

## Claim-Evidence Matrix

| Claim | Evidence source | Strength | Citation needed | Safe wording | Integrity tag | Status |
|---|---|---|---|---|---|---|
| [claim] | [source] | strong/moderate/weak/unsupported | [yes/no/TODO] | [safer phrasing] | ok / [INTEGRITY WARN] / [INTEGRITY CONCERN] | [done/needs work/TODO] |

**Strength guide:**
- Strong: directly supported by provided experiments or verified literature
- Moderate: broadly supported but needs clearer reporting or comparison
- Weak: plausible but evidence is incomplete
- Unsupported: remove, soften, or mark TODO

**Integrity tag guide:**
- `ok` — no integrity audit concerns
- `[INTEGRITY WARN]` — experiment-audit issued a warning on this claim; use conservative scope language
- `[INTEGRITY CONCERN]` — experiment-audit flagged a FAIL on this claim; verify evidence before writing

---

## Literature Matrix

| Cluster | Key papers | What they do | Gap / open direction | How our work differs | Citation priority |
|---|---|---|---|---|---|
| [theme] | [papers] | [summary] | [what is not yet solved] | [our difference] | P0/P1 |

Note: use "gap" or "open direction" rather than "limitation" in this column — it frames the field's state of knowledge positively.

---

## Citation Priority Table

| Citation | Priority | Role | Section | Claim supported | Verification status |
|---|---|---|---|---|---|
| [ref] | P0/P1 | baseline/dataset/metric/method/background | [section] | [claim] | verified/needs-check/TODO |

---

## Venue Compliance Table

| Requirement | Status | Evidence / Location | Fix needed |
|---|---|---|---|
| Page limit | pass/risk/fail/unknown | [details] | [fix] |
| Anonymity | ... | ... | ... |
| Citation style | ... | ... | ... |
| Required sections | ... | ... | ... |
| Supplementary rules | ... | ... | ... |
| No "limitation"/"limitations" in body text | pass/fail | [scan result] | [fix] |

---

## Experimental Log Template

```markdown
## Experiment: [name]

### Setup
- Dataset: 
- Baselines: 
- Metrics: 
- Hardware: 
- Seeds/runs: 

### Results
| Method | Metric 1 | Metric 2 | Notes |
|---|---|---|---|

### Ablations
| Variant | Change | Result | Insight |
|---|---|---|---|

### Observations
- ...

### Scope and Assumptions
- [State what conditions this experiment assumes or requires]
- [Note what configurations were NOT tested — as open directions, not failures]
- Example: "Tested on dataset A only — extension to dataset B is an open direction"
```

---

## Claim Audit Log Template

```markdown
## Claim Audit: [date]

| # | Location | Paper Value | Source Value | Status | Fix Applied |
|---|----------|-------------|-------------|--------|-------------|
| 1 | Table 2 | 85.3% | 85.28% | rounding_ok | — |
| 2 | Abstract | "15%" | 12.8% | number_mismatch | Changed to "12.8%" |

**Overall verdict**: PASS / WARN / FAIL / NOT_APPLICABLE
```

---

## Figure/Table Plan

| ID | Type | Purpose | Data source | Claim supported | Placement | Caption draft | Risk |
|---|---|---|---|---|---|---|---|

---

## Novelty Positioning Map

```markdown
## Core contribution
[one sentence]

## What is reused from prior work
- ...

## What is new in this paper
- ...

## Closest prior work
| Prior work | Similarity | Difference | Evidence for difference | Citation status |
|---|---|---|---|---|

## Safe novelty statement
[conservative, verifiable claim]
```

---

## Writing Preferences (defaults)

- Output format: Markdown (alternative: LaTeX)
- Tone: rigorous, clear, concise, academic
- Claim style: conservative and evidence-grounded
- Citation style: venue default
- TODO markers: always used for missing information
- English: American
- Avoid: exaggerated novelty, fabricated citations/results, vague methods, promotional language, the words "limitation"/"limitations" in body text
- Include when relevant: scope assumptions and conditions, reproducibility details, ethical considerations, dataset/baseline descriptions, figure/table captions
