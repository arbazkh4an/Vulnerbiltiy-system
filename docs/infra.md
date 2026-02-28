# INFRA STRUCTURE SUMMARY FILE

`INFRA_OVERVIEW.md`

---

## Services Used

* Supabase (DB + Auth + Realtime)
* Render (API + Worker)
* Vercel (Frontend)
* Groq/OpenAI (AI)

---

## Scaling Strategy

Phase 1:

* Single worker

Phase 2:

* Multiple workers
* Queue locking via DB row updates

Phase 3:

* Migrate to Redis if needed

---

## Failure Strategy

If scan crashes:

* Mark as failed
* Store error message
* Notify user
