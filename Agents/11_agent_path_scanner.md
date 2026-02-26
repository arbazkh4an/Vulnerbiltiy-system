# AGENT 11 — Path Scanner (Exposed Files & Directories)
**Depends on:** Agent 06 (BaseScanner), Agent 06's `constants.py` COMMON_PATHS list
**Output goes to:** `scanners/path_scanner.py`
**OWASP Coverage:** A01:2021 Broken Access Control, A04:2021 Insecure Design, A05:2021 Security Misconfiguration

---

## YOUR JOB
Probe for exposed sensitive files and directories by requesting common paths and checking what the server returns.

---

## FILES TO CREATE

### `scanners/path_scanner.py`

Class `PathScanner(BaseScanner)`:

**Implement `_run_scan()`:**

Use `asyncio` + `aiohttp` to probe ALL paths **concurrently** (not sequentially — that would be too slow).

**Paths to probe (expand `COMMON_PATHS` from constants.py to include these categories):**

*Sensitive files:*
- `/.env`, `/.env.local`, `/.env.production`, `/.env.backup`
- `/.git/config`, `/.git/HEAD`, `/.gitignore`
- `/config.php`, `/wp-config.php`, `/configuration.php`
- `/database.yml`, `/secrets.yml`, `/settings.py`
- `/backup.zip`, `/backup.sql`, `/db_backup.sql`
- `/robots.txt` (read and parse — may reveal hidden paths)
- `/sitemap.xml` (read — may reveal structure)

*Admin panels:*
- `/admin`, `/admin/`, `/administrator`, `/wp-admin`, `/cpanel`, `/phpmyadmin`, `/manager`

*Server info pages:*
- `/server-status`, `/server-info` (Apache)
- `/.DS_Store`, `/Thumbs.db`
- `/phpinfo.php`, `/info.php`, `/test.php`

**For each path:**
- Send GET request with 5s timeout
- Record: path, HTTP status, content-length, first 200 chars of response body
- Interesting statuses: 200, 301, 302, 403 (forbidden but exists)
- 404 = skip

**Findings by severity:**
- `.env` file accessible (200) → Critical (A04)
- `.git/config` accessible → Critical (A04)
- `wp-config.php` accessible → Critical (A01)
- `/admin` returns 200 → High (A01)
- `/phpinfo.php` returns 200 → High (A05)
- `robots.txt` with Disallow entries → Info (parse and include disallowed paths)
- Server-status/server-info accessible → Medium (A05)
- Any 403 on sensitive path → Low (exists but blocked — still note it)

**Concurrency settings:**
- Max 10 concurrent requests (semaphore)
- Total timeout for entire scanner: 30 seconds

---

## TESTS TO WRITE
File: `scanners/test_path_scanner.py`

- Test: `.env` returns 200 → Critical finding created
- Test: `.git/config` returns 200 → Critical finding
- Test: Path returns 404 → NOT added to findings
- Test: Path returns 403 → Low finding (exists but blocked)
- Test: robots.txt parsed and Disallow paths extracted
- Test: Concurrent requests don't exceed semaphore limit
- Test: Total scan completes within timeout
- Test: Unreachable host → status="error"

---

## PACKAGES NEEDED
```
aiohttp
asyncio
requests
pytest
pytest-asyncio
aioresponses  # for mocking aiohttp
```

---

## DONE WHEN
All 8 tests pass. Scans 50 paths concurrently in under 15 seconds.
Return `scanners/path_scanner.py` and `scanners/test_path_scanner.py`.
