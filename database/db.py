"""
OWASP AI Scanner - Database Connection Layer
Supports both PostgreSQL (production) and SQLite (testing)
"""

import json
import os
import uuid
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

import asyncpg

# Database configuration
POSTGRES_URL = "postgresql://scanner:scanner@localhost:5432/scannerdb"

# Test mode flag - use SQLite when True
TEST_MODE = os.environ.get("DB_TEST_MODE", "false").lower() == "true"
SQLITE_URL = ":memory:"

# Global connection pool
_pool: Optional[asyncpg.Pool] = None
_sqlite_conn: Optional[Any] = None


async def init_db_pool() -> Any:
    """
    Initialize the database connection pool.
    Should be called on application startup.
    
    Returns:
        The connection pool (asyncpg.Pool for PostgreSQL, aiosqlite connection for SQLite)
    """
    global _pool, _sqlite_conn
    
    if TEST_MODE:
        import aiosqlite
        _sqlite_conn = await aiosqlite.connect(SQLITE_URL)
        await _setup_sqlite_schema(_sqlite_conn)
        return _sqlite_conn
    else:
        if _pool is None:
            _pool = await asyncpg.create_pool(
                POSTGRES_URL,
                min_size=2,
                max_size=10,
                command_timeout=60,
            )
        return _pool


