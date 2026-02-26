-- Initialize database schema on first postgres boot
-- Creates the complete schema from database/schema.sql

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Scans table: Main table for tracking URL scans
CREATE TABLE IF NOT EXISTS scans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    url TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued' CHECK (status IN ('queued', 'scanning', 'analyzing', 'complete', 'error')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    user_ip TEXT,
    consent_confirmed BOOLEAN DEFAULT FALSE
);

-- Scan results table: Stores raw scanner output
CREATE TABLE IF NOT EXISTS scan_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    scan_id UUID NOT NULL REFERENCES scans(id) ON DELETE CASCADE,
    scanner_name TEXT NOT NULL,
    raw_json JSONB NOT NULL,
    duration_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- AI reports table: Stores AI-generated vulnerability reports
CREATE TABLE IF NOT EXISTS ai_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    scan_id UUID NOT NULL REFERENCES scans(id) ON DELETE CASCADE,
    risk_score INTEGER CHECK (risk_score >= 0 AND risk_score <= 100),
    summary TEXT,
    findings_json JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_scans_status ON scans(status);
CREATE INDEX IF NOT EXISTS idx_scans_created_at ON scans(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_scan_results_scan_id ON scan_results(scan_id);
CREATE INDEX IF NOT EXISTS idx_ai_reports_scan_id ON ai_reports(scan_id);

-- Comments for documentation
COMMENT ON TABLE scans IS 'Main table for tracking URL vulnerability scans';
COMMENT ON TABLE scan_results IS 'Raw scanner output from individual security scanners';
COMMENT ON TABLE ai_reports IS 'AI-generated vulnerability reports with risk assessments';
