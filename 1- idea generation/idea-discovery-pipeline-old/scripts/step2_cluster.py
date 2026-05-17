"""
step2_cluster.py — Research Space Clustering (v2 — Hybrid)
Phase A: SPECTER/MiniLM embeddings → HDBSCAN → 2D UMAP
Phase B: Knowledge graph construction
Phase C: LLM interprets & names clusters, validates graph gaps
Outputs: output/research_space_map.json, output/embeddings.json,
         output/graph_data.json, output/cluster_report.md
"""

import sys, json, numpy as np
from pathlib import Path
from collections import defaultdict
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from utils import (ClaudeClient, load_config, load_json, save_json,
                   save_markdown, log, print_banner)

SYSTEM_PROMPT = """You are a research clustering agent. You are given:
1. Papers with their method/problem/dataset fields
2. Pre-computed embedding clusters (from HDBSCAN on SPECTER vectors)
3. Graph-detected structural gaps (from a knowledge graph)

Your job: INTERPRET and NAME the clusters, build cross-dimensional analysis,
and validate/augment the graph-detected gaps.

RESPOND WITH ONLY valid JSON — no markdown fences, no explanation.

Output this JSON:
{
  "method_clusters": [
    {"cluster_id":"M1","embedding_cluster":0,"label":"descriptive label",
     "category":"broad category","paper_ids":["id1"],"paper_count":5,
     "year_range":[2022,2025],"trend":"growing|stable|declining",
     "key_methods":["method names"],"coherence_note":"Are papers genuinely similar?"}
  ],
  "problem_clusters": [
    {"cluster_id":"P1","label":"label","domain":"domain","paper_ids":["id1"],
     "paper_count":3,"key_problems":["descriptions"]}
  ],
  "dataset_clusters": [
    {"cluster_id":"D1","label":"family","datasets":["ds1"],"paper_ids":["id1"],
     "paper_count":4,"overused":true}
  ],
  "metric_clusters": [
    {"cluster_id":"R1","label":"family","metrics":["m1"],"paper_ids":["id1"],"paper_count":6}
  ],
  "cross_matrix_method_problem": {
    "M1_P1":{"count":3,"paper_ids":["p1","p2","p3"]},
    "M1_P2":{"count":0,"paper_ids":[]}
  },
  "sparse_regions": [
    {"cell":"M2_P3","method_cluster":"label","problem_cluster":"label",
     "paper_count":0,"is_valid_gap":true,"reason":"why"}
  ],
  "dense_regions": [
    {"cell":"M1_P1","method_cluster":"label","problem_cluster":"label",
     "paper_count":12,"saturation_risk":true}
  ],
  "graph_gap_validation": [
    {"graph_gap_index":0,"valid":true,"reason":"why valid or not"}
  ],
  "orphan_methods":[],"orphan_problems":[],
  "dataset_monocultures":[],"metric_deserts":[],
  "trend_analysis":{"growing":[],"declining":[],"emerging":[]}
}

Rules:
- Use embedding clusters as STARTING POINT, refine with domain knowledge
- If an embedding cluster mixes different things, SPLIT it
- Validate each graph-detected gap: real opportunity or impossible combination?
- Every paper must appear in at least one cluster per dimension
"""

def prepare_paper_summaries(papers):
    summaries = []
    for p in papers:
        if "_error" in p: continue
        summaries.append({
            "paper_id": p.get("paper_id","unknown"), "title": p.get("title",""),
            "year": p.get("year"), "method": p.get("method",{}),
            "problem": p.get("problem",{}),
            "datasets": [d.get("name","") for d in p.get("datasets",[])],
            "metrics": [m.get("name","") for m in p.get("metrics",[])],
        })
    return json.dumps(summaries, indent=1, ensure_ascii=False)

