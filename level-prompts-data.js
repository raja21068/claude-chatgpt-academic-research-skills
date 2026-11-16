// Prompts by level. {A} = "Your topic or idea" box, {B} = the stage's second box.
// {HONEST} = shared honesty rule. Each stage: 3 prompts x 3 levels (beginner / researcher / expert).
const HONEST = "Only use papers, numbers and results you can actually see or link to. If you could not open a file, search the web or run code, say so. Never invent citations, data or results.";
const SCORE_TABLE = "importance 15, evidence that the gap exists 15, novelty 20, scientific insight 15, feasibility 10, potential impact 10, evaluation strength 10, reproducibility 5";

const ICONS = {
  bulb: '<path d="M9 18h6M10 21h4M12 3a6 6 0 0 0-3.6 10.8c.6.5 1 1.2 1 2V16h5.2v-.2c0-.8.4-1.5 1-2A6 6 0 0 0 12 3Z"/>',
  attack: '<circle cx="10.5" cy="10.5" r="6"/><path d="m15 15 5.5 5.5M8 10.5h5"/>',
  rebuild: '<path d="M4 12a8 8 0 0 1 14-5.3M20 12a8 8 0 0 1-14 5.3"/><path d="M18 3v4h-4M6 21v-4h4"/>',
  search: '<circle cx="10.5" cy="10.5" r="6"/><path d="m15 15 5.5 5.5"/>',
  table: '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 10h18M9 5v14M15 5v14"/>',
  pen: '<path d="M4 20h4L19 9l-4-4L4 16v4Z"/><path d="m13.5 6.5 4 4"/>',
  list: '<path d="M9 6h11M9 12h11M9 18h11"/><circle cx="4.5" cy="6" r="1"/><circle cx="4.5" cy="12" r="1"/><circle cx="4.5" cy="18" r="1"/>',
  doc: '<path d="M14 3H6v18h12V7l-4-4Z"/><path d="M14 3v4h4M9 12h6M9 16h6"/>',
  check: '<path d="M12 3 4 6v6c0 4.5 3.4 8 8 9 4.6-1 8-4.5 8-9V6l-8-3Z"/><path d="m8.5 12 2.5 2.5 4.5-5"/>',
  code: '<path d="m8 7-5 5 5 5M16 7l5 5-5 5M13.5 4l-3 16"/>',
  bug: '<rect x="7" y="8" width="10" height="12" rx="5"/><path d="M12 8v12M7 13H3M21 13h-4M8 9 5 6M16 9l3-3M8 18l-3 2M16 18l3 2"/>',
  chart: '<path d="M4 20V4M4 20h16"/><path d="M8 16v-4M12 16V8M16 16v-6"/>',
  mail: '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>'
};

