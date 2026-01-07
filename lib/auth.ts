import { jwtVerify, SignJWT } from "jose"
import { cookies } from "next/headers"
import { getUserById } from "./db"

const JWT_SECRET = new TextEncoder().encode(
  process.env.JWT_SECRET || "your-secret-key-change-in-production-minimum-32-characters-long",
)

export async function createSession(userId: string) {
  const token = await new SignJWT({ userId })
    .setProtectedHeader({ alg: "HS256" })
    .setIssuedAt()
    .setExpirationTime("7d")
    .sign(JWT_SECRET)

  const cookieStore = await cookies()
  cookieStore.set("auth-token", token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    maxAge: 60 * 60 * 24 * 7, // 7 days
    path: "/",
  })

  return token
}

export async function getSession() {
  const cookieStore = await cookies()
  const token = cookieStore.get("auth-token")

  if (!token) {
    return null
  }

  try {
    const { payload } = await jwtVerify(token.value, JWT_SECRET)
    const user = await getUserById(payload.userId as string)
    return user
  } catch (error) {
    console.error("[v0] Session verification failed:", error)
    return null
  }
}

export async function destroySession() {
  const cookieStore = await cookies()
  cookieStore.delete("auth-token")
}

// Simple password hashing (in production, use bcrypt or argon2)
export async function hashPassword(password: string): Promise<string> {
  // Using Web Crypto API for hashing
  const encoder = new TextEncoder()
  const data = encoder.encode(password)
  const hashBuffer = await crypto.subtle.digest("SHA-256", data)
  const hashArray = Array.from(new Uint8Array(hashBuffer))
  return hashArray.map((b) => b.toString(16).padStart(2, "0")).join("")
}

export async function verifyPassword(password: string, hash: string): Promise<boolean> {
  const passwordHash = await hashPassword(password)
  return passwordHash === hash
}
