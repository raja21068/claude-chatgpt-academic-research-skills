const repo = "https://github.com/raja21068/claude-chatgpt-academic-research-skills";
const github = (path, mode = "tree") => repo + "/" + mode + "/main/" + path.split("/").map(encodeURIComponent).join("/");
const release = (path) => ({label: "Download skill ZIP", url: github(path, "raw")});
const stages = [
  {
    id: "idea", title: "Turn a broad interest into a question you can test", nav: "Research idea", intro: "Turn a broad interest into a question you can answer with the data, time, and tools you have.",
    skill: "Idea Discovery V5",
    links: [{label:"Follow the worked idea lesson",url:"cases.html#idea-case"},release("1- idea generation/idea-discovery-v5.zip"), {label: "Read the setup instructions", url: github("1- idea generation/Instrucations.txt","blob")}],
    inputs: ["A topic or practical problem", "Available data, time, and computing resources", "Optional seed papers or notes"],
    steps: ["Unzip the skill and look for its SKILL.md and setup instructions. The repository’s documented corpus mode uses run.sh on your paper PDFs and produces SESSION.md.", "For a first brainstorming pass, open ChatGPT or Claude, attach the skill instructions and any seed papers or SESSION.md you have, then paste your prompt.", "Pick one question and save it with its hypothesis, smallest viable test, and biggest uncertainty."],
    output: "One-page idea brief", check: "You can name a data source, a comparison, and a result that would challenge your hypothesis. The novelty claim stays provisional until Stage 2.",
    fields: ["Topic or problem", "Time, data and resource constraints"],
    example: ["Can a simple model predict next-day campus library visits?", "Four weeks; public daily counts if available; laptop only."],
    tasks: [
      {name:"Generate testable ideas", body:"Propose three research questions. For each, give a testable hypothesis, plausible data source, simplest baseline, primary metric and one failure case. Compare feasibility and choose one to investigate. State which claims need literature verification."},
      {name:"Score one idea", body:"Score the idea using these weights: importance 15, evidence for the gap 15, novelty 20, scientific insight 15, feasibility 10, impact 10, evaluation 10 and reproducibility 5. Give evidence and uncertainty for each score. End with the smallest decisive test."}
    ]
  },
  {
    id: "literature", title: "Find out if anyone already did it", nav: "Literature search", intro: "Find the closest work, test your proposed contribution, and revise the question if the evidence calls for it.",
    skill: "Paper Finder",
    links: [{label:"Open the Paper Finder guide",url:github("16-Paper-Finder-Search (Input 1 Paper + List of Your Favourite Journals )/paper-finder/paper-finder/README.md","blob")},{label:"Browse Paper Finder files",url:github("16-Paper-Finder-Search (Input 1 Paper + List of Your Favourite Journals )/paper-finder/paper-finder")}],
    inputs: ["The idea brief from Stage 1", "Seed papers, DOIs, or preferred venues", "Access to a literature database or supplied PDFs"],
    steps: ["Paste your selected idea into the prompt builder. Add any paper URLs or DOIs you already have.", "For a guided search, attach your seed papers and use a chat with web search enabled. For the Python route, follow Paper Finder’s guide to resolve venues and search OpenAlex.", "Open the closest sources yourself and verify what each paper actually did. Save the search log, shortlist, and novelty matrix."],
    output: "Verified bibliography and novelty matrix", check: "Each comparison in the matrix points to a paper you checked. Record whether the idea should proceed, narrow, or change.",
    fields: ["Selected idea or hypothesis", "Search scope, dates and preferred venues"],
    example: ["Compare a simple next-day library attendance forecast against a same-weekday baseline.", "Search library footfall and building occupancy forecasting. Include older baseline studies."],
    tasks: [
      {name:"Find and compare papers",body:"Generate search queries using synonyms for the mechanism, task and outcome. Search the available sources. For each close paper, report title, year, DOI or source URL, method, dataset, limitations and what was actually checked. Log databases, queries and dates. If browsing is unavailable, return a search plan and analyze only supplied papers."},
      {name:"Challenge the novelty",body:"Look for papers using the same mechanism under other terms or in adjacent domains. Compare the 3–5 closest verified papers in a novelty matrix with evidence per cell. Identify the closest competitor and any rejection-level flaw. Recommend proceed, narrow, or change, and say what evidence would alter that decision."}
    ]
  },
  {
    id: "draft", title: "Write the paper before you have results", nav: "First manuscript draft", intro: "Write the research question and planned methods. Set up the tables and figures before you run the experiment.",
    skill: "Paper Writing Agent V2",
    links: [release("3- paper-writing/1.paper-writing-agent-V2.zip"),{label:"Open the paper-writing folder",url:github("3- paper-writing")}],
    inputs: ["Revised idea and verified literature", "Planned dataset, baselines, split and metrics", "Optional venue template or writing sample"],
    steps: ["Unzip the writing agent and attach its instruction file with your idea brief, bibliography, and methods plan.", "Ask for a manuscript skeleton with an introduction, related work, planned methods, and evaluation plan. Ask for table headers and figure captions or axes with blank result cells and empty plot areas.", "Save the draft and freeze a dated experiment plan. Keep anticipated outcomes explicitly labeled as hypotheses."],
    output: "Manuscript skeleton and dated experiment plan", check: "Every Results table and plot is marked pending. The planned comparisons, metrics, and data split are explicit.",
    fields: ["Research question and proposed method", "Venue, format and planned comparisons"],
    example: ["Predict next-day attendance from lagged counts and weekday. Compare with the same weekday from the previous week.", "Markdown draft; chronological split; MAE and a residual plot."],
    tasks: [
      {name:"Draft with empty tables and figures",body:"Create a manuscript skeleton with a working title, provisional abstract, introduction, related work, planned methods, evaluation plan, Results pending, and limitations. Use verified sources only. Give blank table cells and empty figure placeholders with labels, axes or captions. Include no invented observations, effect sizes, results claims or plots."},
      {name:"Specify tables and figures",body:"List each planned table and figure, its research question, required data artifact, metric, units, uncertainty summary and proposed caption. Leave all quantitative values and plot areas empty. Flag missing evaluation details and save a dated experiment plan."}
    ]
  },
  {
    id: "code", title: "Get code that runs, then check it", nav: "Code and experiments", intro: "Build the smallest runnable experiment, inspect its outputs, and improve the code with recorded changes.",
    skill: "Research Code Agent V5",
    links: [release("2- code generation/research-code-agent-v5.zip"),{label:"Open the code generation folder",url:github("2- code generation")}],
    inputs: ["Dated experiment plan and data access details", "Existing code or an empty project folder", "For updates, the failing command, error, or run log"],
    steps: ["Extract the agent. Open your project in your coding environment and provide the agent instructions, experiment plan, and existing files if you have them.", "Generate the simplest baseline first. Review the code, run a small smoke test, and confirm that splits, metric calculations, and output files match the plan.", "When something breaks, switch to the update prompt and include the exact command and error. Save the change, rerun checks, and record the code version, configuration, data version and run outputs."],
    output: "Reproducible code, run log, and results files", check: "A clean run produces traceable metrics. If code or analysis changed after seeing outcomes, log the change and distinguish exploratory runs.",
    fields: ["Experiment plan or repository context", "Environment, failing command or requested change"],
    example: ["Read daily attendance from CSV. Run a same-weekday baseline and compare it to a simple lag-based model.", "Python on CPU. Keep a chronological holdout and save predictions plus metrics."],
    tasks: [
      {name:"Write the first runnable version",body:"Implement the smallest end-to-end experiment with a baseline, reproducible configuration, explicit data split, metric computation, and saved predictions. Give exact setup and run commands. Add a smoke test and leakage checks. Report actual test outcomes only for commands you executed."},
      {name:"Update or debug existing code",body:"Reproduce the reported error if the environment allows it. Identify the root cause and propose the smallest defensible code change. Preserve the planned analysis unless a change is scientifically necessary. Rerun relevant checks and report the diff, command, outcome and remaining uncertainty."}
    ]
  },
  {
    id: "results", title: "Fill the paper with numbers you can trace", nav: "Results and figures", intro: "Generate tables and figures from saved outputs, then update the manuscript so its claims match the experiment.",
    skill: "Paper Writing Agent V2",
    links: [release("3- paper-writing/1.paper-writing-agent-V2.zip"),{label:"Browse figure-generation skills",url:github("8-Paper-Figure-Generation")}],
    inputs: ["The manuscript skeleton", "Metrics, predictions, and experiment logs", "Plotting scripts, configuration, and code version"],
    steps: ["Give the writing skill your draft and real run artifacts. Map every planned table row and figure to its source file and run ID.", "Regenerate tables and plots with code, then update the Results, Abstract, Discussion, and Limitations. Report null or negative results where relevant.", "Spot-check numbers against the source files and keep incomplete analyses marked pending."],
    output: "Results-backed manuscript and artifact map", check: "Every quantitative claim can be traced to a recorded run and checked against the corresponding artifact.",
    fields: ["Draft sections or artifact filenames", "Run IDs and comparisons to report"],
    example: ["draft.md, metrics.csv, predictions.csv and run_config.yaml", "Use baseline and model runs on the same chronological holdout. Leave missing analyses pending."],
    tasks: [
      {name:"Write results from actual runs",body:"Build tables and figures from the supplied run artifacts. Map each value to a file, run ID, split and metric. Update the abstract, results and limitations with evidence-backed language. Report uncertainty when supported. Keep missing results pending and avoid selective reporting."},
      {name:"Audit claims and artifacts",body:"Audit each quantitative claim in the draft against the saved predictions, metrics or logs. Return a claim-to-artifact table with location, value, source file, run ID and discrepancy. Identify claims that require correction or remain unverified."}
    ]
  },
  {
    id: "review", title: "Find the weak points before a reviewer does", nav: "Review and revision", intro: "Get an evidence-based critique, fix major issues, and check whether each revision resolves the original concern.",
    skill: "Beihang Referee",
    links: [{label:"Follow the worked review lesson",url:"cases.html#review-case"},{label:"Try the practice walkthrough",url:"#how-to"},{label:"Open the Beihang Referee guide",url:github("20- Paper Review Agent/README.md","blob")},release("20- Paper Review Agent/Beihang-Referee.zip"),{label:"Read the teaching example",url:github("20- Paper Review Agent/Example/Example_Review_Report.md","blob")}],
    inputs: ["Current manuscript PDF and relevant supplements", "Target venue or review focus", "For re-review, original report and revised manuscript"],
    steps: ["Follow the practice walkthrough for the chat route. Attach your manuscript and review instructions, then paste the review prompt. For the full Python workflow, extract the ZIP and follow the Referee guide.", "Verify the report’s page or section anchors and prioritize issues that could change the conclusion.", "Revise the manuscript, then use the follow-up prompt with the original report and revised files. Save a response matrix and repeat until major concerns are resolved or explicitly acknowledged."],
    output: "Referee report and revision-closure matrix", check: "Each major issue has a response, an evidence location, and a closure status. Check venue policies before sharing a confidential manuscript with an AI service.",
    fields: ["Manuscript or revised files", "Target venue, review focus or previous concerns"],
    example: ["manuscript.pdf and supplement.pdf", "Review methods, result traceability and scope of claims."],
    tasks: [
      {name:"Run the first review",body:"Produce a field-aware referee report grounded in the supplied manuscript. Rank major and minor concerns. For each major concern provide a verified page or section anchor, why it matters, the minimum sufficient fix, and a closure test. Label any check you could not verify. End with the top revision priorities."},
      {name:"Check the revisions",body:"For every original review concern, compare the revised manuscript and response. Create a matrix with issue ID, author action, evidence location, closure test and status (OPEN, PARTIAL or VERIFIED CLOSED). Explain what evidence remains missing and surface new issues introduced by the revision."}
    ]
  }
];
