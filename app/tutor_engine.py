"""
tutor_engine.py — Core AI engine for PathShala Offline

TutorEngine wraps Ollama's local Gemma 3n model and provides:
  - explain()            — single-shot explanation (Phase 1)
  - explain_with_retry() — retries if output <100 words (Phase 2)
  - simplify()           — re-prompts for a simpler version (Phase 2)
  - stream_explain()     — generator for live streaming (Phase 2)

All methods gracefully handle the case where Ollama is not running.
"""

import ollama
from app.prompts import get_system_prompt


class TutorEngine:
    """Offline AI tutor backed by a local Gemma 3n model via Ollama."""

    def __init__(
        self,
        model: str = "gemma3n:e2b",
        host: str = "http://localhost:11434",
        max_retries: int = 3,
    ):
        self.model = model
        self.host = host
        self.max_retries = max_retries
        self._client = ollama.Client(host=host)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _is_ollama_running(self) -> bool:
        """Return True if the Ollama server responds."""
        try:
            self._client.list()
            return True
        except Exception:
            return False

    def _build_messages(
        self, question: str, language: str, grade_level: str
    ) -> list[dict]:
        system_prompt = get_system_prompt(language)
        user_content = (
            f"[{grade_level} | {language}]\n\n{question}"
        )
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]

    # ------------------------------------------------------------------
    # Phase 1: basic single-shot explain
    # ------------------------------------------------------------------

    def explain(self, question: str, language: str = "English", grade_level: str = "Grade 10") -> str:
        """
        Ask Gemma to explain the given question.
        Returns the model's response as a plain string.
        Raises ConnectionError if Ollama is not running.
        """
        if not self._is_ollama_running():
            raise ConnectionError(
                "Ollama is not running. Please start it with: ollama serve"
            )

        messages = self._build_messages(question, language, grade_level)
        try:
            response = self._client.chat(
                model=self.model,
                messages=messages,
                stream=False,
            )
            # ollama >= 0.4 returns a Pydantic ChatResponse object
            if hasattr(response, "message"):
                return response.message.content
            # fallback for older dict-style response
            return response["message"]["content"]
        except Exception as exc:
            raise RuntimeError(f"Model inference failed: {exc}") from exc

    # ------------------------------------------------------------------
    # Phase 2: retry + simplify + streaming
    # ------------------------------------------------------------------

    def explain_with_retry(
        self, question: str, language: str = "English", grade_level: str = "Grade 10"
    ) -> str:
        """
        Like explain(), but retries up to max_retries times
        if the output is shorter than 100 words.
        """
        for attempt in range(1, self.max_retries + 1):
            result = self.explain(question, language, grade_level)
            if len(result.split()) >= 100:
                return result
            # Too short — retry
            if attempt < self.max_retries:
                continue
        return result  # return whatever we got on last attempt

    def simplify(self, original_answer: str, language: str = "English") -> str:
        """
        Given a previous answer, ask the model to re-explain it
        in even simpler terms — for students who still didn't understand.
        """
        if not self._is_ollama_running():
            raise ConnectionError(
                "Ollama is not running. Please start it with: ollama serve"
            )

        system_prompt = get_system_prompt(language)
        simplify_instruction = {
            "English": "The student said they did not understand the previous explanation. Please re-explain using an even simpler analogy — imagine explaining to a 12-year-old in a village. Use the same structured format.",
            "Hindi": "विद्यार्थी ने कहा कि उन्हें पिछली व्याख्या समझ नहीं आई। कृपया एक और सरल उपमा से दोबारा समझाएं — जैसे गाँव के 12 साल के बच्चे को समझाना हो। वही structured format इस्तेमाल करें।",
            "Marathi": "विद्यार्थ्याने सांगितले की त्यांना आधीचे उत्तर समजले नाही. कृपया आणखी सोप्या उपमेने पुन्हा समजावून सांगा — जणू गावातील 12 वर्षाच्या मुलाला सांगायचे आहे. तोच structured format वापरा.",
        }

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "assistant", "content": original_answer},
            {
                "role": "user",
                "content": simplify_instruction.get(language, simplify_instruction["English"]),
            },
        ]
        try:
            response = self._client.chat(
                model=self.model,
                messages=messages,
                stream=False,
            )
            if hasattr(response, "message"):
                return response.message.content
            return response["message"]["content"]
        except Exception as exc:
            raise RuntimeError(f"Simplify failed: {exc}") from exc

    def stream_explain(
        self, question: str, language: str = "English", grade_level: str = "Grade 10"
    ):
        """
        Generator that yields text chunks from Ollama's streaming API.
        Use in Streamlit with st.write_stream().
        """
        if not self._is_ollama_running():
            raise ConnectionError(
                "Ollama is not running. Please start it with: ollama serve"
            )

        messages = self._build_messages(question, language, grade_level)
        stream = self._client.chat(
            model=self.model,
            messages=messages,
            stream=True,
        )
        for chunk in stream:
            # ollama >= 0.4: chunk is a ChatResponse Pydantic object
            if hasattr(chunk, "message"):
                content = chunk.message.content or ""
            else:
                content = chunk.get("message", {}).get("content", "")
            if content:
                yield content
