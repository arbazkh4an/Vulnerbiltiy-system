"""
SentinelAI — Database-backed Rate Limiting
Enforces scan rate limits per user using the scans table.
"""

from asyncpg import Pool

from app.config import Settings, get_settings
from app.core.exceptions import RateLimitExceeded
from app.logging import get_logger

logger = get_logger(__name__)


async def check_rate_limit(pool: Pool, user_id: str, settings: Settings | None = None) -> None:
    """
    Check if the user has exceeded the scan rate limit.

    Queries the scans table to count recent scans within the configured window.
    Raises RateLimitExceeded if the limit is hit.
    """
    if settings is None:
        settings = get_settings()

    async with pool.acquire() as conn:
        count = await conn.fetchval(
            """
            SELECT COUNT(*)
            FROM scans
            WHERE user_id = $1
              AND created_at > NOW() - ($2 || ' hours')::INTERVAL
            """,
            user_id,
            str(settings.RATE_LIMIT_WINDOW_HOURS),
        )

    if count >= settings.RATE_LIMIT_MAX:
        logger.warning(
            "rate_limit_exceeded",
            user_id=user_id,
            count=count,
            max=settings.RATE_LIMIT_MAX,
        )
        raise RateLimitExceeded(
            f"Maximum {settings.RATE_LIMIT_MAX} scans per {settings.RATE_LIMIT_WINDOW_HOURS} hour(s). "
            f"You have used {count}."
        )
