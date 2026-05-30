import time
import json
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from backend.api.db.database import log_request
import logging

logger = logging.getLogger("api_request_logger")

async def set_body(request: Request, body: bytes):
    async def receive():
        return {"type": "http.request", "body": body}
    request._receive = receive

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Default metrics
        endpoint = request.url.path
        language = "Unknown"
        question_length = 0
        session_id = "Unknown"
        
        # Read body to extract metrics without consuming stream permanently
        if request.method in ["POST", "PUT"] and request.url.path in ["/chat", "/chat/stream"]:
            try:
                body_bytes = await request.body()
                await set_body(request, body_bytes)
                if body_bytes:
                    body_json = json.loads(body_bytes)
                    language = body_json.get("language", "Unknown")
                    question = body_json.get("question", "")
                    question_length = len(question)
                    session_id = body_json.get("session_id", "Unknown")
            except Exception:
                pass

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            status_code = 500
            raise e
        finally:
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            
            log_request(
                endpoint=endpoint,
                language=language,
                response_time_ms=response_time_ms,
                question_length=question_length,
                status_code=status_code,
                session_id=session_id
            )
            
        return response
