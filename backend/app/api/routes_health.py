"""
SentinelAI — Health Check Route
GET /api/health — system health status
"""

from fastapi import APIRouter

from app.db.session import get_pool
from app.logging import get_logger
from app.models.scan_models import HealthResponse

logger = get_logger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Check system health including database connectivity.
    No authentication required.
    """
    db_status = "disconnected"

    try:
        pool = get_pool()
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        db_status = "connected"
    except Exception as exc:
        logger.error("health_check_db_failed", error=str(exc))
        db_status = f"error: {str(exc)[:80]}"

    return HealthResponse(
        status="healthy" if db_status == "connected" else "degraded",
        service="SentinelAI API",
        version="1.0.0",
        db=db_status,
    )
