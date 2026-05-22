---
name: one-shot-resume-agent
description: Generate a complete, evidence-based job application package in one run: tailored ATS resume or academic CV, cover letter, recruiter email, LinkedIn update, interview prep, evidence matrix, ATS/recruiter scorecard, editing report, and optional LaTeX/PDF files. Use when the user gives a candidate profile, resume, CV, notes, portfolio, publications, or a job description and wants application materials.
---

# One-Shot Resume Agent

This skill creates a complete application package from candidate evidence plus a target job description. It combines a one-shot job application pipeline, strict evidence control, ATS tailoring, top 10 percent CV strategy, academic CV handling, bullet improvement, cover letter generation, LinkedIn optimization, interview prep, critique, and optional LaTeX/PDF compilation.

The default behavior is: **do the work in one pass, ask only one blocking question if absolutely necessary, and mark missing evidence with TODO placeholders instead of inventing.**

## Use this skill when

Use this skill for requests such as:

- Generate a resume, CV, cover letter, application email, or all of them at once.
- Tailor my resume for this job description.
- Create an ATS resume and cover letter as PDF or LaTeX.
- Make an academic CV, research CV, technical CV, executive resume, career-change resume, or internship application.
- Analyze a job description and tell me if I am a match.
- Improve bullets using STAR, CAR, X-Y-Z, metrics, or recruiter language.
- Create LinkedIn headline, About section, interview prep, reference list, portfolio case study, or salary negotiation prep as part of an application.

## Core promise

A top application package is not a decorative document. It is a targeted evidence document that proves fit for one role. Optimize in this order:

1. Truth and evidence.
2. Role relevance.
3. Impact and metrics.
4. ATS alignment.
5. Recruiter scanability.
6. Human, non-generic tone.
7. Brevity and page control.

## Required inputs

The skill can work with partial inputs, but the best one-shot result needs:

- Candidate evidence: current resume or CV, profile notes, work history, education, skills, projects, publications, achievements, portfolio, LinkedIn, or raw bullets.
- Target role: job description, company, job title, location, country, seniority, application instructions, and any required documents.
- Constraints: one-page or two-page, resume or CV, country style, target tone, LaTeX/PDF/Markdown/DOCX preference, deadline, no LinkedIn link, no phone, or other limits.

If one of these is missing, continue with best effort and create a `MISSING_EVIDENCE_AND_TODOS.md` section. Do not stop unless the missing item makes the output impossible, for example no candidate evidence at all and the user asks for a final resume.

## Hard safety and evidence rules

Always enforce these rules:

1. **No fabrication.** Do not invent employers, job titles, degrees, dates, metrics, publications, awards, tools, certifications, location, visa status, salary, references, or contact details.
2. **No fake quantification.** If impact exists but numbers are unknown, use conservative wording or `[TODO: verify metric]`. Do not turn guesses into facts.
3. **No hiding gaps.** If the job asks for something the candidate lacks, show a transferable bridge or mark it as a gap. Do not pretend they have it.
4. **No keyword stuffing.** Use job description language naturally only where it matches real evidence.
5. **No overclaiming.** Verbs must match the candidate's actual role. Use “built,” “analyzed,” “supported,” “contributed,” “coordinated,” or “implemented” only when supported.
6. **No vague cliché language.** Avoid unsupported phrases like hardworking, passionate, detail-oriented, results-driven, dynamic, motivated, team player, proven track record, and similar filler.
7. **No AI-sounding prose.** Avoid words and phrases such as delve, tapestry, multifaceted, pivotal, seamless, robust when empty, realm, landscape, synergy, paradigm, underscore, leverage when overused, and generic “I am excited to apply” openings.
8. **No irrelevant life history.** Select evidence for the target role. A resume is not a biography.
9. **ATS-safe by default.** Use standard section names, simple headings, real text, consistent dates, no icons inside ATS version, no tables for core experience, no scanned PDFs.
10. **Preserve fixed facts.** Do not rewrite names, dates, degree titles, publication metadata, or contact details unless the user confirms a correction.
11. **Country conventions matter.** Use CV or resume norms for the target country. Do not include photo, date of birth, marital status, full address, or references unless the country or user requires it.
12. **Latex special characters.** Escape `&`, `%`, `$`, `#`, `_`, `{`, `}`, `~`, `^`, and backslashes when generating LaTeX.

