"""
Tests for the system health check endpoints.
"""

import pytest


@pytest.mark.asyncio
async def test_health_check_returns_ok(client):
    """The /health endpoint should always return a 200 with status 'ok'."""
    response = await client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "service" in body
    assert "debug_mode" in body