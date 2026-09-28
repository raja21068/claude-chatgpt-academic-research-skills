#!/usr/bin/env bash
# Clean up after pipeline run — remove PDFs and heavy files
# Makes the folder small enough to zip and upload
set -e
cd "$(dirname "$0")"

echo "Cleaning up..."

# Delete input papers (already extracted)
rm -f input_papers/*.pdf input_papers/*.txt input_papers/*.md 2>/dev/null
echo "  ✓ Deleted input papers"

# Delete heavy output files (keep SESSION + key reports)
rm -f output/embeddings.npy 2>/dev/null
rm -rf output/extracted_text 2>/dev/null
rm -f logs/*.log 2>/dev/null
echo "  ✓ Deleted heavy files (embeddings, extracted text, logs)"

# Delete Python cache
find . -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null
echo "  ✓ Deleted Python cache"

# Show what remains
echo ""
echo "Remaining output files:"
ls -lh output/ 2>/dev/null
echo ""
echo "Total folder size:"
du -sh .
echo ""
echo "Ready to zip! Run:"
echo "  zip -r my-research.zip . -x '.venv/*'"
echo ""
echo "Then upload to any LLM:"
echo "  1. SKILL.md"
echo "  2. output/SESSION.md"