def generate_cluster_report(space_map, embedding_data=None, graph_stats=None):
    lines = ["# Research Space Clustering Report (v2 — Hybrid)\n"]
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    if embedding_data:
        lines.append("## Embedding analysis\n")
        lines.append(f"- Model: {embedding_data.get('model','?')}")
        lines.append(f"- Papers: {embedding_data.get('n_papers',0)}, Clusters: {embedding_data.get('n_clusters',0)}, Noise: {embedding_data.get('n_noise',0)}")
    if graph_stats:
        lines.append("\n## Knowledge graph\n")
        lines.append(f"- Nodes: {graph_stats.get('total_nodes',0)}, Edges: {graph_stats.get('total_edges',0)}")
        for nt, c in graph_stats.get("node_types",{}).items():
            lines.append(f"  - {nt}: {c}")
    lines.append("\n## Method clusters\n")
    lines.append("| ID | Label | Papers | Trend |")
    lines.append("|-----|-------|--------|-------|")
    for mc in space_map.get("method_clusters",[]):
        lines.append(f"| {mc['cluster_id']} | {mc['label']} | {mc['paper_count']} | {mc.get('trend','-')} |")
    lines.append("\n## Problem clusters\n")
    lines.append("| ID | Label | Papers |")
    lines.append("|-----|-------|--------|")
    for pc in space_map.get("problem_clusters",[]):
        lines.append(f"| {pc['cluster_id']} | {pc['label']} | {pc['paper_count']} |")
    mc_ids = [mc["cluster_id"] for mc in space_map.get("method_clusters",[])]
    pc_ids = [pc["cluster_id"] for pc in space_map.get("problem_clusters",[])]
    if mc_ids and pc_ids:
        lines.append("\n## Method × Problem matrix\n")
        lines.append("| | " + " | ".join(pc_ids) + " |")
        lines.append("|-----|" + "|".join(["-----"]*len(pc_ids)) + "|")
        mx = space_map.get("cross_matrix_method_problem",{})
        for mid in mc_ids:
            row = f"| **{mid}** |"
            for pid in pc_ids:
                cell = mx.get(f"{mid}_{pid}",{})
                cnt = cell.get("count",0) if isinstance(cell,dict) else 0
                row += f" {'█'*min(cnt,5) if cnt else '·'} ({cnt}) |"
            lines.append(row)
    lines.append("\n## Sparse regions\n")
    for sr in space_map.get("sparse_regions",[]):
        v = "✓ GAP" if sr.get("is_valid_gap") else "✗ Not gap"
        lines.append(f"- **{sr['cell']}**: {sr.get('method_cluster','')} × {sr.get('problem_cluster','')} — {v}")
        lines.append(f"  > {sr.get('reason','')}")
    for key, title in [("orphan_methods","Orphan methods"),("dataset_monocultures","Dataset monocultures"),("metric_deserts","Metric deserts")]:
        items = space_map.get(key,[])
        if items:
            lines.append(f"\n## {title}\n")
            for it in items: lines.append(f"- {it}")
    return "\n".join(lines)

def run_clustering(config):
    print_banner("STEP 2: Research Space Clustering (Hybrid)")
    cfg = config["pipeline"]; output_dir = cfg["output_dir"]
    corpus = load_json(f"{output_dir}/paper_corpus.json")
    papers = [p for p in corpus["papers"] if "_error" not in p]
    log.info(f"Clustering {len(papers)} papers...")
    if not papers: log.error("No valid papers"); sys.exit(1)

    # Phase A: Embeddings
    embedding_data = None
    try:
        from embedding_engine import run_embedding_pipeline
        log.info("\n── Phase A: Paper embeddings ──")
        embedding_data = run_embedding_pipeline(papers, output_dir)
    except Exception as e:
        log.warning(f"Embeddings skipped ({e}), using LLM-only")

    # Phase B: Knowledge graph
    graph_stats = None; graph_gaps = []
    try:
        from knowledge_graph import ResearchGraph
        log.info("\n── Phase B: Knowledge graph ──")
        graph = ResearchGraph(); graph.build_from_corpus(corpus); graph.save(output_dir)
        graph_stats = graph.get_stats(); graph_gaps = graph.find_structural_gaps()
    except Exception as e:
        log.warning(f"Knowledge graph skipped ({e})")

    # Phase C: LLM interpretation
    log.info("\n── Phase C: LLM cluster interpretation ──")
    client = ClaudeClient(config=config)
    extra = ""
    if embedding_data:
        ci = [{"id":cs["cluster_id"],"n":cs["paper_count"],"papers":[p["paper_id"] for p in cs["papers"]]}
              for cs in embedding_data.get("cluster_summaries",[])]
        extra += f"\n\nEMBEDDING CLUSTERS:\n{json.dumps(ci, indent=1)}"
    if graph_gaps:
        extra += f"\n\nGRAPH GAPS:\n{json.dumps(graph_gaps[:20], indent=1, ensure_ascii=False)}"

    summaries = prepare_paper_summaries(papers)
    MAX = 40
    if len(papers) <= MAX:
        user_msg = f"Analyze these {len(papers)} papers.\n\nPAPER RECORDS:\n{summaries}{extra}\n\nRespond with ONLY JSON."
        space_map = client.ask_json(SYSTEM_PROMPT, user_msg)
    else:
        chunks = []
        for i in range(0, len(papers), MAX):
            chunk = papers[i:i+MAX]
            s = prepare_paper_summaries(chunk)
            r = client.ask_json(SYSTEM_PROMPT, f"Cluster batch {i//MAX+1}.\n\nPAPERS:\n{s}{extra}\n\nOnly JSON.")
            chunks.append(r)
        space_map = client.ask_json(SYSTEM_PROMPT,
            f"Merge {len(chunks)} batches.\n\n{json.dumps(chunks,indent=1)[:50000]}\n\nOnly JSON.")

    save_json(space_map, f"{output_dir}/research_space_map.json")
    save_markdown(generate_cluster_report(space_map, embedding_data, graph_stats),
                  f"{output_dir}/cluster_report.md")
    log.info(f"\nClustering done: M={len(space_map.get('method_clusters',[]))}, "
             f"P={len(space_map.get('problem_clusters',[]))}, "
             f"sparse={len(space_map.get('sparse_regions',[]))}")
    log.info(f"API stats: {client.stats()}")
    return space_map

if __name__ == "__main__":
    run_clustering(load_config())