## One-shot output package

Unless the user asks for fewer documents, create this package:

```text
applications/{Company}_{Role}/
  00_INPUT_SUMMARY.md
  01_JOB_ANALYSIS.md
  02_EVIDENCE_MATRIX.md
  03_STRATEGY_AND_GAPS.md
  04_TAILORED_RESUME.md
  04_TAILORED_RESUME.tex              optional
  05_COVER_LETTER.md
  05_COVER_LETTER.tex                 optional
  06_APPLICATION_EMAIL.md
  07_LINKEDIN_UPDATE.md
  08_INTERVIEW_PREP.md
  09_ATS_RECRUITER_SCORECARD.md
  10_EDITING_REPORT.md
  11_FINAL_SUBMISSION_CHECKLIST.md
  MISSING_EVIDENCE_AND_TODOS.md       if needed
```

If LaTeX compilation is available, also create:

```text
  resume.pdf
  cover_letter.pdf
```

If the user asks only for resume, produce the resume plus brief evidence matrix and scorecard. If the user asks for “everything,” produce the full package.

## Workflow

### Phase 0: Intake and output decision

Read all user files and pasted content before writing. Decide:

- Output type: resume, academic CV, executive resume, technical resume, career-change resume, internship resume, cover letter, full application package.
- Page target: one-page, two-page, academic CV length, country norms.
- File format: Markdown, LaTeX, PDF, DOCX if external tool supports it, or plain text.
- Candidate voice: concise, senior, research-oriented, technical, policy-oriented, business, academic, or student.

Create an intake summary with:

```markdown
# Input Summary
- Candidate evidence received:
- Job description received:
- Target company:
- Target role:
- Output package:
- Constraints:
- Missing or ambiguous items:
- Assumptions used:
```

### Phase 1: Evidence control

Build an evidence registry before drafting. Every major claim must map to a source.

Use these labels:

- **Confirmed:** explicitly present in user evidence.
- **Derived:** logically derived from evidence, without adding new facts.
- **Needs verification:** likely but not confirmed.
- **Missing:** required by job, not found in evidence.
- **Excluded:** true or possible, but not relevant or not safe to include.

Evidence matrix format:

```markdown
| Job requirement | Priority | Candidate evidence | Evidence status | Resume placement | Cover letter angle | Risk/TODO |
|---|---:|---|---|---|---|---|
```

Provenance rule: If a bullet, summary claim, or cover-letter sentence cannot be traced to evidence, remove it or mark TODO.

### Phase 2: Job description deconstruction

Analyze the job post like an ATS plus a recruiter.

Extract:

- Company name and business context.
- Role title and role family.
- Seniority level.
- Location, remote status, visa or work authorization notes.
- Required qualifications.
- Preferred qualifications.
- Core responsibilities.
- Tools, methods, software, domains, and keywords.
- Repeated terms and exact phrase candidates.
- Soft skills that are actually evidenced by duties.
- Application instructions.
- Possible red flags.

Classify keywords:

```markdown
| Keyword or phrase | Type | Priority | Exact JD wording | Candidate evidence | Use in resume? |
|---|---|---:|---|---|---|
```

Priority scale:

- Tier 1: repeated, required, title-level, responsibility-level, or screening keyword.
- Tier 2: preferred or secondary skill.
- Tier 3: nice-to-have or culture language.

Calculate a transparent match estimate:

```text
Match estimate = weighted evidence coverage, not a guaranteed ATS score.
```

Suggested bands:

- 85 to 100: strong match.
- 70 to 84: competitive with focused tailoring.
- 55 to 69: possible, needs clear bridge and gap handling.
- Below 55: stretch role, apply only if strategic.

### Phase 3: Strategy and positioning

Write a role strategy before the resume.

