"""
step3_conflicts.py — Cross-Paper Conflict Detection
Scans paper corpus for contradictions, reproduction failures, scope conflicts.
Outputs: output/conflict_report.json, output/conflict_report.md
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

SYSTEM_PROMPT = """You are a conflict detection agent. You systematically scan research paper records for contradictions, disagreements, and inconsistencies between papers.

RESPOND WITH ONLY valid JSON — no markdown fences, no explanation.

Conflict types to detect:
- RESULT_CONFLICT: Same method/dataset, different performance numbers
- CLAIM_CONFLICT: Contradictory theoretical or empirical claims
- ASSUMPTION_CONFLICT: One paper's assumption is contradicted by another's evidence
- REPRODUCTION_CONFLICT: Same experiment, different results
- SCOPE_CONFLICT: Paper A claims generality, Paper B shows failure case

Output this JSON:
{
  "total_pairs_compared": 100,
  "conflicts": [
    {
      "conflict_id": "CONF-001",
      "type": "RESULT_CONFLICT | CLAIM_CONFLICT | ASSUMPTION_CONFLICT | REPRODUCTION_CONFLICT | SCOPE_CONFLICT",
      "severity": "HIGH | MEDIUM | LOW",
      "paper_a": {
        "paper_id": "id",
        "title": "title",
        "position": "What Paper A claims (exact claim)",
        "evidence_type": "empirical | theoretical",
        "evidence_strength": "strong | moderate | weak"
      },
      "paper_b": {
        "paper_id": "id",
        "title": "title",
        "position": "What Paper B claims (contradicting Paper A)",
        "evidence_type": "empirical | theoretical",
        "evidence_strength": "strong | moderate | weak"
      },
      "contextual_differences": {
        "dataset": "same | different — specify",
        "evaluation_protocol": "same | different — specify",
        "scale": "same | different — specify",
        "domain": "same | different — specify"
      },
      "possible_explanations": [
        "methodological difference that could explain conflict",
        "contextual difference that could explain conflict"
      ],
      "resolution_status": "RESOLVED | PARTIALLY_RESOLVED | UNRESOLVED",
      "resolution_path": "What experiment or analysis would resolve this",
      "research_opportunity": "1-2 sentences on what investigation this suggests"
    }
  ],
  "conflict_clusters": [
    {
      "cluster_title": "Thematic title for related conflicts",
      "conflict_ids": ["CONF-001", "CONF-003"],
      "pattern": "What systemic disagreement these conflicts reveal",
      "meta_finding": "What the cluster tells us about the field",
      "resolution_approach": "Study design that would address the whole cluster"
    }
  ],
  "summary": {
    "high_severity": 2,
    "medium_severity": 3,
    "low_severity": 1,
    "unresolved": 4,
    "clusters_found": 2
  }
}

