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
  me write the contribution list." This skill captures the author's real, corpus-verified
  voice — always apply it instead of producing generic academic writing.
---

# My Writing Style — Master Corpus Skill

Built from 27 published papers across blockchain, federated learning, deep learning,
IoT security, VANETs, vehicle re-identification, medical imaging, recommender systems,
RFID, remote sensing, NLP, autonomous systems, and complex networks.
Every rule is verified against the actual corpus with frequency counts.

---

## 1. Core Voice Identity

- **First-person plural throughout:** we propose, we design, we introduce, we evaluate,
  we compare, we recommend, we hypothesize, we conduct, we improve.
- **Problem-first framing:** domain importance → specific limitation → proposed solution.
- **Hybrid-framework identity:** always combine two or more techniques and justify why
  neither alone is sufficient.
- **Experimentally grounded:** every claim tied to a named metric and a named baseline.
- **Assertive, not hedging:** write with confidence. Minimal hedging language.
- **Average sentence length:** 17–18 words. Medium-length declarative sentences with
  occasional complex clauses. No very short fragments. No very long run-ons.
  - Short opener (abstract): "Vehicle re-identification is one of the essential applications of urban surveillance." (11 words)
  - Typical body sentence: "At the same time, researchers have also focused on enhancing blockchain scalability and performance using the sharding mechanism." (18 words)
  - Complex clause: "Even though license plates are vital to differentiate between vehicles, their use is uncontrollable and can be faked or broken." (20 words)

---

## 2. Verified Transition Words (with corpus frequencies)

Use these in the proportions shown. "however" is the most used word in the corpus.

| Transition     | Frequency | Primary use                        |
|----------------|-----------|------------------------------------|
| however        | 37×       | Gap introduction, contrast         |
| therefore      | 26×       | Causal conclusion in results/discussion |
| moreover       | 16×       | Adding a point in intro/related work |
| furthermore    | 14×       | Reinforcing in methodology/discussion |
| thus           | 10×       | Short causal link mid-sentence     |
| overall        | 10×       | Summary opener in discussion/conclusion |
| hence          | 8×        | Formal proofs and security analysis |
| in addition    | 5×        | Supplementary point in methodology |
| consequently   | 4×        | Result-of-action in discussion     |
| instead        | 4×        | Contrast with alternative          |

Also use "while" frequently as a within-sentence contrast connector:
"[Component A] improves [X], while [component B] ensures [Y]."

---

## 3. Real Phrases From the Papers

These are verbatim from the corpus. Use them or close variants.

### Opening / context-setting
- "Vehicle re-identification (re-id) received immense attention..."
- "Nowadays, smart devices have become part of the Internet of Things (IoT), and are widely used in..."
- "The present outbreak of COVID-19 is a worldwide calamity."
- "Stock market forecasting has drawn interest [from researchers and practitioners]."
- "NER is a fundamental task [in natural language processing]."
- "The early detection of dangerous situations and forecasting techniques is important."
- "[Domain] has gained significant attention in recent years."

**Opener pattern:** "[Domain/technology/problem] [verb showing importance] [in/for context]."

### Gap-building sentences
- "However, existing methods suffer from [limitation]."
- "However, these studies [gap]."
- "Nevertheless, [prior approach] fails to address [specific issue]."
- "Although [X] has been studied, [Y] remains an open challenge."
- "Still, [topic] has not been studied well." ← adapt the topic: "Still, Sindhi NER has not been studied well."
- "Traditional target detection algorithms have difficulty [doing X]." ← adapt for any traditional method
- "Traditional path-planners generate the shortest possible routes [but ignore safety]." ← adapt for other safety/quality trade-offs
- "To the best of our knowledge, [novelty claim]."
- "To the best of authors' knowledge, [novelty claim]."
- "More importantly, to the best of our knowledge, [strongest novelty claim]."
- "There is still ample room to improve [aspect] under [condition]."
- "Geometric modeling using CNNs remains an open challenge." ← adapt: "[X] remains an open challenge."
- "Most existing approaches focus on [A], while overlooking [B]."

