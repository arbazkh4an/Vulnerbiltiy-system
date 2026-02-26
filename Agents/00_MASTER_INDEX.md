# OWASP AI Scanner — Sub-Agent Task Index
## How to use this folder
Each file = one sub-agent's complete job.
Give the file to the agent. It reads it, builds it, tests it, and returns output.
Agents are mostly independent. Deploy in the order shown.

---

## DEPLOYMENT ORDER & DEPENDENCY MAP

```
PHASE 1 — Infrastructure (no dependencies)
  01_agent_database_setup.md
  02_agent_redis_queue.md
  03_agent_docker_compose.md

PHASE 2 — Backend Core (needs Phase 1)
  04_agent_fastapi_core.md
  05_agent_websocket_server.md

PHASE 3 — Passive Scanners (needs Phase 2)
  06_agent_scanner_base.md
  07_agent_header_scanner.md
  08_agent_ssl_scanner.md
  09_agent_recon_scanner.md
  10_agent_sri_scanner.md

PHASE 4 — Active Scanners (needs Phase 3)
  11_agent_path_scanner.md
  12_agent_auth_scanner.md
  13_agent_cve_scanner.md

PHASE 5 — Injection (needs Phase 4)
  14_agent_injection_scanner.md

PHASE 6 — Orchestration (needs all scanners)
  15_agent_orchestrator.md
  16_agent_json_merger.md

PHASE 7 — AI Engine (needs Phase 6)
  17_agent_ai_engine.md
  18_agent_prompt_builder.md

PHASE 8 — Frontend (can start at Phase 2)
  19_agent_frontend_shell.md
  20_agent_frontend_results_ui.md

PHASE 9 — Security & Hardening (needs everything)
  21_agent_rate_limiter.md
  22_agent_url_validator.md
  23_agent_integration_tests.md
```

---

## AGENT OUTPUT CONTRACT
Every agent must produce:
1. Working code files
2. A test file named `test_<agent_name>.py`
3. A `STATUS.md` confirming: tests pass / known issues

---

## SHARED CONSTANTS (All agents use these)
```
Redis URL:       redis://localhost:6379
Postgres URL:    postgresql://scanner:scanner@localhost:5432/scannerdb
Backend port:    8000
Frontend port:   3000
Max scan time:   120 seconds
```
