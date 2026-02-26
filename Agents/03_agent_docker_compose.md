# AGENT 03 — Docker Compose & Container Setup
**Depends on:** Nothing (but sets up environment that agents 01 & 02 run inside)
**Output goes to:** `docker/` and root `/`

---

## YOUR JOB
Create all Docker and Docker Compose configuration so the entire project runs with one command: `docker-compose up`

---

## FILES TO CREATE

### `docker-compose.yml` (root level)
Define these services:

**postgres**
- Image: postgres:15
- Env: POSTGRES_USER=scanner, POSTGRES_PASSWORD=scanner, POSTGRES_DB=scannerdb
- Port: 5432:5432
- Volume: postgres_data:/var/lib/postgresql/data
- Healthcheck: pg_isready every 5s

**redis**
- Image: redis:7-alpine
- Port: 6379:6379
- Healthcheck: redis-cli ping every 5s

**backend**
- Build: ./docker/Dockerfile.backend
- Port: 8000:8000
- Env: DATABASE_URL, REDIS_URL
- Depends on: postgres, redis (healthy)
- Volume: ./backend:/app (for dev hot reload)
- Command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

**worker**
- Build: ./docker/Dockerfile.worker
- Env: DATABASE_URL, REDIS_URL
- Depends on: postgres, redis (healthy)
- Command: celery -A queue.celery_app worker --loglevel=info -Q scan_queue,ai_queue
- Scale: 2 (two worker replicas by default)

**frontend**
- Build: ./docker/Dockerfile.frontend
- Port: 3000:3000
- Depends on: backend
- Volume: ./frontend:/app

### `docker/Dockerfile.backend`
- Base: python:3.11-slim
- Install: gcc, libpq-dev (for asyncpg)
- Copy requirements, install packages
- Working dir: /app
- Expose 8000

### `docker/Dockerfile.worker`
- Base: python:3.11-slim
- Same as backend but no port expose
- Install security tools via apt: nmap, curl
- Install Python packages including scanners

### `docker/Dockerfile.frontend`
- Base: node:20-alpine
- npm install, expose 3000

### `docker/.env.example`
```
DATABASE_URL=postgresql://scanner:scanner@postgres:5432/scannerdb
REDIS_URL=redis://redis:6379
GROQ_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
SECRET_KEY=change_this_in_production
MAX_SCANS_PER_HOUR=5
```

### `docker/init.sql`
- SQL script that runs on first postgres boot
- Copies schema from `database/schema.sql`
- Creates indexes on scans.status, scans.created_at

---

## TESTS TO WRITE
File: `docker/test_docker.sh` (bash script)

- Test: `docker-compose config` validates without error
- Test: `docker-compose up -d postgres redis` starts successfully
- Test: postgres accepts connections on 5432
- Test: redis responds to PING on 6379
- Test: `docker-compose down` cleans up completely

---

## DONE WHEN
`docker-compose up` starts all services without errors. All bash tests pass.
Return all files.
