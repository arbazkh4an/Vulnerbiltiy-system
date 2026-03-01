"""
SentinelAI — AI Service
LLM-based vulnerability analysis using Groq or OpenAI.
Converts raw scanner output into structured vulnerability reports.
"""

import json
import os
import sys
from typing import Any, Optional

# Add the 'backend' directory to sys.path to resolve 'app' module imports
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.config import get_settings
from app.logging import get_logger
from app.models.ai_models import AIReport

logger = get_logger(__name__)

_SYSTEM_PROMPT = """You are a senior cybersecurity analyst. You will receive raw vulnerability scan results in JSON format from automated security scanners. Your job is to analyze these results and produce a professional, structured vulnerability report.

Rules:
1. Assign a risk_score from 0 (no risk) to 100 (critical risk) based on the overall findings.
2. Write a concise executive summary (2-4 sentences).
3. For each finding, provide:
   - title: clear vulnerability name
   - severity: one of "critical", "high", "medium", "low", "info"
   - owasp_category: the relevant OWASP Top 10:2021 category (e.g., "A01:2021-Broken Access Control")
   - description: detailed explanation of the issue and its impact
   - evidence: the specific technical evidence from the scan results
   - remediation: actionable steps to fix the issue
   - cvss_score: estimated CVSS v3 base score (0.0 to 10.0)
   - cwe_id: the CWE identifier if applicable (e.g., "CWE-79"), or null
4. Deduplicate similar findings across scanners.
5. Prioritize findings by severity (critical first).
6. Do NOT fabricate findings that are not supported by the scan data.
7. Output MUST be valid JSON only — no markdown, no explanation outside the JSON."""

_USER_PROMPT_TEMPLATE = """Analyze the following vulnerability scan results and produce a structured report.

Target URL: {url}

Scan Results:
{scan_results}

Output the report as a JSON object with this exact schema:
{{
  "risk_score": <integer 0-100>,
  "summary": "<executive summary string>",
  "findings": [
    {{
      "title": "<string>",
      "severity": "<critical|high|medium|low|info>",
      "owasp_category": "<string>",
      "description": "<string>",
      "evidence": "<string>",
      "remediation": "<string>",
      "cvss_score": <float 0.0-10.0>,
      "cwe_id": "<string or null>"
    }}
  ]
}}"""


async def generate_ai_report(
    scan_results: dict[str, Any], url: str
) -> dict[str, Any]:
    """
    Generate an AI vulnerability report from raw scan results.

    Tries Groq first, falls back to OpenAI, then to a basic rule-based report.
    """
    settings = get_settings()

    user_prompt = _USER_PROMPT_TEMPLATE.format(
        url=url,
        scan_results=json.dumps(scan_results, indent=2, default=str),
    )

    # Try Groq
    if settings.GROQ_API_KEY:
        report = await _call_groq(settings.GROQ_API_KEY, settings.AI_MODEL, user_prompt)
        if report:
            return report

    # Fallback to OpenAI
    if settings.OPENAI_API_KEY:
        report = await _call_openai(settings.OPENAI_API_KEY, user_prompt)
        if report:
            return report

    # Final fallback: rule-based report
    logger.warning("ai_fallback_to_rules", url=url)
    return _generate_fallback_report(scan_results)


async def _call_groq(api_key: str, model: str, user_prompt: str) -> Optional[dict[str, Any]]:
    """Call Groq API for report generation."""
    try:
        from groq import AsyncGroq

        client = AsyncGroq(api_key=api_key)

        for attempt in range(2):
            try:
                response = await client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": _SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.1,
                    max_tokens=4096,
                )

                content = response.choices[0].message.content
                if not content:
                    continue

                parsed = json.loads(content)

                # Validate through Pydantic
                report = AIReport(**parsed)
                logger.info("ai_report_generated", provider="groq", model=model)
                return report.model_dump()

            except (json.JSONDecodeError, Exception) as exc:
                logger.warning(
                    "groq_attempt_failed",
                    attempt=attempt + 1,
                    error=str(exc),
                )
                continue

    except ImportError:
        logger.warning("groq_not_installed")
    except Exception as exc:
        logger.error("groq_error", error=str(exc))

    return None


async def _call_openai(api_key: str, user_prompt: str) -> Optional[dict[str, Any]]:
    """Call OpenAI API for report generation."""
    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=api_key)

        for attempt in range(2):
            try:
                response = await client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": _SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.1,
                    max_tokens=4096,
                )

                content = response.choices[0].message.content
                if not content:
                    continue

                parsed = json.loads(content)
                report = AIReport(**parsed)
                logger.info("ai_report_generated", provider="openai")
                return report.model_dump()

            except (json.JSONDecodeError, Exception) as exc:
                logger.warning(
                    "openai_attempt_failed",
                    attempt=attempt + 1,
                    error=str(exc),
                )
                continue

    except ImportError:
        logger.warning("openai_not_installed")
    except Exception as exc:
        logger.error("openai_error", error=str(exc))

    return None


def _generate_fallback_report(scan_results: dict[str, Any]) -> dict[str, Any]:
    """Generate a basic report from raw scan data when AI is unavailable."""
    all_findings = []

    for scanner_name, scanner_data in scan_results.items():
        if not isinstance(scanner_data, dict):
            continue
        findings = scanner_data.get("findings", [])
        for finding in findings:
            all_findings.append(
                {
                    "title": finding.get("title", "Unknown Finding"),
                    "severity": finding.get("severity", "info"),
                    "owasp_category": finding.get("owasp_category", "Unknown"),
                    "description": finding.get("description", ""),
                    "evidence": finding.get("evidence", ""),
                    "remediation": finding.get("remediation", ""),
                    "cvss_score": finding.get("cvss_score", 0.0),
                    "cwe_id": finding.get("cwe_id", None),
                }
            )

    # Calculate risk score
    severity_weights = {"critical": 25, "high": 15, "medium": 8, "low": 3, "info": 1}
    risk_score = min(
        100,
        sum(severity_weights.get(f.get("severity", "info"), 1) for f in all_findings),
    )

    # Sort by severity
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
    all_findings.sort(key=lambda f: severity_order.get(f.get("severity", "info"), 5))

    total = len(all_findings)
    summary = (
        f"Scan completed with {total} finding(s). "
        f"Risk score: {risk_score}/100. "
        "This report was generated using rule-based analysis (AI unavailable)."
    )

    return {
        "risk_score": risk_score,
        "summary": summary,
        "findings": all_findings,
    }
