"""
SentinelAI — History API Route
GET /api/history — paginated scan history for the authenticated user
"""

from fastapi import APIRouter, Depends, Query

from app.core.security import get_current_user
from app.db.repositories import get_user_history
from app.db.session import get_pool
from app.models.scan_models import HistoryItem, HistoryResponse

router = APIRouter()


@router.get("/history", response_model=HistoryResponse)
async def scan_history(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user_id: str = Depends(get_current_user),
) -> HistoryResponse:
    """Return paginated scan history for the authenticated user."""
    pool = get_pool()

    items, total = await get_user_history(pool, user_id, limit=limit, offset=offset)

    return HistoryResponse(
        scans=[HistoryItem(**item) for item in items],
        total=total,
    )
