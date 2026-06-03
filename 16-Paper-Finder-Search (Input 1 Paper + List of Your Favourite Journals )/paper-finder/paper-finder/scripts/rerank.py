#!/usr/bin/env python3
"""
Stage 3: LLM relevance re-ranking.

Three modes:
  --api      Use the Anthropic API directly (needs ANTHROPIC_API_KEY).
  --batches  Write prompt files to $out/rerank_batches/ for Claude to score
             inside a chat session. (Use this when running the skill inside
             Claude.ai — Claude reads each batch and writes its scores back.)
  --merge    After Claude saves responses to $out/rerank_responses/, merge
             them into $out/ranked.jsonl.

Reads: $out/candidates.jsonl, $out/queries.json
Writes: $out/ranked.jsonl  (filtered to relevance >= MIN_RELEVANCE)
"""
import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUERIES = ROOT / "$out" / "queries.json"
CANDIDATES = ROOT / "$out" / "candidates.jsonl"
RANKED = ROOT / "$out" / "ranked.jsonl"
BATCH_DIR = ROOT / "$out" / "rerank_batches"
RESP_DIR = ROOT / "$out" / "rerank_responses"

BATCH_SIZE = 20
MIN_RELEVANCE = int(os.environ.get("MIN_RELEVANCE", "6"))

RUBRIC = """\
You are scoring research papers for relevance to a specific research topic.

TOPIC: {topic}

Score each paper on a 0-10 scale:
  9-10: Core paper — would appear in any literature review on this topic.
  6-8:  Substantive contribution to the topic; worth citing.
  3-5:  Adjacent but not central; cite only if filling a specific gap.
  0-2:  Off-topic — discard.

Return ONLY a JSON array, one object per paper:
[
  {{"id": "W123...", "relevance": 9, "reason": "1-2 sentences grounded in what the abstract says, not editorial opinion."}},
  ...
]

Do not include any preamble, explanation, or markdown fences.
"""


def load_inputs():
    if not QUERIES.exists() or not CANDIDATES.exists():
        print(f"❌ Need both {QUERIES.name} and {CANDIDATES.name}. Run earlier stages first.")
        sys.exit(1)
    topic = json.loads(QUERIES.read_text()).get("topic", "")
    if not topic:
        print(f"❌ {QUERIES} must have a `topic` field.")
        sys.exit(1)
    candidates = [json.loads(line) for line in CANDIDATES.open()]
    return topic, candidates


def format_batch(topic: str, batch: list[dict]) -> str:
    rubric = RUBRIC.format(topic=topic)
    items = []
    for c in batch:
        items.append(
            f"ID: {c['id']}\n"
            f"Title: {c['title']}\n"
            f"Venue: {c.get('venue', 'n/a')}  Year: {c.get('year', 'n/a')}\n"
            f"Abstract: {c['abstract'][:1200]}"
        )
    return rubric + "\n\nPAPERS:\n\n" + "\n\n---\n\n".join(items)


def parse_response(text: str) -> list[dict]:
    """Strip code fences if present, parse as JSON array."""
    t = text.strip()
    if t.startswith("```"):
        t = t.split("```", 2)[1]
        if t.startswith("json"):
            t = t[4:]
        t = t.rsplit("```", 1)[0] if "```" in t else t
        t = t.strip()
    try:
        return json.loads(t)
    except json.JSONDecodeError as e:
        print(f"   ⚠  failed to parse response: {e}")
        return []


# ---------- mode: --api ----------

def run_api(topic: str, candidates: list[dict]):
    try:
        import anthropic
    except ImportError:
        print("❌ `anthropic` package not installed. Run: pip install anthropic")
        sys.exit(1)
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY not set in environment.")
        sys.exit(1)

    client = anthropic.Anthropic()
    model = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-7")

    scores = {}
    for i in range(0, len(candidates), BATCH_SIZE):
        batch = candidates[i:i + BATCH_SIZE]
        print(f"  Batch {i // BATCH_SIZE + 1}: scoring {len(batch)} papers...")
        prompt = format_batch(topic, batch)
        resp = client.messages.create(
            model=model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(b.text for b in resp.content if hasattr(b, "text"))
        for item in parse_response(text):
            if "id" in item and "relevance" in item:
                scores[item["id"]] = item
    return scores


# ---------- mode: --batches ----------

def run_batches(topic: str, candidates: list[dict]):
    BATCH_DIR.mkdir(parents=True, exist_ok=True)
    RESP_DIR.mkdir(parents=True, exist_ok=True)
    n_batches = 0
    for i in range(0, len(candidates), BATCH_SIZE):
        batch = candidates[i:i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        prompt = format_batch(topic, batch)
        out = BATCH_DIR / f"batch_{batch_num:03d}.txt"
        out.write_text(prompt)
        n_batches += 1
    print(f"📝 Wrote {n_batches} batch prompts to {BATCH_DIR}")
    print(f"   Next: have Claude score each batch and save responses as:")
    print(f"         {RESP_DIR}/batch_001.json, batch_002.json, ...")
    print(f"   Then run:  python scripts/rerank.py --merge")


# ---------- mode: --merge ----------

def run_merge():
    if not RESP_DIR.exists():
        print(f"❌ {RESP_DIR} not found. Did you run --batches first?")
        sys.exit(1)
    scores = {}
    for f in sorted(RESP_DIR.glob("batch_*.json")):
        try:
            items = json.loads(f.read_text())
        except json.JSONDecodeError:
            # Allow the user to paste raw Claude responses with fences
            items = parse_response(f.read_text())
        for item in items:
            if "id" in item and "relevance" in item:
                scores[item["id"]] = item
        print(f"  ✅ {f.name}: {len(items)} scores")
    return scores


# ---------- writer ----------

def write_ranked(candidates: list[dict], scores: dict):
    enriched = []
    for c in candidates:
        s = scores.get(c["id"])
        if not s:
            continue
        rel = int(s.get("relevance", 0))
        if rel < MIN_RELEVANCE:
            continue
        c["relevance"] = rel
        c["relevance_reason"] = s.get("reason", "")
        enriched.append(c)

    # Sort: relevance desc, then citations desc as tiebreak
    enriched.sort(key=lambda x: (x["relevance"], x.get("cited_by_count", 0)), reverse=True)

    with open(RANKED, "w", encoding="utf-8") as f:
        for r in enriched:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"\n💾 Saved {len(enriched)} ranked papers to {RANKED}")
    print(f"   (filtered to relevance >= {MIN_RELEVANCE})")


def main():
    ap = argparse.ArgumentParser()
    grp = ap.add_mutually_exclusive_group(required=True)
    grp.add_argument("--api", action="store_true", help="Use Anthropic API")
    grp.add_argument("--batches", action="store_true", help="Write prompts for Claude in-chat")
    grp.add_argument("--merge", action="store_true", help="Merge Claude responses to ranked.jsonl")
    args = ap.parse_args()

    if args.batches:
        topic, candidates = load_inputs()
        run_batches(topic, candidates)
        return

    if args.merge:
        _, candidates = load_inputs()
        scores = run_merge()
        write_ranked(candidates, scores)
        return

    if args.api:
        topic, candidates = load_inputs()
        print(f"🤖 Scoring {len(candidates)} candidates via API...")
        scores = run_api(topic, candidates)
        write_ranked(candidates, scores)


if __name__ == "__main__":
    main()
