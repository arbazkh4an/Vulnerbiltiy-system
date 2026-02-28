"""
SentinelAI — Database Repositories
All database operations for scans, results, and consent.
"""

import json
from typing import Any, Optional
from uuid import UUID

from asyncpg import Pool

from app.logging import get_logger

logger = get_logger(__name__)


# ─── Scan CRUD ────────────────────────────────────────────────────────────────


async def create_scan(pool: Pool, user_id: str, url: str) -> str:
    """Insert a new scan record with status 'queued'. Returns the scan UUID."""
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO scans (user_id, target_url, scan_status)
            VALUES ($1, $2, 'queued')
            RETURNING id
            """,
            user_id,
            url,
        )
    scan_id = str(row["id"])
    logger.info("scan_created", scan_id=scan_id, user_id=user_id, url=url)
    return scan_id


async def update_status(
    pool: Pool,
    scan_id: str,
    status: str,
    progress: int = 0,
    error_message: Optional[str] = None,
) -> None:
    """Update the scan status and progress."""
    async with pool.acquire() as conn:
        if status in ("complete", "failed"):
            await conn.execute(
                """
                UPDATE scans
                SET scan_status = $2,
                    progress = $3,
                    error_message = $4,
                    completed_at = NOW()
                WHERE id = $1
                """,
                scan_id,
                status,
                progress,
                error_message,
            )
        else:
            await conn.execute(
                """
                UPDATE scans
                SET scan_status = $2,
                    progress = $3,
                    error_message = $4,
                    started_at = COALESCE(started_at, NOW())
                WHERE id = $1
                """,
                scan_id,
                status,
                progress,
                error_message,
            )


async def get_queued_scan(pool: Pool) -> Optional[dict[str, Any]]:
    """
    Fetch the oldest queued scan using FOR UPDATE SKIP LOCKED
    for safe concurrent worker access.
    """
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT id, user_id, target_url
            FROM scans
            WHERE scan_status = 'queued'
            ORDER BY created_at ASC
            LIMIT 1
            FOR UPDATE SKIP LOCKED
            """
        )
    if row is None:
        return None
    return {
        "id": str(row["id"]),
        "user_id": str(row["user_id"]),
        "target_url": row["target_url"],
    }


async def store_raw_results(pool: Pool, scan_id: str, results: dict) -> None:
    """Insert or update raw scanner results in scan_results."""
    results_json = json.dumps(results)
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO scan_results (scan_id, raw_json)
            VALUES ($1, $2::jsonb)
            ON CONFLICT (scan_id) DO UPDATE
            SET raw_json = $2::jsonb
            """,
            scan_id,
            results_json,
        )


async def store_ai_report(pool: Pool, scan_id: str, report: dict) -> None:
    """Store the AI-generated report in scan_results."""
    report_json = json.dumps(report)
    async with pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE scan_results
            SET ai_report = $2::jsonb
            WHERE scan_id = $1
            """,
            scan_id,
            report_json,
        )


async def get_scan_by_id(pool: Pool, scan_id: str, user_id: str) -> Optional[dict[str, Any]]:
    """Fetch a scan with ownership check, including results if available."""
    async with pool.acquire() as conn:
        scan_row = await conn.fetchrow(
            """
            SELECT s.id, s.target_url, s.scan_status, s.progress,
                   s.created_at, s.completed_at, s.error_message,
                   s.total_vulnerabilities, s.critical_count,
                   s.high_count, s.medium_count, s.low_count,
                   sr.raw_json, sr.ai_report
            FROM scans s
            LEFT JOIN scan_results sr ON sr.scan_id = s.id
            WHERE s.id = $1 AND s.user_id = $2
            """,
            scan_id,
            user_id,
        )

    if scan_row is None:
        return None

    return {
        "id": str(scan_row["id"]),
        "url": scan_row["target_url"],
        "status": scan_row["scan_status"],
        "progress": scan_row["progress"] or 0,
        "created_at": scan_row["created_at"].isoformat() if scan_row["created_at"] else None,
        "completed_at": scan_row["completed_at"].isoformat() if scan_row["completed_at"] else None,
        "error_message": scan_row["error_message"],
        "total_vulnerabilities": scan_row["total_vulnerabilities"] or 0,
        "critical_count": scan_row["critical_count"] or 0,
        "high_count": scan_row["high_count"] or 0,
        "medium_count": scan_row["medium_count"] or 0,
        "low_count": scan_row["low_count"] or 0,
        "raw_results": json.loads(scan_row["raw_json"]) if scan_row["raw_json"] else None,
        "ai_report": json.loads(scan_row["ai_report"]) if scan_row["ai_report"] else None,
    }


async def get_user_history(
    pool: Pool, user_id: str, limit: int = 50, offset: int = 0
) -> tuple[list[dict[str, Any]], int]:
    """Fetch paginated scan history for a user. Returns (items, total_count)."""
    async with pool.acquire() as conn:
        total = await conn.fetchval(
            "SELECT COUNT(*) FROM scans WHERE user_id = $1",
            user_id,
        )
        rows = await conn.fetch(
            """
            SELECT id, target_url, scan_status, created_at, completed_at,
                   total_vulnerabilities, critical_count, high_count, medium_count, low_count
            FROM scans
            WHERE user_id = $1
            ORDER BY created_at DESC
            LIMIT $2 OFFSET $3
            """,
            user_id,
            limit,
            offset,
        )

    items = [
        {
            "id": str(row["id"]),
            "url": row["target_url"],
            "status": row["scan_status"],
            "created_at": row["created_at"].isoformat() if row["created_at"] else None,
            "completed_at": row["completed_at"].isoformat() if row["completed_at"] else None,
            "total_vulnerabilities": row["total_vulnerabilities"] or 0,
            "critical_count": row["critical_count"] or 0,
            "high_count": row["high_count"] or 0,
            "medium_count": row["medium_count"] or 0,
            "low_count": row["low_count"] or 0,
        }
        for row in rows
    ]
    return items, total


async def store_consent(pool: Pool, user_id: str, url: str, ip_address: str) -> None:
    """Log scan consent for compliance."""
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO consent_logs (user_id, url, ip_address)
            VALUES ($1, $2, $3)
            """,
            user_id,
            url,
            ip_address,
        )


async def mark_scan_failed(pool: Pool, scan_id: str, error_message: str) -> None:
    """Mark a scan as failed with an error message."""
    await update_status(pool, scan_id, "failed", progress=0, error_message=error_message)
    logger.error("scan_marked_failed", scan_id=scan_id, error=error_message)


async def update_scan_counts(
    pool: Pool,
    scan_id: str,
    total: int,
    critical: int,
    high: int,
    medium: int,
    low: int,
) -> None:
    """Update vulnerability counts on the scan record."""
    async with pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE scans
            SET total_vulnerabilities = $2,
                critical_count = $3,
                high_count = $4,
                medium_count = $5,
                low_count = $6
            WHERE id = $1
            """,
            scan_id,
            total,
            critical,
            high,
            medium,
            low,
        )
