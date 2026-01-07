-- Vulnerability Scanning System Database Schema
-- This creates all necessary tables for the application

-- Users table (extends the existing neon_auth.users_sync)
-- We'll reference the neon_auth.users_sync.id for user authentication

-- Scans table - stores each URL scan request
CREATE TABLE IF NOT EXISTS scans (
    id SERIAL PRIMARY KEY,
    user_id TEXT REFERENCES neon_auth.users_sync(id) ON DELETE CASCADE,
    target_url TEXT NOT NULL,
    scan_status TEXT NOT NULL DEFAULT 'pending', -- pending, running, completed, failed
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    total_vulnerabilities INTEGER DEFAULT 0,
    critical_count INTEGER DEFAULT 0,
    high_count INTEGER DEFAULT 0,
    medium_count INTEGER DEFAULT 0,
    low_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Vulnerabilities table - stores discovered vulnerabilities
CREATE TABLE IF NOT EXISTS vulnerabilities (
    id SERIAL PRIMARY KEY,
    scan_id INTEGER REFERENCES scans(id) ON DELETE CASCADE,
    vulnerability_name TEXT NOT NULL,
    vulnerability_type TEXT NOT NULL, -- e.g., 'Broken Access Control', 'Injection', etc.
    description TEXT,
    cwe_id TEXT, -- e.g., 'CWE-79'
    cwe_name TEXT,
    cvss_score DECIMAL(3,1), -- 0.0 to 10.0
    severity TEXT NOT NULL, -- critical, high, medium, low
    ai_predicted_severity TEXT, -- AI model prediction
    ai_confidence DECIMAL(5,2), -- confidence score 0-100
    remediation TEXT,
    affected_url TEXT,
    evidence TEXT, -- technical details of the vulnerability
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- CVE mappings - stores CVE associations for vulnerabilities
CREATE TABLE IF NOT EXISTS cve_mappings (
    id SERIAL PRIMARY KEY,
    vulnerability_id INTEGER REFERENCES vulnerabilities(id) ON DELETE CASCADE,
    cve_id TEXT NOT NULL, -- e.g., 'CVE-2023-12345'
    cve_description TEXT,
    cvss_v3_score DECIMAL(3,1),
    published_date DATE,
    last_modified DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Scan history metadata
CREATE TABLE IF NOT EXISTS scan_metadata (
    id SERIAL PRIMARY KEY,
    scan_id INTEGER REFERENCES scans(id) ON DELETE CASCADE,
    key TEXT NOT NULL,
    value TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_scans_user_id ON scans(user_id);
CREATE INDEX IF NOT EXISTS idx_scans_status ON scans(scan_status);
CREATE INDEX IF NOT EXISTS idx_scans_created_at ON scans(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_vulnerabilities_scan_id ON vulnerabilities(scan_id);
CREATE INDEX IF NOT EXISTS idx_vulnerabilities_severity ON vulnerabilities(severity);
CREATE INDEX IF NOT EXISTS idx_cve_mappings_vulnerability_id ON cve_mappings(vulnerability_id);
CREATE INDEX IF NOT EXISTS idx_cve_mappings_cve_id ON cve_mappings(cve_id);
