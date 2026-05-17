---
name: master-auto-review-loop
description: "Master autonomous review-and-improvement skill that preserves the original auto-review-loop package, routes to research, code, paper, citation, or full pipeline review, and produces auditable logs, gates, fixes, and final readiness verdicts. Use when the user says make it pass review, auto improve, reviewer loop, paper/code/research audit, one-shot review, or wants a top-journal/top-conference quality control loop."
argument-hint: "[project-directory-or-paper-directory] [--mode research|code|paper|citation|full] [--rounds N] [--difficulty medium|hard|nightmare] [--human-checkpoint true|false] [--backend codex|llm|minimax|oracle-pro] [--style-ref <source>] [--edit-whitelist <path>] [--soft-only] [--uncited]"
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, Agent, Skill, WebSearch, WebFetch, mcp__codex__codex, mcp__codex__codex-reply
---

# Master Auto Review Loop Skill

Autonomously improve a research project, experiment codebase, LaTeX paper, or citation layer through a controlled loop:

**inspect → readiness gates → external review → parse weaknesses → implement fixes → rerun/recompile → re-review → final audit**.

This master skill does **not** replace the existing uploaded skills. It acts as the router and quality-control layer above them.

---

## 0. Non-Destructive Rule

Preserve the uploaded structure exactly:

```text
auto-review-loop/
auto-review-loop-llm/
auto-review-loop-minimax/
auto-paper-improvement-loop/
citation-audit/
```

Do not rename, move, delete, or rewrite these original skill folders unless the user explicitly asks. Add new orchestration files beside them or inside `review-stage/` in the target project.

When making edits to the user's research/paper project:

1. Create a backup first.
2. Log every touched file.
3. Prefer minimal targeted edits over broad rewriting.
4. Never hide failed experiments, negative results, citation uncertainty, or unresolved reviewer concerns.
5. Never invent metrics, datasets, citations, ablation results, baselines, hyperparameters, or reviewer scores.

---

## 1. Mode Router

Select the mode from the user's request and project state.

| Mode | Use when | Delegate / base skill |
|---|---|---|
| `research` | The user wants the research idea, claims, experiments, or results reviewed and improved. | `auto-review-loop/SKILL.md` |
| `code` | The user wants implementation/code readiness, reproducibility, training/evaluation scripts, or experiment execution fixed. | `auto-review-loop/SKILL.md` + Code Readiness Gate below |
| `paper` | The user has a generated/compiled paper and wants writing, framing, logic, structure, claims, or presentation improved. | `auto-paper-improvement-loop/SKILL.md` |
| `citation` | The user wants references verified, citation contexts checked, or bib hallucinations removed. | `citation-audit/SKILL.md` |
| `full` | The user wants one-shot top-journal/top-conference review from idea/code/results to paper/citations. | Run gates and all relevant skills in sequence |
| `llm` | User wants OpenAI-compatible provider instead of Codex. | `auto-review-loop-llm/SKILL.md` |
| `minimax` | User specifically requests MiniMax. | `auto-review-loop-minimax/SKILL.md` |

Default mode selection:

- If a LaTeX paper exists with `main.tex` and `.bib`, choose `full` unless the user only asks for citations or writing.
- If code/results exist but no paper exists, choose `research` or `code`.
- If only a draft paper exists, choose `paper` then `citation`.
- If the user says “one-shot”, choose `full` and generate all readiness artifacts.

---

## 2. Required Output Folder

Create this folder inside the target project:

```text
review-stage/
  00_INPUT_INVENTORY.md
  01_METHOD_SUMMARY.md
  02_MISSING_INFORMATION_REPORT.md
  03_CODE_READINESS_GATE.md
  04_CLAIM_EVIDENCE_MAP.md
  05_REVIEW_PLAN.md
  AUTO_REVIEW.md
  REVIEW_STATE.json
  FINDINGS.md
  FINAL_READINESS_REPORT.md
  MANIFEST.md
```

If the project already contains `review-stage/`, preserve existing files and append timestamped versions:

```text
review-stage/archive/YYYYMMDD_HHMMSS_<artifact>.md
```

---

