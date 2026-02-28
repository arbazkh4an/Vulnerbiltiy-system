# SentinelAI — Database Design

**Database:** Supabase PostgreSQL

**Extensions:** uuid-ossp, pgcrypto

---

## 1️⃣ Design Principles

* Normalized structure
* JSONB for flexible scan data
* Strict constraints
* Indexed critical fields
* RLS enforced
* Audit logging

---

## 2️⃣ Tables Overview

<pre class="overflow-visible! px-0!" data-start="5445" data-end="5511"><div class="relative w-full my-4"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class=""><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼk ͼy"><div class="cm-scroller"><div class="cm-content q9tKkq_readonly"><span>users</span><br/><span>scans</span><br/><span>scan_results</span><br/><span>ai_reports</span><br/><span>rate_limits</span><br/><span>audit_logs</span></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

---

## 3️⃣ users

<pre class="overflow-visible! px-0!" data-start="5532" data-end="5662"><div class="relative w-full my-4"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class=""><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼk ͼy"><div class="cm-scroller"><div class="cm-content q9tKkq_readonly"><span class="ͼn">CREATE</span><span></span><span class="ͼn">TABLE</span><span> users (</span><br/><span>    id UUID </span><span class="ͼn">PRIMARY</span><span></span><span class="ͼn">KEY</span><span>,</span><br/><span>    email TEXT </span><span class="ͼn">UNIQUE</span><span></span><span class="ͼn">NOT</span><span></span><span class="ͼq">NULL</span><span>,</span><br/><span>    created_at </span><span class="ͼt">TIMESTAMP</span><span></span><span class="ͼn">DEFAULT</span><span> NOW()</span><br/><span>);</span></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

Managed via Supabase Auth.

---

## 4️⃣ scans

Core job queue table.

<pre class="overflow-visible! px-0!" data-start="5734" data-end="6134"><div class="relative w-full my-4"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class=""><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼk ͼy"><div class="cm-scroller"><div class="cm-content q9tKkq_readonly"><span class="ͼn">CREATE</span><span></span><span class="ͼn">TABLE</span><span> scans (</span><br/><span>    id UUID </span><span class="ͼn">PRIMARY</span><span></span><span class="ͼn">KEY</span><span></span><span class="ͼn">DEFAULT</span><span> gen_random_uuid(),</span><br/><span>    user_id UUID </span><span class="ͼn">REFERENCES</span><span> users(id),</span><br/><span>    url TEXT </span><span class="ͼn">NOT</span><span></span><span class="ͼq">NULL</span><span>,</span><br/><span>    status TEXT </span><span class="ͼn">NOT</span><span></span><span class="ͼq">NULL</span><span></span><span class="ͼn">CHECK</span><span> (</span><br/><span>        status </span><span class="ͼn">IN</span><span> (</span><span class="ͼr">'queued'</span><span>,</span><span class="ͼr">'running'</span><span>,</span><span class="ͼr">'complete'</span><span>,</span><span class="ͼr">'failed'</span><span>)</span><br/><span>    ),</span><br/><span>    progress </span><span class="ͼt">INT</span><span></span><span class="ͼn">DEFAULT</span><span></span><span class="ͼq">0</span><span>,</span><br/><span>    consent_given </span><span class="ͼt">BOOLEAN</span><span></span><span class="ͼn">NOT</span><span></span><span class="ͼq">NULL</span><span>,</span><br/><span>    requester_ip TEXT,</span><br/><span>    created_at </span><span class="ͼt">TIMESTAMP</span><span></span><span class="ͼn">DEFAULT</span><span> NOW(),</span><br/><span>    completed_at </span><span class="ͼt">TIMESTAMP</span><br/><span>);</span></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

Indexes:

<pre class="overflow-visible! px-0!" data-start="6146" data-end="6251"><div class="relative w-full my-4"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class=""><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼk ͼy"><div class="cm-scroller"><div class="cm-content q9tKkq_readonly"><span class="ͼn">CREATE</span><span> INDEX idx_scans_status </span><span class="ͼn">ON</span><span> scans(status);</span><br/><span class="ͼn">CREATE</span><span> INDEX idx_scans_user </span><span class="ͼn">ON</span><span> scans(user_id);</span></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

