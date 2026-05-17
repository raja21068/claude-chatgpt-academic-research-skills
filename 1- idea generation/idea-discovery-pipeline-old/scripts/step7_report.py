"""
step7_report.py — Final Report Compiler
Merges all pipeline outputs into a single comprehensive report.
Outputs: output/FINAL_REPORT.md, output/pipeline_summary.json
"""

import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    load_config, load_json, save_json, save_markdown,
    log, print_banner
)


def compile_final_report(config: dict) -> str:
    """Compile all pipeline outputs into a final report."""
    print_banner("STEP 7: Final Report Compilation")

    output_dir = config["pipeline"]["output_dir"]

    # Load all outputs
    corpus = load_json(f"{output_dir}/paper_corpus.json")
    space_map = load_json(f"{output_dir}/research_space_map.json")
    conflicts = load_json(f"{output_dir}/conflict_report.json")
    gaps = load_json(f"{output_dir}/gap_analysis.json")
    ideas = load_json(f"{output_dir}/idea_report.json")
    novelty = load_json(f"{output_dir}/novelty_report.json")

    # ── Build Final Report ─────────────────────────────────────────────────

    papers = [p for p in corpus["papers"] if "_error" not in p]
    n_papers = len(papers)
    n_failed = corpus.get("failed", 0)

    n_method_clusters = len(space_map.get("method_clusters", []))
    n_problem_clusters = len(space_map.get("problem_clusters", []))
    n_sparse = len(space_map.get("sparse_regions", []))

    n_conflicts = len(conflicts.get("conflicts", []))
    n_high_conflicts = len([c for c in conflicts.get("conflicts", []) if c.get("severity") == "HIGH"])

    n_gaps = gaps.get("total_gaps", 0)
    gap_list = gaps.get("gaps", [])
    high_gaps = [g for g in gap_list if g.get("scoring", {}).get("priority_score", 0) >= 18]

    idea_list = ideas.get("ideas", [])
    n_ideas = len(idea_list)

    nov_summary = novelty.get("summary", {})
    verifications = novelty.get("verifications", [])

    # Build actionable ideas (PROCEED or PROCEED_WITH_CAUTION)
    actionable = []
    for v in verifications:
        verdict = v.get("overall_assessment", {}).get("verdict", "")
        if verdict in ("PROCEED", "PROCEED_WITH_CAUTION"):
            # Find matching idea
            idea_id = v.get("idea_id", "")
            matching = [i for i in idea_list if i.get("idea_id") == idea_id]
            if matching:
                actionable.append({
                    "idea": matching[0],
                    "novelty": v,
                })

    # Sort by idea score
    actionable.sort(
        key=lambda x: x["idea"].get("scoring", {}).get("weighted_score", 0),
        reverse=True
    )

    # ── Render Markdown ─────────────────────────────────────────────────────

    lines = []
    lines.append("# 🔬 Idea Discovery Pipeline — Final Report\n")
    lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**Pipeline version**: v3.0.0\n")

    # Executive Summary
    lines.append("---")
    lines.append("## Executive Summary\n")
    lines.append(f"| Stage | Result |")
    lines.append(f"|-------|--------|")
    lines.append(f"| Papers ingested | {n_papers} ({n_failed} failed) |")
    lines.append(f"| Method clusters | {n_method_clusters} |")
    lines.append(f"| Problem clusters | {n_problem_clusters} |")
    lines.append(f"| Sparse regions (potential gaps) | {n_sparse} |")
    lines.append(f"| Conflicts detected | {n_conflicts} ({n_high_conflicts} high severity) |")
    lines.append(f"| Research gaps | {n_gaps} ({len(high_gaps)} high priority) |")
    lines.append(f"| Ideas generated | {n_ideas} |")
    lines.append(f"| Novelty-verified | PROCEED: {nov_summary.get('proceed',0)}, CAUTION: {nov_summary.get('proceed_with_caution',0)}, PIVOT: {nov_summary.get('pivot',0)}, ABANDON: {nov_summary.get('abandon',0)} |")
    lines.append(f"| **Actionable ideas** | **{len(actionable)}** |")

    # ── Recommended Research Agenda ──────────────────────────────────────────

    lines.append("\n---")
    lines.append("## 🎯 Recommended Research Agenda\n")

    if actionable:
        for rank, item in enumerate(actionable, 1):
            idea = item["idea"]
            nov = item["novelty"]
            verdict = nov.get("overall_assessment", {}).get("verdict", "")
            emoji = "✅" if verdict == "PROCEED" else "⚠️"

            lines.append(f"### {rank}. {emoji} {idea.get('idea_id','')}: {idea.get('title','')}")
            lines.append(f"- **Novelty verdict**: {verdict} (score: {nov.get('overall_assessment',{}).get('novelty_score','?')}/10)")
            lines.append(f"- **Source gap**: {idea.get('source_gap','')} — {idea.get('gap_type','')}")

            score = idea.get("scoring", {})
            lines.append(f"- **Idea score**: {score.get('weighted_score','?')}/5.0")

            hyp = idea.get("hypothesis", {})
            lines.append(f"- **Hypothesis**: {hyp.get('statement','')}")

            method = idea.get("method_sketch", {})
            lines.append(f"- **Approach**: {method.get('approach','')}")

            exp = idea.get("experiment_design", {})
            lines.append(f"- **Minimum experiment**: {exp.get('minimum_viable_experiment','')}")

            feas = idea.get("feasibility", {})
            lines.append(f"- **Compute**: {feas.get('compute_estimate','')}")
            lines.append(f"- **Complexity**: {feas.get('implementation_complexity','')}")

            pos = idea.get("positioning", {})
            lines.append(f"- **Target venue**: {pos.get('target_venue','')}")
            lines.append(f"- **Contribution**: {pos.get('contribution_sentence','')}")

            nov_assess = nov.get("overall_assessment", {})
            lines.append(f"- **Positioning advice**: {nov_assess.get('positioning_advice','')}")
            lines.append(f"- **Reviewer risk**: {nov_assess.get('reviewer_risk','')}\n")
    else:
        lines.append("No ideas passed novelty verification. Consider expanding the paper corpus or relaxing gap criteria.\n")

    # ── Key Conflicts (for reference) ─────────────────────────────────────

    high_conflicts = [c for c in conflicts.get("conflicts", []) if c.get("severity") == "HIGH"]
    if high_conflicts:
        lines.append("---")
        lines.append("## ⚡ Unresolved Conflicts (High Severity)\n")
        for c in high_conflicts:
            lines.append(f"**{c.get('conflict_id','')}** ({c.get('type','')})")
            lines.append(f"- {c.get('paper_a',{}).get('paper_id','')}: {c.get('paper_a',{}).get('position','')}")
            lines.append(f"- {c.get('paper_b',{}).get('paper_id','')}: {c.get('paper_b',{}).get('position','')}")
            lines.append(f"- Resolution: {c.get('resolution_path','')}\n")

    # ── Full Gap List ─────────────────────────────────────────────────────

    lines.append("---")
    lines.append("## 📋 All Detected Gaps (Priority-Ranked)\n")
    lines.append("| Rank | ID | Type | Title | Score |")
    lines.append("|------|----|------|-------|-------|")
    sorted_gaps = sorted(gap_list, key=lambda g: g.get("scoring",{}).get("priority_score",0), reverse=True)
    for rank, g in enumerate(sorted_gaps, 1):
        ps = g.get("scoring", {}).get("priority_score", 0)
        lines.append(f"| {rank} | {g.get('gap_id','')} | {g.get('type','')} | {g.get('title','')} | {ps}/27 |")

    # ── Pipeline Outputs Index ────────────────────────────────────────────

    lines.append("\n---")
    lines.append("## 📁 Pipeline Outputs\n")
    lines.append(f"| File | Description |")
    lines.append(f"|------|-------------|")
    lines.append(f"| `output/paper_corpus.json` | Structured paper records ({n_papers} papers) |")
    lines.append(f"| `output/research_space_map.json` | Cluster map + cross-matrices |")
    lines.append(f"| `output/cluster_report.md` | Readable cluster analysis |")
    lines.append(f"| `output/conflict_report.json` | Cross-paper conflicts |")
    lines.append(f"| `output/conflict_report.md` | Readable conflict analysis |")
    lines.append(f"| `output/gap_analysis.json` | Detected research gaps |")
    lines.append(f"| `output/gap_report.md` | Readable gap analysis |")
    lines.append(f"| `output/idea_report.json` | Generated research ideas |")
    lines.append(f"| `output/idea_report.md` | Readable idea report |")
    lines.append(f"| `output/novelty_report.json` | Novelty verification results |")
    lines.append(f"| `output/novelty_report.md` | Readable novelty report |")
    lines.append(f"| `output/FINAL_REPORT.md` | This report |")

    report_text = "\n".join(lines)

    # Save
    save_markdown(report_text, f"{output_dir}/FINAL_REPORT.md")

    # Save compact summary JSON
    summary = {
        "generated": datetime.now().isoformat(),
        "papers_ingested": n_papers,
        "method_clusters": n_method_clusters,
        "problem_clusters": n_problem_clusters,
        "conflicts": n_conflicts,
        "gaps": n_gaps,
        "ideas_generated": n_ideas,
        "ideas_actionable": len(actionable),
        "novelty_verdicts": {
            "proceed": nov_summary.get("proceed", 0),
            "caution": nov_summary.get("proceed_with_caution", 0),
            "pivot": nov_summary.get("pivot", 0),
            "abandon": nov_summary.get("abandon", 0),
        },
        "top_ideas": [
            {
                "id": item["idea"].get("idea_id"),
                "title": item["idea"].get("title"),
                "gap": item["idea"].get("source_gap"),
                "score": item["idea"].get("scoring", {}).get("weighted_score"),
                "verdict": item["novelty"].get("overall_assessment", {}).get("verdict"),
            }
            for item in actionable
        ],
    }
    save_json(summary, f"{output_dir}/pipeline_summary.json")

    log.info(f"\n{'='*60}")
    log.info(f"  FINAL REPORT: output/FINAL_REPORT.md")
    log.info(f"  Actionable ideas: {len(actionable)}")
    log.info(f"{'='*60}")

    return report_text


if __name__ == "__main__":
    config = load_config()
    compile_final_report(config)
