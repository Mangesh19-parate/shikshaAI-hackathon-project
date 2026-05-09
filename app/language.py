"""
language.py — Language utilities for PathShala Offline

Provides:
  - SUPPORTED_LANGUAGES: ordered list for UI dropdown
  - LANGUAGE_CODES: map to ISO codes (for whisper, TTS)
  - UI_STRINGS: translated UI labels per language
"""

SUPPORTED_LANGUAGES = ["English", "Hindi", "Marathi"]

LANGUAGE_CODES = {
    "English": "en",
    "Hindi": "hi",
    "Marathi": "mr",
}

SUBJECTS = ["Mathematics", "Science", "Social Studies", "English Grammar"]

GRADE_LEVELS = ["Grade 9", "Grade 10"]

# UI strings per language for localised interface
UI_STRINGS = {
    "English": {
        "app_title": "📚 PathShala Offline — Your AI Tutor",
        "app_subtitle": "Learn anytime, anywhere — even without internet",
        "language_label": "🌐 Language",
        "grade_label": "🎓 Grade",
        "subject_label": "📖 Subject",
        "question_label": "❓ Your Question",
        "question_placeholder": "Type your question here… e.g. Solve 2x + 5 = 15",
        "ask_button": "🤔 Ask Guruji",
        "simplify_button": "🙋 I didn't understand — Explain simpler",
        "listen_button": "🔊 Listen (TTS)",
        "thinking": "Guruji is thinking…",
        "no_question": "Please type a question first.",
        "error_ollama": "⚠️ Cannot connect to Ollama. Please run: `ollama serve` in your terminal.",
        "history_tab": "📚 My Lessons",
        "offline_tab": "✈️ Offline Test",
    },
    "Hindi": {
        "app_title": "📚 PathShala Offline — आपका AI शिक्षक",
        "app_subtitle": "कहीं भी, कभी भी सीखें — बिना internet के भी",
        "language_label": "🌐 भाषा",
        "grade_label": "🎓 कक्षा",
        "subject_label": "📖 विषय",
        "question_label": "❓ आपका सवाल",
        "question_placeholder": "यहाँ अपना सवाल लिखें… जैसे: 2x + 5 = 15 हल करो",
        "ask_button": "🤔 गुरुजी से पूछो",
        "simplify_button": "🙋 मुझे समझ नहीं आया — और सरल बताओ",
        "listen_button": "🔊 सुनो (TTS)",
        "thinking": "गुरुजी सोच रहे हैं…",
        "no_question": "पहले कोई सवाल लिखें।",
        "error_ollama": "⚠️ Ollama से connection नहीं हो पा रहा। Terminal में चलाएं: `ollama serve`",
        "history_tab": "📚 मेरे धडे",
        "offline_tab": "✈️ Offline टेस्ट",
    },
    "Marathi": {
        "app_title": "📚 PathShala Offline — तुमचा AI शिक्षक",
        "app_subtitle": "कधीही, कुठेही शिका — internet शिवाय सुद्धा",
        "language_label": "🌐 भाषा",
        "grade_label": "🎓 इयत्ता",
        "subject_label": "📖 विषय",
        "question_label": "❓ तुमचा प्रश्न",
        "question_placeholder": "इथे प्रश्न लिहा… उदा: 2x + 5 = 15 सोडवा",
        "ask_button": "🤔 गुरुजींना विचारा",
        "simplify_button": "🙋 मला समजलं नाही — अजून सोपं सांगा",
        "listen_button": "🔊 ऐका (TTS)",
        "thinking": "गुरुजी विचार करत आहेत…",
        "no_question": "आधी प्रश्न लिहा.",
        "error_ollama": "⚠️ Ollama शी connection होत नाही. Terminal मध्ये चालवा: `ollama serve`",
        "history_tab": "📚 माझे धडे",
        "offline_tab": "✈️ Offline चाचणी",
    },
}


def get_ui(language: str) -> dict:
    """Return UI string dict for the given language (fallback: English)."""
    return UI_STRINGS.get(language, UI_STRINGS["English"])
