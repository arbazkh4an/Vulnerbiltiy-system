# AGENT 02 — Redis Job Queue
**Depends on:** Nothing
**Output goes to:** `queue/`

---

## YOUR JOB
Set up the Redis-backed job queue using Celery. This is how scan jobs are passed from the API to the scanner workers asynchronously.

---

## FILES TO CREATE

### `queue/celery_app.py`
- Create a Celery app instance
- Broker: Redis at `redis://localhost:6379/0`
- Backend (result store): Redis at `redis://localhost:6379/1`
- Set task serializer to JSON
- Set result expiry to 3600 seconds (1 hour)
- Configure task routes:
  - `scanners.*` → queue named `scan_queue`
  - `ai.*` → queue named `ai_queue`

### `queue/job_models.py`
Define a Python dataclass `ScanJob`:
```
ScanJob:
  scan_id: str
  url: str
  created_at: str (ISO timestamp)
  priority: int (default 5)
```

### `queue/publisher.py`
- Function: `enqueue_scan(scan_job: ScanJob) → task_id`
  - Pushes job to `scan_queue`
  - Returns Celery task ID
- Function: `get_job_status(task_id) → dict`
  - Returns `{ state, result, traceback }`

### `queue/progress.py`
- Use Redis PubSub for live progress updates
- Function: `publish_progress(scan_id, stage, percent, message)`
  - Publishes to channel `scan_progress:{scan_id}`
- Function: `subscribe_progress(scan_id) → generator`
  - Subscribes and yields progress events as dicts

---

## TESTS TO WRITE
File: `queue/test_queue.py`

- Test: Celery app initializes without error
- Test: ScanJob dataclass validates correctly
- Test: enqueue_scan pushes to queue (mock Redis)
- Test: get_job_status returns correct shape
- Test: publish_progress puts message on correct channel
- Test: subscribe_progress receives published messages

---

## PACKAGES NEEDED
```
celery
redis
pytest
pytest-mock
```

---

## DONE WHEN
All 6 tests pass. Return all files in `queue/`.
