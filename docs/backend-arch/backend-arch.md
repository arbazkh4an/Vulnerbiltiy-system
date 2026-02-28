SentinelAI — Backend Architecture

Stack: FastAPI + Python 3.11

Deployment Target: Render Web Service + Render Worker

Database: Supabase PostgreSQL

1️⃣ Backend Architectural Principles

Async-first design (FastAPI + asyncio)

Zero blocking HTTP calls

Database-backed job queue

Strict schema contracts (Pydantic)

Structured logging

Security-first validation

Clear separation:

API Layer

Domain Logic

Scanner Engine

AI Engine

Worker Engine

Security Controls

2️⃣ Folder Structure

backend/

│

├── app/

│   ├── main.py

│   ├── config.py

│   ├── logging.py

│   │

│   ├── api/

│   │   ├── routes_scan.py

│   │   ├── routes_history.py

│   │   └── routes_health.py

│   │

│   ├── core/

│   │   ├── security.py

│   │   ├── rate_limit.py

│   │   ├── validators.py

│   │   └── exceptions.py

│   │

│   ├── models/

│   │   ├── scan_models.py

│   │   └── ai_models.py

│   │

│   ├── services/

│   │   ├── scan_service.py

│   │   ├── ai_service.py

│   │   └── report_service.py

│   │

│   ├── scanners/

│   │   ├── base.py

│   │   ├── header_scanner.py

│   │   ├── ssl_scanner.py

│   │   ├── path_scanner.py

│   │   └── cve_scanner.py

│   │

│   ├── db/

│   │   ├── session.py

│   │   └── repositories.py

│   │

│   └── worker/

│       └── worker.py

3️⃣ FastAPI Application Core

main.py

Responsibilities:

Initialize FastAPI app

Include routers

Add CORS middleware

Add global exception handlers

Health endpoint

Example:

app = FastAPI(

    title="SentinelAI API",

    version="1.0.0"

)

app.include_router(scan_router, prefix="/api")

app.include_router(history_router, prefix="/api")

4️⃣ API Endpoints

POST /api/scan

Creates new scan.

Flow:

Validate URL

Block private IP ranges

Check rate limit

Insert record into DB

Return scan_id

Response:

{

  "scan_id": "uuid",

  "status": "queued"

}

GET /api/scan/{scan_id}

Returns:

{

  "id": "uuid",

  "status": "running",

  "progress": 60,

  "report": { ...optional... }

}

GET /api/history

Returns user scan history.

GET /api/health

Returns system health.

5️⃣ Scan Service Layer

scan_service.py

Responsibilities:

Create scan record

Update scan status

Fetch queued jobs

Store raw scan results

Store AI report

Key functions:

async def create_scan(user_id: UUID, url: str) -> UUID

async def update_status(scan_id: UUID, status: str)

async def get_queued_scan()

async def store_raw_results(scan_id: UUID, results: dict)

async def store_ai_report(scan_id: UUID, report: dict)

6️⃣ Worker Engine

Runs as separate Render Worker.

worker.py

Loop:

while True:

    job = get_queued_scan()

    if job:

    mark_running(job.id)

    results = run_all_scanners(job.url)

    store_raw_results(job.id, results)

    ai_report = generate_ai_report(results)

    store_ai_report(job.id, ai_report)

    mark_complete(job.id)

    sleep(5)

Concurrency model:

Single worker (MVP)

Later: multiple workers with row-level locking

7️⃣ Scanner Engine

Scanner Contract

base.py

class BaseScanner:

    async def run(self, url: str) -> dict:

    raise NotImplementedError

header_scanner.py

Checks:

Missing security headers

Server disclosure

CORS misconfiguration

ssl_scanner.py

Checks:

TLS version

Certificate expiry

Weak ciphers

HSTS

path_scanner.py

Checks:

/.env

/.git

/backup.zip

/admin

Uses:

Async HTTP client

Timeout per request

Safe payloads only

cve_scanner.py

Uses:

Detected tech stack

NVD API lookup

Version matching

8️⃣ AI Service

ai_service.py

Responsibilities:

Build structured prompt

Send JSON to LLM

Validate JSON response

Enforce schema

Output contract:

{

  "scan_id": "uuid",

  "risk_score": 75,

  "summary": "...",

  "findings": [...]

}

Strict JSON validation via Pydantic.

9️⃣ Security Layer

URL Validation

Reject:

localhost

127.0.0.1

10.x.x.x

172.16.x.x

192.168.x.x

Internal IPv6

Rate Limiting

Strategy:

Count scans per user per hour

Query DB

Reject if > 5

Consent Logging

Store consent flag

Store timestamp

Store IP

🔟 Logging Strategy

Use structured logs:

logger.info("scan_started", scan_id=scan_id, url=url)

Log:

Start

Scanner errors

AI errors

Completion

1️⃣1️⃣ Error Handling

Custom exceptions:

InvalidURLException

RateLimitExceeded

PrivateIPBlocked

ScanFailed

Global exception middleware returns structured JSON errors.

1️⃣2️⃣ Performance Constraints

All HTTP calls async

Timeout: 10–30s max

Total scan target: < 90s

No blocking DB operations
