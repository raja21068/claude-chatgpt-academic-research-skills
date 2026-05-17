"""
step6_novelty.py — Novelty Verification (v2 — Multi-Model + Citation Graph)
1. Keyword search on Semantic Scholar + arXiv
2. Citation graph expansion (1 hop from top seeds)
3. Multi-model consensus (Claude + optional GPT-4 + Gemini)
Verdicts: PROCEED / PROCEED_WITH_CAUTION / PIVOT / ABANDON
Outputs: output/novelty_report.json, output/novelty_report.md
"""

import sys, json, time, urllib.parse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from utils import (ClaudeClient, load_config, load_json, save_json,
                   save_markdown, log, print_banner)

# ── External Search ──────────────────────────────────────────────────────────

def search_semantic_scholar(query, limit=10):
    import requests
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {"query": query, "limit": limit,
              "fields": "title,year,venue,abstract,citationCount,url,paperId"}
    try:
        resp = requests.get(url, params=params, timeout=15)
        if resp.status_code == 200:
            return resp.json().get("data", [])
        if resp.status_code == 429:
            log.warning("SS rate limit — waiting 5s")
            time.sleep(5)
            resp = requests.get(url, params=params, timeout=15)
            if resp.status_code == 200:
                return resp.json().get("data", [])
        return []
    except Exception as e:
        log.warning(f"SS search failed: {e}")
        return []


def search_arxiv(query, max_results=10):
    import requests, xml.etree.ElementTree as ET
    url = "http://export.arxiv.org/api/query"
    params = {"search_query": f"all:{query}", "start": 0,
              "max_results": max_results, "sortBy": "submittedDate",
              "sortOrder": "descending"}
    try:
        resp = requests.get(url, params=params, timeout=15)
        if resp.status_code != 200: return []
        root = ET.fromstring(resp.text)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        results = []
        for entry in root.findall("atom:entry", ns):
            t = entry.find("atom:title", ns)
            s = entry.find("atom:summary", ns)
            pub = entry.find("atom:published", ns)
            link = entry.find("atom:id", ns)
            results.append({
                "title": t.text.strip() if t is not None else "",
                "abstract": s.text.strip()[:500] if s is not None else "",
                "published": pub.text[:10] if pub is not None else "",
                "url": link.text.strip() if link is not None else "",
            })
        return results
    except Exception as e:
        log.warning(f"arXiv search failed: {e}")
        return []


def run_literature_search(idea):
    """Multi-source search for a single idea."""
    title = idea.get("title", "")
    hypothesis = idea.get("hypothesis", {}).get("statement", "")
    method = idea.get("method_sketch", {}).get("approach", "")
    closest = idea.get("positioning", {}).get("closest_work", "")

    queries = set()
    if title: queries.add(title[:100])
    if method:
        queries.add(" ".join(method.split()[:8]))
    if closest: queries.add(closest[:80])
    queries = list(queries)[:4]

    all_ss, all_arxiv = [], []
    for q in queries:
        log.info(f"    Searching: '{q[:60]}...'")
        all_ss.extend(search_semantic_scholar(q, limit=5))
        time.sleep(1)
        all_arxiv.extend(search_arxiv(q, max_results=5))
        time.sleep(0.5)

    # Deduplicate
    seen = set()
    unique_ss = []
    for r in all_ss:
        t = r.get("title", "").lower().strip()
        if t and t not in seen:
            seen.add(t); unique_ss.append(r)
    unique_arxiv = []
    for r in all_arxiv:
        t = r.get("title", "").lower().strip()
        if t and t not in seen:
            seen.add(t); unique_arxiv.append(r)

    return {
        "queries_used": queries,
        "semantic_scholar_results": unique_ss[:10],
        "arxiv_results": unique_arxiv[:10],
        "total_unique_papers_found": len(unique_ss) + len(unique_arxiv),
    }


