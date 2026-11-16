# Sample review: Forecasting next-day visits to a campus library

> **Sample answer, made up to show the format.** The project, papers and scores are fictional. "Paper A", "Paper B"… stand in for the real papers your chat should find and link.

## 1. Scoring table

**Overall reviewer score: 58/100 — moderate potential.** Useful practical problem, but the contribution is not yet clear beyond standard forecasting.

| Criterion | Weight | Score | Rationale |
|---|---|---|---|
| Problem importance | 15 | **10** | Staffing and opening hours depend on visitor numbers; the problem is real but local. |
| Evidence that gap exists | 15 | **6** | No search shown yet; footfall forecasting is a known topic. |
| Novelty vs recent literature | 20 | **7** | Lag features + weekday are standard. Nothing new is claimed about the method. |
| Scientific insight | 15 | **8** | Could show *which* calendar events matter most, but the proposal does not ask that. |
| Experimental feasibility | 10 | **9** | Daily counts exist; runs on a laptop. |
| Potential impact | 10 | **6** | Useful for one library; transfer to others is unclear. |
| Evaluation strength possible | 10 | **8** | Chronological split and a same-weekday baseline are planned. |
| Reproducibility | 5 | **4** | Simple code; data may not be shareable. |
| **Total** | **100** | **58** | |

### Why the score is relatively low

The problem and the plan are sensible. The score is held back because the method is standard and the proposal does not say what new knowledge the study will produce.

## 2. Strongest aspects

### 2.1 A simple, honest baseline

Comparing against "same weekday last week" is exactly the baseline a library manager would use. Beating it is meaningful.

### 2.2 Realistic scope

Four weeks, public counts, a laptop: the plan can actually be finished.

## 3. Major weaknesses

### 3.1 The novelty is unclear (critical)

| Existing work | Overlap | Severity |
|---|---|---|
| Paper A (2022) — footfall forecasting for public buildings | Same task, same lag features | High |
| Paper B (2021) — university building occupancy prediction | Uses academic calendar | High |
| Paper C (2024) — retail visitor forecasting with events | Event features improve forecasts | Medium |

**Reviewer concern:** what will this study show that Papers A–C do not?

### 3.2 Exam periods and holidays are ignored

Library visits change sharply around exams. A model without calendar information may look good on average and fail exactly when staffing matters most.

### 3.3 One library, one year

Results from a single site and season may not generalise.

## 4. Novelty check

### 4.1 What cannot be claimed as new

| Proposed idea | Existing work | Judgment |
|---|---|---|
| Lag-based daily forecasting | Paper A | Not new |
| Weekday effects | Paper A, Paper B | Not new |
| Comparing with a naive baseline | Standard practice | Not new |

### 4.2 What could be new

**When do calendar events (exams, holidays, term breaks) make simple forecasts fail, and how much do event features fix those failures?**

### 4.3 Novelty judgment

- Method novelty: **Low**
- Question novelty: **Moderate, if narrowed**
- Practical value: **Moderate–high**

## 5. Evidence needed

- Search: library / building footfall forecasting, academic calendar effects, event-aware forecasting.
- **Experiment A:** error of the baseline on normal days vs exam days vs holidays.
- **Experiment B:** add calendar features; report error separately for each day type.

## 6. How to improve the score

1. **Narrow the question** to forecast failures around calendar events.
2. **Report errors by day type**, not only an average.
3. **Add a second library or year** to test transfer.

## 7. Expected score after improvement

| Criterion | Current | Potential |
|---|---|---|
| Evidence that gap exists | 6 | 10 |
| Novelty | 7 | 12 |
| Scientific insight | 8 | 11 |
| Potential impact | 6 | 7 |
| **Total** | **58** | **~70** |

## 8. Final assessment

**58/100 — revise before starting.** Narrow the question to calendar-driven failures and run Experiment A first. If the baseline does not fail on exam days, the simpler forecasting study is still a fine student project, but not a novel one.
