# AGENT 14 — Injection Scanner (SQLi + XSS)
**Depends on:** Agent 06 (BaseScanner + constants.py payloads)
**Output goes to:** `scanners/injection_scanner.py`
**OWASP Coverage:** A03:2021 Injection

---

## YOUR JOB
Find forms and URL parameters on the target, then test them with injection payloads. Detect reflected XSS and error-based SQL injection.

---

## FILES TO CREATE

### `scanners/injection_scanner.py`

Class `InjectionScanner(BaseScanner)`:

**Implement `_run_scan()`:**

**Step 1 — Crawl for input points:**
- Fetch homepage HTML
- Use BeautifulSoup to find:
  - All `<form>` elements: extract action URL, method (GET/POST), all input field names
  - All URL parameters in links: `<a href="/search?q=test">` → extract param `q`
- Limit: max 5 forms, max 10 URL parameters (don't crawl whole site)

**Step 2 — XSS Testing (Reflected):**
For each input point, inject these payloads one at a time:
```
<script>alert('XSS')</script>
"><img src=x onerror=alert(1)>
javascript:alert(1)
<svg onload=alert(1)>
```
- Submit form / request URL with each payload as the input value
- Check if the EXACT payload appears unencoded in the response HTML
- If `<script>alert` appears verbatim in response → High XSS finding
- If HTML-encoded version appears (`&lt;script&gt;`) → NOT vulnerable

**Step 3 — SQL Injection Testing (Error-based):**
For each input point, inject:
```
'
''
`
')
"))
1' OR '1'='1
1; DROP TABLE--
```
- Submit and check response for SQL error signatures:
  - MySQL: `You have an error in your SQL syntax`, `mysql_fetch`
  - PostgreSQL: `syntax error at or near`, `pg_query`
  - MSSQL: `Unclosed quotation mark`, `OLE DB`
  - SQLite: `SQLite3::query`, `SQLITE_ERROR`
- If any error signature found → Critical SQLi finding

**Step 4 — Build findings:**
- Reflected XSS confirmed → High (A03), include: param name, payload, URL
- SQLi error confirmed → Critical (A03), include: param name, payload, error excerpt
- Input found but no injection detected → Info (found X testable inputs)

**raw_data:**
```python
{
  "forms_found": 2,
  "url_params_found": 3,
  "total_inputs_tested": 5,
  "payloads_sent": 35,
  "xss_findings": [...],
  "sqli_findings": [...],
  "requests_sent": 35
}
```

---

## TESTS TO WRITE
File: `scanners/test_injection_scanner.py`

- Test: Form with input that reflects XSS payload unencoded → High finding
- Test: Form that HTML-encodes output → NOT flagged as XSS
- Test: URL param that returns MySQL error → Critical SQLi finding
- Test: Clean site → 0 injection findings
- Test: No forms found → 0 findings, no crash
- Test: Form fields correctly extracted from HTML
- Test: Max limits respected (not more than 5 forms)
- Test: Total request count doesn't exceed expected maximum

---

## ⚠️ ETHICAL LIMITS
- Never test more than 5 forms or 10 URL params
- Max 50 total HTTP requests
- 0.5 second delay between each injection request
- Only test inputs found on the homepage (no deep crawling)

---

## PACKAGES NEEDED
```
requests
beautifulsoup4
pytest
responses
```

---

## DONE WHEN
All 8 tests pass. This is the most sensitive scanner — test it carefully.
Return both files.
