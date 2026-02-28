import { z } from "zod"

export const cveSchema = z.object({
  cve_id: z.string(),
  cve_description: z.string().nullable(),
  cvss_v3_score: z.number().nullable(),
  published_date: z.string().nullable(),
})

export const vulnerabilitySchema = z.object({
  id: z.string().uuid(),
  vulnerability_name: z.string(),
  vulnerability_type: z.string(),
  description: z.string(),
  cwe_id: z.string().nullable(),
  cwe_name: z.string().nullable(),
  cvss_score: z.number().nullable(),
  severity: z.enum(["critical", "high", "medium", "low", "info"]),
  ai_predicted_severity: z.string().nullable(),
  ai_confidence: z.number().nullable(),
  remediation: z.string().nullable(),
  affected_url: z.string(),
  evidence: z.string().nullable(),
  cves: z.array(cveSchema).default([]),
})

export const scanSchema = z.object({
  id: z.string().uuid(),
  target_url: z.string().url(),
  scan_status: z.enum(["pending", "running", "completed", "failed", "cancelled"]),
  started_at: z.string().datetime().nullable(),
  completed_at: z.string().datetime().nullable(),
  total_vulnerabilities: z.number().int().min(0).default(0),
  critical_count: z.number().int().min(0).default(0),
  high_count: z.number().int().min(0).default(0),
  medium_count: z.number().int().min(0).default(0),
  low_count: z.number().int().min(0).default(0),
  created_at: z.string().datetime(),
})

export const scanWithVulnerabilitiesSchema = z.object({
  scan: scanSchema,
  vulnerabilities: z.array(vulnerabilitySchema),
})

export const paginationParamsSchema = z
  .object({
    limit: z.coerce.number().int().min(1).max(100).default(50),
    offset: z.coerce.number().int().min(0).default(0),
  })
  .strict()

export const paginationResponseSchema = z.object({
  limit: z.number().int(),
  offset: z.number().int(),
  total: z.number().int(),
})

export const scanListResponseSchema = z.object({
  scans: z.array(scanSchema),
  pagination: paginationResponseSchema.optional(),
})

export const startScanRequestSchema = z
  .object({
    url: z.string().url("Invalid URL format").min(1, "URL is required"),
  })
  .strict()

export const startScanResponseSchema = z.object({
  success: z.boolean(),
  scanId: z.string().uuid(),
  message: z.string(),
  warning: z.string().optional(),
})

export const errorResponseSchema = z.object({
  error: z.string(),
  details: z.unknown().optional(),
  message: z.string().optional(),
})

export const userSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
  name: z.string().nullable(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime().nullable(),
  is_verified: z.boolean().default(false),
})

export type CVE = z.infer<typeof cveSchema>
export type Vulnerability = z.infer<typeof vulnerabilitySchema>
export type Scan = z.infer<typeof scanSchema>
export type ScanWithVulnerabilities = z.infer<typeof scanWithVulnerabilitiesSchema>
export type ScanListResponse = z.infer<typeof scanListResponseSchema>
export type StartScanRequest = z.infer<typeof startScanRequestSchema>
export type StartScanResponse = z.infer<typeof startScanResponseSchema>
export type ErrorResponse = z.infer<typeof errorResponseSchema>
export type User = z.infer<typeof userSchema>
export type PaginationParams = z.infer<typeof paginationParamsSchema>
export type PaginationResponse = z.infer<typeof paginationResponseSchema>

export function validateResponse<T>(schema: z.ZodSchema<T>, data: unknown): T {
  return schema.parse(data)
}

export function safeValidateResponse<T>(schema: z.ZodSchema<T>, data: unknown) {
  return schema.safeParse(data)
}
