"""
step4_gaps.py — Research Gap Detection
Analyzes clusters + conflicts to find structural gaps: missing combinations,
weaknesses, untested assumptions, convergent future work.
Outputs: output/gap_analysis.json, output/gap_report.md
"""

import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    ClaudeClient, load_config, load_json, save_json, save_markdown,
    log, print_banner
)

SYSTEM_PROMPT = """You are a research gap detection agent. You analyze a clustered research landscape and conflict report to systematically identify what is MISSING, WEAK, or CONFLICTING in the current research.

IRON RULE: A gap is a STRUCTURAL ABSENCE in the evidence map, not a wish or opinion.

RESPOND WITH ONLY valid JSON — no markdown fences, no explanation.

Gap types to detect:
1. VOID — A valid method×problem (or other cross-dimension) combination with ZERO papers
2. CONFLICT — An unresolved disagreement between papers that needs investigation
3. WEAKNESS — An area where evidence exists but is thin or methodologically limited
4. ASSUMPTION — A widely-shared assumption that nobody has tested directly
5. FUTURE_WORK — A direction suggested by multiple papers but not yet pursued

For each gap, compute Priority = Impact(1-3) × Feasibility(1-3) × Novelty(1-3). Max = 27.

Output this JSON:
{
  "total_gaps": 10,
  "gaps": [
    {
      "gap_id": "GAP-001",
      "type": "VOID | CONFLICT | WEAKNESS | ASSUMPTION | FUTURE_WORK",
      "title": "Short descriptive title",
      "description": "2-3 sentences explaining the gap",
      "evidence": {
        "source": "Which clusters, conflicts, or papers reveal this gap",
        "empty_cells": ["M2_P4", "M3_P5"],
        "related_papers": ["paper-ids that are closest to this gap"],
        "conflict_ids": ["CONF-001"]
      },
      "scoring": {
        "impact": 3,
        "impact_reason": "Why this matters",
        "feasibility": 2,
        "feasibility_reason": "What's needed to address it",
        "novelty": 3,
        "novelty_reason": "How likely others are already working on it",
        "priority_score": 18
      },
      "potential_direction": "1-2 sentences on what a study addressing this gap would look like (but do NOT propose a specific method — that's the idea generator's job)"
    }
  ],
  "assumption_audit": [
    {
      "assumption": "The shared assumption",
      "papers_relying": 30,
      "papers_testing": 2,
      "verdict": "untested | partially_tested | well_tested",
      "gap_id": "GAP-007 or null if well-tested"
    }
  ],
  "future_work_convergence": [
    {
      "direction": "Future work direction",
      "suggested_by": ["paper-id-1", "paper-id-3"],
      "already_done_by": ["paper-id-5"],
      "still_open": "What remains undone",
      "gap_id": "GAP-010 or null if already addressed"
    }
  ],
  "summary": {
    "void_gaps": 4,
    "conflict_gaps": 2,
    "weakness_gaps": 3,
    "assumption_gaps": 1,
    "future_work_gaps": 2,
    "high_priority_count": 3,
    "avg_priority_score": 14.2
  }
}

Rules:
- Every gap must cite SPECIFIC evidence (cluster IDs, paper IDs, conflict IDs)
- At least 5 gaps should be identified (if fewer, the corpus is too small — note this)
- Conflicts from the conflict report should be converted to CONFLICT-type gaps
- VOID gaps must check: is this empty cell genuinely unstudied, or empty for a good reason?
- Priority scores must be justified with reasons
- Do NOT generate ideas — only identify gaps. Ideas come from the next step.
- Gaps are structural absences, NOT things you think should exist
"""


