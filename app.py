import streamlit as st
from huggingface_hub import InferenceClient

st.set_page_config(page_title="PathShala Offline AI Tutor", page_icon="📚")

st.title("📚 PathShala AI Tutor")
st.markdown("**Offline AI tutor for rural Indian students · Hindi/Marathi/English**")
st.markdown("*Note: This HuggingFace Space uses the Inference API instead of local Ollama for demonstration.*")

client = InferenceClient("mistralai/Mistral-7B-Instruct-v0.2")

st.sidebar.header("Settings")
language = st.sidebar.selectbox("Language", ["English", "Hindi", "Marathi"])
grade = st.sidebar.selectbox("Grade Level", ["Grade 9", "Grade 10"])

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

def get_stream(messages):
    stream = client.chat_completion(
        messages,
        max_tokens=800,
        stream=True,
        temperature=0.3
    )
    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

if prompt := st.chat_input("Ask a question (e.g., Explain photosynthesis)"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        system_prompt = f"You are a helpful AI tutor for a {grade} student in India. Explain concepts simply and patiently. Respond in {language}."
        
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend([{"role": m["role"], "content": m["content"]} for m in st.session_state.messages])

        try:
            response = st.write_stream(get_stream(messages))
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"Error connecting to HuggingFace API: {e}")

if len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "assistant":
    if st.button("Explain simpler"):
        with st.chat_message("assistant"):
            simplify_prompt = f"The student didn't understand. Explain it using an EVEN SIMPLER real-world analogy in {language}."
            
            system_prompt = f"You are a helpful AI tutor for a {grade} student in India. Explain concepts simply and patiently. Respond in {language}."
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend([{"role": m["role"], "content": m["content"]} for m in st.session_state.messages])
            messages.append({"role": "user", "content": simplify_prompt})
            
            try:
                response = st.write_stream(get_stream(messages))
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Error connecting to HuggingFace API: {e}")
