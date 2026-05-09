# PathShala Offline — Build State

## Current Phase
**Phase 1 — SCAFFOLD & LOCAL GEMMA** ✅ Code Complete — Awaiting Ollama

## Last Completed Sub-task
**GATE 1 partial** — pytest ✅ (4 passed, 6 skipped), Streamlit UI launches ✅, UI smoke test ✅ (connection error correctly shown — Ollama not yet running)

## Next Sub-task
**GATE 1 final** — User must:
1. Run `ollama serve` in a terminal
2. Run `ollama pull gemma3n:e2b` (one-time, ~2GB)
3. Then re-run the Streamlit smoke test: ask "Solve 2x+5=15" → capture screenshot → save to `media/gate1_proof.png`
4. Mark `phase-1-complete` git tag

## Sub-task Completion Log

| Sub-task | Description | Status | Timestamp |
|---|---|---|---|
| 1.1 | Folder structure created | ✅ Done | 2026-05-09T20:19 IST |
| 1.2 | scripts/setup_ollama.sh written | ✅ Done | 2026-05-09T20:20 IST |
| 1.3 | app/tutor_engine.py — TutorEngine class | ✅ Done | 2026-05-09T20:21 IST |
| 1.4 | app/main.py — Streamlit UI | ✅ Done | 2026-05-09T20:22 IST |
| 1.5 | data/sample_questions.json — 10 SSC questions | ✅ Done | 2026-05-09T20:22 IST |
| 1.6 | tests/test_engine.py — pytest suite | ✅ Done | 2026-05-09T20:22 IST |
| 1.7 | README.md — 2-command setup | ✅ Done | 2026-05-09T20:23 IST |
| 1.8 | app/prompts.py — Socratic prompts (EN/HI/MR) | ✅ Done | 2026-05-09T20:19 IST |
| 1.9 | app/language.py — UI strings | ✅ Done | 2026-05-09T20:20 IST |
| pytest 4/4 | Unit tests pass (integration skipped) | ✅ Done | 2026-05-09T20:25 IST |
| Streamlit | App launches at localhost:8501 | ✅ Done | 2026-05-09T20:30 IST |
| ollama 0.6.2 fix | Response parsing fixed for Pydantic API | ✅ Done | 2026-05-09T20:31 IST |
| GATE 1 | pytest + Streamlit smoke test | ⏳ Awaiting Ollama | — |

## Blockers
🚧 **BLOCKER: Ollama not running / gemma3n:e2b not pulled**

The Streamlit UI is fully built and running. Pytest passes (4/4). The app correctly shows a connection error when Ollama is offline.

To unblock Gate 1, you need to run these **one time** (needs internet for model download):
```powershell
# Terminal 1 — keep this running
ollama serve

# Terminal 2 — one-time download (~2GB)
ollama pull gemma3n:e2b
```

After that:
```powershell
# Ask Guruji "Solve 2x + 5 = 15" in the browser at http://localhost:8501
# Screenshot → save to media/gate1_proof.png
# Then tell the agent to continue
```

## Phase 2 Preview (once Gate 1 passes)
- Upgrade prompts (already written in prompts.py!)
- Add explain_with_retry() (already written in tutor_engine.py!)
- Add streaming to UI (already written in main.py!)
- Run 10 sample questions → tests/test_outputs.md
- Manual quality review

## Architecture Decisions
- `TutorEngine` uses `ollama` Python client v0.6.2 (Pydantic ChatResponse objects)
- Response parsing: `response.message.content` with dict fallback for compatibility
- System prompts pre-built for all 3 languages — reduces phase 2 work
- Streaming already wired in Phase 1 main.py to avoid double-refactor
- Tests split: unit (always run) + integration (skipped by default, needs Ollama)
- Anaconda Python 3.12.7 at `C:\Users\HP\anaconda3\python.exe`
- Streamlit 1.37.1, ollama 0.6.2, pytest 7.4.4, pyttsx3 2.99

---
*Auto-updated by PathShala Build Agent*
*Last updated: 2026-05-09T20:35:00+05:30*
