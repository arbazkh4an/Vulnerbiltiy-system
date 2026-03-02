import { NextResponse } from "next/server"
import { auth } from "@clerk/nextjs/server"
import { sql } from "@/lib/db"
import { z } from "zod"

const scanIdSchema = z.string().uuid("Invalid scan ID format")

export async function GET(request: Request, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { userId } = await auth()
    if (!userId) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const { id: scanId } = await params

    const scanIdValidation = scanIdSchema.safeParse(scanId)

    if (!scanIdValidation.success) {
      return NextResponse.json(
        { error: "Invalid scan ID", details: scanIdValidation.error.errors[0]?.message },
        { status: 400 }
      )
    }

    // Don't filter by user_id in local dev so we can see all scans
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
      WHERE id = ${scanId} AND user_id = ${userId}
    `

    if (scanResult.length === 0) {
      return NextResponse.json(
        { error: "Scan not found", message: "No scan found with the provided ID" },
        { status: 404 }
      )
    }

    const scan = scanResult[0]

    // Query only columns that exist in the vulnerabilities table per migration.sql
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

    // Return vulnerabilities with empty cves array (cve_mappings table may not exist)
    let finalVulnerabilities = vulnerabilities.map((vuln) => ({
      ...vuln,
      cwe_id: null,
      cwe_name: null,
      cvss_score: 0,
      ai_predicted_severity: vuln.severity,
      ai_confidence: 0,
      evidence: null,
      cves: [],
    }))

    let riskScore = 0

    // Always fetch ai_report to get the risk score (and fallback findings)
    const scanResults = await sql`SELECT ai_report FROM scan_results WHERE scan_id = ${scanId}`
    if (scanResults.length > 0 && scanResults[0].ai_report) {
      const aiReport = typeof scanResults[0].ai_report === 'string'
        ? JSON.parse(scanResults[0].ai_report)
        : scanResults[0].ai_report;

      if (aiReport.risk_score !== undefined) {
        riskScore = aiReport.risk_score
      }

      if (finalVulnerabilities.length === 0 && aiReport && Array.isArray(aiReport.findings)) {
        finalVulnerabilities = aiReport.findings.map((finding: any, index: number) => ({
          id: `ai-finding-${index}-${Date.now()}`,
          vulnerability_name: finding.title || 'Unknown Vulnerability',
          vulnerability_type: finding.owasp_category || 'Unknown',
          description: finding.description || null,
          severity: finding.severity || 'info',
          affected_url: scan.target_url,
          remediation: finding.remediation || null,
          cwe_id: finding.cwe_id || null,
          cwe_name: null,
          cvss_score: finding.cvss_score || 0,
          ai_predicted_severity: finding.severity || 'info',
          ai_confidence: 90,
          evidence: finding.evidence || null,
          cves: [],
        }));
      }
    }

    return NextResponse.json({
      scan: { ...scan, risk_score: riskScore },
      vulnerabilities: finalVulnerabilities,
    })
  } catch (error) {
    console.error("[v0] Error fetching scan results:", error)
    return NextResponse.json({ error: "Failed to fetch scan results", details: error instanceof Error ? error.message : String(error) }, { status: 500 })
  }
}
