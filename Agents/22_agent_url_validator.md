# AGENT 22 — URL Validator (Security Gatekeeper)
**Depends on:** Nothing (pure Python utility)
**Output goes to:** `backend/utils/url_validator.py`

---

## YOUR JOB
Build the security-critical URL validator that runs BEFORE any scan starts. This prevents your platform from being used to scan internal networks, attack infrastructure, or perform SSRF.

---

## FILES TO CREATE

### `backend/utils/url_validator.py`

Class `URLValidator`:

**Method: `validate(url: str) → ValidationResult`**

Returns `ValidationResult(valid: bool, reason: str | None)`

Run ALL these checks in order:

**Check 1 — Basic format:**
- Must start with `http://` or `https://`
- Must have a valid hostname (use `urllib.parse`)
- Must not be empty

**Check 2 — Block private/internal IP ranges (CRITICAL):**
Resolve the hostname to IP, then block if IP is in:
- `127.0.0.0/8` (loopback)
- `10.0.0.0/8` (private)
- `172.16.0.0/12` (private)
- `192.168.0.0/16` (private)
- `169.254.0.0/16` (link-local / AWS metadata)
- `::1` (IPv6 loopback)
- `fc00::/7` (IPv6 private)
- `0.0.0.0`

**Check 3 — Block localhost variants:**
Block hostnames: `localhost`, `127.0.0.1`, `0.0.0.0`, `[::1]`
Also block encoded variants: `0x7f000001`, `2130706433`, `017700000001`

**Check 4 — Block internal hostnames:**
Block: `*.internal`, `*.local`, `*.localhost`, `metadata.google.internal`, `169.254.169.254`

**Check 5 — URL length:**
- Max URL length: 2048 characters

**Check 6 — Scheme check:**
- Only allow `http` and `https` schemes
- Block: `file://`, `ftp://`, `gopher://`, `dict://`, `ldap://`, etc.

**Check 7 — Port restrictions:**
- Allow: 80, 443, 8080, 8443 (common web ports)
- Block: 22 (SSH), 3306 (MySQL), 5432 (Postgres), 6379 (Redis), 27017 (MongoDB), etc.
- If no port specified → OK

**Check 8 — Resolve and re-check:**
- Do a DNS resolution of the hostname
- If resolved IP is in private ranges → block (DNS rebinding protection)
- If DNS resolution fails → block (don't scan unresolvable hosts)

---

## TESTS TO WRITE
File: `backend/utils/test_url_validator.py`

- Test: `https://example.com` → valid
- Test: `http://localhost` → blocked (loopback)
- Test: `http://127.0.0.1` → blocked
- Test: `http://192.168.1.1` → blocked (private range)
- Test: `http://169.254.169.254` → blocked (AWS metadata)
- Test: `http://10.0.0.1` → blocked
- Test: `file:///etc/passwd` → blocked (scheme)
- Test: `https://example.com:3306` → blocked (database port)
- Test: `https://example.com:443` → valid
- Test: URL resolving to private IP → blocked (DNS rebinding)
- Test: Non-existent domain → blocked
- Test: URL > 2048 chars → blocked

---

## PACKAGES NEEDED
```
ipaddress (stdlib)
urllib (stdlib)
socket (stdlib)
validators
pytest
pytest-mock
```

---

## DONE WHEN
All 12 tests pass. This is the most security-critical utility in the whole project.
Return both files.
