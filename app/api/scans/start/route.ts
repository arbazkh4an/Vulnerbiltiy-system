import { type NextRequest, NextResponse } from "next/server"
import { getSession } from "@/lib/auth"
import { sql } from "@/lib/db"
import { checkRateLimit, getClientIp, apiRateLimits } from "@/lib/rate-limit"
import { z } from "zod"

const SSRF_BLOCKED_HOSTS = new Set([
  "localhost",
  "127.0.0.1",
  "::1",
  "0.0.0.0",
  "metadata.google.internal",
  "metadata.google",
  "169.254.169.254",
  "metadata.aws.internal",
])

const SSRF_BLOCKED_PROTOCOLS = new Set(["file:", "gopher:", "ftp:", "data:", "javascript:"])

function isUrlSSRFProne(urlString: string): boolean {
  try {
    const url = new URL(urlString)

    if (SSRF_BLOCKED_PROTOCOLS.has(url.protocol)) {
      return true
    }

    const hostname = url.hostname.toLowerCase()
    if (SSRF_BLOCKED_HOSTS.has(hostname)) {
      return true
    }

    if (hostname.startsWith("127.") || hostname.startsWith("10.") || hostname.startsWith("192.168.")) {
      return true
    }

    if (hostname.startsWith("172.")) {
      const parts = hostname.split(".")
      if (parts.length >= 1) {
        const secondOctet = parseInt(parts[0].split("-")[1] || "0", 10)
        if (secondOctet >= 16 && secondOctet <= 31) {
          return true
        }
      }
    }

    if (hostname === "localhost" || hostname.endsWith(".local") || hostname.endsWith(".localhost")) {
      return true
    }

    if (url.port && (url.port === "22" || url.port === "23" || url.port === "3389")) {
      return true
    }

    return false
  } catch {
    return true
  }
}

const startScanSchema = z.object({
  url: z
    .string()
    .url("Invalid URL format")
    .min(1, "URL is required")
    .refine(
      (url) => {
        try {
          const parsed = new URL(url)
          return parsed.protocol === "http:" || parsed.protocol === "https:"
        } catch {
          return false
        }
      },
      { message: "Only HTTP and HTTPS protocols are allowed" }
    ),
}).strict()

export async function POST(request: NextRequest) {
  const clientIp = getClientIp(request)
  const rateLimitResult = checkRateLimit(`start-scan:${clientIp}`, apiRateLimits.startScan)

  if (!rateLimitResult.success) {
    return NextResponse.json(
      { error: "Too many requests", retryAfter: Math.ceil((rateLimitResult.resetTime - Date.now()) / 1000) },
      { status: 429, headers: { "Retry-After": String(Math.ceil((rateLimitResult.resetTime - Date.now()) / 1000)) } }
    )
  }

  const user = await getSession()

  if (!user) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  }

  let body: unknown
  try {
    body = await request.json()
  } catch {
    return NextResponse.json({ error: "Invalid JSON body" }, { status: 400 })
  }

  const validationResult = startScanSchema.safeParse(body)

  if (!validationResult.success) {
    const errors = validationResult.error.errors.map((e) => ({
      field: e.path.join("."),
      message: e.message,
    }))
    return NextResponse.json({ error: "Validation failed", details: errors }, { status: 400 })
  }

  const { url } = validationResult.data

  if (isUrlSSRFProne(url)) {
    return NextResponse.json(
      { error: "URL is not allowed", details: "This URL cannot be scanned due to security restrictions" },
      { status: 400 }
    )
  }

  try {
    // Insert scan as 'queued' — the background worker will pick it up
    const result = await sql`
      INSERT INTO scans (user_id, target_url, scan_status, progress)
      VALUES (${user.id}, ${url}, 'queued', 0)
      RETURNING id
    `

    const scanId = result[0].id

    return NextResponse.json({
      success: true,
      scanId,
      message: "Scan queued successfully. The background worker will process it shortly.",
    })
  } catch (error) {
    console.error("[v0] Error starting scan:", error)
    return NextResponse.json({ error: "Failed to start scan" }, { status: 500 })
  }
}
