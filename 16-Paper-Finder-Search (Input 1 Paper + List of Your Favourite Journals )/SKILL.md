---
name: paper-finder
description: >
  High-quality literature discovery assistant. Finds peer-reviewed papers from a user-curated list of journals and conferences for a given research topic, using OpenAlex source IDs (not fuzzy venue strings) plus LLM-driven query expansion and relevance re-ranking. Use this skill whenever the user wants to: search for related work, build a literature review pool, find citations on a topic, discover recent papers in specific venues, expand a seed set of papers via citations, or assemble a BibTeX file for a paper draft. Trigger even when the user says vague things like "find me good papers on X", "I need related work for my draft", or "search NeurIPS/CVPR/Nature for Y". Excludes arXiv-only preprints by default. Pairs naturally with the paper-writing-agent skill — outputs feed directly into its LITREVIEW_VERIFY phase.
---

# Paper Finder

You help the user discover **high-quality, peer-reviewed** research papers from a curated venue list. The pipeline is deterministic where it can be (OpenAlex API queries, venue resolution, deduplication) and uses Claude where judgment is required (query expansion, relevance scoring, thematic clustering).

The core design choice: **filter by OpenAlex `source_id`, not venue strings**. OpenAlex maintains a controlled vocabulary of venues; once you resolve "NeurIPS" → `S4306419644` you never have to fuzzy-match again.

## Skill folder structure

```
paper-finder/
├── SKILL.md                       ← you are here
├── $out/                          ← all generated outputs go here
│   ├── queries.json               ← LLM-expanded query set
│   ├── candidates.jsonl           ← raw OpenAlex hits (one paper per line)
│   ├── ranked.jsonl               ← after LLM re-ranking
│   ├── final.bib                  ← BibTeX export for the paper draft
│   ├── final.csv                  ← human-readable table
│   └── summary.md                 ← thematic clustering + coverage notes
├── inputs/
│   ├── venues.csv                 ← user's curated venue list (Name column)
│   └── venue_map.json             ← cached venue → OpenAlex source_id mapping
└── scripts/
    ├── resolve_venues.py          ← one-time: CSV venues → source IDs
    ├── search_openalex.py         ← runs the expanded queries, dumps candidates
    ├── rerank.py                  ← shells LLM scoring over candidates
    ├── expand_citations.py        ← optional: walks citation graph from top hits
    └── export_bibtex.py           ← candidates.jsonl → final.bib
```

## Required inputs

Before running the pipeline, you need:

1. **`venues.csv`** — at minimum a `Name` column listing journals/conferences the user trusts (e.g. "NeurIPS", "Nature Machine Intelligence", "TPAMI")
2. **Research topic** — one sentence describing what the user is looking for. Push for specificity: "graph neural networks" is too vague; "node classification on heterophilic graphs" is workable
3. **(Optional) Cutoff year** — default: 5 years back from today
4. **(Optional) Target count** — default: 30 papers in final pool

If any are missing, ask before proceeding. Do not invent venues or topics.

## Pipeline

### Stage 0 — Resolve venues to OpenAlex source IDs (one-time)

Skip if `inputs/venue_map.json` already exists and covers all rows in `venues.csv`.

For each venue name, query `https://api.openalex.org/sources?search={name}`. OpenAlex returns ranked matches with metadata (publisher, ISSN, type). Show the top 3 hits per venue and confirm ambiguous ones with the user before caching.

```python
# scripts/resolve_venues.py — sketch
import requests, csv, json, time

def resolve(name):
    r = requests.get(
        "https://api.openalex.org/sources",
        params={"search": name, "per-page": 5},
        headers={"User-Agent": "paper-finder/1.0 (mailto:user@example.com)"},
        timeout=30,
    )
    return r.json().get("results", [])

mapping = {}
for row in csv.DictReader(open("inputs/venues.csv", encoding="utf-8-sig")):
    name = row["Name"].strip()
    hits = resolve(name)
    if not hits:
        print(f"⚠ no match: {name}")
        continue
    # Take top hit; flag the rest for user review if scores are close
    mapping[name] = {
        "source_id": hits[0]["id"].rsplit("/", 1)[-1],  # e.g. "S4306419644"
        "display_name": hits[0]["display_name"],
        "type": hits[0].get("type"),
        "alternates": [(h["id"].rsplit("/",1)[-1], h["display_name"]) for h in hits[1:3]],
    }
    time.sleep(0.1)

json.dump(mapping, open("inputs/venue_map.json", "w"), indent=2)
```

**Always include a `mailto:` in the User-Agent** — it puts you in OpenAlex's polite pool with higher rate limits and zero cost.

### Stage 1 — Expand the research topic into a diverse query set (LLM)

Claude reads the user's topic and writes 6–10 queries that together cover the concept space. Aim for:
- 1–2 literal queries (exact phrasing the user used)
- 2–3 synonym variants ("heterophilic graphs" → "non-homophilous graphs", "label heterophily")
- 2–3 methodological adjacents ("GNN" → "message passing", "graph attention")
- 1–2 application-side or motivation-side queries

Save to `$out/queries.json`:

```json
{
  "topic": "node classification on heterophilic graphs",
  "queries": [
    "node classification heterophilic graphs",
    "graph neural network heterophily",
    "non-homophilous graph learning",
    "message passing heterophilic",
    "...etc"
  ]
}
```

Do not invent queries that drift from the user's topic. If you are uncertain whether a variant belongs, ask.

### Stage 2 — Search OpenAlex, filtered by source ID

For each query × all venues, hit:

```
GET https://api.openalex.org/works
    ?search={query}
    &filter=primary_location.source.id:S123|S456|S789,
            publication_year:>{cutoff-1},
            has_doi:true
    &per-page=50
    &cursor=*
```

