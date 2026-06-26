# Z.AI Endpoint Architecture — Full Discovery Map

**Verified:** 2026-06-18

## Two Separate Endpoint Families

Z.AI runs TWO independent API surfaces on `api.z.ai` with different key-type permissions:

### Family 1: Anthropic-Compatible (`/api/v1/*`)

| Endpoint | Method | Auth Header | Returns |
|----------|--------|-------------|---------|
| `/api/v1/models?limit=1000` | GET | `x-api-key` | Anthropic model list (slugs: `gpt-4o`, `gpt-4o-mini`, `o3-mini`) |
| `/api/v1/messages` | POST | `x-api-key` | Anthropic Messages API format |

**Model slugs on this family** (NOT glm-* names):
- `gpt-4o` → maps to glm-5.1 (display_name: "glm-5.1")
- `gpt-4o-mini` → maps to glm-4.5-air
- `o3-mini` → maps to glm-5.1

**Key permissions:**
- MCP keys (prefix: no standard prefix, 32-char hex): 200 on `/api/v1/models`, 403 on `/api/v1/messages`
- Inference keys (prefix: 32-char hex + dot suffix): 403 on `/api/v1/messages` (use OpenAI family instead)
- Coding Plan keys (prefix: `sk-cp-`, ~125 chars): 401 on ALL Z.AI endpoints — BUT these keys are cross-compatible with MiniMax's API (`api.minimax.io`). Test with `curl -X POST https://api.minimax.io/v1/chat/completions -H "Authorization: Bearer KEY" -d '{"model":"MiniMax-M3",...}'`. Z.AI and MiniMax may share backend infrastructure. MiniMax M3 works; MiniMax M2.7 works.

### Family 2: OpenAI-Compatible (`/api/coding/paas/v4/*`)

| Endpoint | Method | Auth Header | Returns |
|----------|--------|-------------|---------|
| `/api/coding/paas/v4/models` | GET | `Authorization: Bearer` | OpenAI model list (glm-4.5, glm-5.2, etc.) |
| `/api/coding/paas/v4/chat/completions` | POST | `Authorization: Bearer` | OpenAI Chat Completions format |

**Model names on this family** (actual GLM names):
- `glm-5.2`, `glm-5.1`, `glm-5`, `glm-5-turbo`, `glm-4.7`, `glm-4.6`, `glm-4.5`, `glm-4.5-air`

**Key permissions:**
- MCP keys: 403 on all
- Inference keys: 200 on both models + chat/completions

## Critical Mismatch

Claude Code uses the Anthropic API format (`/v1/messages`). Z.AI inference keys only work on the OpenAI endpoint (`/api/coding/paas/v4/chat/completions`). This means:

1. **Direct config** (`ANTHROPIC_BASE_URL=https://api.z.ai/api`) — model validation passes but inference returns 403
2. **Proxy required** — translate Anthropic → OpenAI format, forward to `/api/coding/paas/v4/chat/completions`

## Verified Endpoint Path Map

```
Base URL                              + /v1/models?limit=1000        → Result
─────────────────────────────────────────────────────────────────────────────
https://api.z.ai                      → /v1/models                   → 404
https://api.z.ai/api                  → /api/v1/models               → 200 ✓
https://api.z.ai/api/coding/paas/v4   → /api/coding/paas/v4/v1/models → 404
https://api.z.ai/api/coding/paas/v4   → /api/coding/paas/v4/models    → 200 ✓ (OpenAI format)

Base URL                              + /v1/messages                 → Result
─────────────────────────────────────────────────────────────────────────────
https://api.z.ai/api                  → /api/v1/messages              → 403 (all key types)
https://api.z.ai/api/coding/paas/v4   → /api/coding/paas/v4/v1/messages → 404
```

## Claude Code settings.json — Working Config (via proxy)

```json
{
  "env": {
    "ANTHROPIC_API_KEY": "YOUR_INFERENCE_KEY",
    "ANTHROPIC_BASE_URL": "http://127.0.0.1:18765",
    "CLAUDE_CODE_AUTO_COMPACT_WINDOW": "1000000",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "glm-4.5-air",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "glm-5.2",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "glm-5.2"
  },
  "model": "sonnet",
  "skipDangerousModePermissionPrompt": true,
  "agentPushNotifEnabled": true
}
```

## Claude Code settings.json — Direct (no proxy, if Anthropic endpoint works)

```json
{
  "env": {
    "ANTHROPIC_API_KEY": "YOUR_KEY",
    "ANTHROPIC_BASE_URL": "https://api.z.ai/api",
    "CLAUDE_CODE_AUTO_COMPACT_WINDOW": "1000000",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "gpt-4o-mini",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "gpt-4o",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "gpt-4o"
  },
  "model": "sonnet"
}
```

## Key Diagnostic Commands

```bash
# Test which endpoint family your key works on
curl -s -X POST "https://api.z.ai/api/v1/messages" \
  -H "x-api-key: YOUR_KEY" -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"gpt-4o","max_tokens":5,"messages":[{"role":"user","content":"hi"}]}'
# 200 = works on Anthropic family, 403 = need OpenAI family

curl -s -X POST "https://api.z.ai/api/coding/paas/v4/chat/completions" \
  -H "Authorization: Bearer YOUR_KEY" \
  -H "content-type: application/json" \
  -d '{"model":"glm-5.2","max_tokens":5,"messages":[{"role":"user","content":"hi"}]}'
# 200 = works on OpenAI family

# List models on each family
curl -s "https://api.z.ai/api/v1/models" -H "x-api-key: YOUR_KEY" | python3 -m json.tool
curl -s "https://api.z.ai/api/coding/paas/v4/models" -H "Authorization: Bearer YOUR_KEY" | python3 -m json.tool
```
