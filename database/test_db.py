"""
OWASP AI Scanner - Database Tests
Pytest tests for the database connection layer
"""

import json
import pytest
import pytest_asyncio

# Import the database module
import db


# Test constants
TEST_URL = "https://example.com"
TEST_USER_IP = "192.168.1.1"
TEST_CONSENT = True


@pytest_asyncio.fixture
async def setup_db():
    """
    Setup fixture that initializes the database pool.
    This fixture runs once per test session.
    """
    # Initialize the database pool
    await db.init_db_pool()
    yield
    # Cleanup: close the pool after all tests
    await db.close_db_pool()


@pytest.mark.asyncio
async def test_connect_to_db(setup_db):
    """
    Test: Connect to DB successfully
    Verifies that the database connection pool is initialized and working.
    """
    is_healthy = await db.health_check()
    assert is_healthy is True, "Database connection should be healthy"


@pytest.mark.asyncio
async def test_create_and_read_scan(setup_db):
    """
    Test: Create a scan row, read it back, confirm fields match
    Verifies that creating a scan stores the correct data.
    """
    # Create a scan
    scan_id = await db.create_scan(TEST_URL, TEST_USER_IP, TEST_CONSENT)

    # Read it back
    scan = await db.get_scan(scan_id)

    # Verify fields
    assert scan is not None, "Scan should be found"
    assert scan["id"] == scan_id, "Scan ID should match"
    assert scan["url"] == TEST_URL, "URL should match"
    assert scan["status"] == "queued", "Status should be queued"
    assert scan["user_ip"] == TEST_USER_IP, "User IP should match"
    assert scan["consent_confirmed"] is True, "Consent should be confirmed"
    assert scan["created_at"] is not None, "Created at should be set"
    assert scan["completed_at"] is None, "Completed at should be None for queued scan"

@pytest.mark.asyncio
async def test_update_scan_status(setup_db):
    """
    Test: Update scan status from "queued" to "scanning"
    Verifies that status updates work correctly.
    """
    # Create a scan
    scan_id = await db.create_scan(TEST_URL, TEST_USER_IP, TEST_CONSENT)

    # Verify initial status
    scan = await db.get_scan(scan_id)
    assert scan["status"] == "queued", "Initial status should be queued"

    # Update status to scanning
    await db.update_scan_status(scan_id, "scanning")

    # Verify updated status
    scan = await db.get_scan(scan_id)
    assert scan["status"] == "scanning", "Status should be updated to scanning"
    assert scan["completed_at"] is None, "Completed at should still be None"

    # Update to complete and verify completed_at is set
    await db.update_scan_status(scan_id, "complete")
    scan = await db.get_scan(scan_id)
    assert scan["status"] == "complete", "Status should be complete"
    assert scan["completed_at"] is not None, "Completed at should be set"

@pytest.mark.asyncio
async def test_save_scanner_result_jsonb(setup_db):
    """
    Test: Save a scanner result, confirm JSONB stored correctly
    Verifies that JSONB data is stored and retrieved properly.
    """
    # Create a scan
    scan_id = await db.create_scan(TEST_URL, TEST_USER_IP, TEST_CONSENT)

    # Scanner result data
    scanner_name = "header_scanner"
    raw_json = {
        "headers": {
            "X-Frame-Options": "DENY",
            "X-Content-Type-Options": "nosniff",
            "Strict-Transport-Security": "max-age=31536000"
        },
        "issues": [
            {
                "severity": "high",
                "message": "Missing Content-Security-Policy header"
            }
        ]
    }
    duration_ms = 1250

    # Save the scanner result
    result_id = await db.save_scanner_result(scan_id, scanner_name, raw_json, duration_ms)

    # Verify result was created
    assert result_id is not None, "Result ID should be returned"

    # Get the scan with results
    scan = await db.get_scan_with_results(scan_id)

    # Verify the result data
    assert len(scan["results"]) == 1, "Should have one result"
    result = scan["results"][0]

    assert result["scanner_name"] == scanner_name, "Scanner name should match"
    assert result["duration_ms"] == duration_ms, "Duration should match"

    # Verify JSONB was stored correctly (should be a dict when retrieved)
    assert isinstance(result["raw_json"], dict), "raw_json should be a dict (JSONB parsed)"
    assert result["raw_json"]["headers"]["X-Frame-Options"] == "DENY", "JSONB data should match"

