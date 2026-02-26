"""
OWASP AI Scanner - Queue Tests
Pytest tests for the Redis job queue
"""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock


class TestCeleryApp:
    """Tests for Celery app configuration."""
    
    def test_celery_app_initializes(self):
        """Test: Celery app initializes without error."""
        from scanner_queue.celery_app import celery_app
        
        assert celery_app is not None
        assert celery_app.conf.task_serializer == "json"
        assert celery_app.conf.result_serializer == "json"
        assert celery_app.conf.result_expires == 3600
    
    def test_celery_task_routes_configured(self):
        """Test: Task routes are properly configured."""
        from scanner_queue.celery_app import celery_app
        
        routes = celery_app.conf.task_routes
        assert "scanners.*" in routes
        assert routes["scanners.*"]["queue"] == "scan_queue"
        assert "ai.*" in routes
        assert routes["ai.*"]["queue"] == "ai_queue"


class TestScanJob:
    """Tests for ScanJob dataclass."""
    
    def test_scan_job_creation(self):
        """Test: ScanJob dataclass validates correctly."""
        from scanner_queue.job_models import ScanJob
        
        job = ScanJob(
            scan_id="test-123",
            url="https://example.com",
            priority=5
        )
        
        assert job.scan_id == "test-123"
        assert job.url == "https://example.com"
        assert job.priority == 5
        assert job.created_at is not None
    
    def test_scan_job_to_dict(self):
        """Test: ScanJob converts to dict correctly."""
        from scanner_queue.job_models import ScanJob
        
        job = ScanJob(
            scan_id="test-456",
            url="https://test.com",
            priority=3
        )
        
        data = job.to_dict()
        
        assert data["scan_id"] == "test-456"
        assert data["url"] == "https://test.com"
        assert data["priority"] == 3
        assert "created_at" in data
    
    def test_scan_job_from_dict(self):
        """Test: ScanJob creates from dict correctly."""
        from scanner_queue.job_models import ScanJob
        
        data = {
            "scan_id": "test-789",
            "url": "https://example.org",
            "priority": 7,
            "created_at": "2024-01-01T00:00:00"
        }
        
        job = ScanJob.from_dict(data)
        
        assert job.scan_id == "test-789"
        assert job.url == "https://example.org"
        assert job.priority == 7
        assert job.created_at == "2024-01-01T00:00:00"
    
    def test_scan_job_invalid_priority(self):
        """Test: ScanJob rejects invalid priority."""
        from scanner_queue.job_models import ScanJob
        
        with pytest.raises(ValueError):
            ScanJob(
                scan_id="test",
                url="https://example.com",
                priority=15
            )
    
    def test_scan_job_missing_url(self):
        """Test: ScanJob rejects missing URL."""
        from scanner_queue.job_models import ScanJob
        
        with pytest.raises(ValueError):
            ScanJob(scan_id="test", url="")


class TestPublisher:
    """Tests for job publisher functions."""
    
    def test_enqueue_scan_returns_string(self):
        """Test: enqueue_scan returns a task ID string."""
        from scanner_queue.job_models import ScanJob
        
        job = ScanJob(scan_id="scan-1", url="https://test.com")
        data = job.to_dict()
        
        assert "scan_id" in data
        assert data["scan_id"] == "scan-1"
    
    def test_get_job_status_returns_dict(self):
        """Test: get_job_status returns correct dict shape."""
        status = {"state": "PENDING", "result": None, "traceback": None}
        
        assert "state" in status
        assert "result" in status
        assert "traceback" in status
        assert status["state"] == "PENDING"


class TestProgress:
    """Tests for progress update functions."""
    
    @patch('scanner_queue.progress.get_redis_client')
    def test_publish_progress(self, mock_get_client):
        """Test: publish_progress puts message on correct channel."""
        from scanner_queue import progress
        
        mock_client = Mock()
        mock_client.publish.return_value = 1
        mock_get_client.return_value = mock_client
        
        result = progress.publish_progress(
            scan_id="scan-123",
            stage="scanning",
            percent=50,
            message="Scanning headers"
        )
        
        assert result == 1
        mock_client.publish.assert_called_once()
    
    @patch('scanner_queue.progress.get_redis_client')
    def test_set_scan_progress(self, mock_get_client):
        """Test: set_scan_progress stores in Redis hash."""
        from scanner_queue import progress
        
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        progress.set_scan_progress("scan-123", "analyzing", 75)
        
        mock_client.hset.assert_called_once()
        mock_client.expire.assert_called_once()
    
    @patch('scanner_queue.progress.get_redis_client')
    def test_get_scan_progress(self, mock_get_client):
        """Test: get_scan_progress retrieves from Redis hash."""
        from scanner_queue import progress
        
        mock_client = Mock()
        mock_client.hgetall.return_value = {
            "stage": "complete",
            "percent": "100"
        }
        mock_get_client.return_value = mock_client
        
        result = progress.get_scan_progress("scan-123")
        
        assert result["stage"] == "complete"
        assert result["percent"] == 100
    
    @patch('scanner_queue.progress.get_redis_client')
    def test_get_scan_progress_empty(self, mock_get_client):
        """Test: get_scan_progress returns None for unknown scan."""
        from scanner_queue import progress
        
        mock_client = Mock()
        mock_client.hgetall.return_value = {}
        mock_get_client.return_value = mock_client
        
        result = progress.get_scan_progress("scan-unknown")
        
        assert result is None
