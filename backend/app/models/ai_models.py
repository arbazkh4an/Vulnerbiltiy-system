"""
SentinelAI — AI Report Pydantic Models
Schemas for AI-generated vulnerability reports.
"""

from typing import Literal, Optional

from pydantic import BaseModel, Field


class Finding(BaseModel):
    """A single vulnerability finding from the AI analysis."""

    title: str
    severity: Literal["critical", "high", "medium", "low", "info"]
    owasp_category: str = Field(
        ..., description="e.g. A01:2021-Broken Access Control"
    )
    description: str
    evidence: str
    remediation: str
    cvss_score: float = Field(ge=0.0, le=10.0)
    cwe_id: Optional[str] = None


class AIReport(BaseModel):
    """Complete AI-generated vulnerability report."""

    risk_score: int = Field(ge=0, le=100)
    summary: str
    findings: list[Finding] = Field(default_factory=list)
