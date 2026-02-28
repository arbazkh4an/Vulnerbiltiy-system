"""
SentinelAI — Scan Pydantic Models
Request/response schemas for the scan API.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, HttpUrl, field_validator


class ScanStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"


class ScanCreate(BaseModel):
    """Request body for POST /api/scan."""

    url: str
    consent: bool = True

    @field_validator("url")
    @classmethod
    def url_must_be_valid(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("URL is required")
        if not v.startswith(("http://", "https://")):
            raise ValueError("Only HTTP and HTTPS protocols are allowed")
        return v

    @field_validator("consent")
    @classmethod
    def consent_must_be_true(cls, v: bool) -> bool:
        if not v:
            raise ValueError("Consent is required to perform a scan")
        return v


class ScanResponse(BaseModel):
    """Response for POST /api/scan."""

    scan_id: str
    status: ScanStatus


class ScanDetailResponse(BaseModel):
    """Response for GET /api/scan/{scan_id}."""

    id: str
    url: str
    status: ScanStatus
    progress: int = 0
    created_at: Optional[str] = None
    completed_at: Optional[str] = None
    total_vulnerabilities: int = 0
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    raw_results: Optional[dict] = None
    ai_report: Optional[dict] = None
    error_message: Optional[str] = None


class HistoryItem(BaseModel):
    """One item in the scan history list."""

    id: str
    url: str
    status: ScanStatus
    created_at: Optional[str] = None
    completed_at: Optional[str] = None
    total_vulnerabilities: int = 0
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0


class HistoryResponse(BaseModel):
    """Response for GET /api/history."""

    scans: list[HistoryItem]
    total: int = 0


class HealthResponse(BaseModel):
    """Response for GET /api/health."""

    status: str
    service: str
    version: str
    db: str
