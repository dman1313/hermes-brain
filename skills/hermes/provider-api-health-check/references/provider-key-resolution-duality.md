# Provider API Key Resolution Duality (June 2026)

## Xiaomi vs Minimax — Two Separate Providers

| Provider | Config Name | Key Env Var | Key Prefix | Base URL |
|----------|-------------|-------------|-----------|----------|
| **Xiaomi MiMo** | `xiaomi` | `XIAOMI_API_KEY` | `tp-` (token plan) | `https://token-plan-ams.xiaomimimo.com/v1` |
| **MiniMax** | `minimax` | `MINIMAX_API_KEY` | `sk-cp-` (coding plan) | `https://api.minimax.io/v1` |

These are **completely separate accounts** with separate keys. A Xiaomi key does NOT work on the minimax endpoint and vice versa.

## Key Resolution Chain

Hermes resolves provider keys via `resolve_api_key_provider_secret()` in `hermes_cli/auth.py`:

1. Checks `api_key_env_vars` from the ProviderConfig (defined in `PROVIDER_REGISTRY` in `auth.py`)
2. For each env var, checks **both** `os.environ` **and** `~/.hermes/.env` (via `get_env_value()`)
3. Falls back to credential pool in `auth.json`

The Xiaomi ProviderConfig defines `api_key_env_vars=("XIAOMI_API_KEY",)` — it ONLY looks for `XIAOMI_API_KEY`.

## Key Location Best Practices

| Key Type | Store In | Rationale |
|----------|----------|-----------|
| Provider API keys | `~/.hermes/.env` | Auto-read by Hermes gateway, separate from shell env |
| Shell convenience keys | `~/.bashrc` | For CLI testing only — not read by gateway process |
| Xiaomi/MiMo keys | `~/.hermes/.env` | Gateway reads `.env` automatically |
| DeepSeek keys | `~/.hermes/.env` | Same |

## Verifying Key Presence

```bash
# Check if XIAOMI_API_KEY exists in .env
grep "XIAOMI_API_KEY" ~/.hermes/.env
# Output: XIAOMI_API_KEY=tp-el... (masked to *** in tool output)

# Verify by length (since values are masked)
python3 -c "line = [l for l in open('/home/ubuntu/.hermes/.env') if l.startswith('XIAOMI_API_KEY')][0]; print(f'Key length: {len(line.strip().split(\"=\",1)[1])}')"

# Check if the gateway process has the key
sudo cat /proc/$(pgrep -f "hermes_cli.main gateway")/environ 2>/dev/null | tr '\0' '\n' | grep XIAOMI
```

## Relax! These Are Fine

- Xiaomi MiMo requires `XIAOMI_API_KEY` — it does NOT need a separate `MINIMAX_API_KEY`
- The gateway reads `.env` on boot, so keys in `.env` are available even if they're not in `os.environ`
- If a cron job runs successfully with `provider: xiaomi`, the key is fine — no action needed
- The `hermes status` command does NOT show Xiaomi in its API Keys section (it only shows providers that have key entries in the credential pool, not env-var-based providers)
