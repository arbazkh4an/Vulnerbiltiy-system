from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class ScanJob:
    scan_id: str
    url: str
    created_at: Optional[str] = field(default=None)
    priority: int = 5

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc).isoformat()
