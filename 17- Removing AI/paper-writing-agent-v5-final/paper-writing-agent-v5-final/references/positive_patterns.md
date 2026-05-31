# Positive Patterns — What Good Academic Prose Looks Like

This file is the complement to the ban lists. Use it when drafting and when rewriting.
The rewrite agent loads this alongside `phrases.md` and `structures.md`.

---

## Core principle

State the most specific, concrete, verifiable thing first.
Then expand. Never build up to the point — start at it.

---

## Sentence-level patterns that work

### Lead with the finding, not the method
**AI default:** "We apply cross-attention between encoder and decoder representations to
improve alignment, which results in a 2.1 BLEU improvement."
**Better:** "Cross-attention between encoder and decoder improves BLEU by 2.1 points,
primarily by resolving long-range alignment failures (Table 3)."

**Rule:** Number or finding first. Method is the explanation, not the headline.

---

### State the number before the interpretation
**AI default:** "The model generalises well to longer sequences, as shown by the
performance on the long-context benchmark."
**Better:** "Performance drops only 1.3 points on sequences longer than 512 tokens,
compared to a 7.8-point drop for the baseline (Table 4)."

**Rule:** If there is a number, open with it.

---

### Name the mechanism, not the property
**AI default:** "Our model achieves strong performance because it captures long-range dependencies."
**Better:** "The sliding-window attention in layer 6 attends across 2048 tokens;
removing it drops accuracy by 4.1 points on the long-document split (Table 5)."

**Rule:** Properties are adjectives. Mechanisms are verbs and nouns with referents.

---

### One sentence per idea
**AI default:** "Our method, which builds on the transformer architecture and incorporates
a novel cross-modal attention mechanism that jointly processes text and image features,
achieves state-of-the-art results on three benchmarks while maintaining inference efficiency."
**Better:** "The cross-modal attention layer jointly processes text and image features.
This design yields state-of-the-art results on three benchmarks with no inference overhead."

**Rule:** If a sentence has two verbs of approximately equal weight, split it.

---

### Vary the subject of consecutive sentences
**AI default:**
> "We propose a new encoder. We evaluate on three datasets. We compare against four baselines.
> We show improvements on all benchmarks."
**Better:**
> "The encoder processes inputs in two passes. Evaluation covers three datasets spanning
> two domains. Against four baselines, the method improves by 2–4 points depending on input length."

**Rule:** If three consecutive sentences share the same subject, change one.

---

### Specific scope over vague hedge
**AI default:** "The method may not generalise to all domains."
**Better:** "The method was tested on newswire and biomedical text only;
behaviour on social media or legal text is untested."

**Rule:** Replace the hedge word with the specific boundary.

---

## Paragraph-level patterns that work

### Open with a claim, close with evidence or consequence
Structure: [What is true] → [Why / how we know] → [What follows from this].
Not: [Context] → [What we did] → [What happened] → [What this means].

**Example:**
> "Long-range dependencies drive most of the accuracy gap between this model and prior work.
> Without the sliding-window layer, performance on documents over 1000 tokens falls by 6.2 points
> while short-document accuracy is unaffected (Table 5). Capturing these dependencies
> requires attending across the full sequence — a constraint the fixed-window baseline cannot satisfy."

---

### End on a consequence, not a restatement
**AI default ending:** "These results demonstrate the effectiveness of our approach."
**Better endings:**
- A specific number that was not in the opening sentence
- A forward-looking consequence: "This suggests the bottleneck is X, not Y."
- A contrast: "The pattern reverses for out-of-domain inputs (Appendix B)."
- An open question that follows from the finding

**Rule:** If your paragraph ending could be moved to any other paragraph without changing the meaning,
it is too generic.

---

### The three-sentence paragraph (for dense technical sections)
For results and ablation sections, three sentences is often exactly right:
1. The claim (with the number)
2. The supporting observation (what the table/figure shows specifically)
3. The mechanistic interpretation or consequence

Anything longer usually means you are narrating rather than interpreting.

---

## Section-level patterns that work

### Introduction: problem → consequence → gap → contribution
Not: problem → prior work → however → we propose.
Better: Name the problem. State what goes wrong when it is unsolved (specific, concrete).
Name what prior work assumed that prevented solving it. State what you did differently.
Contribution bullets state verifiable claims.

### Related work: clusters with bridges
Group papers by the design choice or assumption they share.
End each cluster with a bridge: "Our method removes [assumption X] by [mechanism Y]."
Two to four clusters. Each cluster 2–4 sentences. No single-paper paragraphs.

### Method: setup → components → interactions → training
State the problem setup and notation in one short paragraph.
Describe each component in order of data flow.
Describe how components interact (this is usually missing in AI drafts).
State the training objective and any key implementation choices.

### Results: question → finding → interpretation → implication
Open each results subsection with the research question it addresses.
State the finding with the number.
Interpret it: why does this happen?
State the implication: what does this mean for the design or the field?

---

## Rewrite heuristics (for the rewrite agent)

When producing alternatives, prefer:

1. **Shorter over longer** — if both say the same thing, the shorter one is better
2. **Concrete over abstract** — "the encoder" over "the model", "WMT-22" over "a benchmark"
3. **Active over passive** — find the actor
4. **Number first** — if a number appears mid-sentence, move it to the front
5. **Claim over description** — "X outperforms Y by 2.1 points" over "X and Y perform differently"
6. **Vary from adjacent sentences** — check the sentence before and after; make sure subject and length differ
7. **Match author's average sentence length** — from `my_writing_style.md`

---

## Checklist: is this sentence good?

- Does it state the most specific thing first?
- Is the subject a human, a system, or a named entity (not "it", "this", "the approach")?
- Is there a verb doing real work (not "is", "has", "involves")?
- Is there a number, a name, or a mechanism — or should there be?
- Is it shorter than it could be without losing meaning?
- Does it differ in length and structure from the sentence before it?

If all six: keep it. If two or fewer: rewrite.
