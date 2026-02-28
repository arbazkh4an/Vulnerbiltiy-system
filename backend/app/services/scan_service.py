"""
SentinelAI — Scan Orchestration Service
Coordinates scanner execution and result processing.
"""

import asyncio
from typing import Any

from asyncpg import Pool

from app.db import repositories as repo
from app.logging import get_logger
from app.scanners.cve_scanner import CVEScanner
from app.scanners.header_scanner import HeaderScanner
from app.scanners.path_scanner import PathScanner
from app.scanners.ssl_scanner import SSLScanner
from app.services.ai_service import generate_ai_report

logger = get_logger(__name__)

# Scanner instances
_scanners = [
    HeaderScanner(),
    SSLScanner(),
    PathScanner(),
    CVEScanner(),
]


async def run_all_scanners(url: str) -> dict[str, Any]:
    """
    Execute all scanners concurrently against the target URL.

    Returns a merged dict keyed by scanner name.
    Individual scanner failures are captured in their error field,
    and do not prevent other scanners from completing.
    """
    tasks = [scanner.run(url) for scanner in _scanners]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    merged: dict[str, Any] = {}
    for scanner, result in zip(_scanners, results):
        if isinstance(result, Exception):
            logger.error(
                "scanner_exception",
                scanner=scanner.name,
                error=str(result),
            )
            merged[scanner.name] = {
                "scanner": scanner.name,
                "findings": [],
                "error": str(result),
            }
        else:
            merged[scanner.name] = result

    return merged


async def process_scan(pool: Pool, scan_id: str, url: str) -> None:
    """
    Full scan pipeline:
    1. Mark as running
    2. Run all scanners
    3. Store raw results
    4. Generate AI report
    5. Store AI report
    6. Update vulnerability counts
    7. Mark as complete
    """
    logger.info("scan_started", scan_id=scan_id, url=url)

    # Mark running
    await repo.update_status(pool, scan_id, "running", progress=10)

    # Run scanners
    try:
        raw_results = await run_all_scanners(url)
    except Exception as exc:
        logger.error("all_scanners_failed", scan_id=scan_id, error=str(exc))
        await repo.mark_scan_failed(pool, scan_id, f"Scanner engine failure: {str(exc)}")
        return

    await repo.update_status(pool, scan_id, "running", progress=50)

    # Store raw results
    await repo.store_raw_results(pool, scan_id, raw_results)
    await repo.update_status(pool, scan_id, "running", progress=60)

    # Generate AI report
    try:
        ai_report = await generate_ai_report(raw_results, url)
    except Exception as exc:
        logger.error("ai_report_failed", scan_id=scan_id, error=str(exc))
        # Store raw results without AI report and mark complete anyway
        ai_report = {
            "risk_score": 0,
            "summary": f"AI analysis failed: {str(exc)[:200]}. Raw scan data is available.",
            "findings": [],
        }

    await repo.update_status(pool, scan_id, "running", progress=80)

    # Store AI report
    await repo.store_ai_report(pool, scan_id, ai_report)

    # Count vulnerabilities by severity
    findings = ai_report.get("findings", [])
    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for finding in findings:
        sev = finding.get("severity", "info")
        if sev in counts:
            counts[sev] += 1

    total = sum(counts.values())
    await repo.update_scan_counts(
        pool,
        scan_id,
        total=total,
        critical=counts["critical"],
        high=counts["high"],
        medium=counts["medium"],
        low=counts["low"],
    )

    # Mark complete
    await repo.update_status(pool, scan_id, "complete", progress=100)
    logger.info(
        "scan_completed",
        scan_id=scan_id,
        url=url,
        total_findings=total,
        risk_score=ai_report.get("risk_score", 0),
    )
