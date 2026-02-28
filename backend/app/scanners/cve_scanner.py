"""
SentinelAI — CVE Scanner
Detects web technology stack and queries NVD API for known CVEs.
"""

import re
from typing import Any, Optional
from urllib.parse import urlparse

import httpx

from app.config import get_settings
from app.logging import get_logger
from app.scanners.base import BaseScanner

logger = get_logger(__name__)

# Patterns to detect technologies from HTTP headers and HTML
_HEADER_TECH_PATTERNS = {
    "server": [
        (r"Apache[/ ]?([\d.]+)?", "Apache HTTP Server"),
        (r"nginx[/ ]?([\d.]+)?", "nginx"),
        (r"Microsoft-IIS[/ ]?([\d.]+)?", "Microsoft IIS"),
        (r"LiteSpeed[/ ]?([\d.]+)?", "LiteSpeed"),
        (r"Caddy[/ ]?([\d.]+)?", "Caddy"),
    ],
    "x-powered-by": [
        (r"PHP[/ ]?([\d.]+)?", "PHP"),
        (r"ASP\.NET[/ ]?([\d.]+)?", "ASP.NET"),
        (r"Express", "Express.js"),
        (r"Next\.js[/ ]?([\d.]+)?", "Next.js"),
        (r"Django[/ ]?([\d.]+)?", "Django"),
    ],
    "x-aspnet-version": [
        (r"([\d.]+)", "ASP.NET"),
    ],
}

_HTML_TECH_PATTERNS = [
    (r'<meta\s+name=["\']generator["\']\s+content=["\']WordPress\s*([\d.]*)', "WordPress"),
    (r'<meta\s+name=["\']generator["\']\s+content=["\']Joomla', "Joomla"),
    (r'<meta\s+name=["\']generator["\']\s+content=["\']Drupal\s*([\d.]*)', "Drupal"),
    (r"/wp-content/", "WordPress"),
    (r"/wp-includes/", "WordPress"),
    (r"jQuery[/ ]v?([\d.]+)", "jQuery"),
    (r"Bootstrap[/ ]v?([\d.]+)", "Bootstrap"),
    (r"react[/ ]v?([\d.]+)", "React"),
    (r"vue[/ ]v?([\d.]+)", "Vue.js"),
    (r"angular[/ ]v?([\d.]+)", "Angular"),
]

NVD_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"


