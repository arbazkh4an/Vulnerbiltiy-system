# AGENT 12 — Auth Scanner
**Depends on:** Agent 06 (BaseScanner)
**Output goes to:** `scanners/auth_scanner.py`
**OWASP Coverage:** A07:2021 Identification & Authentication Failures

---

## YOUR JOB
Test the login mechanism for common authentication weaknesses. DO NOT actually compromise accounts — just probe behavior.

---

## FILES TO CREATE

### `scanners/auth_scanner.py`

Class `AuthScanner(BaseScanner)`:

**Implement `_run_scan()`:**

**Step 1 — Find login page:**
- Check these paths: `/login`, `/signin`, `/wp-login.php`, `/admin/login`, `/user/login`, `/account/login`, `/auth/login`
- For each: GET request, check if response contains `<input type="password">`
- Use BeautifulSoup to find `<form>` with password field
- Extract form action URL and field names (username_field, password_field)
- If no login page found → skip remaining steps, note in raw_data

**Step 2 — Username enumeration test:**
- Try login with: real-looking username (`admin`) + wrong password
- Try login with: definitely fake username (`xXx_nonexistent_user_xXx`) + same wrong password
- Compare: response body length, response time, error message text
- If different messages → username enumeration possible → Medium finding

**Step 3 — Rate limiting test:**
- Send 10 rapid login requests with wrong credentials
- If NO lockout, NO CAPTCHA, NO rate limit header (`Retry-After`, `X-RateLimit-*`) → High finding
- Record: any lockout after N attempts, any CAPTCHA triggered

**Step 4 — Default credentials test (SAFE — only try these exact pairs):**
- `admin / admin`
- `admin / password`
- `admin / 123456`
- `administrator / administrator`
- Check response: if redirect to dashboard or no "invalid credentials" message → Critical finding
- Add 2 second delay between each attempt (be respectful)

**Step 5 — Password policy hint:**
- Check if login error reveals whether password or username was wrong specifically

**raw_data:**
```python
{
  "login_page_found": "/wp-login.php",
  "login_form_action": "/wp-login.php",
  "username_field": "log",
  "password_field": "pwd",
  "username_enumeration_possible": true,
  "rate_limiting_detected": false,
  "lockout_after_attempts": null,
  "captcha_detected": false,
  "default_creds_worked": false,
  "requests_sent": 15
}
```

---

## TESTS TO WRITE
File: `scanners/test_auth_scanner.py`

- Test: Login page found at /wp-login.php → login_page_found set correctly
- Test: No login page found anywhere → graceful skip, not error
- Test: Different error messages for valid vs invalid user → enumeration finding
- Test: Same error for both → no enumeration finding
- Test: 10 rapid requests with no rate limit headers → High finding
- Test: Response with `Retry-After` header → rate limiting detected
- Test: Default creds attempt returns success page → Critical finding
- Test: Default creds fail correctly → no finding

---

## IMPORTANT — ETHICAL LIMITS
- Max 15 total requests to login endpoint
- Always add delay between attempts
- Never try more than 4 default credential pairs
- If CAPTCHA detected → stop immediately, record in raw_data

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
All 8 tests pass. Scanner is respectful and bounded. Return both files.
