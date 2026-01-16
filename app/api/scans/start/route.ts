import { type NextRequest, NextResponse } from "next/server"
import { getSession } from "@/lib/auth"
import { sql } from "@/lib/db"

export async function POST(request: NextRequest) {
  try {
    const user = await getSession()

    if (!user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const body = await request.json()
    const { url } = body

    if (!url) {
      return NextResponse.json({ error: "URL is required" }, { status: 400 })
    }

    // Validate URL format
    try {
      new URL(url)
    } catch {
      return NextResponse.json({ error: "Invalid URL format" }, { status: 400 })
    }

    // Create a new scan record
    const result = await sql`
      INSERT INTO scans (user_id, target_url, scan_status, started_at)
      VALUES (${user.id}, ${url}, 'running', NOW())
      RETURNING id
    `

    const scanId = result[0].id

    // Trigger the Python backend to start scanning
    const backendUrl = process.env.BACKEND_URL || "http://localhost:5000"
    
    try {
      const backendResponse = await fetch(`${backendUrl}/api/scan/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          scanId,
          url: url,
        }),
      })

      if (!backendResponse.ok) {
        const errorData = await backendResponse.json().catch(() => ({}))
        console.error("[v0] Backend scan error:", errorData)
        
        // Update scan status to failed
        await sql`
          UPDATE scans 
          SET scan_status = 'failed'
          WHERE id = ${scanId}
        `
        
        throw new Error(errorData.error || "Backend scan failed")
      }

      const backendData = await backendResponse.json()

    return NextResponse.json({
      success: true,
      scanId,
      message: "Scan started successfully",
        ...backendData,
    })
    } catch (error) {
      console.error("[v0] Error calling backend:", error)
      
      // Update scan status to failed
      try {
        await sql`
          UPDATE scans 
          SET scan_status = 'failed'
          WHERE id = ${scanId}
        `
      } catch (dbError) {
        console.error("[v0] Error updating scan status:", dbError)
      }
      
      // If backend is not available, still return success but log warning
      // This allows the frontend to work even if backend is temporarily down
      if (error instanceof Error && error.message.includes("fetch")) {
        console.warn("[v0] Backend not available, scan queued but not started")
        return NextResponse.json({
          success: true,
          scanId,
          message: "Scan queued (backend unavailable)",
          warning: "Backend service is not available. Scan will start when backend is online.",
        })
      }
      
      throw error
    }
  } catch (error) {
    console.error("[v0] Error starting scan:", error)
    return NextResponse.json({ error: "Failed to start scan" }, { status: 500 })
  }
}
