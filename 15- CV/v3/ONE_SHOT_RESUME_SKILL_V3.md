---
name: one-shot-resume-agent
description: Generate a complete evidence-based job application package in one run: tailored ATS resume or academic CV, cover letter, recruiter email, LinkedIn update, interview prep, evidence matrix, ATS/recruiter critique, and optional LaTeX/PDF. Use when the user provides a resume, CV, profile notes, publications, portfolio, or job description and wants application materials without fabricated claims.
---

# One-Shot Resume Agent

Create a complete, truthful, role-targeted application package from candidate evidence and a target job description. The default is **one strong pass with self-review**, not endless questions.

## Start here

1. Read the user's candidate evidence, job description, files, constraints, and desired output.
2. If the request is broad such as “make everything,” produce the full package.
3. If inputs are partial, continue with best effort and add `MISSING_EVIDENCE_AND_TODOS.md`.
4. Never invent candidate facts. Use `[TODO: verify ...]` for missing metrics or uncertain claims.
5. Prefer concise ATS-safe documents over decorative formatting.

## Use progressive disclosure

Read only the reference files needed for the current task:

- `references/01-evidence-and-anti-fabrication.md` for truth control.
- `references/02-ats-and-formatting.md` for ATS-safe structure.
- `references/03-job-analysis-and-keywords.md` for JD parsing and keyword mapping.
- `references/04-bullet-writing.md` for bullet upgrades.
- `references/05-resume-cv-playbooks.md` for role-specific resumes and academic CVs.
- `references/06-cover-letter-email-linkedin.md` for supporting documents.
- `references/08-review-rubrics.md` for final critique.
- `references/10-failure-modes-and-repair.md` when the draft feels generic, inflated, too long, or unsupported.

Use templates in `templates/` and scripts in `scripts/` when producing files.

## Default full output package

Create this folder when file writing is available:

```text
applications/{Company}_{Role}/
  00_INPUT_SUMMARY.md
  01_JOB_ANALYSIS.md
  02_EVIDENCE_MATRIX.md
  03_STRATEGY_AND_GAPS.md
  04_TAILORED_RESUME.md
  04_TAILORED_RESUME.tex            optional when LaTeX requested
  05_COVER_LETTER.md
  05_COVER_LETTER.tex               optional when LaTeX requested
  06_APPLICATION_EMAIL.md
  07_LINKEDIN_UPDATE.md
  08_INTERVIEW_PREP.md
  09_ATS_RECRUITER_SCORECARD.md
  10_EDITING_REPORT.md
  11_FINAL_SUBMISSION_CHECKLIST.md
  MISSING_EVIDENCE_AND_TODOS.md     if anything is uncertain or missing
```

If the user asks only for resume/CV, still include a short evidence matrix, gap note, and scorecard.

## Quality gates before final answer

Do not finalize until these gates pass:

- Every major claim maps to evidence or is marked TODO.
- Top job requirements are reflected naturally, not stuffed.
- Resume is scan-friendly in 6 to 10 seconds.
- Dates, titles, degrees, employers, and metrics are not changed without evidence.
- Cover letter adds context instead of repeating the resume.
- The scorecard clearly separates confirmed strengths, stretch areas, and missing evidence.
- Final checklist warns the user about all TODOs before submission.

## One-shot behavior

Ask at most one blocking question only when there is no usable candidate evidence or no target role and the user requests a final tailored document. Otherwise, proceed, state assumptions, and mark missing evidence.

## Output style

Write directly and professionally. Avoid AI-sounding filler, inflated adjectives, em dashes, decorative ATS-breaking layouts, fake precision, and unsupported confidence.
