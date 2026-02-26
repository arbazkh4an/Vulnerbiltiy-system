# AGENT 17 — AI Engine (LLM Integration)
**Depends on:** Agent 16 (JSON Merger output), Agent 18 (Prompt Builder)
**Output goes to:** `ai_engine/llm_client.py`

---

## YOUR JOB
Build the AI engine that sends the merged scan JSON to an LLM and parses back a structured vulnerability report.

---

## FILES TO CREATE

### `ai_engine/llm_client.py`

Class `LLMClient`:

**Constructor:**
- Load API key from env: `GROQ_API_KEY` (primary), `OPENAI_API_KEY` (fallback)
- Set model:
  - Groq: `llama-3.3-70b-versatile`
  - OpenAI: `gpt-4o-mini`
- Set max_tokens = 4000

**Method: `analyze(merged_scan_json: dict) → AIReport`**

1. Import PromptBuilder (Agent 18)
2. Build system prompt + user prompt
3. Try Groq API first:
   ```
   POST https://api.groq.com/openai/v1/chat/completions
   Headers: Authorization: Bearer {GROQ_API_KEY}
   Body: { model, messages, temperature: 0.1, max_tokens }
   ```
4. If Groq fails → fallback to OpenAI API (same interface, different base URL)
5. Extract text from response
6. Parse JSON from response (strip markdown code fences if present)
7. Validate against `AIReport` schema
8. Return `AIReport` object

**Method: `_parse_response(raw_text: str) → dict`**
- Strip ```json and ``` if present
- `json.loads()`
- If parse fails → return error report structure

**Method: `_validate_report(data: dict) → AIReport`**
- Check required fields exist
- Clamp risk_score to 0–100
- Ensure findings is a list
- Fill missing fields with defaults

### `ai_engine/report_models.py`

```python
@dataclass
class AIFinding:
    owasp_id: str
    title: str
    severity: str        # Critical/High/Medium/Low/Info
    evidence: str
    impact: str
    recommendation: str
    references: list[str]

@dataclass
class AIReport:
    scan_id: str
    target: str
    risk_score: int      # 0-100
    summary: str
    findings: list[AIFinding]
    generated_at: str
    model_used: str
```

---

## TESTS TO WRITE
File: `ai_engine/test_llm_client.py`

Mock all HTTP calls.

- Test: Valid Groq response → AIReport returned with correct fields
- Test: Groq fails → OpenAI fallback triggered
- Test: Both APIs fail → error AIReport returned (no crash)
- Test: Response with markdown code fences → JSON parsed correctly
- Test: Invalid JSON from LLM → handled gracefully
- Test: risk_score > 100 → clamped to 100
- Test: Missing `findings` field → defaults to empty list
- Test: AI report serializes to dict correctly

---

## PACKAGES NEEDED
```
requests
pytest
pytest-mock
responses
```

---

## DONE WHEN
All 8 tests pass. LLM called correctly, response parsed safely, AIReport returned.
Return `ai_engine/llm_client.py`, `ai_engine/report_models.py`, `ai_engine/test_llm_client.py`.
