import { NextResponse } from "next/server"
import { getSession } from "@/lib/auth"
import { sql } from "@/lib/db"
import { renderToBuffer } from "@react-pdf/renderer"
import { VulnerabilityReportDocument } from "@/components/pdf/VulnerabilityReportDocument"

interface Scan {
  id: string
  target_url: string
  scan_status: string
  started_at: Date | null
  completed_at: Date | null
  total_vulnerabilities: number
  critical_count: number
  high_count: number
  medium_count: number
  low_count: number
  user_name: string | null
  user_email: string | null
}

interface CVE {
  cve_id: string
  cve_description: string
  cvss_v3_score: number | null
  published_date: string | null
}

interface Vulnerability {
  id: string
  vulnerability_name: string
  vulnerability_type: string
  description: string
  cwe_id: string | null
  cwe_name: string | null
  cvss_score: number | null
  severity: string
  ai_predicted_severity: string | null
  ai_confidence: number | null
  remediation: string | null
  affected_url: string | null
  evidence: string | null
  cves: CVE[]
}

export async function GET(request: Request, { params }: { params: Promise<{ id: string }> }) {
  try {
    const user = await getSession()

    if (!user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const { id: scanId } = await params

    const scanResult = await sql`
      SELECT 
        s.id,
        s.target_url,
        s.scan_status,
        s.started_at,
        s.completed_at,
        s.total_vulnerabilities,
        s.critical_count,
        s.high_count,
        s.medium_count,
        s.low_count,
        u.name as user_name,
        u.email as user_email
      FROM scans s
      LEFT JOIN neon_auth.users_sync u ON s.user_id = u.id
      WHERE s.id = ${scanId} AND s.user_id = ${user.id}
    `

    if (scanResult.length === 0) {
      return NextResponse.json({ error: "Scan not found" }, { status: 404 })
    }

    const scan = scanResult[0]

    if (scan.scan_status !== "completed") {
      return NextResponse.json(
        { error: "PDF not ready", message: "Scan is still in progress" },
        { status: 202 }
      )
    }

    const vulnerabilities = await sql`
      SELECT 
        v.id,
        v.vulnerability_name,
        v.vulnerability_type,
        v.description,
        v.cwe_id,
        v.cwe_name,
        v.cvss_score,
        v.severity,
        v.ai_predicted_severity,
        v.ai_confidence,
        v.remediation,
        v.affected_url,
        v.evidence
      FROM vulnerabilities v
      WHERE v.scan_id = ${scanId}
      ORDER BY 
        CASE v.severity
          WHEN 'critical' THEN 1
          WHEN 'high' THEN 2
          WHEN 'medium' THEN 3
          WHEN 'low' THEN 4
        END
    `

    const vulnerabilitiesWithCVEs = await Promise.all(
      vulnerabilities.map(async (vuln) => {
        const cves = await sql`
          SELECT cve_id, cve_description, cvss_v3_score, published_date
          FROM cve_mappings
          WHERE vulnerability_id = ${vuln.id}
        `
        return { ...vuln, cves }
      }),
    )

    const doc = VulnerabilityReportDocument({
      scan: scan as Scan,
      vulnerabilities: vulnerabilitiesWithCVEs as Vulnerability[],
    })
    const buffer = await renderToBuffer(doc)
    const arrayBuffer = buffer.buffer.slice(buffer.byteOffset, buffer.byteOffset + buffer.byteLength) as ArrayBuffer
    const pdfBuffer = arrayBuffer

    const response = new NextResponse(new Uint8Array(pdfBuffer), {
      status: 200,
      headers: {
        "Content-Type": "application/pdf",
        "Content-Disposition": `attachment; filename="vulnerability-report-${scanId}.pdf"`,
        "Cache-Control": "public, max-age=3600, s-maxage=86400",
        "ETag": `"${scanId}-${Date.now()}"`,
      },
    })

    return response
  } catch (error) {
    console.error("[PDF] Error generating PDF:", error)
    return NextResponse.json({ error: "Failed to generate PDF report" }, { status: 500 })
  }
}
