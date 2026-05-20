# GitHub Models API

GitHub provides free access to AI models through `models.inference.ai.azure.com` using standard GitHub authentication. No coding agent required — works with any `gh`-authenticated token.

## Endpoint

```
POST https://models.inference.ai.azure.com/chat/completions
```

## Authentication

Uses the same token as `gh` CLI. Get it with:

```bash
gh auth token
```

Or use directly:

```bash
curl -s -X POST https://models.inference.ai.azure.com/chat/completions \
  -H "Authorization: Bearer $(gh auth token)" \
  -H "Content-Type: application/json" \
  -d '{"model": "gpt-4o-mini", "messages": [{"role": "user", "content": "Say hello"}], "max_tokens": 10}'
```

## Verified Working Models (2026-05-11)

| Model | Status | Notes |
|-------|--------|-------|
| `gpt-4o-mini` | ✅ | Fast, free tier |
| `gpt-4o` | ✅ | Confirmed working |
| `Meta-Llama-3.1-405B-Instruct` | ✅ | Confirmed working, massive |
| `Meta-Llama-3.1-8B-Instruct` | ✅ | Likely available |

**Not available:** Claude models (Haiku, Sonnet, Opus), Mistral, Cohere chat, DeepSeek — GitHub Models is OpenAI + Meta only as of 2026-05-11.

### Full Model Catalog

To list all available models:
```bash
curl -s https://models.inference.ai.azure.com/models \
  -H "Authorization: Bearer $(gh auth token)" | jq -r '.[].id'
```

Current catalog (May 2026):
- `gpt-4o` (versions/2)
- `gpt-4o-mini` (versions/1)  
- `Meta-Llama-3.1-405B-Instruct` (versions/1)
- `Meta-Llama-3.1-8B-Instruct` (versions/1)
- `Cohere-embed-v3-english` (versions/3)
- `Cohere-embed-v3-multilingual` (versions/3)
- `text-embedding-3-large` (versions/1)
- `text-embedding-3-small` (versions/1)

## Response Format

Standard OpenAI-compatible chat completions response:

```json
{
  "choices": [{"message": {"content": "..."}, "finish_reason": "stop"}],
  "model": "gpt-4o-mini-2024-07-18",
  "usage": {"prompt_tokens": 9, "completion_tokens": 10, "total_tokens": 19}
}
```

## Rate Limits

GitHub Models has rate limits tied to the GitHub account tier. Free accounts get limited requests per minute/hour. Check response headers for current limits.

## Use Cases

- Quick prototyping without API key setup
- Free-tier access to GPT-4o-mini for lightweight tasks
- Backup provider when other endpoints are down
- Testing prompts before routing to paid providers

## Pitfalls

- **Token must have `models:read` scope** — classic PATs work; fine-grained tokens may need explicit permission
- **Not all GitHub tokens work** — if you get 401, check token scopes
- **Model availability changes** — GitHub rotates which models are free
- **Rate limits are per-account** — heavy usage may hit limits quickly
