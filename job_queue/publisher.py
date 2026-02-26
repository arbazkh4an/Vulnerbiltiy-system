from job_queue.celery_app import celery_app
from job_queue.job_models import ScanJob


@celery_app.task(bind=True, name="scanners.scan")
def scan_task(self, scan_id: str, url: str, created_at: str, priority: int):
    pass


def enqueue_scan(scan_job: ScanJob) -> str:
    task = scan_task.apply_async(
        args=[scan_job.scan_id, scan_job.url, scan_job.created_at, scan_job.priority],
        queue="scan_queue",
    )
    return task.id


def get_job_status(task_id: str) -> dict:
    task = celery_app.AsyncResult(task_id)
    return {
        "state": task.state,
        "result": task.result if task.ready() else None,
        "traceback": task.info if isinstance(task.info, Exception) else None,
    }
