import time
import asyncio
import json
from backend.app.tutor_engine import TutorEngine
from backend.api.models.schemas import ChatResponse
from backend.api.services.retriever import HybridRetriever

engine = TutorEngine()
retriever = HybridRetriever()

def get_context(question: str) -> str:
    results = retriever.retrieve(question, top_k=3)
    if not results:
        return ""
    
    context_str = ""
    for idx, hit in enumerate(results):
        meta = hit['metadata']
        textbook = meta.get('textbook', 'Unknown')
        page = meta.get('page', 'Unknown')
        context_str += f"[Source {idx+1}: {textbook}, Page {page}]\n{hit['text']}\n\n"
    return context_str

async def generate_chat_response(question: str, language: str, grade_level: str) -> ChatResponse:
    start_time = time.time()
    
    # RAG Retrieval
    results = retriever.retrieve(question, top_k=3)
    
    context_str = ""
    sources = []
    for idx, hit in enumerate(results):
        meta = hit['metadata']
        textbook = meta.get('textbook', 'Unknown')
        page = str(meta.get('page', 'Unknown'))
        chapter = meta.get('chapter', 'Unknown')
        context_str += f"[Source {idx+1}: {textbook}, Page {page}]\n{hit['text']}\n\n"
        sources.append({
            "textbook": textbook,
            "chapter": chapter,
            "page": page,
            "excerpt": hit['text'][:200] + "..."
        })
        
    try:
        answer = await asyncio.to_thread(engine.explain, question, language, grade_level, context_str)
    except Exception as e:
        answer = f"Error generating response: {str(e)}"

    end_time = time.time()
    response_time_ms = (end_time - start_time) * 1000

    tokens_used = len(answer.split()) * 1.3

    return ChatResponse(
        answer=answer,
        language=language,
        tokens_used=int(tokens_used),
        response_time_ms=response_time_ms,
        sources=sources
    )

async def stream_chat_response(question: str, language: str, grade_level: str):
    # RAG Retrieval
    results = retriever.retrieve(question, top_k=3)
    
    context_str = ""
    sources_text = "\n\n**Sources:**\n"
    has_sources = False
    
    for idx, hit in enumerate(results):
        has_sources = True
        meta = hit['metadata']
        textbook = meta.get('textbook', 'Unknown')
        page = str(meta.get('page', 'Unknown'))
        context_str += f"[Source {idx+1}: {textbook}, Page {page}]\n{hit['text']}\n\n"
        sources_text += f"- *From: {textbook}, Page {page}*\n"
        
    def generator():
        try:
            for chunk in engine.stream_explain(question, language, grade_level, context_str):
                yield chunk
            if has_sources:
                yield sources_text
        except Exception as e:
            yield f"\n\n[Error generating response: {str(e)}]"
            
    for chunk in generator():
        yield chunk
        await asyncio.sleep(0.01)
