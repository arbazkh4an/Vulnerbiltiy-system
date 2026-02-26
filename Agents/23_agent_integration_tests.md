# AGENT 23 — Integration Tests (End-to-End)
**Depends on:** ALL other agents (run last)
**Output goes to:** `tests/integration/`

---

## YOUR JOB
Write end-to-end integration tests that test the ENTIRE pipeline working together. These are not unit tests — they test real component interactions.

---

## TARGET TEST APPLICATION
Use `http://testphp.vulnweb.com` — this is an intentionally vulnerable PHP app run by Acunetix specifically for testing scanners. It is legal and designed to be scanned.

---

## FILES TO CREATE

### `tests/integration/test_full_pipeline.py`

**Setup:**
- Start the full stack with Docker Compose (test uses a test DB)
- All tests use `httpx` async client against `http://localhost:8000`

**Test Suite 1 — API Contract Tests:**
```
test_health_endpoint_returns_ok
test_scan_requires_consent
test_scan_rejects_private_ip
test_scan_rejects_localhost
test_scan_accepts_valid_url
test_scan_returns_scan_id
test_get_nonexistent_scan_returns_404
```

**Test Suite 2 — Scanner Unit Integration:**
(These run real scanners against testphp.vulnweb.com)
```
test_header_scanner_finds_missing_headers
test_ssl_scanner_returns_ssl_data
test_path_scanner_finds_something
test_recon_scanner_detects_php
test_injection_scanner_finds_xss_or_sqli
```
Note: These make REAL HTTP requests. Run with `pytest -m integration` marker.

**Test Suite 3 — Full Scan Pipeline:**
```
test_full_scan_completes_within_120_seconds
test_scan_status_progresses_queued_to_complete
test_websocket_receives_progress_events
test_ai_report_generated_with_findings
test_report_has_valid_owasp_ids
test_risk_score_is_between_0_and_100
```

**Test Suite 4 — Abuse Prevention:**
```
test_rate_limit_blocks_6th_scan_in_hour
test_private_ip_blocked_at_api_level
test_url_with_database_port_blocked
test_concurrent_scans_handled
```

### `tests/integration/conftest.py`
- Pytest fixtures: `api_client`, `test_scan_id`, `completed_scan_id`
- `completed_scan_id` fixture: runs a real scan against testphp.vulnweb.com and waits for completion (cached per test session)

### `tests/integration/test_websocket_integration.py`
- Test: Connect WebSocket → receive progress events → receive complete event
- Test: WebSocket connection to invalid scan_id closes immediately
- Test: Multiple clients on same scan all receive events

### `tests/run_tests.sh`
Shell script:
```bash
# Run unit tests only (no network calls)
pytest scanners/ backend/ queue/ database/ orchestrator/ ai_engine/ -v --tb=short

# Run integration tests (needs Docker + network)
pytest tests/integration/ -v -m integration --tb=short

# Run all tests with coverage
pytest --cov=. --cov-report=html
```

---

## WHAT COUNTS AS PASSING
- Unit tests: 100% pass required
- Integration tests: 90% pass required (some scanner tests may vary with live target)
- Coverage: aim for > 70% overall

---

## PACKAGES NEEDED
```
pytest
pytest-asyncio
pytest-cov
httpx
websockets
```

---

## DONE WHEN
Unit test suite passes 100%. Integration test suite passes against testphp.vulnweb.com.
Return all files in `tests/integration/`.
