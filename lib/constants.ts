/**
 * Application Constants
 * Centralized configuration for the VulnScan AI application
 */

export const APP_CONFIG = {
  name: "VulnScan AI",
  version: "1.0.0",
  description: "Automated Web Vulnerability Scanning System",
  author: "Your Name",
  github: "https://github.com/yourusername/vulnscan-ai",
}

export const SCAN_STATUS = {
  PENDING: "pending",
  RUNNING: "running",
  COMPLETED: "completed",
  FAILED: "failed",
} as const

export const SEVERITY_LEVELS = {
  CRITICAL: "critical",
  HIGH: "high",
  MEDIUM: "medium",
  LOW: "low",
} as const

export const SEVERITY_COLORS = {
  critical: {
    bg: "bg-red-500/10",
    border: "border-red-500/50",
    text: "text-red-400",
  },
  high: {
    bg: "bg-orange-500/10",
    border: "border-orange-500/50",
    text: "text-orange-400",
  },
  medium: {
    bg: "bg-yellow-500/10",
    border: "border-yellow-500/50",
    text: "text-yellow-400",
  },
  low: {
    bg: "bg-blue-500/10",
    border: "border-blue-500/50",
    text: "text-blue-400",
  },
} as const

export const OWASP_TOP_10_2025 = [
  {
    id: "A01:2025",
    name: "Broken Access Control",
    description: "Failures related to access controls that allow unauthorized actions",
  },
  {
    id: "A02:2025",
    name: "Cryptographic Failures",
    description: "Failures related to cryptography leading to sensitive data exposure",
  },
  {
    id: "A03:2025",
    name: "Injection",
    description: "Application vulnerable to injection attacks like SQL, NoSQL, OS commands",
  },
  {
    id: "A04:2025",
    name: "Insecure Design",
    description: "Missing or ineffective control design flaws",
  },
  {
    id: "A05:2025",
    name: "Security Misconfiguration",
    description: "Insecure default configurations, incomplete setups, open cloud storage",
  },
  {
    id: "A06:2025",
    name: "Vulnerable and Outdated Components",
    description: "Using components with known vulnerabilities",
  },
  {
    id: "A07:2025",
    name: "Identification and Authentication Failures",
    description: "Failures in confirming user identity, authentication, and session management",
  },
  {
    id: "A08:2025",
    name: "Software and Data Integrity Failures",
    description: "Code and infrastructure that does not protect against integrity violations",
  },
  {
    id: "A09:2025",
    name: "Security Logging and Monitoring Failures",
    description: "Insufficient logging and monitoring",
  },
  {
    id: "A10:2025",
    name: "Server-Side Request Forgery",
    description: "SSRF flaws occur when a web application fetches a remote resource without validating",
  },
] as const

export const API_ENDPOINTS = {
  // Auth
  LOGIN: "/api/auth/login",
  REGISTER: "/api/auth/register",
  LOGOUT: "/api/auth/logout",
  ME: "/api/auth/me",

  // Scans
  SCANS_LIST: "/api/scans",
  SCANS_START: "/api/scans/start",
  SCAN_DETAILS: (id: string | number) => `/api/scans/${id}`,
  SCAN_PDF: (id: string | number) => `/api/scans/${id}/pdf`,
} as const

export const ROUTES = {
  HOME: "/",
  LOGIN: "/login",
  REGISTER: "/register",
  DASHBOARD: "/dashboard",
  SCAN_RESULTS: (id: string | number) => `/scan/${id}`,
} as const

export const PASSWORD_REQUIREMENTS = {
  minLength: 8,
  requireUppercase: false,
  requireLowercase: false,
  requireNumbers: false,
  requireSpecialChars: false,
} as const

export const SCAN_LIMITS = {
  maxConcurrentScans: 5,
  maxUrlLength: 2048,
  timeoutSeconds: 300, // 5 minutes
} as const
