---
name: Kimi API Dual-Path Configuration
version: 1.0.0
category: autonomous-ai-agents
description: Two separate Kimi API access paths and how to configure them correctly in Hermes.
---

# Kimi API — Dual Path Reference

## Path 1: Coding-Agent API
- **Base URL:** `https://api.kimi.com/coding/v1`
- **Key prefix:** `sk-kimi-`
- **Usage:** Hermes delegation, coding subagents (Kimi CLI, Claude Code, Roo Code, etc.)
- **Direct REST:** BLOCKED (403 — "only available for Coding Agents")
- **Through Hermes:** Works correctly
- **Hermes config:** `provider: kimi-for-coding`, `model: k2p5`

## Path 2: Moonshot Platform API
- **Base URL:** `https://api.moonshot.ai/v1`
- **Key:** Generated at https://platform.kimi.ai/console/api-keys
- **Usage:** Standard OpenAI-compatible API access
- **Models:** `kimi-k2.6`, `kimi-k2-thinking`, etc.
- **Direct REST:** Works with correct platform key
- **Important:** Keys from path 1 do NOT work here (401 Invalid Authentication)

## Key Facts
- `platform.kimi.com` and `platform.kimi.ai` are SEPARATE — keys/accounts not interchangeable
- `sk-kimi-` keys are coding-agent only, not valid for Moonshot platform API
- Hermes internally normalizes `kimi-for-coding` to `kimi-coding` — that is expected
- Kimi base URL must include `/v1` suffix or calls return 404

## Common Issues
| Symptom | Cause | Fix |
|---------|-------|-----|
| 403 on direct REST | Using coding-agent endpoint directly | Use Hermes delegation or switch to platform API |
| 404 on Hermes call | Missing `/v1` in base URL | Set base URL to include `/v1` |
| 401 on moonshot API | Using `sk-kimi-` key for platform | Generate correct platform key from platform.kimi.ai |
| model_not_found | Wrong base URL | Verify `base_url=https://api.moonshot.ai/v1` for platform path |

## Hermes Config Fix (already applied)
The Kimi base URL was fixed to include `/v1`. The working Hermes coding-agent path is confirmed functional for both `kimi-k2.5` and `kimi-k2.6`.
