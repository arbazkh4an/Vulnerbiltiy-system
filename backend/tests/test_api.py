"""
SentinelAI — API Integration Tests
Tests for the FastAPI endpoints.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.asyncio
async def test_health_endpoint():
    """Health endpoint should return 200 even without DB."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "SentinelAI API"
    assert data["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_scan_requires_auth():
    """POST /api/scan without auth should return 401."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/scan",
            json={"url": "https://example.com", "consent": True},
        )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_history_requires_auth():
    """GET /api/history without auth should return 401."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/history")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_scan_detail_requires_auth():
    """GET /api/scan/{id} without auth should return 401."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/scan/some-id")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_scan_invalid_url():
    """POST /api/scan with invalid URL should return 422."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/scan",
            json={"url": "not-a-url", "consent": True},
            headers={"Authorization": "Bearer test-user-123"},
        )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_scan_no_consent():
    """POST /api/scan without consent should return 422."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/scan",
            json={"url": "https://example.com", "consent": False},
            headers={"Authorization": "Bearer test-user-123"},
        )
    assert response.status_code == 422
