"""
OWASP AI Scanner - Celery Application
Redis-backed job queue for scan workers
"""

from celery import Celery

# Celery configuration
CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/1"

# Create Celery app
celery_app = Celery(
    "owasp_scanner",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    result_expires=3600,
    task_track_started=True,
    task_routes={
        "scanners.*": {"queue": "scan_queue"},
        "ai.*": {"queue": "ai_queue"},
    },
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["queue"])
