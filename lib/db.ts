import { neon } from "@neondatabase/serverless"

const databaseUrl = process.env.DATABASE_URL;

if (!databaseUrl) {
  console.warn("Warning: DATABASE_URL environment variable is not set. Database operations will fail.");
}

export const sql = databaseUrl
  ? neon(databaseUrl)
  : ((...args: any[]) => {
    throw new Error("DATABASE_URL environment variable is not set");
  }) as any;

// Helper function to get user by email
export async function getUserByEmail(email: string) {
  const result = await sql`
    SELECT id, email, name, created_at, updated_at, 
           COALESCE((raw_json->>'is_verified')::boolean, false) as is_verified
    FROM neon_auth.users_sync
    WHERE email = ${email} AND deleted_at IS NULL
    LIMIT 1
  `
  return result[0] || null
}

// Helper function to get user by ID
export async function getUserById(id: string) {
  const result = await sql`
    SELECT id, email, name, created_at, updated_at,
           COALESCE((raw_json->>'is_verified')::boolean, false) as is_verified
    FROM neon_auth.users_sync
    WHERE id = ${id} AND deleted_at IS NULL
    LIMIT 1
  `
  return result[0] || null
}

// Helper function to create a new user
export async function createUser(email: string, name: string, passwordHash: string) {
  const userId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  const signedUpAtMillis = Date.now()

  // All columns in users_sync are generated from raw_json, so we only insert raw_json
  const rawJson = {
    id: userId,
    display_name: name,
    primary_email: email,
    password_hash: passwordHash,
    signed_up_at_millis: signedUpAtMillis,
    is_verified: false, // New users start unverified
  }

  const result = await sql`
    INSERT INTO neon_auth.users_sync (raw_json)
    VALUES (${JSON.stringify(rawJson)}::jsonb)
    RETURNING id, email, name, created_at
  `

  return result[0]
}

// Get user with password hash (for authentication)
export async function getUserWithPassword(email: string) {
  const result = await sql`
    SELECT 
      id, 
      email, 
      name, 
      raw_json->>'password_hash' as password_hash, 
      COALESCE((raw_json->>'is_verified')::boolean, false) as is_verified,
      created_at
    FROM neon_auth.users_sync
    WHERE email = ${email} AND deleted_at IS NULL
    LIMIT 1
  `
  return result[0] || null
}

export async function verifyUserEmail(userId: string) {
  // Update the is_verified flag in raw_json
  await sql`
    UPDATE neon_auth.users_sync
    SET raw_json = jsonb_set(raw_json, '{is_verified}', 'true'::jsonb)
    WHERE id = ${userId}
  `
}

export async function createVerificationToken(userId: string): Promise<string> {
  const token = `verify_${Date.now()}_${Math.random().toString(36).substr(2, 32)}`
  const expiresAt = new Date(Date.now() + 24 * 60 * 60 * 1000) // 24 hours

  await sql`
    INSERT INTO email_verification_tokens (user_id, token, expires_at)
    VALUES (${userId}, ${token}, ${expiresAt})
  `

  return token
}

export async function verifyToken(token: string) {
  const result = await sql`
    SELECT user_id, expires_at, used_at
    FROM email_verification_tokens
    WHERE token = ${token}
    LIMIT 1
  `

  if (!result[0]) {
    return { valid: false, error: "Invalid token" }
  }

  const { user_id, expires_at, used_at } = result[0]

  if (used_at) {
    return { valid: false, error: "Token already used" }
  }

  if (new Date(expires_at) < new Date()) {
    return { valid: false, error: "Token expired" }
  }

  return { valid: true, userId: user_id }
}

export async function markTokenAsUsed(token: string) {
  await sql`
    UPDATE email_verification_tokens
    SET used_at = NOW()
    WHERE token = ${token}
  `
}
