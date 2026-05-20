# Xiaomi MiMo Provider Notes

## API endpoints

| URL | Purpose |
|---|---|
| `https://token-plan-ams.xiaomimimo.com/v1` | **API host** — use this for `/chat/completions`, `/models` |
| `https://mimo.xiaomi.com` | Marketing site only — returns HTML 404 on API paths |

## Available models (via token-plan-ams)

- `mimo-v2-omni`
- `mimo-v2-pro` — fast non-reasoning, good for simple tasks
- `mimo-v2-tts`
- `mimo-v2.5` — reasoning-capable mid-tier
- `mimo-v2.5-pro` — reasoning model, good for complex analysis
- `mimo-v2.5-tts`
- `mimo-v2.5-tts-voiceclone`
- `mimo-v2.5-tts-voicedesign`

## Token format

Tokens start with `tp-` prefix. Example: `tp-esinantczj96bkosoa33rzc3w5408pj92cv8dtyt80dszhtt`

## Testing pattern

```bash
# Test models endpoint
curl -s --max-time 20 https://token-plan-ams.xiaomimimo.com/v1/models \
  -H "Authorization: Bearer <TOKEN>"

# Test chat (use mimo-v2-pro for quick test to avoid reasoning overhead)
curl -s --max-time 30 https://token-plan-ams.xiaomimimo.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"model":"mimo-v2-pro","messages":[{"role":"user","content":"say ok"}],"max_tokens":50}'
```

## Quirks

- **Reasoning consumes tokens:** `mimo-v2.5-pro` has reasoning mode ON by default. With low `max_tokens` (e.g., 50), the response `content` may be empty because all tokens went to reasoning. Use at least 200 tokens for a short reply, or use `mimo-v2-pro` for simple tasks.
- **Wrong host 404:** Calling `https://mimo.xiaomi.com/v1/...` returns an HTML 404 page, not JSON. Always use the `token-plan-ams` host.
- **No reasoning toggle in API:** Unlike some providers, there's no `reasoning_effort` parameter to disable reasoning mode. Switch to `mimo-v2-pro` instead.
