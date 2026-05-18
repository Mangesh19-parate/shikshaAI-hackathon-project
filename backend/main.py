import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.app.tutor_engine import TutorEngine

app = FastAPI(title="ShikshaAI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = TutorEngine()

class ChatRequest(BaseModel):
    question: str
    language: str = "English"
    grade_level: str = "Grade 10"

@app.post("/api/chat")
async def chat(request: ChatRequest):
    def generate():
        try:
            for chunk in engine.stream_explain(request.question, request.language, request.grade_level):
                yield chunk
        except Exception as e:
            yield f"\n\n[Error: {str(e)}]"
            
    return StreamingResponse(generate(), media_type="text/plain")

@app.post("/api/simplify")
async def simplify(request: dict):
    original_answer = request.get("original_answer")
    language = request.get("language", "English")
    try:
        simpler = engine.simplify(original_answer, language)
        return {"answer": simpler}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/")
async def serve_frontend():
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "index.html")
    with open(frontend_path, "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content=content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
