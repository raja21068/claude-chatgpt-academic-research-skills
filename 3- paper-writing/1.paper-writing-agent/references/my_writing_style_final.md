---
name: my_writing_style
description: >
  Apply this skill whenever the user asks Claude to write, draft, extend, rewrite, or
  improve any academic or research text — including full paper sections (abstract,
  introduction, related work, methodology, results, discussion, conclusion), research
  proposals, cover letters, or rebuttals. Trigger when the user says "write like my
  papers," "use my writing style," "match my style," "write in my voice," "write a
  section for my paper," or uploads a draft and asks for improvements. Also trigger for
  short tasks such as "give me an intro paragraph," "rephrase this abstract," or "help
  me write the contribution list." This skill captures the author's real corpus-verified
  voice — always apply it instead of producing generic academic writing.
---

# My Writing Style — Master Corpus Skill

Verified against 11 actual published PDFs (744,000+ characters of real paper text)
plus extracted metadata from 27 papers. Every count and rule is from the real corpus.

---

## 1. Core Voice Identity

- First-person plural: we propose, we introduce, we present, we develop, we utilize,
  we conducted, we evaluate, we compare, we recommend, we hypothesize.
- Problem-first framing: domain importance → specific limitation → proposed solution.
- Hybrid-framework identity: combines two or more techniques; justifies why each alone
  is insufficient.
- Experimentally grounded: every claim tied to named metrics and named baselines.
- Assertive tone with selective hedging where genuinely needed.
- Sentence length: 17–18 words average in body text. Abstract sentences: 20–25 words
  (denser). No one-sentence paragraphs in body sections.

---

## 2. Transition Words — Verified from 11 PDFs

Proportions confirmed. Use in this order of frequency:

| Transition     | PDF count | Primary use                              |
|----------------|-----------|------------------------------------------|
| however        | 118       | Gap introduction, contrast               |
| while          | 93        | Within-sentence contrast: "A does X, while B ensures Y" |
| therefore      | 84        | Causal conclusion in results/discussion  |
| moreover       | 50        | Adding a reinforcing point               |
| additionally   | 35        | Supplementary point (equal to moreover)  |
| whereas        | 33        | Formal contrast between two approaches  |
| furthermore    | 39        | Reinforcing in methodology/discussion    |
| specifically   | 21        | Narrowing to a detail                    |
| overall        | 20        | Summary opener in discussion/conclusion  |
| in addition    | 15        | Adding a separate point                  |
| instead        | 14        | Replacing one approach with another      |
| in contrast    | 13        | Comparing two different approaches       |
| thus           | 29        | Short causal link mid-sentence           |
| consequently   | 6         | Result-of-action in discussion           |
| hence          | 7         | Formal proofs and security analysis      |
| nevertheless   | 2         | Strong contrast (rare)                   |

"While" is one of the highest-frequency connectors — use it actively:
"[Component A] improves [X], while [component B] ensures [Y]."

---

## 3. Real Phrases From the Papers (Verbatim)

### Opening sentences
- "Vehicle re-identification (re-id) received immense attention..."
- "Nowadays, smart devices have become part of the Internet of Things (IoT), and are widely used in..."
- "The present outbreak of COVID-19 is a worldwide calamity."
- "Stock market forecasting has drawn interest [from researchers and practitioners]."
- "NER is a fundamental task [in natural language processing]."
- "The early detection of dangerous situations and forecasting techniques is important."
- "[Domain] has gained significant attention in recent years."
- "Artificial intelligence (AI) and blockchain (BC) based technologies [are areas of study]."

Pattern: "[Domain/technology] [received/has gained/is widely used] [in context]."

### Gap-building sentences
- "However, existing methods suffer from [limitation]."
- "However, these studies [gap]."
- "However, most of them are not sufficient to [task]."
- "Nevertheless, [prior approach] fails to address [specific issue]."
- "Although [X] has been studied, [Y] remains an open challenge."
- "Still, [topic] has not been studied well." ← adapt the topic
- "Traditional target detection algorithms have difficulty [doing X]." ← adapt method type
- "Traditional path-planners generate the shortest possible routes [but ignore safety]."
- "To the best of our knowledge, [novelty claim]."
- "To the best of authors' knowledge, [novelty claim]."
- "More importantly, to the best of our knowledge, [strongest novelty claim]."
- "There is still ample room to improve [aspect] under [condition]."
- "[X] remains an open challenge."
- "Most existing approaches focus on [A], while overlooking [B]."
- "Additionally, deep learning approaches need [information] to improve [performance]."

