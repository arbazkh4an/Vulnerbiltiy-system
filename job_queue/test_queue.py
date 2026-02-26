import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from job_queue.celery_app import celery_app
from job_queue.job_models import ScanJob
from job_queue import publisher
from job_queue import progress


class TestCeleryApp:
    def test_celery_app_initializes_without_error(self):
        assert celery_app is not None
        assert celery_app.conf.task_serializer == "json"
        assert celery_app.conf.result_expires == 3600
        assert "scanners.*" in celery_app.conf.task_routes
        assert "ai.*" in celery_app.conf.task_routes


class TestScanJob:
    def test_scan_job_dataclass_validates_correctly(self):
        job = ScanJob(scan_id="test-123", url="https://example.com", priority=3)
        assert job.scan_id == "test-123"
        assert job.url == "https://example.com"
        assert job.priority == 3
        assert job.created_at is not None

    def test_scan_job_default_priority(self):
        job = ScanJob(scan_id="test-456", url="https://test.com")
        assert job.priority == 5


class TestPublisher:
    @patch.object(publisher.scan_task, "apply_async")
    def test_enqueue_scan_pushes_to_queue(self, mock_apply):
        mock_task = MagicMock()
        mock_task.id = "task-abc-123"
        mock_apply.return_value = mock_task

        job = ScanJob(scan_id="scan-001", url="https://example.com")
        task_id = publisher.enqueue_scan(job)

        mock_apply.assert_called_once()
        assert task_id == "task-abc-123"
        call_args = mock_apply.call_args
        assert call_args.kwargs["queue"] == "scan_queue"

    @patch("job_queue.publisher.celery_app")
    def test_get_job_status_returns_correct_shape(self, mock_celery):
        mock_task = MagicMock()
        mock_task.state = "SUCCESS"
        mock_task.result = {"status": "completed"}
        mock_task.ready.return_value = True
        mock_task.info = None
        mock_celery.AsyncResult.return_value = mock_task

        result = publisher.get_job_status("task-123")

        assert "state" in result
        assert "result" in result
        assert "traceback" in result
        assert result["state"] == "SUCCESS"


class TestProgress:
    @patch("job_queue.progress._get_redis_client")
    def test_publish_progress_puts_message_on_correct_channel(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        progress.publish_progress("scan-999", "scanning", 50, "Checking endpoints")

        mock_client.publish.assert_called_once()
        call_args = mock_client.publish.call_args
        assert call_args[0][0] == "scan_progress:scan-999"
        payload = json.loads(call_args[0][1])
        assert payload["stage"] == "scanning"
        assert payload["percent"] == 50
        assert payload["message"] == "Checking endpoints"

    @patch("job_queue.progress._get_redis_client")
    def test_subscribe_progress_receives_published_messages(self, mock_get_client):
        mock_client = MagicMock()
        mock_pubsub = MagicMock()

        test_message = {
            "type": "message",
            "data": json.dumps({"stage": "complete", "percent": 100, "message": "Done"})
        }
        mock_pubsub.listen.return_value = iter([test_message])
        mock_client.pubsub.return_value = mock_pubsub
        mock_get_client.return_value = mock_client

        gen = progress.subscribe_progress("scan-123")
        messages = list(gen)

        mock_client.pubsub.assert_called_once()
        mock_pubsub.subscribe.assert_called_with("scan_progress:scan-123")
        assert len(messages) == 1
        assert messages[0]["stage"] == "complete"