@pytest.mark.asyncio
async def test_save_and_read_ai_report(setup_db):
    """
    Test: Save AI report, read it back
    Verifies that AI reports are stored and retrieved correctly.
    """
    # Create a scan
    scan_id = await db.create_scan(TEST_URL, TEST_USER_IP, TEST_CONSENT)

    # AI report data
    risk_score = 75
    summary = "Multiple security vulnerabilities detected including missing security headers"
    findings_json = {
        "findings": [
            {
                "category": "Security Headers",
                "severity": "high",
                "description": "Content-Security-Policy header is missing",
                "recommendation": "Add Content-Security-Policy header to prevent XSS attacks"
            },
            {
                "category": "SSL/TLS",
                "severity": "medium",
                "description": "SSL certificate could not be verified",
                "recommendation": "Ensure valid SSL certificate is installed"
            }
        ],
        "cvss_score": 7.5
    }

    # Save the AI report
    report_id = await db.save_ai_report(scan_id, risk_score, summary, findings_json)

    # Verify report was created
    assert report_id is not None, "Report ID should be returned"

    # Get the scan with results
    scan = await db.get_scan_with_results(scan_id)

    # Verify the report data
    assert scan["report"] is not None, "Report should exist"
    report = scan["report"]

    assert report["risk_score"] == risk_score, "Risk score should match"
    assert report["summary"] == summary, "Summary should match"

    # Verify JSONB was stored correctly
    assert isinstance(report["findings_json"], dict), "findings_json should be a dict"
    assert len(report["findings_json"]["findings"]) == 2, "Should have two findings"

@pytest.mark.asyncio
async def test_get_scan_with_results_nested_data(setup_db):
    """
    Test: get_scan_with_results returns nested data correctly
    Verifies that the full scan data with results and report is returned properly.
    """
    # Create a scan
    scan_id = await db.create_scan(TEST_URL, TEST_USER_IP, TEST_CONSENT)

    # Add multiple scanner results
    await db.save_scanner_result(
        scan_id,
        "header_scanner",
        {"headers": {"X-Frame-Options": "DENY"}},
        500
    )
    await db.save_scanner_result(
        scan_id,
        "ssl_scanner",
        {"ssl_grade": "A", "issues": []},
        1200
    )

    # Add AI report
    await db.save_ai_report(
        scan_id,
        60,
        "Medium risk vulnerabilities found",
        {"findings": [], "cvss_score": 5.0}
    )

    # Get full scan data
    scan = await db.get_scan_with_results(scan_id)

    # Verify structure
    assert scan is not None, "Scan should be found"
    assert scan["id"] == scan_id, "Scan ID should match"
    assert scan["url"] == TEST_URL, "URL should match"

    # Verify results array
    assert "results" in scan, "Results should be in scan data"
    assert len(scan["results"]) == 2, "Should have 2 results"

    # Verify each result has expected fields
    for result in scan["results"]:
        assert "id" in result, "Result should have ID"
        assert "scanner_name" in result, "Result should have scanner_name"
        assert "raw_json" in result, "Result should have raw_json"
        assert "duration_ms" in result, "Result should have duration_ms"

    # Verify report
    assert scan["report"] is not None, "Report should exist"
    assert scan["report"]["risk_score"] == 60, "Risk score should match"
    assert isinstance(scan["report"]["findings_json"], dict), "Findings should be parsed JSON"
