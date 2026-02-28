"""
SentinelAI — Path Exposure Scanner
Probes for commonly exposed sensitive files and directories.
"""

from typing import Any
from urllib.parse import urljoin

import httpx

from app.config import get_settings
from app.logging import get_logger
from app.scanners.base import BaseScanner

logger = get_logger(__name__)

# Sensitive paths to check — (path, description, severity)
_SENSITIVE_PATHS = [
    ("/.env", "Environment configuration file with secrets", "critical"),
    ("/.git/config", "Git repository configuration (source code exposure)", "critical"),
    ("/.git/HEAD", "Git HEAD reference (repository exposure)", "critical"),
    ("/backup.zip", "Backup archive with potential source code or data", "high"),
    ("/backup.tar.gz", "Backup archive with potential source code or data", "high"),
    ("/db.sql", "Database dump file", "critical"),
    ("/dump.sql", "Database dump file", "critical"),
    ("/.DS_Store", "macOS directory metadata (information disclosure)", "low"),
    ("/wp-admin/", "WordPress admin panel", "medium"),
    ("/phpmyadmin/", "phpMyAdmin database management", "high"),
    ("/admin/", "Administrative interface", "medium"),
    ("/server-status", "Apache server status page", "medium"),
    ("/server-info", "Apache server info page", "medium"),
    ("/.htaccess", "Apache configuration file", "medium"),
    ("/.htpasswd", "Apache password file", "critical"),
    ("/web.config", "IIS configuration file", "high"),
    ("/crossdomain.xml", "Flash cross-domain policy", "low"),
    ("/elmah.axd", "ELMAH error log (ASP.NET)", "high"),
    ("/trace.axd", "ASP.NET trace viewer", "high"),
    ("/phpinfo.php", "PHP configuration disclosure", "high"),
    ("/info.php", "PHP configuration disclosure", "high"),
    ("/.well-known/security.txt", "Security contact information", "info"),
]

# Status codes that indicate the path exists
_EXPOSED_CODES = {200, 301, 302, 403}


class PathScanner(BaseScanner):
    """Scans for exposed sensitive files and directories."""

    name = "path_scanner"

    async def run(self, url: str) -> dict[str, Any]:
        findings: list[dict[str, Any]] = []
        settings = get_settings()

        try:
            async with httpx.AsyncClient(
                timeout=5.0,  # Short timeout per path
                follow_redirects=False,
                verify=False,
            ) as client:
                for path, description, severity in _SENSITIVE_PATHS:
                    try:
                        target = urljoin(url.rstrip("/") + "/", path.lstrip("/"))
                        response = await client.head(target)

                        if response.status_code in _EXPOSED_CODES:
                            # 403 is less severe (exists but blocked)
                            actual_severity = severity if response.status_code != 403 else "info"

                            # For 200, verify it's not a generic "not found" page
                            if response.status_code == 200:
                                # Try GET to check content length
                                get_resp = await client.get(target)
                                content_len = len(get_resp.content)

                                # Skip tiny responses (likely custom 404s)
                                if content_len < 20:
                                    continue

                                findings.append(
                                    {
                                        "title": f"Exposed Path: {path}",
                                        "severity": actual_severity,
                                        "description": f"{description}. "
                                        f"This file/directory is publicly accessible.",
                                        "remediation": f"Block public access to {path} via server configuration "
                                        "or remove the file from the web root.",
                                        "owasp_category": "A01:2021-Broken Access Control",
                                        "evidence": f"HTTP {response.status_code} at {target} "
                                        f"(content length: {content_len} bytes)",
                                    }
                                )
                            elif response.status_code == 403:
                                findings.append(
                                    {
                                        "title": f"Path Exists But Forbidden: {path}",
                                        "severity": "info",
                                        "description": f"The path {path} exists but returns 403. "
                                        "While access is denied, the existence of this path reveals information.",
                                        "remediation": "Return a 404 instead of 403 to avoid information disclosure.",
                                        "owasp_category": "A01:2021-Broken Access Control",
                                        "evidence": f"HTTP 403 at {target}",
                                    }
                                )

                    except (httpx.TimeoutException, httpx.ConnectError):
                        # Individual path timeout — skip and continue
                        continue
                    except Exception:
                        continue

            logger.info("path_scan_complete", url=url, findings_count=len(findings))
            return {"scanner": self.name, "findings": findings, "error": None}

        except Exception as exc:
            logger.error("path_scan_error", url=url, error=str(exc))
            return {"scanner": self.name, "findings": [], "error": str(exc)}