SYSTEM_PROMPT = """You are a novelty verification agent. Assess whether a research idea is genuinely novel by analyzing search results from academic databases AND citation-expanded results.

BE BRUTALLY HONEST. A killed idea saves months; a false positive wastes them.

RESPOND WITH ONLY valid JSON:
{
  "idea_id": "IDEA-001",
  "title": "idea title",
  "core_claims_assessment": [
    {"claim_number":1,"claim":"the claim","novelty_level":"HIGH|MEDIUM|LOW",
     "closest_prior_work":"Paper title + year","delta":"what differentiates"}
  ],
  "closest_papers": [
    {"title":"paper","year":2025,"venue":"venue",
     "overlap_type":"method+problem|method_only|problem_only|approach",
     "overlap_level":"HIGH|MEDIUM|LOW","key_difference":"difference",
     "found_via":"keyword|citation_expansion"}
  ],
  "concurrent_work_threats": [
    {"paper":"title","date":"2025-03","threat_level":"HIGH|MEDIUM|LOW",
     "differentiation_strategy":"how to differentiate"}
  ],
  "overall_assessment": {
    "novelty_score": 7,
    "verdict": "PROCEED|PROCEED_WITH_CAUTION|PIVOT|ABANDON",
    "key_differentiator": "what makes unique",
    "reviewer_risk": "what reviewer would cite as prior work",
    "positioning_advice": "how to frame contribution"
  }
}

Verdict rules:
- PROCEED: No overlapping work, high confidence
- PROCEED_WITH_CAUTION: Overlap exists but clear differentiation possible
- PIVOT: Very similar recent work, needs reframing
- ABANDON: Core contribution already published

Rules:
- Assess ACTUAL overlap, not superficial similarity
- Pay special attention to papers found via CITATION EXPANSION — these are indirect prior work the authors might miss
- Check for concurrent work in last 6 months specifically
- "Apply X to Y" is NOT novel unless genuinely surprising insights emerge
"""


def generate_novelty_report_md(report):
    lines = ["# Novelty Verification Report (v2 — Multi-Model)\n"]
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

    summary = report.get("summary", {})
    lines.append("## Summary\n")
    lines.append(f"- Ideas verified: {summary.get('total_verified', 0)}")
    lines.append(f"- Models used: {summary.get('models_used', ['claude'])}")
    lines.append(f"- Citation expansion: {'enabled' if summary.get('citation_expansion') else 'disabled'}")
    lines.append(f"- PROCEED: {summary.get('proceed', 0)}")
    lines.append(f"- PROCEED WITH CAUTION: {summary.get('proceed_with_caution', 0)}")
    lines.append(f"- PIVOT: {summary.get('pivot', 0)}")
    lines.append(f"- ABANDON: {summary.get('abandon', 0)}")
    lines.append(f"- Total papers found: {summary.get('total_search_results', 0)} (keyword) + {summary.get('total_citation_expanded', 0)} (citation expansion)")

    for v in report.get("verifications", []):
        consensus = v.get("consensus", v.get("overall_assessment", {}))
        verdict = consensus.get("verdict", "?")
        emoji = {"PROCEED":"✅","PROCEED_WITH_CAUTION":"⚠️","PIVOT":"🔄","ABANDON":"❌"}.get(verdict, "?")
        score = consensus.get("novelty_score", "?")
        agree = consensus.get("models_agree", True)

        lines.append(f"\n## {emoji} {v.get('idea_id','?')}: {v.get('title','?')}")
        lines.append(f"**Verdict: {verdict}** (score: {score}/10)")
        if not agree:
            lines.append(f"⚡ **Models disagree** — review individual assessments")
            details = consensus.get("disagreement_details", {})
            for model, mv in details.get("verdicts_by_model", {}).items():
                ms = details.get("scores_by_model", {}).get(model, "?")
                lines.append(f"  - {model}: {mv} ({ms}/10)")

        # Assessment details (from the primary model or merged)
        assessment = v.get("assessment", v)
        claims = assessment.get("core_claims_assessment", [])
        if claims:
            lines.append("\n### Core claims\n")
            lines.append("| # | Claim | Novelty | Closest Work | Delta |")
            lines.append("|---|-------|---------|-------------|-------|")
            for c in claims:
                lines.append(f"| {c.get('claim_number','')} | {c.get('claim','')} | {c.get('novelty_level','')} | {c.get('closest_prior_work','')} | {c.get('delta','')} |")

        closest = assessment.get("closest_papers", [])
        if closest:
            lines.append("\n### Closest prior work\n")
            for cp in closest[:5]:
                via = f" [via {cp.get('found_via','keyword')}]" if cp.get("found_via") else ""
                lines.append(f"- **{cp.get('title','')}** ({cp.get('year','')}, {cp.get('venue','')}) — {cp.get('overlap_level','')} overlap{via}")
                lines.append(f"  > {cp.get('key_difference','')}")

        threats = assessment.get("concurrent_work_threats", [])
        if threats:
            lines.append("\n### Concurrent work threats\n")
            for t in threats:
                lines.append(f"- ⚠️ **{t.get('paper','')}** ({t.get('date','')}) — {t.get('threat_level','')}")
                lines.append(f"  > {t.get('differentiation_strategy','')}")

        overall = assessment.get("overall_assessment", consensus)
        lines.append(f"\n**Key differentiator**: {overall.get('key_differentiator','')}")
        lines.append(f"**Reviewer risk**: {overall.get('reviewer_risk','')}")
        lines.append(f"**Positioning**: {overall.get('positioning_advice','')}")

    return "\n".join(lines)


