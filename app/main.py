"""
main.py — PathShala Offline: Streamlit frontend  (Phase 2)

Phase 2 additions over Phase 1:
  - Live streaming output with real-time markdown rendering
  - "Explain simpler" button calls simplify()
  - Quality badge shows QC result after each answer
  - Session history in sidebar (in-memory, Phase 3 adds SQLite)
  - Language-purity indicator
"""

import streamlit as st
from app.tutor_engine import TutorEngine
from app.language import SUPPORTED_LANGUAGES, SUBJECTS, GRADE_LEVELS, get_ui

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PathShala Offline — AI Tutor",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;600;700&family=Noto+Sans+Devanagari:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Noto Sans', 'Noto Sans Devanagari', sans-serif;
    }

    /* ── Header banner ── */
    .ps-header {
        background: linear-gradient(135deg, #0d2137 0%, #1a3a5c 50%, #0d2137 100%);
        border-radius: 16px;
        padding: 1.8rem 2.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid #2563eb;
        box-shadow: 0 8px 32px rgba(37,99,235,0.25);
    }
    .ps-header h1 {
        color: #e0f2fe;
        font-size: 1.9rem;
        font-weight: 700;
        margin: 0 0 0.25rem 0;
    }
    .ps-header p {
        color: #93c5fd;
        font-size: 0.95rem;
        margin: 0;
    }

    /* ── Answer card ── */
    .answer-card {
        background: #0f172a;
        border: 1px solid #1e3a5f;
        border-left: 4px solid #2563eb;
        border-radius: 12px;
        padding: 1.4rem 1.6rem;
        margin-top: 1rem;
        line-height: 1.75;
        font-size: 1.02rem;
        box-shadow: 0 4px 24px rgba(0,0,0,0.5);
    }

    /* ── Quality badge ── */
    .badge-pass {
        background: #052e16;
        color: #4ade80;
        border: 1px solid #4ade80;
        border-radius: 20px;
        padding: 3px 12px;
        font-size: 0.78rem;
        font-weight: 600;
        display: inline-block;
        margin-right: 6px;
    }
    .badge-fail {
        background: #3b0764;
        color: #e879f9;
        border: 1px solid #e879f9;
        border-radius: 20px;
        padding: 3px 12px;
        font-size: 0.78rem;
        font-weight: 600;
        display: inline-block;
        margin-right: 6px;
    }
    .badge-offline {
        background: #052e16;
        color: #4ade80;
        border: 1px solid #4ade80;
        border-radius: 20px;
        padding: 3px 12px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .badge-online {
        background: #450a0a;
        color: #f87171;
        border: 1px solid #f87171;
        border-radius: 20px;
        padding: 3px 12px;
        font-size: 0.78rem;
        font-weight: 600;
    }

    /* ── Buttons ── */
    div.stButton > button {
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.2s ease;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 14px rgba(37,99,235,0.4);
    }

    /* ── History item ── */
    .history-item {
        background: #1e293b;
        border-radius: 8px;
        padding: 0.5rem 0.75rem;
        margin-bottom: 0.4rem;
        font-size: 0.82rem;
        color: #94a3b8;
        border-left: 3px solid #334155;
        cursor: pointer;
    }
    .history-item:hover {
        border-left-color: #2563eb;
        color: #e2e8f0;
    }

    /* ── Streamlit sidebar background ── */
    [data-testid="stSidebar"] {
        background: #0f172a;
    }

    /* ── Metrics ── */
    [data-testid="metric-container"] {
        background: #1e293b;
        border-radius: 8px;
        padding: 0.6rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Session state init ────────────────────────────────────────────────────────
defaults = {
    "language": "English",
    "last_answer": "",
    "last_question": "",
    "last_qc": None,
    "session_history": [],   # list of {"q": str, "a": str, "lang": str}
    "attempt_count": 0,
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ── Engine (cached across reruns) ─────────────────────────────────────────────
@st.cache_resource
def get_engine():
    return TutorEngine()

engine = get_engine()

# ── UI strings ────────────────────────────────────────────────────────────────
lang = st.session_state.language
ui = get_ui(lang)

# ── Sidebar ───────────────────────────────────────────────────────────────────
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

    selected_grade = st.selectbox(ui["grade_label"], GRADE_LEVELS, index=1)
    selected_subject = st.selectbox(ui["subject_label"], SUBJECTS, index=0)

    # Connection status
    st.markdown("---")
    ollama_ok = engine._is_ollama_running()
    if ollama_ok:
        st.markdown(
            '<span class="badge-offline">🟢 Gemma Online</span>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<span class="badge-online">🔴 Ollama Offline</span>',
            unsafe_allow_html=True,
        )
        st.caption("Run `ollama serve` to start")

    st.markdown("**🤖 Model:** `gemma3n:e2b`")
    st.markdown("**💻 Mode:** 100% Offline")

    # Session history
    st.markdown("---")
    st.markdown(f"### {ui.get('history_tab', '📚 History')}")
    if not st.session_state.session_history:
        st.caption("No questions yet this session.")
    else:
        for i, item in enumerate(reversed(st.session_state.session_history[-8:])):
            trunc_q = item["q"][:55] + "…" if len(item["q"]) > 55 else item["q"]
            st.markdown(
                f'<div class="history-item">#{len(st.session_state.session_history)-i} '
                f'[{item["lang"]}] {trunc_q}</div>',
                unsafe_allow_html=True,
            )

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

# ── Controls row ──────────────────────────────────────────────────────────────
c1, c2 = st.columns(2)
c1.info(f"🌐 **{lang}** &nbsp;|&nbsp; 🎓 **{selected_grade}**")
c2.info(f"📖 **{selected_subject}**")

# ── Question input ────────────────────────────────────────────────────────────
question = st.text_area(
    ui["question_label"],
    placeholder=ui["question_placeholder"],
    height=110,
    key="question_input",
)

col_ask, col_simplify = st.columns([3, 2])
ask_clicked = col_ask.button(
    ui["ask_button"], use_container_width=True, type="primary"
)
simplify_clicked = col_simplify.button(
    ui["simplify_button"],
    use_container_width=True,
    disabled=(st.session_state.last_answer == ""),
    key="simplify_btn",
)

# ── ASK GURUJI ───────────────────────────────────────────────────────────────
if ask_clicked:
    if not question.strip():
        st.warning(ui["no_question"])
    else:
        st.session_state.last_question = question.strip()
        try:
            full_answer = ""
            answer_placeholder = st.empty()

            with st.spinner(ui["thinking"]):
                for chunk in engine.stream_explain(
                    question=question.strip(),
                    language=lang,
                    grade_level=selected_grade,
                ):
                    full_answer += chunk
                    # Render markdown live with streaming cursor
                    answer_placeholder.markdown(
                        f'<div class="answer-card">\n\n{full_answer}▌\n\n</div>',
                        unsafe_allow_html=True,
                    )

            # Final render — no cursor
            answer_placeholder.markdown(
                f'<div class="answer-card">\n\n{full_answer}\n\n</div>',
                unsafe_allow_html=True,
            )

            # Save to session state
            st.session_state.last_answer = full_answer
            st.session_state.session_history.append(
                {"q": question.strip(), "a": full_answer, "lang": lang}
            )

            # Quality check badge
            qc = engine.quality_check(full_answer, lang)
            st.session_state.last_qc = qc
            if qc["passed"]:
                st.markdown(
                    f'<span class="badge-pass">✅ Quality OK</span> '
                    f'<span style="color:#64748b;font-size:0.8rem">{qc["word_count"]} words</span>',
                    unsafe_allow_html=True,
                )
            else:
                issues = " | ".join(qc["flags"])
                st.markdown(
                    f'<span class="badge-fail">⚠️ QC Flag</span> '
                    f'<span style="color:#94a3b8;font-size:0.78rem">{issues}</span>',
                    unsafe_allow_html=True,
                )

        except ConnectionError:
            st.error(ui["error_ollama"])
            st.code("ollama serve", language="bash")
        except Exception as e:
            st.error(f"❌ Unexpected error: {e}")

# ── SIMPLIFY ─────────────────────────────────────────────────────────────────
if simplify_clicked and st.session_state.last_answer:
    try:
        with st.spinner(ui["thinking"]):
            simpler = engine.simplify(
                original_answer=st.session_state.last_answer,
                language=lang,
            )
        st.markdown("### 🔁 Simpler Explanation")
        st.markdown(
            f'<div class="answer-card">\n\n{simpler}\n\n</div>',
            unsafe_allow_html=True,
        )
        st.session_state.last_answer = simpler

        # QC the simplified answer
        qc = engine.quality_check(simpler, lang)
        if qc["passed"]:
            st.markdown(
                f'<span class="badge-pass">✅ Quality OK</span> '
                f'<span style="color:#64748b;font-size:0.8rem">{qc["word_count"]} words</span>',
                unsafe_allow_html=True,
            )

    except ConnectionError:
        st.error(ui["error_ollama"])
    except Exception as e:
        st.error(f"❌ Error: {e}")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#475569;font-size:0.78rem;'>"
    "PathShala Offline &nbsp;•&nbsp; Gemma 3n (local) &nbsp;•&nbsp; "
    "100% offline after model download &nbsp;•&nbsp; MIT License"
    "</p>",
    unsafe_allow_html=True,
)
