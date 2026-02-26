# AGENT 08 — SSL/TLS Scanner
**Depends on:** Agent 06 (BaseScanner)
**Output goes to:** `scanners/ssl_scanner.py`
**OWASP Coverage:** A02:2021 Cryptographic Failures

---

## YOUR JOB
Build the SSL/TLS scanner that checks certificate health and cipher strength.

---

## FILES TO CREATE

### `scanners/ssl_scanner.py`

Class `SslScanner(BaseScanner)`:

**Implement `_run_scan()`:**

Use Python's built-in `ssl` module + `socket`. Do NOT use external tools.

**Step 1 — Basic connectivity:**
- Check if target uses HTTPS at all
- If HTTP only → Critical finding (A02, "Unencrypted Transmission")

**Step 2 — Certificate checks (use `ssl.get_server_certificate` + `ssl.SSLContext`):**
- Certificate expiry date → if expires in < 30 days → High finding
- Certificate already expired → Critical finding
- Self-signed certificate → High finding
- Certificate hostname mismatch → Critical finding
- Extract: issuer, subject, expiry date, SANs

**Step 3 — TLS version checks:**
Connect with each protocol version and record if server accepts it:
- TLS 1.0 accepted → High finding (deprecated)
- TLS 1.1 accepted → Medium finding (deprecated)
- TLS 1.2 accepted → OK
- TLS 1.3 accepted → Good (note in raw_data)

**Step 4 — HSTS check:**
- Already checked in header_scanner, but confirm here too
- Include in raw_data

**Step 5 — Build raw_data:**
```python
{
  "uses_https": bool,
  "cert_expiry": "2025-01-01",
  "cert_expiry_days": 45,
  "cert_issuer": "...",
  "cert_subject": "...",
  "self_signed": bool,
  "hostname_match": bool,
  "tls_versions_supported": ["TLSv1.2", "TLSv1.3"],
  "tls_deprecated_supported": ["TLSv1.0"],
}
```

---

## TESTS TO WRITE
File: `scanners/test_ssl_scanner.py`

Mock `ssl` module calls.

- Test: HTTPS with valid cert, TLS 1.2/1.3 only → 0 High/Critical findings
- Test: HTTP-only site → Critical finding
- Test: Cert expiring in 10 days → High finding
- Test: Expired cert → Critical finding
- Test: TLS 1.0 supported → High finding
- Test: TLS 1.1 supported → Medium finding
- Test: Self-signed cert → High finding
- Test: Unreachable host → status="error"

---

## PACKAGES NEEDED
```
ssl (stdlib)
socket (stdlib)
cryptography
pytest
pytest-mock
```

---

## DONE WHEN
All 8 tests pass. Returns proper ScannerResult with all SSL details in raw_data.
Return `scanners/ssl_scanner.py` and `scanners/test_ssl_scanner.py`.
