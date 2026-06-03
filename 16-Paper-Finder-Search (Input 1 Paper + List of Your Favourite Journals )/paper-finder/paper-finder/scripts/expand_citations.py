#!/usr/bin/env python3
"""
Stage 4 (optional): Citation graph expansion.

Takes the top N papers from $out/ranked.jsonl, fetches their referenced works
and citers from OpenAlex, filters by the user's venue list and cutoff year,
and appends new candidates to $out/candidates.jsonl.

After this, re-run scripts/rerank.py to score the expanded pool.
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
CANDIDATES = ROOT / "$out" / "candidates.jsonl"
RANKED = ROOT / "$out" / "ranked.jsonl"

OPENALEX_BASE = "https://api.openalex.org"
MAILTO = os.environ.get("OPENALEX_MAILTO", "")
HEADERS = {
    "User-Agent": f"paper-finder/1.0 (mailto:{MAILTO})" if MAILTO
                  else "paper-finder/1.0"
}
RATE_DELAY = 0.12
MIN_YEAR = int(os.environ.get("MIN_YEAR", dt.date.today().year - 5))

TOP_SEEDS = 5
MAX_EXPANSION = 100  # hard cap on new candidates added


def reconstruct_abstract(inv_index):
    if not inv_index:
        return ""
    positions = [(i, w) for w, idxs in inv_index.items() for i in idxs]
    positions.sort()
    return " ".join(w for _, w in positions)


def normalize(w):
    loc = w.get("primary_location") or {}
    src = loc.get("source") or {}
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
        "authors": [a.get("author", {}).get("display_name", "")
                    for a in w.get("authorships", [])],
    }


SELECT = (
    "id,doi,title,abstract_inverted_index,publication_year,publication_date,"
    "cited_by_count,authorships,primary_location,referenced_works_count,type"
)


def fetch_referenced(refs: list[str], allowed_sources: set[str]):
    """Fetch reference works by ID, filtered by source. OpenAlex supports
    `filter=ids.openalex:W1|W2|...` with up to 100 per request."""
    for i in range(0, len(refs), 100):
        chunk = refs[i:i + 100]
        ids = "|".join(r.rsplit("/", 1)[-1] for r in chunk)
        source_filter = "|".join(allowed_sources)
        try:
            r = requests.get(
                f"{OPENALEX_BASE}/works",
                params={
                    "filter": (
                        f"ids.openalex:{ids},"
                        f"primary_location.source.id:{source_filter},"
                        f"publication_year:>{MIN_YEAR - 1},"
                        f"has_doi:true"
                    ),
                    "per-page": 100,
                    "select": SELECT,
                },
                headers=HEADERS, timeout=30,
            )
            r.raise_for_status()
        except requests.RequestException as e:
            print(f"    ⚠  fetch_referenced failed: {e}")
            continue
        for w in r.json().get("results", []):
            yield w
        time.sleep(RATE_DELAY)


def fetch_citers(seed_id: str, allowed_sources: set[str]):
    """Fetch papers that cite the seed, filtered by source."""
    source_filter = "|".join(allowed_sources)
    try:
        r = requests.get(
            f"{OPENALEX_BASE}/works",
            params={
                "filter": (
                    f"cites:{seed_id},"
                    f"primary_location.source.id:{source_filter},"
                    f"publication_year:>{MIN_YEAR - 1},"
                    f"has_doi:true"
                ),
                "per-page": 50,
                "select": SELECT,
            },
            headers=HEADERS, timeout=30,
        )
        r.raise_for_status()
    except requests.RequestException as e:
        print(f"    ⚠  fetch_citers failed: {e}")
        return
    for w in r.json().get("results", []):
        yield w
    time.sleep(RATE_DELAY)


def fetch_seed_refs(seed_id: str):
    """Get the referenced_works URL list for one seed."""
    try:
        r = requests.get(
            f"{OPENALEX_BASE}/works/{seed_id}",
            params={"select": "referenced_works"},
            headers=HEADERS, timeout=30,
        )
        r.raise_for_status()
    except requests.RequestException as e:
        print(f"    ⚠  fetch seed failed: {e}")
        return []
    return r.json().get("referenced_works", [])


def main():
    if not RANKED.exists():
        print(f"❌ {RANKED} not found. Run rerank.py first.")
        sys.exit(1)

    venue_map = json.loads(VENUE_MAP.read_text())
    allowed = {v["source_id"] for v in venue_map.values()}

    ranked = [json.loads(line) for line in RANKED.open()]
    seeds = ranked[:TOP_SEEDS]
    print(f"🌱 Expanding from top {len(seeds)} seeds (out of {len(ranked)} ranked).")

    existing_ids = {r["id"] for r in ranked}
    if CANDIDATES.exists():
        existing_ids |= {json.loads(l)["id"] for l in CANDIDATES.open()}

    new_records = {}
    for s in seeds:
        if len(new_records) >= MAX_EXPANSION:
            break
        print(f"\n  Seed: {s['title'][:80]}")

        # References this seed makes
        refs = fetch_seed_refs(s["id"])
        print(f"    refs: {len(refs)} cited works to scan")
        for w in fetch_referenced(refs, allowed):
            rec = normalize(w)
            if rec["id"] in existing_ids or rec["id"] in new_records:
                continue
            if not rec["title"] or not rec["abstract"]:
                continue
            new_records[rec["id"]] = rec
            if len(new_records) >= MAX_EXPANSION:
                break

        if len(new_records) >= MAX_EXPANSION:
            break

        # Papers that cite this seed
        print(f"    citers: scanning...")
        for w in fetch_citers(s["id"], allowed):
            rec = normalize(w)
            if rec["id"] in existing_ids or rec["id"] in new_records:
                continue
            if not rec["title"] or not rec["abstract"]:
                continue
            new_records[rec["id"]] = rec
            if len(new_records) >= MAX_EXPANSION:
                break

    if not new_records:
        print("\n   No new candidates found via citation expansion.")
        return

    # Append to candidates.jsonl
    with open(CANDIDATES, "a", encoding="utf-8") as f:
        for rec in new_records.values():
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"\n💾 Added {len(new_records)} new candidates to {CANDIDATES}")
    print(f"   Re-run rerank.py to score the expanded pool.")


if __name__ == "__main__":
    main()
