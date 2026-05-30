---
name: kimi-cli
description: Delegate coding tasks to Kimi CLI (Moonshot AI's terminal coding agent). Uses sk-kimi- API keys which are gated to coding agents only - direct API calls will fail.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Coding-Agent, Kimi, Moonshot, CLI, Automation]
    related_skills: [claude-code, codex, hermes-agent]
---

# Kimi CLI — Hermes Orchestration Guide

Delegate coding tasks to Kimi CLI (Moonshot AI's terminal coding agent) via the Hermes terminal.

## CRITICAL: API Key Gating

**sk-kimi- prefixed keys ONLY work through coding agent clients.** Direct API calls to api.kimi.com/coding/v1 will return an access_terminated_error saying the API is only available for coding agents.

This is a **server-side account-level check**, NOT a header check. Spoofing User-Agent, x-client, or other headers does NOT bypass it. The Moonshot endpoints (api.moonshot.ai, api.moonshot.cn) also reject sk-kimi- keys with "Invalid Authentication".

**Conclusion:** If you have an sk-kimi- key, you MUST use it through a supported coding agent (Kimi CLI is the native one).

## API Key Refresh

When Kimi CLI returns 401, re-authenticate with:
```bash
kimi /login
# Follow the OAuth flow to get a fresh API key
```
Then verify: `kimi -p "Say hello in exactly 5 words"`

## Cost & Routing

Kimi K2.6 is a **paid subscription** (not PAYG). Prefer Kimi for coding tasks — it has the strongest DeepSWE score (24%) among available coding CLIs. DeepSeek is the PAYG fallback (8% DeepSWE). Use Kimi subscription credits before falling back to DeepSeek PAYG.

## Installation

Install Kimi CLI via pip (requires Python 3.12-3.14, 3.13 recommended). On Debian/Ubuntu you may need the --break-system-packages flag. Alternatively use the official installer from https://code.kimi.com/install.sh which handles uv and Python setup automatically.

Verify with: kimi --version

## Authentication — Config File Setup (REQUIRED)

**The KIMI_API_KEY env var alone does NOT work.** Kimi CLI ignores it and says "LLM not set, send /login to login". You must create a config file.

Config location: `~/.kimi/config.toml`

### Correct Config Format

The config schema uses `providers`, `models`, and `default_model` at the top level (NOT `[llm]`). The provider type must be `"kimi"`, NOT `"openai"`. Model keys with dots (like "kimi-k2.6") cause TOML parsing issues, so use a simple key name like "default":

```toml
default_model = "default"

[providers.kimi]
type = "kimi"
base_url = "https://api.kimi.com/coding/v1"
api_key = "YOUR_API_KEY"

[models.default]
provider = "kimi"
model = "kimi-k2.6"
max_context_size = 131072
```

### Config Discovery Process (lessons from trial and error)

1. The config path is resolved by `kimi_cli.share.get_share_dir()` -> `~/.kimi/config.toml`
2. The schema is in `kimi_cli.config.Config` (Pydantic model) -- requires `providers` dict, `models` dict, and `default_model` string
3. Provider type must be the literal `"kimi"` (see `kimi_cli.llm.ProviderType` literal)
4. TOML dotted keys like `[models.kimi-k2.6]` create nested tables in TOML, breaking pydantic validation. Use simple keys instead.
5. The `[llm]` section format found in some docs is WRONG -- that's not in the actual schema.

### Verify Config

```bash
kimi -p "Say hello in exactly 5 words"
# Should return a response, not "LLM not set"
```

## Usage via Hermes

### Print Mode (one-shot, non-interactive)

```bash
kimi -p "Fix the bug in src/auth.py"
```

No env var needed if config file is set up correctly.

### Session Continuation

```bash
kimi -C              # Continue previous session in current directory
kimi -r <session-id> # Resume specific session by ID
```

### Working Directory

```bash
kimi -w /path/to/project -p "Refactor the database layer"
```

## Integration with Hermes delegate_task

Kimi CLI can be used as a subagent through Hermes terminal:

```
terminal(command="KIMI_API_KEY='sk-kimi-...' kimi -p 'Write unit tests for src/api.py' -w /path/to/project", timeout=180)
```

For multi-turn work, use tmux:

```bash
terminal(command="tmux new-session -d -s kimi-work -x 140 -y 40")
terminal(command="tmux send-keys -t kimi-work 'KIMI_API_KEY=sk-kimi-... kimi' Enter")
terminal(command="sleep 5 && tmux send-keys -t kimi-work 'Refactor the auth module' Enter")
terminal(command="sleep 15 && tmux capture-pane -t kimi-work -p -S -50")
```

## Key Flags

| Flag | Purpose |
|------|---------|
| -p "query" | Print mode (non-interactive) |
| -w DIR | Set working directory |
| -r ID | Resume session by ID |
| -C | Continue last session in directory |
| --config JSON/TOML | Load config string |
| --config-file FILE | Load config file |
| --verbose | Verbose output |
| --debug | Debug logging |

## Pitfalls

1. **Direct API calls fail with sk-kimi- keys** -- must use coding agent client
2. **Header spoofing does NOT work** -- server-side gating, not client-side
3. **Moonshot endpoints reject sk-kimi- keys** -- different auth system entirely
4. **KIMI_API_KEY env var alone does NOT work** -- kimi CLI ignores it, needs config.toml
5. **Wrong provider type** -- must be `"kimi"`, not `"openai"`. Check `kimi_cli.llm.ProviderType` for valid types.
6. **TOML dotted model keys** -- `[models.kimi-k2.6]` creates nested table in TOML, breaking pydantic. Use simple keys like `[models.default]`.
7. **[llm] section is wrong** -- the actual schema uses `providers`, `models`, `default_model` at top level.
8. **Needs Python 3.12+** -- won't work on older Python
