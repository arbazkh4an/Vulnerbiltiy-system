# SentinelAI — Database Setup Guide

## 1. Create a Neon PostgreSQL Database

1. Go to [neon.tech](https://neon.tech) and sign up / sign in
2. Click **"New Project"**
3. Configure:
   - **Name**: `sentinelai`
   - **Region**: Choose closest to your Render region (e.g., `us-east-1`)
   - **Postgres Version**: `16` (default)
4. Click **"Create Project"**
5. Copy the **connection string** from the dashboard — it looks like:
   ```
   postgresql://user:password@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require
   ```
   > This is your `DATABASE_URL`. Save it — you'll need it for both the backend and frontend.

---

## 2. Run the Schema Migration

1. In the Neon dashboard, go to **SQL Editor**
2. Copy the **entire contents** of [migration.sql](file:///d:/PROJECTS/Vulnerbiltiy-system/backend/migration.sql)
3. Paste into the SQL editor and click **Run**
4. This script sets up all tables, columns, and indexes automatically.

---

## 3. Verify Schema

Run this query to confirm all tables exist:

```sql
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
```

Expected tables:
| Table | Purpose |
|-------|---------|
| `scans` | Scan jobs (queued → running → complete/failed) |
| `scan_results` | Raw scanner output + AI report (JSONB) |
| `consent_logs` | GDPR compliance logs |

Verify the new columns on `scans`:

```sql
SELECT column_name, data_type FROM information_schema.columns 
WHERE table_name = 'scans' AND column_name IN ('progress', 'error_message');
```

Expected:
- `progress` — integer
- `error_message` — text

---

## 4. Required Indexes

The migration creates these indexes automatically:

| Index | Purpose |
|-------|---------|
| `idx_scans_queued` | Worker polls for oldest queued scan |
| `idx_scans_user_recent` | Rate limiting (count recent user scans) |
| `idx_scan_results_scan_id` | Fast result lookups by scan ID |

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `relation "scans" does not exist` | The base `scans` table must exist first. Check your frontend migration. |
| `permission denied` | Use the database owner role, not a read-only role. |
| `SSL connection required` | Add `?sslmode=require` to your connection string. |
