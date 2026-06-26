# MiniMax Provider Setup for Hermes

**Verified:** 2026-06-18

## API Endpoint

- Base URL: `https://api.minimax.io/v1`
- Chat: `POST /v1/chat/completions` (OpenAI format)
- Models: `GET /v1/models`
- Auth: `Authorization: Bearer <key>`

## Available Models

| Model | Context | Notes |
|-------|---------|-------|
| MiniMax-M3 | 1M tokens | Frontier coding, reasoning, multimodal (text/image/video) |
| MiniMax-M2.7 | — | Previous gen |
| MiniMax-M2.5 | — | |
| MiniMax-M2.1 | — | |

## Key Types

Two key types work on MiniMax:

1. **Direct MiniMax key** (prefix: `sk-api-`, ~120 chars) — from minimax.io dashboard. Needs account balance (returns 402 if empty).
2. **Z.AI Coding Plan key** (prefix: `sk-cp-`, ~125 chars) — from Z.AI dashboard. Cross-compatible with MiniMax API. No separate balance needed (billing via Z.AI plan).

## Hermes Config

### config.yaml
```yaml
providers:
  minimax:
    base_url: https://api.minimax.io/v1
    models:
      MiniMax-M3:
        id: MiniMax-M3
        name: MiniMax M3
        context_window: 1000000
        max_tokens: 16384
        reasoning: true
```

### .env
```
MINIMAX_API_KEY=<your-key>
MINIMAX_BASE_URL=https://api.minimax.io/v1
```

### auth.json credential_pool
```json
{
  "minimax": [{
    "api_key": "<your-key>",
    "base_url": "https://api.minimax.io/v1",
    "last_status": null,
    "last_used": null
  }]
}
```

## Pitfalls

- **402 insufficient balance** — Direct MiniMax keys need account credits. Z.AI coding plan keys don't have this issue.
- **401 on Z.AI endpoints** — `sk-cp-` keys return 401 on `api.z.ai` but 200 on `api.minimax.io`. Don't assume the prefix means Z.AI.
- **Model name is case-sensitive** — `MiniMax-M3` not `minimax-m3` or `MINIMAX_M3`.
