import json
import time
from abc import ABC

import pytest
from unittest.mock import Mock, patch, MagicMock

from scanners.base import BaseScanner
from scanners.result_models import ScannerResult, Finding
from scanners import constants


@pytest.fixture(autouse=True)
def mock_redis():
    with patch("scanners.base.redis_publish_progress") as mock:
        yield mock


class ConcreteScanner(BaseScanner):
    def _run_scan(self) -> dict:
        return {"data": "test", "findings": []}


class FailingScanner(BaseScanner):
    def _run_scan(self) -> dict:
        raise ValueError("Test error")


class SlowScanner(BaseScanner):
    def _run_scan(self) -> dict:
        time.sleep(999)
        return {"data": "slow"}


class TestBaseScannerAbstract:
    def test_base_scanner_cannot_be_instantiated_directly(self):
        with pytest.raises(TypeError):
            BaseScanner("http://example.com", "scan-123")

    def test_concrete_subclass_can_be_instantiated(self):
        scanner = ConcreteScanner("http://example.com", "scan-123")
        assert scanner.url == "http://example.com"
        assert scanner.scan_id == "scan-123"
        assert scanner.host == "example.com"
        assert scanner.scheme == "http"
        assert scanner.path == "/"

    def test_url_parsing_with_port_and_path(self):
        scanner = ConcreteScanner("https://example.com:8443/admin/dashboard", "scan-456")
        assert scanner.scheme == "https"
        assert scanner.host == "example.com"
        assert scanner.port == 8443
        assert scanner.path == "/admin/dashboard"


class TestRunMethod:
    def test_run_returns_scanner_result_with_correct_shape(self):
        scanner = ConcreteScanner("http://example.com", "scan-123")
        result = scanner.run()

        assert isinstance(result, ScannerResult)
        assert result.scanner_name == "ConcreteScanner"
        assert result.scan_id == "scan-123"
        assert result.status == "complete"
        assert isinstance(result.duration_ms, int)
        assert result.duration_ms >= 0
        assert isinstance(result.findings, list)
        assert isinstance(result.raw_data, dict)

    def test_exception_in_run_scan_returns_error_status(self):
        scanner = FailingScanner("http://example.com", "scan-error")
        result = scanner.run()

        assert result.status == "error"
        assert "error" in result.raw_data

    @patch("asyncio.wait_for")
    def test_timeout_fires_correctly(self, mock_wait_for):
        from asyncio import TimeoutError
        mock_wait_for.side_effect = TimeoutError()

        scanner = SlowScanner("http://example.com", "scan-timeout")
        result = scanner.run()

        assert result.status == "timeout"
        assert result.duration_ms > 0


class TestPublishProgress:
    @patch("scanners.base.redis_publish_progress")
    def test_publish_progress_calls_redis(self, mock_redis):
        scanner = ConcreteScanner("http://example.com", "scan-123")
        scanner.publish_progress(50, "Halfway done")

        mock_redis.assert_called_once()
        call_args = mock_redis.call_args
        assert call_args[0][0] == "scan-123"
        assert call_args[0][1] == "ConcreteScanner"
        assert call_args[0][2] == 50
        assert call_args[0][3] == "Halfway done"


class TestHttpMethods:
    @patch("scanners.base.requests.get")
    def test_get_sets_correct_default_headers(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.text = ""
        mock_get.return_value = mock_response

        scanner = ConcreteScanner("http://example.com", "scan-123")
        scanner.get("/test")

        mock_get.assert_called_once()
        call_kwargs = mock_get.call_args[1]
        assert "headers" in call_kwargs
        assert "User-Agent" in call_kwargs["headers"]
        assert call_kwargs["headers"]["User-Agent"] == "VulnScanner/1.0"
        assert call_kwargs["timeout"] == 10
        assert call_kwargs["verify"] is False


class TestScannerResultSerialization:
    def test_scanner_result_serializes_to_dict(self):
        finding = Finding(
            owasp_id="A03:2021",
            title="SQL Injection",
            severity="Critical",
            evidence="Error in response",
            raw={"payload": "' OR '1'='1"},
        )
        result = ScannerResult(
            scanner_name="TestScanner",
            scan_id="scan-123",
            status="complete",
            duration_ms=1500,
            findings=[finding],
            raw_data={"key": "value"},
        )

        result_dict = result.to_dict()

        assert isinstance(result_dict, dict)
        assert result_dict["scanner_name"] == "TestScanner"
        assert result_dict["scan_id"] == "scan-123"
        assert result_dict["status"] == "complete"
        assert result_dict["duration_ms"] == 1500
        assert len(result_dict["findings"]) == 1
        assert result_dict["findings"][0]["owasp_id"] == "A03:2021"

    def test_scanner_result_serializes_to_json(self):
        result = ScannerResult(
            scanner_name="TestScanner",
            scan_id="scan-123",
            status="complete",
            duration_ms=1500,
            findings=[],
            raw_data={"key": "value"},
        )

        json_str = json.dumps(result.to_dict())
        parsed = json.loads(json_str)

        assert parsed["scanner_name"] == "TestScanner"
        assert parsed["scan_id"] == "scan-123"


class TestConstants:
    def test_scanner_timeouts_exists(self):
        assert isinstance(constants.SCANNER_TIMEOUTS, dict)
        assert "default" in constants.SCANNER_TIMEOUTS

    def test_owasp_ids_exists(self):
        assert isinstance(constants.OWASP_IDS, dict)
        assert "sql_injection" in constants.OWASP_IDS
        assert constants.OWASP_IDS["sql_injection"] == "A03:2021"

    def test_common_paths_has_50_items(self):
        assert len(constants.COMMON_PATHS) == 50

    def test_sqli_payloads_has_10_items(self):
        assert len(constants.SQLI_PAYLOADS) == 10

    def test_xss_payloads_has_10_items(self):
        assert len(constants.XSS_PAYLOADS) == 10

    def test_default_credentials_has_10_pairs(self):
        assert len(constants.DEFAULT_CREDENTIALS) == 10
        assert all(isinstance(pair, tuple) and len(pair) == 2 for pair in constants.DEFAULT_CREDENTIALS)

    def test_sensitive_extensions_exists(self):
        assert ".env" in constants.SENSITIVE_EXTENSIONS
        assert ".git" in constants.SENSITIVE_EXTENSIONS
        assert ".bak" in constants.SENSITIVE_EXTENSIONS
        assert ".sql" in constants.SENSITIVE_EXTENSIONS
