"""
step9_session.py — Session File Generator
Produces a single SESSION.md file that combines:
  - Compressed agent brain (essential protocols from 19 agents → ~8KB)
  - Full paper corpus (compact format)
  - Clusters, gaps, conflicts, ideas, novelty verdicts
  - Starter prompts

Upload SESSION.md to ANY LLM (Claude, ChatGPT, Gemini) and start working.

Usage:
  python scripts/step9_session.py                # After full pipeline run
  python scripts/step9_session.py --topic "LLM reasoning"  # Add topic label
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from textwrap import dedent

sys.path.insert(0, str(Path(__file__).parent))
from utils import load_config, load_json, save_json, save_markdown, log, print_banner


# ── Compressed Agent Brain ───────────────────────────────────────────────────
# This replaces 55 files / 712KB with ~8KB of essential protocols.
# Only the rules that matter for idea work survive.

AGENT_BRAIN = dedent("""\
## AGENT BRAIN — Research Idea Discovery Protocols

You are a research idea discovery system. The data below was pre-processed from a corpus of academic papers. Your job is to help the researcher **refine, challenge, and develop** the best ideas.

### Core Rules

1. **IRON RULE: No gap → no idea.** Every idea must trace to a specific gap in the research. Free brainstorming without evidence is forbidden.
2. **Testability > novelty.** A testable mediocre idea beats an untestable brilliant one.
3. **Both outcomes matter.** A good idea produces an interesting finding whether it succeeds or fails (either-way value).
4. **"Apply X to Y" is the lowest form of idea.** Push for deeper mechanistic questions.
5. **Kill early, kill often.** An ABANDON verdict saves months. Don't be gentle with weak ideas.

### How to Analyze Ideas

When the researcher asks about an idea:
1. **Steel-man first**: State the strongest version of the idea
2. **Challenge**: Find the top 3 objections a reviewer would raise
3. **Check novelty**: Does the data below show prior work too close?
4. **Assess feasibility**: Can this be done in 6 months with standard resources?
5. **Position**: How should this be framed as a contribution?

### Novelty Verdicts (from pipeline)

| Verdict | Meaning | Action |
|---------|---------|--------|
| PROCEED | No overlap found, high confidence | Develop into paper |
| PROCEED_WITH_CAUTION | Overlap exists, differentiation possible | Sharpen positioning |
| PIVOT | Very similar work exists | Reframe the contribution |
| ABANDON | Core idea already published | Kill it, move on |

### Gap Types

| Type | What it means |
|------|--------------|
| VOID | No one has tried method M on problem P |
| CONFLICT | Two papers contradict each other |
| WEAKNESS | Existing work has a known flaw |
| ASSUMPTION | A widely-held belief that's never been tested |
| DATASET_MONOCULTURE | Everyone uses the same benchmark |
| ORPHAN_METHOD | A method applied to only 1 domain |

### Devil's Advocate Protocol

When challenging an idea, check:
- **Assumption test**: What must be true for this to work? Is each assumption justified?
- **Alternative explanation**: Could results be explained without the proposed mechanism?
- **Baseline gap**: What's the simplest baseline that might match this approach?
- **Scope trap**: Is this actually solving a sub-problem someone already solved?
- **Replication risk**: Would this replicate with different data/seeds/hardware?

### When Helping Write Paper Sections