## 3. Input Inventory

Before reviewing, inspect and document available inputs.

Write `review-stage/00_INPUT_INVENTORY.md` with:

```markdown
# Input Inventory

## Project Root
- Path: ...
- Detected mode: research/code/paper/citation/full
- Existing review state: none / in_progress / completed

## Files Found
| Category | Files | Notes |
|---|---|---|
| Paper source | `main.tex`, `sections/*.tex` | ... |
| Bibliography | `references.bib` | ... |
| Figures | `figures/*` | ... |
| Code | `src/*`, `train.py`, `eval.py` | ... |
| Configs | `configs/*.yaml` | ... |
| Results | `results/*.json`, `tables/*.csv` | ... |
| Logs | `logs/*`, W&B exports | ... |
| Notes | README, method notes, reviewer notes | ... |

## Immediate Risks
- Missing result files: yes/no
- Missing dataset description: yes/no
- Missing citation file: yes/no
- Missing compile path: yes/no
- Missing random seeds: yes/no
```

---

## 4. Method Summary Gate

Before any reviewer loop, produce `review-stage/01_METHOD_SUMMARY.md`.

This forces the agent to understand the project instead of blindly editing.

Required sections:

```markdown
# Method Summary

## A. One-paragraph research goal
[What problem is solved and why it matters.]

## B. Input
- Data / benchmark / corpus:
- Features / modalities:
- Preprocessing:
- Train/validation/test split:
- External resources:

## C. Output
- Prediction / generation / estimation target:
- Metrics:
- Tables/figures expected:

## D. Architecture / Model / Method
- Core modules:
- Baselines:
- Proposed contribution:
- Mathematical objective / loss:
- Inference process:

## E. Training or estimation process
- Optimizer / estimator:
- Learning rate / tuning:
- Batch size:
- Epochs / stopping rule:
- Seeds:
- Hardware:

## F. Datasets
| Dataset | Role | Size | Split | Source | License/availability |
|---|---|---:|---|---|---|

## G. Evaluation
| Claim | Metric | Baseline | Result file | Figure/table | Status |
|---|---|---|---|---|---|

## H. Current evidence level
- Strong evidence:
- Weak evidence:
- Missing evidence:
- Claims that must be softened:
```

If any field cannot be found, write `UNKNOWN` and add it to the missing-information detector.

---

## 5. Missing Information Detector

Write `review-stage/02_MISSING_INFORMATION_REPORT.md` before implementation or paper improvement.

Detect at least these missing or ambiguous items:

### A. Code and experiment gaps
- hidden hyperparameters
- unspecified preprocessing
- unknown random seeds
- missing train/validation/test split
- missing optimizer settings
- missing scheduler settings
- missing batch size or epochs
- missing hardware/runtime
- missing baseline configuration
- missing evaluation script
- missing dataset filtering rules
- missing logging/checkpoint path
- missing package versions

### B. Method and math gaps
- ambiguous equations
- variables not defined
- losses stated but not implemented
- implementation differs from method description
- proposed module not used in training/evaluation
- claims stronger than available evidence

### C. Paper gaps
- uncited factual claims
- unsupported novelty claims
- missing limitations
- missing ablations
- missing failure cases
- result table not traceable to output file
- figure caption not describing actual result
- abstract claims not supported later

### D. Citation gaps
- citation key missing from bib
- bib entry uncited
- real paper but wrong context
- fabricated DOI/venue/year risk
- citation supports a weaker/different claim

Use severity labels:

```text
BLOCKER = cannot proceed honestly
HIGH = must fix before submission
MEDIUM = should fix for stronger paper
LOW = polish / clarity
```

---

## 6. Code Readiness Gate

Run this gate when mode is `code`, `research`, or `full`.

Write `review-stage/03_CODE_READINESS_GATE.md`.

The code is **not ready** until all required rows are PASS or honestly marked NOT_APPLICABLE.

| Gate | Required evidence | Verdict |
|---|---|---|
| Repository opens | tree can be listed, no missing core files | PASS/FAIL |
| Install path | requirements/environment file exists or can be inferred | PASS/FAIL |
| Config-driven run | experiment can be launched from config/CLI | PASS/FAIL |
| Dataset loader | loader exists and validates paths/splits | PASS/FAIL |
| Preprocessing specified | all transforms/filtering documented | PASS/FAIL |
| Model/method implemented | proposed method appears in code | PASS/FAIL |
| Loss implemented | losses match method summary | PASS/FAIL |
| Baselines implemented | required baselines available | PASS/FAIL |
| Metrics implemented | metrics match paper claims | PASS/FAIL |
| Reproducibility | seeds, deterministic flags, versions logged | PASS/FAIL |
| Smoke test | minimal run or dry-run exists | PASS/FAIL |
| Full run command | exact train/eval commands documented | PASS/FAIL |
| Output schema | results saved as JSON/CSV/plots | PASS/FAIL |
| Claim traceability | each number maps to file + command | PASS/FAIL |
| Error handling | missing files and bad configs fail clearly | PASS/FAIL |

### Code Readiness Decision

- `PASS`: Can run experiments and review results.
- `CONDITIONAL`: Can proceed, but missing items must be logged and claims softened.
- `FAIL`: Do not write strong paper claims. Fix code first.

If FAIL, create `review-stage/CODE_FIX_PLAN.md` with exact files to create/edit.

---

## 7. Claim–Evidence Map

Write `review-stage/04_CLAIM_EVIDENCE_MAP.md`.

Every important paper/research claim must map to concrete evidence.

```markdown
# Claim–Evidence Map

| Claim ID | Claim text | Evidence type | Source file | Metric/result | Figure/table | Status | Action |
|---|---|---|---|---|---|---|---|
| C1 | ... | experiment | results/main.json | Acc = ... | Table 1 | supported | keep |
| C2 | ... | citation | references.bib + intro.tex | ... | n/a | weak | soften |
| C3 | ... | none | n/a | n/a | n/a | unsupported | remove |
```

Rules:

1. If evidence is absent, do not keep the claim as written.
2. If evidence is partial, soften the wording.
3. If evidence contradicts the claim, mark `false/contradicted` and remove or rewrite.
4. If a number appears in the abstract, introduction, results, or conclusion, it must map to a result file.

---

## 8. Review Plan

Write `review-stage/05_REVIEW_PLAN.md` before running external review.

```markdown
# Review Plan

## Selected mode
- Mode:
- Backend:
- Difficulty:
- Max rounds:
- Human checkpoint:

## Reviewer role
- Senior reviewer level: top-tier peer-reviewed AI / CS / domain venue
- Review style: honest, adversarial, evidence-based

## What reviewer will see
- Files/context included:
- Files/context withheld for independence:
- Reason:

## Stop condition
- Score threshold:
- Verdict threshold:
- Hard blockers that override positive score:

## Fix priority
1. Integrity blockers
2. Method/code mismatches
3. Missing experiments/ablations
4. Claim softening
5. Citation corrections
6. Writing/format polish
```

---

## 9. Reviewer Independence Protocol

Use fresh reviewer threads when independence matters.

Required fresh-thread cases:

- first review round
- paper improvement review rounds
- citation audit per-entry checks
- any adversarial/nightmare review
- final readiness review

Allowed continuation-thread cases:

- round 2+ of a normal research auto-review where reviewer memory is intentional
- rebuttal ruling in hard mode

Bias guard:

- Do not tell the reviewer “we fixed everything” as a premise.
- Do not leak style references into reviewer prompts.
- Do not summarize weaknesses in a way that hides raw evidence.
- Save the full raw review response verbatim.

---

## 10. Core Review Loop

Repeat up to `MAX_ROUNDS`.

### Phase A — External Review

Use the selected backend:

- `codex`: base `auto-review-loop/SKILL.md`
- `llm`: base `auto-review-loop-llm/SKILL.md`
- `minimax`: base `auto-review-loop-minimax/SKILL.md`
- `paper`: base `auto-paper-improvement-loop/SKILL.md`
- `citation`: base `citation-audit/SKILL.md`

Reviewer prompt must request:

```markdown
1. Score from 1–10 for target venue / submission readiness
2. Verdict: ready / almost / not ready
3. Critical weaknesses ranked by severity
4. Minimum fix for each weakness
5. Evidence check: which claims are unsupported or overstated
6. Reproducibility check: can another researcher reproduce this?
7. Citation/context check if paper text is included
8. Required action list for the next round
```

### Phase B — Parse Review

Extract:

```json
{
  "round": 1,
  "score": 0.0,
  "verdict": "not ready",
  "critical_weaknesses": [],
  "minimum_fixes": [],
  "claim_risks": [],
  "citation_risks": [],
  "code_risks": [],
  "stop": false
}
```

Save raw review into `review-stage/AUTO_REVIEW.md` inside a collapsible block.

### Phase C — Fix Implementation

Implement fixes in this priority order:

1. False or unsupported claims
2. Code/result mismatch
3. Metric/evaluation bugs
4. Missing baseline/ablation if cheap enough
5. Missing method details
6. Citation corrections
7. Paper structure and writing
8. Formatting/LaTeX warnings

Before each edit:

- Check edit whitelist if provided.
- Reject edits that add fabricated citations or new numerical claims without evidence.
- Record accepted and rejected edits.

### Phase D — Rerun / Recompile / Recheck

Depending on mode:

- Code/research: run smoke tests, evaluation scripts, result aggregation, figure generation.
- Paper: run `latexmk` or the project compile command.
- Citation: re-run cite-key extraction and undefined citation check.
- Full: run all available checks in sequence.

If a full experiment is too expensive, run a smoke test and log that full run is pending. Do not claim final results from a smoke test.

### Phase E — Document Round

Append to `review-stage/AUTO_REVIEW.md`:

```markdown
## Round N — YYYY-MM-DD HH:MM

### Assessment
- Score:
- Verdict:
- Main weaknesses:

### Raw Reviewer Response
<details><summary>Full raw response</summary>

[paste verbatim]

</details>

### Fixes Implemented
| Weakness | File(s) changed | Fix | Evidence | Status |
|---|---|---|---|---|

### Commands Run
```bash
...
```

### Results
- New metrics:
- Compile/test status:
- Remaining blockers:
```

Update `review-stage/REVIEW_STATE.json` after each round.

---

## 11. Paper Improvement Subroutine

Use when mode is `paper` or `full` and paper source exists.

Base behavior from `auto-paper-improvement-loop`:

1. Preserve original paper.
2. Collect paper text.
3. Fresh external review.
4. Implement fixes.
5. Recompile.
6. Run second fresh review.
7. Recompile and format-check.
8. Write `PAPER_IMPROVEMENT_LOG.md`.

Additional master rules:

- Do not rewrite the whole paper unless the review demands structure-level repair.
- If `--style-ref` is provided, use it only to guide structure, paragraph density, section flow, and figure/table balance.
- Never copy prose, claims, examples, or terminology from the style reference.
- If `--edit-whitelist` is provided, obey it strictly and log rejected edits.
- Do not add new citations unless citation verification can be completed.
- If a sentence is unsupported, prefer softening/removing over inventing a citation.

---

## 12. Citation Audit Subroutine

Use when mode is `citation` or `full` and a `.bib` file exists.

Base behavior from `citation-audit`:

1. Extract every `\cite{...}` key and surrounding sentence.
2. Parse all bib entries.
3. Verify existence, metadata, and context.
4. Produce `CITATION_AUDIT.md` and `CITATION_AUDIT.json`.
5. Apply safe fixes only.
6. Recompile and check undefined citations.

Master additions:

- For `--soft-only`, do not mutate `.bib`; rewrite/soften citing sentences instead.
- For `--uncited`, report uncited entries, but do not treat them as failure unless they are used in hidden/manual bibliography text.
- REPLACE and REMOVE require explicit evidence. If uncertain, mark `UNCERTAIN` and avoid destructive changes.

---

## 13. Full One-Shot Pipeline

When the user asks for “one-shot”, “make it top journal/conference ready”, or “do everything”, run:

```text
1. Input Inventory
2. Method Summary Gate
3. Missing Information Detector
4. Code Readiness Gate, if code exists
5. Claim–Evidence Map
6. Research/code auto-review loop, if code/results exist
7. Paper improvement loop, if paper exists
8. Citation audit, if bibliography exists
9. Final readiness review
10. Final report + manifest
```

Minimum final outputs:

```text
review-stage/00_INPUT_INVENTORY.md
review-stage/01_METHOD_SUMMARY.md
review-stage/02_MISSING_INFORMATION_REPORT.md
review-stage/03_CODE_READINESS_GATE.md
review-stage/04_CLAIM_EVIDENCE_MAP.md
review-stage/05_REVIEW_PLAN.md
review-stage/AUTO_REVIEW.md
review-stage/FINAL_READINESS_REPORT.md
review-stage/MANIFEST.md
```

Optional outputs when relevant:

```text
review-stage/CODE_FIX_PLAN.md
review-stage/CLAIMS_FROM_RESULTS.md
review-stage/PAPER_IMPROVEMENT_LOG.md
review-stage/CITATION_AUDIT.md
review-stage/CITATION_AUDIT.json
review-stage/REVIEWER_MEMORY.md
```

---

## 14. Final Readiness Report

Write `review-stage/FINAL_READINESS_REPORT.md`.

```markdown
# Final Readiness Report

## Overall Verdict
- READY / ALMOST READY / NOT READY
- Score progression:
- Final reviewer score:

## What was improved
| Area | Before | After | Evidence |
|---|---|---|---|

## Remaining blockers
| Severity | Issue | Why it matters | Required fix |
|---|---|---|---|

## Code readiness
- Verdict:
- Tests/commands run:
- Reproducibility status:

## Paper readiness
- Compile status:
- Overclaim status:
- Structure status:
- Figure/table status:

## Citation readiness
- Undefined citations:
- Wrong-context citations:
- Metadata issues:

## Claim integrity
| Claim | Evidence | Status |
|---|---|---|

## Recommended next action
- Submit / revise manually / run more experiments / collect missing data / rewrite claims
```

Decision rules:

- `READY`: no blockers, code/paper/citation gates pass, final reviewer verdict ready or almost ready.
- `ALMOST READY`: no integrity blockers, but polish or moderate missing details remain.
- `NOT READY`: any false claim, missing core experiment, unreproducible result, broken compile, or citation integrity blocker remains.

A high reviewer score cannot override an integrity blocker.

---

## 15. Manifest

Append every created or modified file to `review-stage/MANIFEST.md`.

```markdown
# Review-stage Manifest

| Time | File | Action | Reason |
|---|---|---|---|
| ... | review-stage/01_METHOD_SUMMARY.md | created | method understanding gate |
| ... | sections/results.tex | edited | softened unsupported claim C3 |
```

---

## 16. Activation Prompt

Use this prompt when running the master skill on a new project:

```text
Use the master-auto-review-loop skill on this project.

Project path: <PATH>
Target venue/type: <journal/conference/domain>
Mode: full
Difficulty: hard
Rounds: 2-4
Human checkpoint: false unless an edit could change scientific meaning
Backend: codex or available external reviewer

Required behavior:
1. Preserve the original project structure.
2. Create review-stage/ outputs.
3. First produce Method Summary, Missing Information Report, Code Readiness Gate, and Claim–Evidence Map.
4. Run the appropriate review loop.
5. Implement only evidence-supported fixes.
6. Recompile/rerun checks.
7. Run citation audit if a bib file exists.
8. End with FINAL_READINESS_REPORT.md and MANIFEST.md.

Do not invent data, citations, baselines, metrics, or successful results. If information is missing, mark UNKNOWN and create a fix plan.
```

---

## 17. Key Rules

- Preserve original folders and project structure.
- Always inspect before editing.
- Always create readiness gates before reviewer loop.
- Always keep raw reviewer responses.
- Always map claims to evidence.
- Always distinguish smoke-test results from full experiment results.
- Always verify citations before adding or changing them.
- Always recompile/rerun after edits when possible.
- Never let writing polish hide scientific weakness.
- Never let reviewer optimism override reproducibility, citation, or evidence blockers.
