"""
tests/test_engine.py — pytest suite for PathShala Offline (Phase 1)

Gate 1 requirement:
  - Ask "Solve 2x+5=15" → output contains "x = 5" (or "x=5")
  - Ollama must be running locally for integration tests

Run with:
    pytest tests/ -v
"""

import pytest
from app.tutor_engine import TutorEngine


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def engine():
    """Create a single TutorEngine instance for all tests in this module."""
    return TutorEngine()


def _ollama_available(eng: TutorEngine) -> bool:
    return eng._is_ollama_running()


# ─────────────────────────────────────────────────────────────────────────────
# Unit tests (no Ollama needed)
# ─────────────────────────────────────────────────────────────────────────────

class TestEngineInit:
    def test_default_model(self, engine):
        assert engine.model == "gemma3n:e2b"

    def test_default_host(self, engine):
        assert engine.host == "http://localhost:11434"

    def test_is_ollama_running_returns_bool(self, engine):
        result = engine._is_ollama_running()
        assert isinstance(result, bool)

    def test_build_messages_structure(self, engine):
        msgs = engine._build_messages("Solve 2x+5=15", "English", "Grade 10")
        assert len(msgs) == 2
        assert msgs[0]["role"] == "system"
        assert msgs[1]["role"] == "user"
        assert "Grade 10" in msgs[1]["content"]
        assert "Solve 2x+5=15" in msgs[1]["content"]


# ─────────────────────────────────────────────────────────────────────────────
# Integration tests (require Ollama + gemma3n:e2b to be running)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.skipif(
    True,  # set to False manually when Ollama is confirmed running
    reason="Integration test — requires `ollama serve` and gemma3n:e2b model",
)
class TestEngineIntegration:
    """
    GATE 1 integration test.
    To run: set skipif to False, then: pytest tests/ -v -k integration
    """

    def test_algebra_answer_contains_x_equals_5(self, engine):
        """
        GATE 1 core test:
        Ask 'Solve 2x+5=15' → answer must contain 'x = 5' or 'x=5'.
        """
        answer = engine.explain(
            question="Solve 2x + 5 = 15",
            language="English",
            grade_level="Grade 10",
        )
        assert answer, "Engine returned empty response"
        # normalise whitespace for comparison
        normalised = answer.replace(" ", "").lower()
        assert "x=5" in normalised, (
            f"Expected 'x = 5' in answer, but got:\n{answer}"
        )

    def test_answer_minimum_length(self, engine):
        """Answer should be at least 50 words to qualify as an explanation."""
        answer = engine.explain(
            question="Solve 2x + 5 = 15",
            language="English",
            grade_level="Grade 10",
        )
        word_count = len(answer.split())
        assert word_count >= 50, (
            f"Answer too short ({word_count} words). Expected >= 50."
        )

    def test_hindi_question(self, engine):
        """Hindi question should produce a non-empty response."""
        answer = engine.explain(
            question="3x - 7 = 14 के लिए x का मान निकालो",
            language="Hindi",
            grade_level="Grade 9",
        )
        assert answer.strip(), "Hindi question returned empty response"

    def test_marathi_question(self, engine):
        """Marathi question should produce a non-empty response."""
        answer = engine.explain(
            question="x² - 5x + 6 = 0 हे समीकरण सोडवा",
            language="Marathi",
            grade_level="Grade 10",
        )
        assert answer.strip(), "Marathi question returned empty response"

    def test_connection_error_when_offline(self):
        """
        If Ollama host is wrong, engine should raise ConnectionError.
        """
        bad_engine = TutorEngine(host="http://localhost:99999")
        with pytest.raises(ConnectionError):
            bad_engine.explain("Solve 2x+5=15")

    def test_retry_gives_longer_answer(self, engine):
        """explain_with_retry should give >= 100-word response for a real question."""
        answer = engine.explain_with_retry(
            question="Solve 2x + 5 = 15",
            language="English",
            grade_level="Grade 10",
        )
        assert len(answer.split()) >= 100, (
            f"Retry answer still too short: {len(answer.split())} words"
        )
