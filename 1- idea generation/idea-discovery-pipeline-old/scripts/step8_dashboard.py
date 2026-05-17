"""
step8_dashboard.py — Interactive Dashboard Generator
Produces a self-contained HTML file with:
  - Paper scatter plot (2D UMAP projection, colored by cluster)
  - Method × Problem heatmap
  - Idea cards with novelty verdicts
  - Gap analysis summary
  - Pipeline statistics
Uses Chart.js from CDN. No build step needed.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from utils import load_json, save_markdown, log, print_banner


def _safe_load(path):
    """Load JSON or return empty dict/list."""
    try:
        return load_json(path)
    except Exception:
        return {}


def generate_dashboard(config):
    """Generate interactive HTML dashboard from pipeline outputs."""
    print_banner("STEP 8: Interactive Dashboard")

    output_dir = config["pipeline"]["output_dir"]

    # Load all data
    corpus = _safe_load(f"{output_dir}/paper_corpus.json")
    space_map = _safe_load(f"{output_dir}/research_space_map.json")
    embeddings = _safe_load(f"{output_dir}/embeddings.json")
    gaps = _safe_load(f"{output_dir}/gap_analysis.json")
    ideas = _safe_load(f"{output_dir}/idea_report.json")
    novelty = _safe_load(f"{output_dir}/novelty_report.json")
    conflicts = _safe_load(f"{output_dir}/conflict_report.json")
    graph_stats = _safe_load(f"{output_dir}/graph_stats.json")
    pipeline = _safe_load(f"{output_dir}/pipeline_summary.json")

    papers = corpus.get("papers", [])
    n_papers = len(papers)
    n_clusters = len(space_map.get("method_clusters", []))
    n_gaps = len(gaps.get("gaps", []))
    n_ideas = len(ideas.get("ideas", []))

    # Prepare scatter data from embeddings
    scatter_data = []
    if embeddings.get("papers"):
        for p in embeddings["papers"]:
            scatter_data.append({
                "x": p.get("x_2d", 0),
                "y": p.get("y_2d", 0),
                "label": p.get("title", "")[:50],
                "cluster": p.get("cluster_label", -1),
                "paper_id": p.get("paper_id", ""),
            })

    # Prepare idea cards
    idea_cards = []
    verifications = {v.get("idea_id", v.get("assessment", {}).get("idea_id", "")): v
                     for v in novelty.get("verifications", [])}
    for idea in ideas.get("ideas", []):
        iid = idea.get("idea_id", "")
        v = verifications.get(iid, {})
        consensus = v.get("consensus", v.get("assessment", {}).get("overall_assessment", {}))
        idea_cards.append({
            "id": iid,
            "title": idea.get("title", ""),
            "gap": idea.get("source_gap", {}).get("gap_id", ""),
            "hypothesis": idea.get("hypothesis", {}).get("statement", "")[:200],
            "verdict": consensus.get("verdict", "?"),
            "score": consensus.get("novelty_score", "?"),
            "differentiator": consensus.get("key_differentiator", ""),
        })

    # Prepare heatmap data
    mc_ids = [mc["cluster_id"] for mc in space_map.get("method_clusters", [])]
    pc_ids = [pc["cluster_id"] for pc in space_map.get("problem_clusters", [])]
    mc_labels = {mc["cluster_id"]: mc["label"] for mc in space_map.get("method_clusters", [])}
    pc_labels = {pc["cluster_id"]: pc["label"] for pc in space_map.get("problem_clusters", [])}
    matrix = space_map.get("cross_matrix_method_problem", {})
    heatmap_data = []
    for mi, mid in enumerate(mc_ids):
        for pi, pid in enumerate(pc_ids):
            cell = matrix.get(f"{mid}_{pid}", {})
            count = cell.get("count", 0) if isinstance(cell, dict) else 0
            heatmap_data.append({"x": pi, "y": mi, "v": count})

    # Gap summary
    gap_summary = []
    for g in gaps.get("gaps", [])[:10]:
        scoring = g.get("scoring", {})
        gap_summary.append({
            "id": g.get("gap_id", ""),
            "title": g.get("title", ""),
            "type": g.get("type", ""),
            "score": scoring.get("priority_score", 0),
            "human": scoring.get("_human_override", False) or scoring.get("_human_added", False),
        })

    # Novelty summary
    nov_summary = novelty.get("summary", {})

    # Build HTML
    html = _build_html(
        n_papers=n_papers,
        n_clusters=n_clusters,
        n_gaps=n_gaps,
        n_ideas=n_ideas,
        scatter_data=scatter_data,
        idea_cards=idea_cards,
        mc_ids=mc_ids,
        pc_ids=pc_ids,
        mc_labels=mc_labels,
        pc_labels=pc_labels,
        heatmap_data=heatmap_data,
        gap_summary=gap_summary,
        nov_summary=nov_summary,
        graph_stats=graph_stats,
        pipeline=pipeline,
    )

    dash_path = f"{output_dir}/dashboard.html"
    with open(dash_path, "w", encoding="utf-8") as f:
        f.write(html)

    log.info(f"Dashboard saved: {dash_path}")
    return dash_path


def _build_html(**d):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Idea Discovery Dashboard</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
  :root {{
    --bg: #0f1117; --bg2: #1a1d27; --bg3: #252830;
    --fg: #e4e4e7; --fg2: #a1a1aa; --fg3: #71717a;
    --accent: #818cf8; --green: #4ade80; --amber: #fbbf24;
    --red: #f87171; --blue: #60a5fa; --teal: #2dd4bf;
    --radius: 10px;
  }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         background: var(--bg); color: var(--fg); padding: 24px; line-height: 1.5; }}
  h1 {{ font-size: 24px; font-weight: 600; margin-bottom: 4px; }}
  h2 {{ font-size: 18px; font-weight: 500; margin-bottom: 12px; color: var(--fg2); }}
  h3 {{ font-size: 15px; font-weight: 500; margin-bottom: 8px; }}
  .subtitle {{ color: var(--fg3); font-size: 14px; margin-bottom: 24px; }}

  .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px,1fr));
            gap: 12px; margin-bottom: 24px; }}
  .stat {{ background: var(--bg2); border-radius: var(--radius); padding: 16px;
           border: 1px solid #2a2d37; }}
  .stat-value {{ font-size: 28px; font-weight: 600; }}
  .stat-label {{ font-size: 12px; color: var(--fg3); margin-top: 2px; }}

  .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px; }}
  @media (max-width: 900px) {{ .grid {{ grid-template-columns: 1fr; }} }}
  .card {{ background: var(--bg2); border-radius: var(--radius); padding: 20px;
           border: 1px solid #2a2d37; }}
  canvas {{ max-height: 340px; }}

  .idea-list {{ display: flex; flex-direction: column; gap: 10px; }}
  .idea-card {{ background: var(--bg3); border-radius: 8px; padding: 14px; }}
  .idea-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }}
  .idea-title {{ font-weight: 500; font-size: 14px; }}
  .badge {{ font-size: 11px; padding: 2px 8px; border-radius: 12px; font-weight: 500; }}
  .badge-proceed {{ background: #065f46; color: var(--green); }}
  .badge-caution {{ background: #78350f; color: var(--amber); }}
  .badge-pivot {{ background: #1e3a5f; color: var(--blue); }}
  .badge-abandon {{ background: #7f1d1d; color: var(--red); }}
  .idea-meta {{ font-size: 12px; color: var(--fg3); }}

  .gap-row {{ display: flex; justify-content: space-between; padding: 8px 0;
              border-bottom: 1px solid #2a2d37; font-size: 13px; }}
  .gap-score {{ font-weight: 600; color: var(--accent); min-width: 30px; text-align: right; }}
  .gap-type {{ font-size: 11px; color: var(--fg3); background: var(--bg3); padding: 1px 6px;
               border-radius: 4px; margin-left: 8px; }}
  .human-tag {{ font-size: 10px; color: var(--teal); margin-left: 4px; }}

  .footer {{ text-align: center; color: var(--fg3); font-size: 12px; margin-top: 32px; padding-top: 16px;
             border-top: 1px solid #2a2d37; }}
</style>
</head>
<body>

<h1>Idea Discovery Dashboard</h1>
<p class="subtitle">Generated {datetime.now().strftime('%Y-%m-%d %H:%M')} &middot; Pipeline v3.1</p>

<div class="stats">
  <div class="stat"><div class="stat-value">{d['n_papers']}</div><div class="stat-label">Papers analyzed</div></div>
  <div class="stat"><div class="stat-value">{d['n_clusters']}</div><div class="stat-label">Method clusters</div></div>
  <div class="stat"><div class="stat-value">{d['n_gaps']}</div><div class="stat-label">Gaps found</div></div>
  <div class="stat"><div class="stat-value">{d['n_ideas']}</div><div class="stat-label">Ideas generated</div></div>
  <div class="stat"><div class="stat-value">{d['nov_summary'].get('proceed',0)}</div><div class="stat-label">Novel (PROCEED)</div></div>
  <div class="stat"><div class="stat-value">{d['graph_stats'].get('total_nodes','-')}</div><div class="stat-label">Graph nodes</div></div>
</div>

<div class="grid">
  <div class="card">
    <h3>Paper embedding space</h3>
    <canvas id="scatter"></canvas>
  </div>
  <div class="card">
    <h3>Method × Problem heatmap</h3>
    <canvas id="heatmap"></canvas>
  </div>
</div>

<div class="grid">
  <div class="card">
    <h3>Top gaps (by priority score)</h3>
    <div id="gap-list">
      {''.join(f'''<div class="gap-row">
        <div><span>{g['id']}</span><span class="gap-type">{g['type']}</span>
        {'<span class="human-tag">👤 human</span>' if g.get('human') else ''}
        <br><span style="color:var(--fg2);font-size:12px">{g['title'][:60]}</span></div>
        <div class="gap-score">{g['score']}</div>
      </div>''' for g in d['gap_summary'])}
    </div>
  </div>
  <div class="card">
    <h3>Ideas + novelty verdicts</h3>
    <div class="idea-list">
      {''.join(_idea_card_html(ic) for ic in d['idea_cards'][:8])}
    </div>
  </div>
</div>

<div class="card" style="margin-bottom:24px">
  <h3>Novelty verification summary</h3>
  <canvas id="verdictChart" style="max-height:200px"></canvas>
</div>

<div class="footer">
  Idea Discovery Pipeline v3.1 &middot; Powered by Claude + SPECTER + NetworkX
</div>

<script>
const COLORS = ['#818cf8','#4ade80','#fbbf24','#f87171','#60a5fa','#2dd4bf','#fb923c','#e879f9','#a78bfa','#94a3b8'];
const scatterData = {json.dumps(d['scatter_data'])};
const mcLabels = {json.dumps(list(d['mc_labels'].values()))};
const pcLabels = {json.dumps(list(d['pc_labels'].values()))};
const heatData = {json.dumps(d['heatmap_data'])};
const novSummary = {json.dumps(d['nov_summary'])};

// Scatter plot
if (scatterData.length > 0) {{
  const clusters = [...new Set(scatterData.map(p=>p.cluster))].sort((a,b)=>a-b);
  const datasets = clusters.map((c,i) => ({{
    label: c === -1 ? 'Noise' : 'Cluster '+c,
    data: scatterData.filter(p=>p.cluster===c).map(p=>({{x:p.x,y:p.y}})),
    backgroundColor: c===-1 ? '#555' : COLORS[i % COLORS.length],
    pointRadius: 5, pointHoverRadius: 8,
  }}));
  new Chart(document.getElementById('scatter'), {{
    type: 'scatter',
    data: {{ datasets }},
    options: {{
      responsive: true,
      plugins: {{ legend: {{ labels: {{ color: '#a1a1aa', font: {{size:11}} }} }} }},
      scales: {{
        x: {{ display: false }},
        y: {{ display: false }},
      }},
    }},
  }});
}} else {{
  document.getElementById('scatter').parentElement.innerHTML += '<p style="color:var(--fg3);font-size:13px;margin-top:8px">No embedding data (run with embeddings enabled)</p>';
}}

// Heatmap (bubble chart)
if (heatData.length > 0 && mcLabels.length > 0) {{
  const maxV = Math.max(...heatData.map(h=>h.v), 1);
  new Chart(document.getElementById('heatmap'), {{
    type: 'bubble',
    data: {{
      datasets: [{{
        data: heatData.filter(h=>h.v>0).map(h=>({{x:h.x, y:h.y, r: Math.max(4, (h.v/maxV)*22)}})),
        backgroundColor: 'rgba(129,140,248,0.5)',
        borderColor: '#818cf8',
      }}]
    }},
    options: {{
      responsive: true,
      plugins: {{ legend: {{ display: false }} }},
      scales: {{
        x: {{ type:'category', labels: pcLabels, ticks: {{ color:'#a1a1aa', font:{{size:10}}, maxRotation:45 }} }},
        y: {{ type:'category', labels: mcLabels, ticks: {{ color:'#a1a1aa', font:{{size:10}} }}, reverse: true }},
      }},
    }},
  }});
}}

// Verdict donut
new Chart(document.getElementById('verdictChart'), {{
  type: 'doughnut',
  data: {{
    labels: ['Proceed','Caution','Pivot','Abandon'],
    datasets: [{{
      data: [novSummary.proceed||0, novSummary.proceed_with_caution||0, novSummary.pivot||0, novSummary.abandon||0],
      backgroundColor: ['#4ade80','#fbbf24','#60a5fa','#f87171'],
      borderWidth: 0,
    }}]
  }},
  options: {{
    responsive: true,
    plugins: {{ legend: {{ labels: {{ color:'#a1a1aa' }} }} }},
    cutout: '60%',
  }},
}});
</script>

</body>
</html>"""


def _idea_card_html(ic):
    vmap = {"PROCEED":"proceed","PROCEED_WITH_CAUTION":"caution","PIVOT":"pivot","ABANDON":"abandon"}
    badge_cls = vmap.get(ic["verdict"], "caution")
    return f"""<div class="idea-card">
  <div class="idea-header">
    <span class="idea-title">{ic['id']}: {ic['title'][:45]}</span>
    <span class="badge badge-{badge_cls}">{ic['verdict']} ({ic['score']}/10)</span>
  </div>
  <div class="idea-meta">{ic['hypothesis'][:120]}{'...' if len(ic.get('hypothesis',''))>120 else ''}</div>
</div>"""


if __name__ == "__main__":
    config = load_config()
    generate_dashboard(config)