**Pattern:** gap sentences always name a specific technical limitation — not a vague "research gap."

### Proposing the method
- "To tackle the mentioned challenges, we propose..."
- "To tackle the aforementioned issues, we propose..."
- "To solve the mentioned challenges, [framework] is proposed."
- "To address the aforementioned problems, we propose..."
- "To address these issues, we propose..."
- "To overcome this weakness, [approach] is introduced."
- "To handle this issue, we have designed an improved [model]."
- "To deal with this issue, we propose [model]."
- "With this motivation, [we propose / this paper presents]..."
- "In this paper, we propose a methodology for [task]."
- "In this paper, we propose a model for [task]."
- "This paper presents a novel framework for [task]."
- "This paper presents a novel technique for [task]."
- "This paper presents a comprehensive study of [topic]."
- "This paper introduces a framework [for/to] [purpose]."
- "This article presents [design/method]."
- "This work presents a novel [X] for [Y]."
- "We propose a novel end-to-end, two-stream-based deep learning framework."

### Describing the system
- "The proposed framework consists of [A], [B], and [C]."
- "The proposed framework collects a small amount of data from various sources."
- "The proposed scheme creates trust [in/for/between] [entities]."
- "The proposed [model/scheme/approach] has the ability to [do X]."
- "Smart contract provides the authentication mechanism."
- "Blockchain guarantees the trust, confidentiality, and integrity."
- "Blockchain-based integrity proof chain [provides/ensures X]."
- "RFID and blockchain are considered as dynamic duals."
- "The inbuilt power of federated architecture [enables/ensures X]."
- "Without relying on a central server."
- "Collaboratively train a global model."
- "Raw data never leave the local node; only [parameters/gradients] are transmitted."
- "[Component] is well-suited for real-time [application] applications."
- "We hypothesize that robust information can be extracted through [mechanism]."

### Contribution list opener — use one of these exactly
- "The main contributions of this paper are summarized as follows:"
- "The main contributions of this paper are as follows:"

### Results sentences
- "Extensive experimental results demonstrate that the proposed method outperforms..."
- "Extensive experiments demonstrate [X]."
- "Extensive empirical evaluation demonstrates [X]."
- "Experimental outcomes demonstrate [X]."
- "Experimental results show [X]."
- "Experimental results validate their effectiveness."
- "Simulation results show [X]."
- "The proposed method outperforms state-of-the-art methods."
- "The proposed scheme significantly improves performance."
- "Compared with [baseline], the proposed [model] achieves..."
- "Ablation experiments reveal [X]."
- "We attain new state-of-the-art results."
- "We recommend it for the identification of [task/disease]."
- "The best results for the three datasets were obtained [by/with] [method]."

### Closing / forward-looking
- "[This work] will frame the next level research."
- "We aim to facilitate future research [in domain]."
- "Future work might include [specific direction]."
- "In future work, we aim to [specific action]."
- "There are massive opportunities for improvement and research [in this area]."
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
- 4–5 dense sentences:
  1. Domain + core problem
  2. Proposed framework and key components
  3. Evaluation setting and main metric result (with number)
  4. Practical significance
- No citations. No bullet points. ≤250 words. No limitations mentioned.
- Sentence length: keep each under 25 words.

### Introduction
**¶1 — Broad domain importance** (2–3 sentences)
Pattern: "[Domain] [received/has gained] [attention/importance] [because/due to]..."

**¶2 — Narrow to one specific technical challenge** (3–4 sentences)
One barrier: privacy leakage, computational overhead, dataset bias, authentication cost,
gradient exposure, data scarcity, routing instability, low-resource constraints.

**¶3 — Grouped literature + gap** (4–6 sentences)
Group prior methods by family. End with: "However, [gap]." or "To the best of our knowledge, [novelty]."

