# AGENT 21 — Rate Limiter & Abuse Protection
**Depends on:** Agent 04 (FastAPI Core — middleware goes here)
**Output goes to:** `backend/middleware/`

---

## YOUR JOB
Protect the platform from abuse. Add rate limiting, request validation, and abuse detection as FastAPI middleware.

---

## FILES TO CREATE

### `backend/middleware/rate_limiter.py`

FastAPI middleware using Redis for tracking:

**Per-IP rate limits:**
- `/api/scan` POST: max 5 scans per hour per IP
- `/api/scan` GET: max 60 requests per hour per IP
- Global: max 100 requests per hour per IP (all endpoints)

**Implementation:**
- Use Redis sorted sets (sliding window algorithm)
  - Key: `ratelimit:{ip}:{endpoint}`
  - Score: timestamp
  - Count requests in last 3600 seconds
- If limit exceeded → return HTTP 429 with:
  ```json
  { "error": "rate_limit_exceeded", "retry_after_seconds": 300, "message": "..." }
  ```
- Add headers to all responses:
  - `X-RateLimit-Limit: 5`
  - `X-RateLimit-Remaining: 3`
  - `X-RateLimit-Reset: 1735000000`

**Extract real IP:**
- Check `X-Forwarded-For` header (behind Nginx proxy)
- Fall back to `request.client.host`

### `backend/middleware/security_headers.py`

Middleware that adds security headers to ALL responses:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Content-Security-Policy: default-src 'self'; script-src 'self'; connect-src 'self' ws://localhost:8000`
- Remove `Server:` header (don't reveal FastAPI/uvicorn version)

### `backend/middleware/cors.py`
- Allow origins: `http://localhost:3000` (dev), production domain
- Allow methods: GET, POST
- Allow headers: Content-Type, Authorization
- Max age: 3600

---

## TESTS TO WRITE
File: `backend/middleware/test_rate_limiter.py`

- Test: First 5 scans within hour → all succeed (200)
- Test: 6th scan within hour → 429 returned
- Test: After hour passes → limit resets (mock time)
- Test: Rate limit headers present on every response
- Test: X-Forwarded-For used when present
- Test: Security headers present on every response
- Test: Server header removed from responses
- Test: CORS allows localhost:3000, blocks random origin

---

## PACKAGES NEEDED
```
fastapi
redis
pytest
pytest-asyncio
httpx
```

---

## DONE WHEN
All 8 tests pass. Middleware registered in main.py. Returns both middleware files.
