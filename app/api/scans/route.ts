import { NextResponse } from "next/server"
import { getSession } from "@/lib/auth"
import { sql } from "@/lib/db"

export async function GET() {
  try {
    const user = await getSession()

    if (!user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    // Fetch all scans for the current user
    const scans = await sql`
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
        low_count,
        created_at
      FROM scans
      WHERE user_id = ${user.id}
      ORDER BY created_at DESC
      LIMIT 50
    `

    return NextResponse.json({ scans })
  } catch (error) {
    console.error("[v0] Error fetching scans:", error)
    return NextResponse.json({ error: "Failed to fetch scans" }, { status: 500 })
  }
}