**¶4 — Proposed solution + contributions** (2–3 sentences + numbered list)
Open: "To tackle the aforementioned issues / To address the aforementioned problems, we propose..."
Then: "The main contributions of this paper are summarized as follows:"

**¶5 — Paper organization** (1 sentence)
"The rest of this paper is organized as follows."

Typical introduction: 4–5 paragraphs. Contribution list: 3–5 numbered points.

### Related Work
- Group by method family — never list author-by-author.
- End each group with what the family collectively fails to solve.
- Typical groupings from this corpus:
  - Blockchain, federated learning, and cryptographic approaches
  - Appearance-based, license-plate-based, and spatio-temporal Re-ID
  - Rule-based, statistical, and neural NER
  - Traditional detectors vs. YOLO-based single-stage detectors
  - PKI, identity-based, and certificateless VANET authentication
  - Data anonymization, differential privacy, and homomorphic encryption

### Methodology
Describe sequentially — component by component:
1. System model or data source
2. Preprocessing / data augmentation
3. Feature extraction or model architecture (name each component)
4. Security / privacy / trust mechanism
5. Training, aggregation, routing, or authentication protocol
6. Evaluation protocol and metrics

Use present tense throughout: "the framework consists of," "we compute," "the model takes."
Include equations when defining hash functions, aggregation rules, similarity functions,
routing decisions, loss functions, or formal security proofs.
Name your framework with an acronym (e.g., Fed-CARS, OSGM, EINDM, CLSS-CPPA, MCNN, SPP).

### Results
- Past tense throughout: "achieved," "improved," "outperformed," "produced."
- Always compare against named baselines.
- Always use "compared with" — never "compared to" (0 uses of "compared to" in corpus).
- Structure: table/figure reference → interpretation → comparison → reason for gain.

### Discussion
- Opens by explaining WHY each component contributes.
- Pattern: "[Component A] [improves/ensures X], while [Component B] [ensures Y]."
- Real examples from corpus:
  - "Blockchain permits secure collaboration among hospitals, while deep learning improves early-stage detection."
  - "Federated learning protects hospital data, while blockchain authenticates and aggregates model updates."
  - "Data augmentation reduces background and pose bias, while spatio-temporal cues reduce the negative effects of visual variations."
- Present tense for interpretation.

### Conclusion
- ¶1: Restate problem + proposed framework name/components. Present tense.
- ¶2: Key experimental findings with at least one metric value. Past tense.
- ¶3: Limitations — brief and specific (17/27 papers say "Not stated" — but always include it).
- ¶4: Future work — always specific:
  - "Extend LSS to directed and weighted networks."
  - "Improve blockchain latency and cost-effectiveness."
  - "Use attention networks to extract more salient features."
  - Never: "We will improve the model in future work."

---

## 6. Contribution List Structure

Every paper has exactly **one theoretical contribution + one practical contribution**.
This is a 100% consistent pattern across all 27 papers.

**Contribution point starters** (by frequency):
- "The proposed [framework/scheme/model]..." (18×) — most common
- "We propose / We design..." (4×)
- "A novel [framework/approach]..." (4×)
- "An efficient [method/scheme]..." (4×)
- "A comprehensive [study/review]..." (2×)

Each contribution point: one sentence, ending with a period.
Always one theoretical contribution (what it adds to knowledge) and
one practical contribution (what real-world problem it solves).

---

## 7. How to Write Equations, Methods, and Algorithms

### Introducing an equation
Always: motivating sentence → equation → "where" clause defining every symbol.
Never drop an equation in without context.

**Phrases to introduce equations:**
- "The [function/procedure] is defined as follows:"
- "The [output/weight/probability] is computed as:"
- "Formally, [quantity] is given by:"
- "The [loss/objective/distance] function is formulated as:"
- "Let [symbol] denote [meaning]. Then [quantity] is defined as:"
- "where [symbol] denotes [meaning], and [symbol] represents [meaning]."

