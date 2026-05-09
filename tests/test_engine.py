"""
tests/test_engine.py — pytest suite for PathShala Offline  (Phase 1 + Phase 2)

Test classes:
  TestEngineInit        — unit tests, no Ollama needed ✅
  TestQualityCheck      — unit tests for quality_check(), no Ollama needed ✅
  TestPromptsModule     — unit tests for prompts.py, no Ollama needed ✅
  TestEngineIntegration — integration tests, require Ollama (skipped by default)

Run unit tests only (no Ollama):
    pytest tests/ -v

Run integration tests (need: ollama serve + gemma3n:e2b pulled):
    pytest tests/ -v -m integration
"""

import pytest
from app.tutor_engine import TutorEngine
from app.prompts import (
    get_system_prompt,
    get_required_sections,
    FORBIDDEN_ANALOGIES,
    SOCRATIC_TUTOR_EN,
    SOCRATIC_TUTOR_HI,
    SOCRATIC_TUTOR_MR,
)


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def engine():
    return TutorEngine()


# ─────────────────────────────────────────────────────────────────────────────
# Unit tests — engine init (no Ollama)
# ─────────────────────────────────────────────────────────────────────────────

class TestEngineInit:
    def test_default_model(self, engine):
        assert engine.model == "gemma3n:e2b"

    def test_default_host(self, engine):
        assert engine.host == "http://localhost:11434"

    def test_is_ollama_running_returns_bool(self, engine):
        assert isinstance(engine._is_ollama_running(), bool)

    def test_build_messages_structure(self, engine):
        msgs = engine._build_messages("Solve 2x+5=15", "English", "Grade 10")
        assert len(msgs) == 2
        assert msgs[0]["role"] == "system"
        assert msgs[1]["role"] == "user"
        assert "Grade 10" in msgs[1]["content"]
        assert "Solve 2x+5=15" in msgs[1]["content"]

    def test_build_messages_hindi(self, engine):
        msgs = engine._build_messages("3x - 7 = 14", "Hindi", "Grade 9")
        system = msgs[0]["content"]
        # System prompt should contain Devanagari for Hindi
        assert any(ord(c) > 2304 for c in system), "Hindi system prompt should contain Devanagari"

    def test_build_messages_marathi(self, engine):
        msgs = engine._build_messages("x² - 5x + 6 = 0", "Marathi", "Grade 10")
        system = msgs[0]["content"]
        assert any(ord(c) > 2304 for c in system), "Marathi system prompt should contain Devanagari"


# ─────────────────────────────────────────────────────────────────────────────
# Unit tests — quality_check (no Ollama)
# ─────────────────────────────────────────────────────────────────────────────