async def _setup_sqlite_schema(conn: Any) -> None:
    """Create SQLite schema for testing."""
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id TEXT PRIMARY KEY,
            url TEXT NOT NULL,
            status TEXT,
            created_at TEXT,
            completed_at TEXT,
            user_ip TEXT,
            consent_confirmed INTEGER
        )
    """)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS scan_results (
            id TEXT PRIMARY KEY,
            scan_id TEXT NOT NULL,
            scanner_name TEXT,
            raw_json TEXT,
            duration_ms INTEGER,
            created_at TEXT,
            FOREIGN KEY (scan_id) REFERENCES scans(id) ON DELETE CASCADE
        )
    """)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS ai_reports (
            id TEXT PRIMARY KEY,
            scan_id TEXT NOT NULL,
            risk_score INTEGER,
            summary TEXT,
            findings_json TEXT,
            created_at TEXT,
            FOREIGN KEY (scan_id) REFERENCES scans(id) ON DELETE CASCADE
        )
    """)
    await conn.commit()


async def close_db_pool() -> None:
    """
    Close the database connection pool.
    Should be called on application shutdown.
    """
    global _pool, _sqlite_conn
    if TEST_MODE:
        if _sqlite_conn is not None:
            await _sqlite_conn.close()
            _sqlite_conn = None
    else:
        if _pool is not None:
            await _pool.close()
            _pool = None


def get_pool() -> Any:
    """
    Get the current database connection pool.
    
    Returns:
        The connection pool
        
    Raises:
        RuntimeError: If pool not initialized
    """
    if TEST_MODE:
        if _sqlite_conn is None:
            raise RuntimeError("Database not initialized. Call init_db_pool() first.")
        return _sqlite_conn
    else:
        if _pool is None:
            raise RuntimeError("Database pool not initialized. Call init_db_pool() first.")
        return _pool


@asynccontextmanager
async def get_connection():
    """
    Context manager for getting a database connection from the pool.
    
    Yields:
        A database connection
    """
    pool = get_pool()
    if TEST_MODE:
        yield pool
    else:
        async with pool.acquire() as connection:
            yield connection


def _to_bool(value: Any) -> bool:
    """Convert value to boolean for SQLite."""
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value == 1
    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes')
    return bool(value)


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
    
    if TEST_MODE:
        conn = get_pool()
        consent_val = 1 if consent else 0
        await conn.execute(
            "INSERT INTO scans (id, url, user_ip, consent_confirmed, status, created_at) VALUES (?, ?, ?, ?, 'queued', datetime('now'))",
            (scan_id, url, user_ip, consent_val)
        )
    else:
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
    
    if TEST_MODE:
        conn = get_pool()
        if status in ('complete', 'error'):
            await conn.execute(
                "UPDATE scans SET status = ?, completed_at = datetime('now') WHERE id = ?",
                (status, scan_id)
            )
        else:
            await conn.execute(
                "UPDATE scans SET status = ? WHERE id = ?",
                (status, scan_id)
            )
    else:
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
    
    if TEST_MODE:
        conn = get_pool()
        await conn.execute(
            "INSERT INTO scan_results (id, scan_id, scanner_name, raw_json, duration_ms, created_at) VALUES (?, ?, ?, ?, ?, datetime('now'))",
            (result_id, scan_id, scanner_name, json.dumps(raw_json), duration_ms)
        )
    else:
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
    
    if TEST_MODE:
        conn = get_pool()
        await conn.execute(
            "INSERT INTO ai_reports (id, scan_id, risk_score, summary, findings_json, created_at) VALUES (?, ?, ?, ?, ?, datetime('now'))",
            (report_id, scan_id, risk_score, summary, json.dumps(findings_json))
        )
    else:
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
    if TEST_MODE:
        conn = get_pool()
        cursor = await conn.execute(
            "SELECT id, url, status, created_at, completed_at, user_ip, consent_confirmed FROM scans WHERE id = ?",
            (scan_id,)
        )
        row = await cursor.fetchone()
        
        if row is None:
            return None
        
        return {
            "id": row[0],
            "url": row[1],
            "status": row[2],
            "created_at": row[3],
            "completed_at": row[4],
            "user_ip": row[5],
            "consent_confirmed": _to_bool(row[6])
        }
    else:
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
    if TEST_MODE:
        conn = get_pool()
        
        cursor = await conn.execute(
            "SELECT id, url, status, created_at, completed_at, user_ip, consent_confirmed FROM scans WHERE id = ?",
            (scan_id,)
        )
        scan_row = await cursor.fetchone()
        
        if scan_row is None:
            return None
        
        scan = {
            "id": scan_row[0],
            "url": scan_row[1],
            "status": scan_row[2],
            "created_at": scan_row[3],
            "completed_at": scan_row[4],
            "user_ip": scan_row[5],
            "consent_confirmed": _to_bool(scan_row[6])
        }
        
        # Get scan results
        cursor = await conn.execute(
            "SELECT id, scanner_name, raw_json, duration_ms, created_at FROM scan_results WHERE scan_id = ? ORDER BY created_at",
            (scan_id,)
        )
        result_rows = await cursor.fetchall()
        
        scan['results'] = []
        for row in result_rows:
            scan['results'].append({
                "id": row[0],
                "scanner_name": row[1],
                "raw_json": json.loads(row[2]) if row[2] else {},
                "duration_ms": row[3],
                "created_at": row[4]
            })
        
        # Get AI report if exists
        cursor = await conn.execute(
            "SELECT id, risk_score, summary, findings_json, created_at FROM ai_reports WHERE scan_id = ?",
            (scan_id,)
        )
        report_row = await cursor.fetchone()
        
        if report_row:
            scan['report'] = {
                "id": report_row[0],
                "risk_score": report_row[1],
                "summary": report_row[2],
                "findings_json": json.loads(report_row[3]) if report_row[3] else {},
                "created_at": report_row[4]
            }
        else:
            scan['report'] = None
        
        return scan
    else:
        async with get_connection() as conn:
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


async def health_check() -> bool:
    """
    Check if the database connection is healthy.
    
    Returns:
        bool: True if connection is healthy
    """
    try:
        if TEST_MODE:
            conn = get_pool()
            await conn.execute("SELECT 1")
        else:
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
    if TEST_MODE:
        conn = get_pool()
        cursor = await conn.execute("DELETE FROM scans WHERE id = ?", scan_id)
        return cursor.rowcount > 0
    else:
        async with get_connection() as conn:
            result = await conn.execute(
                "DELETE FROM scans WHERE id = $1",
                scan_id,
            )
            return result != "DELETE 0"