**After every equation, connect back to purpose:**
- "This ensures that [security/privacy/convergence] is [guaranteed/maintained]."
- "By doing so, [component] achieves [outcome]."
- "As a result, [system output/model performance] is [improved/maintained]."

### Domain-specific equation patterns

**Blockchain/security:** H(·) for hash, σ = Sign(sk, m) for signatures,
T = {ID, timestamp, hash, data} for transaction structure.
Close with: "The scheme is proved secure under the [ECDLP] hardness assumption
in the random oracle model."

**Federated learning:** wᵢ for local parameters, w_global = Σᵢ(|Dᵢ|/|D|)·wᵢ for
aggregation. Always state: "Raw data never leave the local node."

**Vehicle Re-ID/similarity:** S(q,g) = α·V(q,g) + (1−α)·ST(q,g) for composite score.

**VANET/clustering:** Cost function C = w₁·d + w₂·Δv + w₃·overhead.

**Path planning:** J = w₁·length + w₂·risk + w₃·smoothness for trajectory cost.

**NLP/sequence labeling:** hₜ = [hᶜₜ; hʷₜ] for contextual representation.

**Clustering/topic models:** ws(w) = log(N/df(w)) for word specificity.

### Describing an algorithm

**Style 1 — Formal block:**
```
Algorithm n: [Name]
Input:  [inputs with types]
Output: [outputs with types]
1.  [Action verb] [object]
2.  [Action verb] [object]
3.  Return [output]
```

**Style 2 — Sequential prose:**
"First, [step]. Then, [step]. Subsequently, [step]. Finally, [result]."
Or: "In the first phase, [action]. In the second phase, [action]."

**Intro phrases before algorithm:**
- "The proposed algorithm is summarized in Algorithm [n]."
- "The procedure is described as follows."

### Introducing model components
Three-part pattern:
1. "The [component] is designed to [function/goal]."
2. "Specifically, [component] takes [input] as input and produces [output]."
3. "This design [ensures/allows/enables] [technical benefit]."

### Security proof (Paper 12 pattern)
1. "We consider two types of adversaries: Type-I [who...] and Type-II [who...]."
2. "Theorem n: The proposed scheme is [EUF-CMA] secure under [assumption] in the random oracle model."
3. "Proof: We construct a simulator S that [action]. If adversary A can [break property], then S can solve [hard problem] with non-negligible probability, which is a contradiction."
4. "Therefore, the proposed scheme is secure against [attack type]. □"

---

## 8. Domain-Specific Metrics

| Domain | Primary Metrics |
|---|---|
| Medical imaging | accuracy, sensitivity, specificity, F1-score, AUC, PSNR, MSE, MCC |
| Vehicle Re-ID | mAP, CMC, HIT@1, HIT@5, Rank-k |
| Recommender systems | MAE, RMSE, nDCG, HIT@K |
| VANET / Security | computational cost, communication cost, latency, verification time, throughput |
| Remote sensing | AP, mAP, FPS (detection speed) |
| Clustering / NLP | NMI, purity, homogeneity, V-measure, F1, precision, recall |
| Path planning / Routing | cluster lifespan, path length, computation time, collision rate, DCPA |
| Blockchain / RFID | read range, transaction throughput, tamper detection rate, gas cost |
| Stock / time-series | RMSE, MSE, MAE, R-squared, explained variance, Kendall correlation |
| Complex networks | SIR score, Kendall correlation, time complexity O(nk²+|E|) |
| Autonomous / HRI | balanced accuracy, precision, recall, F-measure, latency |

---

## 9. Signature Patterns

**"Dynamic duals":** "[Technology A] and [Technology B] are considered as dynamic duals."

**"Without relying on a central server":** close federated/distributed system descriptions.

