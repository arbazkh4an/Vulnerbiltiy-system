# AGENT 06 — Scanner Base Class
**Depends on:** Agent 02 (Redis Queue for progress publishing)
**Output goes to:** `scanners/`

---

## YOUR JOB
Create the base class that ALL scanner modules will inherit from. This ensures every scanner has the same interface, same error handling, same timeout behavior, and same output format.

---

## FILES TO CREATE

### `scanners/base.py`

Abstract base class `BaseScanner`:

**Constructor: `__init__(self, url: str, scan_id: str)`**
- Store url, scan_id
- Parse URL into components (scheme, host, path) using `urllib.parse`
- Initialize logger

**Abstract method: `_run_scan(self) → dict`**
- Subclasses implement this
- Returns raw findings dict

**Public method: `run(self) → ScannerResult`**
- Calls `_run_scan()` wrapped in:
  - Try/except (catch all exceptions, return error result)
  - Timeout enforcement (use `asyncio.wait_for` with per-scanner timeout)
  - Timing measurement (record duration_ms)
  - Progress publishing (publish start + end events via Redis)
- Returns a `ScannerResult` object

**Utility methods available to all subclasses:**
- `self.get(path, **kwargs)` — HTTP GET with default headers, 10s timeout, SSL verify=False
- `self.post(path, data, **kwargs)` — HTTP POST
- `self.publish_progress(percent, message)` — publish to Redis channel
- `self.log(message)` — structured logging with scan_id context

### `scanners/result_models.py`
Dataclasses:

```python
@dataclass
class ScannerResult:
    scanner_name: str
    scan_id: str
    status: str          # "complete" | "error" | "timeout"
    duration_ms: int
    findings: list       # list of Finding objects
    raw_data: dict       # everything collected, unprocessed

@dataclass
class Finding:
    owasp_id: str        # e.g. "A05:2021"
    title: str
    severity: str        # "Critical"|"High"|"Medium"|"Low"|"Info"
    evidence: str
    raw: dict            # raw data that produced this finding
```

### `scanners/constants.py`
- Dict `SCANNER_TIMEOUTS` mapping scanner name → seconds
- Dict `OWASP_IDS` mapping short names to full OWASP IDs
- List `COMMON_PATHS` — 50 common sensitive paths to probe
- List `SQLI_PAYLOADS` — 10 basic SQL injection test strings
- List `XSS_PAYLOADS` — 10 basic XSS test strings
- List `DEFAULT_CREDENTIALS` — 10 common username/password pairs
- List `SENSITIVE_EXTENSIONS` — .env, .git, .bak, .sql, .zip, .config, etc.

---

## TESTS TO WRITE
File: `scanners/test_base.py`

- Test: BaseScanner cannot be instantiated directly (abstract)
- Test: Concrete subclass with `_run_scan` can be instantiated
- Test: `run()` returns ScannerResult with correct shape
- Test: Exception in `_run_scan` returns status="error", not crash
- Test: Timeout works — mock `_run_scan` to sleep 999s, confirm timeout fires
- Test: `publish_progress` calls Redis correctly (mock Redis)
- Test: `self.get()` sets correct default headers
- Test: ScannerResult serializes to dict/JSON cleanly

---

## PACKAGES NEEDED
```
requests
aiohttp
redis
pytest
pytest-asyncio
pytest-mock
```

---

## DONE WHEN
All 8 tests pass. This is the foundation — get it right because every other scanner depends on it.
Return `scanners/base.py`, `scanners/result_models.py`, `scanners/constants.py`.