### Proposing the method
- "To tackle the mentioned challenges, we propose..."
- "To tackle the aforementioned issues, we propose..."
- "To address the above mentioned issues, researchers have proposed..."
- "To solve the mentioned challenges, [framework] is proposed."
- "To address the aforementioned problems, we propose..."
- "To overcome this weakness, [approach] is introduced."
- "To handle this issue, we have designed an improved [model]."
- "To deal with this issue, we propose [model]."
- "In this paper, we propose a [novel/methodology/model] for [task]."
- "In this paper, we utilize blockchain and [technology] to [purpose]."
- "This paper presents a novel framework for [task]."
- "This paper presents a novel technique for [task]."
- "This paper presents a comprehensive study of [topic]."
- "This paper introduces a framework [for/to] [purpose]."
- "This article presents [design/method]."
- "This work presents a novel [X] for [Y]."
- "We propose a novel end-to-end, two-stream-based deep learning framework."

### Describing the system
- "The proposed framework consists of [A], [B], and [C]."
- "The proposed framework collects a [small/large] amount of data from [sources]."
- "The proposed scheme creates trust [in/for/between] [entities]."
- "The proposed [model] has the ability to [do X]."
- "Smart contract provides the authentication mechanism."
- "Blockchain guarantees the trust, confidentiality, and integrity."
- "RFID and blockchain are considered as dynamic duals."
- "The inbuilt power of federated architecture [enables/ensures X]."
- "Without relying on a central server."
- "Collaboratively train a global model."
- "Raw data never leave the local node; only [parameters/gradients] are transmitted."
- "[Component] is well-suited for real-time [application]."
- "We hypothesize that robust information can be extracted through [mechanism]."
- "Each [hospital/organization] contributes a part of significant [information/data]."

### Contribution list opener — use one of these exactly
- "The main contributions of this paper are summarized as follows:"
- "The main contributions of this paper are as follows:"
- "The contribution of our work is four-fold:"

### Results sentences
- "Extensive experimental results demonstrate that the proposed method [achieves/outperforms]."
- "Extensive experiments demonstrate [X]."
- "Extensive empirical evaluation demonstrates [X]."
- "Experimental outcomes demonstrate [X]."
- "Experimental results show [X]."
- "Experimental results validate their effectiveness."
- "Simulation results show [X]."
- "An extensive empirical study has been conducted to verify [X]."
- "Fig. n shows [description]."
- "Table n shows [description]."
- "The proposed method outperforms state-of-the-art methods."
- "The proposed scheme significantly improves performance."
- "Compared to [baseline], the proposed [model] achieves..."
- "Ablation experiments reveal [X]."
- "We attain new state-of-the-art results."
- "We recommend it for the identification of [task/disease]."
- "The best results for the three datasets were obtained [by/with] [method]."

### Closing / forward-looking
- "[This work] will frame the next level research."
- "We aim to facilitate future research [in domain]."
- "Future work might include [specific direction]."
- "In future work, we aim to [specific action]."
- "There are massive opportunities for improvement and research."
- "Our study is devoted to updating state-of-the-art [in domain]."
- "[Framework] lays a robust foundation [for future direction]."
- "Despite the federated cost, [advantage]."
- "[Limitation] remains an open challenge."

---

## 4. Paper-Level Structure

```
Abstract     →  Problem + method + result + practical contribution (≤250 words)
Introduction →  Context → challenge → grouped literature + gap → proposal → contributions → organization
Related Work →  Grouped by method family — never author-by-author
Methodology  →  System model → components sequential → algorithm/equations → evaluation setup
Results      →  Tables/figures → named metric comparison vs named baselines → analysis
Discussion   →  Why each component improves results → practical implications
Conclusion   →  Summary → key findings → limitations → specific future work
```

---

## 5. Section-by-Section Rules

### Abstract
- 4–6 sentences covering: problem, proposed method + components, evaluation setting,
  main metric result (with number), practical significance.
