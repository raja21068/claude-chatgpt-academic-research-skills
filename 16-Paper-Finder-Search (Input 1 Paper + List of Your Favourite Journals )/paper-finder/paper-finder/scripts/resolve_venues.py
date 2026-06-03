#!/usr/bin/env python3
"""
Stage 0: Resolve a CSV of venue names to OpenAlex source IDs.

Reads `inputs/venues.csv` (must have a `Name` column), queries OpenAlex's
/sources endpoint for each, and writes `inputs/venue_map.json` with the
top match and alternates per venue.

Run once. Re-run when you add or change venues.
"""
import csv
import json
import os
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
VENUES_CSV = ROOT / "inputs" / "venues.csv"
VENUE_MAP = ROOT / "inputs" / "venue_map.json"

OPENALEX_BASE = "https://api.openalex.org"
MAILTO = os.environ.get("OPENALEX_MAILTO", "")
HEADERS = {
    "User-Agent": f"paper-finder/1.0 (mailto:{MAILTO})" if MAILTO
                  else "paper-finder/1.0"
}
RATE_DELAY = 0.12  # seconds between requests (polite pool: 10 req/s)


def find_name_column(fieldnames):
    """Accept several common header names for the venue column."""
    for candidate in ["Name", "Venue", "Journal", "Conference", "Title"]:
        if candidate in fieldnames:
            return candidate
    raise ValueError(
        f"venues.csv must have one of: Name, Venue, Journal, Conference, Title. "
        f"Found: {fieldnames}"
    )


def resolve_one(name: str):
    """Query OpenAlex /sources for a venue name; return top 5 hits."""
    r = requests.get(
        f"{OPENALEX_BASE}/sources",
        params={"search": name, "per-page": 5},
        headers=HEADERS,
        timeout=30,
    )
    r.raise_for_status()
    return r.json().get("results", [])


def short_id(openalex_url: str) -> str:
    """Strip the URL prefix: https://openalex.org/S4306419644 -> S4306419644"""
    return openalex_url.rsplit("/", 1)[-1]


def main():
    if not VENUES_CSV.exists():
        print(f"❌ {VENUES_CSV} not found. Create it with a `Name` column.")
        sys.exit(1)

    # Load existing mapping if present — we only resolve new venues
    existing = {}
    if VENUE_MAP.exists():
        existing = json.loads(VENUE_MAP.read_text())
        print(f"📂 Loaded {len(existing)} cached venues from {VENUE_MAP.name}")

    with open(VENUES_CSV, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        col = find_name_column(reader.fieldnames or [])
        names = [row[col].strip() for row in reader if row.get(col, "").strip()]

    print(f"🔍 Resolving {len(names)} venues against OpenAlex...")

    mapping = dict(existing)  # start from cache
    ambiguous = []
    failed = []

    for name in names:
        if name in mapping:
            continue
        try:
            hits = resolve_one(name)
        except requests.RequestException as e:
            print(f"  ⚠  {name}: request failed ({e})")
            failed.append(name)
            time.sleep(RATE_DELAY)
            continue

        if not hits:
            print(f"  ❌ {name}: no match in OpenAlex")
            failed.append(name)
            time.sleep(RATE_DELAY)
            continue

        top = hits[0]
        entry = {
            "source_id": short_id(top["id"]),
            "display_name": top["display_name"],
            "type": top.get("type"),
            "publisher": top.get("host_organization_name"),
            "works_count": top.get("works_count"),
            "alternates": [
                {
                    "source_id": short_id(h["id"]),
                    "display_name": h["display_name"],
                    "type": h.get("type"),
                    "works_count": h.get("works_count"),
                }
                for h in hits[1:3]
            ],
        }
        mapping[name] = entry
        print(f"  ✅ {name:35s} → {entry['source_id']}  ({entry['display_name']})")

        # Flag ambiguity: top two hits within 30% of each other in works_count
        if len(hits) > 1:
            top_n = top.get("works_count") or 0
            alt_n = hits[1].get("works_count") or 0
            if top_n and alt_n and alt_n / top_n > 0.7:
                ambiguous.append((name, top["display_name"], hits[1]["display_name"]))

        time.sleep(RATE_DELAY)

    VENUE_MAP.write_text(json.dumps(mapping, indent=2, ensure_ascii=False))
    print(f"\n💾 Saved {len(mapping)} venues to {VENUE_MAP}")

    if ambiguous:
        print("\n⚠  Ambiguous matches (review these in venue_map.json):")
        for name, top, alt in ambiguous:
            print(f"     {name}: chose '{top}' over '{alt}'")

    if failed:
        print("\n❌ Failed to resolve (omit from venues.csv or try alternate naming):")
        for name in failed:
            print(f"     {name}")


if __name__ == "__main__":
    main()
