"""
citation_graph.py — Citation Graph Traversal
Goes beyond keyword search: finds papers-that-cite-papers-that-cite,
expands the search net for novelty verification.
"""

import json
import time
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))
from utils import log

try:
    import requests
except ImportError:
    raise ImportError("requests required. Run: pip install requests")


SS_API = "https://api.semanticscholar.org/graph/v1"
FIELDS = "title,year,venue,abstract,citationCount,url"


def _ss_get(url: str, params: dict, retries: int = 2) -> Optional[dict]:
    """Semantic Scholar API request with retry."""
    for attempt in range(retries):
        try:
            resp = requests.get(url, params=params, timeout=15)
            if resp.status_code == 200:
                return resp.json()
            elif resp.status_code == 429:
                wait = 5 * (attempt + 1)
                log.warning(f"Rate limit, waiting {wait}s...")
                time.sleep(wait)
            else:
                log.warning(f"SS API returned {resp.status_code}")
                return None
        except Exception as e:
            log.warning(f"SS API error: {e}")
            time.sleep(2)
    return None


def search_papers(query: str, limit: int = 10) -> list[dict]:
    """Search Semantic Scholar for papers."""
    data = _ss_get(f"{SS_API}/paper/search", {
        "query": query, "limit": limit, "fields": FIELDS
    })
    return data.get("data", []) if data else []


def get_paper_details(paper_id: str) -> Optional[dict]:
    """Get full details for a paper by its Semantic Scholar ID."""
    data = _ss_get(f"{SS_API}/paper/{paper_id}", {"fields": FIELDS})
    return data


def get_citations(paper_id: str, limit: int = 20) -> list[dict]:
    """Get papers that CITE this paper (forward citations)."""
    data = _ss_get(f"{SS_API}/paper/{paper_id}/citations", {
        "fields": FIELDS, "limit": limit
    })
    if data:
        return [c.get("citingPaper", {}) for c in data.get("data", []) if c.get("citingPaper")]
    return []


def get_references(paper_id: str, limit: int = 20) -> list[dict]:
    """Get papers that this paper REFERENCES (backward citations)."""
    data = _ss_get(f"{SS_API}/paper/{paper_id}/references", {
        "fields": FIELDS, "limit": limit
    })
    if data:
        return [r.get("citedPaper", {}) for r in data.get("data", []) if r.get("citedPaper")]
    return []


def expand_search_via_citations(
    seed_papers: list[dict],
    max_depth: int = 1,
    max_papers_per_hop: int = 10,
) -> list[dict]:
    """
    Expand the search space via citation traversal.

    Starting from seed papers found via keyword search:
    1. Get papers that cite the seeds (forward)
    2. Get papers that the seeds reference (backward)
    3. Optionally go one more hop

    This catches related work that uses different terminology.
    """
    all_papers = {}
    seen_ids = set()

    # Add seeds
    for p in seed_papers:
        pid = p.get("paperId")
        if pid and pid not in seen_ids:
            all_papers[pid] = p
            seen_ids.add(pid)

    # Traverse
    current_frontier = [p.get("paperId") for p in seed_papers if p.get("paperId")]

    for depth in range(max_depth):
        next_frontier = []
        log.info(f"  Citation hop {depth + 1}: expanding from {len(current_frontier)} papers...")

        for pid in current_frontier[:5]:  # Limit to 5 seeds per hop to stay under rate limits
            time.sleep(1)  # Rate limit

            # Forward citations (who cites this?)
            citations = get_citations(pid, limit=max_papers_per_hop)
            for c in citations:
                cid = c.get("paperId")
                if cid and cid not in seen_ids:
                    c["_found_via"] = f"cited_by:{pid}"
                    c["_hop_depth"] = depth + 1
                    all_papers[cid] = c
                    seen_ids.add(cid)
                    next_frontier.append(cid)

            # Backward references (what does this cite?)
            references = get_references(pid, limit=max_papers_per_hop)
            for r in references:
                rid = r.get("paperId")
                if rid and rid not in seen_ids:
                    r["_found_via"] = f"referenced_by:{pid}"
                    r["_hop_depth"] = depth + 1
                    all_papers[rid] = r
                    seen_ids.add(rid)
                    next_frontier.append(rid)

        current_frontier = next_frontier
        log.info(f"  Hop {depth + 1}: found {len(next_frontier)} new papers (total: {len(all_papers)})")

    return list(all_papers.values())


def deep_novelty_search(idea: dict, initial_results: dict) -> dict:
    """
    Enhanced novelty search:
    1. Start with initial keyword search results
    2. Take top-5 most relevant results
    3. Traverse their citation graph (1 hop)
    4. Return expanded result set

    This catches indirect prior work that standard keyword search misses.
    """
    # Get seed papers from initial search
    ss_results = initial_results.get("semantic_scholar_results", [])
    seed_papers = [p for p in ss_results if p.get("paperId")][:5]

    if not seed_papers:
        log.info("  No seed papers with IDs for citation expansion")
        return {
            "expanded_papers": [],
            "citation_hops": 0,
            "total_expanded": 0,
        }

    log.info(f"  Expanding search via citation graph ({len(seed_papers)} seeds)...")

    expanded = expand_search_via_citations(
        seed_papers,
        max_depth=1,
        max_papers_per_hop=8,
    )

    # Filter: only keep recent papers (last 3 years) and papers with abstracts
    import datetime
    current_year = datetime.datetime.now().year
    recent = [
        p for p in expanded
        if p.get("year") and p["year"] >= current_year - 3
        and p.get("abstract")
    ]

    # Sort by citation count (most cited first)
    recent.sort(key=lambda p: p.get("citationCount", 0), reverse=True)

    return {
        "expanded_papers": recent[:20],  # Top 20 most relevant
        "citation_hops": 1,
        "total_expanded": len(expanded),
        "total_recent_filtered": len(recent),
    }