class TestQualityCheck:
    """Phase 2.2 — quality_check() unit tests (no Ollama needed)."""

    GOOD_ANSWER_EN = """
**📌 Problem:**
We need to find the value of x in the equation 2x + 5 = 15.

**📝 Steps:**
Step 1: Think of x as a secret number hiding in a box. We have 2 boxes plus 5 extra mangoes, making 15 mangoes total.
Step 2: Remove the 5 extra mangoes from both sides: 2x + 5 - 5 = 15 - 5, so 2x = 10.
Step 3: We have 2 boxes with equal mangoes. Divide both sides by 2: x = 10 / 2 = 5.

**✅ Answer:**
**x = 5**
This means the unknown number is 5 — like finding out each box has 5 mangoes!

**🧠 Try It Yourself:**
Solve: 3x + 4 = 19. [Hint: Start by removing 4 from both sides, then divide.]

You've got this — keep going!
"""

    BAD_SHORT = "x = 5"

    BAD_NO_STEPS = """
**📌 Problem:** Solve 2x + 5 = 15

**✅ Answer:** x = 5 because we subtract 5 and divide by 2.

**🧠 Try It Yourself:** Try 3x + 4 = 19
This is a standard algebraic equation. The solution methodology involves isolating the variable.
"""

    BAD_LATEX = r"""
**📌 Problem:** Solve \(2x + 5 = 15\)
**📝 Steps:**
Step 1: Subtract 5: \(2x = 10\)
Step 2: Divide by 2: \(x = 5\)
**✅ Answer:** x = 5
**🧠 Try It Yourself:** Solve \(3x + 4 = 19\) [Hint: same method]
You are doing great keep going with your studies today!
"""

    BAD_FOREIGN = """
**📌 Problem:** Solve 2x + 5 = 15

**📝 Steps:**
Step 1: Think of x like slices of pizza — you have 2 pizzas plus 5 dollars.
Step 2: Remove 5 dollars: 2x = 10
Step 3: Divide by 2: x = 5

**✅ Answer:** x = 5 — each pizza slice is worth 5 dollars.

**🧠 Try It Yourself:** Solve 3x + 2 = 14 [Hint: same method]
Great effort student!
"""

    def test_good_answer_passes(self, engine):
        qc = engine.quality_check(self.GOOD_ANSWER_EN, "English")
        assert qc["passed"], f"Expected to pass, got flags: {qc['flags']}"
        assert qc["has_steps"]
        assert qc["has_sections"]
        assert not qc["foreign_analogy"]
        assert not qc["latex_detected"]

    def test_too_short_flagged(self, engine):
        qc = engine.quality_check(self.BAD_SHORT, "English")
        assert not qc["passed"]
        assert qc["word_count"] < 100
        assert any("too_short" in f for f in qc["flags"])

    def test_missing_steps_flagged(self, engine):
        qc = engine.quality_check(self.BAD_NO_STEPS, "English")
        assert not qc["passed"]
        assert not qc["has_steps"]

    def test_latex_flagged(self, engine):
        qc = engine.quality_check(self.BAD_LATEX, "English")
        assert not qc["passed"]
        assert qc["latex_detected"]

    def test_foreign_analogy_flagged(self, engine):
        qc = engine.quality_check(self.BAD_FOREIGN, "English")
        assert not qc["passed"]
        assert qc["foreign_analogy"]

    def test_word_count_accurate(self, engine):
        text = "one two three four five"
        qc = engine.quality_check(text, "English")
        assert qc["word_count"] == 5

    def test_hindi_sections_detected(self, engine):
        hindi_ok = """
**📌 समस्या:** 2x + 5 = 15 में x का मान निकालो।

**📝 पायदान (Steps):**
Step 1: रोटी की तरह सोचो — दो थाली में बराबर रोटियाँ और 5 अतिरिक्त।
Step 2: 5 हटाओ: 2x = 10
Step 3: 2 से भाग दो: x = 5

**✅ उत्तर:** x = 5 — हर थाली में 5 रोटियाँ थीं।

**🧠 खुद करके देखो:** 3x + 4 = 19 हल करो [संकेत: पहले 4 हटाओ]

बहुत अच्छा सवाल किया! एक और करके देखो।
"""
        qc = engine.quality_check(hindi_ok, "Hindi")
        assert qc["has_steps"]
        assert qc["has_sections"]

    def test_marathi_sections_detected(self, engine):
        marathi_ok = """
**📌 समस्या:** 2x + 5 = 15 मध्ये x शोधा.

**📝 पायऱ्या:**
पायरी 1: आंब्याच्या टोपल्यांसारखा विचार करा.
पायरी 2: 5 वजा करा: 2x = 10
पायरी 3: 2 ने भागा: x = 5

**✅ उत्तर:** **x = 5** — प्रत्येक टोपलीत 5 आंबे होते.

**🧠 स्वतः करून पहा:** 3x + 4 = 19 सोडवा [संकेत: आधी 4 वजा करा]

गुरुजींना तुमचा अभिमान आहे!
"""
        qc = engine.quality_check(marathi_ok, "Marathi")
        assert qc["has_steps"]
        assert qc["has_sections"]


# ─────────────────────────────────────────────────────────────────────────────
# Unit tests — prompts module (no Ollama)
# ─────────────────────────────────────────────────────────────────────────────

