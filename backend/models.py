"""
Pydantic models for request/response validation
"""

from pydantic import BaseModel, HttpUrl, model_validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class ScanRequest(BaseModel):
    url: HttpUrl
    consent: bool

    @model_validator(mode='before')
    @classmethod
    def check_consent(cls, data):
        if isinstance(data, dict) and not data.get('consent', True):
            raise ValueError('consent must be true')
        return data


class ScanResponse(BaseModel):
    scan_id: str
    status: str
    message: str


class ScanStatusResponse(BaseModel):
    scan_id: str
    url: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    findings: Optional[Dict[str, Any]] = None


class ScannerResult(BaseModel):
    scanner_name: str
    raw_json: Dict[str, Any]
    duration_ms: Optional[int] = None


class ScanResultsResponse(BaseModel):
    scan_id: str
    results: List[ScannerResult]


class HealthResponse(BaseModel):
    status: str
    db: str
    redis: str


class ScanListItem(BaseModel):
    id: str
    url: str
    status: str
    created_at: datetime


class ScanListResponse(BaseModel):
    scans: List[ScanListItem]
