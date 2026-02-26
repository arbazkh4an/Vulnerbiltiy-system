"""
FastAPI Backend - Main Application
Vulnerability scanning API with Redis queue integration
"""

import json
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
import redis.asyncio as redis
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from models import (
    ScanRequest, ScanResponse, ScanStatusResponse,
    ScanResultsResponse, HealthResponse, ScanListResponse, ScanListItem,
    ScannerResult
)
from config import settings
from dependencies import init_db_pool, close_db_pool, init_redis, close_redis, get_db, get_redis
from database.db import create_scan, get_scan, get_scan_with_results, health_check as db_health_check
import websocket


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db_pool()
    await init_redis()
    yield
    await close_db_pool()
    await close_redis()


app = FastAPI(title="VulnScan API", lifespan=lifespan)

app.include_router(websocket.router)


def is_localhost(url: str) -> bool:
    """Check if URL is localhost or internal."""
    url_lower = url.lower()
    return (
        "localhost" in url_lower or
        "127.0.0.1" in url_lower or
        "0.0.0.0" in url_lower or
        ".local" in url_lower or
        url_lower.startswith("http://localhost")
    )


@app.post("/api/scan", response_model=ScanResponse)
async def create_new_scan(request: ScanRequest, req: Request):
    """
    Start a new vulnerability scan.
    """
    url_str = str(request.url)
    
    if is_localhost(url_str):
        raise HTTPException(status_code=400, detail="Localhost URLs are not allowed")
    
    if not request.consent:
        raise HTTPException(status_code=400, detail="Consent must be true")
    
    user_ip = req.client.host if req.client else "unknown"
    
    scan_id = await create_scan(url_str, user_ip, request.consent)
    
    redis_client = await get_redis()
    job_data = json.dumps({"scan_id": scan_id, "url": url_str})
    await redis_client.lpush("scan_queue", job_data)
    
    return ScanResponse(
        scan_id=scan_id,
        status="queued",
        message="Scan started"
    )


@app.get("/api/scan/{scan_id}", response_model=ScanStatusResponse)
async def get_scan_status(scan_id: str):
    """
    Get scan status and details.
    """
    scan = await get_scan(scan_id)
    
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    findings = None
    if scan["status"] == "complete":
        full_scan = await get_scan_with_results(scan_id)
        if full_scan and full_scan.get("report"):
            findings = full_scan["report"]
    
    return ScanStatusResponse(
        scan_id=scan["id"],
        url=scan["url"],
        status=scan["status"],
        created_at=scan["created_at"],
        completed_at=scan.get("completed_at"),
        findings=findings
    )


@app.get("/api/scan/{scan_id}/results", response_model=ScanResultsResponse)
async def get_scan_results(scan_id: str):
    """
    Get all scanner sub-results for a scan.
    """
    scan = await get_scan(scan_id)
    
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    full_scan = await get_scan_with_results(scan_id)
    
    results = []
    if full_scan and full_scan.get("results"):
        for r in full_scan["results"]:
            results.append(ScannerResult(
                scanner_name=r["scanner_name"],
                raw_json=r["raw_json"] if isinstance(r["raw_json"], dict) else json.loads(r["raw_json"]),
                duration_ms=r.get("duration_ms")
            ))
    
    return ScanResultsResponse(scan_id=scan_id, results=results)


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint - verifies DB and Redis connections.
    """
    db_status = "ok" if await db_health_check() else "error"
    
    try:
        redis_client = await get_redis()
        await redis_client.ping()
        redis_status = "ok"
    except Exception:
        redis_status = "error"
    
    return HealthResponse(
        status="ok" if db_status == "ok" and redis_status == "ok" else "degraded",
        db=db_status,
        redis=redis_status
    )


@app.get("/api/scans", response_model=ScanListResponse)
async def list_scans():
    """
    Get last 10 scans (no sensitive data).
    """
    from database.db import get_pool
    
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT id, url, status, created_at
            FROM scans
            ORDER BY created_at DESC
            LIMIT 10
            """
        )
    
    scans = [
        ScanListItem(
            id=str(row["id"]),
            url=row["url"],
            status=row["status"],
            created_at=row["created_at"]
        )
        for row in rows
    ]
    
    return ScanListResponse(scans=scans)
