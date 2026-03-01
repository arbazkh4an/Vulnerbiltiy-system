# VulnScan AI - Complete System Documentation

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Directory Structure](#3-directory-structure)
4. [Frontend (Next.js)](#4-frontend-nextjs)
5. [Backend (FastAPI)](#5-backend-fastapi)
6. [Database Schema](#6-database-schema)
7. [Vulnerability Scanners](#7-vulnerability-scanners)
8. [Background Worker](#8-background-worker)
9. [AI Analysis Service](#9-ai-analysis-service)
10. [API Endpoints](#10-api-endpoints)
11. [Security Features](#11-security-features)
12. [Dependencies](#12-dependencies)
13. [System Flow Diagrams](#13-system-flow-diagrams)
14. [Configuration](#14-configuration)
15. [Running the Application](#15-running-the-application)

---

## 1. Project Overview

**VulnScan AI** is an AI-powered web vulnerability scanning system that targets the OWASP Top 10:2025 vulnerabilities. It provides automated security scanning with intelligent analysis using Large Language Models (LLM).

### Key Features

- **Multi-scanner architecture**: 4 independent scanners running in parallel
- **AI-powered analysis**: Groq/OpenAI integration for intelligent vulnerability reporting
- **Real-time progress**: Live scan status updates
- **PDF reports**: Downloadable vulnerability reports
- **Rate limiting**: Prevents abuse
- **SSRF protection**: Blocks scanning of internal/private networks

### Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 16, React 19, Tailwind CSS, Radix UI |
| Backend | FastAPI, Python 3.x |
| Database | PostgreSQL (Neon) |
| AI | Groq (primary), OpenAI (fallback) |
| Worker | Async Python worker with database polling |

---

## 2. System Architecture

The application uses a **split architecture** with three independent processes:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         VULNSCAN AI SYSTEM                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────┐    ┌─────────────────────┐                   │
│  │    FRONTEND         │    │    BACKEND API      │                   │
│  │   (Next.js)         │    │    (FastAPI)        │                   │
│  │   Port: 3000        │    │    Port: 3001       │                   │
│  │                     │    │                     │                   │
│  │  - User Interface   │    │  - REST API         │                   │
│  │  - Dashboard        │    │  - URL Validation   │                   │
│  │  - Scan Results     │    │  - Rate Limiting    │                   │
│  │  - PDF Generation   │    │  - Auth             │                   │
│  └──────────┬──────────┘    └──────────┬──────────┘                   │
│             │                           │                               │
│             │         HTTP              │                               │
│             └───────────────────────────┘                               │
│                                 │                                         │
│                                 ▼                                         │
│                        ┌─────────────────┐                                │
│                        │   POSTGRESQL    │                                │
│                        │   (Neon DB)    │                                │
│                        │                 │                                │
│                        │  - scans       │                                │
│                        │  - results     │                                │
│                        │  - vulnerabilities│                            │
│                        └────────┬────────┘                                │
│                                 │                                         │
│                                 │ Polling (5s)                            │
│                                 ▼                                         │
│                        ┌─────────────────┐                                │
│                        │   WORKER        │                                │
│                        │   (Python)      │                                │
│                        │                 │                                │
│                        │  - Poll DB      │                                │
│                        │  - Run scanners │                                │
│                        │  - AI analysis  │                                │
│                        │  - Update DB    │                                │
│                        └─────────────────┘                                │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Process Communication

1. **User** submits URL via frontend
2. **Frontend** calls Backend API → validates → inserts scan as "queued" → returns scan_id
3. **Worker** polls database every 5 seconds for queued scans
4. **Worker** picks up scan → runs all 4 scanners → stores raw results → generates AI report → updates status to "completed"
5. **Frontend** polls for status → displays results when complete

---

## 3. Directory Structure

```
Vulnerbiltiy-system/
├── app/                          # Next.js frontend (App Router)
│   ├── api/                      # Frontend API routes (proxies to backend)
│   │   └── scans/
│   │       ├── route.ts          # GET scans list
│   │       ├── start/
│   │       │   └── route.ts      # POST start scan
│   │       └── [id]/
│   │           ├── route.ts      # GET scan details
│   │           └── pdf/
│   │               └── route.ts  # GET PDF report
│   ├── dashboard/
│   │   └── page.tsx              # User dashboard
│   ├── scan/
│   │   └── [id]/
│   │       └── page.tsx          # Scan results page
│   ├── login/
│   │   └── page.tsx              # Login page
│   ├── register/
│   │   └── page.tsx              # Registration page
│   ├── page.tsx                  # Landing page
│   └── globals.css               # Global styles
│
├── backend/                      # FastAPI backend
│   ├── app/
│   │   ├── api/                  # API route handlers
│   │   │   ├── routes_scan.py    # Scan endpoints
│   │   │   ├── routes_history.py# History endpoints
│   │   │   └── routes_health.py # Health check
│   │   ├── core/                # Security & validation
│   │   │   ├── security.py      # JWT authentication
│   │   │   ├── validators.py    # URL validation
│   │   │   ├── rate_limit.py    # Rate limiting
│   │   │   └── exceptions.py    # Custom exceptions
│   │   ├── db/                   # Database layer
│   │   │   ├── session.py        # Connection pool
│   │   │   └── repositories.py  # CRUD operations
│   │   ├── models/               # Pydantic schemas
│   │   │   ├── scan_models.py    # Scan schemas
│   │   │   └── ai_models.py      # AI report schemas
│   │   ├── scanners/             # Vulnerability scanners
│   │   │   ├── base.py           # Base scanner interface
│   │   │   ├── ssl_scanner.py   # SSL/TLS scanner
│   │   │   ├── header_scanner.py# HTTP header scanner
│   │   │   ├── path_scanner.py   # Sensitive path scanner
│   │   │   └── cve_scanner.py   # CVE detector
│   │   ├── services/             # Business logic
│   │   │   ├── scan_service.py  # Scan orchestration
│   │   │   └── ai_service.py    # AI report generation
│   │   ├── worker/               # Background worker
│   │   │   └── worker.py         # Async worker
│   │   ├── config.py             # Configuration
│   │   ├── logging.py            # Logging setup
│   │   └── main.py               # FastAPI entry point
│   ├── requirements.txt          # Python dependencies
│   ├── migration.sql             # Database schema
│   ├── Dockerfile                # Container build
│   └── render.yaml               # Render deployment config
│
├── components/                   # React UI components
│   ├── site-header.tsx           # Navigation header
│   ├── hero-section.tsx          # Landing hero
│   ├── features-section.tsx      # Features display
│   ├── scanners-section.tsx      # Scanner info
│   ├── methodology-section.tsx   # How it works
│   ├── pricing-section.tsx       # Pricing tiers
│   ├── ui/                       # Radix UI components
│   └── pdf/
│       └── VulnerabilityReportDocument.tsx  # PDF template
│
├── hooks/                        # Custom React hooks
│   ├── use-rate-limiter.ts       # Client-side rate limiting
│   ├── use-debounce.ts           # Input debouncing
│   ├── use-local-storage.ts      # LocalStorage wrapper
│   ├── use-mobile.ts             # Mobile detection
│   └── use-toast.ts              # Toast notifications
│
├── lib/                          # Utilities
│   ├── db.ts                     # Database connection
│   ├── rate-limit.ts             # Rate limiting logic
│   ├── utils.ts                  # General utilities
│   └── types.ts                  # TypeScript types
│
├── docs/                         # Documentation
│
├── public/                       # Static assets
│
├── package.json                  # NPM dependencies
└── README.md                     # Project readme
```

---

## 4. Frontend (Next.js)

### Pages/Routes

| Route | File | Purpose |
|-------|------|---------|
| `/` | `app/page.tsx` | Landing page with hero, features, pricing |
| `/dashboard` | `app/dashboard/page.tsx` | User dashboard - scan management, history table |
| `/scan/[id]` | `app/scan/[id]/page.tsx` | Scan results detail with vulnerability listing |
| `/login` | `app/login/page.tsx` | User login (Clerk integration) |
| `/register` | `app/register/page.tsx` | User registration |

### Frontend API Routes

| Route | Method | File | Purpose |
|-------|--------|------|---------|
| `/api/scans` | GET | `app/api/scans/route.ts` | Fetch paginated scan history |
| `/api/scans/start` | POST | `app/api/scans/start/route.ts` | Start new vulnerability scan |
| `/api/scans/[id]` | GET | `app/api/scans/[id]/route.ts` | Get scan details & vulnerabilities |
| `/api/scans/[id]/pdf` | GET | `app/api/scans/[id]/pdf/route.ts` | Generate PDF vulnerability report |

### Key Components

| Component | File | Description |
|-----------|------|-------------|
| `SiteHeader` | `components/site-header.tsx` | Navigation header with auth |
| `HeroSection` | `components/hero-section.tsx` | Landing page hero section |
| `FeaturesSection` | `components/features-section.tsx` | Features showcase |
| `ScannersSection` | `components/scanners-section.tsx` | Available scanners display |
| `MethodologySection` | `components/methodology-section.tsx` | Scan methodology explanation |
| `PricingSection` | `components/pricing-section.tsx` | Pricing tiers display |
| `VulnerabilityReportDocument` | `components/pdf/VulnerabilityReportDocument.tsx` | React-PDF document template |

### Custom Hooks

| Hook | File | Purpose |
|------|------|---------|
| `useRateLimiter` | `hooks/use-rate-limiter.ts` | Client-side rate limiting |
| `useDebounce` | `hooks/use-debounce.ts` | Debounce input values |
| `useLocalStorage` | `hooks/use-local-storage.ts` | Persist data in localStorage |
| `useMobile` | `hooks/use-mobile.ts` | Mobile viewport detection |
| `useToast` | `hooks/use-toast.ts` | Toast notifications |

---

## 5. Backend (FastAPI)

### API Endpoints (Backend)

| Route | Method | File | Purpose |
|-------|--------|------|---------|
| `/api/scan` | POST | `routes_scan.py` | Create new scan request |
| `/api/scan/{scan_id}` | GET | `routes_scan.py` | Get scan status & results |
| `/api/history` | GET | `routes_history.py` | Get paginated scan history |
| `/api/health` | GET | `routes_health.py` | Health check |

### Core Modules

| Module | File | Purpose |
|--------|------|---------|
| Security | `app/core/security.py` | JWT token validation, user extraction |
| Validators | `app/core/validators.py` | URL validation, SSRF protection |
| Rate Limiting | `app/core/rate_limit.py` | Database-backed rate limiting |
| Exceptions | `app/core/exceptions.py` | Custom HTTP exception classes |

### Database Layer

| File | Purpose |
|------|---------|
| `app/db/session.py` | AsyncPG connection pool management |
| `app/db/repositories.py` | All CRUD operations for scans, results, consent |

### Pydantic Models

| Model | File | Purpose |
|-------|------|---------|
| `ScanCreate`, `ScanResponse`, `ScanDetailResponse` | `models/scan_models.py` | Scan request/response schemas |
| `HistoryItem`, `HistoryResponse` | `models/scan_models.py` | History pagination schemas |
| `HealthResponse` | `models/scan_models.py` | Health check response |
| `AIReport`, `Finding` | `models/ai_models.py` | AI-generated report schemas |

---

## 6. Database Schema

### Tables

#### `scans` - Main scan records

```sql
CREATE TABLE scans (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT NOT NULL,
    target_url TEXT NOT NULL,
    scan_status TEXT NOT NULL DEFAULT 'queued',
    -- Status values: 'queued', 'running', 'completed', 'failed'
    progress INTEGER DEFAULT 0,
    error_message TEXT,
    total_vulnerabilities INTEGER DEFAULT 0,
    critical_count INTEGER DEFAULT 0,
    high_count INTEGER DEFAULT 0,
    medium_count INTEGER DEFAULT 0,
    low_count INTEGER DEFAULT 0,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Indexes:**
- `idx_scans_user_id` - User lookups
- `idx_scans_status` - Status filtering
- `idx_scans_created_at` - Sorting
- `idx_scans_queued` - Worker query optimization

#### `scan_results` - Raw scan + AI results

```sql
CREATE TABLE scan_results (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    scan_id UUID REFERENCES scans(id) ON DELETE CASCADE UNIQUE,
    raw_json JSONB NOT NULL DEFAULT '{}',
    ai_report JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### `vulnerabilities` - Discovered vulnerabilities

```sql
CREATE TABLE vulnerabilities (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    scan_id UUID REFERENCES scans(id) ON DELETE CASCADE,
    vulnerability_name TEXT NOT NULL,
    vulnerability_type TEXT NOT NULL,
    description TEXT,
    severity TEXT NOT NULL,
    affected_url TEXT,
    remediation TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### `consent_logs` - GDPR compliance

```sql
CREATE TABLE consent_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT NOT NULL,
    url TEXT NOT NULL,
    ip_address TEXT,
    consented_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## 7. Vulnerability Scanners

The system implements **4 independent vulnerability scanners** that run concurrently. All scanners inherit from the `BaseScanner` interface.

### Scanner Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     BASE SCANNER                            │
│                    (base.py - ABC)                          │
├─────────────────────────────────────────────────────────────┤
│  name: str                                                 │
│  async run(url: str) -> dict[str, Any]                    │
│    - scanner: str                                          │
│    - findings: list[dict]                                 │
│    - error: str | None                                     │
└─────────────────────────────────────────────────────────────┘
            │            │            │            │
            ▼            ▼            ▼            ▼
    ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐
    │    SSL    │ │  HEADER   │ │   PATH    │ │    CVE    │
    │ SCANNER   │ │ SCANNER   │ │ SCANNER   │ │ SCANNER   │
    └───────────┘ └───────────┘ └───────────┘ └───────────┘
```

### 7.1 SSL Scanner (`ssl_scanner.py`)

**Purpose:** Checks TLS/SSL configuration of HTTPS websites

**Checks Performed:**

| Check | Description |
|-------|-------------|
| Protocol Version | Detects weak TLS versions (TLSv1.0, TLSv1.1) |
| Certificate Expiry | Checks if cert is expired or expires within 30 days |
| Cipher Suite Strength | Detects weak ciphers (RC4, DES, 3DES, MD5, NULL, EXPORT, "anon") |
| Certificate Verification | Validates trusted CA verification |

**Vulnerabilities Detected:**

| Vulnerability | Severity |
|--------------|----------|
| No HTTPS Encryption | high |
| Weak TLS Version (1.0/1.1) | high |
| Expired SSL Certificate | critical |
| SSL Certificate Expiring Soon | medium |
| Weak Cipher Suite | high |
| SSL Certificate Verification Failed | high |
| SSL Connection Failed | info |

**External APIs:** None (uses Python's `ssl` and `socket` libraries)

---

### 7.2 Header Scanner (`header_scanner.py`)

**Purpose:** Analyzes HTTP response headers for missing security headers and information disclosure

**Checks Performed:**

| Check | Description |
|-------|-------------|
| Missing Security Headers | Checks for absence of 6 critical headers |
| Server Version Disclosure | Detects version numbers in Server header |
| X-Powered-By Disclosure | Checks for technology stack in X-Powered-By |
| CORS Misconfiguration | Verifies Access-Control-Allow-Origin |

**Vulnerabilities Detected:**

**Missing Security Headers:**

| Header | Severity | Risk |
|--------|----------|------|
| Strict-Transport-Security (HSTS) | high | Browser may use insecure HTTP |
| Content-Security-Policy | medium | XSS/injection risk |
| X-Content-Type-Options | medium | MIME-sniffing XSS |
| X-Frame-Options | medium | Clickjacking |
| Referrer-Policy | low | URL leakage |
| Permissions-Policy | low | Unrestricted browser features |

**Additional Findings:**

| Vulnerability | Severity |
|--------------|----------|
| Server Version Disclosure | low |
| Technology Stack Disclosure | low |
| Permissive CORS Policy | medium |

**External APIs:** None (direct HTTP requests via `httpx`)

---

### 7.3 Path Scanner (`path_scanner.py`)

**Purpose:** Probes for publicly accessible sensitive files and directories

**Checks Performed:**

| Check | Description |
|-------|-------------|
| Sensitive File Detection | Attempts to access 22+ known sensitive paths |
| Status Code Analysis | Treats 200, 301, 302, 403 as exposed |
| Content Validation | Verifies 200 responses have >20 bytes |
| 403 Handling | Reports "Path Exists But Forbidden" |

**Vulnerabilities Detected:**

**Critical Severity:**
- `/.env` - Environment configuration
- `/.git/config`, `/.git/HEAD` - Git repository exposure
- `/db.sql`, `/dump.sql` - Database dumps
- `/.htpasswd` - Apache password file

**High Severity:**
- `/backup.zip`, `/backup.tar.gz` - Backup archives
- `/phpmyadmin/` - phpMyAdmin
- `/web.config` - IIS configuration
- `/elmah.axd`, `/trace.axd` - ASP.NET pages
- `/phpinfo.php`, `/info.php` - PHP info

**Medium Severity:**
- `/wp-admin/` - WordPress admin
- `/admin/` - Admin interface
- `/server-status`, `/server-info` - Apache status
- `/.htaccess` - Apache config

**Low Severity:**
- `/.DS_Store` - macOS metadata
- `/crossdomain.xml` - Flash policy

**External APIs:** None (uses `httpx`)

---

### 7.4 CVE Scanner (`cve_scanner.py`)

**Purpose:** Detects technology stack and queries NIST NVD for known CVEs

**Detection Sources:**

**From HTTP Headers:**
| Header | Patterns Detected |
|--------|-------------------|
| Server | Apache, nginx, Microsoft IIS, LiteSpeed, Caddy |
| X-Powered-By | PHP, ASP.NET, Express.js, Next.js, Django |
| X-AspNet-Version | ASP.NET |

**From HTML Body (first 50KB):**
- WordPress (generator meta, /wp-content/, /wp-includes/)
- Joomla, Drupal
- jQuery, Bootstrap, React, Vue.js, Angular

**External APIs:**

| Service | URL | Purpose |
|---------|-----|---------|
| NIST NVD API | `https://services.nvd.nist.gov/rest/json/cves/2.0` | Query CVEs |
| API Key | Optional (`NVD_API_KEY`) | Higher rate limits |

---

## 8. Background Worker

### Overview

The worker is a **standalone async process** that polls the database for queued scans and processes them. It runs independently from the API server.

### Worker Implementation

**File:** `backend/app/worker/worker.py`

### How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                      WORKER PROCESS                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. STARTUP                                                    │
│     - Initialize database connection pool                       │
│     - Register signal handlers (SIGINT, SIGTERM)               │
│     - Log "worker_ready"                                        │
│                                                                 │
│  2. POLL LOOP (every 5 seconds)                                │
│     ┌─────────────────────────────────────────────────────┐    │
│     │ SELECT id, user_id, target_url FROM scans           │    │
│     │ WHERE scan_status = 'queued'                        │    │
│     │ ORDER BY created_at ASC                             │    │
│     │ LIMIT 1                                             │    │
│     │ FOR UPDATE SKIP LOCKED                              │    │
│     └─────────────────────────────────────────────────────┘    │
│                         │                                       │
│                         ▼                                       │
│              ┌─────────────────────┐                           │
│              │ Found queued scan?  │                           │
│              └─────────────────────┘                           │
│                   │           │                                 │
│                  YES          NO                                │
│                   │           │                                 │
│                   ▼           ▼                                 │
│     ┌──────────────────┐   ┌──────────────────┐               │
│     │ PROCESS SCAN     │   │ Sleep 5 seconds  │               │
│     │ (scan_service)   │   │ and poll again   │               │
│     └──────────────────┘   └──────────────────┘               │
│                                                                 │
│  3. SHUTDOWN                                                   │
│     - Close database pool                                       │
│     - Log "worker_stopped"                                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Key Features

- **Database Polling:** Checks every 5 seconds (configurable via `WORKER_POLL_INTERVAL`)
- **Concurrent Safety:** Uses `FOR UPDATE SKIP LOCKED` to prevent multiple workers from processing the same scan
- **Graceful Shutdown:** Handles SIGINT/SIGTERM signals
- **Error Handling:** Any exceptions mark scan as "failed"

### Running the Worker

```bash
cd backend
python -m app.worker.worker
```

### Worker Logs

```
{"poll_interval": 5, "event": "worker_starting", ...}
{"event": "db_pool_creating", "dsn": "postgresql://...", ...}
{"event": "db_pool_created", ...}
{"event": "worker_ready", ...}
{"event": "worker_processing", "scan_id": "...", "url": "..."}
{"event": "scan_completed", "scan_id": "...", "total_findings": 5}
```

---

## 9. AI Analysis Service

### Overview

The AI service converts raw scanner output into a structured vulnerability report using Large Language Models.

**File:** `backend/app/services/ai_service.py`

### Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI SERVICE FLOW                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Raw Scanner Results (JSON)                                     │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ {                                                          │  │
│  │   "ssl_scanner": { "findings": [...] },                   │  │
│  │   "header_scanner": { "findings": [...] },                │  │
│  │   "path_scanner": { "findings": [...] },                  │  │
│  │   "cve_scanner": { "findings": [...] }                    │  │
│  │ }                                                          │  │
│  └───────────────────────────────────────────────────────────┘  │
│                           │                                      │
│                           ▼                                      │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                 PROMPT GENERATION                          │  │
│  │  - System prompt: cybersecurity analyst instructions      │  │
│  │  - User prompt: scan results + target URL                 │  │
│  └───────────────────────────────────────────────────────────┘  │
│                           │                                      │
│                           ▼                                      │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────────────┐   │
│  │   GROQ      │   │  OPENAI     │   │   RULE-BASED        │   │
│  │  (Primary)  │──▶│  (Fallback) │──▶│   (Final Fallback)  │   │
│  └─────────────┘   └─────────────┘   └─────────────────────┘   │
│       │                 │                     │                 │
│       └─────────────────┴─────────────────────┘                 │
│                         │                                        │
│                         ▼                                        │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              AI Report (JSON)                             │  │
│  │  {                                                        │  │
│  │    "risk_score": 75,                                      │  │
│  │    "summary": "Executive summary...",                    │  │
│  │    "findings": [                                          │  │
│  │      {                                                     │  │
│  │        "title": "Weak TLS Configuration",                 │  │
│  │        "severity": "high",                                │  │
│  │        "owasp_category": "A02:2021-Cryptographic Failures",│
│  │        "description": "...",                              │  │
│  │        "evidence": "...",                                  │  │
│  │        "remediation": "...",                               │  │
│  │        "cvss_score": 7.5,                                 │  │
│  │        "cwe_id": "CWE-327"                                 │  │
│  │      }                                                     │  │
│  │    ]                                                       │  │
│  │  }                                                        │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### AI Report Schema

```python
class Finding(BaseModel):
    title: str                           # Vulnerability name
    severity: str                        # critical|high|medium|low|info
    owasp_category: str                 # OWASP Top 10:2021 category
    description: str                     # Detailed explanation
    evidence: str                        # Technical evidence
    remediation: str                     # Fix instructions
    cvss_score: float                   # CVSS v3 score (0.0-10.0)
    cwe_id: str | None                  # CWE identifier

class AIReport(BaseModel):
    risk_score: int                      # 0-100
    summary: str                         # Executive summary
    findings: list[Finding]              # Prioritized findings
```

### Fallback Chain

1. **Groq** (primary) - Uses `GROQ_API_KEY` and `AI_MODEL`
2. **OpenAI** (fallback) - Uses `OPENAI_API_KEY` with GPT-4o-mini
3. **Rule-based** (final) - Basic severity-weighted scoring when AI unavailable

---

## 10. API Endpoints

### Frontend API Routes

#### POST /api/scans/start

Start a new vulnerability scan.

**Request:**
```json
{
  "url": "https://example.com"
}
```

**Response:**
```json
{
  "success": true,
  "scanId": "uuid-string",
  "message": "Scan queued successfully. The background worker will process it shortly."
}
```

#### GET /api/scans

Get paginated scan history.

**Response:**
```json
{
  "scans": [
    {
      "id": "uuid",
      "url": "https://example.com",
      "status": "completed",
      "created_at": "2026-03-01T10:00:00Z",
      "completed_at": "2026-03-01T10:02:30Z",
      "total_vulnerabilities": 5,
      "critical_count": 1,
      "high_count": 2,
      "medium_count": 1,
      "low_count": 1
    }
  ],
  "total": 100,
  "page": 1,
  "pageSize": 20
}
```

#### GET /api/scans/[id]

Get scan details and results.

**Response:**
```json
{
  "id": "uuid",
  "url": "https://example.com",
  "status": "completed",
  "progress": 100,
  "created_at": "2026-03-01T10:00:00Z",
  "completed_at": "2026-03-01T10:02:30Z",
  "total_vulnerabilities": 5,
  "critical_count": 1,
  "high_count": 2,
  "medium_count": 1,
  "low_count": 1,
  "ai_report": {
    "risk_score": 75,
    "summary": "...",
    "findings": [...]
  }
}
```

### Backend API Routes

#### POST /api/scan

Create new scan (called by frontend).

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "url": "https://example.com",
  "consent": true
}
```

**Response:**
```json
{
  "scan_id": "uuid-string",
  "status": "queued"
}
```

#### GET /api/scan/{scan_id}

Get scan status and results.

#### GET /api/history

Get user scan history.

#### GET /api/health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-03-01T10:00:00Z"
}
```

---

## 11. Security Features

### SSRF Protection

Blocks scanning of internal/private networks:

```python
SSRF_BLOCKED_HOSTS = {
    "localhost", "127.0.0.1", "::1", "0.0.0.0",
    "169.254.169.254",  # AWS metadata
    "metadata.google.internal",  # GCP metadata
}

# Blocks:
# - Private IP ranges: 10.x, 192.168.x, 172.16-31.x
# - Localhost and .local domains
# - Dangerous ports: 22, 23, 3389
```

### Rate Limiting

- **Default:** 10 scans per user per hour
- **Backend:** Database-backed (stored in memory with Redis fallback)
- **Frontend:** In-memory rate limiter

### Authentication

- JWT-based authentication via `python-jose`
- Frontend: Clerk (currently disabled, using local-user)
- Token validation on protected endpoints

### Consent Logging

All scans are logged for GDPR compliance:
- User ID
- Target URL
- IP address
- Timestamp

---

## 12. Dependencies

### Frontend (NPM)

| Package | Version | Purpose |
|---------|---------|---------|
| `next` | 16.0.10 | React framework |
| `react` | 19.2.0 | UI library |
| `@clerk/nextjs` | 6.36.7 | Authentication |
| `@radix-ui/react-*` | Various | UI components |
| `@react-pdf/renderer` | 4.3.2 | PDF generation |
| `recharts` | 2.15.4 | Charts |
| `framer-motion` | 12.24.10 | Animations |
| `zod` | 3.25.76 | Validation |
| `lucide-react` | 0.454.0 | Icons |
| `tailwindcss` | 4.1.9 | CSS |
| `date-fns` | 4.1.0 | Date utilities |
| `jose` | 6.1.3 | JWT handling |
| `@neondatabase/serverless` | 1.0.2 | DB connection |

### Backend (Python)

| Package | Version | Purpose |
|---------|---------|---------|
| `fastapi` | 0.115.6 | Web framework |
| `uvicorn` | 0.34.0 | ASGI server |
| `asyncpg` | 0.30.0 | Async PostgreSQL |
| `httpx` | 0.28.1 | HTTP client |
| `pydantic` | 2.10.4 | Validation |
| `pydantic-settings` | 2.7.1 | Settings |
| `structlog` | 24.4.0 | Logging |
| `groq` | 0.14.0 | Groq AI |
| `openai` | 1.58.1 | OpenAI AI |
| `reportlab` | 4.0.7 | PDF generation |
| `python-jose` | 3.3.0 | JWT |

---

## 13. System Flow Diagrams

### Complete Scan Flow

```
┌──────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────┐
│  USER    │────▶│  FRONTEND    │────▶│   BACKEND   │────▶│   DB    │
│          │     │  (Next.js)   │     │   (FastAPI) │     │ (Neon)  │
└──────────┘     └──────────────┘     └─────────────┘     └──────────┘
                                                                    │
                                       ┌─────────────────────────────┘
                                       │
                                       │ INSERT scan (status: 'queued')
                                       ▼
                               ┌─────────────┐
                               │    WORKER   │
                               │  (Python)   │
                               └─────────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
                    ▼                  ▼                  ▼
            ┌────────────┐    ┌────────────┐    ┌────────────┐
            │SSL Scanner │    │Hdr Scanner │    │Path Scanner│
            └────────────┘    └────────────┘    └────────────┘
                    │                  │                  │
                    └──────────────────┼──────────────────┘
                                       │
                                       ▼
                              ┌────────────────┐
                              │  CVE Scanner  │
                              │ (NVD API)     │
                              └────────────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
                    ▼                  ▼                  ▼
            ┌──────────────────────────────────────────────────┐
            │              RAW RESULTS                       │
            └──────────────────────────────────────────────────┘
                               │
                               ▼
                    ┌────────────────────┐
                    │   AI SERVICE      │
                    │ (Groq/OpenAI)     │
                    └────────────────────┘
                               │
                               ▼
                    ┌────────────────────┐
                    │   AI REPORT       │
                    └────────────────────┘
                               │
                               ▼
                        ┌───────────┐
                        │   UPDATE  │
                        │   DB      │
                        │ status:   │
                        │'completed'│
                        └───────────┘
                               │
                               ▼
                        ┌───────────┐
                        │  FRONTEND │
                        │  POLLS &  │
                        │  DISPLAYS │
                        └───────────┘
```

### Database Relationships

```
┌─────────────┐       ┌─────────────────┐       ┌───────────────┐
│    scans    │──────▶│   scan_results  │       │ vulnerabilities│
├─────────────┤       ├─────────────────┤       ├───────────────┤
│ id (PK)     │       │ id (PK)         │       │ id (PK)       │
│ user_id     │       │ scan_id (FK)    │──────▶│ scan_id (FK)  │
│ target_url  │       │ raw_json        │       │ name          │
│ scan_status │       │ ai_report       │       │ type          │
│ progress    │       └─────────────────┘       │ severity      │
│ ...         │                                 │ remediation   │
└─────────────┘                                 └───────────────┘
       │
       │ (one-to-many)
       ▼
┌─────────────┐
│ consent_logs│
├─────────────┤
│ id (PK)     │
│ user_id (FK)│
│ url         │
│ ip_address  │
│ consented_at│
└─────────────┘
```

---

## 14. Configuration

### Environment Variables

**Backend (.env):**

```bash
# Database
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require

# Worker
WORKER_POLL_INTERVAL=5  # seconds

# Scanning
SCAN_TIMEOUT=30         # Per-scanner timeout
TOTAL_SCAN_TIMEOUT=120   # Total scan budget

# Rate Limiting
RATE_LIMIT_MAX=10        # Max scans per user
RATE_LIMIT_WINDOW_HOURS=1

# AI
GROQ_API_KEY=your_groq_key
AI_MODEL=llama-3.3-70b-versatile

# NVD API
NVD_API_KEY=your_nvd_key

# CORS
CORS_ORIGINS=["http://localhost:3000"]

# Logging
LOG_LEVEL=INFO
```

---

## 15. Running the Application

### Development Mode

You need **3 terminal windows** to run the complete system:

**Terminal 1 - Frontend:**
```bash
npm run dev
# Runs on http://localhost:3000
```

**Terminal 2 - Backend API:**
```bash
cd backend
uvicorn app.main:app --reload --port 3001
# Runs on http://localhost:3001
```

**Terminal 3 - Worker:**
```bash
cd backend
python -m app.worker.worker
# Polls database every 5 seconds
```

### Production (Render)

The `render.yaml` defines two services:

1. **sentinelai-api** - FastAPI on uvicorn
2. **sentinelai-worker** - Background worker

### Verification

Check if worker is running:
```bash
curl http://localhost:3001/api/health
# {"status":"healthy","timestamp":"..."}
```

Check database for queued scans:
```sql
SELECT id, target_url, scan_status FROM scans 
WHERE scan_status = 'queued' 
ORDER BY created_at DESC;
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Start Frontend | `npm run dev` |
| Start Backend | `cd backend && uvicorn app.main:app --reload --port 3001` |
| Start Worker | `cd backend && python -m app.worker.worker` |
| Health Check | `curl http://localhost:3001/api/health` |
| Run Migration | Copy `backend/migration.sql` to Neon SQL Editor |

---

*Generated on 2026-03-01*
