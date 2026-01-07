import { NextResponse } from "next/server"
import { getSession } from "@/lib/auth"
import { sql } from "@/lib/db"

export async function GET(request: Request, { params }: { params: { id: string } }) {
  try {
    const user = await getSession()

    if (!user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const scanId = params.id

    // Fetch scan details
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

    // Fetch vulnerabilities
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

    // Fetch CVEs for each vulnerability
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

    // In a real implementation, this would call the Python backend to generate PDF
    // For now, we'll call a simple PDF generation endpoint
    // Forward the data to the backend for PDF generation
    const backendUrl = process.env.BACKEND_URL || "http://localhost:5000"

    const pdfResponse = await fetch(`${backendUrl}/api/generate-pdf`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        scan,
        vulnerabilities: vulnerabilitiesWithCVEs,
      }),
    })

    if (!pdfResponse.ok) {
      throw new Error("Failed to generate PDF")
    }

    const pdfBuffer = await pdfResponse.arrayBuffer()

    return new NextResponse(pdfBuffer, {
      headers: {
        "Content-Type": "application/pdf",
        "Content-Disposition": `attachment; filename="vulnerability-report-${scanId}.pdf"`,
      },
    })
  } catch (error) {
    console.error("[v0] Error generating PDF:", error)
    return NextResponse.json({ error: "Failed to generate PDF report" }, { status: 500 })
  }
}
