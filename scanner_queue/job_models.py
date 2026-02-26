"""
OWASP AI Scanner - Job Models
Data models for scan jobs
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class ScanJob:
    """
    Represents a scan job to be processed by the queue.
    
    Attributes:
        scan_id: Unique identifier for the scan
        url: Target URL to scan
        created_at: ISO timestamp when job was created
        priority: Job priority (1=highest, 10=lowest, default=5)
    """
    scan_id: str
    url: str
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    priority: int = 5
    
    def __post_init__(self):
        """Validate job parameters."""
        if not self.scan_id:
            raise ValueError("scan_id is required")
        if not self.url:
            raise ValueError("url is required")
        if not 1 <= self.priority <= 10:
            raise ValueError("priority must be between 1 and 10")
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "scan_id": self.scan_id,
            "url": self.url,
            "created_at": self.created_at,
            "priority": self.priority,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ScanJob":
        """Create from dictionary."""
        return cls(
            scan_id=data["scan_id"],
            url=data["url"],
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
            priority=data.get("priority", 5),
        )
