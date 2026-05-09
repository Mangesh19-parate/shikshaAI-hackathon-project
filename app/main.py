"""
main.py — PathShala Offline: Streamlit frontend

Phase 1: single-page UI with language, grade, subject, question, answer.
Phase 2 additions: streaming, simplify button, markdown output.
"""

import streamlit as st
from app.tutor_engine import TutorEngine
from app.language import SUPPORTED_LANGUAGES, SUBJECTS, GRADE_LEVELS, get_ui

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PathShala Offline — AI Tutor",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;600;700&family=Noto+Sans+Devanagari:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Noto Sans', 'Noto Sans Devanagari', sans-serif;
    }
    .main { background: #0f1117; }

    /* Header banner */
    .ps-header {
        background: linear-gradient(135deg, #1a472a 0%, #2d6a4f 50%, #1b4332 100%);
        border-radius: 16px;
        padding: 2rem 2.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid #40916c;
        box-shadow: 0 8px 32px rgba(45,106,79,0.3);
    }
    .ps-header h1 {
        color: #d8f3dc;
        font-size: 2rem;
        font-weight: 700;
        margin: 0 0 0.3rem 0;
    }
    .ps-header p {
        color: #95d5b2;
        font-size: 1rem;
        margin: 0;
    }

    /* Answer card */
    .answer-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 1rem;
        box-shadow: 0 4px 24px rgba(0,0,0,0.4);
    }

    /* Buttons */
    div.stButton > button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.2s ease;
        border: 1.5px solid #40916c;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(64,145,108,0.4);
    }

    /* Offline badge */
    .badge-offline {
        background: #1e3a1e;
        color: #52c41a;
        border: 1px solid #52c41a;
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
    }
    .badge-online {
        background: #3a1e1e;
        color: #ff4d4f;
        border: 1px solid #ff4d4f;
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Session state ─────────────────────────────────────────────────────────────
if "language" not in st.session_state:
    st.session_state.language = "English"
if "last_answer" not in st.session_state:
    st.session_state.last_answer = ""
if "last_question" not in st.session_state:
    st.session_state.last_question = ""

# ── Engine (cached so it's not re-instantiated on every rerun) ────────────────
@st.cache_resource
def get_engine():
    return TutorEngine()

engine = get_engine()

# ── UI strings ────────────────────────────────────────────────────────────────
lang = st.session_state.language
ui = get_ui(lang)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class="ps-header">
        <h1>{ui['app_title']}</h1>
        <p>{ui['app_subtitle']}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar controls ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    selected_lang = st.selectbox(
        ui["language_label"],
        SUPPORTED_LANGUAGES,
        index=SUPPORTED_LANGUAGES.index(st.session_state.language),
        key="lang_selector",
    )
    if selected_lang != st.session_state.language:
        st.session_state.language = selected_lang
        st.rerun()

    selected_grade = st.selectbox(ui["grade_label"], GRADE_LEVELS, index=1, key="grade_selector")
    selected_subject = st.selectbox(ui["subject_label"], SUBJECTS, index=0, key="subject_selector")

    st.markdown("---")
    st.markdown("**🔌 Model:** `gemma3n:e2b`")
    st.markdown("**💻 Mode:** 100% Offline")
    st.markdown("**📡 Internet:** Not required")

# ── Main content area ─────────────────────────────────────────────────────────
col_lang, col_grade = st.columns(2)
with col_lang:
    st.info(f"🌐 {lang}", icon=None)
with col_grade:
    st.info(f"🎓 {selected_grade if 'selected_grade' in dir() else 'Grade 10'}", icon=None)

question = st.text_area(
    ui["question_label"],
    placeholder=ui["question_placeholder"],
    height=120,
    key="question_input",
)

col_ask, col_simplify = st.columns([2, 1])

with col_ask:
    ask_clicked = st.button(ui["ask_button"], use_container_width=True, type="primary")

with col_simplify:
    simplify_clicked = st.button(
        ui["simplify_button"],
        use_container_width=True,
        disabled=(st.session_state.last_answer == ""),
        key="simplify_btn",
    )

# ── Ask Guruji ────────────────────────────────────────────────────────────────
if ask_clicked:
    if not question.strip():
        st.warning(ui["no_question"])
    else:
        st.session_state.last_question = question.strip()
        try:
            with st.spinner(ui["thinking"]):
                answer_placeholder = st.empty()
                full_answer = ""

                # Streaming output
                for chunk in engine.stream_explain(
                    question=question.strip(),
                    language=lang,
                    grade_level=selected_grade if "selected_grade" in dir() else "Grade 10",
                ):
                    full_answer += chunk
                    answer_placeholder.markdown(
                        f'<div class="answer-card">{full_answer}▌</div>',
                        unsafe_allow_html=True,
                    )

                # Final render without cursor
                answer_placeholder.markdown(
                    f'<div class="answer-card">{full_answer}</div>',
                    unsafe_allow_html=True,
                )
                st.session_state.last_answer = full_answer

        except ConnectionError as e:
            st.error(ui["error_ollama"])
            st.code(str(e))
        except Exception as e:
            st.error(f"❌ Unexpected error: {e}")

# ── Simplify ──────────────────────────────────────────────────────────────────
if simplify_clicked and st.session_state.last_answer:
    try:
        with st.spinner(ui["thinking"]):
            simpler = engine.simplify(
                original_answer=st.session_state.last_answer,
                language=lang,
            )
            st.markdown("### 🔁 Simpler Explanation")
            st.markdown(
                f'<div class="answer-card">{simpler}</div>',
                unsafe_allow_html=True,
            )
            st.session_state.last_answer = simpler
    except ConnectionError:
        st.error(ui["error_ollama"])
    except Exception as e:
        st.error(f"❌ Error: {e}")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#666;font-size:0.8rem;'>"
    "PathShala Offline • Powered by Gemma 3n (local) • MIT License"
    "</p>",
    unsafe_allow_html=True,
)
