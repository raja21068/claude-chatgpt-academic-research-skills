# Academic AI Structures — Section-Level Patterns to Avoid

These are structural patterns at the section or paragraph level.
They complement `academic_phrases.md` (sentence-level) and `structures.md` (generic sentence patterns).

---

## 1. Introduction section anti-patterns

### "Organized as follows" boilerplate
**Pattern:** Introduction ends with a paragraph describing what each section contains.
> "The rest of this paper is organized as follows. Section 2 reviews related work.
> Section 3 describes our method. Section 4 presents experiments. Section 5 concludes."

**Why it's wrong:** Readers can see the section headings. This paragraph adds no information.
**Fix:** End the introduction at the contribution bullets or at a motivating sentence about impact.
If a roadmap is venue-required, collapse it to one sentence: "Sections 2–5 cover related work,
method, experiments, and conclusion respectively."

### Contribution bullets that mirror the abstract
**Pattern:** Introduction ends with 3–4 bullets that are paraphrased copies of the abstract sentences.
**Fix:** Contributions should be *claims*, not summaries. Each bullet should be independently
verifiable. "We achieve 3.2 BLEU improvement on WMT-22 over the prior best system" is a claim.
"We present a novel approach that improves translation quality" is an abstract echo.

### Gap sentence that uses "however"
**Pattern:** Every AI introduction has the structure:
"X is important. Prior work has studied Y. **However**, Z remains unsolved. We address Z."
The "however" pivot is so formulaic it reads as a template.
**Fix:** Make the gap a *consequence* of the prior work's assumptions, not a simple negation.
Show why the gap exists structurally, not just that it exists.

---

## 2. Related work section anti-patterns

### Chronological ordering
**Pattern:** Related work organized by year, working forward from earliest to most recent.
> "Early work by [A] (2018) proposed X. Later, [B] (2020) extended this to Y.
> Most recently, [C] (2023) introduced Z."

**Why it's wrong:** Chronology is not a conceptual argument. It positions the paper as a
literature survey, not a contribution.
**Fix:** Organize by *theme* or *design choice*. Group papers by what they assume or optimize for,
then contrast each group with this work.

### Paragraph with no contrast sentence
**Pattern:** A related work paragraph that cites 3+ papers and contains none of:
"unlike", "in contrast", "however", "whereas", "differ from", "our work instead".
**Fix:** Every related work paragraph must end with or contain a bridge sentence that says
specifically how this work differs from the cluster just described.

### Summary-only related work
**Pattern:** "[Author] et al. propose X, which does Y using Z."
Nothing about why this matters to the positioning of the current paper.
**Fix:** After describing what the prior work does, add: "This approach requires [assumption];
our method removes this requirement by [mechanism]."

### Citation padding
**Pattern:** More than 5 citations in a single sentence, usually:
> "Many works have studied this problem [1, 2, 3, 4, 5, 6, 7]."
**Fix:** Name 2–3 representative papers specifically. State what distinguishes them.
Mass citations signal that the author hasn't engaged with the papers.

---

## 3. Method section anti-patterns

### Section-announcing opener
**Pattern:** Every subsection opens with a sentence announcing what the section will describe.
> "In this section, we present our encoder architecture."
> "We now describe the training procedure."
> "This section introduces the inference algorithm."
**Fix:** Start describing. The heading already announces the topic.

### Forward-reference chain
**Pattern:** Method section repeatedly defers: "details are provided in Section X",
"we discuss this in the Appendix", "as described later". More than 2 forward references
in a method section signals the method is not self-contained.

### Passive method steps
**Pattern:** Every step in the method uses passive voice:
> "The input is tokenized. Features are extracted. Embeddings are concatenated."
**Fix:** Use active voice with the system as subject or "we":
> "The encoder tokenizes the input. We extract features using [method]. The model concatenates..."

### Assumption burial
**Pattern:** Key assumptions appear in footnotes, appendix, or a single buried sentence
in the middle of a dense paragraph.
**Fix:** State each major assumption as its own sentence, early in the relevant subsection.

---

## 4. Results section anti-patterns

### Narrating the table
**Pattern:** Results section text simply restates what is visible in the table:
> "As shown in Table 1, our method achieves 84.3 on Dataset A, 79.1 on Dataset B,
> and 91.2 on Dataset C. The baseline achieves 81.2, 75.4, and 88.7 respectively."
**Fix:** State the *interpretation*, not the numbers. The reader can read the table.
> "Our method improves most on Dataset C (+2.5 points), where longer contexts are present,
> consistent with the design motivation in Section 3.2."

### Missing ablation explanation
**Pattern:** Ablation table present but results section only says "ablation results are in Table 3".
**Fix:** Each ablation row needs an interpretive sentence: what does the number tell you
about which component contributes what?

### Positive-only discussion
**Pattern:** Results section describes improvements only; never addresses where the method
performs worse than a baseline or why.
**Fix:** Name at least one setting where performance is lower and give a mechanistic reason.
This increases credibility and preempts reviewer questions.

---

## 5. Conclusion section anti-patterns

### Section summary conclusion
**Pattern:** Conclusion restates what each section contained:
> "In this paper, we proposed X (Section 3), evaluated it on Y (Section 4),
> and showed improvements over Z (Section 5)."
**Fix:** Lead with the single strongest finding. Then state its implications.
Then name one concrete open direction.

### "Future work" catch-all
**Pattern:** "Future work will explore [everything not done in this paper]."
A list of 4–6 future directions with no prioritization.
**Fix:** Name one specific open problem that this work surfaces. Be concrete:
"A natural extension is applying [method] to [setting X], which would require [Y]."

### Restated contribution bullets
**Pattern:** Conclusion bullet list that is a copy-paste of the introduction's contributions.
**Fix:** The conclusion should state what was *learned*, not what was *attempted*.

---

## 6. Abstract anti-patterns

### The four-sentence formula
**Pattern:** Abstract is exactly 4 sentences: (1) Problem. (2) Prior work gap. (3) We propose X.
(4) Experiments show improvement. Every AI abstract follows this. Reviewers recognise it.
**Fix:** Vary the structure. Lead with the finding. Start with the question.
Open with a concrete number. Break the formula.

### Absent numbers in the abstract
**Pattern:** "Our method achieves state-of-the-art results on multiple benchmarks."
**Fix:** Name the benchmark. State the number. State the comparison.
"X improves BLEU by 2.1 on WMT-22 over [prior best method Y]."

### Contribution overclaim in abstract
**Pattern:** Abstract claims broader scope than the experiments actually cover.
If experiments are on English-only data, the abstract should not claim "multilingual" results.
**Fix:** Scope the abstract to exactly what was tested.

---

## Quick section-structure checklist

Run after completing any full section:

- [ ] Introduction ends without "organized as follows"?
- [ ] Contribution bullets are verifiable claims, not abstract echoes?
- [ ] Related work organized thematically, not chronologically?
- [ ] Every related work paragraph contains a contrast sentence?
- [ ] No citation cluster of 5+ in a single sentence?
- [ ] Method subsections start with description, not announcement?
- [ ] Results section interprets, not just narrates, the tables?
- [ ] Ablation rows each have an interpretive sentence?
- [ ] At least one result reported where method underperforms, with reason?
- [ ] Conclusion leads with finding, not with section summary?
- [ ] Abstract contains at least one specific number?
- [ ] Abstract scope matches experiment coverage?
