import pytest
import asyncio
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

async def test_health_check(async_client: AsyncClient):
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

async def test_chat_unauthorized(async_client: AsyncClient):
    response = await async_client.post(
        "/api/chat",
        json={"question": "Hello", "language": "English", "session_id": "123"}
    )
    assert response.status_code == 401

async def test_chat_valid_request(async_client: AsyncClient, auth_headers):
    response = await async_client.post(
        "/api/chat",
        headers=auth_headers,
        json={"question": "What is 2+2?", "language": "English", "session_id": "test_session_1"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert data["language"] == "English"
    assert "tokens_used" in data
    assert "response_time_ms" in data

async def test_chat_invalid_language(async_client: AsyncClient, auth_headers):
    response = await async_client.post(
        "/api/chat",
        headers=auth_headers,
        json={"question": "Hello", "language": "French", "session_id": "123"}
    )
    assert response.status_code == 422 # Pydantic validation error

async def test_chat_empty_question(async_client: AsyncClient, auth_headers):
    response = await async_client.post(
        "/api/chat",
        headers=auth_headers,
        json={"question": "   ", "language": "English", "session_id": "123"}
    )
    assert response.status_code == 422 # Pydantic validation error

async def test_session_persistence(async_client: AsyncClient, auth_headers):
    session_id = "persistence_test_session"
    
    # 1. Send chat message
    await async_client.post(
        "/api/chat",
        headers=auth_headers,
        json={"question": "First question", "language": "English", "session_id": session_id}
    )
    
    # 2. Get history
    response = await async_client.get(f"/api/session/{session_id}/history", headers=auth_headers)
    assert response.status_code == 200
    
    history = response.json().get("history", [])
    assert len(history) >= 2 # At least user message and assistant message
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "First question"
    assert history[1]["role"] == "assistant"

async def test_rate_limiting(async_client: AsyncClient, auth_headers):
    # Depending on how the rate limiter counts testing might be flaky if we share IPs,
    # but let's assume limit is 10/minute, we can send 11 quick requests.
    session_id = "rate_limit_test"
    
    # Make 11 requests
    responses = []
    for _ in range(11):
        resp = await async_client.post(
            "/api/chat",
            headers=auth_headers,
            json={"question": "Test", "language": "English", "session_id": session_id}
        )
        responses.append(resp.status_code)
    
    # At least one should be 429
    assert 429 in responses

async def test_streaming_endpoint(async_client: AsyncClient, auth_headers):
    session_id = "stream_test_session"
    
    async with async_client.stream(
        "POST", 
        "/api/chat/stream",
        headers=auth_headers,
        json={"question": "Write a short poem", "language": "English", "session_id": session_id}
    ) as response:
        assert response.status_code == 200
        
        chunks = []
        async for chunk in response.aiter_lines():
            if chunk.startswith("data: "):
                chunks.append(chunk[6:])
                
        assert len(chunks) > 0 # Should have received at least one chunk