- No citations. No limitations. ≤250 words.
- Contribution list in abstract uses (i)(ii)(iii)(iv) roman numeral format inline.
- Example structure from Paper 1:
  "[Problem statement]. [Gap and concern]. [Proposed solution]. The contribution of
  our work is four-fold: (i) [contribution]. (ii) [contribution]. (iii) [contribution].
  (iv) [contribution]. [Validation sentence]. [Result sentence]."

### Introduction
¶1 — Domain importance (3–4 sentences): why the field matters, what technology enables it.
¶2 — Specific technical challenge (3–5 sentences): one concrete barrier.
¶3 — Literature grouping + gap (4–6 sentences): method families, then "However, [gap]."
¶4 — Proposed solution + contributions (3–4 sentences + numbered list):
     "To tackle the aforementioned challenges, we propose..."
     "The main contributions of this paper are summarized as follows:"
¶5 — Paper organization (1 sentence):
     "The rest of the paper is organized as follows: In Section 2, we discuss [topic].
     Section 3 presents [topic]. Section 4 describes [topic]. Finally, Section 5 concludes."

Typical introduction: 4–5 paragraphs, each 4–8 sentences.

### Related Work
- Group by method family — never author-by-author.
- End each group with what the family fails to solve.
- Reference introduction: "Kumar et al. [n] proposed..." or "In [n], [author] designed..."

### Methodology
- Present tense throughout: "the framework consists of," "we compute," "the model takes."
- Component by component, sequential.
- Name the framework with an acronym (OSGM, EINDM, Fed-CARS, MCNN, SPP, CLSS-CPPA).
- Include equations when defining hashing, aggregation, similarity, routing, loss functions.

### Results
- Past tense: "achieved," "improved," "outperformed," "produced," "conducted."
- Always compare to named baselines.
- "compared to" (17 uses) is standard — NOT "compared with" (only 1 use in corpus).
- Introduce results with "Fig. n shows..." or "Table n shows..." or "shown in Fig. n."

### Discussion
- Pattern: "[Component A] [improves/ensures X], while [Component B] [ensures Y]."
- Present tense for interpretation.
- Real examples:
  "Blockchain permits secure collaboration among hospitals, while deep learning improves detection."
  "Federated learning protects hospital data, while blockchain authenticates model updates."
  "Data augmentation reduces background and pose bias, while spatio-temporal cues reduce
   the negative effects of visual variations."

### Conclusion
- ¶1: Restate problem + proposed framework (present tense).
- ¶2: Key findings with metric value (past tense).
- ¶3: Limitations — brief, specific, one sentence.
- ¶4: Future work — always specific to a setting, dataset, or method:
  "Extend to non-IID federated settings under edge constraints."
  Never: "We will improve the model in future work."

---

## 6. Contribution List Format

Every paper has contributions listed using one of these formats:
- Roman numeral inline: (i) ... (ii) ... (iii) ... (iv) ...
- Bullet points: • First contribution. • Second contribution.
- Numbered: (1) ... (2) ... (3) ...

Most common in this corpus: **roman numeral (i)(ii)(iii)** and **bullet •**
Each contribution point: one sentence starting with "We propose," "The proposed [name],"
"A novel [framework]," or "An extensive empirical study."

Every paper has exactly one theoretical contribution and one practical contribution.

---

## 7. Equations, Methods, and Algorithms

### Introducing an equation
Pattern: motivating sentence → equation → "where" clause.
Never drop an equation without context.

Intro phrases from actual papers:
- "...can be expressed as:"
- "...is defined as follows:"
- "...is given as:"
- "...is formulated as:"
- "...is computed as:"
- "...performs as follows:"
- "...can be verified as follows:"

After equation: always explain it.
- "It can be seen in Equation (n), the learning rate is η..."
- "Equation (n) contains three prominent parts."

### Equation numbering and reference
- Numbered (1), (2), (3) at right margin.
- Referenced in text: "Equation (n)" (17 uses) > "Eq. (n)" (10 uses).
- Never: "equation n" without parentheses, "formula n."

### Domain-specific equations
**Blockchain/security:** H(·) for hash; σ = Sign(sk, m); T = {ID, timestamp, hash, data};
"The scheme is proved secure under the ECDLP hardness assumption in the random oracle model."

**Federated learning:** wᵢ = local parameters; w_global = Σᵢ(|Dᵢ|/|D|)·wᵢ aggregation;
"Raw data never leave the local node."

