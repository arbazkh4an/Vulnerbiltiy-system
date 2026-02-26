# AGENT 18 — Prompt Builder
**Depends on:** Agent 16 (knows the merged JSON shape)
**Output goes to:** `ai_engine/prompt.py`

---

## YOUR JOB
Build the system prompt and user prompt that gets sent to the LLM. This is pure prompt engineering — no API calls, just string construction.

---

## FILES TO CREATE

### `ai_engine/prompt.py`

Class `PromptBuilder`:

**Method: `build_system_prompt() → str`**

Return this exact system prompt (you can refine the wording):

```
You are a senior penetration tester and OWASP Top 10 (2021) security analyst.
You will receive structured scan data collected from automated passive and active 
reconnaissance on a target web application.

Your task:
1. Analyze the scan data for OWASP Top 10 vulnerabilities
2. Only report vulnerabilities that are directly evidenced by the scan data
3. Do NOT invent or assume findings not supported by evidence
4. Assign severity accurately: Critical / High / Medium / Low / Informational
5. Write recommendations that are specific and actionable

Risk Score Guide:
- 0-20: Minimal risk (mostly informational findings)
- 21-40: Low risk (minor misconfigurations)
- 41-60: Medium risk (real vulnerabilities but limited impact)
- 61-80: High risk (exploitable vulnerabilities present)
- 81-100: Critical risk (severe exploitable vulnerabilities, data at risk)

Output ONLY valid JSON. No markdown. No explanation outside the JSON structure.

Required output format:
{
  "scan_id": "string",
  "target": "string",
  "risk_score": integer 0-100,
  "summary": "2-3 sentence executive summary",
  "findings": [
    {
      "owasp_id": "A03:2021",
      "title": "SQL Injection in search parameter",
      "severity": "Critical",
      "evidence": "MySQL error returned when ' injected into ?q= parameter",
      "impact": "Attacker can read/write/delete database contents",
      "recommendation": "Use parameterized queries / prepared statements for all database queries",
      "references": ["https://owasp.org/www-project-top-ten/2021/A03_2021-Injection"]
    }
  ]
}
```

**Method: `build_user_prompt(merged_scan_json: dict) → str`**

Return:
```
Analyze the following automated scan data and produce a complete OWASP vulnerability report.
Focus on findings supported by concrete evidence in the data.

Scan Data:
{json.dumps(merged_scan_json, indent=2)}
```

**Method: `build_messages(merged_scan_json: dict) → list`**
Returns the messages array for the chat API:
```python
[
  { "role": "system", "content": build_system_prompt() },
  { "role": "user", "content": build_user_prompt(merged_scan_json) }
]
```

**Method: `estimate_token_count(merged_json: dict) → int`**
- Rough estimate: `len(json.dumps(merged_json)) / 4`
- If estimated tokens > 12000 → call `trim_for_context(merged_json)`

**Method: `trim_for_context(merged_json: dict) → dict`**
If JSON is too large, trim in this priority order (remove least important first):
1. Truncate `raw` fields in individual findings
2. Remove `dns_txt` records
3. Truncate CVE descriptions to 100 chars
4. Keep: all findings, severity_summary, critical exposures

---

## TESTS TO WRITE
File: `ai_engine/test_prompt.py`

- Test: build_system_prompt() returns non-empty string containing "OWASP"
- Test: build_user_prompt() contains the scan JSON serialized
- Test: build_messages() returns list with 2 items, correct roles
- Test: estimate_token_count returns integer > 0
- Test: Large JSON (>12000 tokens) gets trimmed
- Test: After trim, all critical findings still present
- Test: trim does not mutate the original dict
- Test: Output JSON format example in system prompt is valid JSON

---

## PACKAGES NEEDED
```
json (stdlib)
pytest
```

---

## DONE WHEN
All 8 tests pass. Prompts are clean and will produce reliable LLM output.
Return `ai_engine/prompt.py` and `ai_engine/test_prompt.py`.
