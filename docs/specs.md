## Frontend

* React
* TailwindCSS
* Supabase client
* Hosted on Vercel

---

## Backend

* Python 3.11
* FastAPI
* Hosted on Render Web Service

Endpoints:

<pre class="overflow-visible! px-0!" data-start="4863" data-end="4921"><div class="relative w-full my-4"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class=""><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼk ͼy"><div class="cm-scroller"><div class="cm-content q9tKkq_readonly"><span>POST /api/scan</span><br/><span>GET /api/scan/{id}</span><br/><span>GET /api/history</span></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

---

## Worker

* Separate Render Worker
* Poll DB every 5 seconds
* Fetch scans WHERE status='queued'
* Update status='running'
* Execute scanners sequentially or parallel via asyncio
* Store raw results
* Call AI
* Update status='complete'

---

## Database (Supabase)

### scans table

| Field        | Type      |
| ------------ | --------- |
| id           | UUID      |
| user_id      | UUID      |
| url          | TEXT      |
| status       | TEXT      |
| created_at   | TIMESTAMP |
| completed_at | TIMESTAMP |

---

### scan_results table

| Field     | Type  |
| --------- | ----- |
| scan_id   | UUID  |
| raw_json  | JSONB |
| ai_report | JSONB |

---

## AI Engine

Input:

* Structured scan JSON

Output:

* Strict JSON vulnerability report
* Risk score 0–100
* OWASP mapping
* Severity classification

---

## Deployment

Frontend → Vercel

Backend → Render Web Service

Worker → Render Worker

Database → Supabase

AI → Groq/OpenAI

---
