from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime

class ChatRequest(BaseModel):
    question: str = Field(..., description="The user's question to the AI tutor", min_length=1, example="Explain photosynthesis")
    language: str = Field(..., description="Language for the response", example="English")
    session_id: str = Field(..., description="Unique identifier for the chat session", example="sess_12345")
    grade_level: str = Field("Grade 10", description="The student's grade level", example="Grade 10")

    @validator("question")
    def question_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("Question cannot be empty or only whitespace")
        return v

    @validator("language")
    def validate_language(cls, v):
        allowed = ["English", "Hindi", "Marathi"]
        if v not in allowed:
            raise ValueError(f"Language must be one of {allowed}")
        return v

    class Config:
        schema_extra = {
            "example": {
                "question": "What is photosynthesis?",
                "language": "English",
                "session_id": "sess_001",
                "grade_level": "Grade 10"
            }
        }

class Citation(BaseModel):
    textbook: str
    chapter: str
    page: str
    excerpt: str

class ChatResponse(BaseModel):
    answer: str = Field(..., description="The generated response from the tutor")
    language: str = Field(..., description="Language of the response")
    tokens_used: int = Field(0, description="Estimated number of tokens generated")
    response_time_ms: float = Field(..., description="Time taken to generate the response in milliseconds")
    sources: List[Citation] = Field(default_factory=list, description="List of NCERT sources used")

class HistoryMessage(BaseModel):
    role: str
    content: str
    timestamp: datetime

class ChatHistoryResponse(BaseModel):
    session_id: str
    history: List[HistoryMessage]
