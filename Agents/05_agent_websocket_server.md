# AGENT 05 — WebSocket Server (Live Progress)
**Depends on:** Agent 04 (FastAPI Core), Agent 02 (Redis Queue)
**Output goes to:** `backend/websocket.py`

---

## YOUR JOB
Add WebSocket support to the FastAPI app so the frontend gets live scan progress updates without polling.

---

## FILES TO CREATE

### `backend/websocket.py`
- FastAPI WebSocket route: `WS /ws/{scan_id}`
- On client connect:
  1. Validate scan_id exists in DB (disconnect if not)
  2. Subscribe to Redis PubSub channel `scan_progress:{scan_id}`
  3. Stream all incoming messages to the WebSocket client as JSON
  4. If scan status is already "complete", immediately send final report and close
  5. On disconnect, unsubscribe cleanly

- Message format sent to client:
```json
{
  "type": "progress",
  "scan_id": "uuid",
  "stage": "header_scanner",
  "percent": 35,
  "message": "Checking HTTP security headers...",
  "timestamp": "2025-02-26T10:00:00Z"
}
```
- Final message type: `"complete"` with full report attached
- Error message type: `"error"` with error description

### `backend/connection_manager.py`
- Class `ConnectionManager`:
  - `connect(websocket, scan_id)` — register connection
  - `disconnect(websocket, scan_id)` — unregister
  - `send_to_scan(scan_id, message: dict)` — send to all clients watching this scan
  - Track active connections in a dict `{ scan_id: [websocket, ...] }`

### Update `backend/main.py`
- Import and include the WebSocket router
- Add connection manager instance

---

## TESTS TO WRITE
File: `backend/test_websocket.py`

Use `pytest` + `httpx` WebSocket test client.

- Test: Connect to valid scan_id, receive connection_ack message
- Test: Connect to invalid scan_id, connection closes immediately
- Test: Publish progress to Redis channel, confirm WebSocket client receives it
- Test: When scan completes, client receives type="complete" message
- Test: Multiple clients on same scan_id all receive messages
- Test: Client disconnect unregisters cleanly (no memory leak)

---

## PACKAGES NEEDED
```
fastapi[websockets]
websockets
pytest-asyncio
```

---

## DONE WHEN
All 6 tests pass. WebSocket streams messages from Redis to browser in real time.
Return `backend/websocket.py` and `backend/connection_manager.py`.
