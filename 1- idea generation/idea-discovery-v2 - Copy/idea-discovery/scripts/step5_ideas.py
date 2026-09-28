"""
step5_ideas.py — Gap-Driven Idea Generation
Takes gaps and generates concrete, testable research ideas.
IRON RULE: No gap, no idea — every idea must cite a GAP-ID.
Outputs: output/idea_report.json, output/idea_report.md
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

SYSTEM_PROMPT = """You are a research idea generation agent. You generate concrete, testable research ideas EXCLUSIVELY from detected gaps.

⚠️ IRON RULE: No gap, no idea. Every idea MUST cite a specific GAP-ID.

RESPOND WITH ONLY valid JSON — no markdown fences, no explanation.

For each priority gap, generate 1-2 ideas. Then rank and filter them.

Hard filters (if any fails, KILL the idea):
1. Gap traceability — Can you cite a specific GAP-ID? If no → KILL
2. Testability — Can you define a pass/fail criterion? If no → KILL
3. Feasibility — Can a single team do this in 3-6 months? If no → KILL or DOWNSCALE
4. "So what?" test — Does the answer matter to anyone? If no → KILL
5. "Apply X to Y" test — Is this just gluing two things together? If yes → DOWNRANK

Scoring rubric (each 1-5):
- Gap importance: 30% weight
- Scientific rigor: 25%
- Feasibility: 20%
- Either-way value: 15%
- Novelty potential: 10%

Output this JSON:
{
  "total_gaps_analyzed": 7,
  "total_ideas_generated": 12,
  "total_ideas_surviving": 5,
  "ideas": [
    {
      "idea_id": "IDEA-001",
      "source_gap": "GAP-001",
      "gap_type": "VOID",
      "title": "One-sentence descriptive title",
      "hypothesis": {
        "statement": "If we do X, then Y will happen because Z",
        "null_hypothesis": "X has no effect on Y",
        "expected_direction": "positive | negative | diagnostic"
      },
      "method_sketch": {
        "approach": "2-3 sentence description of proposed method",
        "key_components": ["component1", "component2"],
        "baselines": ["baseline1", "baseline2"],
        "ablations": ["what to ablate to understand contributions"]
      },
      "experiment_design": {
        "datasets": ["which datasets and why"],
        "metrics": ["which metrics to report"],
        "evaluation_protocol": "How to evaluate fairly",
        "minimum_viable_experiment": "Cheapest experiment that gives signal"
      },
      "feasibility": {
        "compute_estimate": "GPU-hours for minimum viable experiment",
        "data_requirements": "What data is needed, is it available?",
        "implementation_complexity": "days | weeks | months",
        "dependencies": ["external tools, models, infrastructure needed"]
      },
      "expected_outcomes": {
        "if_positive": "What it means if hypothesis is confirmed",
        "if_negative": "What it means if hypothesis is rejected",
        "either_way_value": "Why the finding matters regardless"
      },
      "contribution_type": "empirical | method | theoretical | diagnostic | benchmark | reproduction",
      "risk_assessment": {
        "risk_level": "LOW | MEDIUM | HIGH",
        "main_risk": "What is most likely to go wrong",
        "mitigation": "How to reduce the risk",
        "reviewer_objection": "Strongest objection a reviewer would raise"
      },
      "positioning": {
        "closest_work": "Most similar existing paper",
        "differentiation": "What makes this different",
        "target_venue": "Where to submit",
        "contribution_sentence": "One sentence: what this adds to the field"
      },
      "scoring": {
        "gap_importance": 4,
        "scientific_rigor": 4,
        "feasibility": 3,
        "either_way_value": 4,
        "novelty_potential": 3,
        "weighted_score": 3.75
      }
    }
  ],
  "eliminated_ideas": [
    {
      "idea_id": "IDEA-X",
      "source_gap": "GAP-002",
      "title": "Title of eliminated idea",
      "reason": "Why it was eliminated (which filter failed)"
    }
  ],
  "traceability_matrix": [
    {"idea_id": "IDEA-001", "gap_id": "GAP-001", "gap_type": "VOID", "gap_priority": 18}
  ]
}