Rules:
- Every conflict must cite SPECIFIC claims from BOTH papers
- Always document contextual differences (dataset, scale, domain, protocol)
- Propose at least 2 possible explanations per conflict
- Resolution paths must be specific and feasible experiments
- Group related conflicts into clusters with meta-findings
- LOW severity conflicts: document briefly but don't elaborate
- If no conflicts found, return empty conflicts array (this is valid for small/homogeneous corpora)
"""


def prepare_claims_for_conflict_scan(papers: list) -> str:
    """Extract claims and results from papers for efficient conflict scanning."""
    summaries = []
    for p in papers:
        if "_error" in p:
            continue
        s = {
            "paper_id": p.get("paper_id", "unknown"),
            "title": p.get("title", ""),
            "year": p.get("year"),
            "method": {
                "name": p.get("method", {}).get("name", ""),
                "category": p.get("method", {}).get("category", ""),
                "novelty_claim": p.get("method", {}).get("novelty_claim", ""),
            },
            "datasets": [d.get("name", "") for d in p.get("datasets", [])],
            "metrics": p.get("metrics", []),
            "claims": p.get("claims", []),
            "limitations": p.get("limitations", {}),
            "failure_cases": p.get("failure_cases", {}),
        }
        summaries.append(s)
    return json.dumps(summaries, indent=1, ensure_ascii=False)


def generate_conflict_report_md(conflict_data: dict) -> str:
    """Generate a readable markdown report from conflict detection results."""
    lines = ["# Conflict Detection Report\n"]
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

    summary = conflict_data.get("summary", {})
    lines.append("## Summary\n")
    lines.append(f"- Total conflicts detected: {len(conflict_data.get('conflicts', []))}")
    lines.append(f"- High severity: {summary.get('high_severity', 0)}")
    lines.append(f"- Medium severity: {summary.get('medium_severity', 0)}")
    lines.append(f"- Low severity: {summary.get('low_severity', 0)}")
    lines.append(f"- Unresolved: {summary.get('unresolved', 0)}")
    lines.append(f"- Conflict clusters: {summary.get('clusters_found', 0)}")

    # High-priority conflicts
    conflicts = conflict_data.get("conflicts", [])
    high = [c for c in conflicts if c.get("severity") == "HIGH"]
    med = [c for c in conflicts if c.get("severity") == "MEDIUM"]

    if high:
        lines.append("\n## High-Severity Conflicts\n")
        for c in high:
            lines.append(f"### {c['conflict_id']}: {c['type']}")
            lines.append(f"- **Paper A** ({c['paper_a']['paper_id']}): {c['paper_a']['position']}")
            lines.append(f"- **Paper B** ({c['paper_b']['paper_id']}): {c['paper_b']['position']}")
            ctx = c.get("contextual_differences", {})
            if ctx:
                lines.append(f"- **Key difference**: Dataset={ctx.get('dataset','?')}, Scale={ctx.get('scale','?')}")
            lines.append(f"- **Status**: {c.get('resolution_status','?')}")
            lines.append(f"- **Resolution path**: {c.get('resolution_path','?')}")
            lines.append(f"- **Opportunity**: {c.get('research_opportunity','?')}\n")

    if med:
        lines.append("\n## Medium-Severity Conflicts\n")
        for c in med:
            lines.append(f"### {c['conflict_id']}: {c['type']}")
            lines.append(f"- **Paper A**: {c['paper_a']['position']}")
            lines.append(f"- **Paper B**: {c['paper_b']['position']}")
            lines.append(f"- **Opportunity**: {c.get('research_opportunity','?')}\n")

    # Conflict clusters
    clusters = conflict_data.get("conflict_clusters", [])
    if clusters:
        lines.append("\n## Conflict Clusters\n")
        for cc in clusters:
            lines.append(f"### {cc['cluster_title']}")
            lines.append(f"- Conflicts: {', '.join(cc.get('conflict_ids', []))}")
            lines.append(f"- Pattern: {cc.get('pattern', '?')}")
            lines.append(f"- Meta-finding: {cc.get('meta_finding', '?')}")
            lines.append(f"- Resolution: {cc.get('resolution_approach', '?')}\n")

    return "\n".join(lines)


def run_conflict_detection(config: dict) -> dict:
    """Run conflict detection on the paper corpus."""
    print_banner("STEP 3: Conflict Detection")

    cfg = config["pipeline"]
    output_dir = cfg["output_dir"]

    # Load corpus
    corpus = load_json(f"{output_dir}/paper_corpus.json")
    papers = [p for p in corpus["papers"] if "_error" not in p]
    log.info(f"Scanning {len(papers)} papers for conflicts...")

    client = ClaudeClient(config=config)

    # Prepare claims
    claims_text = prepare_claims_for_conflict_scan(papers)

    # For large corpora, chunk the comparison
    MAX_CHARS = 50000
    if len(claims_text) <= MAX_CHARS:
        user_msg = f"""Scan these {len(papers)} paper records for conflicts and contradictions.

PAPER CLAIMS AND RESULTS:
{claims_text}

Respond with ONLY the JSON conflict report."""

        conflict_data = client.ask_json(SYSTEM_PROMPT, user_msg)
    else:
        # Process in overlapping windows for large corpora
        log.info("Large corpus — processing in overlapping windows...")
        all_conflicts = []
        chunk_size = 25
        for i in range(0, len(papers), chunk_size // 2):  # 50% overlap
            chunk = papers[i:i + chunk_size]
            if len(chunk) < 3:
                break
            log.info(f"  Window {i // (chunk_size // 2) + 1}: papers {i+1}-{i+len(chunk)}")
            chunk_text = prepare_claims_for_conflict_scan(chunk)
            user_msg = f"""Scan these {len(chunk)} papers for conflicts.

PAPER RECORDS:
{chunk_text}

Respond with ONLY the JSON conflict report."""
            result = client.ask_json(SYSTEM_PROMPT, user_msg)
            all_conflicts.extend(result.get("conflicts", []))

        # Deduplicate and cluster
        merge_msg = f"""Merge and deduplicate these conflict detections into a unified report.
Remove duplicate conflicts (same two papers, same issue).
Group related conflicts into clusters.

RAW CONFLICTS:
{json.dumps(all_conflicts, indent=1)[:50000]}

Respond with the unified JSON conflict report using the standard schema."""

        conflict_data = client.ask_json(SYSTEM_PROMPT, merge_msg)

    # Save outputs
    save_json(conflict_data, f"{output_dir}/conflict_report.json")
    report_md = generate_conflict_report_md(conflict_data)
    save_markdown(report_md, f"{output_dir}/conflict_report.md")

    n_conflicts = len(conflict_data.get("conflicts", []))
    n_high = len([c for c in conflict_data.get("conflicts", []) if c.get("severity") == "HIGH"])
    log.info(f"\nConflict detection complete: {n_conflicts} conflicts ({n_high} high severity)")
    log.info(f"API stats: {client.stats()}")

    return conflict_data


if __name__ == "__main__":
    config = load_config()
    run_conflict_detection(config)
