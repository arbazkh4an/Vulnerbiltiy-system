# AGENT 13 — CVE Scanner
**Depends on:** Agent 06 (BaseScanner), Agent 09 output (tech_stack_summary)
**Output goes to:** `scanners/cve_scanner.py`
**OWASP Coverage:** A06:2021 Vulnerable & Outdated Components

---

## YOUR JOB
Take the tech stack detected by the recon scanner and look up known CVEs for each component using the free NVD (NIST) API.

---

## FILES TO CREATE

### `scanners/cve_scanner.py`

Class `CveScanner(BaseScanner)`:

**Constructor also accepts:** `tech_stack: list[str]`
- e.g. `["WordPress 5.8", "jQuery 1.12.4", "PHP 7.2", "Apache 2.4.29"]`

**Implement `_run_scan()`:**

**Step 1 — Parse tech stack into name + version pairs:**
- Input: `"WordPress 5.8"` → `{ "product": "wordpress", "version": "5.8" }`
- Input: `"jQuery 1.12.4"` → `{ "product": "jquery", "version": "1.12.4" }`
- Handle edge cases: no version detected → skip CVE lookup for that component

**Step 2 — Query NVD API v2 for each component:**
- Endpoint: `https://services.nvd.nist.gov/rest/json/cves/2.0`
- Query params: `keywordSearch={product}`, `keywordExactMatch=false`
- Filter results to only CVEs matching the detected version
- Extract per CVE: CVE ID, description, CVSS score, severity, published date
- Limit: top 5 CVEs per component (sorted by CVSS score descending)
- NVD rate limit: 5 requests/30 seconds without API key — add delays

**Step 3 — Version age check (no API needed):**
- Known EOL dates dict (hardcode these):
  - PHP: 7.x EOL = Nov 2022, 8.0 EOL = Nov 2023
  - jQuery: < 3.0 → outdated
  - WordPress: flag anything < latest-2 versions
- If detected version is EOL → High finding regardless of CVEs

**Step 4 — Build findings:**
- CVE with CVSS >= 9.0 → Critical finding
- CVE with CVSS 7.0–8.9 → High finding
- CVE with CVSS 4.0–6.9 → Medium finding
- EOL component → High finding
- Outdated but not EOL → Medium finding

**raw_data:**
```python
{
  "components_checked": 4,
  "components_with_cves": 2,
  "cves_found": [
    {
      "component": "WordPress 5.8",
      "cve_id": "CVE-2021-39200",
      "cvss_score": 7.5,
      "severity": "HIGH",
      "description": "...",
      "published": "2021-09-09"
    }
  ],
  "eol_components": ["PHP 7.2"]
}
```

---

## TESTS TO WRITE
File: `scanners/test_cve_scanner.py`

Mock the NVD API responses.

- Test: Empty tech stack → 0 findings, no crash
- Test: "WordPress 5.8" → NVD queried with correct params
- Test: CVE with CVSS 9.5 returned → Critical finding created
- Test: CVE with CVSS 5.0 returned → Medium finding created
- Test: "PHP 7.2" detected → EOL High finding created
- Test: "jQuery 1.12" detected → outdated Medium finding
- Test: NVD API timeout → status="error" gracefully
- Test: NVD API rate limit (429) → retry with backoff

---

## PACKAGES NEEDED
```
requests
pytest
responses
pytest-mock
```

---

## DONE WHEN
All 8 tests pass. Return both files. Note: in production, get a free NVD API key to avoid rate limits.
