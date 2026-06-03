#!/usr/bin/env python3
"""
Stage 2: Search OpenAlex for papers matching the expanded queries, filtered to
the user's curated venues. Reads `inputs/venue_map.json` and `$out/queries.json`;
writes deduplicated candidates to `$out/candidates.jsonl`.

Filters applied:
  - primary_location.source.id IN (user's venue source IDs)
  - publication_year >= cutoff (default: 5 years ago)
  - has_doi:true  (proxy for "actually published", excludes arXiv-only preprints)
"""
import datetime as dt
import json
import os
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
VENUE_MAP = ROOT / "inputs" / "venue_map.json"
QUERIES = ROOT / "$out" / "queries.json"
CANDIDATES = ROOT / "$out" / "candidates.jsonl"

OPENALEX_BASE = "https://api.openalex.org"
MAILTO = os.environ.get("OPENALEX_MAILTO", "")
HEADERS = {
    "User-Agent": f"paper-finder/1.0 (mailto:{MAILTO})" if MAILTO
                  else "paper-finder/1.0"
}
RATE_DELAY = 0.12

MIN_YEAR = int(os.environ.get("MIN_YEAR", dt.date.today().year - 5))
PER_PAGE = 50
MAX_PAGES_PER_QUERY = 4  # cap per query × venue-set to keep latency reasonable


def reconstruct_abstract(inv_index: dict) -> str:
    """OpenAlex stores abstracts as inverted indices. Rebuild as a string."""
    if not inv_index:
        return ""
    positions = []
    for word, idxs in inv_index.items():
        for i in idxs:
            positions.append((i, word))
    positions.sort()
    return " ".join(w for _, w in positions)


def load_venue_ids() -> list[str]:
    if not VENUE_MAP.exists():
        print(f"❌ {VENUE_MAP} not found. Run resolve_venues.py first.")
        sys.exit(1)
    mapping = json.loads(VENUE_MAP.read_text())
    ids = sorted({v["source_id"] for v in mapping.values()})
    print(f"📂 {len(ids)} unique source IDs from {len(mapping)} venues")
    return ids


def load_queries() -> list[str]:
    if not QUERIES.exists():
        print(f"❌ {QUERIES} not found. Create it with a `queries` list.")
        print("   Example:")
        print('   {"topic": "...", "queries": ["query 1", "query 2", ...]}')
        sys.exit(1)
    data = json.loads(QUERIES.read_text())
    qs = data.get("queries", [])
    if not qs:
        print(f"❌ {QUERIES} has no `queries` field or it is empty.")
        sys.exit(1)
    print(f"📂 {len(qs)} queries from {QUERIES.name}")
    return qs


def search(query: str, source_ids: list[str]):
    """Yield work records for one query, paginated, source-filtered."""
    source_filter = "|".join(source_ids)
    filter_str = (
        f"primary_location.source.id:{source_filter},"
        f"publication_year:>{MIN_YEAR - 1},"
        f"has_doi:true"
    )
    cursor = "*"
    pages = 0
    while cursor and pages < MAX_PAGES_PER_QUERY:
        try:
            r = requests.get(
                f"{OPENALEX_BASE}/works",
                params={
                    "search": query,
                    "filter": filter_str,
                    "per-page": PER_PAGE,
                    "cursor": cursor,
                    "select": (
                        "id,doi,title,abstract_inverted_index,publication_year,"
                        "publication_date,cited_by_count,authorships,"
                        "primary_location,referenced_works_count,type"
                    ),
                },
                headers=HEADERS,
                timeout=30,
            )
            r.raise_for_status()
        except requests.RequestException as e:
            print(f"    ⚠  request failed: {e}")
            return
        data = r.json()
        for w in data.get("results", []):
            yield w
        cursor = data.get("meta", {}).get("next_cursor")
        pages += 1
        time.sleep(RATE_DELAY)


def normalize(w: dict) -> dict:
    """Trim OpenAlex record to the fields downstream stages need."""
    loc = w.get("primary_location") or {}
    src = loc.get("source") or {}
    authors = [
        a.get("author", {}).get("display_name", "")
        for a in w.get("authorships", [])
    ]
    return {
        "id": w["id"].rsplit("/", 1)[-1],
        "openalex_url": w["id"],
        "doi": (w.get("doi") or "").replace("https://doi.org/", ""),
        "title": w.get("title") or "",
        "abstract": reconstruct_abstract(w.get("abstract_inverted_index")),
        "year": w.get("publication_year"),
        "date": w.get("publication_date"),
        "venue": src.get("display_name"),
        "source_id": (src.get("id") or "").rsplit("/", 1)[-1] or None,
        "type": w.get("type"),
        "cited_by_count": w.get("cited_by_count", 0),
        "referenced_works_count": w.get("referenced_works_count", 0),
        "authors": authors,
    }


def main():
    source_ids = load_venue_ids()
    queries = load_queries()

    seen = {}  # id -> normalized record
    per_query_counts = []

    for i, q in enumerate(queries, 1):
        before = len(seen)
        print(f"\n[{i}/{len(queries)}] Searching: {q!r}")
        for w in search(q, source_ids):
            rec = normalize(w)
            if not rec["title"] or not rec["abstract"]:
                continue  # need both to re-rank
            if rec["id"] not in seen:
                seen[rec["id"]] = rec
        added = len(seen) - before
        per_query_counts.append(added)
        print(f"    +{added} new candidates  (total: {len(seen)})")

    # Write JSONL
    CANDIDATES.parent.mkdir(parents=True, exist_ok=True)
    with open(CANDIDATES, "w", encoding="utf-8") as f:
        for rec in seen.values():
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"\n💾 Saved {len(seen)} unique candidates to {CANDIDATES}")
    print(f"📊 Per-query yields: {per_query_counts}")
    if min(per_query_counts, default=0) == 0:
        print("⚠  Some queries returned zero new results — check phrasing or venue coverage.")


if __name__ == "__main__":
    main()
