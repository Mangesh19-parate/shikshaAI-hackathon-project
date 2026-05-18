"""
app/voice.py — Offline voice input/output for PathShala Offline (Phase 3.2 & 3.3)

Voice Input  (3.2): Offline speech-to-text via SpeechRecognition (CMU Sphinx offline)
             Falls back to: manual text input if mic unavailable
Voice Output (3.3): Offline text-to-speech via pyttsx3

WHY pyttsx3 over Whisper/Coqui-TTS:
  - pyttsx3 uses system TTS engines (SAPI5 on Windows, espeak on Linux)
  - Zero extra download — works immediately offline
  - Coqui-TTS Hindi/Marathi models are 500MB+ — too heavy for 8GB RAM target
  - pyttsx3 Devanagari rendering depends on Windows language packs

VOICE INPUT STRATEGY:
  - Primary: SpeechRecognition with Sphinx (offline, CMU PocketSphinx)
  - Fallback: If Sphinx not installed, show helpful install instructions
  - Language: basic multilingual keyword detection
"""

import io
import threading
from typing import Optional


# ─── TTS (pyttsx3) ────────────────────────────────────────────────────────────

def get_tts_engine():
    """Return a pyttsx3 engine instance, or None if unavailable."""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        return engine
    except Exception:
        return None


def speak_text(text: str, language: str = "English", rate: int = 145) -> bool:
    """
    Speak the given text using pyttsx3 (offline).

    Args:
        text:     Text to speak (Markdown stripped automatically)
        language: 'English', 'Hindi', or 'Marathi'
        rate:     Words per minute (default 145 — clear for students)

    Returns:
        True if speech succeeded, False if TTS engine unavailable.
    """
    engine = get_tts_engine()
    if engine is None:
        return False

    # Strip markdown so TTS doesn't read ** or ## aloud
    clean = _strip_markdown(text)

    try:
        engine.setProperty("rate", rate)

        # Attempt to select a voice that matches the language
        _set_voice_for_language(engine, language)

        # Run in a daemon thread so Streamlit doesn't block
        def _run():
            engine.say(clean)
            engine.runAndWait()

        t = threading.Thread(target=_run, daemon=True)
        t.start()
        return True
    except Exception:
        return False


def _strip_markdown(text: str) -> str:
    """Remove common markdown tokens so TTS reads cleanly."""
    import re
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)     # bold
    text = re.sub(r"\*(.+?)\*", r"\1", text)          # italic
    text = re.sub(r"#{1,6}\s", "", text)              # headings
    text = re.sub(r"[📌📝✅🧠🔊🎤📚✈️⚠️🟢🔴]", "", text)  # emoji
    text = re.sub(r"`+", "", text)                    # code ticks
    text = re.sub(r"\n{3,}", "\n\n", text)            # excess newlines
    return text.strip()


def _set_voice_for_language(engine, language: str) -> None:
    """Try to select a voice matching the language on Windows SAPI5."""
    try:
        voices = engine.getProperty("voices")
        lang_keywords = {
            "Hindi":   ["hindi", "hi-in", "indian"],
            "Marathi": ["marathi", "mr-in", "indian"],
            "English": ["english", "en-in", "en-us", "en-gb"],
        }
        target_kws = lang_keywords.get(language, ["english"])

        for voice in voices:
            name_lower = voice.name.lower()
            if any(kw in name_lower for kw in target_kws):
                engine.setProperty("voice", voice.id)
                return
        # No match — keep default voice
    except Exception:
        pass


def list_available_voices() -> list[dict]:
    """Return all available TTS voices for debug/settings UI."""
    engine = get_tts_engine()
    if engine is None:
        return []
    try:
        voices = engine.getProperty("voices")
        return [{"id": v.id, "name": v.name, "languages": v.languages} for v in voices]
    except Exception:
        return []


# ─── STT (SpeechRecognition / offline Sphinx) ─────────────────────────────────

def check_stt_available() -> dict:
    """
    Check which speech-to-text backends are available.
    Returns a dict with 'sphinx', 'pyaudio', 'vosk' availability flags.
    """
    result = {"sphinx": False, "pyaudio": False, "vosk": False, "any": False}
    try:
        import speech_recognition  # noqa: F401
        result["sphinx"] = True
    except ImportError:
        pass
    try:
        import pyaudio  # noqa: F401
        result["pyaudio"] = True
    except ImportError:
        pass
    try:
        import vosk  # noqa: F401
        result["vosk"] = True
    except ImportError:
        pass
    result["any"] = result["sphinx"] and result["pyaudio"]
    return result


def record_and_transcribe(
    duration: int = 8,
    language: str = "English",
) -> tuple[str, str]:
    """
    Record `duration` seconds of audio from the default microphone
    and transcribe it offline using CMU Sphinx.

    Returns:
        (transcribed_text, error_message)
        On success: (text, "")
        On failure: ("", error_reason)
    """
    stt = check_stt_available()
    if not stt["any"]:
        return "", (
            "SpeechRecognition or PyAudio not installed.\n"
            "Install with: pip install SpeechRecognition pyaudio"
        )

    try:
        import speech_recognition as sr

        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 300
        recognizer.dynamic_energy_threshold = True

        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.record(source, duration=duration)

        # Sphinx offline recognition
        # Language mapping (Sphinx supports limited languages)
        sphinx_lang = {"Hindi": "hi-IN", "Marathi": "mr-IN", "English": "en-US"}
        lang_code = sphinx_lang.get(language, "en-US")

        try:
            text = recognizer.recognize_sphinx(audio, language=lang_code)
            return text.strip(), ""
        except sr.UnknownValueError:
            return "", "Could not understand audio — please speak clearly."
        except sr.RequestError as e:
            # Sphinx not installed as offline engine
            return "", f"Sphinx engine error: {e}\nTry: pip install pocketsphinx"

    except OSError as e:
        return "", f"Microphone error: {e}"
    except Exception as e:
        return "", f"Recording failed: {e}"
