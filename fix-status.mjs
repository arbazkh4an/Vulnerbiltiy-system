import { neon } from "@neondatabase/serverless";
const sql = neon(process.env.DATABASE_URL);

// Fix all non-standard statuses
const r1 = await sql`UPDATE scans SET scan_status='completed' WHERE scan_status NOT IN ('queued', 'pending', 'running', 'completed', 'failed')`;
console.log("Fixed statuses:", r1);

// Show scan statuses
const scans = await sql`SELECT id, scan_status, total_vulnerabilities, target_url FROM scans ORDER BY created_at DESC`;
for (const s of scans) {
    console.log(`${s.id} | status: "${s.scan_status}" | vulns: ${s.total_vulnerabilities} | ${s.target_url}`);
}

// Check if scan_results has any AI reports
const results = await sql`SELECT scan_id, (ai_report IS NOT NULL) as has_report, (raw_json IS NOT NULL) as has_raw FROM scan_results LIMIT 5`;
console.log("\nScan results:", results);

// Check what's in a scan_result ai_report
const aiReport = await sql`SELECT scan_id, ai_report FROM scan_results WHERE ai_report IS NOT NULL LIMIT 1`;
if (aiReport.length > 0) {
    const report = aiReport[0].ai_report;
    console.log("\nAI Report sample:", JSON.stringify(report).substring(0, 500));
}
