# Paper Writing Checklists

Read this file when performing quality checks, reviewer simulation, or final audit.

## Quality and Safety Rules

### Never fabricate
- Citations, authors, publication venues, DOI links
- Experiments, numbers, datasets, baselines
- Deadlines, page limits, reviewer comments

### Use precise uncertainty
Prefer: "The uploaded results suggest...", "This claim needs verification...", "TODO: add citation for..."
Avoid: "This proves..." (unless proof supplied), "State-of-the-art" (unless verified), "Significantly better" (unless statistical support provided)

### Protect anonymity (double-blind venues)
Check for: author names, institution names, lab names, acknowledgments, self-identifying repository links, file names or figure metadata that identify authors.

### Preserve scientific integrity
- State scope constraints and assumptions honestly — use "the method assumes X," "the approach is most effective when Y," "an open direction is Z" rather than the word "limitations"
- Report negative or inconclusive results when relevant
- Do not cherry-pick results without noting scope
- Do not hide missing baselines
- Do not overstate causal conclusions from correlational evidence

### No "limitation" / "limitations" in body text or headings
Never write "limitation" or "limitations" in paper body text, section headings, or figure captions. Reframe instead:
- "A limitation is that the method requires X" → "The method assumes X"
- "A key limitation is performance on Y" → "The approach is most effective when Y is satisfied"
- "Limitations include Z" → "An open direction is Z" or "Future work could extend to Z"
The word may appear inside `\cite{...}` keys and in direct quotations of prior work — those are acceptable.

---

## Final Submission Checklist

### Content
- [ ] Main problem is clear
- [ ] Contribution is specific
- [ ] Claims match evidence
- [ ] Experiments answer the stated research questions
- [ ] Scope constraints and assumptions are stated honestly (not labelled "limitations")
- [ ] Conclusion does not introduce new claims
- [ ] No "limitation"/"limitations" appears in body text, headings, or captions

### Integrity
- [ ] `/paper-claim-audit` run or manual numeric cross-check completed — verdict is PASS, WARN (fixed), or NOT_APPLICABLE
- [ ] `/experiment-audit` run or inline integrity check completed (if experiments were run by an agent)
- [ ] All numbers in the paper verified against source material or raw result files

### Citations
- [ ] Every factual literature claim has a verified citation
- [ ] Bibliography entries are complete
- [ ] Citation style matches venue
- [ ] No placeholder citation remains unless intentionally marked TODO
- [ ] No BibTeX generated from memory — all entries verified via DBLP/CrossRef/DOI

### Formatting
- [ ] Page limit checked
- [ ] Template followed
- [ ] Figures and tables fit
- [ ] Captions are clear and do not start with "Figure X:"
- [ ] Cross-references are consistent

### Review readiness
- [ ] Related work addresses obvious comparisons
- [ ] Method is reproducible enough for the venue
- [ ] Baselines are justified
- [ ] Metrics are defined
- [ ] Reviewer objections have been anticipated

### Anonymity (if required)
- [ ] Author identities removed
- [ ] Self-citations anonymized according to venue rules
- [ ] Acknowledgments removed
- [ ] Links and artifacts checked

### Additional final checks
- [ ] Reviewer simulation completed and major issues addressed
- [ ] Venue compliance table completed
- [ ] Literature matrix completed or citation gaps marked TODO
- [ ] Claim-evidence map completed for abstract, introduction, results, and conclusion
- [ ] Contribution statement is precise and does not overclaim
- [ ] Language polish did not change scientific meaning
- [ ] Rebuttal/advisor comment log updated if comments exist
- [ ] Final submission audit says ready or lists remaining blockers

---

## Section-by-Section Prompt Cheatsheet

### Start a paper project
"Build a prompt contract for this project. Summarize my topic, contribution, evidence, missing materials, and best next step. Do not invent citations or results."

### Turn notes into a plan
"Using only my uploaded notes, create: contribution statement, claim-evidence map, section-by-section outline, and TODO list."

### Draft a section
"Draft the [section name] in [Markdown/LaTeX]. Use only evidence I provided. Mark unsupported claims as TODO. Keep tone formal, precise, non-exaggerated."

### Sharpen contribution
"What is new, why it matters, what evidence supports it, what prior work it differs from, and what claim would be too strong."

### Literature review
"Organize references into a literature matrix. Group by theme, identify the gap, write a related-work outline. Do not add papers I did not provide."

### Claim-evidence check
"Check every strong claim. Label each as supported, weakly supported, unsupported, or contradicted. Suggest safer rewrites."

### Reviewer simulation
"Review as three strict reviewers and an area chair using six-axis scoring. Focus on novelty, evidence, clarity, methodology, results, scope assumptions, and venue fit. Give a prioritized revision plan with CRITICAL/MAJOR/MINOR severity labels."

### Final submission audit
"Audit: venue rules, anonymity, citations, placeholders, figures, tables, scope assumptions, ethics/reproducibility, claim-number audit, and consistency across abstract, intro, results, conclusion."

### Source isolation
"Use only uploaded materials. Do not rely on memory for citations, authors, results, datasets, or venue rules. Mark missing info as TODO."

### P0/P1 citation triage
"Categorize references into P0 must-cite and P1 useful background. Explain the role of each and where it belongs."

### Integrity audit
"Run the claim auditor on the current draft. Verify every reported number against the source material. Flag any value that differs from the raw data."
