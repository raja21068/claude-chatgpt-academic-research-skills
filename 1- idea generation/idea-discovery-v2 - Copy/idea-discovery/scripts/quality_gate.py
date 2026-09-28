"""
quality_gate.py — Self-Critique & Human Checkpoint System
Validates outputs between pipeline steps.
Saves checkpoint YAML for human review before idea generation.
"""

import json
import sys
import yaml
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from utils import ClaudeClient, load_config, load_json, save_json, log


# ── Ingestion Quality Check ─────────────────────────────────────────────────

INGESTION_CRITIQUE_PROMPT = """You are a quality auditor for paper extraction. Review these extracted paper records and identify problems.

Check for:
1. MISSING FIELDS: Any paper with null/empty title, method, or problem
2. DUPLICATE PAPERS: Same paper appearing twice (preprint + published version)
3. CATEGORY INCONSISTENCY: Same method labeled differently across papers
4. WEAK EXTRACTIONS: Papers with extraction_confidence = "low" that have important data
5. SUSPICIOUS CLAIMS: Claims that seem too strong for the evidence type

RESPOND WITH ONLY JSON:
{
  "total_reviewed": 10,
  "issues": [
    {
      "paper_id": "smith-2024",
      "issue_type": "missing_field | duplicate | inconsistency | weak_extraction | suspicious_claim",
      "severity": "HIGH | MEDIUM | LOW",
      "description": "What's wrong",
      "suggested_fix": "How to fix it"
    }
  ],
  "category_normalization": [
    {"found": "transformer", "also_found_as": "attention-based", "normalize_to": "transformer"}
  ],
  "overall_quality": "GOOD | ACCEPTABLE | NEEDS_REVIEW",
  "summary": "1-2 sentence summary of quality"
}"""


def critique_ingestion(config: dict) -> dict:
    """Run quality check on ingestion output."""
    log.info("Running ingestion quality check...")
    output_dir = config["pipeline"]["output_dir"]
    corpus = load_json(f"{output_dir}/paper_corpus.json")
    papers = corpus.get("papers", [])

    client = ClaudeClient(config=config)

    # Compact representation for review
    compact = []
    for p in papers[:50]:  # Review first 50
        compact.append({
            "paper_id": p.get("paper_id"),
            "title": p.get("title"),
            "method_name": p.get("method", {}).get("name"),
            "method_category": p.get("method", {}).get("category"),
            "problem": p.get("problem", {}).get("statement", "")[:100],
            "n_claims": len(p.get("claims", [])),
            "n_limitations": len(p.get("limitations", {}).get("acknowledged", [])),
            "n_inferred_limitations": len(p.get("limitations", {}).get("inferred", [])),
            "extraction_confidence": p.get("extraction_confidence"),
            "_has_error": "_error" in p,
        })

    user_msg = f"""Review these {len(compact)} paper extraction records for quality issues.

RECORDS:
{json.dumps(compact, indent=1, ensure_ascii=False)}

Respond with ONLY the JSON quality report."""

    result = client.ask_json(INGESTION_CRITIQUE_PROMPT, user_msg)
    save_json(result, f"{output_dir}/quality_ingestion.json")

    quality = result.get("overall_quality", "?")
    n_issues = len(result.get("issues", []))
    log.info(f"Ingestion quality: {quality} ({n_issues} issues found)")

    return result


# ── Cluster Quality Check ────────────────────────────────────────────────────

CLUSTER_CRITIQUE_PROMPT = """You are a quality auditor for research clustering. Review this cluster analysis and challenge it.

Play devil's advocate:
1. Are any clusters too broad? ("deep learning" contains everything)
2. Are any clusters too narrow? (1-2 papers each, could merge)
3. Do the cluster labels actually distinguish meaningfully different approaches?
4. Are there obvious papers assigned to wrong clusters?
5. Are the "sparse regions" genuinely gaps or just impossible combinations?
6. Is any "dense region" actually two different things lumped together?

RESPOND WITH ONLY JSON:
{
  "cluster_quality": "GOOD | ACCEPTABLE | NEEDS_REVIEW",
  "challenges": [
    {
      "target": "M2 or sparse_region M1_P3",
      "challenge_type": "too_broad | too_narrow | mislabeled | false_gap | over_merged",
      "description": "The challenge",
      "suggested_action": "What to do about it"
    }
  ],
  "suggested_merges": [
    {"cluster_a": "M3", "cluster_b": "M5", "reason": "Both are retrieval-based methods"}
  ],
  "suggested_splits": [
    {"cluster": "M1", "into": ["M1a: encoder-only", "M1b: decoder-only"], "reason": "Fundamentally different architectures"}
  ],
  "false_gaps_identified": [
    {"cell": "M2_P4", "reason": "This combination doesn't make physical/logical sense because..."}
  ],
  "summary": "1-2 sentence quality assessment"
}"""


