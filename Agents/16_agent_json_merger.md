# AGENT 16 — JSON Merger
**Depends on:** All scanner agents (06–14)
**Output goes to:** `orchestrator/merger.py`

---

## YOUR JOB
Take the raw output from all 8 scanners and merge them into a single, clean, structured JSON object that gets sent to the AI engine. This is the most important data transformation step.

---

## FILES TO CREATE

### `orchestrator/merger.py`

Class `ScanMerger`:

**Method: `merge(scan_id: str, scanner_results: list[ScannerResult]) → dict`**

Takes a list of `ScannerResult` objects from all scanners.
Returns one unified JSON dict structured exactly like this:

```python
{
  "scan_id": "...",
  "target": "https://example.com",
  "timestamp": "ISO timestamp",
  "scan_duration_seconds": 45,
  "scanners_completed": 8,
  "scanners_errored": 0,

  "recon": {
    # From ReconScanner raw_data
    "ip_addresses": [...],
    "tech_stack": [...],
    "cms": "...",
    "web_server": "...",
    "dns_txt": [...]
  },

  "headers": {
    # From HeaderScanner raw_data
    "server": "...",
    "missing_headers": [...],
    "present_headers": {...},
    "cors_open": bool
  },

  "ssl": {
    # From SslScanner raw_data
    "uses_https": bool,
    "cert_expiry_days": int,
    "tls_versions": [...],
    "deprecated_tls": [...],
    "grade_estimate": "A/B/C/F"
  },

  "exposed_paths": {
    # From PathScanner raw_data
    "critical_exposures": [...],
    "accessible_admin": [...],
    "info_pages": [...]
  },

  "injection": {
    # From InjectionScanner raw_data
    "inputs_tested": int,
    "xss_findings": [...],
    "sqli_findings": [...]
  },

  "auth": {
    # From AuthScanner raw_data
    "login_page": "...",
    "rate_limiting": bool,
    "username_enumeration": bool,
    "default_creds_work": bool
  },

  "cves": {
    # From CveScanner raw_data
    "components": [...],
    "cves_found": [...],
    "eol_components": [...]
  },

  "sri": {
    # From SriScanner raw_data
    "external_resources": int,
    "missing_sri": [...],
    "eval_usage": bool
  },

  "all_findings": [
    # COMBINED list of ALL Finding objects from ALL scanners
    # sorted by severity: Critical first, then High, Medium, Low, Info
    {
      "owasp_id": "A03:2021",
      "title": "SQL Injection",
      "severity": "Critical",
      "evidence": "...",
      "source_scanner": "injection_scanner"
    }
  ],

  "severity_summary": {
    "critical": 2,
    "high": 3,
    "medium": 5,
    "low": 2,
    "info": 4
  }
}
```

**Method: `estimate_ssl_grade(ssl_data: dict) → str`**
Simple logic:
- Critical issues → F
- TLS 1.0 supported → C
- No TLS 1.3 → B
- All good → A

**Method: `sort_findings_by_severity(findings: list) → list`**
Order: Critical → High → Medium → Low → Info

**Method: `handle_missing_scanner(scanner_name: str) → dict`**
If a scanner errored out, return a placeholder dict with null values so the shape stays consistent.

---

## TESTS TO WRITE
File: `orchestrator/test_merger.py`

- Test: All 8 scanner results → single merged dict with all top-level keys present
- Test: Findings sorted correctly (Critical before High before Medium etc.)
- Test: severity_summary counts are accurate
- Test: Missing scanner (errored) → shape still complete, no KeyError
- Test: ssl_grade estimation logic (test each grade)
- Test: all_findings is flat list (not nested by scanner)
- Test: scan_duration_seconds calculated correctly
- Test: Empty scanner results list → minimal valid dict

---

## PACKAGES NEEDED
```
pytest
```
(No external packages needed — pure Python transformation)

---

## DONE WHEN
All 8 tests pass. Output JSON is exactly the shape the AI engine expects.
Return `orchestrator/merger.py` and `orchestrator/test_merger.py`.
