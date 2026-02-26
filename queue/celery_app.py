from celery import Celery

celery_app = Celery(
    "vuln_scanner",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
)

celery_app.conf.update(
    task_serializer="json",
    result_expires=3600,
    task_routes={
        "scanners.*": {"queue": "scan_queue"},
        "ai.*": {"queue": "ai_queue"},
    },
)
