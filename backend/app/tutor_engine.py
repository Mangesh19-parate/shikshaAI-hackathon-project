"""
tutor_engine.py — Core AI engine for PathShala Offline  (Phase 2)

TutorEngine wraps Ollama's local Gemma 3n model and provides:
  - explain()            — single-shot explanation
  - explain_with_retry() — retries if output <100 words (Phase 2)
  - simplify()           — re-prompts for a simpler version (Phase 2)
  - stream_explain()     — generator for live streaming (Phase 2)
  - quality_check()      — validate output meets pedagogy bar (Phase 2)

All methods gracefully handle the case where Ollama is not running.
"""

import re
import time
import os

import ollama
from huggingface_hub import InferenceClient

from backend.app.prompts import (
    FORBIDDEN_ANALOGIES,
    get_required_sections,
    get_system_prompt,
)


class TutorEngine:
    """Offline AI tutor backed by a local Gemma 4 model via Ollama."""

    def __init__(
        self,
        model: str = "gemma2:2b",
        host: str = "http://localhost:11434",
        max_retries: int = 3,
    ):
        self.model = model
        self.host = host
        self.max_retries = max_retries
        self.use_hf = os.environ.get("USE_HF_API", "false").lower() == "true"
        self.hf_model = os.environ.get("HF_MODEL", "google/gemma-1.1-7b-it")
        
        if self.use_hf:
            self._hf_client = InferenceClient(self.hf_model)
        else:
            self._client = ollama.Client(host=host)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _is_ollama_running(self) -> bool:
        """Return True if the Ollama server responds or if using HF."""
        if self.use_hf:
            return True
        try:
            self._client.list()
            return True
        except Exception:
            return False

    def _build_messages(
        self, question: str, language: str, grade_level: str
    ) -> list[dict]:
        system_prompt = get_system_prompt(language)
        user_content = f"[{grade_level} | {language}]\n\n{question}"
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]

    def _extract_content(self, response) -> str:
        """Extract plain text from an Ollama ChatResponse (Pydantic or dict)."""
        if hasattr(response, "message"):
            return response.message.content or ""
        return response.get("message", {}).get("content", "")

    def _extract_chunk(self, chunk) -> str:
        """Extract text from a streaming chunk."""
        if hasattr(chunk, "message"):
            return chunk.message.content or ""
        return chunk.get("message", {}).get("content", "")

    # ------------------------------------------------------------------
    # Phase 2.2 — Quality checker
    # ------------------------------------------------------------------

    def quality_check(self, text: str, language: str = "English") -> dict:
        """
        Validate that an output meets the Phase 2 pedagogy bar.

        Returns a dict:
          {
            "passed": bool,
            "flags": [list of issue strings],
            "word_count": int,
            "has_steps": bool,
            "has_sections": bool,
            "foreign_analogy": bool,
            "latex_detected": bool,
          }
        """
        flags = []

        # 1. Word count (strip markdown markers for a cleaner count)
        clean_text = re.sub(r"[\*#_>`]", "", text)
        word_count = len(clean_text.split())
        
        has_too_few = word_count < 100
        has_too_many = word_count > 600
        if has_too_few:
            flags.append(f"too_short ({word_count} words, need ≥100)")
        if has_too_many:
            flags.append(f"too_long ({word_count} words, prefer ≤500)")

        # 2. Numbered steps
        has_steps = bool(re.search(r"(Step\s*1|पायरी\s*1|पायदान\s*1)", text))
        if not has_steps:
            flags.append("missing_steps (no 'Step 1' or 'पायरी 1' found)")

        # 3. Required sections
        required = get_required_sections(language)
        missing_secs = [s for s in required if s.lower() not in text.lower()]
        has_sections = len(missing_secs) == 0
        if missing_secs:
            flags.append(f"missing_sections: {missing_secs}")

        # 4. LaTeX detection
        latex_detected = bool(re.search(r"\$\$|\\[\(\[]", text))
        if latex_detected:
            flags.append("latex_detected — use plain text math instead")

        # 5. Forbidden foreign analogies
        text_lower = text.lower()
        found_foreign = [a for a in FORBIDDEN_ANALOGIES if a in text_lower]
        foreign_analogy = len(found_foreign) > 0
        if foreign_analogy:
            flags.append(f"foreign_analogy: {found_foreign}")

        return {
            "passed": len(flags) == 0,
            "flags": flags,
            "word_count": word_count,
            "has_steps": has_steps,
            "has_sections": has_sections,
            "foreign_analogy": foreign_analogy,
            "latex_detected": latex_detected,
        }

    # ------------------------------------------------------------------
    # Phase 1 — basic single-shot explain
    # ------------------------------------------------------------------

    def explain(
        self,
        question: str,
        language: str = "English",
        grade_level: str = "Grade 10",
    ) -> str:
        """
        Ask Gemma to explain the given question.
        Returns the model response as a plain string.
        Raises ConnectionError if Ollama is not running.
        """
        if not self._is_ollama_running():
            raise ConnectionError(
                "Ollama is not running. Please start it with: ollama serve"
            )

        messages = self._build_messages(question, language, grade_level)
        try:
            if self.use_hf:
                res = self._hf_client.chat_completion(messages=messages, max_tokens=1000, stream=False)
                return res.choices[0].message.content or ""
            else:
                response = self._client.chat(
                    model=self.model,
                    messages=messages,
                    stream=False,
                )
                return self._extract_content(response)
        except Exception as exc:
            raise RuntimeError(f"Model inference failed: {exc}") from exc

    # ------------------------------------------------------------------
    # Phase 2.2 — explain_with_retry
    # ------------------------------------------------------------------

    def explain_with_retry(
        self,
        question: str,
        language: str = "English",
        grade_level: str = "Grade 10",
    ) -> tuple[str, int]:
        """
        Like explain(), but retries up to max_retries times if:
          - output is shorter than 100 words, OR
          - quality_check fails (missing sections / wrong language)

        Returns (answer_text, attempt_count).
        """
        last_result = ""
        for attempt in range(1, self.max_retries + 1):
            result = self.explain(question, language, grade_level)
            qc = self.quality_check(result, language)

            if qc["passed"] or attempt == self.max_retries:
                return result, attempt

            # If too short or missing critical sections — retry
            critical_fail = (
                qc["word_count"] < 100
                or not qc["has_steps"]
                or not qc["has_sections"]
            )
            if not critical_fail:
                # Non-critical issues (e.g., slightly too long) — accept
                return result, attempt

            last_result = result
            time.sleep(0.5)  # brief pause before retry

        return last_result, self.max_retries

    # ------------------------------------------------------------------
    # Phase 2.2 — simplify
    # ------------------------------------------------------------------

    def simplify(self, original_answer: str, language: str = "English") -> str:
        """
        Given a previous answer the student didn't understand,
        ask the model to re-explain in even simpler terms with
        a fresh rural analogy.
        """
        if not self._is_ollama_running():
            raise ConnectionError(
                "Ollama is not running. Please start it with: ollama serve"
            )

        system_prompt = get_system_prompt(language)
        simplify_instruction = {
            "English": (
                "The student didn't understand the previous explanation of their mistake. "
                "Re-explain the misconception using an EVEN SIMPLER real-world analogy and easier vocabulary. "
                "Maintain the empathetic notebook grading tone. Always include the 🔍 The Misconception, 💡 The Analogy, and ✅ The Correction sections."
            ),
            "Hindi": (
                "विद्यार्थी को अपनी गलती का पिछला स्पष्टीकरण समझ नहीं आया। "
                "एक और भी सरल वास्तविक दुनिया की उपमा का उपयोग करके गलतफहमी को फिर से समझाएं। "
                "सहानुभूतिपूर्ण स्वर बनाए रखें। हमेशा 🔍 गलतफहमी (The Misconception), 💡 असल ज़िंदगी का उदाहरण, और ✅ सही तरीका शामिल करें।"
            ),
            "Marathi": (
                "विद्यार्थ्याला त्याच्या चुकीचे मागील स्पष्टीकरण समजले नाही. "
                "आणखी सोप्या खऱ्या जगातील उदाहरणाचा वापर करून गैरसमज पुन्हा समजावून सांगा. "
                "सहानुभूतीपूर्ण टोन ठेवा. नेहमी 🔍 गैरसमज (The Misconception), 💡 खऱ्या जगातील उदाहरण, आणि ✅ योग्य पद्धत समाविष्ट करा."
            ),
        }

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "assistant", "content": original_answer},
            {
                "role": "user",
                "content": simplify_instruction.get(
                    language, simplify_instruction["English"]
                ),
            },
        ]
        try:
            if self.use_hf:
                res = self._hf_client.chat_completion(messages=messages, max_tokens=1000, stream=False)
                return res.choices[0].message.content or ""
            else:
                response = self._client.chat(
                    model=self.model,
                    messages=messages,
                    stream=False,
                )
                return self._extract_content(response)
        except Exception as exc:
            raise RuntimeError(f"Simplify failed: {exc}") from exc

    # ------------------------------------------------------------------
    # Phase 2.2 — stream_explain (live streaming)
    # ------------------------------------------------------------------

    def stream_explain(
        self,
        question: str,
        language: str = "English",
        grade_level: str = "Grade 10",
    ):
        """
        Generator that yields text chunks from Ollama's streaming API.
        Use in Streamlit with st.write_stream() or manual accumulation.
        """
        if not self._is_ollama_running():
            raise ConnectionError(
                "Ollama is not running. Please start it with: ollama serve"
            )

        messages = self._build_messages(question, language, grade_level)
        if self.use_hf:
            stream = self._hf_client.chat_completion(
                messages=messages,
                max_tokens=1000,
                stream=True,
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        else:
            stream = self._client.chat(
                model=self.model,
                messages=messages,
                stream=True,
            )
            for chunk in stream:
                content = self._extract_chunk(chunk)
                if content:
                    yield content
