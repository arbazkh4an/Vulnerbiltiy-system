# AGENT 01 — Database Setup
**Depends on:** Nothing
**Output goes to:** `database/`

---

## YOUR JOB
Create the PostgreSQL database schema and connection layer for the OWASP scanner.

---

## FILES TO CREATE

### `database/schema.sql`
Create these tables:

**scans**
- id (UUID, primary key)
- url (TEXT, not null)
- status (TEXT) — values: "queued" | "scanning" | "analyzing" | "complete" | "error"
- created_at (TIMESTAMP)
- completed_at (TIMESTAMP, nullable)
- user_ip (TEXT)
- consent_confirmed (BOOLEAN)

**scan_results**
- id (UUID, primary key)
- scan_id (UUID, foreign key → scans.id)
- scanner_name (TEXT) — e.g. "header_scanner"
- raw_json (JSONB)
- duration_ms (INTEGER)
- created_at (TIMESTAMP)

**ai_reports**
- id (UUID, primary key)
- scan_id (UUID, foreign key → scans.id)
- risk_score (INTEGER 0-100)
- summary (TEXT)
- findings_json (JSONB)
- created_at (TIMESTAMP)

### `database/db.py`
- Use `asyncpg` for async PostgreSQL connection
- Create a connection pool on startup
- Expose these functions:
  - `create_scan(url, user_ip, consent) → scan_id`
  - `update_scan_status(scan_id, status)`
  - `save_scanner_result(scan_id, scanner_name, raw_json, duration_ms)`
  - `save_ai_report(scan_id, risk_score, summary, findings_json)`
  - `get_scan(scan_id) → dict`
  - `get_scan_with_results(scan_id) → dict`

---

## TESTS TO WRITE
File: `database/test_db.py`

- Test: Connect to DB successfully
- Test: Create a scan row, read it back, confirm fields match
- Test: Update scan status from "queued" to "scanning"
- Test: Save a scanner result, confirm JSONB stored correctly
- Test: Save AI report, read it back
- Test: get_scan_with_results returns nested data correctly

Use pytest. Mock the DB connection using `pytest-asyncio` + a test database.

---

## PACKAGES NEEDED
```
asyncpg
pytest
pytest-asyncio
```

---

## DONE WHEN
All 6 tests pass. Return `database/db.py`, `database/schema.sql`, `database/test_db.py`.
