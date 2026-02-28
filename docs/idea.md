## Project Name

**SentinelAI — Intelligent OWASP Web Security Scanner**

---

## Vision

Build a lightweight, AI-powered web security scanning platform that:

* Performs automated OWASP-based scans
* Analyzes findings using LLM reasoning
* Produces structured vulnerability reports
* Operates on a simplified PaaS infrastructure (Supabase + Render)
* Requires no Docker or heavy DevOps

---

## Core Problem

Small developers and students:

* Don’t understand OWASP Top 10 risks
* Don’t know how to interpret raw scanner output
* Lack affordable, simple security analysis tools

---

## Solution

A web app where users:

1. Enter a URL
2. System performs passive + active checks
3. Results are structured into JSON
4. AI converts raw findings into professional vulnerability reports
5. User sees severity-based report with recommendations

---

## Target Users

* CS students
* Freelance web developers
* Startup founders
* Ethical hacking learners
* Portfolio builders

---

## Unique Value Proposition

* AI explains findings in human-readable format
* Async scanning with live updates
* No complex infrastructure
* Clean, minimal UX
* Educational positioning

---

## MVP Scope

Include:

* Header analysis
* SSL/TLS check
* Basic path exposure scan
* Simple injection probes (safe test payloads)
* CVE lookup
* AI-generated report

Exclude (Phase 2+):

* Bruteforce testing
* Full SQLMap integration
* Advanced fuzzing
* Multi-target batch scanning
