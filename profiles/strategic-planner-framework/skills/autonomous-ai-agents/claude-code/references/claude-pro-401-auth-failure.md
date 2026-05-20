# Claude Code — Claude Pro 401 Auth Failure

## Symptom

`claude auth status` reports "logged in" but every API call fails with 401.

## Auth Status Output (looks healthy — it's not)

```json
{
  "loggedIn": true,
  "authMethod": "claude.ai",
  "apiProvider": "firstParty",
  "email": "dwayneprimeau@gmail.com",
  "orgId": "27c0f3f2-6c85-4ce9-970f-bf9be6eb533b",
  "orgName": "Dwayne",
  "subscriptionType": "pro"
}
```

## Print Mode (-p) Failure

```json
{
  "type": "result",
  "subtype": "success",
  "is_error": true,
  "api_error_status": 401,
  "result": "Failed to authenticate. API Error: 401 {\"type\":\"error\",\"error\":{\"type\":\"authentication_error\",\"message\":\"Invalid authentication credentials\"},\"request_id\":\"req_011CaeRaxmxZFtaMrW8gHsKH\"}",
  "total_cost_usd": 0,
  "usage": {"input_tokens": 0, "output_tokens": 0}
}
```

## Interactive Mode Failure

Every user message (including the first one after the welcome screen) returns:

```
Please run /login · API Error: 401 {"type":"error","error":{"type":"authentication_error","message":"Invalid authentication credentials"}}
```

The welcome screen and TUI render fine. Claude accepts input. It just can't make any API call.

## Root Cause

Claude Pro ($20/mo) is a consumer subscription for claude.ai browser chat only. It does NOT grant API access. Claude Code CLI requires API-key billing — an `ANTHROPIC_API_KEY` env var + `claude auth login --console` to bind it, or a Max/Team/Enterprise plan.

## Resolution

1. Get an API key from https://console.anthropic.com/
2. Export it: `export ANTHROPIC_API_KEY=sk-ant-...`
3. Run `claude auth login --console` in an interactive terminal (NOT via agent/script — requires TTY)
4. Verify: `claude -p "Say OK" --max-turns 1 --output-format json | python3 -c 'import sys,json; print(json.load(sys.stdin)["subtype"])'` should print `success`

## Detection

Run the smoke test before any Claude Code task:

```
claude -p 'Say OK' --max-turns 1 --output-format json 2>&1 | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get("subtype","UNKNOWN"))'
```

- `success` → good to go
- `error` / 401 → Pro mismatch, needs API key