**Re-ID/similarity:** S(q,g) = α·V(q,g) + (1−α)·ST(q,g)

**Path planning:** J = w₁·length + w₂·risk + w₃·smoothness

**NLP:** hₜ = [hᶜₜ; hʷₜ]; P(y|x) = (1/Z(x))·exp(...)

**Clustering:** ws(w) = log(N/df(w))

### Algorithm description
Formal block:
```
Algorithm n: [Name]
Input:  [with types]
Output: [with types]
1.  [Action] [object]
2.  [Action] [object]
...
Return [output]
```
Sequential prose: "First, [step]. Then, [step]. Subsequently, [step]. Finally, [result]."

### Component introduction (3-part pattern)
1. "The [component] is designed to [function]."
2. "Specifically, [component] takes [input] and produces [output]."
3. "This design ensures [technical benefit]."

---

## 8. Domain-Specific Metrics

| Domain | Metrics |
|---|---|
| Medical imaging | accuracy, sensitivity, specificity, F1-score, AUC, PSNR, MSE, MCC |
| Vehicle Re-ID | mAP, CMC, HIT@1, HIT@5, Rank-k |
| Recommender systems | MAE, RMSE, nDCG, HIT@K |
| VANET / Security | computational cost, communication cost, latency, verification time |
| Remote sensing | AP, mAP, FPS |
| Clustering / NLP | NMI, purity, homogeneity, V-measure, F1, precision, recall |
| Path planning | path length, computation time, collision rate, DCPA |
| Blockchain / RFID | read range, throughput, tamper detection rate |
| Stock / time-series | RMSE, MSE, MAE, R-squared, Kendall correlation |
| Complex networks | SIR score, Kendall correlation, O(nk²+\|E\|) complexity |
| Autonomous / HRI | balanced accuracy, precision, recall, F-measure, latency |

---

## 9. Signature Phrases

"RFID and blockchain are considered as dynamic duals."
"Without relying on a central server."
"Collaboratively train a global model."
"[This work] lays a robust foundation for [direction]."
"[This work] will frame the next level research."
"Our study is devoted to updating state-of-the-art [in domain]."
"There are massive opportunities for improvement and research."
"The inbuilt power of [federated architecture / blockchain] [enables X]."
"The proposed [model] has the ability to tackle [challenge]."
"[X] remains an open challenge."
"[A] does X, while [B] ensures Y." — core discussion pattern.

---

## 10. Verified Style Rules (All From PDF Text)

### Punctuation

**Em dash `—`:** Appears 17 times in PDFs but ONLY in author contribution statements
("Writing — review and editing") and conference title strings. Never in body text paragraphs.
Do not use em dash in paper body text.

**En dash `–`:** 623 uses — in number ranges ("100–300 ms", "866–868 MHz") and author
contribution statements. In body text: only for ranges.

**Semicolons `;`:** 505 uses total. The vast majority are in citation lists:
"(Zhang et al., 2018; Seo and Shin, 2019)." In body sentences (not citations),
use only for: (1) before "however" — "[X]; however, [Y]." (2) separating parallel
metric results. (3) tightly linked independent clauses. Never to list items in prose.

**Oxford comma:** 56 uses with, 51 without — nearly equal. Use it when it aids clarity,
but it is not a strict rule in this corpus.

**Colons `:`:** Before contribution lists, algorithm blocks, and metric result lists.
Not used mid-sentence.

**Parentheses `( )`:** Heavily used (2,386 total) — primarily for acronym definitions
(CT), (RCNN), (IoT), and citation years (2021). Also for mathematical expressions.

### Hyphenation (verified from 11 PDFs)

Always hyphenated:
blockchain-based, privacy-preserving, spatio-temporal, state-of-the-art, self-attention,
context-aware, real-time, real-world, cross-dataset, multi-level, large-scale,
co-occurrence, rule-based, end-to-end, high-dimensional, semi-supervised (38 uses),
multi-label (22 uses), fine-grained, pre-trained (15 uses), attention-based,
few-shot, path-planning, long-term, short-term.

Never hyphenated (standalone nouns or noun phrases):
deep learning (93 unhyphenated vs 1 hyphenated)
federated learning (75 vs 4)
transfer learning (45 vs 0)
machine learning (17 vs 1)
neural network, smart contract

### Capitalization (verified)