- **Introduction**: Gap → why it matters → what we propose → what we find
- **Related work**: Cluster-based organization (from the research map), not chronological
- **Method**: From the idea's method sketch, expand with concrete details
- **Experiments**: Use the idea's evaluation plan as skeleton
- **Positioning**: Frame contribution relative to closest_papers from novelty check
""")


def _safe_load(path):
    try:
        return load_json(path)
    except Exception:
        return {}


def compact_paper(p):
    """Compress one paper record to essential fields."""
    if "_error" in p:
        return None

    method = p.get("method", {})
    problem = p.get("problem", {})
    limitations = p.get("limitations", {})

    compact = {
        "id": p.get("paper_id", "?"),
        "title": p.get("title", "?"),
        "year": p.get("year"),
        "venue": p.get("venue", ""),
    }

    # Method (compact)
    if isinstance(method, dict):
        m_parts = []
        if method.get("name"): m_parts.append(method["name"])
        if method.get("category"): m_parts.append(f"[{method['category']}]")
        if method.get("novelty_claim"): m_parts.append(f"Novelty: {method['novelty_claim']}")
        if m_parts:
            compact["method"] = " — ".join(m_parts)

    # Problem (compact)
    if isinstance(problem, dict) and problem.get("statement"):
        compact["problem"] = problem["statement"][:150]

    # Claims (top 3, compact)
    claims = p.get("claims", [])
    if claims:
        compact["claims"] = [
            c.get("claim", "")[:120] if isinstance(c, dict) else str(c)[:120]
            for c in claims[:3]
        ]

    # Limitations (compact)
    ack = limitations.get("acknowledged", []) if isinstance(limitations, dict) else []
    inferred = limitations.get("inferred", []) if isinstance(limitations, dict) else []
    all_lim = []
    for l in (ack + inferred)[:3]:
        if isinstance(l, dict):
            all_lim.append(l.get("limitation", "")[:100])
        elif isinstance(l, str):
            all_lim.append(l[:100])
    if all_lim:
        compact["limitations"] = all_lim

    # Datasets
    datasets = p.get("datasets", [])
    if datasets:
        compact["datasets"] = [d.get("name", "") if isinstance(d, dict) else str(d)
                               for d in datasets[:4]]

    return compact


def compact_cluster_map(space_map):
    """Compress cluster analysis to readable text."""
    lines = []

    # Method clusters
    for mc in space_map.get("method_clusters", []):
        trend = mc.get("trend", "")
        trend_str = f" ({trend})" if trend else ""
        methods = ", ".join(mc.get("key_methods", [])[:3])
        lines.append(f"- **{mc['cluster_id']}: {mc['label']}** — "
                     f"{mc['paper_count']} papers{trend_str}. Methods: {methods}")

    lines.append("")

    # Problem clusters
    for pc in space_map.get("problem_clusters", []):
        lines.append(f"- **{pc['cluster_id']}: {pc['label']}** — {pc['paper_count']} papers")

    lines.append("")

    # Sparse regions (gaps)
    sparse = space_map.get("sparse_regions", [])
    if sparse:
        lines.append("**Sparse regions (potential gaps):**")
        for sr in sparse:
            valid = "✓ VALID" if sr.get("is_valid_gap") else "✗ invalid"
            lines.append(f"- {sr['cell']}: {sr.get('method_cluster','')} × "
                        f"{sr.get('problem_cluster','')} — {valid}. {sr.get('reason','')}")

    # Dense regions
    dense = space_map.get("dense_regions", [])
    if dense:
        lines.append("\n**Dense regions (well-explored):**")
        for dr in dense[:5]:
            sat = " ⚠️ saturated" if dr.get("saturation_risk") else ""
            lines.append(f"- {dr['cell']}: {dr.get('method_cluster','')} × "
                        f"{dr.get('problem_cluster','')} ({dr['paper_count']} papers){sat}")

    # Structural findings
    for key, label in [("orphan_methods", "Orphan methods"), ("dataset_monocultures", "Dataset monocultures")]:
        items = space_map.get(key, [])
        if items:
            lines.append(f"\n**{label}:** {', '.join(items[:5])}")

    return "\n".join(lines)


def compact_gaps(gaps):
    """Compress gaps to ranked list."""
    lines = []
    for g in gaps.get("gaps", []):
        scoring = g.get("scoring", {})
        score = scoring.get("priority_score", 0)
        human = " 👤" if scoring.get("_human_override") or scoring.get("_human_added") else ""
        lines.append(f"### {g.get('gap_id','?')} — {g.get('title','?')} (priority: {score}/27){human}")
        lines.append(f"- **Type**: {g.get('type','?')}")
        lines.append(f"- **Description**: {g.get('description','')[:200]}")
        direction = g.get("potential_direction", "")
        if direction:
            lines.append(f"- **Direction**: {direction[:200]}")
        lines.append("")
    return "\n".join(lines)


def compact_conflicts(conflicts):
    """Compress conflicts."""
    lines = []
    for c in conflicts.get("conflicts", []):
        lines.append(f"- **{c.get('conflict_id','?')}** [{c.get('severity','?')}]: "
                    f"{c.get('paper_a',{}).get('paper_id','?')} vs "
                    f"{c.get('paper_b',{}).get('paper_id','?')} — "
                    f"{c.get('description','')[:150]}")
    return "\n".join(lines) if lines else "No contradictions detected."


def compact_ideas(ideas):
    """Compress ideas with full detail (this is the core deliverable)."""
    lines = []
    for idea in ideas.get("ideas", []):
        lines.append(f"### {idea.get('idea_id','?')}: {idea.get('title','?')}")
        lines.append(f"- **Source gap**: {idea.get('source_gap',{}).get('gap_id','?')}")

        hyp = idea.get("hypothesis", {})
        if isinstance(hyp, dict):
            lines.append(f"- **Hypothesis**: {hyp.get('statement','')[:200]}")
            lines.append(f"- **If true**: {hyp.get('if_true','')[:150]}")
            lines.append(f"- **If false**: {hyp.get('if_false','')[:150]}")

        method = idea.get("method_sketch", {})
        if isinstance(method, dict):
            lines.append(f"- **Approach**: {method.get('approach','')[:200]}")

        eval_plan = idea.get("evaluation_plan", {})
        if isinstance(eval_plan, dict):
            ds = eval_plan.get("datasets", [])
            metrics = eval_plan.get("metrics", [])
            baselines = eval_plan.get("baselines", [])
            if ds: lines.append(f"- **Datasets**: {', '.join(str(d) for d in ds[:4])}")
            if metrics: lines.append(f"- **Metrics**: {', '.join(str(m) for m in metrics[:4])}")
            if baselines: lines.append(f"- **Baselines**: {', '.join(str(b) for b in baselines[:4])}")

        ranking = idea.get("ranking", {})
        if isinstance(ranking, dict):
            lines.append(f"- **Score**: {ranking.get('overall_score','?')}/50 "
                        f"(novelty:{ranking.get('novelty','-')}, "
                        f"feasibility:{ranking.get('feasibility','-')}, "
                        f"impact:{ranking.get('impact','-')})")

        lines.append("")
    return "\n".join(lines)


def compact_novelty(novelty):
    """Compress novelty verdicts."""
    lines = []
    for v in novelty.get("verifications", []):
        # Handle both multi-model and single-model formats
        consensus = v.get("consensus", v.get("overall_assessment", {}))
        assessment = v.get("assessment", v)

        verdict = consensus.get("verdict", "?")
        score = consensus.get("novelty_score", "?")
        emoji = {"PROCEED":"✅","PROCEED_WITH_CAUTION":"⚠️","PIVOT":"🔄","ABANDON":"❌"}.get(verdict, "?")
        agree = consensus.get("models_agree", True)

        lines.append(f"### {emoji} {v.get('idea_id','?')}: {v.get('title','?')}")
        lines.append(f"- **Verdict**: {verdict} (score: {score}/10)")

        if not agree:
            details = consensus.get("disagreement_details", {})
            for model, mv in details.get("verdicts_by_model", {}).items():
                lines.append(f"  - {model}: {mv}")

        overall = assessment.get("overall_assessment", consensus)
        diff = overall.get("key_differentiator", "")
        risk = overall.get("reviewer_risk", "")
        pos = overall.get("positioning_advice", "")
        if diff: lines.append(f"- **Differentiator**: {diff[:200]}")
        if risk: lines.append(f"- **Reviewer risk**: {risk[:200]}")
        if pos: lines.append(f"- **Positioning**: {pos[:200]}")

        # Closest papers
        closest = assessment.get("closest_papers", [])
        if closest:
            lines.append(f"- **Closest work**:")
            for cp in closest[:3]:
                lines.append(f"  - {cp.get('title','?')} ({cp.get('year','?')}) "
                            f"— {cp.get('overlap_level','?')} overlap")

        lines.append("")
    return "\n".join(lines)


STARTER_PROMPTS = dedent("""\
## What You Can Ask Me

