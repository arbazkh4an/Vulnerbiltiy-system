/**
 * TypeScript Type Definitions
 * Shared types across the application
 */

export interface User {
  id: string
  email: string
  name: string
  created_at?: string
  updated_at?: string
}

export interface Scan {
  id: number
  user_id: string
  target_url: string
  scan_status: "pending" | "running" | "completed" | "failed"
  started_at: string
  completed_at: string | null
  total_vulnerabilities: number
  critical_count: number
  high_count: number
  medium_count: number
  low_count: number
  created_at: string
  updated_at?: string
}

export interface CVE {
  id?: number
  cve_id: string
  cve_description: string
  cvss_v3_score: number
  published_date: string
  last_modified?: string
}

export interface Vulnerability {
  id: number
  scan_id: number
  vulnerability_name: string
  vulnerability_type: string
  description: string
  cwe_id: string
  cwe_name: string
  cvss_score: number
  severity: "critical" | "high" | "medium" | "low"
  ai_predicted_severity: "critical" | "high" | "medium" | "low"
  ai_confidence: number
  remediation: string
  affected_url: string
  evidence: string
  created_at?: string
  cves?: CVE[]
}

export interface ScanWithVulnerabilities extends Scan {
  vulnerabilities: Vulnerability[]
  user_name?: string
  user_email?: string
}

export interface ApiResponse<T = any> {
  success?: boolean
  data?: T
  error?: string
  message?: string
}

export interface AuthResponse {
  success: boolean
  user?: User
  error?: string
}

export interface ScanStartResponse {
  success: boolean
  scanId: number
  message?: string
  error?: string
}

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  pageSize: number
  totalPages: number
}