class TestPromptsModule:
    def test_all_three_prompts_exist(self):
        assert len(SOCRATIC_TUTOR_EN) > 500
        assert len(SOCRATIC_TUTOR_HI) > 500
        assert len(SOCRATIC_TUTOR_MR) > 500

    def test_get_system_prompt_english(self):
        p = get_system_prompt("English")
        assert "Guruji" in p
        assert "Step 1" in p

    def test_get_system_prompt_hindi(self):
        p = get_system_prompt("Hindi")
        assert "गुरुजी" in p

    def test_get_system_prompt_marathi(self):
        p = get_system_prompt("Marathi")
        assert "गुरुजी" in p

    def test_fallback_to_english(self):
        p = get_system_prompt("French")
        assert "Guruji" in p  # falls back to English

    def test_forbidden_analogies_list_nonempty(self):
        assert len(FORBIDDEN_ANALOGIES) > 0
        assert "pizza" in FORBIDDEN_ANALOGIES
        assert "dollar" in FORBIDDEN_ANALOGIES

    def test_required_sections_english(self):
        secs = get_required_sections("English")
        assert "Step 1" in secs
        assert "Answer" in secs
        assert "Try It Yourself" in secs

    def test_required_sections_hindi(self):
        secs = get_required_sections("Hindi")
        assert "उत्तर" in secs

    def test_required_sections_marathi(self):
        secs = get_required_sections("Marathi")
        assert "उत्तर" in secs

    def test_no_latex_in_prompts(self):
        """System prompts themselves must not contain *actual* LaTeX math.
        They may mention LaTeX as a banned style, but must not use it to typeset math.
        We detect misuse by looking for $$ followed by math chars or \( followed by digits.
        """
        import re
        # Only flag actual LaTeX math usage, not the prohibition-clause mention
        latex_math_pattern = re.compile(r'\$\$.+?\$\$|\\\(.+?\\\)')
        for prompt in [SOCRATIC_TUTOR_EN, SOCRATIC_TUTOR_HI, SOCRATIC_TUTOR_MR]:
            match = latex_math_pattern.search(prompt)
            assert not match, (
                f"System prompt contains actual LaTeX math: {match.group()!r}"
            )

    def test_english_prompt_structure(self):
        """The English prompt must have the key structural markers."""
        prompt = SOCRATIC_TUTOR_EN
        assert "Step 1" in prompt, "Prompt missing 'Step 1' example"
        assert "Try It Yourself" in prompt, "Prompt missing 'Try It Yourself' section"
        assert "Answer" in prompt, "Prompt missing 'Answer' section"
        assert "analogy" in prompt.lower() or "roti" in prompt.lower(), \
            "Prompt should reference Indian analogies"


# ─────────────────────────────────────────────────────────────────────────────
# Integration tests — require Ollama + gemma3n:e2b
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.integration
class TestEngineIntegration:
    """
    GATE 1 + GATE 2 integration tests.
    Run with: pytest tests/ -v -m integration
    (Requires: ollama serve + gemma3n:e2b pulled)
    """

    def test_algebra_answer_contains_x_equals_5(self, engine):
        """GATE 1 core test."""
        answer = engine.explain("Solve 2x + 5 = 15", "English", "Grade 10")
        assert answer, "Engine returned empty response"
        normalised = answer.replace(" ", "").lower()
        assert "x=5" in normalised, f"Expected 'x = 5' in answer:\n{answer}"

    def test_answer_passes_quality_check(self, engine):
        """GATE 2: English answer should pass automated QC."""
        answer = engine.explain("Solve 2x + 5 = 15", "English", "Grade 10")
        qc = engine.quality_check(answer, "English")
        assert qc["passed"], f"QC failed: {qc['flags']}"

    def test_answer_has_all_four_sections(self, engine):
        answer = engine.explain("Solve 2x + 5 = 15", "English", "Grade 10")
        assert "Step 1" in answer
        assert "Answer" in answer.lower() or "✅" in answer
        assert "Try It Yourself" in answer or "स्वतः" in answer

    def test_hindi_passes_quality_check(self, engine):
        answer = engine.explain("3x - 7 = 14 के लिए x का मान निकालो", "Hindi", "Grade 9")
        qc = engine.quality_check(answer, "Hindi")
        assert qc["word_count"] >= 50, f"Hindi answer too short: {qc['word_count']} words"

    def test_marathi_passes_quality_check(self, engine):
        answer = engine.explain("x² - 5x + 6 = 0 हे समीकरण सोडवा", "Marathi", "Grade 10")
        qc = engine.quality_check(answer, "Marathi")
        assert qc["word_count"] >= 50, f"Marathi answer too short: {qc['word_count']} words"

    def test_retry_returns_longer_answer(self, engine):
        answer, attempts = engine.explain_with_retry("Solve 2x + 5 = 15", "English", "Grade 10")
        assert len(answer.split()) >= 80, f"Retry answer too short: {len(answer.split())} words"

    def test_simplify_returns_different_answer(self, engine):
        original = engine.explain("Solve 2x + 5 = 15", "English", "Grade 10")
        simpler = engine.simplify(original, "English")
        assert simpler.strip(), "Simplify returned empty"
        assert simpler != original, "Simplified answer is identical to original"

    def test_stream_yields_chunks(self, engine):
        chunks = list(engine.stream_explain("Solve 2x + 5 = 15", "English", "Grade 10"))
        assert len(chunks) > 3, "Stream yielded too few chunks"
        full = "".join(chunks)
        assert len(full.split()) >= 50, f"Streamed answer too short: {len(full.split())} words"

    def test_connection_error_when_bad_host(self):
        bad_engine = TutorEngine(host="http://localhost:99999")
        with pytest.raises(ConnectionError):
            bad_engine.explain("Solve 2x + 5 = 15")
