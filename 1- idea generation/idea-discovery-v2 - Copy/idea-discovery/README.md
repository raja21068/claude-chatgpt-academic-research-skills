# Idea Discovery Pipeline

Turn research papers into novel, verified research ideas.

## How it works

```
You have 50 papers → Run pipeline → Get SESSION.md → Upload to any LLM → Get ideas
```

## Quick start (5 minutes)

```bash
# 1. Set your API key
cp .env.example .env
# Edit .env: ANTHROPIC_API_KEY=sk-ant-your-key-here

# 2. Drop papers into input_papers/
#    (PDF, TXT, or MD files)

# 3. Run
chmod +x run.sh
./run.sh --topic "Your Research Topic"

# 4. Upload 2 files to Claude or ChatGPT:
#    - SKILL.md          (instructions — same every time)
#    - output/SESSION.md  (your research data — changes per topic)

# 5. Start asking questions!
```

## What you upload to the LLM

| File | What it is | Changes? |
|------|-----------|----------|
| **SKILL.md** | Instructions — tells the LLM how to be a research agent | Never (reusable) |
| **output/SESSION.md** | Your paper data — clusters, gaps, ideas, novelty verdicts | Per topic |

## What the LLM does automatically

1. **Analyzes** your session data — ranks existing ideas
2. **Searches online** for recent papers and new techniques
3. **Synthesizes** the best idea combining your data + new findings
4. **Generates implementation plan** — method, experiments, code structure, timeline

## Run modes

| Command | What it does |
|---------|-------------|
| `./run.sh` | Full pipeline |
| `./run.sh --lite` | Fast (no embeddings) |
| `./run.sh --topic "X"` | Labels the session |
| `./run.sh --checkpoint` | Pause for human review |
| `./run.sh --resume` | Resume from checkpoint |

## After running

```bash
# Optional: clean up PDFs to make folder small
./clean.sh

# Now you can zip and store
zip -r my-research.zip . -x '.venv/*'
```

## Modes (in SKILL.md)

- **General** (default) — any research domain
- **Robotics** — say "robotics mode" — sim-first, embodiment-aware
- **Patent** — say "patent mode" — invention disclosure format

## Cost estimate

| Papers | Mode | Cost | Time |
|--------|------|------|------|
| 20 | --lite | $0.50-1 | 5-10 min |
| 50 | full | $3-6 | 15-30 min |
| 100 | full | $5-10 | 30-60 min |

## Requirements

- Python 3.10+
- Anthropic API key
