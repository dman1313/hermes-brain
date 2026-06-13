# Alibaba DashScope (Qwen Models) — API Testing Reference

## Endpoints

Two endpoints per region, both tested 2026-06-08:

| Endpoint | Format | Auth |
|----------|--------|------|
| `dashscope.aliyuncs.com/compatible-mode/v1/chat/completions` | OpenAI-compatible | Bearer token |
| `dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation` | Native DashScope (`input.messages` wrapper) | Bearer token |

### Region Matters

| Region | Base URL | Behavior |
|--------|----------|----------|
| China mainland | `dashscope.aliyuncs.com` | Rejects international keys (401 `invalid_api_key`) |
| International | `dashscope-intl.aliyuncs.com` | Rejects domestic keys. Works with `sk-...` keys provisioned in intl console |

**A key provisioned in the international console will fail on the domestic endpoint and vice versa.** The 401 `invalid_api_key` error is the same for both "wrong region" and "wrong key" — test the correct endpoint first.

### /v1/models Endpoint

The `/v1/models` listing endpoint (OpenAI-compatible) returns 401 even with a valid API key. It appears to require different auth (possibly Alibaba Cloud AccessKey, not DashScope API key). Do NOT rely on it for model discovery — probe models directly via chat completions instead.

## Request Bodies

**OpenAI-compatible (`/compatible-mode/v1/`):**
```json
{
  "model": "qwen-plus",
  "messages": [{"role": "user", "content": "Say hello"}],
  "max_tokens": 50
}
```

**Native DashScope (`/api/v1/services/aigc/text-generation/generation`):**
```json
{
  "model": "qwen-plus",
  "input": {
    "messages": [{"role": "user", "content": "Say hello"}]
  }
}
```

## Error Responses

- **401 `invalid_api_key`** (OpenAI format) / **`InvalidApiKey`** (native format): Key is wrong, expired, wrong region, or not activated for DashScope
- Same error on both endpoints = key itself is the problem (not endpoint mismatch)
- Same error after previously working = rate limit lockout (see below)

## Rate Limiting (Critical)

DashScope international has **aggressive rate limiting** that temporarily invalidates the API key entirely (not just 429 — full 401 on all models including ones that just worked).

**Observed behavior (2026-06-08):**
- ~30 rapid sequential requests with 0.3s delay → key locked out for 10+ minutes
- Concurrent requests (ThreadPoolExecutor, 10 workers) → instant lockout
- Even 1s delay between sequential requests → lockout after all models probed
- Single request works fine before and after cooldown

**Safe probing strategy:**
1. Test ONE model first (qwen-plus) to validate key works
2. Probe remaining models sequentially with **3-5 second delays**
3. Max ~10 models per batch, then wait 60s before next batch
4. If you get 401 on a model that just worked → stop, wait 5+ minutes
5. Use Python urllib (not curl) to avoid shell escaping issues

**DO NOT use ThreadPoolExecutor/probing scripts with <3s delays.** The lockout is silent — no 429 warning, just immediate 401 on everything.

## Models (Confirmed Working)

- `qwen-plus` — balanced, good default test model (confirmed 2026-06-08)

Models likely available but blocked by rate limit during testing:
- `qwen-turbo`, `qwen-max`, `qwen-long`
- `qwen3-235b-a22b`, `qwen3-32b`, `qwen3-30b-a3b`, `qwen3-14b`, `qwen3-8b`, `qwen3-4b`
- `qwen2.5-72b-instruct`, `qwen2.5-coder-32b-instruct`
- `deepseek-v3`, `deepseek-r1` (third-party hosted on DashScope)

## Key Activation

Alibaba Cloud API keys must be explicitly enabled for DashScope/Model Studio in the console. A key that works for OSS/ECS will NOT work for DashScope. The key format is `sk-...` (same prefix as other providers).

Console: https://bailian.console.alibabacloud.com/ → API Key Management

## Quick Test Script

```python
import urllib.request, json, sys

key = sys.argv[1]
model = sys.argv[2] if len(sys.argv) > 2 else "qwen-plus"
endpoint = f"https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions"

body = json.dumps({
    "model": model,
    "messages": [{"role": "user", "content": "hi"}],
    "max_tokens": 5
}).encode()

req = urllib.request.Request(endpoint, data=body, headers={
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json",
})
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        r = json.loads(resp.read())
        print(f"OK: {r['choices'][0]['message']['content']} (model={r.get('model')})")
except Exception as e:
    err = e.read().decode()[:200] if hasattr(e, 'read') else str(e)
    print(f"FAIL: {err}")
```