def critique_clusters(config: dict) -> dict:
    """Run quality check on clustering output."""
    log.info("Running cluster quality check...")
    output_dir = config["pipeline"]["output_dir"]
    space_map = load_json(f"{output_dir}/research_space_map.json")

    client = ClaudeClient(config=config)

    user_msg = f"""Review this research space clustering for quality.

CLUSTER MAP:
{json.dumps(space_map, indent=1, ensure_ascii=False)[:30000]}

Challenge the clusters aggressively. Are they real? Are the gaps real?
Respond with ONLY the JSON quality report."""

    result = client.ask_json(CLUSTER_CRITIQUE_PROMPT, user_msg)
    save_json(result, f"{output_dir}/quality_clusters.json")

    quality = result.get("cluster_quality", "?")
    n_challenges = len(result.get("challenges", []))
    log.info(f"Cluster quality: {quality} ({n_challenges} challenges)")

    return result


# ── Idea Quality Check (Reviewer Simulation) ─────────────────────────────────

REVIEWER_PROMPT = """You are a tough but fair peer reviewer at a top venue (NeurIPS/ICML/ACL).
Review these research ideas as if they were submitted as short proposals.

For each idea, give:
1. A score (1-10, where 6 = borderline accept at a top venue)
2. The strongest objection a reviewer would raise
3. Whether the hypothesis is actually testable as stated
4. Whether the "either-way value" claim holds up
5. Any fatal flaw that wasn't caught

RESPOND WITH ONLY JSON:
{
  "reviews": [
    {
      "idea_id": "IDEA-001",
      "reviewer_score": 7,
      "strengths": ["What's good about this idea"],
      "weaknesses": ["What's wrong"],
      "fatal_flaw": null,
      "strongest_objection": "The specific objection",
      "hypothesis_testable": true,
      "either_way_holds": true,
      "missing_baselines": ["Baseline X that must be compared"],
      "verdict": "ACCEPT | BORDERLINE | REJECT",
      "improvement_suggestions": ["How to make it stronger"]
    }
  ],
  "ranking_agrees_with_pipeline": true,
  "suggested_reranking": ["IDEA-003", "IDEA-001", "IDEA-002"],
  "summary": "Overall assessment"
}"""


def simulate_reviewer(config: dict) -> dict:
    """Simulate peer review of generated ideas."""
    log.info("Running reviewer simulation...")
    output_dir = config["pipeline"]["output_dir"]
    ideas = load_json(f"{output_dir}/idea_report.json")

    client = ClaudeClient(config=config)

    user_msg = f"""Review these research ideas as a tough peer reviewer.

IDEAS:
{json.dumps(ideas.get("ideas", []), indent=1, ensure_ascii=False)[:30000]}

Be harsh but fair. Score each idea. Find fatal flaws.
Respond with ONLY the JSON review report."""

    result = client.ask_json(REVIEWER_PROMPT, user_msg)
    save_json(result, f"{output_dir}/quality_reviewer.json")

    for r in result.get("reviews", []):
        verdict = r.get("verdict", "?")
        score = r.get("reviewer_score", "?")
        log.info(f"  {r.get('idea_id','?')}: {verdict} (score: {score}/10)")

    return result


# ── Human Checkpoint ─────────────────────────────────────────────────────────

