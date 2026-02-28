"""
SentinelAI — Scanner Contract Tests
Verifies that all scanners conform to the BaseScanner output contract.
"""

import pytest

from app.scanners.header_scanner import HeaderScanner
from app.scanners.ssl_scanner import SSLScanner
from app.scanners.path_scanner import PathScanner
from app.scanners.cve_scanner import CVEScanner


def _validate_scanner_output(result: dict) -> None:
    """Assert the scanner output matches the expected contract."""
    assert "scanner" in result, "Missing 'scanner' key"
    assert "findings" in result, "Missing 'findings' key"
    assert "error" in result, "Missing 'error' key"
    assert isinstance(result["findings"], list), "'findings' must be a list"

    for finding in result["findings"]:
        assert "title" in finding, "Finding missing 'title'"
        assert "severity" in finding, "Finding missing 'severity'"
        assert finding["severity"] in (
            "critical", "high", "medium", "low", "info"
        ), f"Invalid severity: {finding['severity']}"
        assert "description" in finding, "Finding missing 'description'"
        assert "remediation" in finding, "Finding missing 'remediation'"


@pytest.mark.asyncio
async def test_header_scanner_contract():
    scanner = HeaderScanner()
    result = await scanner.run("https://example.com")
    _validate_scanner_output(result)
    assert result["scanner"] == "header_scanner"


@pytest.mark.asyncio
async def test_ssl_scanner_contract():
    scanner = SSLScanner()
    result = await scanner.run("https://example.com")
    _validate_scanner_output(result)
    assert result["scanner"] == "ssl_scanner"


@pytest.mark.asyncio
async def test_path_scanner_contract():
    scanner = PathScanner()
    result = await scanner.run("https://example.com")
    _validate_scanner_output(result)
    assert result["scanner"] == "path_scanner"


@pytest.mark.asyncio
async def test_cve_scanner_contract():
    scanner = CVEScanner()
    result = await scanner.run("https://example.com")
    _validate_scanner_output(result)
    assert result["scanner"] == "cve_scanner"


@pytest.mark.asyncio
async def test_header_scanner_handles_invalid_url():
    scanner = HeaderScanner()
    result = await scanner.run("https://this-domain-does-not-exist-12345.invalid")
    _validate_scanner_output(result)
    # Should have an error but not crash
    assert result["error"] is not None or result["findings"] == []


@pytest.mark.asyncio
async def test_ssl_scanner_http_url():
    """SSL scanner should flag HTTP-only URLs."""
    scanner = SSLScanner()
    result = await scanner.run("http://example.com")
    _validate_scanner_output(result)
    # Should have at least one finding about missing HTTPS
    assert any("HTTPS" in f.get("title", "") or "HTTP" in f.get("title", "") for f in result["findings"])


@pytest.mark.asyncio
async def test_path_scanner_handles_timeout():
    """Path scanner should not crash on unreachable hosts."""
    scanner = PathScanner()
    result = await scanner.run("https://10.255.255.1:12345")
    _validate_scanner_output(result)