const LEVEL_STAGES = [
  // ───────────────────────── 1. IDEA ─────────────────────────
  {
    id: "idea", nav: "1 · Idea", title: "Get ideas → Check them → Improve",
    bLabel: "What you have (time, data, computer)",
    aHolder: "e.g. Forecasting how many students will visit the campus library tomorrow",
    bHolder: "e.g. 4 weeks, daily visit counts for 2 years, one laptop",
    exA: "Forecasting next-day visits to a campus library",
    exB: "4 weeks; 2 years of daily visit counts; the academic calendar; a laptop",
    loop: "Score still low? Give the new version to prompt 2 again. Most ideas need 2–3 rounds. Stop when the score is high enough for you (for example 75+), then go to step 2.",
    steps: [
      {
        title: "Generate ideas", icon: "bulb", chip: "You get: 3 ideas, pick 1", line: "No score yet. Just get good options.",
        attach: "Nothing needed. Optional: 1–3 papers you like, or the Idea Discovery skill file.",
        attachB: "You don't need to attach anything.",
        prompts: {
          beginner: `I am new to research.
My topic: {A}
What I have: {B}

Please suggest 3 simple research ideas I could really finish. For each idea, use plain words and give:
- The question (one sentence)
- Why it matters (one sentence)
- What data I would use
- What I would compare it against (a simple baseline)
- What result would show my idea is wrong

Then pick the best idea for me and tell me the first 3 things to do this week.

Do not give scores yet. {HONEST}`,
          researcher: `Goal: generate testable research ideas.
Topic: {A}
Resources and constraints: {B}

Propose 3 candidate research questions. For each give: a falsifiable hypothesis, likely data source, the simplest credible baseline, the primary metric, the main failure mode, and the smallest feasible test.
Separate a candidate gap (you think it is open) from an established gap (you have evidence it is open).
Finish with a comparison table, pick one idea, and say what evidence to look for first.

Do not score the ideas yet. {HONEST}`,
          expert: `Act as a senior researcher brainstorming with me.
Topic: {A}
Resources and constraints: {B}

Generate 5 research directions. For each:
1. The core mechanism in one sentence (what is actually new, not the application).
2. Which existing method families come closest and why they do not already solve it.
3. A falsifiable hypothesis and the result that would refute it.
4. The main identification or evaluation risk (e.g. confounding, simulator bias, offline-log limits).
5. The cheapest decisive experiment and the strongest baseline it must beat at equal budget.

Rank the 5 by expected value of information per unit of effort, recommend one, and write a one-paragraph idea brief for it.
Do not score yet; scoring happens in the next prompt. {HONEST}`
        },
        get: {
          beginner: ["3 ideas in plain words", "The best one picked for you", "3 things to do this week"],
          researcher: ["3 questions with hypothesis, data, baseline, metric", "Candidate vs established gap", "Comparison table + chosen idea"],
          expert: ["5 directions with mechanism + closest work", "Risk and decisive experiment for each", "Ranking + one-paragraph idea brief"]
        },
        sample: `<table><thead><tr><th>Idea</th><th>Question</th><th>Compare against</th></tr></thead><tbody>
<tr><td>A</td><td>Do exam weeks and holidays make simple visit forecasts fail?</td><td>Same weekday last week</td></tr>
<tr><td>B</td><td>Does weather change how many students visit?</td><td>Model without weather</td></tr>
<tr><td>C</td><td>Can visits in the morning predict the rest of the day?</td><td>Yesterday's total</td></tr>
</tbody></table><p><strong>Best pick:</strong> A — the data and calendar are easy to get and it runs on a laptop.</p><p class="hint">Sample answer, made up to show the format.</p>`
      },
      {
        title: "Score it & check if it's new", icon: "attack", chip: "Sample result: 58 / 100", line: "AI acts as a tough reviewer and searches for papers that already did it.",
        attach: "Your chosen idea from prompt 1 (same chat), or your proposal file (PDF/Word). Turn on web search.",
        attachB: "If your chat has a web search button, turn it on.",
        prompts: {
          beginner: `Here is my research idea: {A}

Act as a kind but honest teacher.
1. Search for papers that already did something similar. List up to 5, each with a link and one line on how close it is to my idea.
2. In plain words, tell me which part of my idea is already done and which part might still be new.
3. Score my idea out of 100 using this table: {SCORE}. Write one sentence for each score.
4. Tell me: go ahead, make it narrower, or change it, and why.

{HONEST}`,
          researcher: `Review this research idea as a skeptical referee: {A}

1. Scoring table out of 100 with weights ({SCORE}). Give a rationale for each line.
2. Strongest aspects (2–4).
3. Major weaknesses, ranked critical / major / minor.
4. Novelty attack: search the exact mechanism, synonyms and adjacent fields. Give a table: paper | link | overlap | severity.
5. What could still be genuinely new, stated as one sentence.
6. Recommendation: proceed, narrow, or change — and the smallest experiment that could change your view.

{HONEST}`,
          expert: `Act as an expert reviewer for a top venue. Review this research idea or the attached proposal: {A}

Write the report with exactly these sections:
1. Scoring table — criterion | weight | score | rationale, using {SCORE}. Then "Why the score is relatively low/high".
2. Strongest aspects — with sub-headings.
3. Major weaknesses — label each Critical/Major. Cover: novelty vs very recent work, whether the algorithm is specified, whether the chosen method (e.g. RL) is really needed, and whether the evaluation could show simulator/offline gains instead of real gains.
4. Novelty check — table: proposed idea | existing research | judgment. Then "What could genuinely be new" and a novelty judgment (architecture / algorithm / empirical: low–high).
5. Evidence needed — table of essential papers (priority | paper with link | issue to investigate), 2–3 preliminary experiments, and real-data analyses.
6. How to improve the score — 4–5 concrete changes, including a narrowed research question and a mandatory baseline table.
7. Expected score after improvement — current vs potential, per criterion.
8. Final assessment — score, recommendation, and the single decisive experiment.

Search literature from the last 2–3 years, including preprints. {HONEST}`
        },
        get: {
          beginner: ["Up to 5 similar papers with links", "What is done vs what is new", "Score /100 with one line each", "Go / narrow / change"],
          researcher: ["Scoring table with rationale", "Strengths and ranked weaknesses", "Overlap table with severity", "Recommendation + smallest test"],
          expert: ["8-section review report", "Overlap table of recent papers", "Evidence and experiments needed", "Current vs potential score"]
        },
        example: {file: "demo/sample-idea-review.md", label: "See a sample answer: review scored 58/100", note: "Made-up sample to show the format (library-visits project)."}
      },
      {
        title: "Improve & re-score", icon: "rebuild", chip: "Sample result: 58 → 76 / 100", line: "Fix the weak points the review found and score again.",
        attach: "Same chat as prompt 2. If new chat: paste your idea and the full review from prompt 2.",
        attachB: "Nothing to attach.",
        prompts: {
          beginner: `Here is my idea: {A}
Use the review above in this chat.

Help me make it better.
1. Rewrite my research question in one clear sentence that avoids what other papers already did.
2. Explain the new idea with a simple everyday example.
3. Give me a step-by-step method (at most 5 steps).
4. List 3 experiments, from smallest to biggest, and what each one must show.
5. Score the new version with the same 100-point table, next to the old score.
6. Tell me the one experiment to run first.

{HONEST}`,
          researcher: `Using the review above, rebuild this idea so it survives review: {A}

1. What to change: table of original claim | closest work (with link) | what the new version must show.
2. Narrowed research question (one sentence) and a concrete example scenario.
3. Method: the key components, what exactly is estimated, and the decision rule.
4. Experiments table: experiment | design and baselines at equal budget | evidence required.
5. Score table: original vs rebuilt per criterion ({SCORE}) with what still limits each.
6. The decisive experiment, and what to publish instead if it fails.

{HONEST}`,
          expert: `Act as senior co-author and reviewer. Rebuild the idea using the review above: {A}

Open with two short paragraphs: what to keep, what to change, old score → new score and whether you would fund the pilot.
Then write exactly these sections:
1. What I would change in the original idea — table: what the original proposed | closest work (named, linked) | what the new idea must establish. End with the single strongest contribution.
2. Updated research idea — research question, a concrete real-world example, and a table of cases the method must handle (where it should succeed, and where no method can succeed and why).
3. Methodology — components; the exact target being estimated; any key equation with the assumption it needs; a 3-way decision rule (use / keep testing / withhold); what you keep from the earlier review's suggestions.
4. Experiments — table: experiment | design and controls (strongest baselines, same budget, no hidden labels) | evidence required. Include a ground-truth simulator test, the main test, ablations, a second environment, and a real-data test. Say what is frozen before testing.
5. Score and decision — table: criterion | original | rebuilt | what still limits it, total, the decisive experiment, and the fallback paper if it fails.

{HONEST} Do not claim any results; this is a proposal.`
        },
        get: {
          beginner: ["New one-sentence question", "Everyday example", "5-step method + 3 experiments", "Old vs new score"],
          researcher: ["What-to-change table", "Narrow question + method", "Experiments table", "Old vs new score + decisive test"],
          expert: ["5-section rebuilt proposal", "Decision rule + key equation", "5 experiments with controls", "Old vs new score table"]
        },
        example: {file: "demo/sample-idea-rebuild.md", label: "See a sample answer: rebuilt 58 → 76/100", note: "Made-up sample to show the format (library-visits project)."}
      }
    ]
  },

  // ───────────────────────── 2. LITERATURE ─────────────────────────
  {
    id: "literature", nav: "2 · Literature", title: "Find papers → Compare → Write",
    bLabel: "Search scope (years, venues, databases)",
    aHolder: "Paste your chosen idea (one paragraph) from step 1",
    bHolder: "e.g. 2018–2026, Google Scholar and arXiv, journals in my field",
    exA: "Do academic-calendar features (exams, holidays) improve next-day library visit forecasts over a same-weekday baseline?",
    exB: "2015–2026; Google Scholar and arXiv; footfall, occupancy and event-aware forecasting",
    loop: "Found a paper that already does your idea? Go back to step 1, prompt 3 (Improve) with that paper. Otherwise carry the gap statement to step 3.",
    steps: [
      {
        title: "Find the closest papers", icon: "search", chip: "You get: 10–20 checked papers", line: "Search widely, then keep only papers you can open.",
        attach: "Your idea. Optional: 1–3 seed papers you already know. Turn on web search.",
        attachB: "Turn on web search if your chat has it.",
        prompts: {
          beginner: `My research idea: {A}
Where to look: {B}

Help me find papers close to my idea.
1. Give me 5 search phrases I can type into Google Scholar (include other words people use for the same thing).
2. Search and list up to 10 papers. For each: title, year, link, and one plain sentence on what it did.
3. Mark the 3 papers closest to my idea with ⭐.

{HONEST}`,
          researcher: `Idea: {A}
Scope: {B}

Run a literature search for this idea.
1. Break the idea into concepts (task, mechanism, setting, outcome) and list synonyms for each.
2. Search the scope above. Log: database, query, date, number of hits.
3. Return 10–20 papers: title | year | venue | DOI or link | method | dataset | how close (high/medium/low).
4. State which papers you opened in full text vs only saw the abstract.

{HONEST}`,
          expert: `Idea: {A}
Scope: {B}

Run a systematic, adversarial search whose goal is to find work that already does this idea.
1. Query plan: exact mechanism, conceptual synonyms, older names for the problem, adjacent fields (e.g. bandits, RL, continual learning, causal inference), and preprints from the last 12 months.
2. Search log table: source | query | date | hits | kept.
3. Inclusion/exclusion criteria, stated before results.
4. Ranked shortlist (max 20): paper | year | venue | link | mechanism | evaluation setting | overlap with my idea (what exactly) | what I checked (abstract / full text / code).
5. Coverage risk: which areas you could not search well and what query I should run myself.

{HONEST}`
        },
        get: {
          beginner: ["5 search phrases", "Up to 10 papers with links", "Top 3 marked ⭐"],
          researcher: ["Concepts + synonyms", "Search log", "10–20 paper table"],
          expert: ["Query plan + search log", "Inclusion rules", "Ranked overlap table", "Coverage risks"]
        }
      },
      {
        title: "Compare with your idea", icon: "table", chip: "You get: comparison table", line: "Put your idea next to the closest papers, side by side.",
        attach: "Same chat. Best: attach the PDFs of the 3–5 closest papers.",
        attachB: "If you have the PDFs of the top papers, attach them.",
        prompts: {
          beginner: `Using the papers above, help me see what is new about my idea: {A}

1. Make a simple table: rows = the 3–5 closest papers, columns = the main parts of my idea. Use ✓ (they did it), △ (partly), ✗ (not done), ? (not sure).
2. In plain words: which part of my idea nobody has done yet?
3. Which paper is my biggest "competitor", and why?

{HONEST}`,
          researcher: `Compare my idea with the 3–5 closest papers above: {A}

1. Novelty matrix: rows = papers + "my idea"; columns = 4–6 key design features. Use ✓ / △ / ✗ / ?, and give the page or section that supports each ✓ or △.
2. The strongest competitor and the exact difference from my idea.
3. A one-sentence contribution statement that is still true after this comparison.
4. Recommendation: proceed, narrow, or change.

{HONEST}`,
          expert: `Build an evidence-backed novelty matrix for: {A}

1. Columns = the minimal set of features that define my contribution (mechanism, target being estimated, setting, evaluation protocol, assumptions). Rows = closest papers.
2. Each cell: ✓ / △ / ✗ / ? plus a cited location (page, section, equation or table). Mark cells checked from abstract only.
3. For the 2 strongest competitors: could their method, with small changes, do what mine does? Explain concretely.
4. Bounded contribution statement: what survives, under which assumptions, and what must be shown empirically to claim it.
5. Rejection risk: the one sentence a reviewer would most likely write, and the evidence that would answer it.

{HONEST}`
        },
        get: {
          beginner: ["Simple ✓/✗ table", "What nobody has done", "Biggest competitor"],
          researcher: ["Matrix with page references", "Strongest competitor", "One-sentence contribution"],
          expert: ["Feature matrix with citations", "Competitor adaptability check", "Bounded contribution + rejection risk"]
        },
        sample: `<table><thead><tr><th>Paper</th><th>Daily forecast</th><th>Uses calendar events</th><th>Errors by day type</th></tr></thead><tbody>
<tr><td>Paper X (2026)</td><td>✓</td><td>✗</td><td>△</td></tr>
<tr><td>Paper Y (2024)</td><td>△</td><td>✓</td><td>✗</td></tr>
<tr><td><strong>My idea</strong></td><td>✓</td><td>✓</td><td>✓</td></tr>
</tbody></table><p class="hint">Illustrative example made up for teaching. Your matrix must cite real pages.</p>`
      },
      {
        title: "Write the related-work section", icon: "pen", chip: "You get: section text + reference list", line: "Turn the comparison into text for your paper.",
        attach: "Same chat. Optional: a related-work section from a paper you like (for style).",
        attachB: "Nothing to attach.",
        prompts: {
          beginner: `Using only the papers above, write a short "Related Work" section for my idea: {A}

- 3 short paragraphs, each about one group of papers.
- End with one paragraph: "What is missing" — the gap my work fills.
- Put each paper as [Author, Year].
- Then give me the reference list with links.

{HONEST}`,
          researcher: `Write the Related Work section for: {A}

1. Group papers into 3–4 themes; one paragraph per theme that compares, not just lists.
2. Final paragraph: the gap, stated so it follows from the comparison.
3. Cite only papers above, as \\cite{key}.
4. Give BibTeX entries with DOI or URL for every cited paper.
5. List claims in the text that still need a check.

{HONEST}`,
          expert: `Write a venue-ready Related Work and gap statement for: {A}

1. Organise by the contribution's design axes (not chronologically). For each theme: what the line of work assumes, what it achieves, and the precise limitation relevant to my question.
2. Position my work against the strongest competitor explicitly, with the bounded contribution statement from the matrix.
3. Introduction gap paragraph (≤120 words) that a skeptical reviewer would accept.
4. BibTeX for every citation with DOI/URL; flag preprints and any entry not verified against the source.
5. Self-check: list every sentence that makes a factual claim about another paper, with its supporting location.

{HONEST}`
        },
        get: {
          beginner: ["3-paragraph related work", "What is missing", "Reference list with links"],
          researcher: ["Themed related work", "Gap paragraph", "BibTeX file", "Claims to check"],
          expert: ["Axis-organised related work", "Gap paragraph ≤120 words", "Verified BibTeX", "Claim-to-source list"]
        }
      }
    ]
  },

  // ───────────────────────── 3. DRAFT ─────────────────────────
  {
    id: "draft", nav: "3 · First draft", title: "Outline → Draft → Check the plan",
    bLabel: "Target venue and format",
    aHolder: "Your idea + method plan (paste from steps 1–2)",
    bHolder: "e.g. NeurIPS LaTeX template, 9 pages; or a Word draft for my supervisor",
    exA: "Event-aware library visit forecasting: same-weekday baseline vs lag model vs lag + calendar model; MAE per day type",
    exB: "Conference paper, LaTeX, 9 pages + appendix",
    loop: "The plan check found gaps? Fix the plan and re-run prompt 3. When the plan is frozen, go to step 4 (Code).",
    steps: [
      {
        title: "Make the outline", icon: "list", chip: "You get: section-by-section outline", line: "Decide what each section must say before writing it.",
        attach: "Idea brief, related-work draft and .bib from step 2. Optional: the venue template.",
        attachB: "Attach your idea and your related-work text from step 2.",
        prompts: {
          beginner: `Help me plan my paper.
My idea: {A}
Where I will send it: {B}

Give me an outline with these sections: Title, Abstract, Introduction, Related Work, Method, Experiments, Results, Conclusion.
Under each, write 2–4 bullet points of what it should say, in plain words.
Tell me which section to write first.

{HONEST}`,
          researcher: `Create a paper outline for: {A}
Venue/format: {B}

For each section: purpose, 3–6 key points, which citations go there, and target length.
List every planned table and figure: number, question it answers, data it needs, metric.
List the contributions as 2–4 bullet points that the experiments will test.

{HONEST}`,
          expert: `Produce a reviewer-proof outline for: {A}
Venue/format: {B}

1. Contribution list (2–4), each paired with the experiment and table/figure that will test it.
2. Section plan with word budget, key claims, and the evidence each claim needs.
3. Table/figure plan: id | research question | data artifact | metric | uncertainty | caption draft.
4. Notation table for the method.
5. Anticipated reviewer objections and where in the paper each is answered.

{HONEST}`
        },
        get: {
          beginner: ["Outline with plain bullets", "Which section to write first"],
          researcher: ["Section plan + lengths", "Table/figure list", "Contribution bullets"],
          expert: ["Contribution → evidence map", "Word budget per section", "Notation table", "Objections → answers"]
        }
      },
      {
        title: "Draft with empty results", icon: "doc", chip: "You get: draft with empty tables", line: "Write everything except numbers. Tables and plots stay empty.",
        attach: "Same chat. Attach the writing-agent skill file and template if you have them.",
        attachB: "Nothing to attach.",
        prompts: {
          beginner: `Write a first draft of my paper using the outline above.
My idea: {A}

Rules:
- Write every section except the results.
- Make the results tables with column names but EMPTY cells.
- For each figure, write the caption and axis names, but no data.
- Write "[pending]" wherever a number will go.

{HONEST}`,
          researcher: `Draft the manuscript from the outline above for: {A}
Format: {B}

Write title, provisional abstract, introduction, related work, method, planned evaluation and limitations.
Results: table headers and row labels with blank cells; figure captions and axes with empty plot areas; mark "[pending]".
Keep expected effects as hypotheses, never as findings. Use only citations from the .bib.

{HONEST}`,
          expert: `Write a full pre-results manuscript for: {A}
Format: {B}

- Complete Introduction (problem, gap, contributions with forward references), Related Work, Method (with notation and any key equation and its assumptions), Experimental Protocol (datasets, splits, baselines at equal budget, metrics, statistical tests, what is frozen before testing).
- Results: every planned table with headers/rows and blank cells; every figure with caption, axes and units; all marked [pending].
- Limitations and threats to validity.
- Output LaTeX that compiles with the template; list anything that would not compile.

Hypotheses must stay hypotheses. {HONEST}`
        },
        get: {
          beginner: ["Draft of all sections", "Empty tables and figures", "[pending] where numbers go"],
          researcher: ["Full draft, results pending", "Blank tables + captions", "Only .bib citations"],
          expert: ["Compilable LaTeX", "Full experimental protocol", "Threats to validity"]
        },
        sample: `<table><caption>Table 1. Forecast error by day type (pending)</caption><thead><tr><th>Model</th><th>MAE normal days</th><th>MAE exam days</th></tr></thead><tbody><tr><td>Same-weekday baseline</td><td>[pending]</td><td>[pending]</td></tr><tr><td>Lag + calendar</td><td>[pending]</td><td>[pending]</td></tr></tbody></table><p class="hint">Sample, made up to show the format.</p>`
      },
      {
        title: "Check the plan", icon: "check", chip: "You get: a fixed plan with a date", line: "Catch weak spots before you write any code.",
        attach: "The draft from prompt 2.",
        attachB: "Nothing to attach.",
        prompts: {
          beginner: `Read my draft above like a teacher. My idea: {A}

1. Is anything unclear or missing in the method or experiments? List up to 5 problems in plain words.
2. Is any sentence claiming a result I don't have yet? Point to it.
3. Write my experiment plan as a short checklist with today's date: data, what I compare, what I measure.

{HONEST}`,
          researcher: `Audit the draft above before experiments start: {A}

1. Ranked list of gaps in method or evaluation (data split, baselines, metrics, leakage risk).
2. Any sentence that states an outcome as fact — quote it and rewrite it as a hypothesis.
3. A dated experiment plan in YAML: datasets, splits, baselines, metrics, seeds, statistical test, success criteria.

{HONEST}`,
          expert: `Pre-register the study described in the draft: {A}

1. Reviewer-style audit: identifiability of the main quantity, baseline fairness (same budget/information), leakage, multiple-comparison risk, power.
2. Pre-registration document: hypotheses (H1…), primary/secondary endpoints, analysis plan, exclusion rules, stopping rules, seeds, what counts as a null result.
3. A YAML experiment config the code agent can read directly.
4. List any decisions still open, with a recommended default.

{HONEST}`
        },
        get: {
          beginner: ["Up to 5 problems", "Sentences claiming results", "Dated checklist"],
          researcher: ["Ranked gaps", "Overclaims rewritten", "YAML experiment plan"],
          expert: ["Validity audit", "Pre-registration", "YAML config for code", "Open decisions"]
        }
      }
    ]
  },

  // ───────────────────────── 4. CODE ─────────────────────────
  {
    id: "code", nav: "4 · Code", title: "Write code → Fix errors → Check it",
    bLabel: "Language, environment and data",
    aHolder: "Paste the experiment plan (YAML or checklist) from step 3",
    bHolder: "e.g. Python 3.11, laptop, data/visits.csv and data/calendar.csv",
    exA: "Compare same-weekday baseline, lag model and lag + calendar model on a chronological split; MAE per day type",
    exB: "Python 3.11, pandas + scikit-learn, laptop, data/visits.csv, data/calendar.csv",
    loop: "A check failed? Use prompt 2 with the exact error, then re-run prompt 3. When the audit passes, go to step 5 (Results).",
    steps: [
      {
        title: "Write the first runnable version", icon: "code", chip: "You get: code that runs + a quick test", line: "Start with the simplest version that runs from start to end.",
        attach: "Experiment plan, a sample of your data (first 20 rows), and the code-agent skill file.",
        attachB: "Attach your plan and the first 20 rows of your data.",
        prompts: {
          beginner: `I need code for my experiment.
Plan: {A}
My setup: {B}

Write the simplest Python code that:
1. Loads my data.
2. Runs one simple baseline.
3. Prints the result and saves it to results.csv.
Explain how to run it, step by step, as if I have never used the terminal.
Add a tiny test I can run to check it works.

{HONEST}`,
          researcher: `Implement the smallest end-to-end experiment for this plan: {A}
Environment: {B}

- Config file (YAML), fixed seeds, explicit train/val/test split.
- Baseline first, then the proposed method behind a flag.
- Save predictions, metrics and the config with a run ID.
- Smoke test on a tiny subset, plus a leakage check.
- Exact setup and run commands.
Report only checks you actually ran.

{HONEST}`,
          expert: `Implement a reproducible research codebase for: {A}
Environment: {B}

Structure: src/ (data, methods, metrics, runner), configs/, tests/, scripts/. Requirements:
- Every method shares the same candidate set, information and budget; differences only in the decision logic.
- Deterministic seeding; run ID = hash of config + git commit; all outputs under runs/<id>/.
- Unit tests for metrics and split logic; a no-effect control that must produce ~zero advantage.
- Logging of assignment probabilities if any randomisation is used.
- One command to reproduce every table in the plan.
List what you executed and the exact output.

{HONEST}`
        },
        get: {
          beginner: ["Short Python file", "Step-by-step run guide", "Tiny test"],
          researcher: ["Config + seeds + splits", "Baseline + method", "Smoke test + leakage check"],
          expert: ["Full project structure", "Matched-budget baselines", "No-effect control test", "One-command reproduction"]
        }
      },
      {
        title: "Fix errors / update code", icon: "bug", chip: "You get: the fix + proof it works", line: "Paste the exact error. Get the smallest safe change.",
        attach: "The file(s) involved, the exact command you ran, and the full error message.",
        attachB: "Also paste your code and the full error message.",
        prompts: {
          beginner: `My code gave an error.
What I'm doing: {A}
My setup: {B}
Command I ran: [paste]
Error: [paste the full error]

Explain in plain words what went wrong, give me the fixed code, and tell me how to check it works now.

{HONEST}`,
          researcher: `Debug this. Context: {A}. Environment: {B}.
Command: [paste]
Error / unexpected output: [paste]

1. Root cause.
2. Smallest change (as a diff).
3. Re-run the relevant test and show the output.
4. Does the fix change any result already reported? Say yes/no and why.

{HONEST}`,
          expert: `Diagnose and fix. Context: {A}. Environment: {B}.
Command, error, and expected behaviour: [paste]

1. Reproduce, then give the root cause with evidence (stack trace line, failing assertion, data example).
2. Minimal diff; no refactors beyond the fix.
3. Regression test that fails before and passes after.
4. Impact analysis: which runs/tables are affected; whether the analysis plan changes (if so, log it as a deviation with date and reason).

{HONEST}`
        },
        get: {
          beginner: ["Plain-words cause", "Fixed code", "How to check"],
          researcher: ["Root cause", "Diff", "Re-run output", "Impact on results"],
          expert: ["Evidence-backed cause", "Minimal diff + regression test", "Deviation log entry"]
        }
      },
      {
        title: "Check the code before trusting it", icon: "check", chip: "You get: pass/fail checklist", line: "Check the code really does what the plan says.",
        attach: "The code (zip or repo link) and the experiment plan.",
        attachB: "Attach your code files.",
        prompts: {
          beginner: `Please check my code before I trust the results. Plan: {A}

Answer yes / no / not sure for each, with one line why:
1. Does the test data stay hidden during training?
2. Is the metric calculated correctly?
3. Do I get the same result if I run it twice?
4. Do all methods get the same data?

{HONEST}`,
          researcher: `Audit this code against the plan: {A}

Checklist (pass / fail / unclear + file:line evidence): split correctness, leakage, metric implementation, seeding/determinism, baseline fairness (same data and budget), saved config per run.
Then list fixes in priority order.

{HONEST}`,
          expert: `Run a pre-results code audit against the pre-registration: {A}

1. Plan-to-code trace: each planned item → file:line where it is implemented, or MISSING.
2. Validity checks: leakage, metric correctness vs a hand-computed example, determinism across 2 runs, budget parity, correct use of assignment probabilities.
3. Sanity results: no-effect control ≈ 0; oracle ≥ all methods; baseline in expected range.
4. Verdict: ready / not ready, with the blocking items.

{HONEST}`
        },
        get: {
          beginner: ["4 yes/no checks"],
          researcher: ["Pass/fail with file:line", "Priority fixes"],
          expert: ["Plan-to-code trace", "Sanity results", "Ready / not ready"]
        },
        sample: `<table><thead><tr><th>Check</th><th>Result</th><th>Evidence</th></tr></thead><tbody><tr><td>Test data hidden</td><td>✓ pass</td><td>split.py:42</td></tr><tr><td>Same result twice</td><td>✗ fail</td><td>seed not set in sampler.py:17</td></tr></tbody></table><p class="hint">Illustrative example made up for teaching.</p>`
      }
    ]
  },

  // ───────────────────────── 5. RESULTS ─────────────────────────
  {
    id: "results", nav: "5 · Results", title: "Tables & figures → Write results → Check numbers",
    bLabel: "Result files and run IDs",
    aHolder: "Short description of the paper (or paste the draft abstract)",
    bHolder: "e.g. runs/2026-11-10_a1/metrics.csv, runs/…/predictions.csv, config.yaml",
    exA: "Library visit forecasting paper; draft from step 3 with results pending",
    exB: "runs/main/metrics.csv, runs/main/predictions.csv, runs/ablation/*.csv",
    loop: "Audit found a mismatch? Fix the text or re-run the code, then audit again. When every claim traces to a file, go to step 6 (Review).",
    steps: [
      {
        title: "Make tables & figures", icon: "chart", chip: "You get: tables + plotting code", line: "Every number comes from a saved file, never typed by hand.",
        attach: "Your metrics/prediction CSV files and the draft's empty tables.",
        attachB: "Attach your result files (for example .csv) and your draft.",
        prompts: {
          beginner: `Here are my result files: {B}
Paper: {A}

1. Fill the empty tables in my draft using ONLY the numbers in these files.
2. Write Python code that makes each figure from the files.
3. Under each table, write which file each number came from.

{HONEST}`,
          researcher: `Build the planned tables and figures from these artifacts: {B}
Paper: {A}

- Tables in LaTeX (booktabs) with mean ± std over seeds where available.
- Plotting script that reads the files directly; one figure per planned question.
- A mapping: table cell → file, column, run ID.
- List any planned table/figure that cannot be filled yet.

{HONEST}`,
          expert: `Generate publication-grade tables and figures from: {B}
Paper: {A}

1. Script (not manual) that regenerates every table and figure from runs/; deterministic output names.
2. Tables: mean, uncertainty (CI or std, say which and n), best-method marking only where the difference is significant under the pre-registered test.
3. Figures: units, axis labels, consistent colours per method, colour-blind-safe, caption that states the takeaway and n.
4. Artifact map: every cell/point → file, run ID, seed set, metric definition.
5. Report null/negative results as planned — no dropping inconvenient runs.

{HONEST}`
        },
        get: {
          beginner: ["Filled tables", "Plotting code", "Where each number came from"],
          researcher: ["LaTeX tables with ± std", "Plot script", "Cell → file map"],
          expert: ["Regeneration script", "Significance-aware tables", "Captioned figures", "Full artifact map"]
        }
      },
      {
        title: "Write results & discussion", icon: "pen", chip: "You get: results section + new abstract", line: "Say exactly what the numbers show — no more, no less.",
        attach: "Same chat, with the tables and figures from prompt 1.",
        attachB: "Nothing to attach.",
        prompts: {
          beginner: `Using only the tables above, write the Results section of my paper: {A}

- One paragraph per table or figure: what it shows, in plain words.
- If our method did not win somewhere, say so honestly.
- Then update the Abstract and Conclusion to match.

{HONEST}`,
          researcher: `Write Results and Discussion for: {A}

- For each research question: the answer, the numbers, the uncertainty.
- Report null and negative results.
- Discussion: why, limitations, and what the results do NOT show.
- Update Abstract, Introduction contributions and Conclusion so they match the numbers exactly.

{HONEST}`,
          expert: `Write Results, Discussion and the revised front matter for: {A}

1. Results ordered by pre-registered hypotheses; for each: estimate, interval, test, decision (supported / not supported / inconclusive).
2. Mechanism evidence from ablations; robustness and where the method loses.
3. Deviations from the pre-registration, with reasons.
4. Discussion: scope of the claim, threats to validity, alternative explanations.
5. Rewrite Abstract and contribution bullets so every claim maps to a table/figure.

{HONEST}`
        },
        get: {
          beginner: ["Results in plain words", "Honest about losses", "Updated Abstract + Conclusion"],
          researcher: ["Answer per question", "Null results reported", "Matched Abstract"],
          expert: ["Hypothesis-by-hypothesis results", "Deviations section", "Claims → evidence"]
        }
      },
      {
        title: "Check every number", icon: "check", chip: "You get: number-by-number check", line: "Check each number in the text against the files.",
        attach: "The updated draft and the result files.",
        attachB: "Attach your draft and your result files.",
        prompts: {
          beginner: `Check my paper against my result files: {B}

Find every number in the text. For each one, tell me: where it is in the paper, which file it should come from, and whether it matches (✓ / ✗).
List anything that does not match.

{HONEST}`,
          researcher: `Audit all quantitative claims in the draft against: {B}

Table: location | claim | value in text | source file + run ID | value in file | match?
Then list claims that are overstated (e.g. "significantly" without a test) and how to fix them.

{HONEST}`,
          expert: `Full claim-to-artifact audit against: {B}

1. Every quantitative and comparative claim (text, abstract, captions, tables): location | claim | stated value | artifact | recomputed value | status (VERIFIED / MISMATCH / UNVERIFIABLE).
2. Language audit: causal or significance wording without matching analysis.
3. Selective-reporting check: planned analyses missing from the paper.
4. Fix list in priority order.

{HONEST}`
        },
        get: {
          beginner: ["Every number ✓/✗", "List of mismatches"],
          researcher: ["Claim-to-file table", "Overclaims + fixes"],
          expert: ["VERIFIED/MISMATCH table", "Wording audit", "Missing analyses"]
        },
        sample: `<table><thead><tr><th>Where</th><th>Claim</th><th>File</th><th>Match</th></tr></thead><tbody><tr><td>Abstract</td><td>"18% lower error on exam days"</td><td>runs/main/metrics.csv</td><td>✗ file says 14%</td></tr></tbody></table><p class="hint">Illustrative example made up for teaching.</p>`
      }
    ]
  },

  // ───────────────────────── 6. REVIEW ─────────────────────────
  {
    id: "review", nav: "6 · Review", title: "Review → Plan the fixes → Re-check",
    bLabel: "Target venue / review focus",
    aHolder: "Paper title (attach the full PDF in the chat)",
    bHolder: "e.g. a journal or conference name; focus on methods and evaluation",
    exA: "When the Calendar Breaks the Forecast: Event-Aware Library Visit Prediction",
    exB: "Short paper for an education-data workshop; focus on evaluation and claims",
    loop: "Some problems still not fixed? Fix them and run prompt 3 again. When every big problem is fixed, the paper is ready to submit.",
    steps: [
      {
        title: "Get a referee review", icon: "check", chip: "You get: problems, most serious first", line: "A tough reviewer reads the whole paper.",
        attach: "Your manuscript PDF (+ supplement). Use a Temporary chat if the paper is confidential. Optional: Beihang Referee skill.",
        attachB: "Attach your paper as a PDF. If it is private, use a temporary chat.",
        prompts: {
          beginner: `Please review my attached paper: {A}
It is for: {B}

Act as a fair reviewer. Give me:
1. A short summary of the paper (to check you understood it).
2. The 3 biggest problems, most important first. For each: where it is (page/section), why it matters, and how I can fix it.
3. 3 smaller problems.
4. Would you accept, ask for changes, or reject — and why?

{HONEST}`,
          researcher: `Review the attached manuscript "{A}" for {B}.

1. Summary and claimed contributions.
2. Major concerns, ranked. For each: evidence location (page/section), impact on the main claim, minimum sufficient fix, and a closure test (how we will know it is fixed).
3. Minor concerns.
4. Scores: novelty, soundness, clarity, significance (1–5) with one line each.
5. Recommendation and top 3 revision priorities.

List anything you could not verify. {HONEST}`,
          expert: `Act as Reviewer 2 for {B}. Review "{A}" (attached) to that venue's standard.

1. Summary in your own words; list contributions as the authors claim them.
2. Major issues (ID M1…): evidence location, why it threatens validity or novelty, minimum fix, closure test. Must cover: novelty vs the last 2 years, baseline fairness, statistical validity, whether claims exceed evidence, reproducibility.
3. Minor issues (ID m1…).
4. Questions for the authors.
5. Score card (venue scale) and confidence.
6. The single issue most likely to cause rejection.

Distinguish missing evidence from demonstrated errors. {HONEST}`
        },
        get: {
          beginner: ["Summary", "3 big + 3 small problems with fixes", "Accept / changes / reject"],
          researcher: ["Ranked major concerns + closure tests", "Scores 1–5", "Top 3 priorities"],
          expert: ["M1…/m1… issue IDs", "Questions for authors", "Score card + confidence", "Main rejection risk"]
        },
        sample: `<dl class="review-example"><dt>Evidence</dt><dd>Page 1, Methods. Students chose whether to receive a reminder.</dd><dt>Concern</dt><dd>Self-selection weakens the causal claim.</dd><dt>Fix</dt><dd>Report the association and state the design limitation.</dd><dt>Closure test</dt><dd>Abstract, results and conclusion only claim what the design supports.</dd></dl><p class="hint">From the site's practice manuscript.</p>`
      },
      {
        title: "Plan the fixes", icon: "list", chip: "Sample result: 5.5 → 7.5 / 10", line: "Turn the review into a clear list of fixes.",
        attach: "Same chat as the review, plus your manuscript (PDF or LaTeX/Word source).",
        attachB: "Nothing new to attach.",
        prompts: {
          beginner: `Help me fix my paper "{A}" using the review above. It is for: {B}

Rule: do not fix problems by adding bigger claims. Prefer making claims narrower and more exact.

1. Make a table: problem | how to fix it | how important (critical / high / medium).
2. For each critical problem: explain in plain words what is wrong, give a small example of how it could fail, and tell me exactly what to change.
3. For any claim that is too strong: show me "Don't say: …" and "Say instead: …".
4. List new experiments I need, smallest first.
5. Tell me my score now and what it could be after the fixes (out of 10), and why.

{HONEST}`,
          researcher: `Turn the review above into a revision plan for "{A}" ({B}).
Principle: narrow claims and strengthen evidence; do not answer reviewers by adding claims.

1. Verdict: can the paper be made strong? Current vs expected score (/10), with the honest caveat.
2. Priority revision map: current weakness | concrete solution | importance | likely effect. Mark which items are corrections (must fix) vs extensions.
3. One section per critical/high item: the problem (with a concrete failure example), the best solution (method, algorithm or proof change), and the rewritten claim ("Do not say … / Say …").
4. Baseline fairness fixes: for each baseline, is the comparison fair (same information, budget, inference type)? How to fix it.
5. Experiments to add: more settings/datasets, one real or hardware/real-data test if relevant, and the metrics to report.
6. Score table: dimension | current | after strong revision.

{HONEST}`,
          expert: `Act as a senior reviewer helping the authors of "{A}" ({B}) turn the review above into a strong revision.
Principle: do not solve the review by adding claims — narrow claims, repair the theory, then add experiments that validate the repaired guarantees.

Write exactly these parts:
1. Opening verdict (2–3 sentences): can it be made substantially stronger, and current → expected score (/10), without promising a journal outcome.
2. Priority revision map — table: current weakness | concrete solution | importance | likely effect. State which items are mathematical/methodological corrections, not optional extensions.
3. One numbered section per weakness, most dangerous first. Each section: (a) why it breaks the current claim, with a concrete counterexample or attack; (b) the best solution, with equations, assumptions or algorithm changes written out; (c) an even better version if one exists (turn the weakness into a contribution); (d) the rewritten claim as "Do not say: … / Say: …".
4. Redesigned main results: the sequence of theorems/propositions the paper should prove, as a chain from assumptions to the final guarantee.
5. Baseline fairness: a 2×2 or similar table separating the effect of each ingredient; rename or faithfully implement any "X-style" baseline.
6. External validity: broader synthetic families with the metrics to report and an expected scaling law; one real/hardware/HIL experiment with the overheads to measure; delayed or long-horizon effects if relevant.
7. Narrowed central claim — the exact sentence to lead the paper with, and the scope the negative/impossibility result should quantify over.
8. Revised architecture — components in order, each with its single responsibility.
9. Score table: dimension | current | after strong revision, and a closing chain: assumption → estimator → inference → global guarantee → executed action.

Use LaTeX for equations. Base every weakness on the manuscript (cite section/equation/algorithm). {HONEST}`
        },
        get: {
          beginner: ["Problem → fix table", "Plain-words fixes", "Don't say / Say instead", "Score now vs after"],
          researcher: ["Priority revision map", "Fix per weakness + rewritten claim", "Fair-baseline fixes", "Current vs after score table"],
          expert: ["Verdict + priority map", "Numbered fixes with equations", "Redesigned theorem chain", "Architecture + score table"]
        },
        example: {file: "demo/sample-review-revision-plan.md", label: "See a sample answer: revision plan 5.5 → 7.5/10", note: "Made-up sample to show the format (the site's practice manuscript)."}
      },
      {
        title: "Re-check & write the reply", icon: "mail", chip: "You get: fixed / not fixed + reply letter", line: "After you revise: check each fix, then draft the response letter.",
        attach: "Original review, the revision plan, and your revised manuscript.",
        attachB: "Attach your updated paper.",
        prompts: {
          beginner: `Here is the original review, my revised paper "{A}", and the fix plan above.

1. For each problem in the original review, tell me: fixed ✓, partly fixed △, or not fixed ✗ — and why.
2. Did my changes create any new problems?
3. Write a polite reply to the reviewer for each problem: what I changed and where (page/section).

{HONEST}`,
          researcher: `Verify the revision of "{A}" ({B}).

1. Matrix: issue ID | author action | evidence location in revised paper | closure test | status (OPEN / PARTIAL / VERIFIED CLOSED).
2. New issues introduced by the revision, and remaining work before submission.
3. Response letter: quote each reviewer point, reply, and point to the changed location.

{HONEST}`,
          expert: `Act as the same reviewer on the revised "{A}" for {B}.

1. Closure matrix for every original issue and every item in the revision map: action, revised location, whether the closure test is met, status (OPEN / PARTIAL / VERIFIED CLOSED), evidence still missing.
2. Theorem-to-claim alignment check: does every claim in the abstract/intro now match exactly what is proved or shown?
3. New major issues introduced by the revision.
4. Updated score table vs the first round.
5. Point-by-point response letter: reviewer text, response, manuscript location, new evidence; firm but courteous where disagreeing.
6. Submission readiness: ready / one more round, and the blocking items.

{HONEST}`
        },
        get: {
          beginner: ["✓ / △ / ✗ per problem", "New problems", "Polite replies"],
          researcher: ["Closure matrix", "Remaining work", "Response letter"],
          expert: ["Full closure matrix", "Claim alignment check", "Updated scores + letter", "Ready / not ready"]
        }
      }
    ]
  }
];
