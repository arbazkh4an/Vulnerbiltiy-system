import asyncio
import importlib.util
import logging
import sys
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import urlparse

import requests

project_root = Path(__file__).parent.parent.parent
queue_module_path = project_root / "job_queue" / "progress.py"
spec = importlib.util.spec_from_file_location("queue_progress", queue_module_path)
queue_progress = importlib.util.module_from_spec(spec)
spec.loader.exec_module(queue_progress)
redis_publish_progress = queue_progress.publish_progress

from scanners.result_models import ScannerResult, Finding
from scanners.constants import SCANNER_TIMEOUTS

logger = logging.getLogger(__name__)


class BaseScanner(ABC):
    DEFAULT_TIMEOUT = 10
    DEFAULT_HEADERS = {
        "User-Agent": "VulnScanner/1.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    def __init__(self, url: str, scan_id: str):
        self.url = url
        self.scan_id = scan_id
        self.scheme: str = ""
        self.host: str = ""
        self.path: str = ""
        self.port: Optional[int] = None

        self._parse_url()
        self._setup_logger()

    def _parse_url(self) -> None:
        parsed = urlparse(self.url)
        self.scheme = parsed.scheme or "http"
        self.host = parsed.hostname or ""
        self.path = parsed.path or "/"
        self.port = parsed.port

    def _setup_logger(self) -> None:
        self.logger = logging.getLogger(f"{self.__class__.__name__}_{self.scan_id}")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - [%(scan_id)s] - %(message)s",
                defaults={"scan_id": self.scan_id},
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    @abstractmethod
    def _run_scan(self) -> Dict[str, Any]:
        pass

    async def _run_scan_async(self) -> Dict[str, Any]:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._run_scan)

    def run(self) -> ScannerResult:
        scanner_name = self.__class__.__name__
        timeout = SCANNER_TIMEOUTS.get(scanner_name.lower(), SCANNER_TIMEOUTS["default"])

        start_time = time.time()
        self.publish_progress(0, "Starting scan...")

        try:
            self.publish_progress(10, "Running scanner...")
            raw_data = asyncio.run(asyncio.wait_for(self._run_scan_async(), timeout=timeout))
            status = "complete"
            self.publish_progress(100, "Scan complete")

        except asyncio.TimeoutError:
            raw_data = {}
            status = "timeout"
            self.logger.error(f"Scan timed out after {timeout} seconds")
            self.publish_progress(0, f"Scan timed out after {timeout}s")

        except Exception as e:
            raw_data = {"error": str(e)}
            status = "error"
            self.logger.exception(f"Scan failed with error: {e}")
            self.publish_progress(0, f"Scan failed: {str(e)}")

        duration_ms = int((time.time() - start_time) * 1000)
        findings = self._extract_findings(raw_data)

        return ScannerResult(
            scanner_name=scanner_name,
            scan_id=self.scan_id,
            status=status,
            duration_ms=duration_ms,
            findings=findings,
            raw_data=raw_data,
        )

    def _extract_findings(self, raw_data: Dict[str, Any]) -> list[Finding]:
        findings = []
        if "findings" in raw_data and isinstance(raw_data["findings"], list):
            for f in raw_data["findings"]:
                if isinstance(f, Finding):
                    findings.append(f)
                elif isinstance(f, dict):
                    findings.append(
                        Finding(
                            owasp_id=f.get("owasp_id", "Unknown"),
                            title=f.get("title", "Unknown Finding"),
                            severity=f.get("severity", "Info"),
                            evidence=f.get("evidence", ""),
                            raw=f.get("raw", {}),
                        )
                    )
        return findings

    def get(self, path: str, **kwargs) -> requests.Response:
        url = f"{self.scheme}://{self.host}"
        if self.port:
            url += f":{self.port}"
        url += path if path.startswith("/") else f"/{path}"

        kwargs.setdefault("headers", {}).update(self.DEFAULT_HEADERS)
        kwargs.setdefault("timeout", self.DEFAULT_TIMEOUT)
        kwargs.setdefault("verify", False)

        return requests.get(url, **kwargs)

    def post(self, path: str, data: Any, **kwargs) -> requests.Response:
        url = f"{self.scheme}://{self.host}"
        if self.port:
            url += f":{self.port}"
        url += path if path.startswith("/") else f"/{path}"

        kwargs.setdefault("headers", {}).update(self.DEFAULT_HEADERS)
        kwargs.setdefault("timeout", self.DEFAULT_TIMEOUT)
        kwargs.setdefault("verify", False)

        return requests.post(url, data=data, **kwargs)

    def publish_progress(self, percent: int, message: str) -> None:
        try:
            stage = self.__class__.__name__
            redis_publish_progress(self.scan_id, stage, percent, message)
        except Exception as e:
            self.logger.warning(f"Failed to publish progress: {e}")

    def log(self, message: str, level: str = "info") -> None:
        getattr(self.logger, level.lower())(message)
