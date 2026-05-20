# Provider Health Check — 2026-05-13

## Summary

| Provider | /models | Chat Completions | Status |
|---|---|---|---|
| DeepSeek | OK (v4-pro, v4-flash) | Not tested (no API key exposed via terminal) | LIKELY OK — default model works, session is running on deepseek-chat |
| Xiaomi MiMo (AMS) | OK (5 models: mimo-v2-omni, v2-pro, v2.5, v2.5-pro, TTS models) | Not tested | KEY CONFIRMED active |
| Z.AI / GLM | 401 "token expired or incorrect" | Not tested | KEY LIKELY EXPIRED — `hermes status` shows ✓ but raw API returns 401 |

## What Works

- DeepSeek v4-pro — Verified available at /models endpoint, key confirmed in .env
- deepseek-chat — running as default model for this session
- Xiaomi MiMo — Token Plan AMS endpoint up, 5 models available (mimo-v2.5-pro, mimo-v2.5, mimo-v2-pro, mimo-v2-omni, mimo-v2-tts)
- Kimi — API key confirmed present in .env (sk-kimi-... key). Direct API access is 403 per known Kimi restriction. Claude Code ANTHROPIC_BASE_URL pattern validated previously.

## What's Broken

- **GLM 5.1 (zai):** API key returned 401 on /models endpoint. The key `63c5...Vnz5` exists in .env but may be expired or have wrong base URL. `hermes status` shows Z.AI as ✓ which might be stale.
- **Haiku / Copilot tier:** No provider configured at all. See routing skill "Dead Simple" tier notes.

## Key Files Checked

- `/home/ubuntu/.hermes/config.yaml` — provider blocks for xiaomi, deepseek, kimi, zai
- `/home/ubuntu/.hermes/.env` — API keys for DeepSeek, Xiaomi, Kimi, GLM
- `hermes status` — confirmed portal login, gateway running, 16 active cron jobs

## Action Items

1. Re-check GLM key — may need renewal or the key got rotated
2. Wire up Xiaomi Anthropic endpoint as a Hermes provider for a Haiku-capable tier
3. Consider GitHub Models for free fallback (not yet configured per hermes status)
