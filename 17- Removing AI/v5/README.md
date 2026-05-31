# Paper Writing Agent v6

Anti-slop checker and rewriter for academic papers. Detects and auto-fixes AI writing patterns before submission.

## What's new in v6

- **Humanizer skill integrated** — 30+ new detection patterns from Wikipedia's "Signs of AI writing" guide, including AI vocabulary density, formulaic phrases, em dash overuse, filler openers, and chatbot artifacts
- **Sentence-cutting bug fixed** — v5's `rewrite_zombie_noun()` and `rewrite_passive()` rewrites were cutting content by dropping regex capture groups; both removed; rewriter now applies phrase-level substitutions only
- **`[BASELINE]` placeholder bug fixed** — `rewrite_context_free()` was injecting literal placeholder text into sentences; removed
- **Smarter scoring** — humanizer penalty normalized by word count (per-1000-word density) so long papers aren't over-penalised for a few expected uses of words like "robust"
- **Cleaner output** — rewriter now reports `score before → score after`, no stale placeholder notes

## Quick start

```bash
# First time
python run.py setup

# Check a paper
python run.py check input/my_paper.txt

# Check with full detail
python run.py check input/my_paper.txt --report

# Auto-rewrite (double-click on Windows/Mac)
run.bat   # Windows
./run.sh  # Mac / Linux
```

## Commands

| Command | What it does |
|---|---|
| `python run.py setup` | Install dependencies |
| `python run.py check <file>` | Score report with all checks |
| `python run.py check <file> --report` | Full report with rewrite hints |
| `python run.py diff v1.txt v2.txt` | Compare two drafts |
| `python run.py rhythm <file>` | Sentence rhythm only |
| `python run.py latex <file.tex>` | LaTeX-aware check |
| `python run.py abstract <file>` | Abstract structure check |

## Score interpretation

| Score | Meaning |
|---|---|
| 75–100 | Clean — low AI signal |
| 50–74 | Borderline — some patterns to fix |
| 0–49 | AI-like — significant patterns detected |

Threshold for pass is 70 (configurable in `slop_config.yaml`).

## What the checker detects

### Humanizer patterns (new in v6)
- **AI vocabulary density** — `robust`, `comprehensive`, `furthermore`, `leveraging`, `paradigm`, `pivotal`, `showcase`, `tapestry`, `vibrant`, and 20+ more; penalises when density exceeds 5/1000 words
- **Formulaic AI phrases** — `plays a crucial role`, `it is worth noting`, `serves as a testament`, `evolving landscape`, `setting the stage for`, `experts argue`, and 40+ more
- **Safe auto-fixes** — removes filler openers (`It is important to note that`, `To the best of our knowledge`), compresses filler phrases (`in order to` → `to`, `due to the fact that` → `because`), fixes copula avoidance (`serves as a` → `is a`), replaces spaced em dashes with commas

### Existing checks (v5)
- Passive voice ratio by section (spaCy or regex fallback)
- AI methods verbs (`was performed`, `was calculated`, etc.)
- Formulaic connectors, evaluation phrases, impersonal "it" constructions
- Sentence rhythm uniformity (stdev, shape CV)
- Hedge word stacking
- Zombie nouns, synonym drift, sentence-starter entropy

## Auto-rewriter (double-click mode)

Drop `.txt` or `.tex` files in `input/`, then double-click `run.bat` (Windows) or `./run.sh` (Mac/Linux).

**Pass 1 — Humanizer**: applies 30+ phrase-level substitutions across the whole document. Safe: never restructures sentences.

**Pass 2 — Sentence rewrites**: removes hedge stacks and academic filler openers from individual sentences.

Rewritten files appear in `output/` with `_rewritten` suffix.

## Folder structure

```
paper-writing-agent-v6/
├── run.py              ← main launcher
├── run.bat / run.sh    ← double-click launchers
├── _runner.py          ← auto-rewriter for double-click
├── rewrite_runner.py   ← rewrite library (v6: fixed sentence-cutting)
├── slop_lib/
│   ├── humanizer.py    ← NEW: humanizer skill integration
│   ├── analysis.py     ← core scoring engine
│   ├── ai_patterns.py  ← passive ratio, methods verbs, formulaic phrases
│   ├── linguistic.py   ← spaCy / regex passive detection
│   ├── report.py       ← report rendering
│   └── ...
├── scripts/
│   ├── slop_score.py   ← CLI scorer
│   └── ...
├── input/              ← drop papers here
├── output/             ← rewritten papers appear here
└── references/         ← writing style profiles
```

## Personal style setup (optional)

For more personalised feedback, build a corpus from your own published papers:

```bash
# 1. Drop your PDFs into scripts/pdfs/
# 2. Drop 2-3 field papers into scripts/reference_papers/
# 3. Run:
python run.py style
# Then compare your draft:
python run.py corpus my_draft.txt
```
