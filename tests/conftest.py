"""
Shared pytest fixtures used across the test suite.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    """
    An async HTTP client that talks directly to our FastAPI app in-memory,
    without needing a running server on a real port.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac