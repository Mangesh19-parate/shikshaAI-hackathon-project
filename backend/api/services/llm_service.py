import time
import asyncio
from backend.app.tutor_engine import TutorEngine
from backend.api.models.schemas import ChatResponse

engine = TutorEngine()

async def generate_chat_response(question: str, language: str, grade_level: str) -> ChatResponse:
    start_time = time.time()
    
    # We use asyncio.to_thread since the current TutorEngine explain is synchronous
    # and blocking might freeze the FastAPI event loop.
    try:
        answer = await asyncio.to_thread(engine.explain, question, language, grade_level)
    except Exception as e:
        answer = f"Error generating response: {str(e)}"

    end_time = time.time()
    response_time_ms = (end_time - start_time) * 1000

    # Rough estimate of tokens used based on word count
    tokens_used = len(answer.split()) * 1.3

    return ChatResponse(
        answer=answer,
        language=language,
        tokens_used=int(tokens_used),
        response_time_ms=response_time_ms
    )

async def stream_chat_response(question: str, language: str, grade_level: str):
    # stream_explain is a sync generator, we can adapt it to async generator
    def generator():
        try:
            for chunk in engine.stream_explain(question, language, grade_level):
                yield chunk
        except Exception as e:
            yield f"\n\n[Error generating response: {str(e)}]"
            
    # Convert sync generator to async
    for chunk in generator():
        yield chunk
        await asyncio.sleep(0.01) # Small sleep to yield to event loop