def save_human_checkpoint(config: dict):
    """
    Save a YAML checkpoint file for human review.
    The researcher can edit gaps, add their own, remove false positives,
    then the pipeline continues from their edits.
    """
    output_dir = config["pipeline"]["output_dir"]
    gaps = load_json(f"{output_dir}/gap_analysis.json")
    conflicts = load_json(f"{output_dir}/conflict_report.json")

    # Build human-friendly checkpoint
    checkpoint = {
        "_instructions": (
            "Review the gaps below. You can:\n"
            "  - Set 'approved: false' to remove a gap\n"
            "  - Edit 'priority_override' to change ranking\n"
            "  - Add new gaps under 'custom_gaps'\n"
            "  - Set 'proceed: true' when ready\n"
            "Save this file and re-run the pipeline."
        ),
        "generated": datetime.now().isoformat(),
        "proceed": False,
        "gaps": [],
        "custom_gaps": [
            {
                "title": "YOUR GAP HERE",
                "description": "Describe the gap you've identified",
                "type": "VOID | CONFLICT | WEAKNESS | ASSUMPTION",
                "priority_override": 20,
                "approved": False,
            }
        ],
    }

    for gap in gaps.get("gaps", []):
        checkpoint["gaps"].append({
            "gap_id": gap.get("gap_id", ""),
            "title": gap.get("title", ""),
            "type": gap.get("type", ""),
            "description": gap.get("description", ""),
            "priority_score": gap.get("scoring", {}).get("priority_score", 0),
            "priority_override": None,
            "approved": True,
            "notes": "",
        })

    # Save as YAML for easy human editing
    checkpoint_path = f"{output_dir}/CHECKPOINT_REVIEW.yaml"
    with open(checkpoint_path, "w", encoding="utf-8") as f:
        yaml.dump(checkpoint, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    log.info(f"\n{'='*60}")
    log.info(f"  HUMAN CHECKPOINT SAVED")
    log.info(f"  Edit: {checkpoint_path}")
    log.info(f"  Set 'proceed: true' when ready")
    log.info(f"{'='*60}")

    return checkpoint_path


def load_human_checkpoint(config: dict) -> dict:
    """Load and apply human-reviewed checkpoint."""
    output_dir = config["pipeline"]["output_dir"]
    checkpoint_path = f"{output_dir}/CHECKPOINT_REVIEW.yaml"

    if not Path(checkpoint_path).exists():
        log.info("No human checkpoint found, proceeding automatically")
        return {"status": "auto", "modified": False}

    with open(checkpoint_path, "r", encoding="utf-8") as f:
        checkpoint = yaml.safe_load(f)

    if not checkpoint.get("proceed", False):
        log.info("Human checkpoint exists but 'proceed' is still False")
        log.info(f"Edit {checkpoint_path} and set proceed: true")
        return {"status": "waiting", "modified": False}

    # Apply human edits to gap analysis
    gaps = load_json(f"{output_dir}/gap_analysis.json")

    # Filter out rejected gaps
    approved_ids = set()
    overrides = {}
    for g in checkpoint.get("gaps", []):
        if g.get("approved", True):
            approved_ids.add(g.get("gap_id", ""))
            if g.get("priority_override") is not None:
                overrides[g["gap_id"]] = g["priority_override"]

    original_count = len(gaps.get("gaps", []))
    gaps["gaps"] = [
        g for g in gaps.get("gaps", [])
        if g.get("gap_id", "") in approved_ids
    ]

    # Apply priority overrides
    for g in gaps["gaps"]:
        gid = g.get("gap_id", "")
        if gid in overrides:
            g["scoring"]["priority_score"] = overrides[gid]
            g["scoring"]["_human_override"] = True

    # Add custom gaps
    for i, custom in enumerate(checkpoint.get("custom_gaps", [])):
        if custom.get("approved", False) and custom.get("title", "") != "YOUR GAP HERE":
            custom_gap = {
                "gap_id": f"GAP-CUSTOM-{i+1}",
                "type": custom.get("type", "VOID"),
                "title": custom.get("title", ""),
                "description": custom.get("description", ""),
                "evidence": {"source": "human expert input"},
                "scoring": {
                    "priority_score": custom.get("priority_override", 15),
                    "_human_added": True,
                },
                "potential_direction": custom.get("description", ""),
            }
            gaps["gaps"].append(custom_gap)

    # Update counts
    gaps["total_gaps"] = len(gaps["gaps"])
    gaps["_human_reviewed"] = True
    gaps["_human_review_date"] = datetime.now().isoformat()

    # Save updated gaps
    save_json(gaps, f"{output_dir}/gap_analysis.json")

    removed = original_count - len([g for g in gaps["gaps"] if not g.get("gap_id", "").startswith("GAP-CUSTOM")])
    added = len([g for g in gaps["gaps"] if g.get("gap_id", "").startswith("GAP-CUSTOM")])
    overridden = len(overrides)

    log.info(f"Human checkpoint applied: {removed} gaps removed, {added} added, {overridden} re-prioritized")
    return {"status": "applied", "modified": True, "removed": removed, "added": added}


# ── Run All Quality Checks ───────────────────────────────────────────────────

def run_quality_checks(config: dict, stage: str) -> dict:
    """Run quality checks for a specific pipeline stage."""
    if stage == "ingestion":
        return critique_ingestion(config)
    elif stage == "clusters":
        return critique_clusters(config)
    elif stage == "ideas":
        return simulate_reviewer(config)
    else:
        log.warning(f"Unknown quality check stage: {stage}")
        return {}
