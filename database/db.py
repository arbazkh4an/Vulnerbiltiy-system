"""
OWASP AI Scanner - Database Connection Layer
Async PostgreSQL database operations using asyncpg
"""

import json
import uuid
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

import asyncpg

# Database configuration
POSTGRES_URL = "postgresql://scanner:scanner@localhost:5432/scannerdb"

# Global connection pool
_pool: Optional[asyncpg.Pool] = None


async def init_db_pool() -> asyncpg.Pool:
    """
    Initialize the database connection pool.
    Should be called on application startup.
    
    Returns:
        asyncpg.Pool: The connection pool instance
    """
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            POSTGRES_URL,
            min_size=2,
            max_size=10,
            command_timeout=60,
        )
    return _pool

async def close_db_pool() -> None:
    """
    Close the database connection pool.
    Should be called on application shutdown.
    """
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


def get_pool() -> asyncpg.Pool:
    """
    Get the current database connection pool.
    
    Returns:
        asyncpg.Pool: The connection pool
        
    Raises:
        RuntimeError: If pool not initialized
    """
    if _pool is None:
        raise RuntimeError("Database pool not initialized. Call init_db_pool() first.")
    return _pool


@asynccontextmanager
async def get_connection():
    """
    Context manager for getting a database connection from the pool.
    
    Yields:
        asyncpg.Connection: A database connection
    """
    pool = get_pool()
    async with pool.acquire() as connection:
        yield connection

async def create_scan(url: str, user_ip: str, consent: bool) -> str:
    """
    Create a new scan record in the database.
    
    Args:
        url: The URL to scan
        user_ip: The IP address of the user
        consent: Whether user consent was confirmed
        
    Returns:
        str: The UUID of the created scan
    """
    scan_id = str(uuid.uuid4())
    
    async with get_connection() as conn:
        await conn.execute(
            """
            INSERT INTO scans (id, url, user_ip, consent_confirmed, status, created_at)
            VALUES ($1, $2, $3, $4, 'queued', NOW())
            """,
            scan_id,
            url,
            user_ip,
            consent,
        )
    
    return scan_id


async def update_scan_status(scan_id: str, status: str) -> None:
    """
    Update the status of a scan.
    
    Args:
        scan_id: The UUID of the scan
        status: The new status ('queued' | 'scanning' | 'analyzing' | 'complete' | 'error')
    """
    valid_statuses = ['queued', 'scanning', 'analyzing', 'complete', 'error']
    if status not in valid_statuses:
        raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")
    
    # If status is 'complete' or 'error', also set completed_at timestamp
    if status in ('complete', 'error'):
        async with get_connection() as conn:
            await conn.execute(
                """
                UPDATE scans 
                SET status = $1, completed_at = NOW() 
                WHERE id = $2
                """,
                status,
                scan_id,
            )
    else:
        async with get_connection() as conn:
            await conn.execute(
                """
                UPDATE scans 
                SET status = $1 
                WHERE id = $2
                """,
                status,
                scan_id,
            )


async def save_scanner_result(
    scan_id: str,
    scanner_name: str,
    raw_json: Dict[str, Any],
    duration_ms: int
) -> str:
    """
    Save a scanner result to the database.
    
    Args:
        scan_id: The UUID of the scan
        scanner_name: The name of the scanner (e.g., 'header_scanner')
        raw_json: The raw JSON output from the scanner
        duration_ms: Duration of the scan in milliseconds
        
    Returns:
        str: The UUID of the created scan_result
    """
    result_id = str(uuid.uuid4())
    
    async with get_connection() as conn:
        await conn.execute(
            """
            INSERT INTO scan_results (id, scan_id, scanner_name, raw_json, duration_ms, created_at)
            VALUES ($1, $2, $3, $4, $5, NOW())
            """,
            result_id,
            scan_id,
            scanner_name,
            json.dumps(raw_json),
            duration_ms,
        )
    
    return result_id

async def save_ai_report(
    scan_id: str,
    risk_score: int,
    summary: str,
    findings_json: Dict[str, Any]
) -> str:
    """
    Save an AI report to the database.
    
    Args:
        scan_id: The UUID of the scan
        risk_score: Risk score from 0-100
        summary: Summary of the findings
        findings_json: Detailed findings in JSON format
        
    Returns:
        str: The UUID of the created ai_report
    """
    if not (0 <= risk_score <= 100):
        raise ValueError("Risk score must be between 0 and 100")
    
    report_id = str(uuid.uuid4())
    
    async with get_connection() as conn:
        await conn.execute(
            """
            INSERT INTO ai_reports (id, scan_id, risk_score, summary, findings_json, created_at)
            VALUES ($1, $2, $3, $4, $5, NOW())
            """,
            report_id,
            scan_id,
            risk_score,
            summary,
            json.dumps(findings_json),
        )
    
    return report_id

async def get_scan(scan_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a scan by its ID.
    
    Args:
        scan_id: The UUID of the scan
        
    Returns:
        Optional[Dict]: The scan data or None if not found
    """
    async with get_connection() as conn:
        row = await conn.fetchrow(
            """
            SELECT id, url, status, created_at, completed_at, user_ip, consent_confirmed
            FROM scans
            WHERE id = $1
            """,
            scan_id,
        )
        
        if row is None:
            return None
        
        return dict(row)

async def get_scan_with_results(scan_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a scan along with all its results and AI report.
    
    Args:
        scan_id: The UUID of the scan
        
    Returns:
        Optional[Dict]: The scan data with nested results and report, or None if not found
    """
    async with get_connection() as conn:
        # Get the scan
        scan_row = await conn.fetchrow(
            """
            SELECT id, url, status, created_at, completed_at, user_ip, consent_confirmed
            FROM scans
            WHERE id = $1
            """,
            scan_id,
        )
        
        if scan_row is None:
            return None
        
        scan = dict(scan_row)
        
        # Get scan results
        result_rows = await conn.fetch(
            """
            SELECT id, scanner_name, raw_json, duration_ms, created_at
            FROM scan_results
            WHERE scan_id = $1
            ORDER BY created_at
            """,
            scan_id,
        )
        
        scan['results'] = [dict(row) for row in result_rows]
        
        # Get AI report if exists
        report_row = await conn.fetchrow(
            """
            SELECT id, risk_score, summary, findings_json, created_at
            FROM ai_reports
            WHERE scan_id = $1
            """,
            scan_id,
        )
        
        if report_row:
            scan['report'] = dict(report_row)
        else:
            scan['report'] = None
        
        return scan

# Utility functions for testing

async def health_check() -> bool:
    """
    Check if the database connection is healthy.
    
    Returns:
        bool: True if connection is healthy
    """
    try:
        async with get_connection() as conn:
            await conn.fetchval("SELECT 1")
        return True
    except Exception:
        return False


async def delete_scan(scan_id: str) -> bool:
    """
    Delete a scan and all related data (cascade will handle results and reports).
    
    Args:
        scan_id: The UUID of the scan to delete
        
    Returns:
        bool: True if scan was deleted
    """
    async with get_connection() as conn:
        result = await conn.execute(
            "DELETE FROM scans WHERE id = $1",
            scan_id,
        )
        return result != "DELETE 0"
