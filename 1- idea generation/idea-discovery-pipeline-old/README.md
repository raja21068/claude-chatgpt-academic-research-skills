# Idea Discovery Pipeline v3.1

An automated research idea discovery system. Feed it papers, get back novel research ideas — clustered, gap-analyzed, conflict-checked, novelty-verified, and ranked.

## What it does

```
Papers (PDF/TXT/MD)
  → Structured extraction (Claude API)
  → Embedding clustering (SPECTER2 + HDBSCAN)
  → Knowledge graph (NetworkX)
  → Conflict detection
  → Gap analysis (graph queries + LLM)
  → Idea generation (gap-driven, no gap = no idea)
  → Novelty verification (multi-source + optional multi-model)
  → Interactive dashboard (Chart.js)
```

## Quick start

```bash
# 1. Clone and enter
cd idea-discovery-pipeline

# 2. Set your API key
cp .env.example .env
# Edit .env → add ANTHROPIC_API_KEY

# 3. Add papers
# Drop PDF/TXT/MD files into input_papers/

# 4. Run
chmod +x run.sh
./run.sh
```

Results land in `output/`:
- `FINAL_REPORT.md` — human-readable summary
- `dashboard.html` — interactive visualization
- All intermediate JSON files

## Run modes

```bash
./run.sh                      # Full pipeline (all features)
./run.sh --lite               # Fast mode (no embeddings, no quality checks)
./run.sh --checkpoint         # Pause after gaps for human review
./run.sh --resume             # Resume from human-reviewed checkpoint
./run.sh --skip-embeddings    # Skip ML deps (LLM-only clustering)
./run.sh --no-quality         # Skip quality gate checks
./run.sh --dashboard-only     # Regenerate dashboard from existing data
```

## Pipeline steps

| Step | Script | What it does |
|------|--------|-------------|
| 1 | `step1_ingest.py` | Extract structured records from papers (problem, method, claims, limitations) |
| 2 | `step2_cluster.py` | Hybrid clustering: SPECTER embeddings + knowledge graph + LLM interpretation |
| 3 | `step3_conflicts.py` | Detect contradictions between papers |
| 4 | `step4_gaps.py` | Find structural gaps scored by Impact × Feasibility × Novelty |
| — | *checkpoint* | Optional human review (approve/reject/add gaps) |
| 5 | `step5_ideas.py` | Generate ideas from gaps (iron rule: no gap = no idea) |
| 6 | `step6_novelty.py` | Verify via Semantic Scholar + arXiv + citation graph + optional multi-model |
| 7 | `step7_report.py` | Compile FINAL_REPORT.md |
| 8 | `step8_dashboard.py` | Generate interactive HTML dashboard |

Quality gates run between steps 1→2, 2→3, and after step 5.

## New in v3.1

### Real embeddings (SPECTER2 + HDBSCAN)
Papers are embedded into vector space using sentence-transformers. Clustering uses HDBSCAN instead of LLM guessing. The LLM's role shifts to naming and interpreting the mathematically-found clusters.

### Knowledge graph (NetworkX)
Papers, methods, problems, datasets, and claims become nodes with typed edges. Gap detection becomes graph queries ("find method nodes with no edge to problem P3") instead of asking an LLM to spot patterns in JSON.

### Quality gates
- **Ingestion check**: validates extracted fields, catches duplicates and inconsistencies
- **Cluster critique**: devil's advocate challenges whether clusters and gaps are real
- **Reviewer simulation**: simulates peer review of generated ideas (scores 1-10)

### Human checkpoint
After gap detection, the pipeline saves a YAML file. The researcher can approve/reject gaps, re-prioritize, and add their own. The pipeline continues from the edited gaps.

### Multi-model novelty verification
Optionally queries Claude + GPT-4 + Gemini independently, then takes conservative consensus. Catches blind spots from any single model.

### Citation graph expansion
Goes beyond keyword search: finds papers-that-cite-papers-that-cite via Semantic Scholar API. Catches indirect prior work that standard search misses.

### Interactive dashboard
Self-contained HTML with Chart.js. Includes paper scatter plot (UMAP projection), method×problem heatmap, idea cards with novelty verdicts, gap rankings.

## Configuration

Edit `config/settings.json`:

```json
{
  "embeddings": { "enabled": true },
  "knowledge_graph": { "enabled": true },
  "quality_gates": { "enabled": true },
  "multi_model": { "enabled": false },
  "citation_expansion": { "enabled": true },
  "dashboard": { "enabled": true }
}
```

### Multi-model setup

1. Set `multi_model.enabled: true` in config
2. Add API keys to `.env`:
   ```
   OPENAI_API_KEY=sk-...
   GOOGLE_API_KEY=...
   ```
3. Uncomment `openai` and/or `google-generativeai` in `requirements.txt`

Falls back gracefully to Claude-only if keys aren't set.

## Output files

| File | Description |
|------|-------------|
| `paper_corpus.json` | Structured paper records |
| `embeddings.json` | Paper vectors + 2D coordinates + cluster labels |
| `embeddings.npy` | Raw embedding matrix (numpy) |
| `graph_data.json` | Knowledge graph (D3-ready nodes + edges) |
| `graph_stats.json` | Graph statistics |
| `graph_gaps.json` | Structural gaps from graph queries |
| `research_space_map.json` | Cluster analysis + cross-matrices |
| `cluster_report.md` | Readable cluster report |
| `conflict_report.json/md` | Detected contradictions |
| `gap_analysis.json` | Scored gaps |
| `gap_report.md` | Readable gap report |
| `CHECKPOINT_REVIEW.yaml` | Human review checkpoint (if `--checkpoint`) |
| `idea_report.json/md` | Generated ideas |
| `novelty_report.json/md` | Novelty verdicts |
| `quality_*.json` | Quality gate results |
| `FINAL_REPORT.md` | Complete summary |
| `dashboard.html` | Interactive dashboard |
| `pipeline_summary.json` | Timing and metadata |

## Architecture

```
scripts/
├── utils.py               Shared: API client, file I/O, logging
├── embedding_engine.py     SPECTER/MiniLM embeddings + HDBSCAN + UMAP
├── knowledge_graph.py      NetworkX entity graph + gap queries
├── quality_gate.py         Self-critique + human checkpoint
├── multi_model.py          Claude + GPT-4 + Gemini consensus
├── citation_graph.py       Semantic Scholar citation traversal
├── step1_ingest.py         Paper → structured JSON
├── step2_cluster.py        Hybrid clustering (embeddings + graph + LLM)
├── step3_conflicts.py      Cross-paper contradiction detection
├── step4_gaps.py           Gap detection + scoring
├── step5_ideas.py          Gap-driven idea generation
├── step6_novelty.py        Multi-source novelty verification
├── step7_report.py         Final report compilation
├── step8_dashboard.py      Interactive HTML dashboard
└── run_pipeline.py         Orchestrator with quality gates
```

## Dependencies

**Core** (always required): anthropic, requests, PyYAML, PyMuPDF

**ML** (skip with `--skip-embeddings`): sentence-transformers, numpy, scikit-learn, hdbscan, umap-learn

**Graph**: networkx

**Optional**: openai, google-generativeai (for multi-model)

## Tips

- Start with `--lite` for a fast first run, then add features
- The human checkpoint (`--checkpoint`) is where domain expertise makes the biggest difference
- Citation expansion catches 20-40% more relevant prior work than keyword search alone
- If you're getting rate-limited on Semantic Scholar, reduce `citation_expansion.max_papers_per_hop` in config
- The dashboard works offline — just open the HTML file in any browser
