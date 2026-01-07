import { type NextRequest, NextResponse } from "next/server"
import { createUser, getUserByEmail, createVerificationToken } from "@/lib/db"
import { hashPassword } from "@/lib/auth"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { email, password, name } = body

    // Validation
    if (!email || !password || !name) {
      return NextResponse.json({ error: "Email, password, and name are required" }, { status: 400 })
    }

    if (password.length < 8) {
      return NextResponse.json({ error: "Password must be at least 8 characters long" }, { status: 400 })
    }

    const existingUser = await getUserByEmail(email)
    if (existingUser) {
      return NextResponse.json(
        {
          error: "User already exists, please login",
        },
        { status: 409 },
      )
    }

    // Hash password and create user
    const passwordHash = await hashPassword(password)
    const user = await createUser(email, name, passwordHash)

    const verificationToken = await createVerificationToken(user.id)

    const verificationUrl = `${process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000"}/verify-email?token=${verificationToken}`

    console.log("[v0] Verification email would be sent to:", email)
    console.log("[v0] Verification URL:", verificationUrl)

    return NextResponse.json({
      success: true,
      message: "Registration successful! Please check your email to verify your account.",
      verificationUrl, // Include in response for demo purposes
      user: {
        id: user.id,
        email: user.email,
        name: user.name,
      },
    })
  } catch (error) {
    console.error("[v0] Registration error:", error)
    return NextResponse.json({ error: "An error occurred during registration" }, { status: 500 })
  }
}