class CVEScanner(BaseScanner):
    """Detects technology stack and queries NVD for known CVEs."""

    name = "cve_scanner"

    async def run(self, url: str) -> dict[str, Any]:
        findings: list[dict[str, Any]] = []
        settings = get_settings()

        try:
            # Step 1: Fetch the page
            async with httpx.AsyncClient(
                timeout=settings.SCAN_TIMEOUT,
                follow_redirects=True,
                verify=False,
            ) as client:
                response = await client.get(url)

            # Step 2: Detect technologies
            detected = self._detect_technologies(response)

            if not detected:
                logger.info("cve_scan_no_tech_detected", url=url)
                return {"scanner": self.name, "findings": [], "error": None}

            # Step 3: Query NVD API for each detected technology
            async with httpx.AsyncClient(timeout=15) as client:
                for tech_name, tech_version in detected:
                    cve_findings = await self._query_nvd(
                        client, tech_name, tech_version, settings.NVD_API_KEY
                    )
                    findings.extend(cve_findings)

            logger.info(
                "cve_scan_complete",
                url=url,
                technologies_detected=len(detected),
                findings_count=len(findings),
            )
            return {"scanner": self.name, "findings": findings, "error": None}

        except Exception as exc:
            logger.error("cve_scan_error", url=url, error=str(exc))
            return {"scanner": self.name, "findings": [], "error": str(exc)}

    def _detect_technologies(
        self, response: httpx.Response
    ) -> list[tuple[str, Optional[str]]]:
        """Detect web technologies from response headers and HTML body."""
        detected: list[tuple[str, Optional[str]]] = []

        # Check headers
        for header_name, patterns in _HEADER_TECH_PATTERNS.items():
            header_value = response.headers.get(header_name, "")
            if header_value:
                for pattern, tech_name in patterns:
                    match = re.search(pattern, header_value, re.IGNORECASE)
                    if match:
                        version = match.group(1) if match.lastindex and match.group(1) else None
                        detected.append((tech_name, version))

        # Check HTML body (first 50KB to avoid memory issues)
        body = response.text[:50000]
        for pattern, tech_name in _HTML_TECH_PATTERNS:
            match = re.search(pattern, body, re.IGNORECASE)
            if match:
                version = match.group(1) if match.lastindex and match.group(1) else None
                # Avoid duplicates
                tech_names = [t[0] for t in detected]
                if tech_name not in tech_names:
                    detected.append((tech_name, version))

        return detected

    async def _query_nvd(
        self,
        client: httpx.AsyncClient,
        tech_name: str,
        version: Optional[str],
        api_key: str,
    ) -> list[dict[str, Any]]:
        """Query the NVD API for CVEs related to a technology."""
        findings: list[dict[str, Any]] = []

        params: dict[str, str] = {
            "keywordSearch": tech_name,
            "resultsPerPage": "5",
        }

        headers: dict[str, str] = {}
        if api_key:
            headers["apiKey"] = api_key

        try:
            response = await client.get(NVD_API_URL, params=params, headers=headers)

            if response.status_code == 403:
                logger.warning("nvd_api_rate_limited", tech=tech_name)
                return []

            if response.status_code != 200:
                logger.warning(
                    "nvd_api_error",
                    tech=tech_name,
                    status=response.status_code,
                )
                return []

            data = response.json()
            vulnerabilities = data.get("vulnerabilities", [])

            for vuln in vulnerabilities[:5]:
                cve_data = vuln.get("cve", {})
                cve_id = cve_data.get("id", "Unknown")

                # Get description
                descriptions = cve_data.get("descriptions", [])
                description = ""
                for desc in descriptions:
                    if desc.get("lang") == "en":
                        description = desc.get("value", "")
                        break

                # Get CVSS score
                cvss_score = 0.0
                metrics = cve_data.get("metrics", {})
                cvss_v31 = metrics.get("cvssMetricV31", [])
                if cvss_v31:
                    cvss_score = cvss_v31[0].get("cvssData", {}).get("baseScore", 0.0)
                else:
                    cvss_v30 = metrics.get("cvssMetricV30", [])
                    if cvss_v30:
                        cvss_score = cvss_v30[0].get("cvssData", {}).get("baseScore", 0.0)

                # Get severity
                if cvss_score >= 9.0:
                    severity = "critical"
                elif cvss_score >= 7.0:
                    severity = "high"
                elif cvss_score >= 4.0:
                    severity = "medium"
                elif cvss_score > 0:
                    severity = "low"
                else:
                    severity = "info"

                # Get CWE IDs
                cwe_ids = []
                weaknesses = cve_data.get("weaknesses", [])
                for weakness in weaknesses:
                    for desc in weakness.get("description", []):
                        if desc.get("lang") == "en":
                            cwe_ids.append(desc.get("value", ""))

                version_info = f" (version {version})" if version else ""
                findings.append(
                    {
                        "title": f"{cve_id} — {tech_name}{version_info}",
                        "severity": severity,
                        "description": description[:500] if description else f"Known vulnerability in {tech_name}.",
                        "remediation": f"Update {tech_name} to the latest patched version. "
                        f"Review {cve_id} details at https://nvd.nist.gov/vuln/detail/{cve_id}",
                        "owasp_category": "A06:2021-Vulnerable and Outdated Components",
                        "evidence": f"Detected {tech_name}{version_info} on target. "
                        f"CVE: {cve_id}, CVSS: {cvss_score}",
                        "cvss_score": cvss_score,
                        "cwe_id": cwe_ids[0] if cwe_ids else None,
                    }
                )

        except httpx.TimeoutException:
            logger.warning("nvd_api_timeout", tech=tech_name)
        except Exception as exc:
            logger.warning("nvd_api_query_error", tech=tech_name, error=str(exc))

        return findings
