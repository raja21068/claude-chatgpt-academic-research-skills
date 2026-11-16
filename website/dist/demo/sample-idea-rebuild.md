# Sample rebuild: When the calendar breaks the forecast — event-aware next-day library visit prediction

> **Sample answer, made up to show the format.** The project, papers and scores are fictional.

Keep the original goal of **forecasting next-day library visits**. Change the question: instead of "can a model forecast visits?", ask **when simple forecasts fail and whether calendar information fixes those failures**.

**Assessment: 76/100, up from 58/100. Novelty moves from 7/20 to 12/20.** Worth doing as a student project and a short paper.

## 1. What I would change in the original idea

| What the original proposed | Closest work | What the new version must show |
|---|---|---|
| Lag + weekday model for daily visits | Paper A (footfall forecasting) | Results broken down by day type, not just one average error |
| Beat a same-weekday baseline | Paper B (building occupancy) | Where the baseline fails: exams, holidays, term start |
| One library | Paper C (events in retail) | Whether the findings hold for a second year or site |

The strongest contribution: **a clear map of when simple library forecasts fail, and how much event features help in exactly those periods.**

## 2. Updated research idea

**Research question.** Do academic-calendar features reduce next-day forecast error during exam weeks and holidays, compared with a same-weekday baseline and a lag-only model?

**Example.** During exam week, visits double. The same-weekday baseline copies last week's lower number and under-predicts, so the library is under-staffed exactly when it is busiest.

| Case | What happens | What the model should do |
|---|---|---|
| **Normal week** | Visits follow the weekly pattern | Match the baseline; no gain expected |
| **Exam week** | Visits jump | Use the exam flag to predict the jump |
| **Unannounced event** | Visits change with no calendar signal | No model can know in advance — report it as a limit |

## 3. Methodology

### A. Data

Daily visit counts plus a calendar table: exam weeks, holidays, term start/end. Only use information known the day before.

### B. Models

1. Same-weekday baseline: \(\hat y_t = y_{t-7}\)
2. Lag model: \(\hat y_t = f(y_{t-1}, y_{t-7}, \text{weekday})\)
3. Lag + calendar model: add exam, holiday and term flags.

### C. Decision rule

- **Use the calendar model** if it lowers error on exam and holiday days without hurting normal days.
- **Keep the simpler model** if the gain is within noise.
- **Report as a limit** any day type where no model does well.

## 4. Experiments

| Experiment | Design | Evidence required |
|---|---|---|
| **1. Failure map** | Baseline error by day type (normal / exam / holiday / term start) | Errors clearly higher on event days |
| **2. Main test** | All 3 models, chronological split, same features available to each | Lower error on event days for the calendar model |
| **3. Ablation** | Remove one calendar flag at a time | Which flag matters most |
| **4. Transfer** | Train on one year, test on the next (or a second library) | Gains hold outside the training year |

Freeze the split, metrics (MAE per day type) and model list before looking at test data.

## 5. Score and decision

| Criterion | Original | Rebuilt | What still limits it |
|---|---|---|---|
| Problem importance | 10/15 | **11/15** | Still a local problem |
| Evidence that the gap exists | 6/15 | **10/15** | Needs the failure map to confirm |
| Novelty | 7/20 | **12/20** | Event features are known; the day-type analysis is the new part |
| Scientific insight | 8/15 | **12/15** | Explains *when* forecasts fail |
| Feasibility | 9/10 | **9/10** | Easy to run |
| Potential impact | 6/10 | **7/10** | Directly useful for staffing |
| Evaluation strength | 8/10 | **10/10** | Per-day-type errors + transfer test |
| Reproducibility | 4/5 | **5/5** | Calendar table is easy to share |
| **Total** | **58/100** | **76/100** | |

**Decisive experiment:** the failure map (Experiment 1). If the baseline does not fail on event days, the calendar idea has nothing to fix — write it up as a clean forecasting comparison instead.
