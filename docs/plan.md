## Phase 1 — Foundation (Week 1)

* Setup Supabase project
* Design database schema
* Setup FastAPI backend on Render
* Connect frontend to backend
* Implement scan submission endpoint
* Implement DB-based job queue

Deliverable:

User can submit URL → record created in DB

---

## Phase 2 — Worker System (Week 2)

* Create background worker on Render
* Implement polling mechanism
* Build scanner modules:
  * header_scanner
  * ssl_scanner
  * path_scanner
* Update scan status in DB

Deliverable:

Scan runs asynchronously and updates status

---

## Phase 3 — Realtime + UI (Week 3)

* Integrate Supabase Realtime
* Add progress states:
  * queued
  * running
  * complete
  * failed
* Build clean results UI
* Add severity badges

Deliverable:

Live scan updates visible

---

## Phase 4 — AI Integration (Week 4)

* Merge scanner outputs
* Design structured LLM prompt
* Integrate Groq/OpenAI
* Parse JSON output
* Store AI report

Deliverable:

AI-generated structured report

---

## Phase 5 — Security & Hardening (Week 5)

* Block private IP ranges
* Rate limit per user
* Add consent checkbox
* Implement RLS policies
* Logging

Deliverable:

Platform hardened against abuse
