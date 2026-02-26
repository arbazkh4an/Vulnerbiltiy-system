# AGENT 20 — Frontend Results UI (Styling & Report Display)
**Depends on:** Agent 19 (Frontend Shell components exist)
**Output goes to:** `frontend/src/components/` (styling + enhanced components)

---

## YOUR JOB
Make the frontend look professional and cybersecurity-appropriate. Style all components. Build the detailed report display.

---

## DESIGN DIRECTION
Dark theme. Terminal/hacker aesthetic but clean and professional.
Colors: Dark background (#0a0f1a), cyan accent (#00e5ff), red for Critical (#ff3d71), orange for High, yellow for Medium, blue for Low.

---

## FILES TO CREATE / ENHANCE

### `frontend/src/styles/globals.css`
- Dark background
- Monospace font for code/evidence sections (JetBrains Mono or Fira Code via Google Fonts)
- Sans-serif for body text (IBM Plex Sans)
- CSS variables for all severity colors
- Animated grid background (subtle)

### `frontend/src/components/SeverityBadge.jsx`
Props: `{ severity }` — "Critical" | "High" | "Medium" | "Low" | "Info"
- Colored pill badge
- Critical: red glow
- High: orange
- Medium: yellow
- Low: blue
- Info: gray

### `frontend/src/components/RiskMeter.jsx`
Props: `{ score: 0-100 }`
- Large circular gauge (use SVG, no library)
- Color changes: green (0-30), yellow (31-60), orange (61-80), red (81-100)
- Animated fill on mount
- Score number in center

### `frontend/src/components/FindingCard.jsx`
Props: `{ finding }` — one AI finding object
- Collapsible card (click to expand)
- Header: SeverityBadge + OWASP ID + title
- Expanded: evidence, impact, recommendation, reference links
- Monospace font for evidence text
- Copy-to-clipboard button on evidence

### `frontend/src/components/ReportViewer.jsx` (enhance Agent 19's version)
Full report display:
- Top section: RiskMeter + summary text + scan metadata
- Filter bar: filter findings by severity (All / Critical / High / Medium / Low)
- Findings list: FindingCard for each finding
- Footer: "Download Report as JSON" button (just `JSON.stringify` to file download)
- Empty state: if no findings → green checkmark + "No vulnerabilities detected"

### `frontend/src/components/ProgressTracker.jsx` (enhance Agent 19's version)
- Animated progress bar with glow effect
- Scanner stages shown as timeline steps (completed = checkmark, active = pulse, pending = dot)
- Terminal-style scrolling log at bottom

### `frontend/src/components/URLInput.jsx` (enhance Agent 19's version)
- Dark input with cyan focus border
- Animated scan button (pulse when scanning)
- Example URLs shown as clickable chips (only show test targets like `http://testphp.vulnweb.com`)

---

## TESTS TO WRITE
File: `frontend/src/__tests__/ui.test.jsx`

- Test: SeverityBadge renders "Critical" with correct class
- Test: RiskMeter renders score=85 with red color class
- Test: FindingCard collapses/expands on click
- Test: ReportViewer filter hides non-matching findings
- Test: Download button triggers file download
- Test: Empty findings → shows "No vulnerabilities detected"
- Test: ProgressTracker shows completed stages correctly

---

## PACKAGES NEEDED
```
react
tailwindcss (or plain CSS)
```
No heavy UI libraries — keep it lightweight.

---

## DONE WHEN
All 7 tests pass. UI looks professional. Report is easy to read.
Return all component files and CSS.