Output:

```markdown
# Positioning Strategy
- Core positioning sentence:
- Top 3 evidence pillars:
- Strongest transferable bridge:
- Keywords to use naturally:
- Keywords not safe to use:
- Gaps and how to handle them:
- What to lead with:
- What to minimize:
```

Examples of role-specific positioning:

- **Research or economics:** methods, datasets, identification strategy, policy relevance, writing outputs, reproducibility.
- **Data analyst or AI:** tools, pipelines, modeling, SQL/Python, dashboards, data scale, deployment, stakeholders.
- **EdTech or education:** curriculum, student outcomes, LMS operations, assessment, teacher coordination, content quality.
- **Finance or FP&A:** forecasting, variance analysis, budgeting, reporting, Excel/SQL, business decisions.
- **Academic CV:** publications, research agenda, methods, teaching, grants, presentations, service.
- **Executive:** scope, P&L, teams, strategy, transformation, stakeholder influence, board-level outcomes.
- **Career changer:** transferable skills first, then domain bridge. Do not hide the original domain.

### Phase 4: Bullet bank and achievement upgrading

For each role or project, select the strongest evidence for the target job. Rewrite bullets using one of these formulas:

**X-Y-Z formula**

```text
Accomplished [X result] as measured by [Y metric] by doing [Z action/method].
```

**CAR formula**

```text
Challenge/context + Action + Result.
```

**STAR condensed formula**

```text
Situation/task + action + measurable or concrete result.
```

**Technical bullet formula**

```text
Built/implemented/analyzed [system/dataset/model/process] using [tools/methods] to [business/research/user outcome].
```

**Research bullet formula**

```text
Estimated/tested/evaluated [research question] using [data/method] to show [finding or contribution].
```

Bullet rules:

- Start with an accurate action verb.
- Include tool, method, domain, scale, or output whenever available.
- Use one idea per bullet.
- Prefer concrete nouns over adjectives.
- Put the most job-relevant evidence in the first two bullets.
- Avoid “responsible for,” “worked on,” “helped with,” “involved in,” unless the role was truly support-only.
- Use `[TODO: quantify X]` rather than inventing a metric.
- Do not overuse the same verb.
- Keep bullets short enough for the selected page target.

Metric discovery questions:

- How many users, students, clients, datasets, transactions, reports, papers, dashboards, or stakeholders?
- What time, cost, error, accuracy, speed, completion, revenue, adoption, ranking, grade, or quality changed?
- What was the before and after?
- What was the frequency, monthly/weekly/daily volume, or time period?
- What tool or process was improved?
- Who used the result?

Conservative metrics are allowed only when the user evidence supports them. Ranges are safer than exact numbers when evidence is partial, for example “50+” only if the source supports at least 50.

### Phase 5: Resume or CV generation

Choose the right document type.

#### ATS resume structure

Use this order by default:

1. Name and contact.
2. Targeted headline or role line.
3. Summary, 3 to 5 lines.
4. Skills or core competencies.
5. Experience.
6. Projects or selected research, if stronger than experience.
7. Education.
8. Certifications, awards, publications, leadership, or languages if relevant.

ATS rules:

- Use standard section headings: Summary, Skills, Experience, Projects, Education, Certifications, Publications.
- Use text-based PDF or DOCX. Do not output scanned images.
- Use consistent dates: `MMM YYYY - MMM YYYY` or `YYYY - YYYY`.
- Avoid tables for main experience.
- Avoid icons in ATS version.
- Keep columns minimal. If using LaTeX, keep source clean and text extractable.
- File name: `FirstName_LastName_Resume_TargetRole.pdf`.

#### Academic CV structure

Use when the target is academic, research, postdoc, faculty, research assistant, research scientist, PhD, scholarship, fellowship, or grant-related.

Recommended order:

1. Contact.
2. Research profile or research interests.
3. Education.
4. Research appointments.
5. Publications.
6. Working papers or manuscripts.
7. Conference presentations.
8. Teaching experience.
9. Grants, awards, honors.
10. Technical skills and methods.
11. Service, leadership, outreach.
12. References if requested.