**"Collaboratively train a global model":** for multi-party/hospital collaboration.

**"Lays a robust foundation":** "[This work] lays a robust foundation for [direction]."

**"Frame the next level research":** "[This work] will frame the next level research."

**"Devoted to updating state-of-the-art":** for survey/benchmark papers.

**"Massive opportunities":** "There are massive opportunities for improvement and research."

**"Inbuilt power":** "The inbuilt power of [federated architecture / blockchain] [enables X]."

**"Has the ability to tackle":** "The proposed [model] has the ability to tackle [challenge]."

**"Remains an open challenge":** for closing limitation/gap statements.

**"While" contrast connector:** "[A] does X, while [B] ensures Y." Used in discussion to
explain why the hybrid framework outperforms single-method approaches.

---

## 10. Verified Style Rules

### Punctuation
- **No `---` horizontal rules** in paper text. Prose flows continuously under numbered headings.
- **No em dash `—`**: 0 uses across 27 papers. Never use.
- **En dash `–`**: only in number ranges: 7–4.5 m, 866–868 MHz, 100–500 vehicles.
- **Semicolons `;`**: only 3 verified patterns:
  1. Before "however": "[X]; however, [Y]."
  2. Separating parallel metric results: "News: NMI 0.843; Tweets: NMI 0.844."
  3. Joining two tightly related independent clauses (rare).
  Never for listing items — use commas.
- **Colons `:`**: only before contribution lists, algorithm blocks, or metric result lists.
- **Parentheses `( )`**: only for acronym definitions or math expressions. No side remarks.
- **Oxford comma**: always — 26 verified uses: "privacy, ethical, and legal."

### Hyphenation
Always hyphenate: blockchain-based, privacy-preserving, spatio-temporal, state-of-the-art,
self-attention, context-aware, IoT-enabled, real-time, real-world, cross-dataset,
multi-level, large-scale, path-planning, attention-based, few-shot, co-occurrence,
long-term, short-term, rule-based, similarity-based, de-noising, e-voting, human-robot.

Do NOT hyphenate as standalone nouns: deep learning (16×), federated learning (18×),
machine learning (4×), neural network, smart contract.

### Capitalization
- blockchain → **lowercase** (54 vs 18)
- federated learning → **lowercase** (24 vs 9)
- deep learning → **lowercase** (17 vs 3)
- smart contract → **lowercase** (9 vs 0)
- IoT → **all caps** always
- VANET → **all caps** always
- Internet of Things → **capitalized** (proper noun)
- Re-ID → **capitalized hyphen** always

Acronym first use: full term lowercase + acronym in parentheses:
"federated learning (FL)", "vehicular ad-hoc networks (VANETs)"

### Numbers and statistics
- Default to numerals: 60 numeral uses vs 14 spelled-out across corpus.
- Percentages: always `%` symbol — "percent" has 0 uses.
- Metric decimal places: 2 decimal places (24 occurrences) > 3 (14) > 1 (12). Default: 2.
- Number ranges: en dash without spaces: 7–4.5 m, 866–868 MHz.

### Tense by section
| Section | Tense |
|---|---|
| Methodology | Present — "the framework consists of," "we compute" |
| Results | Past — "achieved," "improved," "outperformed" |
| Own framework description | Present — "we propose," "the proposed scheme avoids" |
| Literature review | Past — "Kumar et al. proposed," "the method achieved" |
| Discussion | Present — "this demonstrates," "the improvement is due to" |
| Conclusion summary | Present — "this paper proposes" |
| Future work | Future — "we aim to," "future work will examine" |

### Word choices (verified frequencies)
**System noun** (model 61 > framework 52 > technique 33 > scheme 12 > system 12):
- Use "model" or "framework" as primary terms.
- "technique" for a specific component. "scheme" only for security/authentication papers.
- Avoid "approach" (4) and "method" (4).

