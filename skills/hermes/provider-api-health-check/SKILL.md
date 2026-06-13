---
name: provider-api-health-check
category: hermes
description: Systematically test LLM provider APIs to determine which models actually work. Two-phase probe of /models endpoint then chat completions.
tags: [hermes, diagnostics, models, providers, api-testing]
triggers:
  - "test all models"
  - "api check for models"
  - "which models work"
  - "validate provider APIs"
  - "check model availability"
  - "remove broken models"
  - "verify API keys"
  - "test api key"
  - "test alibaba key"
  - "test dashscope"
  - "test qwen"
---

# Provider API Health Check

Systematic validation of LLM provider APIs to determine which providers and models are actually functional. Uses a two-phase approach: first probes the `/models` endpoint for provider reachability, then tests actual chat completions to catch models that are listed but non-functional.

## Why This Matters

The models cache (`models_dev_cache.json`) lists models from 40+ providers, but:
- Many providers have no valid API keys configured
- The `/models` endpoint returns models that can't actually serve chat completions (e.g., OpenRouter lists OpenAI gpt-5.x models that all return 400)
- Credential pool status flags (e.g., `exhausted`) can be stale -- keys marked exhausted may actually work
- Base URLs change, endpoints get deprecated, API versions drift

## Prerequisites

- Access to `~/.hermes/auth.json` for credential pools
- Access to `~/.hermes/config.yaml` for provider configurations
- `curl` installed
- Python with `json` standard library
- Network connectivity to provider API endpoints

## Procedure

### Phase 1: Quick Status Scan

Start with `hermes status` to see which providers have API keys and which don't:

```
hermes status 2>&1 | grep -E "(Provider:|✓|✗|API Key)"
```

This tells you immediately which providers are authorized vs missing.

### Phase 2: Config Inventory

Read the provider blocks from config:

```python
from hermes_tools import terminal
result = terminal("cat ~/.hermes/config.yaml")
# Inspect the providers: block for base URLs and model definitions
```

### Phase 3: Test /models Endpoint (Provider Reachability) via hermes doctor

```
hermes doctor 2>&1
```

This tests /models reachability for all configured providers and reports ✓/✗/⚠ for OpenRouter, Anthropic, Z.AI/GLM, Kimi, DeepSeek, MiniMax, etc.

### Phase 4: Test Chat Completions via hermes -z (one-shot mode)

Use `hermes -z` to test actual chat completions through Hermes' own routing and credential resolution:

```bash
# Test DeepSeek
timeout 30 hermes -z "Reply with exactly OK and nothing else." --provider deepseek -m deepseek-v4-pro 2>&1

# Test Xiaomi MiMo
timeout 30 hermes -z "Reply with exactly OK and nothing else." --provider xiaomi -m mimo-v2.5-pro 2>&1

# Test Z.AI / GLM
timeout 30 hermes -z "Reply with exactly OK and nothing else." --provider zai -m glm-5.1 2>&1

# Test Kimi (usually fails via direct API — expected)
timeout 30 hermes -z "Reply with exactly OK and nothing else." --provider kimi -m kimi-for-coding 2>&1
```

**Why this approach:** Hermes resolves credentials internally and handles auth headers. You cannot extract raw API keys from .env files to use with raw `curl` — Hermes redacts secrets in terminal output.

### Phase 5: Deep Dive — Raw API Tests When hermes -z Is Insufficient

For cases where `hermes -z` succeeds but you need to distinguish between provider endpoint issues vs credential pool issues, use raw curl with secrets handled via env vars (DO NOT echo them):

## Common Pitfalls

### 1. OpenRouter Lists Models It Cannot Serve
OpenRouter returns 353+ models from /models, but OpenAI gpt-5.x models (gpt-5.5, 5.4, 5.2, 5.1, o3, o4-mini, etc.) all return HTTP 400 on chat completions. OpenRouter lacks the direct OpenAI API key needed to route these.

### 2. Credential Pool Status Is Misleading
- `status=exhausted` does not guarantee the key is dead (ZAI keys worked despite exhausted status)
- `status=ok` does not guarantee the key works today (Anthropic showed ok but returned 401)
- Always verify with actual API calls, never trust cached status

### 3. Timeout Sensitivity
| Provider | Recommended Timeout |
|----------|-------------------|
| DeepSeek | 10-15s |
| Xiaomi (both endpoints) | 10-15s |
| OpenRouter | 15-20s |
| Z.AI | 20-30s |
| Anthropic | 15s |
| Kimi | 10s |

### 4. Xiaomi Token Plan Recovery and Credential Management

The Xiaomi token plan (`token-plan-ams.xiaomimimo.com/v1`) requires TWO pieces to work:

1. **A Xiaomi token plan key** (`tp-...` format) — set as `XIAOMI_API_KEY` in `.env`
2. **An Anthropic API key configured on the Xiaomi portal** — without this, even a fresh valid token returns 401 "Invalid API Key"

**Diagnosing 401 on Xiaomi:** A 401 does NOT necessarily mean the token is invalid/expired. It often means the upstream Anthropic key hasn't been configured on the Xiaomi portal. The token itself may be fine — the portal just can't route to Anthropic without it.

**Credential update workflow (when user provides a new token):**

Step 1 — Update `.env`:
```bash
sed -i 's/^XIAOMI_API_KEY=.*/XIAOMI_API_KEY=<new-token>/' ~/.hermes/.env
```

