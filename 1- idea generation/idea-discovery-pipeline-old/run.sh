#!/usr/bin/env bash
# ── Idea Discovery Pipeline — One-click launcher ─────────────────────────────
# Usage:
#   ./run.sh                     Full pipeline (auto)
#   ./run.sh --checkpoint        Pause after gaps for human review
#   ./run.sh --resume            Resume after editing checkpoint
#   ./run.sh --skip-embeddings   No ML deps (LLM-only clustering)
#   ./run.sh --dashboard-only    Regenerate dashboard from existing data
#   ./run.sh --no-quality        Skip quality checks (faster)
#   ./run.sh --lite              Shortcut for --skip-embeddings --no-quality
# ─────────────────────────────────────────────────────────────────────────────

set -e
cd "$(dirname "$0")"

# Parse --lite shortcut
ARGS="$@"
if [[ "$ARGS" == *"--lite"* ]]; then
    ARGS="${ARGS//--lite/--skip-embeddings --no-quality}"
fi

# Load .env if present
if [ -f .env ]; then
    echo "Loading .env..."
    set -a; source .env; set +a
fi

# Check API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "ERROR: ANTHROPIC_API_KEY not set."
    echo "  1. Copy .env.example to .env"
    echo "  2. Add your key"
    echo "  3. Run again"
    exit 1
fi

# Setup venv if needed
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate

# Install deps
echo "Checking dependencies..."
pip install -q -r requirements.txt 2>/dev/null

# Create dirs
mkdir -p input_papers output logs

# Check for papers
if [ -z "$(ls -A input_papers/ 2>/dev/null)" ]; then
    if [[ "$ARGS" != *"--dashboard-only"* ]] && [[ "$ARGS" != *"--resume"* ]]; then
        echo ""
        echo "No papers found in input_papers/"
        echo "Add your PDF, TXT, or MD files and run again."
        exit 0
    fi
fi

# Run
echo ""
python scripts/run_pipeline.py $ARGS
