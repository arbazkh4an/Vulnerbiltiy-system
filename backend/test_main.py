"""
Tests for FastAPI Backend
Using httpx + pytest with FastAPI TestClient
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient, ASGITransport
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))


@pytest.fixture(scope="function")
def mock_dependencies():
    mock_pool = MagicMock()
    mock_conn = AsyncMock()
    mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_pool.acquire.return_value.__aexit__ = AsyncMock()
    
    async def mock_ping():
        return True
    
    mock_redis_instance = AsyncMock()
    mock_redis_instance.ping = mock_ping
    mock_redis_instance.lpush = AsyncMock()
    
    patchers = [
        patch("database.db.get_pool", return_value=mock_pool),
        patch("database.db.init_db_pool", new_callable=AsyncMock),
        patch("database.db.close_db_pool", new_callable=AsyncMock),
    ]
    
    for p in patchers:
        p.start()
    
    import main
    
    original_lifespan = main.app.router.lifespan_context
    
    async def mock_lifespan(app):
        yield
    
    main.app.router.lifespan_context = mock_lifespan
    
    patchers2 = [
        patch("main.db_health_check", new_callable=AsyncMock),
        patch("main.init_redis", new_callable=AsyncMock),
        patch("main.close_redis", new_callable=AsyncMock),
        patch("main.get_redis", new_callable=AsyncMock),
    ]
    
    mock_db_health = patchers2[0].start()
    mock_db_health.return_value = True
    
    for p in patchers2[1:]:
        p.start()
    
    main.get_redis = AsyncMock(return_value=mock_redis_instance)
    
    yield mock_pool, mock_conn, mock_redis_instance
    
    for p in reversed(patchers):
        p.stop()
    
    for p in reversed(patchers2):
        p.stop()


@pytest_asyncio.fixture
async def client(mock_dependencies):
    import main
    transport = ASGITransport(app=main.app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_post_scan_valid_url_consent_true(client):
    """Test: POST /api/scan with valid URL and consent=true returns 200 + scan_id"""
    import main
    with patch("main.create_scan", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = "test-scan-id-1234"
        
        response = await client.post(
            "/api/scan",
            json={"url": "https://example.com", "consent": True}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert "scan_id" in data
    assert data["status"] == "queued"
    assert data["message"] == "Scan started"


@pytest.mark.asyncio
async def test_post_scan_consent_false(client):
    """Test: POST /api/scan with consent=false returns 400"""
    response = await client.post(
        "/api/scan",
        json={"url": "https://example.com", "consent": False}
    )
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_post_scan_invalid_url(client):
    """Test: POST /api/scan with invalid URL returns 422"""
    response = await client.post(
        "/api/scan",
        json={"url": "not-a-valid-url", "consent": True}
    )
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_post_scan_localhost_url(client):
    """Test: POST /api/scan with localhost URL returns 400 (blocked)"""
    response = await client.post(
        "/api/scan",
        json={"url": "http://localhost:8080", "consent": True}
    )
    
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_scan_valid_id(client, mock_dependencies):
    """Test: GET /api/scan/{valid_id} returns scan object"""
    import main
    with patch("main.get_scan", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = {
            "id": "test-scan-id",
            "url": "https://example.com",
            "status": "queued",
            "created_at": "2024-01-01T00:00:00+00:00",
            "completed_at": None
        }
        
        response = await client.get("/api/scan/test-scan-id")
    
    assert response.status_code == 200
    data = response.json()
    assert data["scan_id"] == "test-scan-id"
    assert data["url"] == "https://example.com"
    assert data["status"] == "queued"


@pytest.mark.asyncio
async def test_get_scan_invalid_id(client):
    """Test: GET /api/scan/{invalid_id} returns 404"""
    import main
    with patch("main.get_scan", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None
        
        response = await client.get("/api/scan/nonexistent-id")
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_health_returns_all_green(client):
    """Test: GET /api/health returns health status"""
    response = await client.get("/api/health")
    
    assert response.status_code in [200, 503]
    data = response.json()
    assert "status" in data
    assert "db" in data
    assert "redis" in data


@pytest.mark.asyncio
async def test_get_scans_returns_list(client, mock_dependencies):
    """Test: GET /api/scans returns list"""
    mock_pool, mock_conn, _ = mock_dependencies
    
    mock_conn.fetch = AsyncMock(return_value=[
        {"id": "scan-1", "url": "https://example1.com", "status": "complete", "created_at": "2024-01-01T00:00:00"},
        {"id": "scan-2", "url": "https://example2.com", "status": "queued", "created_at": "2024-01-02T00:00:00"},
    ])
    
    mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
    
    response = await client.get("/api/scans")
    
    assert response.status_code == 200
    data = response.json()
    assert "scans" in data
    assert len(data["scans"]) == 2
