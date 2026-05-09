#!/usr/bin/env bash
# scripts/run.sh
# ─────────────────────────────────────────────────────────────────────────────
# PathShala Offline — Start the app
# Run: bash scripts/run.sh
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check Ollama
if ! command -v ollama &>/dev/null; then
    echo -e "${RED}✗ Ollama not found. Run: bash scripts/setup_ollama.sh${NC}"
    exit 1
fi

# Start Ollama in background if not running
if ! curl -s http://localhost:11434/api/tags &>/dev/null; then
    echo -e "${YELLOW}Starting Ollama server in background...${NC}"
    ollama serve &>/dev/null &
    sleep 2
fi

echo -e "${GREEN}✓ Ollama running${NC}"
echo -e "${YELLOW}Launching PathShala Offline...${NC}"
echo ""

cd "$(dirname "$0")/.."
streamlit run app/main.py --server.port 8501 --server.headless false
