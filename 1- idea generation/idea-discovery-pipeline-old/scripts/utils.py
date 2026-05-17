"""
utils.py — Shared utilities for the Idea Discovery Pipeline
API client, file I/O, logging, retry logic
"""

import json
import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

# ── Logging ──────────────────────────────────────────────────────────────────

def setup_logging(log_dir: str = "logs") -> logging.Logger:
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = Path(log_dir) / f"pipeline_{ts}.log"

    logger = logging.getLogger("idea_pipeline")
    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)

    fmt = logging.Formatter("[%(asctime)s] %(levelname)-8s %(message)s", datefmt="%H:%M:%S")
    fh.setFormatter(fmt)
    ch.setFormatter(fmt)

    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger

log = setup_logging()

# ── Config ───────────────────────────────────────────────────────────────────

def load_config(path: str = "config/settings.json") -> dict:
    with open(path, "r") as f:
        return json.load(f)

# ── File I/O ─────────────────────────────────────────────────────────────────

def save_json(data: dict | list, path: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    log.info(f"Saved: {path}")

def load_json(path: str) -> dict | list:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_markdown(text: str, path: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    log.info(f"Saved: {path}")

# ── Claude API Client ────────────────────────────────────────────────────────

class ClaudeClient:
    """Wrapper around the Anthropic Messages API with retry logic."""

    def __init__(self, api_key: Optional[str] = None, config: Optional[dict] = None):
        try:
            import anthropic
            self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
            if not self.api_key:
                raise ValueError(
                    "ANTHROPIC_API_KEY not set. Export it:\n"
                    "  export ANTHROPIC_API_KEY=sk-ant-..."
                )
            self.client = anthropic.Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError("Run: pip install anthropic")

        cfg = config or {}
        api_cfg = cfg.get("api", {})
        self.model = api_cfg.get("model", "claude-sonnet-4-20250514")
        self.max_tokens = api_cfg.get("max_tokens", 8096)
        self.retries = api_cfg.get("retry_attempts", 3)
        self.retry_delay = api_cfg.get("retry_delay_seconds", 5)
        self.call_count = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0

    def ask(self, system: str, user: str, temperature: float = 0.3) -> str:
        """Send a message to Claude and return the text response."""
        for attempt in range(1, self.retries + 1):
            try:
                resp = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=temperature,
                    system=system,
                    messages=[{"role": "user", "content": user}],
                )
                self.call_count += 1
                self.total_input_tokens += resp.usage.input_tokens
                self.total_output_tokens += resp.usage.output_tokens

                text = ""
                for block in resp.content:
                    if hasattr(block, "text"):
                        text += block.text
                return text.strip()

            except Exception as e:
                log.warning(f"API call attempt {attempt}/{self.retries} failed: {e}")
                if attempt < self.retries:
                    time.sleep(self.retry_delay * attempt)
                else:
                    raise

    def ask_json(self, system: str, user: str, temperature: float = 0.1) -> dict | list:
        """Send a message expecting JSON back. Auto-strips markdown fences."""
        raw = self.ask(system, user, temperature=temperature)
        # Strip ```json ... ``` fences if present
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            # Remove first line (```json) and last line (```)
            lines = [l for l in lines if not l.strip().startswith("```")]
            cleaned = "\n".join(lines)
        return json.loads(cleaned)

    def stats(self) -> dict:
        return {
            "api_calls": self.call_count,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
        }

# ── PDF Text Extraction ─────────────────────────────────────────────────────

def extract_pdf_text(pdf_path: str) -> str:
    """Extract text from a PDF file. Tries PyMuPDF first, falls back to pdfplumber."""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text() + "\n"
        doc.close()
        return text.strip()
    except Exception:
        pass

    try:
        import pdfplumber
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text += t + "\n"
        return text.strip()
    except Exception as e:
        log.error(f"Failed to extract text from {pdf_path}: {e}")
        return ""

def load_papers_from_dir(input_dir: str) -> list[dict]:
    """Load all papers from input directory. Supports .pdf and .txt files."""
    papers = []
    input_path = Path(input_dir)

    if not input_path.exists():
        log.error(f"Input directory not found: {input_dir}")
        return papers

    files = sorted(input_path.glob("*"))
    supported = [f for f in files if f.suffix.lower() in (".pdf", ".txt", ".md")]

    if not supported:
        log.error(f"No PDF/TXT/MD files found in {input_dir}")
        return papers

    log.info(f"Found {len(supported)} papers in {input_dir}")

    for f in supported:
        if f.suffix.lower() == ".pdf":
            text = extract_pdf_text(str(f))
        else:
            text = f.read_text(encoding="utf-8", errors="replace")

        if text:
            papers.append({
                "filename": f.name,
                "text": text[:80000],  # Truncate very long papers to ~80k chars
            })
            log.info(f"  Loaded: {f.name} ({len(text)} chars)")
        else:
            log.warning(f"  Skipped (empty): {f.name}")

    return papers

# ── Progress Display ─────────────────────────────────────────────────────────

def print_banner(title: str):
    width = 60
    print("\n" + "=" * width)
    print(f"  {title}")
    print("=" * width)

def print_step(step: int, total: int, description: str):
    print(f"\n── Step {step}/{total}: {description} ──")
