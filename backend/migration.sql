-- SentinelAI — Complete System Schema
-- This script sets up all necessary tables and indexes for the application.
-- Run this in the Neon SQL Editor.

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 1. Scans Table
-- Tracks each URL scan request
CREATE TABLE IF NOT EXISTS scans (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT NOT NULL, -- References neon_auth.users_sync(id)
    target_url TEXT NOT NULL,
    scan_status TEXT NOT NULL DEFAULT 'queued', -- queued, running, complete, failed
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

-- 2. Scan Results Table
-- Stores raw scanner output and AI-generated reports
CREATE TABLE IF NOT EXISTS scan_results (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    scan_id UUID REFERENCES scans(id) ON DELETE CASCADE UNIQUE,
    raw_json JSONB NOT NULL DEFAULT '{}',
    ai_report JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Consent Logs Table
-- GDPR compliance / scan consent tracking
CREATE TABLE IF NOT EXISTS consent_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT NOT NULL,
    url TEXT NOT NULL,
    ip_address TEXT,
    consented_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Vulnerabilities Table
-- Stores discovered vulnerabilities for detailed reporting
CREATE TABLE IF NOT EXISTS vulnerabilities (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    scan_id UUID REFERENCES scans(id) ON DELETE CASCADE,
    vulnerability_name TEXT NOT NULL,
    vulnerability_type TEXT NOT NULL,
    description TEXT,
    severity TEXT NOT NULL, -- critical, high, medium, low
    affected_url TEXT,
    remediation TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Indexes for Performance
CREATE INDEX IF NOT EXISTS idx_scans_user_id ON scans(user_id);
CREATE INDEX IF NOT EXISTS idx_scans_status ON scans(scan_status);
CREATE INDEX IF NOT EXISTS idx_scans_created_at ON scans(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_scans_queued ON scans (created_at ASC) WHERE scan_status = 'queued';
CREATE INDEX IF NOT EXISTS idx_scan_results_scan_id ON scan_results (scan_id);
CREATE INDEX IF NOT EXISTS idx_vulnerabilities_scan_id ON vulnerabilities(scan_id);
