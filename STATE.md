# PathShala Offline — Build State

## Current Phase
**Phase 1 — SCAFFOLD & LOCAL GEMMA**

## Last Completed Sub-task
**1.7** — README.md written with 2-command setup section

## Next Sub-task
**GATE 1 verification** — run pytest, launch Streamlit, take smoke-test screenshot → `media/gate1_proof.png`, git tag `phase-1-complete`

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
| GATE 1 | pytest + Streamlit smoke test | ⏳ Pending | — |

## Blockers
None. Waiting for human to:
1. Run `pip install -r requirements.txt`
2. Run `ollama serve` (if not already running)
3. Ensure `gemma3n:e2b` is pulled: `ollama pull gemma3n:e2b`
4. Run `pytest tests/ -v` (unit tests pass without Ollama)
5. Run `streamlit run app/main.py`
6. Take screenshot → save as `media/gate1_proof.png`
7. Run `git tag phase-1-complete`

## Phase 2 Preview (once Gate 1 passes)
- Upgrade prompts (already written in prompts.py!)
- Add explain_with_retry() (already written in tutor_engine.py!)
- Add streaming to UI (already written in main.py!)
- Run 10 sample questions → tests/test_outputs.md
- Manual quality review

## Architecture Decisions
- `TutorEngine` uses `ollama` Python client (not raw requests) for cleaner API
- System prompts pre-built for all 3 languages — reduces phase 2 work
- Streaming already wired in Phase 1 main.py to avoid double-refactor
- Tests split: unit (always run) + integration (skipped by default, needs Ollama)

---
*Auto-updated by PathShala Build Agent*  
*Last updated: 2026-05-09T20:23:00+05:30*
