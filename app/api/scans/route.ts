import { NextResponse } from "next/server"
import { auth } from "@clerk/nextjs/server"
import { sql } from "@/lib/db"
import { checkRateLimit, getClientIp, apiRateLimits } from "@/lib/rate-limit"
import { z } from "zod"

const paginationSchema = z.object({
  limit: z.coerce.number().min(1).max(100).default(50),
  offset: z.coerce.number().min(0).default(0),
}).strict()

export async function GET(request: Request) {
  try {
    const clientIp = getClientIp(request)
    const rateLimitResult = checkRateLimit(`scans-list:${clientIp}`, apiRateLimits.scansList)

    if (!rateLimitResult.success) {
      return NextResponse.json(
        { error: "Too many requests", retryAfter: Math.ceil((rateLimitResult.resetTime - Date.now()) / 1000) },
        { status: 429, headers: { "Retry-After": String(Math.ceil((rateLimitResult.resetTime - Date.now()) / 1000)) } }
      )
    }

    const { userId } = await auth()
    if (!userId) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const { searchParams } = new URL(request.url)
    const limit = searchParams.get("limit") || "50"
    const offset = searchParams.get("offset") || "0"

    const validatedParams = paginationSchema.parse({ limit, offset })

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
      WHERE user_id = ${userId}
      ORDER BY created_at DESC
      LIMIT ${validatedParams.limit}
      OFFSET ${validatedParams.offset}
    `

    return NextResponse.json({ scans })
  } catch (error) {
    if (error instanceof z.ZodError) {
      console.error("[v0] Validation error:", error.errors)
      return NextResponse.json({ error: "Invalid query parameters", details: error.errors }, { status: 400 })
    }
    console.error("[v0] Error fetching scans:", error)
    return NextResponse.json({ error: "Failed to fetch scans", details: error instanceof Error ? error.message : String(error) }, { status: 500 })
  }
}