**Proposal verbs** (design 20 > propose 14 > develop 3 > present 2 > introduce 1):
- Default to "we design" and "we propose."
- Never: construct, create, build (0 uses each).

**Results verbs** (demonstrate 8 > show 3 > validate 2 > reveal 2):
- "demonstrate" is the primary verb for results.
- Never: indicate, illustrate, confirm, prove (0 uses each).

**Gap adjective** (existing 27 > state-of-the-art 9 > prior 5 > current 4 > traditional 4 > previous 1):
- Default to "existing." Avoid "previous" (only 1 use).

**use vs utilize**: always "use" — "utilize" has 0 occurrences across all 27 papers.

**perform vs conduct**: always "perform" (43×) — "conduct" = 0, "carry out" = 0.

**compared with vs compared to**: always "compared with" (7×) — "compared to" = 0.

**improve vs enhance**: improve (49×) >> enhance (19×) >> achieve (14×).
Never: boost (0), strengthen (1).

**limitation vs drawback**: limitation (30×) >> challenge (12×) >> constraint (5×).
Never: drawback (0), shortcoming (0).

**performance vs accuracy**: performance (37×) >> accuracy (23×) >> effectiveness (4×).

**this paper vs this work vs this study**:
"this paper" (6×) > "in this paper" (2×) > "this work" (1×).
Never "this study" (0 uses).

**which vs that**: prefer "that" (14×) over "which" (3×).

### Hedging and intensifiers
- Hedging — minimal: "may" (7×), "might" (1×). All others: 0 uses.
- Write assertively. Do not hedge unless genuinely uncertain.
- Intensifiers — almost none: "significantly" (2×), "highly" (1×).
- Never: very, greatly, extremely, remarkably (all 0 uses).
- Never: clearly, obviously, evidently, undoubtedly (all 0 uses).

### Citations
- Square bracket format: [n] for single, [n,m] for multiple adjacent.
- Introduced as: "as proposed in [n]" or "Author et al. [n] proposed..."
- Never author-year format (0 instances).

---

## 12. Verified From Actual PDF Papers

These 5 items were verified by reading the raw text of 11 actual papers.

### Paragraph Length by Section

Introduction paragraphs run **4–8 sentences** each. Typical structure:
- ¶1 domain importance: 3–4 sentences
- ¶2 specific challenge: 3–5 sentences
- ¶3 literature gap: 4–6 sentences
- ¶4 proposed solution + contributions: 3–4 sentences + numbered list
- ¶5 paper organization: 1 sentence

Methodology subsection paragraphs: 3–5 sentences per component.
Results paragraphs: 3–6 sentences per baseline comparison block.
Discussion paragraphs: 3–5 sentences explaining one component's gain.
Conclusion: 4 paragraphs of 2–4 sentences each.
**No one-sentence paragraphs in body text** (except the paper organization closing line).

### Paragraph Indentation

**No paragraph indentation.** Papers use block paragraph format — paragraphs are
separated by vertical space, not by a first-line indent. Confirmed across all 11 PDFs.
Do not indent the first line of any paragraph.

### Figure and Table Introduction

**Figures — always "Fig." (abbreviated), never "Figure" in running text.**
Evidence: "Fig. n" appears 181 times; "Figure n" appears 25 times (mainly in captions).

The 4 verified patterns ranked by frequency:
1. "shown in Fig. n" — most common: *"the architecture is shown in Fig. 3."*
2. "Fig. n shows..." — active subject: *"Fig. 3 shows the architecture of the proposed framework."*
3. "as shown in Fig. n" — inline: *"as shown in Fig. 1, the system consists of..."*
4. "Fig. n illustrates..." — *"Fig. 7 illustrates a few samples of data."*

**Tables — always "Table" (full word), never "Tab." abbreviated.**
The 4 verified patterns:
1. "Table n shows..." — *"Table 1 shows the parameter settings."*
2. "in Table n" — *"results are summarized in Table 4."*
3. "Table n presents..." — *"Table 3 presents the comparison."*
4. "illustrated in Table n" — *"as illustrated in Table 6, this enhancement..."*

