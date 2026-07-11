# SentinelAI — System Flow Documentation

This document outlines the complete end-to-end flow of the SentinelAI vulnerability scanning system, from the moment a user enters a URL to the final rendering of AI-analyzed results.

## Phase 1: Initiation (Frontend)

1.  **URL Submission:** The user enters a target URL in the Dashboard (`app/dashboard/page.tsx`).
2.  **Scanning State:** The `handleStartScan` function is triggered, which:
    *   Validates the URL format.
    *   Checks local rate limits.
    *   Makes an optimistic update to the scan list with a `pending` status.
3.  **API Call:** A `POST /api/scans/start` request is sent to the backend with the target URL.

## Phase 2: Queuing (Backend API)

1.  **Validation & Security:** The API (`backend/app/api/routes_scan.py`):
    *   Validates the URL using `validate_scan_url` (blocking SSRF and local IPs).
    *   Checks server-side rate limits for the user.
2.  **Consent Logging:** Stores the user's consent and client IP in the database.
3.  **Persistence:** Creates a new scan record in the `scans` table with status `queued`.
4.  **Response:** Returns a unique `scan_id` to the frontend.

## Phase 3: Transition & Polling (Frontend)

1.  **Redirection:** The Dashboard redirects the user to the scan details page: `/scan/{scan_id}` (`app/scan/[id]/page.tsx`).
2.  **Active Polling:** The scan details page initiates a `setInterval` that polls `GET /api/scans/{scan_id}` every 3 seconds to fetch the latest status, progress, and findings.

## Phase 4: Processing (Background Worker)

1.  **Job Discovery:** A standalone background worker (`backend/app/worker/worker.py`) constantly polls the database for scans with a `queued` status.
2.  **Orchestration:** Once a scan is picked up, the worker calls `process_scan` in `backend/app/services/scan_service.py`.
3.  **Scanner Execution:**
    *   The service concurrently runs multiple modular scanners:
        *   `HeaderScanner`: Checks security headers (HSTS, CSP, etc.).
        *   `SSLScanner`: Analyzes SSL/TLS configuration.
        *   `PathScanner`: Probes for common sensitive files/directories.
        *   `CVEScanner`: Performs version-based vulnerability checks.
    *   Raw results are merged and stored in the database.
4.  **Status Updates:** The service periodically updates the scan's `progress` and `status` in the database, which the frontend polling picks up.

## Phase 5: AI Analysis (AI Service)

1.  **LLM Call:** The `scan_service` passes the raw results to `generate_ai_report` (`backend/app/services/ai_service.py`).
2.  **Prompt Engineering:**
    *   **System Prompt:** Provides the persona (Senior Cybersecurity Analyst) and strict JSON structure rules.
    *   **User Prompt:** Templates the target URL and raw scan data for the LLM.
3.  **Model Inference:** The service tries Groq (fastest) first, then falls back to OpenAI if needed.
4.  **Structured Output:** The LLM returns a structured JSON containing:
    *   Executive Summary.
    *   Overall Risk Score (0-100).
    *   Specific Findings (Title, Severity, OWASP Category, Evidence, Remediation, CVSS Score).

## Phase 6: Finalization & Rendering

1.  **Database Storage:** The AI report is parsed, validated against a Pydantic model (`AIReport`), and stored in the database.
2.  **Completion:** The scan status is marked as `completed`.
3.  **Frontend Update:** The next polling request from the frontend receives the `completed` status and the full AI report.
4.  **Rendering:**
    *   The `HackerScanDashboard` component renders the findings as cards.
    *   Users can click findings to see AI-generated descriptions and remediations.
    *   The final risk score is displayed in a specialized modal.
    *   A "Download PDF" button becomes active, allowing users to export the final report.

---
**Key Technologies:**
- **Frontend:** Next.js (App Router), Tailwind CSS, Framer Motion, Lucide React.
- **Backend:** FastAPI, Asyncpg (PostgreSQL), Pydantic.
- **Workers:** Python Asyncio loop.
- **AI:** Groq (LLaMA 3), OpenAI (GPT-4o).
- **Database:** PostgreSQL.
