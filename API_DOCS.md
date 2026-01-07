# API Documentation - VulnScan AI

Complete API reference for the VulnScan AI application.

## Base URLs

- **Frontend API**: `http://localhost:3000/api` (dev) or `https://your-app.vercel.app/api` (prod)
- **Backend API**: `http://localhost:5000/api` (dev) or `https://your-backend.onrender.com/api` (prod)

## Authentication

VulnScan AI uses JWT-based authentication with HTTP-only cookies.

### Authentication Flow

1. User registers or logs in
2. Server generates JWT token
3. Token stored in HTTP-only cookie
4. Client includes cookie in subsequent requests
5. Server validates token for protected endpoints

---

## Frontend API Endpoints

### Authentication

#### Register User

Creates a new user account.

**Endpoint:** `POST /api/auth/register`

**Request Body:**
\`\`\`json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword123"
}
\`\`\`

**Response (200 OK):**
\`\`\`json
{
  "success": true,
  "user": {
    "id": "user_1234567890_abc123",
    "email": "john@example.com",
    "name": "John Doe"
  }
}
\`\`\`

**Error Responses:**
- `400 Bad Request`: Missing required fields
- `409 Conflict`: User already exists

---

#### Login User

Authenticates an existing user.

**Endpoint:** `POST /api/auth/login`

**Request Body:**
\`\`\`json
{
  "email": "john@example.com",
  "password": "securepassword123"
}
\`\`\`

**Response (200 OK):**
\`\`\`json
{
  "success": true,
  "user": {
    "id": "user_1234567890_abc123",
    "email": "john@example.com",
    "name": "John Doe"
  }
}
\`\`\`

**Error Responses:**
- `400 Bad Request`: Missing credentials
- `401 Unauthorized`: Invalid credentials

---

#### Logout User

Ends the user session.

**Endpoint:** `POST /api/auth/logout`

**Response (200 OK):**
\`\`\`json
{
  "success": true
}
\`\`\`

---

#### Get Current User

Retrieves the authenticated user's information.

**Endpoint:** `GET /api/auth/me`

**Response (200 OK):**
\`\`\`json
{
  "user": {
    "id": "user_1234567890_abc123",
    "email": "john@example.com",
    "name": "John Doe"
  }
}
\`\`\`

**Response (Unauthenticated):**
\`\`\`json
{
  "user": null
}
\`\`\`

---

### Scans

#### List User Scans

Retrieves all scans for the authenticated user.

**Endpoint:** `GET /api/scans`

**Headers:**
- `Cookie`: auth-token (automatic)

**Response (200 OK):**
\`\`\`json
{
  "scans": [
    {
      "id": 1,
      "target_url": "https://example.com",
      "scan_status": "completed",
      "started_at": "2025-01-15T10:30:00Z",
      "completed_at": "2025-01-15T10:32:00Z",
      "total_vulnerabilities": 8,
      "critical_count": 2,
      "high_count": 3,
      "medium_count": 2,
      "low_count": 1
    }
  ]
}
\`\`\`

**Error Responses:**
- `401 Unauthorized`: Not authenticated

---

#### Start New Scan

Initiates a vulnerability scan for a target URL.

**Endpoint:** `POST /api/scans/start`

**Headers:**
- `Cookie`: auth-token (automatic)
- `Content-Type`: application/json

**Request Body:**
\`\`\`json
{
  "url": "https://example.com"
}
\`\`\`

**Response (200 OK):**
\`\`\`json
{
  "success": true,
  "scanId": 42,
  "message": "Scan started successfully"
}
\`\`\`

**Error Responses:**
- `400 Bad Request`: Invalid URL format
- `401 Unauthorized`: Not authenticated

---

#### Get Scan Details

Retrieves detailed information about a specific scan including all vulnerabilities.

**Endpoint:** `GET /api/scans/:id`

**Parameters:**
- `id` (path): Scan ID

**Headers:**
- `Cookie`: auth-token (automatic)

**Response (200 OK):**
\`\`\`json
{
  "scan": {
    "id": 42,
    "target_url": "https://example.com",
    "scan_status": "completed",
    "started_at": "2025-01-15T10:30:00Z",
    "completed_at": "2025-01-15T10:32:00Z",
    "total_vulnerabilities": 8,
    "critical_count": 2,
    "high_count": 3,
    "medium_count": 2,
    "low_count": 1
  },
  "vulnerabilities": [
    {
      "id": 123,
      "vulnerability_name": "SQL Injection in Login Form",
      "vulnerability_type": "Injection",
      "description": "The login form is vulnerable to SQL injection...",
      "cwe_id": "CWE-89",
      "cwe_name": "Improper Neutralization of Special Elements used in an SQL Command",
      "cvss_score": 9.8,
      "severity": "critical",
      "ai_predicted_severity": "critical",
      "ai_confidence": 95.5,
      "remediation": "Use parameterized queries...",
      "affected_url": "https://example.com/login",
      "evidence": "Parameter 'username' accepts unsanitized SQL",
      "cves": [
        {
          "cve_id": "CVE-2024-5678",
          "cve_description": "SQL injection vulnerability in authentication mechanism",
          "cvss_v3_score": 9.8,
          "published_date": "2024-02-10"
        }
      ]
    }
  ]
}
\`\`\`

**Error Responses:**
- `401 Unauthorized`: Not authenticated
- `404 Not Found`: Scan not found

---

#### Download PDF Report

Generates and downloads a PDF report for a scan.

**Endpoint:** `GET /api/scans/:id/pdf`

**Parameters:**
- `id` (path): Scan ID

**Headers:**
- `Cookie`: auth-token (automatic)

**Response:**
- `Content-Type`: application/pdf
- `Content-Disposition`: attachment; filename="vulnerability-report-{id}.pdf"

**Error Responses:**
- `401 Unauthorized`: Not authenticated
- `404 Not Found`: Scan not found
- `500 Internal Server Error`: PDF generation failed

---

## Backend API Endpoints

### Health Check

#### Health Status

Checks if the backend service is running.

**Endpoint:** `GET /health`

**Response (200 OK):**
\`\`\`json
{
  "status": "healthy",
  "service": "VulnScan AI Backend",
  "version": "1.0.0"
}
\`\`\`

---

### Scanning

#### Execute Scan

Performs the actual vulnerability scan (called by frontend API).

**Endpoint:** `POST /api/scan/start`

**Request Body:**
\`\`\`json
{
  "scanId": 42,
  "url": "https://example.com"
}
\`\`\`

**Response (200 OK):**
\`\`\`json
{
  "success": true,
  "scanId": 42,
  "vulnerabilities_found": 8,
  "critical": 2,
  "high": 3,
  "medium": 2,
  "low": 1
}
\`\`\`

**Error Responses:**
- `400 Bad Request`: Missing parameters
- `500 Internal Server Error`: Scan failed

---

#### Get Scan Status

Retrieves the current status of a running scan.

**Endpoint:** `GET /api/scan/status/:scanId`

**Parameters:**
- `scanId` (path): Scan ID

**Response (200 OK):**
\`\`\`json
{
  "scan_status": "running",
  "total_vulnerabilities": 0,
  "critical_count": 0,
  "high_count": 0,
  "medium_count": 0,
  "low_count": 0
}
\`\`\`

---

### PDF Generation

#### Generate PDF Report

Creates a PDF report from scan data (called by frontend API).

**Endpoint:** `POST /api/generate-pdf`

**Request Body:**
\`\`\`json
{
  "scan": {
    "id": 42,
    "target_url": "https://example.com",
    "scan_status": "completed",
    "started_at": "2025-01-15T10:30:00Z",
    "total_vulnerabilities": 8
  },
  "vulnerabilities": [...]
}
\`\`\`

**Response:**
- PDF file binary data

---

## Data Models

### User
\`\`\`typescript
{
  id: string
  email: string
  name: string
  created_at: string
  updated_at: string
}
\`\`\`

### Scan
\`\`\`typescript
{
  id: number
  user_id: string
  target_url: string
  scan_status: 'pending' | 'running' | 'completed' | 'failed'
  started_at: string
  completed_at: string | null
  total_vulnerabilities: number
  critical_count: number
  high_count: number
  medium_count: number
  low_count: number
  created_at: string
}
\`\`\`

### Vulnerability
\`\`\`typescript
{
  id: number
  scan_id: number
  vulnerability_name: string
  vulnerability_type: string
  description: string
  cwe_id: string
  cwe_name: string
  cvss_score: number
  severity: 'critical' | 'high' | 'medium' | 'low'
  ai_predicted_severity: 'critical' | 'high' | 'medium' | 'low'
  ai_confidence: number
  remediation: string
  affected_url: string
  evidence: string
  cves: CVE[]
}
\`\`\`

### CVE
\`\`\`typescript
{
  cve_id: string
  cve_description: string
  cvss_v3_score: number
  published_date: string
}
\`\`\`

---

## Error Handling

All API endpoints follow consistent error response format:

\`\`\`json
{
  "error": "Error message describing what went wrong"
}
\`\`\`

### HTTP Status Codes

- `200 OK`: Request successful
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource already exists
- `500 Internal Server Error`: Server error

---

## Rate Limiting

Currently, no rate limiting is enforced. For production:
- Recommended: 100 requests per minute per IP
- Scanning: 5 concurrent scans per user

---

## Security

### Best Practices

1. **Always use HTTPS in production**
2. **Never expose JWT_SECRET**
3. **Validate all inputs server-side**
4. **Use parameterized queries**
5. **Enable CORS only for trusted domains**

### Authentication Headers

JWT tokens are automatically included via HTTP-only cookies. No manual header management required in the frontend.

---

## Testing with cURL

### Register
\`\`\`bash
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","password":"testpass123"}'
\`\`\`

### Login
\`\`\`bash
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"email":"test@example.com","password":"testpass123"}'
\`\`\`

### Start Scan
\`\`\`bash
curl -X POST http://localhost:3000/api/scans/start \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"url":"https://example.com"}'
\`\`\`

### Get Scans
\`\`\`bash
curl http://localhost:3000/api/scans \
  -b cookies.txt
\`\`\`

---

## WebSocket Support (Future)

Planned for real-time scan progress updates:

\`\`\`javascript
const ws = new WebSocket('wss://api.vulnscan.ai/scan/42/progress');
ws.onmessage = (event) => {
  const progress = JSON.parse(event.data);
  console.log(`Scan progress: ${progress.percent}%`);
};
\`\`\`

---

## Support

For API questions or issues:
- Open a GitHub issue
- Email: support@example.com
- Check the source code for implementation details
