"""
SentinelAI — Background Worker
Standalone async worker that polls the database for queued scans
and processes them through the scanner pipeline.

Run with: python -m app.worker.worker
"""

import asyncio
import signal
import sys
from pathlib import Path

# Ensure the backend directory is in the path when run as a module
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.config import get_settings
from app.db.repositories import get_queued_scan, mark_scan_failed
from app.db.session import close_pool, create_pool
from app.logging import get_logger, setup_logging
from app.services.scan_service import process_scan

logger = get_logger(__name__)

_shutdown = False


def _handle_signal(signum: int, frame) -> None:
    """Handle shutdown signals gracefully."""
    global _shutdown
    logger.info("shutdown_signal_received", signal=signum)
    _shutdown = True


async def main() -> None:
    """Main worker loop."""
    global _shutdown

    settings = get_settings()
    setup_logging(settings.LOG_LEVEL)

    logger.info(
        "worker_starting",
        poll_interval=settings.WORKER_POLL_INTERVAL,
    )

    # Initialize database
    pool = await create_pool()

    # Register signal handlers
    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    logger.info("worker_ready")

    while not _shutdown:
        try:
            job = await get_queued_scan(pool)

            if job:
                scan_id = job["id"]
                url = job["target_url"]

                logger.info("worker_processing", scan_id=scan_id, url=url)

                try:
                    await process_scan(pool, scan_id, url)
                except Exception as exc:
                    logger.error(
                        "worker_scan_failed",
                        scan_id=scan_id,
                        error=str(exc),
                    )
                    await mark_scan_failed(
                        pool, scan_id, f"Worker error: {str(exc)[:500]}"
                    )
            else:
                # No jobs — wait before polling again
                await asyncio.sleep(settings.WORKER_POLL_INTERVAL)

        except Exception as exc:
            logger.error("worker_loop_error", error=str(exc))
            await asyncio.sleep(settings.WORKER_POLL_INTERVAL)

    # Graceful shutdown
    logger.info("worker_shutting_down")
    await close_pool()
    logger.info("worker_stopped")


if __name__ == "__main__":
    asyncio.run(main())