---

## 5️⃣ scan_results

Stores raw scanner output.

<pre class="overflow-visible! px-0!" data-start="6307" data-end="6524"><div class="relative w-full my-4"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class=""><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼk ͼy"><div class="cm-scroller"><div class="cm-content q9tKkq_readonly"><span class="ͼn">CREATE</span><span></span><span class="ͼn">TABLE</span><span> scan_results (</span><br/><span>    id UUID </span><span class="ͼn">PRIMARY</span><span></span><span class="ͼn">KEY</span><span></span><span class="ͼn">DEFAULT</span><span> gen_random_uuid(),</span><br/><span>    scan_id UUID </span><span class="ͼn">REFERENCES</span><span> scans(id) </span><span class="ͼn">ON</span><span></span><span class="ͼn">DELETE</span><span></span><span class="ͼn">CASCADE</span><span>,</span><br/><span>    raw_data JSONB </span><span class="ͼn">NOT</span><span></span><span class="ͼq">NULL</span><span>,</span><br/><span>    created_at </span><span class="ͼt">TIMESTAMP</span><span></span><span class="ͼn">DEFAULT</span><span> NOW()</span><br/><span>);</span></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

Index:

<pre class="overflow-visible! px-0!" data-start="6534" data-end="6608"><div class="relative w-full my-4"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class=""><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼk ͼy"><div class="cm-scroller"><div class="cm-content q9tKkq_readonly"><span class="ͼn">CREATE</span><span> INDEX idx_scan_results_scan_id </span><span class="ͼn">ON</span><span> scan_results(scan_id);</span></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

---

## 6️⃣ ai_reports

Structured AI output.

<pre class="overflow-visible! px-0!" data-start="6657" data-end="6890"><div class="relative w-full my-4"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class=""><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼk ͼy"><div class="cm-scroller"><div class="cm-content q9tKkq_readonly"><span class="ͼn">CREATE</span><span></span><span class="ͼn">TABLE</span><span> ai_reports (</span><br/><span>    id UUID </span><span class="ͼn">PRIMARY</span><span></span><span class="ͼn">KEY</span><span></span><span class="ͼn">DEFAULT</span><span> gen_random_uuid(),</span><br/><span>    scan_id UUID </span><span class="ͼn">REFERENCES</span><span> scans(id) </span><span class="ͼn">ON</span><span></span><span class="ͼn">DELETE</span><span></span><span class="ͼn">CASCADE</span><span>,</span><br/><span>    risk_score </span><span class="ͼt">INT</span><span>,</span><br/><span>    report JSONB </span><span class="ͼn">NOT</span><span></span><span class="ͼq">NULL</span><span>,</span><br/><span>    created_at </span><span class="ͼt">TIMESTAMP</span><span></span><span class="ͼn">DEFAULT</span><span> NOW()</span><br/><span>);</span></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

---

## 7️⃣ rate_limits

Tracks usage.

<pre class="overflow-visible! px-0!" data-start="6932" data-end="7136"><div class="relative w-full my-4"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class=""><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼk ͼy"><div class="cm-scroller"><div class="cm-content q9tKkq_readonly"><span class="ͼn">CREATE</span><span></span><span class="ͼn">TABLE</span><span> rate_limits (</span><br/><span>    id UUID </span><span class="ͼn">PRIMARY</span><span></span><span class="ͼn">KEY</span><span></span><span class="ͼn">DEFAULT</span><span> gen_random_uuid(),</span><br/><span>    user_id UUID </span><span class="ͼn">REFERENCES</span><span> users(id),</span><br/><span>    request_count </span><span class="ͼt">INT</span><span></span><span class="ͼn">DEFAULT</span><span></span><span class="ͼq">0</span><span>,</span><br/><span>    window_start </span><span class="ͼt">TIMESTAMP</span><span></span><span class="ͼn">DEFAULT</span><span> NOW()</span><br/><span>);</span></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

---

## 8️⃣ audit_logs

Security compliance.

