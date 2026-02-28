import { z } from "zod"

const envSchema = z.object({
  DATABASE_URL: z.string().min(1, "DATABASE_URL is required"),
  JWT_SECRET: z.string().min(32, "JWT_SECRET must be at least 32 characters"),
  BACKEND_URL: z.string().url("BACKEND_URL must be a valid URL"),
  NODE_ENV: z.enum(["development", "production", "test"]).default("development"),
  NEXTAUTH_URL: z.string().url().optional(),
  NEXTAUTH_SECRET: z.string().min(32).optional(),
}).strict()

type Env = z.infer<typeof envSchema>

let envCache: Env | null = null

function validateEnv(): Env {
  if (envCache) {
    return envCache
  }

  const rawEnv = {
    DATABASE_URL: process.env.DATABASE_URL,
    JWT_SECRET: process.env.JWT_SECRET,
    BACKEND_URL: process.env.BACKEND_URL,
    NODE_ENV: process.env.NODE_ENV,
    NEXTAUTH_URL: process.env.NEXTAUTH_URL,
    NEXTAUTH_SECRET: process.env.NEXTAUTH_SECRET,
  }

  const result = envSchema.safeParse(rawEnv)

  if (!result.success) {
    const errors = result.error.errors.map((e) => `${e.path.join(".")}: ${e.message}`).join("\n")
    throw new Error(`Environment variable validation failed:\n${errors}`)
  }

  envCache = result.data
  return envCache
}

export function getEnv(): Env {
  return validateEnv()
}

export const DATABASE_URL = () => {
  const env = getEnv()
  return env.DATABASE_URL
}

export const JWT_SECRET = () => {
  const env = getEnv()
  return env.JWT_SECRET
}

export const BACKEND_URL = () => {
  const env = getEnv()
  return env.BACKEND_URL
}

export const NODE_ENV = () => {
  const env = getEnv()
  return env.NODE_ENV
}

export const NEXTAUTH_URL = () => {
  const env = getEnv()
  return env.NEXTAUTH_URL
}

export const NEXTAUTH_SECRET = () => {
  const env = getEnv()
  return env.NEXTAUTH_SECRET
}

export const isProduction = () => NODE_ENV() === "production"
export const isDevelopment = () => NODE_ENV() === "development"
export const isTest = () => NODE_ENV() === "test"
