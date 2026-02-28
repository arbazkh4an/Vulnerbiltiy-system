-- SentinelAI Database Migration
-- Run this SQL against your Neon/Supabase PostgreSQL database
-- to add the required tables and columns for the new backend.

-- scan_results: stores raw scanner output + AI report
CREATE TABLE IF NOT EXISTS scan_results (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    scan_id UUID REFERENCES scans(id) ON DELETE CASCADE UNIQUE,
    raw_json JSONB NOT NULL DEFAULT '{}',
    ai_report JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- consent_logs: GDPR compliance / scan consent tracking
CREATE TABLE IF NOT EXISTS consent_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT NOT NULL,
    url TEXT NOT NULL,
    ip_address TEXT,
    consented_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add progress column to scans (if not exists)
DO $$ BEGIN
    ALTER TABLE scans ADD COLUMN progress INTEGER DEFAULT 0;
EXCEPTION WHEN duplicate_column THEN NULL;
END $$;

-- Add error_message column to scans (if not exists)
DO $$ BEGIN
    ALTER TABLE scans ADD COLUMN error_message TEXT;
EXCEPTION WHEN duplicate_column THEN NULL;
END $$;

-- Index for worker queue polling
CREATE INDEX IF NOT EXISTS idx_scans_queued
    ON scans (created_at ASC)
    WHERE scan_status = 'queued';

-- Index for rate limiting queries
CREATE INDEX IF NOT EXISTS idx_scans_user_recent
    ON scans (user_id, created_at DESC);

-- Index for scan_results lookup
CREATE INDEX IF NOT EXISTS idx_scan_results_scan_id
    ON scan_results (scan_id);
