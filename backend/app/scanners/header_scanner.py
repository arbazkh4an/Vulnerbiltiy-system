"""
SentinelAI — HTTP Security Header Scanner
Checks for missing or misconfigured security headers.
"""

from typing import Any

import httpx

from app.config import get_settings
from app.logging import get_logger
from app.scanners.base import BaseScanner

logger = get_logger(__name__)

# Headers that should be present for security
_SECURITY_HEADERS = {
    "Strict-Transport-Security": {
        "severity": "high",
        "description": "HTTP Strict Transport Security (HSTS) not configured. "
        "Browsers may connect over insecure HTTP.",
        "remediation": "Add 'Strict-Transport-Security: max-age=31536000; includeSubDomains' header.",
        "owasp": "A05:2021-Security Misconfiguration",
    },
    "Content-Security-Policy": {
        "severity": "medium",
        "description": "Content Security Policy (CSP) not set. "
        "Increases risk of XSS and data injection attacks.",
        "remediation": "Implement a Content-Security-Policy header restricting allowed sources.",
        "owasp": "A03:2021-Injection",
    },
    "X-Content-Type-Options": {
        "severity": "medium",
        "description": "X-Content-Type-Options header missing. "
        "Browser may MIME-sniff content, enabling XSS.",
        "remediation": "Add 'X-Content-Type-Options: nosniff' header.",
        "owasp": "A05:2021-Security Misconfiguration",
    },
    "X-Frame-Options": {
        "severity": "medium",
        "description": "X-Frame-Options header missing. "
        "Site may be vulnerable to clickjacking attacks.",
        "remediation": "Add 'X-Frame-Options: DENY' or 'SAMEORIGIN' header.",
        "owasp": "A05:2021-Security Misconfiguration",
    },
    "Referrer-Policy": {
        "severity": "low",
        "description": "Referrer-Policy not set. "
        "Full URLs may be leaked in Referer headers to third parties.",
        "remediation": "Add 'Referrer-Policy: strict-origin-when-cross-origin' header.",
        "owasp": "A05:2021-Security Misconfiguration",
    },
    "Permissions-Policy": {
        "severity": "low",
        "description": "Permissions-Policy (formerly Feature-Policy) not set. "
        "Browser features may be used without restriction.",
        "remediation": "Add a Permissions-Policy header to restrict camera, microphone, geolocation, etc.",
        "owasp": "A05:2021-Security Misconfiguration",
    },
}


class HeaderScanner(BaseScanner):
    """Scans for missing or misconfigured HTTP security headers."""

    name = "header_scanner"

    async def run(self, url: str) -> dict[str, Any]:
        findings: list[dict[str, Any]] = []
        settings = get_settings()

        try:
            async with httpx.AsyncClient(
                timeout=settings.SCAN_TIMEOUT,
                follow_redirects=True,
                verify=False,
            ) as client:
                response = await client.get(url)

            response_headers = {k.lower(): v for k, v in response.headers.items()}

            # Check for missing security headers
            for header_name, info in _SECURITY_HEADERS.items():
                if header_name.lower() not in response_headers:
                    findings.append(
                        {
                            "title": f"Missing Security Header: {header_name}",
                            "severity": info["severity"],
                            "description": info["description"],
                            "remediation": info["remediation"],
                            "owasp_category": info["owasp"],
                            "evidence": f"Header '{header_name}' was not present in the response.",
                        }
                    )

            # Check for server version disclosure
            server_header = response_headers.get("server", "")
            if server_header:
                # Check if version numbers are disclosed
                import re

                if re.search(r"\d+\.\d+", server_header):
                    findings.append(
                        {
                            "title": "Server Version Disclosure",
                            "severity": "low",
                            "description": f"The server discloses its version: '{server_header}'. "
                            "This aids attackers in targeting known vulnerabilities.",
                            "remediation": "Configure the server to suppress version information in the Server header.",
                            "owasp_category": "A05:2021-Security Misconfiguration",
                            "evidence": f"Server header value: {server_header}",
                        }
                    )

            # Check X-Powered-By disclosure
            x_powered = response_headers.get("x-powered-by", "")
            if x_powered:
                findings.append(
                    {
                        "title": "Technology Stack Disclosure (X-Powered-By)",
                        "severity": "low",
                        "description": f"X-Powered-By header reveals: '{x_powered}'. "
                        "Attackers can target known framework vulnerabilities.",
                        "remediation": "Remove the X-Powered-By header from server responses.",
                        "owasp_category": "A05:2021-Security Misconfiguration",
                        "evidence": f"X-Powered-By: {x_powered}",
                    }
                )

            # Check CORS misconfiguration
            acao = response_headers.get("access-control-allow-origin", "")
            if acao == "*":
                findings.append(
                    {
                        "title": "Permissive CORS Policy",
                        "severity": "medium",
                        "description": "Access-Control-Allow-Origin is set to '*', "
                        "allowing any origin to make cross-origin requests.",
                        "remediation": "Restrict Access-Control-Allow-Origin to specific trusted domains.",
                        "owasp_category": "A01:2021-Broken Access Control",
                        "evidence": "Access-Control-Allow-Origin: *",
                    }
                )

            logger.info("header_scan_complete", url=url, findings_count=len(findings))
            return {"scanner": self.name, "findings": findings, "error": None}

        except httpx.TimeoutException:
            logger.warning("header_scan_timeout", url=url)
            return {
                "scanner": self.name,
                "findings": [],
                "error": f"Connection timed out after {settings.SCAN_TIMEOUT}s",
            }
        except Exception as exc:
            logger.error("header_scan_error", url=url, error=str(exc))
            return {"scanner": self.name, "findings": [], "error": str(exc)}