Step 2 — Update `auth.json` credential pool entries (both `xiaomi` and `custom:xiaomi` pools):
```python
import json, time
with open('/home/ubuntu/.hermes/auth.json') as f:
    auth = json.load(f)
for pool_name in ['xiaomi', 'custom:xiaomi']:
    for entry in auth['credential_pool'].get(pool_name, []):
        entry['access_token'] = '<new-token>'
        entry['last_status'] = None   # clear exhausted/401
        entry['exhausted'] = None
        entry['last_status_at'] = time.time()
with open('/home/ubuntu/.hermes/auth.json', 'w') as f:
    json.dump(auth, f, indent=2)
```

Step 3 — Verify with raw curl (prefer curl over `hermes -z` for key validation — `hermes -z` may produce empty output even on success):
```bash
curl -s --max-time 15 "https://token-plan-ams.xiaomimimo.com/v1/chat/completions" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"model":"mimo-v2.5-pro","messages":[{"role":"user","content":"hi"}],"max_tokens":10}'
```

**Related env vars** (in `~/.hermes/.env`):
- `XIAOMI_API_KEY` — the token plan key
- `XIAOMI_BASE_URL=https://token-plan-ams.xiaomimimo.com/v1` — API endpoint
- `XIAOMI_ANTHROPIC_BASE_URL=https://token-plan-ams.xiaomimimo.com/anthropic` — Anthropic key config portal (may 404 without auth; use browser with token to access)

**Portal recovery:** If the token is valid but 401 persists, the Anthropic upstream key needs to be configured. The user must visit the Xiaomi token plan management dashboard in a browser (authenticated with their token) and add/update their Anthropic API key. The exact portal URL may differ from the API base URL.

**The `hermes status` output does NOT list Xiaomi** in the API Keys section even when configured — Xiaomi appears only as the active provider line. Do not rely on `hermes status` to confirm Xiaomi key presence; check `.env` and `auth.json` directly.

See `references/xiaomi-token-plan-recovery.md` for a session-specific recovery transcript.
See `references/alibaba-dashscope-testing.md` for DashScope/Qwen endpoint details and testing approach.

### 5. OpenRouter 402 Does Not Mean Dead Provider
OpenRouter returns HTTP 402 "This request requires more credits" when the remaining balance is insufficient for the requested `max_tokens`. The provider is alive — the request just needs a smaller `max_tokens` (try 10 for health checks). The system's remaining balance and monthly limit are available via `GET /api/v1/auth/key`. Do NOT mark OpenRouter as failed based on 402 alone.

### 6. Codex OAuth Tokens Expire (~5 Days)
OpenAI Codex uses OAuth device flow tokens that expire after a few days. If the `openai-codex` credential pool returns 403, the access token has expired. A `refresh_token` is stored but the Codex CLI (v0.118+) also changed its expected auth format — `codex whoami` may fail with `missing field id_token`. Re-authentication requires running the device flow again. Until then, Codex as a Hermes provider is dead, but the credential pool entry can stay (harmless).

### 7. API Keys Are Redacted — Use hermes -z Instead of Raw curl
Hermes redacts secrets when reading `auth.json` or `.env` via `read_file` or `terminal("cat ...")`. You **cannot** extract raw API keys to use with raw `curl` calls. Always prefer `hermes -z` (one-shot mode) for chat completion testing — it resolves credentials internally. Raw curl is only needed for deep debugging (Phase 5 in the procedure above).

## Result Categorization

Three categories for providers:
- **working**: /models responds AND chat completions pass
- **partial**: /models responds but some/all chat completions fail
- **failed**: /models endpoint unreachable, no key, or auth failure

## Reporting Format

```
## Provider Health Summary

### Working Providers
- Provider: N models -- [model list]

### Partial / Inconsistent
- Provider: N listed, M chat failures -- [details]

### Failed Providers
- Provider: Reason (404/401/no key/rate limited)
```

### 8. curl Shell Escaping Fails on API Key Testing

When testing raw API keys with curl, bash frequently breaks with `unexpected EOF while looking for matching '"'` if the key or JSON body contains characters the shell interprets. This is especially common when the key is interpolated inline.

**Fix:** Use Python urllib for raw key validation instead of curl:

```python
import urllib.request, json
req = urllib.request.Request(
    "https://endpoint/v1/chat/completions",
    data=json.dumps({"model":"model","messages":[{"role":"user","content":"hi"}],"max_tokens":10}).encode(),
    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
)
with urllib.request.urlopen(req, timeout=15) as resp:
    print(resp.read().decode())
```

No escaping issues, no heredoc gymnastics, works with any key format.

### 9. deepseek-chat and google/gemini-2.5-flash Silently Fail
These models may produce zero assistant responses on simple prompts (tested: "Reply with exactly OK"). No error message, no HTTP failure — just empty output. If testing model availability, check for non-empty responses. Use deepseek-v4-pro or mimo-v2.5-pro as the reference model for health checks. (Observed: 3 consecutive failures on deepseek-chat, 1 on gemini-2.5-flash, Apr 30 2026.)

### 10. DashScope Rate Limiting Silently Invalidates the Key

DashScope (Alibaba) does not return 429 on rate limit — it returns 401 `invalid_api_key` on ALL models, including ones that just worked. This looks like a bad key but is actually a temporary lockout.

**Trigger:** ~30 rapid requests (sequential with <1s delay) or any concurrent probing.
**Duration:** 10+ minutes cooldown.
**Fix:** Stop probing, wait 5 minutes, test with a single request. Use 3-5s delays between model probes, max 10 models per batch.

See `references/alibaba-dashscope-testing.md` for the full analysis and safe probing strategy.

## Verification After Cleanup

After removing failed providers or models:
1. Rerun Phase 4 on remaining providers
2. Verify the default model still works for completions
3. Confirm fallback providers are functional