Notes:
- `|` between source IDs is OR within the filter — one request covers all venues
- `has_doi:true` is a cheap proxy for "actually published" (arXiv-only preprints lack DOIs)
- Use `cursor=*` then walk `meta.next_cursor` for full pagination
- Reconstruct abstracts from `abstract_inverted_index` (OpenAlex stores them inverted; helper below)

```python
# scripts/search_openalex.py — key helper
def reconstruct_abstract(inv_index):
    if not inv_index:
        return ""
    positions = []
    for word, idxs in inv_index.items():
        for i in idxs:
            positions.append((i, word))
    positions.sort()
    return " ".join(w for _, w in positions)
```

Deduplicate by OpenAlex `id`. Write each candidate as one JSON line to `$out/candidates.jsonl` with fields: `id`, `doi`, `title`, `abstract`, `year`, `venue`, `cited_by_count`, `authors`, `referenced_works_count`.

### Stage 3 — LLM re-rank for relevance (the quality lever)

Citation count rewards age; venue filter rewards prestige. Neither rewards *actual relevance to the user's question*. This stage fixes that.

For each candidate (in batches of ~20 to keep the prompt small), present title + abstract + venue + year and ask Claude to return a JSON array of:

```json
[
  {
    "id": "W2964313798",
    "relevance": 9,
    "reason": "Directly proposes a heterophily-aware GNN; introduces the H2GCN architecture central to this line of work."
  },
  { "id": "...", "relevance": 3, "reason": "Tangential — heterophily mentioned only in future work." }
]
```

Scoring guidance to give Claude:
- **9–10**: core paper, would appear in any literature review on this topic
- **6–8**: substantive contribution to the topic; worth citing
- **3–5**: adjacent but not central; cite only if filling a specific gap
- **0–2**: off-topic, discard

Keep relevance ≥ 6 by default. Write the kept set to `$out/ranked.jsonl` sorted by `relevance` desc, then `cited_by_count` desc as tiebreak.

### Stage 4 — Citation graph expansion (optional but high-value)

For the top 5 papers in `ranked.jsonl`, fetch their `referenced_works` (what they cite) and their citers (`cited_by_api_url`). Filter the harvested IDs through the same venue list (Stage 2's `source.id` filter) and re-rank (Stage 3). Add anything scoring ≥ 7 to the final pool.

This catches the seminal paper everyone cites but whose title didn't keyword-match.

Cap total expansion at ~100 additional candidates to keep latency reasonable.

### Stage 5 — Export

`scripts/export_bibtex.py` reads `ranked.jsonl` and writes `$out/final.bib`. For BibTeX keys, use `firstauthor_year_firstword` (e.g. `zhu_2020_heterophily`) — short, stable, paper-writing-agent-compatible.

Also emit:
- `$out/final.csv` — rank, title, year, venue, citations, relevance, doi, url
- `$out/summary.md` — thematic clusters (Claude groups the final pool by approach/theme) + a "coverage gaps" section flagging concepts in the queries that returned few results

## Universal rules

1. **No invented papers.** Every entry in any output file must come from a real OpenAlex response. If a search returns nothing, say so; do not pad the pool.
2. **No author opinions.** Claude's `reason` field in the re-rank stage describes *what the abstract says about the topic*, not editorial commentary on the authors or work quality.
3. **No arXiv-only preprints** in the final pool by default. They lack peer review, which is the whole point of the venue filter. If the user explicitly wants preprints, relax the `has_doi:true` filter and tell them you did.
4. **Cite OpenAlex's freshness.** OpenAlex updates weekly but isn't real-time. For papers from the last 2 months, mention that coverage may be incomplete.
5. **Don't merge sources silently.** If you fall back to Semantic Scholar or Crossref for a specific gap (e.g. missing abstract), label the source per record in the output.

## Common pitfalls

- **Venue name collisions**: "ICML" can resolve to International Conference on Machine Learning *or* International Conference on Multimedia. Always show the user the top 3 hits in Stage 0 and confirm.
- **Workshop vs main conference**: OpenAlex sometimes treats workshop proceedings as separate sources. If the user wants only the main track, filter on `type=conference` and review.
- **Abstract reconstruction edge cases**: `abstract_inverted_index` can have gaps; if reconstructed abstract is < 50 chars, fall back to fetching the work record directly or skip.
- **Rate limits**: OpenAlex polite pool allows 10 req/s. Stage 2 with many queries × venues can hit this — add `time.sleep(0.1)` between requests.

## Composition with paper-writing-agent

The output `final.bib` plugs directly into paper-writing-agent's `[CITATION_POOL]` (LITREVIEW_WRITE phase). Each entry in `ranked.jsonl` also has the OpenAlex `id`, abstract, and year — exactly the fields paper-writing-agent's LITREVIEW_VERIFY phase consumes (`candidate_title`, `s2_top_hit:{title, abstract, year, paperId}`).

When the user is on a paper draft and asks "find more citations for the GNN section", run this skill scoped to that section's terminology, then hand off `ranked.jsonl` to paper-writing-agent.

## Quick-start checklist

When triggered:

1. Confirm you have `venues.csv` and a specific research topic
2. Run `resolve_venues.py` if `venue_map.json` is stale or missing
3. Expand the topic into queries (Stage 1) — show the user before running
4. Search + dedupe (Stage 2)
5. Re-rank (Stage 3) — show the user the top 10 and confirm before expanding
6. Citation expansion if the user wants depth (Stage 4)
7. Export and summarize (Stage 5)
8. Hand off to paper-writing-agent if appropriate