def run_novelty_verification(config):
    """Run novelty verification with multi-model + citation expansion."""
    print_banner("STEP 6: Novelty Verification (Multi-Model + Citations)")

    cfg = config["pipeline"]
    output_dir = cfg["output_dir"]
    mm_cfg = config.get("multi_model", {})
    use_multi_model = mm_cfg.get("enabled", False)
    use_citation_expansion = config.get("citation_expansion", {}).get("enabled", True)

    ideas = load_json(f"{output_dir}/idea_report.json").get("ideas", [])
    log.info(f"Verifying novelty of {len(ideas)} ideas...")
    log.info(f"  Multi-model: {'ON' if use_multi_model else 'OFF (Claude only)'}")
    log.info(f"  Citation expansion: {'ON' if use_citation_expansion else 'OFF'}")

    # Initialize verifier
    verifier = None
    if use_multi_model:
        try:
            from multi_model import MultiModelVerifier
            verifier = MultiModelVerifier(config)
        except Exception as e:
            log.warning(f"Multi-model init failed ({e}), using Claude only")

    client = ClaudeClient(config=config) if not verifier else None
    verifications = []
    total_search = 0
    total_citation = 0
    models_used = set()

    for i, idea in enumerate(ideas, 1):
        idea_id = idea.get("idea_id", f"IDEA-{i}")
        log.info(f"\n[{i}/{len(ideas)}] {idea_id}: {idea.get('title','?')}")

        # 1. Keyword search
        search_results = run_literature_search(idea)
        total_search += search_results["total_unique_papers_found"]
        log.info(f"  Keyword search: {search_results['total_unique_papers_found']} papers")

        # 2. Citation graph expansion
        expanded_results = None
        if use_citation_expansion:
            try:
                from citation_graph import deep_novelty_search
                expanded_results = deep_novelty_search(idea, search_results)
                n_expanded = len(expanded_results.get("expanded_papers", []))
                total_citation += n_expanded
                log.info(f"  Citation expansion: {n_expanded} additional papers")

                # Merge expanded into search results for the LLM
                search_results["citation_expanded_papers"] = expanded_results.get("expanded_papers", [])[:10]
            except Exception as e:
                log.warning(f"  Citation expansion failed: {e}")

        # 3. Novelty assessment
        if verifier:
            # Multi-model consensus
            result = verifier.verify(idea, search_results)
            models_used.update(result.get("models_queried", []))

            # Also get detailed assessment from Claude
            assessment = _get_detailed_assessment(config, idea, search_results)
            result["assessment"] = assessment
            result["title"] = idea.get("title", "")
        else:
            # Claude only
            assessment = _get_detailed_assessment(config, idea, search_results)
            result = {
                "idea_id": idea_id,
                "title": idea.get("title", ""),
                "assessment": assessment,
                "consensus": assessment.get("overall_assessment", {}),
                "n_models_used": 1,
                "models_queried": ["claude"],
            }
            models_used.add("claude")

        result["_search_meta"] = {
            "queries": search_results["queries_used"],
            "keyword_results": search_results["total_unique_papers_found"],
            "citation_expanded": len(search_results.get("citation_expanded_papers", [])),
        }
        verifications.append(result)

        verdict = result.get("consensus", {}).get("verdict", "?")
        score = result.get("consensus", {}).get("novelty_score", "?")
        log.info(f"  → {verdict} (score: {score}/10)")

    # Build report
    verdicts = [v.get("consensus", {}).get("verdict", "") for v in verifications]
    report = {
        "verification_date": datetime.now().strftime("%Y-%m-%d"),
        "pipeline_version": "v2_multi_model",
        "total_ideas": len(ideas),
        "verifications": verifications,
        "summary": {
            "total_verified": len(verifications),
            "models_used": list(models_used),
            "citation_expansion": use_citation_expansion,
            "proceed": verdicts.count("PROCEED"),
            "proceed_with_caution": verdicts.count("PROCEED_WITH_CAUTION"),
            "pivot": verdicts.count("PIVOT"),
            "abandon": verdicts.count("ABANDON"),
            "total_search_results": total_search,
            "total_citation_expanded": total_citation,
        },
    }

    save_json(report, f"{output_dir}/novelty_report.json")
    save_markdown(generate_novelty_report_md(report), f"{output_dir}/novelty_report.md")

    log.info(f"\nNovelty verification complete:")
    log.info(f"  PROCEED: {verdicts.count('PROCEED')}")
    log.info(f"  PROCEED WITH CAUTION: {verdicts.count('PROCEED_WITH_CAUTION')}")
    log.info(f"  PIVOT: {verdicts.count('PIVOT')}")
    log.info(f"  ABANDON: {verdicts.count('ABANDON')}")
    log.info(f"  Models used: {list(models_used)}")
    if client:
        log.info(f"  API stats: {client.stats()}")

    return report


