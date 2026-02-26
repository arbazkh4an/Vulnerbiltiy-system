# AGENT 04 — FastAPI Backend Core
**Depends on:** Agent 01 (DB), Agent 02 (Queue)
**Output goes to:** `backend/`

---

## YOUR JOB
Build the FastAPI backend with all API endpoints. This is the core of the application that the frontend talks to.

---

## FILES TO CREATE

### `backend/main.py`
FastAPI app with these routes:

**POST /api/scan**
- Body: `{ "url": "https://target.com", "consent": true }`
- Validate: url is valid, consent is true
- Call url_validator (Agent 22) — for now just use basic check
- Create scan record in DB (status = "queued")
- Enqueue job to Redis queue
- Return: `{ "scan_id": "uuid", "status": "queued", "message": "Scan started" }`

**GET /api/scan/{scan_id}**
- Fetch scan from DB
- Return full scan object with status
- If complete, include ai_report

**GET /api/scan/{scan_id}/results**
- Return all scanner sub-results for this scan
- Structured by scanner name

**GET /api/health**
- Return: `{ "status": "ok", "db": "ok", "redis": "ok" }`
- Actually check DB and Redis connections

**GET /api/scans**
- Return last 10 scans (no sensitive data, just id/url/status/timestamp)

### `backend/models.py`
Pydantic models for request/response validation:
- `ScanRequest`: url (HttpUrl), consent (bool must be True)
- `ScanResponse`: scan_id, status, message
- `ScanStatusResponse`: scan_id, url, status, created_at, completed_at, findings (optional)
- `HealthResponse`: status, db, redis

### `backend/config.py`
- Load all env vars using pydantic BaseSettings
- DATABASE_URL, REDIS_URL, GROQ_API_KEY, SECRET_KEY, MAX_SCANS_PER_HOUR

### `backend/dependencies.py`
- FastAPI dependency: `get_db()` — yields DB connection
- FastAPI dependency: `get_redis()` — yields Redis connection

---

## TESTS TO WRITE
File: `backend/test_main.py`

Use `httpx` + `pytest` with FastAPI TestClient.

- Test: POST /api/scan with valid URL and consent=true returns 200 + scan_id
- Test: POST /api/scan with consent=false returns 400
- Test: POST /api/scan with invalid URL returns 422
- Test: POST /api/scan with localhost URL returns 400 (blocked)
- Test: GET /api/scan/{valid_id} returns scan object
- Test: GET /api/scan/{invalid_id} returns 404
- Test: GET /api/health returns all green
- Test: GET /api/scans returns list

Mock DB and Redis in tests.

---

## PACKAGES NEEDED
```
fastapi
uvicorn
asyncpg
redis
pydantic
pydantic-settings
httpx
pytest
pytest-asyncio
```

---

## DONE WHEN
All 8 tests pass. Server starts with `uvicorn main:app`. Return all files in `backend/`.