<pre class="overflow-visible! px-0!" data-start="7184" data-end="7386"><div class="relative w-full my-4"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class=""><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼk ͼy"><div class="cm-scroller"><div class="cm-content q9tKkq_readonly"><span class="ͼn">CREATE</span><span></span><span class="ͼn">TABLE</span><span> audit_logs (</span><br/><span>    id UUID </span><span class="ͼn">PRIMARY</span><span></span><span class="ͼn">KEY</span><span></span><span class="ͼn">DEFAULT</span><span> gen_random_uuid(),</span><br/><span>    user_id UUID,</span><br/><span>    scan_id UUID,</span><br/><span></span><span class="ͼn">action</span><span> TEXT,</span><br/><span>    metadata JSONB,</span><br/><span>    created_at </span><span class="ͼt">TIMESTAMP</span><span></span><span class="ͼn">DEFAULT</span><span> NOW()</span><br/><span>);</span></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

---

## 9️⃣ Row Level Security (RLS)

Enable RLS:

<pre class="overflow-visible! px-0!" data-start="7439" data-end="7494"><div class="relative w-full my-4"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class=""><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼk ͼy"><div class="cm-scroller"><div class="cm-content q9tKkq_readonly"><span class="ͼn">ALTER</span><span></span><span class="ͼn">TABLE</span><span> scans ENABLE </span><span class="ͼn">ROW</span><span></span><span class="ͼn">LEVEL</span><span> SECURITY;</span></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

Policy:

<pre class="overflow-visible! px-0!" data-start="7505" data-end="7601"><div class="relative w-full my-4"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class=""><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼk ͼy"><div class="cm-scroller"><div class="cm-content q9tKkq_readonly"><span class="ͼn">CREATE</span><span> POLICY </span><span class="ͼr">"Users see own scans"</span><br/><span class="ͼn">ON</span><span> scans</span><br/><span class="ͼn">FOR</span><span></span><span class="ͼn">SELECT</span><br/><span class="ͼn">USING</span><span> (auth.uid() </span><span class="ͼn">=</span><span> user_id);</span></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

Repeat for:

* scan_results
* ai_reports

---

## 🔟 Queue Mechanism

Worker fetches:

<pre class="overflow-visible! px-0!" data-start="7689" data-end="7797"><div class="relative w-full my-4"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class=""><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼk ͼy"><div class="cm-scroller"><div class="cm-content q9tKkq_readonly"><span class="ͼn">SELECT</span><span></span><span class="ͼn">*</span><span></span><span class="ͼn">FROM</span><span> scans</span><br/><span class="ͼn">WHERE</span><span> status</span><span class="ͼn">=</span><span class="ͼr">'queued'</span><br/><span class="ͼn">ORDER</span><span></span><span class="ͼn">BY</span><span> created_at </span><span class="ͼn">ASC</span><br/><span class="ͼn">LIMIT</span><span></span><span class="ͼq">1</span><br/><span class="ͼn">FOR</span><span></span><span class="ͼn">UPDATE</span><span> SKIP LOCKED;</span></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

Then:

<pre class="overflow-visible! px-0!" data-start="7806" data-end="7866"><div class="relative w-full my-4"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class=""><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼk ͼy"><div class="cm-scroller"><div class="cm-content q9tKkq_readonly"><span class="ͼn">UPDATE</span><span> scans</span><br/><span class="ͼn">SET</span><span> status</span><span class="ͼn">=</span><span class="ͼr">'running'</span><br/><span class="ͼn">WHERE</span><span> id</span><span class="ͼn">=</span><span class="ͼr">'...'</span><span>;</span></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

This prevents duplicate workers processing same job.

---

## 1️⃣1️⃣ Data Retention Policy

* Raw scan data retained 90 days
* AI reports retained indefinitely
* Failed scans retained 30 days

Optional cleanup job via cron worker.

---

## 1️⃣2️⃣ Performance Considerations

* JSONB indexed if necessary
* Partition scans table if > 1M records
* Archive old scans to cold storage
* Monitor slow queries

---

## 1️⃣3️⃣ Backup Strategy

* Supabase automated backups
* Weekly export
* Audit logs immutable
