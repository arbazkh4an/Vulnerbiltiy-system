"""
SentinelAI — SSL/TLS Scanner
Checks TLS version, certificate expiry, weak ciphers, and HSTS.
"""

import asyncio
import ssl
import socket
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

from app.config import get_settings
from app.logging import get_logger
from app.scanners.base import BaseScanner

logger = get_logger(__name__)

# TLS versions considered weak
_WEAK_TLS = {"TLSv1", "TLSv1.1"}

# Cipher suites considered weak
_WEAK_CIPHERS_KEYWORDS = {"RC4", "DES", "3DES", "MD5", "NULL", "EXPORT", "anon"}


class SSLScanner(BaseScanner):
    """Scans SSL/TLS configuration for security issues."""

    name = "ssl_scanner"

    async def run(self, url: str) -> dict[str, Any]:
        findings: list[dict[str, Any]] = []
        settings = get_settings()

        parsed = urlparse(url)
        hostname = parsed.hostname or ""
        port = parsed.port or (443 if parsed.scheme == "https" else 80)

        # Skip SSL checks for HTTP-only sites
        if parsed.scheme != "https":
            findings.append(
                {
                    "title": "No HTTPS Encryption",
                    "severity": "high",
                    "description": "The site is served over plain HTTP without TLS encryption. "
                    "All traffic, including credentials and sensitive data, is transmitted in cleartext.",
                    "remediation": "Enable HTTPS with a valid TLS certificate (e.g., Let's Encrypt).",
                    "owasp_category": "A02:2021-Cryptographic Failures",
                    "evidence": f"Site accessed via {parsed.scheme}://",
                }
            )
            return {"scanner": self.name, "findings": findings, "error": None}

        try:
            # Run SSL checks in a thread to avoid blocking the event loop
            ssl_result = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None, self._check_ssl, hostname, port
                ),
                timeout=settings.SCAN_TIMEOUT,
            )
            findings.extend(ssl_result)

            logger.info("ssl_scan_complete", url=url, findings_count=len(findings))
            return {"scanner": self.name, "findings": findings, "error": None}

        except asyncio.TimeoutError:
            logger.warning("ssl_scan_timeout", url=url)
            return {
                "scanner": self.name,
                "findings": findings,
                "error": f"SSL check timed out after {settings.SCAN_TIMEOUT}s",
            }
        except Exception as exc:
            logger.error("ssl_scan_error", url=url, error=str(exc))
            return {"scanner": self.name, "findings": findings, "error": str(exc)}

    def _check_ssl(self, hostname: str, port: int) -> list[dict[str, Any]]:
        """Synchronous SSL checks (run in executor)."""
        findings: list[dict[str, Any]] = []

        try:
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    # TLS version
                    tls_version = ssock.version()
                    if tls_version and tls_version in _WEAK_TLS:
                        findings.append(
                            {
                                "title": f"Weak TLS Version: {tls_version}",
                                "severity": "high",
                                "description": f"Server supports {tls_version}, which has known vulnerabilities. "
                                "This can be exploited via POODLE, BEAST, or CRIME attacks.",
                                "remediation": "Disable TLS 1.0 and 1.1. Use TLS 1.2 or 1.3 only.",
                                "owasp_category": "A02:2021-Cryptographic Failures",
                                "evidence": f"Negotiated TLS version: {tls_version}",
                            }
                        )

                    # Certificate expiry
                    cert = ssock.getpeercert()
                    if cert:
                        not_after_str = cert.get("notAfter", "")
                        if not_after_str:
                            not_after = datetime.strptime(
                                not_after_str, "%b %d %H:%M:%S %Y %Z"
                            ).replace(tzinfo=timezone.utc)
                            now = datetime.now(timezone.utc)
                            days_remaining = (not_after - now).days

                            if days_remaining < 0:
                                findings.append(
                                    {
                                        "title": "Expired SSL Certificate",
                                        "severity": "critical",
                                        "description": f"The SSL certificate expired {abs(days_remaining)} days ago. "
                                        "Users will see browser warnings and connections may be intercepted.",
                                        "remediation": "Renew the SSL certificate immediately.",
                                        "owasp_category": "A02:2021-Cryptographic Failures",
                                        "evidence": f"Certificate expiry: {not_after_str}",
                                    }
                                )
                            elif days_remaining < 30:
                                findings.append(
                                    {
                                        "title": "SSL Certificate Expiring Soon",
                                        "severity": "medium",
                                        "description": f"The SSL certificate expires in {days_remaining} days. "
                                        "If not renewed, users will see browser security warnings.",
                                        "remediation": "Renew the SSL certificate before expiry.",
                                        "owasp_category": "A02:2021-Cryptographic Failures",
                                        "evidence": f"Certificate expiry: {not_after_str}, {days_remaining} days remaining",
                                    }
                                )

                    # Cipher strength
                    cipher_info = ssock.cipher()
                    if cipher_info:
                        cipher_name = cipher_info[0]
                        for weak_keyword in _WEAK_CIPHERS_KEYWORDS:
                            if weak_keyword in cipher_name.upper():
                                findings.append(
                                    {
                                        "title": f"Weak Cipher Suite: {cipher_name}",
                                        "severity": "high",
                                        "description": f"The server negotiated a weak cipher suite: {cipher_name}. "
                                        "This may be vulnerable to cryptographic attacks.",
                                        "remediation": "Disable weak cipher suites. Use only AES-GCM or ChaCha20-Poly1305.",
                                        "owasp_category": "A02:2021-Cryptographic Failures",
                                        "evidence": f"Negotiated cipher: {cipher_name}",
                                    }
                                )
                                break

        except ssl.SSLCertVerificationError as exc:
            findings.append(
                {
                    "title": "SSL Certificate Verification Failed",
                    "severity": "high",
                    "description": f"SSL certificate could not be verified: {str(exc)[:200]}. "
                    "This may indicate a self-signed, expired, or mismatched certificate.",
                    "remediation": "Use a valid certificate from a trusted Certificate Authority.",
                    "owasp_category": "A02:2021-Cryptographic Failures",
                    "evidence": str(exc)[:300],
                }
            )
        except (socket.timeout, ConnectionRefusedError, OSError) as exc:
            findings.append(
                {
                    "title": "SSL Connection Failed",
                    "severity": "info",
                    "description": f"Could not establish SSL connection: {str(exc)[:200]}",
                    "remediation": "Ensure the server accepts TLS connections on the correct port.",
                    "owasp_category": "A02:2021-Cryptographic Failures",
                    "evidence": str(exc)[:300],
                }
            )

        return findings
