from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional


@dataclass
class Finding:
    owasp_id: str
    title: str
    severity: str
    evidence: str
    raw: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ScannerResult:
    scanner_name: str
    scan_id: str
    status: str
    duration_ms: int
    findings: List[Finding]
    raw_data: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scanner_name": self.scanner_name,
            "scan_id": self.scan_id,
            "status": self.status,
            "duration_ms": self.duration_ms,
            "findings": [f.to_dict() for f in self.findings],
            "raw_data": self.raw_data,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScannerResult":
        findings = [Finding(**f) if isinstance(f, dict) else f for f in data.get("findings", [])]
        return cls(
            scanner_name=data["scanner_name"],
            scan_id=data["scan_id"],
            status=data["status"],
            duration_ms=data["duration_ms"],
            findings=findings,
            raw_data=data.get("raw_data", {}),
        )
