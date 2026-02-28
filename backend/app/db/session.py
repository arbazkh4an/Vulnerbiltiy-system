"""
SentinelAI — Async Database Session
asyncpg connection pool lifecycle management.
"""

from typing import Optional

import asyncpg
from asyncpg import Pool

from app.config import get_settings
from app.logging import get_logger

logger = get_logger(__name__)

_pool: Optional[Pool] = None


async def create_pool() -> Pool:
    """Create and cache the asyncpg connection pool."""
    global _pool
    if _pool is not None:
        return _pool

    settings = get_settings()
    logger.info("db_pool_creating", dsn=settings.DATABASE_URL[:30] + "...")

    _pool = await asyncpg.create_pool(
        dsn=settings.DATABASE_URL,
        min_size=2,
        max_size=10,
        command_timeout=60,
    )

    logger.info("db_pool_created")
    return _pool


async def close_pool() -> None:
    """Close the asyncpg connection pool."""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
        logger.info("db_pool_closed")


def get_pool() -> Pool:
    """
    Get the current pool instance.

    Must be called after create_pool().
    """
    if _pool is None:
        raise RuntimeError("Database pool not initialized. Call create_pool() first.")
    return _pool
