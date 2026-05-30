import streamlit as st
import requests
import json
import uuid
import os

st.set_page_config(page_title="PathShala Offline AI Tutor", page_icon="📚")

st.title("📚 PathShala AI Tutor")
st.markdown("**Offline AI tutor for rural Indian students · Hindi/Marathi/English**")

# Backend API configuration
API_URL = os.getenv("API_URL", "http://localhost:8000/api")
API_USER = os.getenv("API_USER", "admin")
API_PASSWORD = os.getenv("API_PASSWORD", "secret")
AUTH = (API_USER, API_PASSWORD)

# Generate a unique session ID if not exists
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

st.sidebar.header("Settings")
language = st.sidebar.selectbox("Language", ["English", "Hindi", "Marathi"])
grade = st.sidebar.selectbox("Grade Level", ["Grade 9", "Grade 10"])

# Load chat history from backend on startup or when needed, though for now we can rely on session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Optionally load from backend:
    try:
        resp = requests.get(f"{API_URL}/session/{st.session_state.session_id}/history", auth=AUTH)
        if resp.status_code == 200:
            history = resp.json().get("history", [])
            for msg in history:
                st.session_state.messages.append({"role": msg["role"], "content": msg["content"]})
    except Exception:
        pass

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

def get_stream_from_backend(question, lang, grade_level):
    req_body = {
        "question": question,
        "language": lang,
        "grade_level": grade_level,
        "session_id": st.session_state.session_id
    }
    
    with requests.post(f"{API_URL}/chat/stream", json=req_body, auth=AUTH, stream=True) as response:
        if response.status_code == 401:
            yield "Authentication failed with the backend API."
            return
        elif response.status_code == 429:
            yield "Rate limit exceeded. Please try again later."
            return
        
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith("data: "):
                    yield decoded_line[6:]

if prompt := st.chat_input("Ask a question (e.g., Explain photosynthesis)"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            stream = get_stream_from_backend(prompt, language, grade)
            response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"Error connecting to backend API: {e}")
