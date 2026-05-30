import pytest
from httpx import AsyncClient, ASGITransport
import os

# We set environment variables before importing the app
os.environ["API_USER"] = "testuser"
os.environ["API_PASSWORD"] = "testpass"

from backend.api.main import app
from backend.api.db.database import init_db

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    init_db()
    yield

@pytest.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

@pytest.fixture
def auth_headers():
    import base64
    credentials = f"testuser:testpass"
    encoded = base64.b64encode(credentials.encode()).decode()
    return {"Authorization": f"Basic {encoded}"}
