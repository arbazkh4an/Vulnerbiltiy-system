# AGENT 07 — Header Scanner
**Depends on:** Agent 06 (BaseScanner)
**Output goes to:** `scanners/header_scanner.py`
**OWASP Coverage:** A05:2021 Security Misconfiguration

---

## YOUR JOB
Build the HTTP security header scanner. This is the simplest scanner — one HTTP request, analyze the response headers.

---

## FILES TO CREATE

### `scanners/header_scanner.py`

Class `HeaderScanner(BaseScanner)`:

**Implement `_run_scan()`:**

1. Make a single GET request to the target URL
2. Capture ALL response headers
3. Check for presence/absence/value of these security headers:

| Header | Check | Severity if missing/wrong |
|---|---|---|
| `Strict-Transport-Security` | Present + max-age >= 31536000 | High |
| `Content-Security-Policy` | Present and not just "unsafe-inline" | High |
| `X-Frame-Options` | DENY or SAMEORIGIN | Medium |
| `X-Content-Type-Options` | Must be "nosniff" | Medium |
| `Referrer-Policy` | Present | Low |
| `Permissions-Policy` | Present | Low |
| `Server` | Should NOT reveal version (e.g. "Apache/2.4.29") | Medium |
| `X-Powered-By` | Should NOT be present | Medium |
| `Access-Control-Allow-Origin` | Should NOT be `*` on non-public APIs | Medium |

4. Also check:
   - Is HTTP redirecting to HTTPS?
   - Response status code
   - Response time

5. Return raw_data with: full header dict, redirect chain, status code, response_time_ms

6. For each issue found, create a `Finding` object with:
   - owasp_id = "A05:2021"
   - title = descriptive title
   - severity = from table above
   - evidence = exact header value or "header not present"

---

## TESTS TO WRITE
File: `scanners/test_header_scanner.py`

Use `responses` library to mock HTTP calls.

- Test: Site with all headers correct → 0 findings
- Test: Site missing HSTS → 1 High finding
- Test: Site with `Server: Apache/2.4.29` → 1 Medium finding
- Test: Site with `Access-Control-Allow-Origin: *` → 1 Medium finding
- Test: Site with `X-Powered-By: PHP/7.2` → finding created
- Test: Site redirecting HTTP→HTTPS correctly → no redirect finding
- Test: Unreachable site → status="error", no crash
- Test: Output matches ScannerResult schema exactly

---

## PACKAGES NEEDED
```
requests
responses  # for mocking
pytest
```

---

## DONE WHEN
All 8 tests pass. Scanner runs in under 5 seconds. Returns proper ScannerResult.
Return `scanners/header_scanner.py` and `scanners/test_header_scanner.py`.
