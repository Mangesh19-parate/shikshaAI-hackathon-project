#!/usr/bin/env bash
# scripts/setup_ollama.sh
# ─────────────────────────────────────────────────────────────────────────────
# PathShala Offline — One-time Ollama + Gemma 3n Setup Script
# OS: Linux / macOS (use WSL on Windows)
# Run: bash scripts/setup_ollama.sh
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== PathShala Offline — Ollama Setup ===${NC}"
echo ""

# ── Step 1: Install Ollama if not present ─────────────────────────────────────
if command -v ollama &>/dev/null; then
    echo -e "${GREEN}✓ Ollama already installed: $(ollama --version)${NC}"
else
    echo -e "${YELLOW}Installing Ollama...${NC}"
    curl -fsSL https://ollama.com/install.sh | sh
    echo -e "${GREEN}✓ Ollama installed successfully${NC}"
fi

# ── Step 2: Start Ollama server (background) ──────────────────────────────────
echo ""
echo -e "${YELLOW}Starting Ollama server...${NC}"
ollama serve &>/dev/null &
OLLAMA_PID=$!
sleep 3  # wait for server to be ready

# Verify server
if curl -s http://localhost:11434/api/tags &>/dev/null; then
    echo -e "${GREEN}✓ Ollama server running (PID: $OLLAMA_PID)${NC}"
else
    echo -e "${RED}✗ Ollama server failed to start. Try manually: ollama serve${NC}"
    exit 1
fi

# ── Step 3: Pull Gemma 3n E2B model ──────────────────────────────────────────
echo ""
echo -e "${YELLOW}Pulling gemma3n:e2b model (~2GB, one-time download)...${NC}"
echo -e "${YELLOW}NOTE: After this, the app works 100% offline.${NC}"
echo ""

if ollama pull gemma3n:e2b; then
    echo -e "${GREEN}✓ Model downloaded successfully${NC}"
else
    echo -e "${RED}✗ Model pull failed. Check internet connection for this one-time setup.${NC}"
    exit 1
fi

# ── Step 4: Verify with a test query ─────────────────────────────────────────
echo ""
echo -e "${YELLOW}Running smoke test...${NC}"
TEST_RESPONSE=$(ollama run gemma3n:e2b "Reply with exactly: PATHSHALA_OK" 2>/dev/null || echo "")

if [[ -z "$TEST_RESPONSE" ]]; then
    echo -e "${RED}✗ Smoke test failed — model not responding${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Model responding: ${TEST_RESPONSE}${NC}"

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}  Setup complete! PathShala Offline ready.${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo ""
echo -e "Next step:"
echo -e "  ${YELLOW}bash scripts/run.sh${NC}"
echo ""
echo -e "Or manually:"
echo -e "  ${YELLOW}ollama serve${NC}   (keep this running in background)"
echo -e "  ${YELLOW}streamlit run app/main.py${NC}"
