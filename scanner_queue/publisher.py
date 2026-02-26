"""
OWASP AI Scanner - Job Publisher
Functions to enqueue scan jobs and check status
"""

from typing import Any, Dict, Optional

from celery import group, signature
from celery.result import AsyncResult

from queue.celery_app import celery_app
from queue.job_models import ScanJob


# Celery task signatures for scanning
SCAN_TASK_NAME = "scanners.run_scan"


def enqueue_scan(scan_job: ScanJob) -> str:
    """
    Push a scan job to the scan_queue.
    
    Args:
        scan_job: The ScanJob to enqueue
        
    Returns:
        str: Celery task ID
    """
    task = celery_app.send_task(
        SCAN_TASK_NAME,
        args=[scan_job.to_dict()],
        queue="scan_queue",
        priority=scan_job.priority,
    )
    return task.id


def enqueue_scanners(scan_job: ScanJob) -> list[str]:
    """
    Enqueue all individual scanner tasks for a scan.
    
    Args:
        scan_job: The ScanJob to enqueue scanners for
        
    Returns:
        list[str]: List of Celery task IDs
    """
    scanner_tasks = [
        "scanners.header_scan",
        "scanners.ssl_scan",
        "scanners.recon_scan",
        "scanners.sri_scan",
        "scanners.path_scan",
        "scanners.auth_scan",
        "scanners.cve_scan",
        "scanners.injection_scan",
    ]
    
    task_ids = []
    for task_name in scanner_tasks:
        task = celery_app.send_task(
            task_name,
            args=[scan_job.to_dict()],
            queue="scan_queue",
            priority=scan_job.priority,
        )
        task_ids.append(task.id)
    
    return task_ids


def enqueue_ai_analysis(scan_id: str) -> str:
    """
    Enqueue AI analysis task after scanners complete.
    
    Args:
        scan_id: The scan ID to analyze
        
    Returns:
        str: Celery task ID
    """
    task = celery_app.send_task(
        "ai.analyze_results",
        args=[scan_id],
        queue="ai_queue",
    )
    return task.id


def get_job_status(task_id: str) -> Dict[str, Any]:
    """
    Get the status of a Celery task.
    
    Args:
        task_id: The Celery task ID
        
    Returns:
        dict: Status information with keys:
            - state: Task state (PENDING, STARTED, SUCCESS, FAILURE, etc.)
            - result: Task result if available
            - traceback: Error traceback if failed
    """
    result = AsyncResult(task_id, app=celery_app)
    
    status = {
        "state": result.state,
        "result": None,
        "traceback": None,
    }
    
    if result.ready():
        if result.successful():
            status["result"] = result.result
        elif result.failed():
            status["traceback"] = result.traceback
    
    return status


def revoke_task(task_id: str, terminate: bool = False) -> bool:
    """
    Revoke (cancel) a running task.
    
    Args:
        task_id: The task ID to revoke
        terminate: If True, forcefully terminate the task
        
    Returns:
        bool: True if revoked successfully
    """
    celery_app.control.revoke(task_id, terminate=terminate)
    return True
