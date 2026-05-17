"""
step1_ingest.py — Paper Ingestion Pipeline
Reads PDFs/text from input_papers/, calls Claude to extract structured JSON records.
Outputs: output/paper_corpus.json
"""

import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    ClaudeClient, load_config, load_papers_from_dir,
    save_json, log, print_banner, print_step
)

SYSTEM_PROMPT = """You are a research paper extraction agent. You extract structured information from academic papers into a precise JSON format.

RESPOND WITH ONLY a valid JSON object — no explanation, no markdown fences.

Extract the following fields from the paper text:

{
  "paper_id": "slug: first-author-lastname-year (e.g., smith-2024)",
  "title": "full paper title",
  "authors": ["list of author names"],
  "year": 2024,
  "venue": "conference or journal name, or 'arXiv preprint' if unknown",
  "arxiv_id": "arxiv ID if available, else null",
  "doi": "DOI if available, else null",

  "problem": {
    "statement": "What specific problem does this paper address? 1-2 sentences.",
    "motivation": "Why does this problem matter? 1 sentence.",
    "scope": "What boundaries does the paper set? 1 sentence."
  },

  "method": {
    "name": "Named method or framework (e.g., 'TransformerXL')",
    "category": "One of: transformer, cnn, rnn, diffusion, rl, gnn, optimization, statistical, hybrid, benchmark, survey, other",
    "mechanism": "HOW the method works technically, 2-3 sentences. Not just what it does.",
    "components": ["key technical components"],
    "novelty_claim": "What the authors claim is new about their approach",
    "dependencies": ["required: specific data, compute, pretrained models, etc."]
  },

  "datasets": [
    {"name": "dataset name", "domain": "domain", "size": "size info", "public": true}
  ],

  "metrics": [
    {"name": "metric name", "value": "best reported value", "baseline_comparison": "vs X baseline, +/-Y%"}
  ],

  "claims": [
    {
      "claim": "Specific claim the paper makes",
      "evidence_type": "empirical | theoretical | ablation | case_study",
      "strength": "strong | moderate | weak",
      "conditions": "Under what conditions does this claim hold?"
    }
  ],

  "limitations": {
    "acknowledged": ["Limitations explicitly stated by authors"],
    "inferred": ["Limitations apparent from methodology/results but NOT stated. Always include at least 1."]
  },

  "failure_cases": {
    "reported": ["Cases where the method fails, if mentioned"],
    "conditions": ["Conditions where performance degrades"]
  },

  "related_work_positioning": {
    "builds_on": ["key prior works this extends"],
    "competes_with": ["methods compared against"],
    "orthogonal_to": ["related but different approaches mentioned"]
  },

  "future_work": ["Directions suggested by the authors for future research"],

  "reproducibility": {
    "code_available": true,
    "code_url": "URL or null",
    "data_available": true,
    "compute_requirements": "GPU/compute info if mentioned"
  },

  "extraction_confidence": "high if full text available, medium if abstract+intro only, low if abstract only"
}

Rules:
- Extract what the paper ACTUALLY says, not what you assume
- For 'limitations.inferred', always include at least 1 entry — no paper is perfect
- For 'claims', distinguish between what authors claim and what evidence supports
- Use consistent category labels across papers
- If a field is not present in the paper, use null (not empty string)
"""


def ingest_single_paper(client: ClaudeClient, paper: dict, idx: int, total: int) -> dict:
    """Extract structured record from a single paper."""
    filename = paper["filename"]
    text = paper["text"]

    log.info(f"[{idx}/{total}] Ingesting: {filename}")

    # Truncate text to fit context (leave room for system prompt)
    max_chars = 60000
    if len(text) > max_chars:
        # Keep beginning and end (intro + conclusion typically most informative)
        half = max_chars // 2
        text = text[:half] + "\n\n[... middle sections truncated ...]\n\n" + text[-half:]

    user_msg = f"""Extract structured information from this research paper.

FILENAME: {filename}

PAPER TEXT:
{text}

Respond with ONLY the JSON object, no other text."""

    try:
        record = client.ask_json(SYSTEM_PROMPT, user_msg)
        record["_source_file"] = filename
        log.info(f"  ✓ Extracted: {record.get('title', 'Unknown')}")
        return record
    except json.JSONDecodeError as e:
        log.error(f"  ✗ JSON parse error for {filename}: {e}")
        # Retry with stronger instruction
        try:
            retry_msg = user_msg + "\n\nCRITICAL: Output ONLY valid JSON. No markdown fences, no explanation."
            record = client.ask_json(SYSTEM_PROMPT, retry_msg)
            record["_source_file"] = filename
            return record
        except Exception:
            return {"paper_id": f"FAILED-{filename}", "_source_file": filename, "_error": str(e)}
    except Exception as e:
        log.error(f"  ✗ Error processing {filename}: {e}")
        return {"paper_id": f"FAILED-{filename}", "_source_file": filename, "_error": str(e)}


def run_ingestion(config: dict) -> dict:
    """Run the full ingestion pipeline."""
    print_banner("STEP 1: Paper Ingestion")

    cfg = config["pipeline"]
    input_dir = cfg["input_dir"]
    output_dir = cfg["output_dir"]

    # Load papers
    papers = load_papers_from_dir(input_dir)
    if not papers:
        log.error("No papers to process. Add PDF/TXT files to input_papers/")
        sys.exit(1)

    max_papers = cfg.get("max_papers", 200)
    if len(papers) > max_papers:
        log.warning(f"Limiting to {max_papers} papers (found {len(papers)})")
        papers = papers[:max_papers]

    # Initialize Claude client
    client = ClaudeClient(config=config)

    # Process papers
    records = []
    failed = 0
    for i, paper in enumerate(papers, 1):
        record = ingest_single_paper(client, paper, i, len(papers))
        if "_error" in record:
            failed += 1
        records.append(record)

    # Build corpus
    corpus = {
        "extraction_date": datetime.now().strftime("%Y-%m-%d"),
        "total_papers": len(records),
        "successful": len(records) - failed,
        "failed": failed,
        "extraction_method": cfg.get("extraction_depth", "full_text"),
        "papers": records,
    }

    # Save
    output_path = f"{output_dir}/paper_corpus.json"
    save_json(corpus, output_path)

    log.info(f"\nIngestion complete: {len(records) - failed}/{len(records)} papers processed")
    log.info(f"API stats: {client.stats()}")

    return corpus


if __name__ == "__main__":
    config = load_config()
    run_ingestion(config)
