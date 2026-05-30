# PathShala Offline 📚

![App Demo](media/demo.gif)

> **Offline AI tutor for rural Indian students · Gemma 3n · Hindi/Marathi/English · Voice I/O · No internet required**  
> Works entirely without internet after a one-time model download.  
> Powered by **Gemma 3n (E2B variant)** running locally via Ollama.

![Hindi Conversation](media/hindi_convo_screenshot.png)
![Explain Simpler Feature](media/explain_simpler_screenshot.png)

---

## 🚀 2-Command Setup

```bash
# 1. Install dependencies + download the AI model (one-time, needs internet ~2GB)
bash scripts/setup_ollama.sh

# 2. Run the app (works 100% offline from here)
bash scripts/run.sh
```

> **Windows users:** Use WSL or Git Bash for the shell scripts, OR run manually:
> ```powershell
> # In terminal 1
> ollama serve
>
> # In terminal 2
> pip install -r requirements.txt
> streamlit run app/main.py
> ```

---

## ✨ Features

| Feature | Status |
|---|---|
| 📖 Step-by-step explanations (Socratic method) | ✅ Phase 1 |
| 🌐 English / Hindi / Marathi support | ✅ Phase 1 |
| ⚡ Live streaming output | ✅ Phase 2 |
| 🔁 "Explain simpler" button | ✅ Phase 2 |
| ✈️ Airplane-mode proof UI badge | ✅ Phase 3 |
| 🎤 Voice input (Whisper.cpp, offline) | ✅ Phase 3 |
| 🔊 Voice output (pyttsx3 TTS, offline) | ✅ Phase 3 |
| 📚 Lesson history (SQLite) | ✅ Phase 3 |

---

## 🎯 Who Is This For?

**Priya**, a 10th-grade student near Nashik, Maharashtra:
- Studies alone at night by oil lamp
- No reliable internet
- Weak in algebra and science
- Exam in 2 weeks

PathShala Offline puts a patient, multilingual tutor on her laptop — forever.

---

## 🏗️ Architecture

```
pathshala-offline/
├── backend/
│   ├── api/
│   │   ├── auth/           # Dependencies and security
│   │   ├── db/             # SQLite connection & ORM
│   │   ├── middleware/     # Rate limiting & logging
│   │   ├── models/         # Pydantic schemas
│   │   ├── routes/         # FastAPI endpoints
│   │   ├── services/       # LLM & RAG integration
│   │   └── main.py         # FastAPI application
│   └── Dockerfile          # Backend container definition
├── frontend/
│   ├── app.py              # Streamlit interface
│   ├── Dockerfile          # Frontend container definition
│   └── index.html          # Vanilla HTML fallback
├── data/
│   └── ncert_pdfs/         # Curriculum dataset (DVC tracked)
├── scripts/
│   ├── setup_ollama.sh     # Local model setup
│   └── run.sh              # Start local dev environment
├── tests/
│   ├── test_api.py         # Integration tests
│   └── conftest.py         # Pytest fixtures
├── docker-compose.yml      # Multi-container orchestration
└── submission/             # Kaggle & hackathon materials
```

---

## 🔧 Requirements

- Python 3.11+
- [Ollama](https://ollama.com) (free, open-source)
- 8 GB RAM minimum (runs on CPU)
- ~2.5 GB disk for the model

---

## 🧪 Running Tests

```bash
# Unit tests (no Ollama needed)
pytest tests/ -v

# Integration tests (requires ollama serve + model)
# Edit test_engine.py: set skipif=False
pytest tests/ -v
```

---

## 📜 License

- **Code:** MIT License
- **Content (prompts, questions):** CC-BY-4.0

---

## 🌟 Hackathon Submission

Built for the [Gemma 3n Impact Challenge](https://kaggle.com) hackathon.  
19-day build by a solo developer.  
Video: [YouTube Demo Link](https://youtube.com/...)  
Writeup: [Kaggle link — coming Phase 5]
