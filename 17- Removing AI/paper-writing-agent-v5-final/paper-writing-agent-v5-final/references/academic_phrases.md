# Academic AI Phrases — Banned List

These are patterns that appear constantly in AI-generated academic writing.
They do not appear in the generic stop-slop lists because that skill was designed
for blog/essay prose. Add this file alongside `phrases.md` and `structures.md`.

---

## 1. Paper-announcement openers

AI introduces the paper from inside the paper. Cut these entirely.
State the contribution directly.

| Banned | Replace with |
|--------|-------------|
| "In this paper, we propose…" | Name the method and what it does |
| "In this work, we present…" | Start with the problem or the result |
| "In this paper, we introduce…" | Start with what the method achieves |
| "We propose a novel…" | State the approach + its differentiating property |
| "This paper presents…" | State the finding or contribution directly |
| "This work investigates…" | State what was found, not that investigation happened |
| "The rest of this paper is organized as follows…" | Delete. Use section headings. |
| "The remainder of this paper…" | Delete. |

---

## 2. False humility / epistemic theatre

These phrases perform uncertainty without adding precision.
Replace with specific scope statements.

| Banned | Replace with |
|--------|-------------|
| "To the best of our knowledge…" | State the specific gap: "No prior work addresses X in setting Y" |
| "As far as we are aware…" | Same — name the specific gap |
| "We believe that…" | State the claim directly, or cite the evidence |
| "We argue that…" (without proof) | Only use if an argument follows; else state the claim |
| "It is hoped that…" | Delete or reframe as specific future direction |
| "We hope to demonstrate…" | State what you demonstrate |

---

## 3. Filler observation phrases

These announce that something exists in the results rather than stating it.

| Banned | Replace with |
|--------|-------------|
| "It is worth noting that…" | State the observation directly |
| "We note that…" | Delete; state the observation |
| "It is important to note that…" | Delete; state why it matters, not that it matters |
| "Notably,…" | Delete; state the notable thing |
| "Interestingly,…" | Delete; state what is interesting and why |
| "Importantly,…" | Delete; state why it matters specifically |
| "It can be observed that…" | State the observation |
| "As can be seen from Table/Figure X…" | "Table X shows…" or state the finding directly |
| "We can see that…" | State the finding |
| "One can observe that…" | State the finding |
| "From the results, it is clear that…" | State the result |
| "The results clearly show…" | State the result + the number |

---

## 4. Contribution inflation

Vague superlatives that overstate the work.
Use only when backed by a specific comparative number.

| Banned unless number-backed | Replace with |
|-----------------------------|-------------|
| "significant improvement" | "X-point improvement on benchmark Y" |
| "substantial gains" | Name the gain and the baseline |
| "considerable improvement" | Same |
| "dramatically outperforms" | State the margin |
| "extensive experiments" | State how many, on which benchmarks |
| "comprehensive evaluation" | State the specific coverage |
| "state-of-the-art results" | State the metric, dataset, and comparison |
| "promising results" | State the result |
| "strong performance" | State the number |
| "competitive results" | State the gap |
| "superior performance" | State the margin and the baseline |

---

## 5. Hedge stacking (density problem, not single-word problem)

No single word here is banned alone. The ban is on **3 or more in one sentence**.
Run `scripts/rhythm_check.py` — it flags sentences with hedge density ≥ 3.

Hedge words to count: `may`, `might`, `could`, `potentially`, `possibly`,
`appears to`, `seems to`, `arguably`, `presumably`, `likely`, `suggest`,
`indicate`, `imply`, `perhaps`, `somewhat`, `relatively`, `generally`,
`typically`, `usually`, `often`, `tend to`.

**Safe use:** 1 hedge per sentence is fine when evidence is genuinely uncertain.
2 hedges is borderline. 3+ is AI stacking.

**Example:**
> "Results may potentially suggest the model could possibly generalize."
→ "The model generalises to X setting (Table 3); behaviour on out-of-distribution Y remains untested."

---

## 6. Uniform contribution bullets

AI writes contribution lists where every bullet:
- starts with "We"
- runs 10–14 words
- uses a gerund ("proposing", "introducing", "demonstrating")
- ends with a noun phrase

**Check:** if all contribution bullets have the same grammatical shape, vary them.
Mix direct statements, quantified claims, and method descriptions.

**Banned shape (all three together):**
> "We propose X. We introduce Y. We demonstrate Z."

**Better:** vary subject, length, and structure:
> "X achieves Y on benchmark Z. The key insight is [mechanism]. We release code and models."

---

## 7. Method-section throat-clearing

| Banned | Replace with |
|--------|-------------|
| "In this section, we describe…" | Start describing. |
| "We now present our method." | Start presenting. |
| "The proposed method consists of…" | Name the method; state its components. |
| "Our approach is as follows:" | State the approach. |
| "We formulate the problem as follows:" | State the formulation. |

---

## 8. Related-work AI padding

| Banned | Replace with |
|--------|-------------|
| "[Author] et al. propose X." (alone, no contrast) | State what X does and how it differs from this work |
| "Many works have studied…" | Name the specific cluster; cite 2-3 representative papers |
| "Numerous studies have shown…" | State the finding; cite the source |
| "A line of work…" (without naming it) | Name the methods or the defining paper |
| "Recent advances in X have enabled Y." (alone) | State specifically which advance, which paper |

---

## 9. Conclusion theatre

| Banned | Replace with |
|--------|-------------|
| "In this paper, we have shown…" | State the strongest single finding. |
| "In conclusion, we have presented…" | State the contribution and the strongest number. |
| "We have demonstrated that…" | State what was demonstrated and at what scale. |
| "Future work will explore…" (vague) | Name a specific open problem or concrete next step. |
| "We leave X for future work." (as the last sentence) | End on the contribution, not the gap. |

---

## Quick academic slop checklist

Run after every section, in addition to the generic `stop_slop.md` checklist:

- [ ] Any "In this paper/work, we…" opener? Cut it.
- [ ] "To the best of our knowledge"? Replace with the specific gap statement.
- [ ] Any observation phrase ("it is worth noting", "as can be seen")? State the observation.
- [ ] Any unquantified superlative ("significant", "extensive", "state-of-the-art")? Add the number or remove.
- [ ] Contribution bullets all the same grammatical shape? Break the uniformity.
- [ ] Hedge density ≥ 3 in any single sentence? (run `rhythm_check.py` or count manually)
- [ ] Related work paragraphs that summarise without contrasting? Add the bridge sentence.
- [ ] Conclusion opens with "In this paper, we have shown"? Rewrite with the finding first.