### Equation Numbering and Reference Style

**Numbering:** Equations are numbered with a plain integer in parentheses at the
right margin: (1), (2), (3) etc. No "Eq." prefix on the equation number itself.

**Referencing in text** (frequency count):
- "Equation (n)" — most common (25 uses): *"It can be seen in Equation (1) that..."*
- "Eq. (n)" — secondary (13 uses): *"As shown in Eq. (2), the loss function..."*
- Never: "equation n" (without parentheses), "Eqn. n", "formula n"

**Phrases introducing equations** (verified from papers):
- "...can be expressed as:"
- "...is defined as follows:"
- "...is given as:"
- "...is formulated as:"
- "...is computed as:"
- "...performs as follows:"
- "...can be verified as follows:"

After presenting the equation, always follow with a sentence explaining it:
*"Equation (3) contains three prominent parts."*
*"It can be seen in Equation (1), the learning rate is η..."*

### Reference List Format

**The format depends on the target journal — not a fixed personal style.**
All three formats appear across the 11 papers:

| Journal type | Format used | Example |
|---|---|---|
| IEEE journals | `[n] Author, "title," Journal, vol., pp., year.` | IEEE Trans. Veh. Technol., IEEE Sensors J. |
| Elsevier journals | `Author, A., Year. Title. Journal.` | Computerized Medical Imaging, Expert Systems |
| MDPI journals | `n. Author, A.; Author, B. Title. Journal year, vol, pages.` | Electronics, Applied Sciences, Mathematics |

When writing a paper, match the reference format to the target journal exactly.
Do not invent a personal format.

---

## 13. Pre-Output Checklist

**Punctuation & formatting**
- [ ] No `---` horizontal rules anywhere
- [ ] No em dash `—` anywhere
- [ ] No paragraph indentation — block paragraphs only
- [ ] Semicolons only in the 3 verified patterns
- [ ] Colons only before lists/algorithms/metric results
- [ ] Parentheses only for acronyms or math
- [ ] Oxford comma in all three-item lists

**Figures, tables, equations**
- [ ] Figures: "Fig. n" not "Figure n" in running text
- [ ] Tables: "Table n" not "Tab. n" — always full word
- [ ] Equations: referenced as "Equation (n)" (primary) or "Eq. (n)" (secondary)
- [ ] Every equation introduced with a phrase before it and explained after it

**Terminology**
- [ ] blockchain / federated learning / deep learning / smart contract — all lowercase
- [ ] IoT, VANET — all caps
- [ ] "use" not "utilize"
- [ ] "perform" not "conduct"
- [ ] "compared with" not "compared to"
- [ ] "existing" as primary gap adjective
- [ ] "model" or "framework" as primary system noun
- [ ] "that" preferred over "which"
- [ ] "this paper" not "this work" or "this study"
- [ ] Hyphenated compounds correct
- [ ] No "very," "clearly," "obviously," "boost," "utilize," "conduct"

**Numbers**
- [ ] Numerals by default
- [ ] % symbol not "percent"
- [ ] Metrics to 2 decimal places
- [ ] Ranges with en dash: 7–4.5 m

**Tense**
- [ ] Methodology in present tense
- [ ] Results in past tense
- [ ] Own framework in present tense

**Structure**
- [ ] Sentence length ≈ 17–18 words average
- [ ] Introduction: 4–5 paragraphs of 4–8 sentences each
- [ ] Gap introduced with "However," or verified phrase
- [ ] Contribution list: exactly one theoretical + one practical
- [ ] Contribution list opens with exact phrase from Section 3
- [ ] Framework named with acronym
- [ ] Future work specific — not generic
- [ ] First-person plural throughout
- [ ] Zero invented facts, citations, or metrics
