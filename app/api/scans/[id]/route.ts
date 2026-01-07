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
        id, 
        target_url, 
        scan_status, 
        started_at, 
        completed_at, 
        total_vulnerabilities,
        critical_count,
        high_count,
        medium_count,
        low_count
      FROM scans
      WHERE id = ${scanId} AND user_id = ${user.id}
    `

    if (scanResult.length === 0) {
      return NextResponse.json({ error: "Scan not found" }, { status: 404 })
    }

    const scan = scanResult[0]

    // Fetch vulnerabilities for this scan
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

    // Fetch CVE mappings for each vulnerability
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

    return NextResponse.json({
      scan,
      vulnerabilities: vulnerabilitiesWithCVEs,
    })
  } catch (error) {
    console.error("[v0] Error fetching scan results:", error)
    return NextResponse.json({ error: "Failed to fetch scan results" }, { status: 500 })
  }
}
