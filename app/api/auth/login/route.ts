import { type NextRequest, NextResponse } from "next/server"
import { getUserWithPassword } from "@/lib/db"
import { createSession, verifyPassword } from "@/lib/auth"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { email, password } = body

    console.log("[v0] Login attempt for email:", email)

    // Validation
    if (!email || !password) {
      return NextResponse.json({ error: "Email and password are required" }, { status: 400 })
    }

    const user = await getUserWithPassword(email)

    if (!user) {
      console.log("[v0] User not found:", email)
      return NextResponse.json({ error: "User not found" }, { status: 404 })
    }

    const passwordHash = user.password_hash?.toString().replace(/"/g, "") || ""
    const isValid = await verifyPassword(password, passwordHash)

    if (!isValid) {
      console.log("[v0] Invalid password for user:", email)
      return NextResponse.json({ error: "Invalid credentials" }, { status: 401 })
    }

    const isVerified = user.is_verified === true || user.is_verified === "true"
    console.log("[v0] User verification status:", { email, isVerified, rawValue: user.is_verified })

    if (!isVerified) {
      console.log("[v0] User email not verified:", email)
      return NextResponse.json(
        {
          error: "Please verify your email before logging in",
        },
        { status: 403 },
      )
    }

    // Create session
    await createSession(user.id)
    console.log("[v0] Login successful for user:", email)

    return NextResponse.json({
      success: true,
      user: {
        id: user.id,
        email: user.email,
        name: user.name,
      },
    })
  } catch (error) {
    console.error("[v0] Login error:", error)
    return NextResponse.json({ error: "An error occurred during login" }, { status: 500 })
  }
}
