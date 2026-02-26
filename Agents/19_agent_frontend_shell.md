# AGENT 19 — Frontend Shell (React App Structure)
**Depends on:** Agent 04 (knows API endpoints), Agent 05 (knows WebSocket URL)
**Output goes to:** `frontend/src/`

---

## YOUR JOB
Build the React frontend shell: app structure, routing, API client, and WebSocket hook. No styling needed (Agent 20 handles UI). Just working logic.

---

## FILES TO CREATE

### `frontend/src/api/client.js`

Axios-based API client:

```javascript
const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000'

export const api = {
  startScan: async (url, consent) => {
    // POST /api/scan
    // Returns { scan_id, status }
  },
  getScan: async (scanId) => {
    // GET /api/scan/{scanId}
    // Returns scan object
  },
  getScanResults: async (scanId) => {
    // GET /api/scan/{scanId}/results
  },
  getRecentScans: async () => {
    // GET /api/scans
  },
  checkHealth: async () => {
    // GET /api/health
  }
}
```

### `frontend/src/hooks/useWebSocket.js`

Custom React hook:

```javascript
export function useWebSocket(scanId) {
  // Returns: { progress, stage, percent, isConnected, finalReport, error }
  // Opens WS to ws://localhost:8000/ws/{scanId}
  // Parses incoming JSON messages
  // Updates state on each message
  // Cleans up on unmount
  // Reconnects once on disconnect (then gives up)
}
```

### `frontend/src/hooks/useScan.js`

Custom React hook that combines API + WebSocket:

```javascript
export function useScan() {
  // Returns: { startScan, scanId, status, progress, report, error, isScanning }
  // startScan(url, consent):
  //   1. Calls api.startScan()
  //   2. Gets back scan_id
  //   3. Activates WebSocket on that scan_id
  //   4. Tracks status through queued → scanning → complete
}
```

### `frontend/src/App.jsx`

Main app with two views:
- View 1: URL input form (shown when no active scan)
- View 2: Progress + results (shown during/after scan)

State managed by `useScan()` hook.

### `frontend/src/components/URLInput.jsx`
- Input field for URL
- Consent checkbox: "I own this domain or have written permission to test it"
- Submit button (disabled if no consent or invalid URL)
- Client-side URL validation (must start with http:// or https://)

### `frontend/src/components/ProgressTracker.jsx`
Props: `{ stage, percent, messages: [] }`
- Shows progress bar (percent)
- Shows current stage name
- Shows scrolling log of messages

### `frontend/src/components/ReportViewer.jsx`
Props: `{ report: AIReport }`
- Shows risk score (big number)
- Shows summary paragraph
- Lists all findings (passed to Agent 20 for styling)

---

## TESTS TO WRITE
File: `frontend/src/__tests__/`

Use React Testing Library + Jest.

- Test: URLInput renders with disabled submit when no URL
- Test: URLInput submit enabled only when URL + consent both present
- Test: Invalid URL (no http) shows validation error
- Test: useScan hook: startScan calls api.startScan with correct args
- Test: ProgressTracker renders correct percent value
- Test: ReportViewer renders risk_score from report prop
- Test: WebSocket message updates progress state

---

## PACKAGES NEEDED
```
react
axios
react-testing-library
jest
```

---

## DONE WHEN
All 7 tests pass. App renders, scan starts, WebSocket connects, results display.
Return all files in `frontend/src/`.
