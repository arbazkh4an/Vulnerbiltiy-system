# AGENT 15 — Scan Orchestrator (Celery Worker)
**Depends on:** Agent 02 (Queue), Agents 06–14 (all scanners), Agent 01 (DB)
**Output goes to:** `orchestrator/`

---

## YOUR JOB
Build the Celery worker that picks scan jobs from the queue, runs all scanner modules in parallel, collects results, and triggers the AI engine.

---

## FILES TO CREATE

### `orchestrator/worker.py`

Celery task: `@app.task(name='orchestrator.run_scan')`
Function: `run_scan(scan_job: dict)`

**Flow:**
1. Deserialize `scan_job` dict into `ScanJob` object
2. Update DB: status = "scanning"
3. Publish progress: 5%, "Starting scan..."
4. Run ALL scanners in parallel using `concurrent.futures.ThreadPoolExecutor`
   - Max workers = 8 (one per scanner)
   - Scanners to run:
     - `ReconScanner` (run first, then pass tech_stack to CveScanner)
     - `HeaderScanner`
     - `SslScanner`
     - `SriScanner`
     - `PathScanner`
     - `AuthScanner`
     - `InjectionScanner`
   - After recon completes: run `CveScanner(tech_stack=recon_result.raw_data['tech_stack_summary'])`
5. As each scanner completes, publish progress update with scanner name + percent
6. Wait for all scanners to complete (or timeout at 90 seconds total)
7. Collect all `ScannerResult` objects
8. Save each result to DB via `save_scanner_result()`
9. Publish progress: 85%, "Analyzing with AI..."
10. Call `orchestrator.analyze.run_ai_analysis(scan_id, merged_json)` (separate Celery task)

**Progress calculation:**
- Recon = 10%
- Headers = 20%
- SSL = 30%
- SRI = 40%
- Paths = 50%
- Auth = 65%
- Injection = 75%
- CVE = 80%
- AI = 85–100%

### `orchestrator/analyze.py`

Celery task: `@app.task(name='orchestrator.analyze')`
Function: `run_ai_analysis(scan_id: str, merged_json: dict)`

1. Import AI engine (Agent 17)
2. Call `ai_engine.analyze(merged_json)`
3. Save AI report to DB
4. Update scan status = "complete"
5. Publish progress: 100%, type="complete", attach full report

### `orchestrator/error_handler.py`

- Function: `handle_scanner_failure(scan_id, scanner_name, error)`
  - Log error
  - Save partial result to DB with status="error"
  - Continue with other scanners (don't abort whole scan)
- Function: `handle_total_failure(scan_id, error)`
  - Update scan status = "error"
  - Publish error event to WebSocket

---

## TESTS TO WRITE
File: `orchestrator/test_worker.py`

Mock all scanner classes and DB.

- Test: All 8 scanners called when job runs
- Test: Recon result passed to CVE scanner correctly
- Test: Scanner failure doesn't abort other scanners
- Test: Progress events published in correct order
- Test: DB status updated to "scanning" then triggers "complete"
- Test: Total timeout fires if scanners hang
- Test: run_ai_analysis called after all scanners finish
- Test: Results saved to DB for each scanner

---

## PACKAGES NEEDED
```
celery
redis
concurrent.futures (stdlib)
pytest
pytest-mock
```

---

## DONE WHEN
All 8 tests pass. Worker picks a job, runs all scanners, publishes progress, saves results.
Return all files in `orchestrator/`.
