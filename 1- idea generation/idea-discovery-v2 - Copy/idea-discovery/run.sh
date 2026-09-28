#!/usr/bin/env bash
# Run the idea discovery pipeline
# Usage:
#   ./run.sh                         Full pipeline
#   ./run.sh --lite                  Fast (no embeddings, no quality checks)
#   ./run.sh --topic "My Topic"      Label the session file
#   ./run.sh --checkpoint            Pause for human review after gaps
#   ./run.sh --resume                Resume from checkpoint
#   ./run.sh --session-only          Regenerate session file only

set -e
cd "$(dirname "$0")"

ARGS="$@"
[[ "$ARGS" == *"--lite"* ]] && ARGS="${ARGS//--lite/--skip-embeddings --no-quality}"

[ -f .env ] && { set -a; source .env; set +a; }

if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "ERROR: Set ANTHROPIC_API_KEY in .env file"
    echo "  cp .env.example .env && nano .env"
    exit 1
fi

[ -d ".venv" ] || python3 -m venv .venv
source .venv/bin/activate
pip install -q -r requirements.txt 2>/dev/null

mkdir -p input_papers output logs

if [ -z "$(ls input_papers/*.pdf input_papers/*.txt input_papers/*.md 2>/dev/null)" ]; then
    if [[ "$ARGS" != *"--session-only"* ]] && [[ "$ARGS" != *"--resume"* ]] && [[ "$ARGS" != *"--dashboard-only"* ]]; then
        echo "No papers in input_papers/. Add PDF/TXT/MD files."
        exit 0
    fi
fi

python scripts/run_pipeline.py $ARGS

echo ""
echo "Done! Upload these 2 files to any LLM:"
echo "  1. SKILL.md          (instructions — reusable)"
echo "  2. output/SESSION.md (your research data)"
echo ""
echo "Or run: ./clean.sh  to remove PDFs and shrink for easy zipping"
