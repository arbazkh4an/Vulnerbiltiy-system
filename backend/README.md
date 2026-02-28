# SentinelAI — Backend

AI-powered OWASP web security scanner backend built with **FastAPI + Python 3.11**.

## Architecture

```
backend/
├── app/
│   ├── main.py              ← FastAPI entry point
│   ├── config.py             ← Pydantic Settings
│   ├── logging.py            ← structlog JSON logging
│   ├── api/                  ← API routes (scan, history, health)
│   ├── core/                 ← Security, validation, rate limiting, exceptions
│   ├── models/               ← Pydantic request/response schemas
│   ├── services/             ← AI service, scan orchestration, PDF generation
│   ├── scanners/             ← Header, SSL, Path, CVE scanners
│   ├── db/                   ← asyncpg session + repositories
│   └── worker/               ← Background scan worker
├── tests/                    ← pytest test suites
├── migration.sql             ← Database schema migration
├── Dockerfile                ← Production container
├── render.yaml               ← Render deployment (web + worker)
├── requirements.txt          ← Python dependencies
└── .env.example              ← Environment variable template
```

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with DATABASE_URL, GROQ_API_KEY, etc.

# 3. Run database migration
# Execute migration.sql against your PostgreSQL database

# 4. Start API server
uvicorn app.main:app --reload --port 5000

# 5. Start background worker (separate terminal)
python -m app.worker.worker
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/scan` | Submit URL for scanning |
| GET | `/api/scan/{id}` | Get scan status + results |
| GET | `/api/history` | Paginated scan history |
| GET | `/api/health` | System health check |

## Running Tests

```bash
pip install pytest pytest-asyncio
pytest tests/ -v
```

## Deployment

Configured for **Render** with two services:
- **Web Service**: FastAPI API server via uvicorn
- **Worker Service**: Background scan processor

See `render.yaml` for configuration.
