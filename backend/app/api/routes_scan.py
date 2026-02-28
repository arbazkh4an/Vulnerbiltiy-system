"""
SentinelAI — Scan API Routes
POST /api/scan — create a new scan
GET  /api/scan/{scan_id} — get scan status and results
"""

from fastapi import APIRouter, Depends, Request

from app.core.exceptions import ScanNotFound
from app.core.rate_limit import check_rate_limit
from app.core.security import get_current_user
from app.core.validators import validate_scan_url
from app.db.repositories import create_scan, get_scan_by_id, store_consent
from app.db.session import get_pool
from app.logging import get_logger
from app.models.scan_models import ScanCreate, ScanDetailResponse, ScanResponse, ScanStatus

logger = get_logger(__name__)

router = APIRouter()


@router.post("/scan", response_model=ScanResponse)
async def start_scan(
    body: ScanCreate,
    request: Request,
    user_id: str = Depends(get_current_user),
) -> ScanResponse:
    """
    Submit a new URL for vulnerability scanning.

    Flow:
    1. Validate URL (format + SSRF blocking)
    2. Check rate limit
    3. Log consent
    4. Insert scan record as 'queued'
    5. Return scan_id immediately (worker handles async processing)
    """
    pool = get_pool()

    # Validate URL and block SSRF
    validated_url = validate_scan_url(body.url)

    # Check rate limit
    await check_rate_limit(pool, user_id)

    # Log consent
    client_ip = request.client.host if request.client else "unknown"
    await store_consent(pool, user_id, validated_url, client_ip)

    # Create scan record
    scan_id = await create_scan(pool, user_id, validated_url)

    logger.info("scan_queued", scan_id=scan_id, user_id=user_id, url=validated_url)

    return ScanResponse(scan_id=scan_id, status=ScanStatus.QUEUED)


@router.get("/scan/{scan_id}", response_model=ScanDetailResponse)
async def get_scan(
    scan_id: str,
    user_id: str = Depends(get_current_user),
) -> ScanDetailResponse:
    """
    Get the current status and results of a scan.

    Returns progress during execution, and the full report when complete.
    """
    pool = get_pool()

    scan = await get_scan_by_id(pool, scan_id, user_id)
    if scan is None:
        raise ScanNotFound()

    return ScanDetailResponse(**scan)
