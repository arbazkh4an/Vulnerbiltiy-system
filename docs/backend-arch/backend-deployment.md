# SentinelAI — Backend Deployment Guide

Complete step-by-step guide to deploy the FastAPI backend and worker to production on **Render**.

---

## Prerequisites

- [x] Database set up and migration applied (see [db-setup.md](./db-setup.md))
- [x] GitHub repository pushed with the latest code
- [x] Accounts on: [Render](https://render.com), [Groq](https://console.groq.com), and optionally [NVD](https://nvd.nist.gov/developers/request-an-api-key)

---

## Step 1: Get Your API Keys

### 1.1 DATABASE_URL (Neon PostgreSQL)

Already obtained during database setup. Format:
```
postgresql://user:password@ep-xxx.region.aws.neon.tech/neondb?sslmode=require
```

### 1.2 GROQ_API_KEY (AI Reports — Primary)

1. Go to [console.groq.com](https://console.groq.com)
2. Sign up / log in (free tier: 14,400 requests/day)
3. Go to **API Keys** → **Create API Key**
4. Name it `sentinelai-production`
5. Copy the key — starts with `gsk_...`

> **Why Groq?** — Fastest inference (sub-second for Llama 3.3 70B), generous free tier. Perfect for MVP.

### 1.3 OPENAI_API_KEY (AI Reports — Fallback, Optional)

1. Go to [platform.openai.com](https://platform.openai.com)
2. Go to **API Keys** → **Create new secret key**
3. Name it `sentinelai-fallback`
4. Copy the key — starts with `sk-...`

> Only charged if Groq is down. Uses `gpt-4o-mini` ($0.15/1M input tokens).

### 1.4 NVD_API_KEY (CVE Scanner — Optional but Recommended)

1. Go to [nvd.nist.gov/developers/request-an-api-key](https://nvd.nist.gov/developers/request-an-api-key)
2. Fill in your email
3. Check your email for the API key

> **Without key**: 5 requests per 30 seconds. **With key**: 50 requests per 30 seconds.

### 1.5 JWT_SECRET (Token Verification)

Generate a secure 64-character random string:

```bash
# macOS/Linux
openssl rand -hex 32

# PowerShell (Windows)
-join ((1..64) | ForEach-Object { '{0:x}' -f (Get-Random -Maximum 16) })

# Or use: https://generate-secret.vercel.app/64
```

> If your frontend uses Clerk and acts as the auth gate (passing user IDs directly), you can leave this empty — the backend will accept raw user IDs as tokens.

---

## Step 2: Deploy to Render

### 2.1 Connect Repository

1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Click **New** → **Blueprint**
3. Connect your GitHub repository
4. Render will detect `backend/render.yaml` automatically
5. It will create **two services**:
   - `sentinelai-api` (Web Service)
   - `sentinelai-worker` (Background Worker)

### 2.2 Configure Environment Variables

For **both** services, set these env vars in the Render dashboard:

| Variable | Value | Required |
|----------|-------|----------|
| `DATABASE_URL` | Your Neon connection string | ✅ Yes |
| `GROQ_API_KEY` | `gsk_...` from Step 1.2 | ✅ Yes |
| `OPENAI_API_KEY` | `sk-...` from Step 1.3 | ❌ Optional |
| `NVD_API_KEY` | From Step 1.4 | ❌ Optional |
| `JWT_SECRET` | 64-char hex from Step 1.5 | ❌ Optional |
| `CORS_ORIGINS` | `["https://your-frontend.vercel.app"]` | ✅ Yes |
| `LOG_LEVEL` | `INFO` | ❌ Has default |
| `SCAN_TIMEOUT` | `30` | ❌ Has default |
| `RATE_LIMIT_MAX` | `5` | ❌ Has default |

### 2.3 Deploy

1. Click **Apply** on the Blueprint
2. Render will build and deploy both services
3. Build takes ~2 minutes

---

## Step 3: Verify Deployment

### 3.1 Check API Health

```bash
curl https://sentinelai-api.onrender.com/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "SentinelAI API",
  "version": "1.0.0",
  "db": "connected"
}
```

### 3.2 Check Worker Logs

In Render dashboard → `sentinelai-worker` → **Logs**. You should see:
```
{"event": "worker_ready", ...}
```

### 3.3 Test a Scan (Manual)

```bash
curl -X POST https://sentinelai-api.onrender.com/api/scan \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test-user-123" \
  -d '{"url": "https://example.com", "consent": true}'
```

Expected:
```json
{"scan_id": "uuid-here", "status": "queued"}
```

Then poll:
```bash
curl https://sentinelai-api.onrender.com/api/scan/UUID-HERE \
  -H "Authorization: Bearer test-user-123"
```

---

## Step 4: Connect Frontend

### 4.1 Update Vercel Environment

In your Vercel project settings, update/remove:

| Variable | Action |
|----------|--------|
| `BACKEND_URL` | **Remove** — no longer needed (scans are queue-based) |
| `DATABASE_URL` | Keep — same Neon connection string |

### 4.2 Redeploy Frontend

```bash
vercel --prod
```

The frontend now inserts scans as `queued` directly into the database. The Render worker picks them up automatically.

---

## Architecture in Production

```
User → Vercel (Next.js)
         ↓ INSERT scan (queued)
       Neon PostgreSQL ← Render Worker (polls every 5s)
         ↑                    ↓
       Results           4 Scanners + AI Report
```

---

## Monitoring & Troubleshooting

| Symptom | Diagnosis | Fix |
|---------|-----------|-----|
| Health returns `"db": "error"` | Database connection failed | Check `DATABASE_URL`, ensure `?sslmode=require` |
| Scans stay `queued` forever | Worker not running | Check Render worker logs, ensure it's deployed |
| AI report is rule-based fallback | No API key configured | Add `GROQ_API_KEY` to worker env vars |
| `429 Rate limit exceeded` | User hit 5 scans/hour limit | Wait, or increase `RATE_LIMIT_MAX` |
| `403 Private IP blocked` | SSRF protection triggered | User tried to scan localhost/internal IPs |
| Worker crashes on startup | Missing `DATABASE_URL` | Add env var to the worker service |
| Slow CVE scan | No NVD API key | Add `NVD_API_KEY` for 10x higher rate limit |

---

## Scaling (When You Need It)

| What | How |
|------|-----|
| More concurrent scans | Add more worker instances on Render |
| Faster API response | Increase uvicorn `--workers` in Dockerfile |
| Higher rate limits | Increase `RATE_LIMIT_MAX` env var |
| Multiple regions | Deploy worker in additional Render regions |