**Pick the best idea:**
> "Compare the top PROCEED ideas. Which has the strongest chance at a top venue? Why?"

**Develop an idea into a paper:**
> "Take IDEA-003 and help me write a 1-page extended abstract for [venue]."
> "Design the complete experiment plan for IDEA-001. What datasets, baselines, metrics, and ablations?"
> "Write the Introduction section for a paper based on IDEA-002."

**Challenge and stress-test:**
> "Play devil's advocate on IDEA-005. What are the top 3 reasons a reviewer would reject it?"
> "What's the simplest baseline that could beat IDEA-001?"

**Refine PIVOT ideas:**
> "IDEA-004 was marked PIVOT. How can I reframe it to avoid overlap with [closest paper]?"

**Find missed gaps:**
> "Looking at the paper corpus, are there any gaps the pipeline missed?"
> "Which papers in the corpus are under-utilized — they have interesting methods no one has combined?"

**Go deeper on a specific paper:**
> "Paper smith-2024 claims X but wang-2025 contradicts it. Who's right and what experiment would resolve this?"

**Plan next steps:**
> "I want to pursue IDEA-002. Give me a 12-week research timeline."
> "What additional papers should I read before starting IDEA-003?"
""")


def generate_session(config, topic: str = ""):
    """Generate the SESSION.md file."""
    print_banner("STEP 9: Session File Generator")

    output_dir = config["pipeline"]["output_dir"]

    # Load all outputs
    corpus = _safe_load(f"{output_dir}/paper_corpus.json")
    space_map = _safe_load(f"{output_dir}/research_space_map.json")
    gaps = _safe_load(f"{output_dir}/gap_analysis.json")
    conflicts = _safe_load(f"{output_dir}/conflict_report.json")
    ideas = _safe_load(f"{output_dir}/idea_report.json")
    novelty = _safe_load(f"{output_dir}/novelty_report.json")
    pipeline = _safe_load(f"{output_dir}/pipeline_summary.json")
    graph_stats = _safe_load(f"{output_dir}/graph_stats.json")

    papers = corpus.get("papers", [])
    n_papers = len(papers)
    n_gaps = len(gaps.get("gaps", []))
    n_ideas = len(ideas.get("ideas", []))

    nov_summary = novelty.get("summary", {})
    topic_label = topic or "Research Corpus"

    # ── Build the session file ───────────────────────────────────────────

    sections = []

    # Header
    sections.append(f"# SESSION: {topic_label}")
    sections.append(f"*Generated {datetime.now().strftime('%Y-%m-%d %H:%M')} — "
                   f"Idea Discovery Pipeline v3.1*\n")
    sections.append(f"**{n_papers} papers analyzed → {n_gaps} gaps found → "
                   f"{n_ideas} ideas generated → "
                   f"{nov_summary.get('proceed',0)} PROCEED / "
                   f"{nov_summary.get('proceed_with_caution',0)} CAUTION / "
                   f"{nov_summary.get('pivot',0)} PIVOT / "
                   f"{nov_summary.get('abandon',0)} ABANDON**\n")
    sections.append("---\n")

    # Agent brain
    sections.append(AGENT_BRAIN)
    sections.append("---\n")

    # Paper corpus (compact)
    sections.append("## PAPER CORPUS\n")
    sections.append(f"{n_papers} papers, compact format. Each paper's extracted "
                   "method, problem, claims, and limitations.\n")

    compact_papers = []
    for p in papers:
        cp = compact_paper(p)
        if cp:
            compact_papers.append(cp)

    # Format as readable text (not raw JSON — LLMs work better with text)
    for cp in compact_papers:
        sections.append(f"### {cp['id']}: {cp['title']} ({cp.get('year','')})")
        if cp.get('venue'): sections.append(f"*{cp['venue']}*")
        if cp.get('method'): sections.append(f"- **Method**: {cp['method']}")
        if cp.get('problem'): sections.append(f"- **Problem**: {cp['problem']}")
        if cp.get('claims'):
            sections.append(f"- **Claims**: " + " | ".join(cp['claims']))
        if cp.get('limitations'):
            sections.append(f"- **Limitations**: " + " | ".join(cp['limitations']))
        if cp.get('datasets'):
            sections.append(f"- **Datasets**: {', '.join(cp['datasets'])}")
        sections.append("")

    sections.append("---\n")

    # Research map
    sections.append("## RESEARCH SPACE MAP\n")
    sections.append(compact_cluster_map(space_map))
    sections.append("\n---\n")

    # Conflicts
    sections.append("## CONFLICTS DETECTED\n")
    sections.append(compact_conflicts(conflicts))
    sections.append("\n---\n")

    # Gaps
    sections.append("## RESEARCH GAPS (ranked by priority)\n")
    sections.append(compact_gaps(gaps))
    sections.append("---\n")

    # Ideas
    sections.append("## GENERATED IDEAS\n")
    sections.append(compact_ideas(ideas))
    sections.append("---\n")

    # Novelty
    sections.append("## NOVELTY VERDICTS\n")
    sections.append(compact_novelty(novelty))
    sections.append("---\n")

    # Starter prompts
    sections.append(STARTER_PROMPTS)

    # Assemble
    session_text = "\n".join(sections)

    # Save markdown
    session_path = f"{output_dir}/SESSION.md"
    save_markdown(session_text, session_path)

    # Save JSON (structured version for programmatic use)
    session_json = {
        "topic": topic_label,
        "generated": datetime.now().isoformat(),
        "pipeline_version": "3.1",
        "stats": {
            "n_papers": n_papers,
            "n_gaps": n_gaps,
            "n_ideas": n_ideas,
            "n_proceed": nov_summary.get("proceed", 0),
            "n_caution": nov_summary.get("proceed_with_caution", 0),
            "n_pivot": nov_summary.get("pivot", 0),
            "n_abandon": nov_summary.get("abandon", 0),
        },
        "papers": compact_papers,
        "clusters": space_map,
        "conflicts": conflicts.get("conflicts", []),
        "gaps": gaps.get("gaps", []),
        "ideas": ideas.get("ideas", []),
        "novelty": novelty.get("verifications", []),
    }
    save_json(session_json, f"{output_dir}/SESSION.json")

    # Stats
    char_count = len(session_text)
    token_estimate = char_count // 4  # rough estimate
    log.info(f"\nSession files generated:")
    log.info(f"  SESSION.md:   {char_count:,} chars (~{token_estimate:,} tokens)")
    log.info(f"  SESSION.json: {len(json.dumps(session_json)):,} chars")
    log.info(f"  Papers: {n_papers}, Gaps: {n_gaps}, Ideas: {n_ideas}")
    log.info(f"\n  Upload SKILL.md + SESSION.md to any LLM and start working!")

    return session_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", type=str, default="",
                        help="Topic label for the session (e.g., 'LLM Reasoning')")
    args = parser.parse_args()

    config = load_config()
    generate_session(config, topic=args.topic)
