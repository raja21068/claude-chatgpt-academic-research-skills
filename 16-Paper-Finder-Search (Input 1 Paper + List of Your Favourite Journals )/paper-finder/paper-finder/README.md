# paper-finder

A Claude skill for discovering **high-quality, peer-reviewed** research papers from a curated list of journals and conferences. Built around OpenAlex source IDs (not fuzzy venue strings) with LLM-driven query expansion and relevance re-ranking.

Pairs naturally with the `paper-writing-agent` skill — outputs feed straight into its literature-review phases.

---

## Quickstart

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

Only `requests` is strictly required. `anthropic` is optional (for the automated re-rank mode).

### 2. Edit your venue list

Open `inputs/venues.csv` and replace the sample rows with venues you trust. The file just needs a `Name` column.

### 3. Resolve venues to OpenAlex source IDs (one-time)

```bash
python scripts/resolve_venues.py
```

Inspect `inputs/venue_map.json` afterwards — the script flags ambiguous matches. Fix any wrong ones by editing the JSON directly (the `alternates` field lists other candidates).

### 4. Write your research topic and queries

Create `$out/queries.json`:

```json
{
  "topic": "node classification on heterophilic graphs",
  "queries": [
    "node classification heterophilic graphs",
    "graph neural network heterophily",
    "non-homophilous graph learning",
    "message passing heterophily",
    "graph attention heterophilic"
  ]
}
```

If you're using this skill **inside Claude**, ask Claude to expand your topic into queries first — see `SKILL.md` Stage 1 for the recipe.

### 5. Run the pipeline

```bash
# Stage 2: search OpenAlex
python scripts/search_openalex.py

# Stage 3: re-rank candidates by relevance
# Option A — automated (needs ANTHROPIC_API_KEY in env)
python scripts/rerank.py --api

# Option B — batch mode (writes prompts for Claude to process in-chat)
python scripts/rerank.py --batches
#   ... Claude scores each batch, you save responses to $out/rerank_responses/
python scripts/rerank.py --merge

# Stage 4 (optional): expand via citation graph
python scripts/expand_citations.py

# Stage 5: export BibTeX + CSV
python scripts/export_bibtex.py
```

Or run all stages at once:

```bash
python scripts/run_pipeline.py
```

### 6. Use the outputs

- `$out/final.bib` — BibTeX file, drop into your paper draft
- `$out/final.csv` — human-readable ranked table
- `$out/summary.md` — thematic clusters and coverage notes (generate in-chat with Claude)

---

## Files

```
paper-finder/
├── SKILL.md                       Claude-facing skill instructions
├── README.md                      this file
├── requirements.txt
├── inputs/
│   ├── venues.csv                 your curated venue list
│   └── venue_map.json             cached venue → source_id mapping (generated)
├── scripts/
│   ├── resolve_venues.py          Stage 0
│   ├── search_openalex.py         Stage 2
│   ├── rerank.py                  Stage 3
│   ├── expand_citations.py        Stage 4
│   ├── export_bibtex.py           Stage 5
│   └── run_pipeline.py            orchestrator
└── $out/                          all generated outputs land here
    ├── queries.json
    ├── candidates.jsonl
    ├── ranked.jsonl
    ├── final.bib
    ├── final.csv
    └── summary.md
```

---

## Configuration

Edit the constants at the top of each script, or set environment variables:

| Variable | Purpose | Default |
|---|---|---|
| `OPENALEX_MAILTO` | Your email — puts you in OpenAlex's polite pool (higher rate limits) | none |
| `ANTHROPIC_API_KEY` | Required only for `rerank.py --api` mode | none |
| `MIN_YEAR` | Earliest publication year to include | 5 years ago |
| `MIN_RELEVANCE` | Re-rank threshold for inclusion in final pool | 6 |

---

## Notes

- **No arXiv-only preprints** — the OpenAlex query filters `has_doi:true`, which is a reliable proxy for peer-reviewed publication.
- **OpenAlex polite pool** — adding a `mailto:` in the User-Agent gets you 10 req/s with no API key. Be a good citizen.
- **Citations as a signal** — used only for tiebreaks. Citation count rewards age more than quality; the LLM relevance score is the primary ranking signal.