def generate_gap_report_md(gap_data: dict) -> str:
    """Generate readable markdown from gap analysis."""
    lines = ["# Gap Analysis Report\n"]
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

    summary = gap_data.get("summary", {})
    lines.append("## Summary\n")
    lines.append(f"- Total gaps detected: {gap_data.get('total_gaps', 0)}")
    lines.append(f"- Void gaps (missing combinations): {summary.get('void_gaps', 0)}")
    lines.append(f"- Conflict-derived gaps: {summary.get('conflict_gaps', 0)}")
    lines.append(f"- Weakness gaps: {summary.get('weakness_gaps', 0)}")
    lines.append(f"- Assumption gaps: {summary.get('assumption_gaps', 0)}")
    lines.append(f"- Future work gaps: {summary.get('future_work_gaps', 0)}")
    lines.append(f"- High priority (≥18): {summary.get('high_priority_count', 0)}")

    # Priority-ranked gaps
    gaps = sorted(gap_data.get("gaps", []),
                  key=lambda g: g.get("scoring", {}).get("priority_score", 0),
                  reverse=True)

    lines.append("\n## Priority-Ranked Gaps\n")
    for g in gaps:
        score = g.get("scoring", {})
        ps = score.get("priority_score", 0)
        emoji = "🔴" if ps >= 18 else "🟡" if ps >= 12 else "⚪"
        lines.append(f"### {emoji} {g['gap_id']}: {g.get('title', '?')} — Score: {ps}/27")
        lines.append(f"- **Type**: {g.get('type', '?')}")
        lines.append(f"- **Description**: {g.get('description', '?')}")
        lines.append(f"- **Impact**: {score.get('impact', '?')}/3 — {score.get('impact_reason', '')}")
        lines.append(f"- **Feasibility**: {score.get('feasibility', '?')}/3 — {score.get('feasibility_reason', '')}")
        lines.append(f"- **Novelty**: {score.get('novelty', '?')}/3 — {score.get('novelty_reason', '')}")
        ev = g.get("evidence", {})
        if ev.get("empty_cells"):
            lines.append(f"- **Empty cells**: {', '.join(ev['empty_cells'])}")
        if ev.get("conflict_ids"):
            lines.append(f"- **Related conflicts**: {', '.join(ev['conflict_ids'])}")
        lines.append(f"- **Potential direction**: {g.get('potential_direction', '?')}\n")

    # Assumption audit
    assumptions = gap_data.get("assumption_audit", [])
    if assumptions:
        lines.append("\n## Assumption Audit\n")
        lines.append("| Assumption | Papers Relying | Papers Testing | Verdict |")
        lines.append("|-----------|---------------|---------------|---------|")
        for a in assumptions:
            lines.append(f"| {a.get('assumption','')} | {a.get('papers_relying',0)} | {a.get('papers_testing',0)} | {a.get('verdict','')} |")

    # Future work convergence
    fw = gap_data.get("future_work_convergence", [])
    if fw:
        lines.append("\n## Future Work Convergence\n")
        for f in fw:
            status = "✅ Addressed" if not f.get("gap_id") else f"⬜ Open → {f['gap_id']}"
            lines.append(f"- **{f.get('direction','')}** — suggested by {len(f.get('suggested_by',[]))} papers — {status}")
            if f.get("still_open"):
                lines.append(f"  > Still open: {f['still_open']}")

    return "\n".join(lines)


def run_gap_detection(config: dict) -> dict:
    """Run gap detection on clusters + conflicts."""
    print_banner("STEP 4: Gap Detection")

    cfg = config["pipeline"]
    output_dir = cfg["output_dir"]

    # Load inputs
    corpus = load_json(f"{output_dir}/paper_corpus.json")
    space_map = load_json(f"{output_dir}/research_space_map.json")
    conflict_data = load_json(f"{output_dir}/conflict_report.json")

    papers = [p for p in corpus["papers"] if "_error" not in p]
    log.info(f"Detecting gaps across {len(papers)} papers...")

    client = ClaudeClient(config=config)

    # Build compact input
    compact_corpus = []
    for p in papers:
        compact_corpus.append({
            "paper_id": p.get("paper_id"),
            "title": p.get("title"),
            "year": p.get("year"),
            "method_category": p.get("method", {}).get("category"),
            "method_name": p.get("method", {}).get("name"),
            "problem": p.get("problem", {}).get("statement", ""),
            "limitations": p.get("limitations", {}),
            "future_work": p.get("future_work", []),
            "claims": p.get("claims", []),
        })

    user_msg = f"""Analyze this research landscape to detect gaps.

PAPER CORPUS ({len(papers)} papers):
{json.dumps(compact_corpus, indent=1, ensure_ascii=False)[:25000]}

RESEARCH SPACE MAP (clusters and cross-matrices):
{json.dumps(space_map, indent=1, ensure_ascii=False)[:20000]}

CONFLICT REPORT:
{json.dumps(conflict_data, indent=1, ensure_ascii=False)[:10000]}

Detect ALL structural gaps: missing combinations, conflicts as opportunities,
weaknesses, untested assumptions, and convergent future work directions.

Respond with ONLY the JSON gap analysis."""

    gap_data = client.ask_json(SYSTEM_PROMPT, user_msg)

    # Save outputs
    save_json(gap_data, f"{output_dir}/gap_analysis.json")
    report_md = generate_gap_report_md(gap_data)
    save_markdown(report_md, f"{output_dir}/gap_report.md")

    n_gaps = gap_data.get("total_gaps", len(gap_data.get("gaps", [])))
    high_p = len([g for g in gap_data.get("gaps", [])
                  if g.get("scoring", {}).get("priority_score", 0) >= 18])
    log.info(f"\nGap detection complete: {n_gaps} gaps found ({high_p} high priority)")
    log.info(f"API stats: {client.stats()}")

    return gap_data


if __name__ == "__main__":
    config = load_config()
    run_gap_detection(config)
