# ShikshaAI: Offline AI Tutor for Rural India

**Submission for the Gemma 3n Impact Challenge**

## The Problem
Over 250 million students in rural India face a stark reality: inconsistent internet access and a severe shortage of quality educators. A student studying late at night for their 10th-grade board exams often has no one to turn to when they stumble on a complex algebra or science concept. While AI has revolutionized education in urban centers, the digital divide leaves these students behind. They need an intelligent, patient, and multilingual tutor that doesn't rely on a cloud connection.

## The Solution
**ShikshaAI (PathShala Offline)** is an offline-first AI learning companion designed to bridge this divide. It places a powerful, empathetic tutor directly on low-cost devices, functioning 100% locally without an internet connection. 

Key features include:
1. **Multilingual Socratic Tutoring**: Native support for English, Hindi, and Marathi. Instead of just giving answers, ShikshaAI guides students step-by-step.
2. **Zero-Connectivity Architecture**: Powered entirely by a local instance of Gemma 3n.
3. **"Explain Simpler" Pedagogical Loop**: If a student is struggling, the system dynamically re-prompts the model to generate a simpler, real-world analogy grounded in rural Indian contexts.

## Architecture
ShikshaAI is engineered for production-grade reliability while remaining lightweight:
- **Model Layer**: We utilize the **Gemma 3n (E2B variant)** running via Ollama. It offers an incredible balance of low memory footprint and high reasoning capability, making it perfect for consumer hardware.
- **Backend Serving**: A FastAPI layer serves the LLM locally, exposing robust endpoints for chat, streaming, and session management. This decouple the UI from the heavy model logic.
- **Frontend**: A highly responsive, progressive UI built with Streamlit (and a vanilla HTML fallback), featuring progressively revealed markdown and active telemetry showing 0KB of data sent.

## Key Learnings & Future Roadmap
Building ShikshaAI highlighted the immense potential of Gemma 3n for edge deployment. 

**What we learned:**
- **Prompt Engineering for Low-Resource Languages**: Translating Socratic methods into Hindi and Marathi required careful prompt tuning to avoid awkward, literal translations. We implemented strict fallback guidelines.
- **Latency vs. Quality**: Streaming responses (Server-Sent Events) is critical for UX when running models locally on CPU-constrained devices.

**What's Next:**
We are currently evolving the architecture into a full MLOps pipeline. Phase 2 involves hybrid Retrieval-Augmented Generation (RAG) over NCERT (Indian Curriculum) PDFs using Qdrant, ensuring all answers are strictly grounded in the official syllabus. We will also implement MLflow for experiment tracking and GitHub Actions for automated evaluation gates to continuously improve the response quality.

ShikshaAI isn't just a hackathon project; it's a blueprint for democratizing education across the Global South.
