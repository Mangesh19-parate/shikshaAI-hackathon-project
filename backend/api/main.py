from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import chat
from backend.api.middleware.logging import RequestLoggingMiddleware
from backend.api.auth.dependencies import limiter
from backend.api.db.database import init_db

app = FastAPI(
    title="ShikshaAI Backend",
    description="Production-ready FastAPI backend for PathShala Offline AI Tutor",
    version="1.0.0",
    contact={
        "name": "Backend Team",
        "email": "engineering@shiksha.ai",
    }
)

# Set up Rate Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add Middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)

# Initialize Database on startup
@app.on_event("startup")
def startup_event():
    init_db()

# Include Routers
app.include_router(chat.router, prefix="/api")

@app.get("/health", tags=["System"])
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
