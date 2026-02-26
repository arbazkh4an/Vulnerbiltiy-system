"""
FastAPI dependencies for database and Redis connections
"""

from typing import AsyncGenerator
import redis.asyncio as redis
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from database.db import get_pool, init_db_pool, close_db_pool
from config import settings


_redis_client: redis.Redis = None


async def init_redis() -> redis.Redis:
    """Initialize Redis client."""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis_client


async def close_redis() -> None:
    """Close Redis client."""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None


async def get_db():
    """
    FastAPI dependency that yields a database connection from the pool.
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        yield conn


async def get_redis() -> redis.Redis:
    """
    FastAPI dependency that yields a Redis client.
    """
    return await init_redis()