def _get_detailed_assessment(config, idea, search_results):
    """Get detailed novelty assessment from Claude."""
    client = ClaudeClient(config=config)

    # Include citation-expanded papers if available
    extra_section = ""
    expanded = search_results.get("citation_expanded_papers", [])
    if expanded:
        extra_section = f"""

CITATION-EXPANDED PAPERS (found via citation graph, not keyword search):
{json.dumps(expanded, indent=1, ensure_ascii=False)[:6000]}

Pay special attention to these — they represent indirect prior work the authors might miss."""

    user_msg = f"""Assess novelty of this research idea.

IDEA:
{json.dumps(idea, indent=2, ensure_ascii=False)[:8000]}

KEYWORD SEARCH RESULTS (Semantic Scholar):
{json.dumps(search_results['semantic_scholar_results'], indent=1, ensure_ascii=False)[:6000]}

KEYWORD SEARCH RESULTS (arXiv):
{json.dumps(search_results['arxiv_results'], indent=1, ensure_ascii=False)[:6000]}
{extra_section}

QUERIES USED: {search_results['queries_used']}

Be brutally honest. Respond with ONLY the JSON assessment."""

    return client.ask_json(SYSTEM_PROMPT, user_msg)


if __name__ == "__main__":
    run_novelty_verification(load_config())