| Term | Form | Evidence |
|---|---|---|
| blockchain | **lowercase** | 141 lower vs 51 upper |
| federated learning | **lowercase** | 57 lower vs 6 upper |
| deep learning | **lowercase** | 81 lower vs 1 upper |
| smart contract | **lowercase** | 40 lower vs 1 upper |
| machine learning | **lowercase** | 16 lower vs 1 upper |
| neural network | **lowercase** | 44 lower vs 2 upper |
| CNN | **ALL CAPS** | 50 upper vs 9 "convolutional neural network" |
| Internet of Things | **Capitalized** | Proper noun |
| IoT | **ALL CAPS** | Always |
| VANET | **ALL CAPS** | Always |
| Re-ID | **Capitalized hyphen** | Consistent |

Acronym first use: full term lowercase + acronym in parentheses:
"federated learning (FL)", "vehicular ad-hoc networks (VANETs)", "convolutional neural
network (CNN)"

### Numbers and statistics

**Numerals vs spelled-out:** BOTH are used.
- Numerals: 3,999 uses — default for measurements, counts, metrics.
- Spelled-out: 184 uses — "two hospitals", "three phases", "four components", "one issue."
  Rule: use numerals for exact quantities and measurements; spell out for general counts
  and small ordinals at start of thought ("Two types of attackers are considered...").

**Percentages:** Always % symbol (183 uses). "percent" = 0.

**Decimal places:** 1 decimal (380 uses) and 2 decimal (387 uses) — nearly equal.
Default to 2 for accuracy/metric tables; 1 for approximate comparisons in prose.

**Ranges:** En dash: "100–300 ms", "866–868 MHz", "100–500 vehicles."

### Tense by section

| Section | Tense | Verified |
|---|---|---|
| Methodology | Present — "consists of," "we compute," "the model takes" | ✓ |
| Results | Past — "achieved," "improved," "outperformed," "conducted" | ✓ |
| Own framework (present) | Present — "we propose," "the proposed scheme avoids" | ✓ |
| Literature review | Past — "proposed," "designed," "achieved" | ✓ |
| Discussion | Present — "demonstrates," "is due to," "outperforms" | ✓ |
| Conclusion summary | Present — "this paper proposes" | ✓ |
| Future work | Future — "we aim to," "future work will" | ✓ |

### Word choices (verified from 11 PDFs — CORRECTED COUNTS)

**System noun** (model 564 >> algorithm 128 >> scheme 103 >> framework 97 >> approach 85
>> method 76 >> system 65 >> technique 34):
- "model" is the dominant term — use it as primary.
- "algorithm" is very common — do not avoid it.
- "framework" for the overall system architecture.
- "scheme" for security/authentication papers.
- All of approach, method, technique are acceptable.

**Proposal verbs** (we propose 20 >> we design 3 / we present 3 / we introduce 2):
- "we propose" is by far the primary verb — use it as default.
- "we design," "we present," "we introduce" are secondary and rare.
- "we utilize" appears in actual papers — acceptable.

**Results verbs** (shows/show 87 >> demonstrates/demonstrate 28 >> validates 15
>> indicates 13 >> illustrates 9 >> confirms 6):
- "shows" is the primary results verb (Fig. n shows...; Table n shows...).
- "demonstrates" is for overall conclusion statements ("results demonstrate...").
- "validates," "indicates," "illustrates," "confirms" are all used — not forbidden.

**Gap adjectives** (current 37 >> previous 27 >> existing 22 >> recent 24
>> state-of-the-art 16 >> traditional 14):
- "current," "previous," "existing," and "recent" are all commonly used — no single
  dominant preference. Use whichever fits the sentence naturally.

**use vs utilize:** Both are used. "use/used/using" (371 total) >> "utilize/utilized" (33).
Prefer "use" but "utilize" is acceptable and appears in the papers.

**perform vs conduct:** Both are used. "perform" (38) and "conducted" (18) both appear.
"An extensive empirical study has been conducted" is a real phrase from the corpus.
"conducted" = experiment context. "performed" = algorithmic/process context.

**compared to vs compared with:** "compared to" (17 uses) is standard in this corpus.
"compared with" appears only 1 time. Use "compared to."

**improve vs enhance:** Both are common. improve (48) ≈ enhance (44). Use either.

**limitation vs drawback:** limitation/limitations (18) >> challenges (42) >> drawback (3).
"challenges" is actually the most common word for limitations.