Academic CV rules:

- Do not relabel unpublished work as published.
- Preserve author order and publication status.
- Use “under review,” “working paper,” “manuscript in preparation,” only if confirmed.
- Do not inflate role in coauthored work.
- Emphasize methods, contribution, research question, and evidence.

#### Technical resume structure

For software, data, AI, analytics, and engineering roles:

- Lead with technical skills grouped by relevance.
- Include project architecture, tools, data scale, deployment, tests, stakeholders, and measurable outcomes.
- Avoid raw code counts unless user explicitly wants them and source supports them.
- Show production impact, not just coursework.

#### Executive resume structure

For leadership roles:

- Use a strong executive profile.
- Show scope: budget, team size, regions, revenue, strategy, transformation, stakeholders.
- Focus on business outcomes and leadership decisions.
- Two pages is acceptable for senior roles.

#### Career change resume structure

- Lead with transferable strengths tied to the target job.
- Keep prior domain honest.
- Use a bridge summary.
- Add projects, certifications, or portfolio evidence that lowers perceived risk.

### Phase 6: Cover letter generation

Default cover letter length:

- Industry: 250 to 350 words, 3 paragraphs.
- Academic/research/lab: 350 to 650 words, 4 paragraphs.
- Internship/student: 220 to 320 words.

Structure:

1. Hook: connect company role to candidate evidence. Avoid generic openings.
2. Fit paragraph: 2 to 3 strongest evidence points aligned to requirements.
3. Contribution paragraph: what the candidate can do in the role.
4. Closing: concise, confident, not exaggerated.

Cover letter rules:

- Do not repeat the resume line by line.
- Do not use flattery without evidence.
- Do not invent company projects unless supplied or researched separately.
- If the employer name or hiring manager is unknown, use a safe greeting.
- Use the same truth standards as the resume.
- Match tone to employer: academic, startup, nonprofit, government, corporate, or research lab.

Hook verification gate:

Before finalizing, check:

- Does paragraph 1 clearly name the role?
- Does it connect the candidate's actual evidence to the employer's need?
- Is there a non-generic reason for fit?
- Are there any unsupported company claims?

### Phase 7: Recruiter email, LinkedIn, interview, portfolio, references

When generating the full package, include these supporting assets.

#### Application email

Structure:

```text
Subject: Application for [Role] - [Candidate Name]
Dear [Hiring Manager/Team],
[1 sentence role application]
[1 to 2 sentences strongest fit]
[Attachments note]
[Concise closing]
```

#### LinkedIn update

Produce:

- Headline, under 220 characters.
- About section, 3 short paragraphs.
- Experience bullet rewrites, 3 to 5 bullets for target role.
- Featured section suggestions.
- Skills list, top 20 to 40 skills, grouped by search value.

LinkedIn differs from a resume: it can be warmer and broader, but it must still be evidence-based.

#### Interview prep

Produce:

- 30-second pitch.
- 60-second pitch.
- Why this role.
- Why this company.
- Top 8 likely questions.
- STAR story bank: leadership, conflict, technical problem, failure, impact, teamwork, ambiguity, role-specific challenge.
- Gaps and how to answer them honestly.
- Questions to ask interviewer.

#### Portfolio case study

For creative, technical, product, data, policy, or research work, include case study outline:

```markdown
Problem | Context | Role | Method | Tools | Output | Impact | Evidence links | Visuals to include
```

#### Reference list

Only include if requested. Ask permission before naming references. Do not invent references.

### Phase 8: ATS, recruiter, and truth critique

Run a critique before final output. Use five readers:

1. ATS robot: keyword and section scan.
2. Recruiter glance: 10-second relevance and readability.
3. HR screen: minimum qualifications and risk scan.
4. Hiring manager: role fit, domain credibility, evidence strength.
5. Technical or academic reviewer: truthfulness, depth, publications/projects, consistency.

Score across eight dimensions:

