from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from backend.api.models.schemas import ChatRequest, ChatResponse, ChatHistoryResponse
from backend.api.services.llm_service import generate_chat_response, stream_chat_response
from backend.api.auth.dependencies import verify_credentials, limiter
from backend.api.db.database import save_chat_message, get_chat_history

router = APIRouter(tags=["Chat API"], dependencies=[Depends(verify_credentials)])

@router.post(
    "/chat", 
    response_model=ChatResponse,
    summary="Generate a chat response",
    description="Accepts a user question and returns a generated answer synchronously."
)
@limiter.limit("10/minute")
async def chat_endpoint(request: Request, chat_request: ChatRequest):
    # Save user message to history
    save_chat_message(chat_request.session_id, "user", chat_request.question)
    
    # Generate response
    response = await generate_chat_response(
        question=chat_request.question,
        language=chat_request.language,
        grade_level=chat_request.grade_level
    )
    
    # Save assistant message to history
    save_chat_message(chat_request.session_id, "assistant", response.answer)
    
    return response

@router.post(
    "/chat/stream",
    summary="Generate a streaming chat response",
    description="Returns streaming responses using Server-Sent Events (SSE).",
    response_class=StreamingResponse
)
@limiter.limit("10/minute")
async def chat_stream_endpoint(request: Request, chat_request: ChatRequest):
    # Save user message to history
    save_chat_message(chat_request.session_id, "user", chat_request.question)
    
    async def sse_generator():
        full_answer = []
        async for chunk in stream_chat_response(
            question=chat_request.question,
            language=chat_request.language,
            grade_level=chat_request.grade_level
        ):
            full_answer.append(chunk)
            # SSE format
            yield f"data: {chunk}\n\n"
        
        # Save complete assistant message to history
        save_chat_message(chat_request.session_id, "assistant", "".join(full_answer))
        
    return StreamingResponse(sse_generator(), media_type="text/event-stream")

@router.get(
    "/session/{session_id}/history",
    response_model=ChatHistoryResponse,
    summary="Get chat history for a session",
    description="Retrieves the full chronological chat history for a given session ID."
)
async def get_history(session_id: str):
    history = get_chat_history(session_id)
    return ChatHistoryResponse(
        session_id=session_id,
        history=history
    )
