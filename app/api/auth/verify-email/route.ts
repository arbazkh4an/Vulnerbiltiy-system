import { type NextRequest, NextResponse } from "next/server"
import { verifyToken, markTokenAsUsed, verifyUserEmail } from "@/lib/db"

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const token = searchParams.get("token")

    console.log("[v0] Email verification attempt with token:", token)

    if (!token) {
      return NextResponse.json({ error: "Token is required" }, { status: 400 })
    }

    // Verify the token
    const tokenResult = await verifyToken(token)
    console.log("[v0] Token verification result:", tokenResult)

    if (!tokenResult.valid) {
      return NextResponse.json({ error: tokenResult.error }, { status: 400 })
    }

    // Mark user as verified
    await verifyUserEmail(tokenResult.userId!)
    console.log("[v0] User marked as verified:", tokenResult.userId)

    // Mark token as used
    await markTokenAsUsed(token)
    console.log("[v0] Token marked as used")

    return NextResponse.json({
      success: true,
      message: "Email verified successfully! You can now log in.",
    })
  } catch (error) {
    console.error("[v0] Email verification error:", error)
    return NextResponse.json(
      {
        error: "An error occurred during email verification",
        details: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 },
    )
  }
}