| Dimension | Weight |
|---|---:|
| ATS keyword match | 15% |
| Role relevance | 20% |
| Evidence density | 15% |
| Impact and metrics | 10% |
| Recruiter scanability | 10% |
| Domain credibility | 10% |
| Gap handling and honesty | 10% |
| Tone and polish | 10% |

Report:

```markdown
# ATS and Recruiter Scorecard
- Estimated readiness score: X/100
- Best strengths:
- Main risks:
- Missing keywords that can be added truthfully:
- Missing keywords that cannot be added:
- Overclaiming risks:
- Formatting risks:
- Top 5 fixes completed:
- Remaining TODOs:
```

Truthfulness table:

```markdown
| Claim | Where used | Evidence source | Status | Action |
|---|---|---|---|---|
```

### Phase 9: Revision loop

By default, revise once after critique. Do not create endless loops unless the user asks.

Revision priorities:

1. Remove unsupported claims.
2. Add high-value keywords where evidence supports them.
3. Move strongest evidence upward.
4. Shorten weak bullets.
5. Improve role framing.
6. Fix formatting and ATS issues.
7. Remove AI-sounding language.

Produce an editing report:

```markdown
# Editing Report
| Area | Before | After | Reason |
|---|---|---|---|
```

### Phase 10: File generation and PDF compilation

If the environment supports file creation, save outputs into `applications/{Company}_{Role}/`.

If LaTeX is requested:

1. Generate `.tex` files from ATS-safe templates.
2. Escape special characters.
3. Compile twice using `pdflatex` or `latexmk`.
4. If compilation fails, diagnose and fix common errors:
   - Unescaped `&`, `%`, `#`, `$`, `_`.
   - Unsupported Unicode.
   - Missing package.
   - Broken hyperlink.
   - Overfull boxes from long lines.
5. If PDF tools are unavailable, provide `.tex` and explain that local compilation is needed.

Do not fail the whole task only because PDF compilation is unavailable. Deliver Markdown and LaTeX sources.

## Style standards

Resume style:

- Direct and specific.
- No filler adjectives.
- Every bullet should answer: what did you do, with what method/tool, at what scale, and why did it matter?
- Use domain vocabulary from the job description naturally.
- Keep the strongest evidence above the fold.
- Use readable line lengths.

Cover letter style:

- Human, polished, specific.
- Do not sound like a mass template.
- Use one or two concrete achievements, not a list of everything.
- End with confidence, not desperation.

Avoid these weak phrases unless directly supported:

```text
responsible for, worked on, helped with, participated in, familiar with, passionate about, hardworking, detail-oriented, fast learner, team player, proven track record, dynamic, results-driven
```

Prefer:

```text
analyzed, built, designed, implemented, evaluated, automated, coordinated, trained, modeled, forecasted, reduced, increased, improved, produced, presented, published, deployed, documented, validated
```

## Output formatting rules

When responding in chat, keep the response useful and not too long. If files are created, give links to the files and summarize what changed. If writing directly in chat, use clean headings and markdown tables.

For a one-shot package, present:

1. A short note on assumptions.
2. The final resume or link.
3. The cover letter or link.
4. The scorecard summary.
5. Remaining TODOs.

## Minimal one-shot prompt pattern

```text
Use the one-shot-resume skill.

Target output: full application package with ATS resume, cover letter, recruiter email, LinkedIn update, interview prep, evidence matrix, ATS scorecard, and final checklist.

Rules:
- Do not invent metrics or experience.
- Use TODO placeholders for missing numbers.
- Keep resume ATS-friendly.
- Create LaTeX/PDF if possible.

Candidate evidence:
[paste resume/profile]

Job description:
[paste JD]
```

## If candidate evidence is weak

Do not fabricate. Produce:

- A conservative resume draft.
- A missing evidence checklist.
- Questions the candidate can answer to strengthen metrics.
- A “version after verification” plan.

## If the user wants speed

Return a compact package:

- Tailored resume.
- Cover letter.
- Application email.
- ATS scorecard.
- TODOs.

Skip LinkedIn, portfolio, and interview prep unless requested.
