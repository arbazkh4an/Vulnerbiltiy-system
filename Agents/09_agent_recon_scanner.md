# AGENT 09 — Recon Scanner (Tech Stack & DNS)
**Depends on:** Agent 06 (BaseScanner)
**Output goes to:** `scanners/recon_scanner.py`
**OWASP Coverage:** A06:2021 Vulnerable & Outdated Components

---

## YOUR JOB
Identify what technologies the target website uses. This feeds directly into the CVE scanner (Agent 13).

---

## FILES TO CREATE

### `scanners/recon_scanner.py`

Class `ReconScanner(BaseScanner)`:

**Implement `_run_scan()`:**

**Step 1 — DNS Recon (use `dnspython`):**
- Resolve A records (IP addresses)
- Resolve MX records
- Resolve TXT records (may reveal SPF, DMARC, verification tokens)
- Attempt zone transfer (AXFR) — record if it succeeds (that's a finding!)

**Step 2 — HTTP Fingerprinting (use `requests` + parse response):**
- Fetch homepage, read response headers + body
- Detect from headers:
  - `Server:` → web server + version
  - `X-Powered-By:` → backend tech
  - `Set-Cookie:` names → PHPSESSID=PHP, JSESSIONID=Java, ASP.NET=.NET
- Detect from HTML body:
  - `<meta name="generator">` → CMS name/version
  - WordPress: check `/wp-login.php` existence + `wp-content` in HTML
  - Joomla: check for `Joomla!` in source
  - Drupal: check `Drupal.settings` in source
  - Common JS libraries in `<script src>`: jQuery, React, Angular, Vue + versions from filenames

**Step 3 — Wappalyzer (use `python-Wappalyzer` library):**
- Run Wappalyzer on the target URL
- Extract: cms, programming_languages, frameworks, web_servers, databases, js_frameworks
- Include version numbers where detected

**Step 4 — Build raw_data:**
```python
{
  "ip_addresses": ["1.2.3.4"],
  "dns_mx": [...],
  "dns_txt": [...],
  "zone_transfer_possible": false,
  "web_server": "Apache/2.4.29",
  "backend_tech": "PHP/7.2",
  "cms": "WordPress 5.8",
  "js_libraries": [{"name": "jQuery", "version": "1.12.4"}],
  "frameworks": [...],
  "tech_stack_summary": ["WordPress 5.8", "PHP 7.2", "Apache 2.4.29", "jQuery 1.12.4"]
}
```

**Findings to create:**
- DNS zone transfer possible → High (A05)
- Version numbers in headers → Low (A05, information disclosure)
- Outdated CMS detected (version check heuristic: if WordPress < 6.0, flag) → Info

---

## TESTS TO WRITE
File: `scanners/test_recon_scanner.py`

- Test: Normal site → returns tech_stack_summary as non-empty list
- Test: WordPress detection works from HTML pattern matching
- Test: jQuery version extracted from script src URL
- Test: Zone transfer attempt made and failure handled gracefully
- Test: Server header version number creates Info finding
- Test: Wappalyzer failure (timeout/error) doesn't crash scanner
- Test: raw_data contains all expected fields

---

## PACKAGES NEEDED
```
dnspython
requests
beautifulsoup4
python-Wappalyzer
pytest
responses
pytest-mock
```

---

## DONE WHEN
All 7 tests pass. `tech_stack_summary` list is the primary output that Agent 13 (CVE scanner) will consume.
Return `scanners/recon_scanner.py` and `scanners/test_recon_scanner.py`.
