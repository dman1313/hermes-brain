# Claude Code with Proxy Providers (Non-Anthropic Backends)

## Problem

Claude Code is designed for Anthropic's API. Using it with proxy providers (z.ai, OpenRouter, custom endpoints) requires understanding three validation layers:

1. **API key auth** — Does the key authenticate? (401 vs 200/403)
2. **Model permissions** — Does the key have LLM inference access? (403 "No permission to access model")
3. **Model validation** — Does `/v1/models` return the model name? (404 → "There's an issue with the selected model")

## Debugging Flow

### Step 1: Verify API key authenticates

```python
import urllib.request, json
data = json.dumps({'model': 'test', 'max_tokens': 1, 'messages': [{'role': 'user', 'content': 'hi'}]}).encode()
req = urllib.request.Request('https://api.z.ai/api/v1/messages', data=data, method='POST')
req.add_header('Content-Type', 'application/json')
req.add_header('Authorization', 'Bearer YOUR_KEY')
req.add_header('anthropic-version', '2023-06-01')
try:
    resp = urllib.request.urlopen(req, timeout=10)
except Exception as e:
    print(getattr(e, 'code', 'N/A'))  # 401=bad key, 403=key works but no model access, 404=wrong endpoint
```

### Step 2: Find the right endpoint path

Common patterns:
- `/v1/messages` — standard Anthropic
- `/api/v1/messages` — z.ai proxy

### Step 3: Test model permissions

If you get 403 "No permission to access model", the key type doesn't support LLM inference. Get a different key from the provider dashboard.

### Step 4: Handle model validation

Claude Code queries `/v1/models` before making calls. If the proxy doesn't support this:
- Use `@lee_ai/coding-helper` (for z.ai/GLM)
- Use OpenRouter (supports `/v1/models`)
- Fall back to Hermes delegation instead

## settings.json Configuration

**NOTE:** The Z.AI-specific config, endpoint map, and model slugs are in `references/zai-endpoint-discovery.md`. The config below is a generic template.

```json
{
  "env": {
    "ANTHROPIC_API_KEY": "your-key",
    "ANTHROPIC_BASE_URL": "https://api.z.ai/api",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "gpt-4o",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "gpt-4o-mini",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "gpt-4o",
    "CLAUDE_CODE_AUTO_COMPACT_WINDOW": "1000000"
  },
  "model": "sonnet",
  "skipDangerousModePermissionPrompt": true
}
```

**Key insight:** `ANTHROPIC_DEFAULT_*_MODEL` changes the model name sent to the API, but Claude Code still validates via `/v1/models` first. The base URL must be set so that `BASE_URL/v1/models` hits a working endpoint. For Z.AI, that's `https://api.z.ai/api` (NOT `https://api.z.ai` or `https://api.z.ai/api/coding/paas/v4`).

## z.ai Key Types

z.ai issues different key types:
- **MCP keys** — work for glms-search, glms-reader, glms-zread, glms-vision (HTTP MCP servers). 403 on all LLM endpoints.
- **Inference keys** — work for LLM API calls. May work on `/api/v1/messages` (Anthropic) AND/OR `/api/coding/paas/v4/chat/completions` (OpenAI).
- **How to test:** `curl -X POST https://api.z.ai/api/v1/messages -H "x-api-key: KEY" -d '{"model":"glm-5.2","max_tokens":5,"messages":[{"role":"user","content":"hi"}]}'` — 403 = MCP key or wrong endpoint family.

## Recommended Setup

For z.ai/GLM with Claude Code:
1. **Best path:** Install `@lee_ai/coding-helper` (handles protocol translation)
   - `npm install -g @lee_ai/coding-helper@latest`
   - `chelper auth glm_coding_plan_global "YOUR_KEY"`
   - `chelper auth reload claude-code`
2. **Anthropic→OpenAI proxy** (if chelper unavailable or key only works on OpenAI endpoint):
   - Run: `ANTHROPIC_API_KEY=*** node scripts/zai-anthropic-proxy.js`
   - Set base URL: `http://127.0.0.1:18765`
   - See `references/zai-endpoint-discovery.md` for full config
3. **Direct config** (if key works on `/api/v1/messages`):
   - Set `ANTHROPIC_BASE_URL=https://api.z.ai/api` with model slugs `gpt-4o`/`gpt-4o-mini`
4. Add MCP servers via `claude mcp add` (see `references/glm-coding-plan-setup.md`)

For other proxies:
1. Verify `/v1/models` endpoint works at `BASE_URL/v1/models`
2. Set `ANTHROPIC_BASE_URL` in `~/.claude/settings.json`
3. Run `claude -p 'Say OK' --max-turns 1` to smoke test
