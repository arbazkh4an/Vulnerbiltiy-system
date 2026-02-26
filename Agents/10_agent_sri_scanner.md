# AGENT 10 — SRI Scanner (Subresource Integrity)
**Depends on:** Agent 06 (BaseScanner)
**Output goes to:** `scanners/sri_scanner.py`
**OWASP Coverage:** A08:2021 Software & Data Integrity Failures

---

## YOUR JOB
Find all external JavaScript and CSS resources loaded by the page that are missing Subresource Integrity (SRI) attributes. A missing `integrity=` attribute means if the CDN is compromised, malicious code runs on users.

---

## FILES TO CREATE

### `scanners/sri_scanner.py`

Class `SriScanner(BaseScanner)`:

**Implement `_run_scan()`:**

1. Fetch the homepage HTML using `requests`
2. Parse with `BeautifulSoup`
3. Find ALL `<script src="...">` tags
4. Find ALL `<link rel="stylesheet" href="...">` tags
5. For each resource:
   - Is it external? (src starts with http/https or `//`)
   - Does it have an `integrity` attribute?
   - Does it have a `crossorigin` attribute? (required when integrity is present)
6. Build list of violations: external resources missing `integrity`
7. Also check inline scripts for suspicious patterns:
   - `eval(` usage → Medium finding
   - `document.write(` usage → Low finding
   - `innerHTML =` with unescaped variable → Low finding

**Findings:**
- External script missing SRI → Medium (A08)
- External stylesheet missing SRI → Low (A08)
- `eval()` in inline script → Medium (A03, potential injection vector)

**raw_data:**
```python
{
  "total_external_scripts": 5,
  "total_external_styles": 2,
  "scripts_missing_sri": [
    {
      "src": "https://cdn.jquery.com/jquery-1.12.min.js",
      "has_integrity": false,
      "has_crossorigin": false
    }
  ],
  "styles_missing_sri": [...],
  "inline_script_issues": [
    { "issue": "eval() usage", "line_preview": "eval(userInput)" }
  ]
}
```

---

## TESTS TO WRITE
File: `scanners/test_sri_scanner.py`

Use mock HTML responses.

- Test: Page with all SRI correct → 0 findings
- Test: Page with external jQuery, no integrity attr → 1 Medium finding
- Test: Page with external CSS, no integrity → 1 Low finding
- Test: Local script (src="/js/app.js") → NOT flagged (only external)
- Test: Protocol-relative URL (`//cdn.example.com/lib.js`) → treated as external
- Test: `eval()` in inline script → Medium finding
- Test: Page with no scripts → 0 findings, no crash
- Test: raw_data totals match actual counts

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
All 8 tests pass. Fast scanner (< 5s). Return both files.
