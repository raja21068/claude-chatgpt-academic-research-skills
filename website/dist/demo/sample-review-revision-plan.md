# Sample revision plan: "Reminder messages and quiz scores" (practice manuscript)

> **Sample answer, made up to show the format.** It uses the site's fictional practice manuscript. Scores are illustrative.

Yes, the paper can be made stronger. The main point: **do not answer the review by adding bigger claims.** Narrow the causal claim, fix the analysis, then add the evidence that supports the narrower claim.

If done carefully, I would expect the manuscript to move from roughly **5.5/10 to about 7.5/10**, though no journal outcome can be guaranteed.

## Priority revision map

| Current weakness | Concrete solution | Importance | Likely effect |
|---|---|---|---|
| Students chose whether to get reminders (self-selection) | Drop the causal claim, or randomise reminders in a new term | **Critical** | Very high |
| Prior ability not controlled | Adjust for the pre-course score | **Critical** | High |
| Many outcomes tested, one reported as significant | Correct for multiple comparisons; name the primary outcome | **Critical** | High |
| One course, one term | Add a second course or term, or narrow the scope | High | Medium-high |
| No effect size reported | Report the difference with a confidence interval | Medium | Medium |

The first three are **corrections**, not optional extensions.

---

# 1. Fix the most dangerous issue: self-selection

Students who opted in to reminders are probably more motivated. So the score difference may come from motivation, not reminders.

**Example of failure:** if motivated students score 8 points higher anyway, and only they opt in, the study shows an 8-point "effect" even if reminders do nothing.

### Best solution

Randomise who receives reminders in the next term. Then the comparison is fair by design.

### If you cannot run a new study

Keep the data, but change the claim.

Do not say:

> Reminders improve quiz scores.

Say:

> Students who chose to receive reminders scored higher; because students self-selected, this association may reflect motivation rather than an effect of reminders.

---

# 2. Adjust for prior ability

Add the pre-course score \(x_i\) to the analysis:

\[
y_i = \beta_0 + \beta_1\,\text{reminder}_i + \beta_2\,x_i + \varepsilon_i
\]

Report \(\beta_1\) with a 95% confidence interval. If it shrinks a lot after adjustment, say so — that is an honest and useful finding.

---

# 3. Correct for multiple comparisons

The paper tests 6 quiz outcomes and highlights the one with \(p<0.05\). Name **one primary outcome** (e.g. final quiz score) in advance, and treat the others as secondary with a correction:

\[
\alpha_{\text{each}} = \frac{0.05}{6} \approx 0.0083
\]

---

# 4. Widen or narrow the scope

Either add one more course or term, or state clearly in the title and abstract that the study covers one course in one term.

---

# 5. Change the paper's central claim

Do not lead with "reminders improve learning."

Lead with:

> In one course, students who opted in to reminders scored higher on the final quiz; after adjusting for prior ability the difference was smaller, and the design cannot separate reminder effects from motivation.

That is narrower, but a reviewer cannot reject it as overclaiming.

---

# 6. How the scores could change

| Dimension | Current | After strong revision |
|---|---|---|
| Causal validity | 3.5 | **7.0** (with randomisation) |
| Statistical soundness | 4.5 | **8.0** |
| Claim-to-evidence match | 4.0 | **8.5** |
| Generalisability | 4.0 | **6.5** |
| Clarity | 7.0 | **8.0** |
| Overall | ~5.5 | **~7.5** |

You do **not** need a new idea. What is missing is a tighter chain:

\[
\boxed{\text{fair comparison}\rightarrow\text{adjusted estimate}\rightarrow\text{corrected test}\rightarrow\text{claim that matches the design}}
\]