**performance vs accuracy:** performance (139) >> accuracy (80) >> efficiency (18).
"performance" is the dominant term.

**this paper vs this work:** this paper (16) > this work (10). Both are acceptable.
"this study" = 0 uses — do not use.

**which vs that:** that (265) >> which (161). Prefer "that" but "which" is common.

**very:** 16 uses in corpus — "very often," "very difficult," "very simple," "very large."
Use sparingly but it is not forbidden.

**highly:** 12 uses — acceptable as an intensifier.

**clearly:** 3 uses — acceptable but use sparingly.

**obviously:** 0 uses — do not use.

### Figure and table references (verified)

**Figures:** Always "Fig." abbreviated (181 uses vs 25 "Figure").
Four verified patterns by frequency:
1. "shown in Fig. n" (20) — most common.
2. "Fig. n shows [description]" (12) — active subject.
3. "as shown in Fig. n" (8) — inline.
4. "Fig. n illustrates [description]" (6).

**Tables:** Always "Table n" — never "Tab." (0 uses).
Patterns: "Table n shows...", "in Table n", "Table n presents...", "summarized in Table n."

**Equations:** Numbered (1), (2), (3).
Referenced as "Equation (n)" (17 uses) > "Eq. (n)" (10 uses).

### Paragraph structure (verified from PDFs)

- No paragraph indentation — block paragraph format confirmed.
- Introduction paragraphs: 4–8 sentences each, 4–5 paragraphs total.
- Methodology subsections: 3–5 sentences per component description.
- Results: 3–6 sentences per comparison block.
- Conclusion: 4 paragraphs of 2–4 sentences each.

### Reference formats

Depends on target journal — not a fixed personal style:
- IEEE journals → [n] Author, "title," Journal, vol., pp., year.
- Elsevier journals → Author, A., Year. Title. Journal volume, pages.
- MDPI journals → n. Author, A.; Author, B. Title. Journal year, vol, pages.

In-text citation style (IEEE): "as proposed in [n]" or "Author et al. [n] proposed..."
In-text citation style (Elsevier/MDPI): "(Author et al., year)" or "Author et al. (year)"

---

## 11. Pre-Output Checklist

**Formatting**
- [ ] No horizontal rules (`---`) anywhere in paper body
- [ ] No em dash (`—`) in body text
- [ ] No paragraph indentation — block format
- [ ] Semicolons only for: before "however"; parallel metrics; tightly linked clauses
- [ ] Colons only before lists, algorithms, metric results
- [ ] Parentheses for acronym definitions and math only

**Figures, tables, equations**
- [ ] "Fig. n" not "Figure n" in running text
- [ ] "Table n" not "Tab. n"
- [ ] Equations referenced as "Equation (n)" or "Eq. (n)"
- [ ] Every equation introduced before and explained after

**Terminology**
- [ ] blockchain / federated learning / deep learning / smart contract → lowercase
- [ ] CNN / IoT / VANET → all caps
- [ ] "this paper" not "this study"
- [ ] "compared to" not "compared with"
- [ ] "model" or "framework" as primary system noun
- [ ] "algorithm" included where relevant (very common)
- [ ] "we propose" as primary proposal verb
- [ ] "shows" for Fig/Table results; "demonstrates" for overall conclusions
- [ ] Hyphenated: semi-supervised, pre-trained, privacy-preserving, state-of-the-art
- [ ] Not hyphenated: deep learning, federated learning, transfer learning
- [ ] "obviously" never used

**Numbers**
- [ ] % symbol not "percent"
- [ ] Numerals for measurements; spelled-out for general small counts
- [ ] Decimal places: 2 for metric tables, 1 for prose approximations
- [ ] Ranges with en dash: 100–300 ms

**Tense**
- [ ] Methodology in present tense
- [ ] Results and experiments in past tense
- [ ] Own framework description in present tense

**Structure**
- [ ] Sentence length ≈ 17–18 words average in body text
- [ ] Introduction: 4–5 paragraphs of 4–8 sentences each
- [ ] Gap introduced with "However," or verified phrase
- [ ] Contribution list opens with exact phrase
- [ ] Framework named with acronym
- [ ] Future work specific — not generic
- [ ] First-person plural throughout
- [ ] Zero invented facts, citations, or metrics
