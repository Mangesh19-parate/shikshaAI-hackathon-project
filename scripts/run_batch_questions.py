"""
scripts/run_batch_questions.py — Phase 2, Task 2.4

Runs all 10 questions from data/sample_questions.json through TutorEngine
and saves raw outputs + quality check results to tests/test_outputs.md.

Usage (from repo root):
    python scripts/run_batch_questions.py

Requirements:
    - ollama serve must be running
    - gemma2:2b model must be pulled
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime

# Make sure app/ is importable from repo root
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.tutor_engine import TutorEngine

# ─── Paths ────────────────────────────────────────────────────────────────────
QUESTIONS_FILE = Path("data/sample_questions.json")
OUTPUT_FILE = Path("tests/test_outputs.md")

# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("PathShala Offline — Batch Question Runner (Phase 2.4)")
    print("=" * 60)

    engine = TutorEngine()

    if not engine._is_ollama_running():
        print("\n[!] ERROR: Ollama is not running.")
        print("    Start it with: ollama serve")
        print("    Then pull model: ollama pull gemma2:2b")
        sys.exit(1)

    print("[+] Ollama connected\n")

    # Load questions
    questions = json.loads(QUESTIONS_FILE.read_text(encoding="utf-8"))
    print(f"Loaded {len(questions)} questions\n")

    results = []
    passed_count = 0
    flagged_count = 0

    for i, q in enumerate(questions, 1):
        qid     = q["id"]
        lang    = q["language"]
        grade   = q["grade"]
        subject = q["subject"]
        topic   = q["topic"]
        question_text = q["question"]

        print(f"[{i:02d}/{len(questions)}] {qid} — {lang} — {topic}")
        print(f"  Q: {question_text[:80]}{'…' if len(question_text) > 80 else ''}")

        try:
            answer, attempts = engine.explain_with_retry(
                question=question_text,
                language=lang,
                grade_level=grade,
            )
            qc = engine.quality_check(answer, lang)

            status_icon = "[OK]" if qc["passed"] else "[!!]"
            print(f"  {status_icon} {qc['word_count']} words | attempts={attempts} | flags={qc['flags'] or 'none'}")

            if qc["passed"]:
                passed_count += 1
            else:
                flagged_count += 1

            results.append({
                "qid": qid,
                "lang": lang,
                "grade": grade,
                "subject": subject,
                "topic": topic,
                "question": question_text,
                "answer": answer,
                "qc": qc,
                "attempts": attempts,
            })

        except ConnectionError as e:
            print(f"  [!] Connection error: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"  [!] Error: {e}")
            results.append({
                "qid": qid,
                "lang": lang,
                "grade": grade,
                "subject": subject,
                "topic": topic,
                "question": question_text,
                "answer": f"ERROR: {e}",
                "qc": {"passed": False, "flags": [str(e)], "word_count": 0,
                        "has_steps": False, "has_sections": False,
                        "foreign_analogy": False, "latex_detected": False},
                "attempts": 0,
            })

        # Respectful pause between calls (avoid overwhelming CPU)
        time.sleep(1)

    # ── Write test_outputs.md ─────────────────────────────────────────────────
    write_markdown(results, passed_count, flagged_count)
    print(f"\n{'=' * 60}")
    print(f"[OK] Passed: {passed_count}/{len(questions)}")
    print(f"[!!] Flagged: {flagged_count}/{len(questions)}")
    print(f"\nOutputs saved to: {OUTPUT_FILE}")

    if flagged_count > 0:
        print("\n🔧 Flagged questions need prompt iteration (see test_outputs.md)")
        print("   Edit app/prompts.py and re-run this script until all pass.")


def write_markdown(results: list, passed: int, flagged: int):
    """Write structured test_outputs.md."""
    lines = [
        "# PathShala Offline — Batch Test Outputs (Phase 2.4)",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
        f"**Model:** gemma2:2b  ",
        f"**Total Questions:** {len(results)}  ",
        f"**Quality Check Passed:** {passed}/{len(results)}  ",
        f"**Flagged:** {flagged}/{len(results)}",
        "",
        "---",
        "",
        "## Summary Table",
        "",
        "| ID | Lang | Topic | Words | QC | Flags |",
        "|---|---|---|---|---|---|",
    ]

    for r in results:
        qc = r["qc"]
        status = "✅" if qc["passed"] else "⚠️"
        flags_short = "; ".join(qc["flags"])[:60] if qc["flags"] else "—"
        lines.append(
            f"| {r['qid']} | {r['lang']} | {r['topic']} | "
            f"{qc['word_count']} | {status} | {flags_short} |"
        )

    lines += ["", "---", "", "## Detailed Outputs", ""]

    for r in results:
        qc = r["qc"]
        status = "✅ PASSED" if qc["passed"] else "⚠️ FLAGGED"

        lines += [
            f"### {r['qid']} — {r['lang']} — {r['topic']}",
            "",
            f"**Subject:** {r['subject']}  ",
            f"**Grade:** {r['grade']}  ",
            f"**Status:** {status}  ",
            f"**Word count:** {qc['word_count']}  ",
            f"**Attempts:** {r['attempts']}  ",
            f"**Has steps:** {'✅' if qc['has_steps'] else '❌'}  ",
            f"**Has sections:** {'✅' if qc['has_sections'] else '❌'}  ",
            f"**Foreign analogy:** {'⚠️ YES' if qc['foreign_analogy'] else '✅ No'}  ",
            f"**LaTeX:** {'⚠️ YES' if qc['latex_detected'] else '✅ No'}  ",
        ]

        if qc["flags"]:
            lines.append(f"**Flags:** {'; '.join(qc['flags'])}")

        lines += [
            "",
            "**Question:**",
            f"> {r['question']}",
            "",
            "**Guruji's Answer:**",
            "",
            "```",
            r["answer"],
            "```",
            "",
            "---",
            "",
        ]

    # Phase 2.5 manual review section
    lines += [
        "## Phase 2.5 — Manual Quality Review",
        "",
        "Human reviewer: read 3 outputs and check:",
        "",
        "| Check | Q1 (M001) | Q2 (S001) | Q3 (M003) |",
        "|---|---|---|---|",
        "| Indian rural analogy present? | [ ] | [ ] | [ ] |",
        "| Steps numbered correctly? | [ ] | [ ] | [ ] |",
        "| Sounds like a teacher (not robot)? | [ ] | [ ] | [ ] |",
        "| Language pure (no wrong-lang mix)? | [ ] | [ ] | [ ] |",
        "| 'Try It Yourself' included? | [ ] | [ ] | [ ] |",
        "",
        "**Verdict:** [ ] GATE 2 PASSED &nbsp;&nbsp; [ ] Needs prompt iteration",
        "",
        "**Agent flags (auto):**",
        "",
    ]

    flagged = [r for r in results if not r["qc"]["passed"]]
    if flagged:
        for r in flagged:
            lines.append(f"- ⚠️ `{r['qid']}` ({r['lang']}): {'; '.join(r['qc']['flags'])}")
    else:
        lines.append("_No agent flags — all 10 outputs passed automated QC_ ✅")

    OUTPUT_FILE.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