Rules:
- Every idea MUST cite a GAP-ID. No exceptions.
- Every idea MUST have a testable hypothesis with clear null hypothesis
- Every idea MUST estimate compute requirements
- Every idea MUST describe what a NEGATIVE result would mean
- Ranking uses the 5-axis rubric — no gut-feel
- At least 1 idea should be diagnostic/benchmark type (not all methods)
- Eliminated ideas must be listed with reasons
- "Apply X to Y" ideas are allowed ONLY if the combination reveals something genuinely surprising
"""


def generate_idea_report_md(idea_data: dict) -> str:
    """Generate readable markdown report from idea generation results."""
    lines = ["# Idea Generation Report\n"]
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

    lines.append("## Summary\n")
    lines.append(f"- Gaps analyzed: {idea_data.get('total_gaps_analyzed', 0)}")
    lines.append(f"- Ideas generated: {idea_data.get('total_ideas_generated', 0)}")
    lines.append(f"- Ideas surviving filters: {idea_data.get('total_ideas_surviving', 0)}")

    # Traceability matrix
    trace = idea_data.get("traceability_matrix", [])
    if trace:
        lines.append("\n## Gap → Idea Traceability\n")
        lines.append("| Idea | Gap | Gap Type | Gap Priority |")
        lines.append("|------|-----|----------|-------------|")
        for t in trace:
            lines.append(f"| {t['idea_id']} | {t['gap_id']} | {t.get('gap_type','')} | {t.get('gap_priority','')} |")

    # Ranked ideas
    ideas = sorted(idea_data.get("ideas", []),
                   key=lambda i: i.get("scoring", {}).get("weighted_score", 0),
                   reverse=True)

    lines.append("\n## Ranked Ideas\n")
    for rank, idea in enumerate(ideas, 1):
        score = idea.get("scoring", {})
        ws = score.get("weighted_score", 0)
        medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"#{rank}"

        lines.append(f"### {medal} {idea['idea_id']}: {idea.get('title', '?')} — Score: {ws}/5.0")
        lines.append(f"- **Source gap**: {idea.get('source_gap', '?')} ({idea.get('gap_type', '?')})")
        lines.append(f"- **Contribution type**: {idea.get('contribution_type', '?')}")

        hyp = idea.get("hypothesis", {})
        lines.append(f"- **Hypothesis**: {hyp.get('statement', '?')}")

        method = idea.get("method_sketch", {})
        lines.append(f"- **Approach**: {method.get('approach', '?')}")
        if method.get("baselines"):
            lines.append(f"- **Baselines**: {', '.join(method['baselines'])}")

        exp = idea.get("experiment_design", {})
        lines.append(f"- **Minimum experiment**: {exp.get('minimum_viable_experiment', '?')}")

        feas = idea.get("feasibility", {})
        lines.append(f"- **Compute**: {feas.get('compute_estimate', '?')}")
        lines.append(f"- **Complexity**: {feas.get('implementation_complexity', '?')}")

        outcomes = idea.get("expected_outcomes", {})
        lines.append(f"- **If positive**: {outcomes.get('if_positive', '?')}")
        lines.append(f"- **If negative**: {outcomes.get('if_negative', '?')}")
        lines.append(f"- **Either way**: {outcomes.get('either_way_value', '?')}")

        risk = idea.get("risk_assessment", {})
        lines.append(f"- **Risk**: {risk.get('risk_level', '?')} — {risk.get('main_risk', '?')}")
        lines.append(f"- **Reviewer objection**: {risk.get('reviewer_objection', '?')}")

        pos = idea.get("positioning", {})
        lines.append(f"- **Target venue**: {pos.get('target_venue', '?')}")
        lines.append(f"- **Contribution**: {pos.get('contribution_sentence', '?')}\n")

    # Eliminated ideas
    eliminated = idea_data.get("eliminated_ideas", [])
    if eliminated:
        lines.append("\n## Eliminated Ideas\n")
        lines.append("| ID | Gap | Title | Reason |")
        lines.append("|----|-----|-------|--------|")
        for e in eliminated:
            lines.append(f"| {e['idea_id']} | {e.get('source_gap','')} | {e.get('title','')} | {e.get('reason','')} |")

    return "\n".join(lines)


def run_idea_generation(config: dict) -> dict:
    """Generate ideas from gaps."""
    print_banner("STEP 5: Idea Generation")

    cfg = config["pipeline"]
    output_dir = cfg["output_dir"]
    top_ideas = cfg.get("top_ideas", 5)

    # Load inputs
    gap_data = load_json(f"{output_dir}/gap_analysis.json")
    corpus = load_json(f"{output_dir}/paper_corpus.json")
    space_map = load_json(f"{output_dir}/research_space_map.json")

    gaps = gap_data.get("gaps", [])
    papers = [p for p in corpus["papers"] if "_error" not in p]
    log.info(f"Generating ideas from {len(gaps)} gaps (targeting top {top_ideas})...")

    client = ClaudeClient(config=config)

    # Compact paper context for positioning
    paper_context = []
    for p in papers:
        paper_context.append({
            "paper_id": p.get("paper_id"),
            "title": p.get("title"),
            "method_name": p.get("method", {}).get("name"),
            "method_category": p.get("method", {}).get("category"),
            "novelty_claim": p.get("method", {}).get("novelty_claim"),
        })

    user_msg = f"""Generate research ideas from these detected gaps.

TARGET: Generate ideas for the top gaps, keep the best {top_ideas} after filtering.

GAPS (priority-ranked):
{json.dumps(gaps, indent=1, ensure_ascii=False)[:25000]}

PAPER CORPUS CONTEXT ({len(papers)} papers):
{json.dumps(paper_context, indent=1, ensure_ascii=False)[:15000]}

CLUSTER MAP CONTEXT:
{json.dumps(space_map, indent=1, ensure_ascii=False)[:10000]}

Remember:
- Every idea MUST trace to a GAP-ID
- Include eliminated ideas with reasons
- At least 1 diagnostic/benchmark idea
- Both positive AND negative expected outcomes required

Respond with ONLY the JSON idea report."""

    idea_data = client.ask_json(SYSTEM_PROMPT, user_msg)

    # Save outputs
    save_json(idea_data, f"{output_dir}/idea_report.json")
    report_md = generate_idea_report_md(idea_data)
    save_markdown(report_md, f"{output_dir}/idea_report.md")

    n_ideas = idea_data.get("total_ideas_surviving", len(idea_data.get("ideas", [])))
    n_eliminated = len(idea_data.get("eliminated_ideas", []))
    log.info(f"\nIdea generation complete: {n_ideas} ideas surviving, {n_eliminated} eliminated")
    log.info(f"API stats: {client.stats()}")

    return idea_data


if __name__ == "__main__":
    config = load_config()
    run_idea_generation(config)
