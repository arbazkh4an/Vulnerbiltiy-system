import { NextResponse } from "next/server"
// import { auth } from "@clerk/nextjs/server"
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
  user_name?: string
  user_email?: string
}

interface Vulnerability {
  id: string
  vulnerability_name: string
  vulnerability_type: string
  description: string | null
  severity: string
  affected_url: string | null
  remediation: string | null
  cwe_id: string | null
  cwe_name: string | null
  cvss_score: number
  ai_predicted_severity: string | null
  ai_confidence: number
  evidence: string | null
  cves: Array<{
    cve_id: string
    cve_description: string
    cvss_v3_score: number
    published_date: string
  }>
}

export async function GET(request: Request, { params }: { params: Promise<{ id: string }> }) {
  try {
    // Clerk disabled for local dev
    const userId = "local-user"

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
        s.low_count
      FROM scans s
      WHERE s.id = ${scanId}
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
        id,
        vulnerability_name,
        vulnerability_type,
        description,
        severity,
        affected_url,
        remediation
      FROM vulnerabilities
      WHERE scan_id = ${scanId}
      ORDER BY 
        CASE severity
          WHEN 'critical' THEN 1
          WHEN 'high' THEN 2
          WHEN 'medium' THEN 3
          WHEN 'low' THEN 4
        END
    `

    const vulnerabilitiesWithCVEs = vulnerabilities.map((vuln) => ({
      ...vuln,
      cwe_id: null,
      cwe_name: null,
      cvss_score: 0,
      ai_predicted_severity: vuln.severity,
      ai_confidence: 0,
      evidence: null,
      cves: [],
    }))

    const doc = VulnerabilityReportDocument({
      scan: scan as any,
      vulnerabilities: vulnerabilitiesWithCVEs as any,
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
    return NextResponse.json({ error: "Failed to generate PDF report", details: error instanceof Error ? error.message : String(error) }, { status: 500 })
  }
}
