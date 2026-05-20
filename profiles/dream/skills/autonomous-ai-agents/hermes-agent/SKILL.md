---
name: hermes-agent
description: "Configure, extend, or contribute to Hermes Agent."
version: 2.0.0
author: Hermes Agent + Teknium
license: MIT
metadata:
  hermes:
    tags: [hermes, setup, configuration, multi-agent, spawning, cli, gateway, development]
    homepage: https://github.com/NousResearch/hermes-agent
    related_skills: [claude-code, codex, opencode]
---

# Hermes Agent

Hermes Agent is an open-source AI agent framework by Nous Research that runs in your terminal, messaging platforms, and IDEs. It belongs to the same category as Claude Code (Anthropic), Codex (OpenAI), and OpenClaw — autonomous coding and task-execution agents that use tool calling to interact with your system. Hermes works with any LLM provider (OpenRouter, Anthropic, OpenAI, DeepSeek, local models, and 15+ others) and runs on Linux, macOS, and WSL.

What makes Hermes different:

- **Self-improving through skills** — Hermes learns from experience by saving reusable procedures as skills. When it solves a complex problem, discovers a workflow, or gets corrected, it can persist that knowledge as a skill document that loads into future sessions. Skills accumulate over time, making the agent better at your specific tasks and environment.
- **Persistent memory across sessions** — remembers who you are, your preferences, environment details, and lessons learned. Pluggable memory backends (built-in, Honcho, Mem0, and more) let you choose how memory works.
- **Multi-platform gateway** — the same agent runs on Telegram, Discord, Slack, WhatsApp, Signal, Matrix, Email, and 10+ other platforms with full tool access, not just chat.
- **Provider-agnostic** — swap models and providers mid-workflow without changing anything else. Credential pools rotate across multiple API keys automatically.
- **Profiles** — run multiple independent Hermes instances with isolated configs, sessions, skills, and memory.
- **Extensible** — plugins, MCP servers, custom tools, webhook triggers, cron scheduling, and the full Python ecosystem.

People use Hermes for software development, research, system administration, data analysis, content creation, home automation, and anything else that benefits from an AI agent with persistent context and full system access.

**This skill helps you work with Hermes Agent effectively** — setting it up, configuring features, spawning additional agent instances, troubleshooting issues, finding the right commands and settings, and understanding how the system works when you need to extend or contribute to it.

**Docs:** https://hermes-agent.nousresearch.com/docs/

## Quick Start

```bash
# Install
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash

# Interactive chat (default)
hermes

# Single query
hermes chat -q "What is the capital of France?"

# Setup wizard
hermes setup

# Change model/provider
hermes model

# Check health
hermes doctor
```

---

## CLI Reference

### Global Flags

```
hermes [flags] [command]

  --version, -V             Show version
  --resume, -r SESSION      Resume session by ID or title
  --continue, -c [NAME]     Resume by name, or most recent session
  --worktree, -w            Isolated git worktree mode (parallel agents)
  --skills, -s SKILL        Preload skills (comma-separate or repeat)
  --profile, -p NAME        Use a named profile
  --yolo                    Skip dangerous command approval
  --pass-session-id         Include session ID in system prompt
```

No subcommand defaults to `chat`.

### Chat

```
hermes chat [flags]
  -q, --query TEXT          Single query, non-interactive
  -m, --model MODEL         Model (e.g. anthropic/claude-sonnet-4)
  -t, --toolsets LIST       Comma-separated toolsets
  --provider PROVIDER       Force provider (openrouter, anthropic, nous, etc.)
  -v, --verbose             Verbose output
  -Q, --quiet               Suppress banner, spinner, tool previews
  --checkpoints             Enable filesystem checkpoints (/rollback)
  --source TAG              Session source tag (default: cli)
```

### Configuration

```
hermes setup [section]      Interactive wizard (model|terminal|gateway|tools|agent)
hermes model                Interactive model/provider picker
hermes config               View current config
hermes config edit          Open config.yaml in $EDITOR
hermes config set KEY VAL   Set a config value
hermes config path          Print config.yaml path
hermes config env-path      Print .env path
hermes config check         Check for missing/outdated config
hermes config migrate       Update config with new options
hermes login [--provider P] OAuth login (nous, openai-codex)
hermes logout               Clear stored auth
hermes doctor [--fix]       Check dependencies and config
hermes status [--all]       Show component status
```

### Tools & Skills

```
hermes tools                Interactive tool enable/disable (curses UI)
hermes tools list           Show all tools and status
hermes tools enable NAME    Enable a toolset
hermes tools disable NAME   Disable a toolset

hermes skills list          List installed skills
hermes skills search QUERY  Search the skills hub
hermes skills install ID    Install a skill (ID can be a hub identifier OR a direct https://…/SKILL.md URL; pass --name to override when frontmatter has no name)
hermes skills inspect ID    Preview without installing
hermes skills config        Enable/disable skills per platform
hermes skills check         Check for updates
hermes skills update        Update outdated skills
hermes skills uninstall N   Remove a hub skill
hermes skills publish PATH  Publish to registry
hermes skills browse        Browse all available skills
hermes skills tap add REPO  Add a GitHub repo as skill source
```

### MCP Servers

```
hermes mcp serve            Run Hermes as an MCP server
hermes mcp add NAME         Add an MCP server (--url or --command)
hermes mcp remove NAME      Remove an MCP server
hermes mcp list             List configured servers
hermes mcp test NAME        Test connection
hermes mcp configure NAME   Toggle tool selection
```

### Gateway (Messaging Platforms)

```
hermes gateway run          Start gateway foreground
hermes gateway install      Install as background service
hermes gateway start/stop   Control the service
hermes gateway restart      Restart the service
hermes gateway status       Check status
hermes gateway setup        Configure platforms
```

Supported platforms: Telegram, Discord, Slack, WhatsApp, Signal, Email, SMS, Matrix, Mattermost, Home Assistant, DingTalk, Feishu, WeCom, BlueBubbles (iMessage), Weixin (WeChat), API Server, Webhooks, IRC, Microsoft Teams, QQ Bot, Yuanbao. Open WebUI connects via the API Server adapter.

**Google Chat is NOT supported.** It existed in OpenClaw (the predecessor) but was not ported to Hermes. A community plugin platform adapter could be built following the pattern in `plugins/platforms/irc/`.

Platform docs: https://hermes-agent.nousresearch.com/docs/user-guide/messaging/

### Sessions

```
hermes sessions list        List recent sessions
hermes sessions browse      Interactive picker
hermes sessions export OUT  Export to JSONL
hermes sessions rename ID T Rename a session
hermes sessions delete ID   Delete a session
hermes sessions prune       Clean up old sessions (--older-than N days)
hermes sessions stats       Session store statistics
```

### Cron Jobs

```
hermes cron list            List jobs (--all for disabled)
hermes cron create SCHED    Create: '30m', 'every 2h', '0 9 * * *'
hermes cron edit ID         Edit schedule, prompt, delivery
hermes cron pause/resume ID Control job state
hermes cron run ID          Trigger on next tick
hermes cron remove ID       Delete a job
hermes cron status          Scheduler status
```

### Skill Curator (v0.12+)

Background maintenance task that periodically reviews agent-created skills, prunes stale ones, consolidates overlaps, and archives obsolete skills. Bundled and hub-installed skills are never touched. Archives are recoverable; auto-deletion never happens. Uses an auxiliary model for the deep review pass.

```
hermes curator status       Show status, run count, skill stats (most/least used)
hermes curator run          Trigger a review pass now (auto pass runs immediately, LLM pass runs async)
hermes curator pause        Pause the curator until resumed
hermes curator resume       Resume a paused curator
hermes curator pin NAME     Pin a skill so the curator never auto-transitions it
hermes curator unpin NAME   Unpin a pinned skill
hermes curator restore NAME Restore an archived skill
```

Default schedule: every 7 days. Stale threshold: 30 days unused. Archive threshold: 90 days unused. The auto pass runs inline; the LLM consolidation pass runs in the background — check `hermes curator status` later for results.

### Webhooks

```
hermes webhook subscribe N  Create route at /webhooks/<name>
hermes webhook list         List subscriptions
hermes webhook remove NAME  Remove a subscription
hermes webhook test NAME    Send a test POST
```

### Profiles

```
hermes profile list         List all profiles
hermes profile create NAME  Create (--clone, --clone-all, --clone-from)
hermes profile use NAME     Set sticky default
hermes profile delete NAME  Delete a profile
hermes profile show NAME    Show details
hermes profile alias NAME   Manage wrapper scripts
hermes profile rename A B   Rename a profile
hermes profile export NAME  Export to tar.gz
hermes profile import FILE  Import from archive
```

### Credential Pools

```
hermes auth add             Interactive credential wizard
hermes auth list [PROVIDER] List pooled credentials
hermes auth remove P INDEX  Remove by provider + index
hermes auth reset PROVIDER  Clear exhaustion status
```

### Other

```
hermes insights [--days N]  Usage analytics
hermes update               Update to latest version
hermes pairing list/approve/revoke  DM authorization
hermes plugins list/install/remove  Plugin management
  hermes plugins install <owner>/<repo>   Install from GitHub (e.g. obra/superpowers)
  hermes plugins install <url>            Install from any git URL
  hermes plugins enable <name>            Activate installed plugin
  hermes plugins disable <name>           Deactivate without removing
  hermes plugins remove <name>            Uninstall completely
  Lifecycle: install → enable → gateway restart (or new session for CLI)
hermes honcho setup/status  Honcho memory integration (requires honcho plugin)
hermes memory setup/status/off  Memory provider config
hermes completion bash|zsh  Shell completions
hermes acp                  ACP server (IDE integration)
hermes claw migrate         Migrate from OpenClaw
hermes uninstall            Uninstall Hermes
```

---

## Slash Commands (In-Session)

Type these during an interactive chat session.

### Session Control
```
/new (/reset)        Fresh session
/clear               Clear screen + new session (CLI)
/retry               Resend last message
/undo                Remove last exchange
/title [name]        Name the session
/compress            Manually compress context
/stop                Kill background processes
/rollback [N]        Restore filesystem checkpoint
/background <prompt> Run prompt in background
/queue <prompt>      Queue for next turn
/resume [name]       Resume a named session
```

### Configuration
```
/config              Show config (CLI)
/model [name]        Show or change model
/personality [name]  Set personality
/reasoning [level]   Set reasoning (none|minimal|low|medium|high|xhigh|show|hide)
/verbose             Cycle: off → new → all → verbose
/voice [on|off|tts]  Voice mode
/yolo                Toggle approval bypass
/skin [name]         Change theme (CLI)
/statusbar           Toggle status bar (CLI)
```

### Tools & Skills
```
/tools               Manage tools (CLI)
/toolsets            List toolsets (CLI)
/skills              Search/install skills (CLI)
/skill <name>        Load a skill into session
/cron                Manage cron jobs (CLI)
/reload-mcp          Reload MCP servers
/plugins             List plugins (CLI)
```

### Gateway
```
/approve             Approve a pending command (gateway)
/deny                Deny a pending command (gateway)
/restart             Restart gateway (gateway)
/sethome             Set current chat as home channel (gateway)
/update              Update Hermes to latest (gateway)
/platforms (/gateway) Show platform connection status (gateway)
```

### Utility
```
/branch (/fork)      Branch the current session
/fast                Toggle priority/fast processing
/browser             Open CDP browser connection
/history             Show conversation history (CLI)
/save                Save conversation to file (CLI)
/paste               Attach clipboard image (CLI)
/image               Attach local image file (CLI)
```

### Info
```
/help                Show commands
/commands [page]     Browse all commands (gateway)
/usage               Token usage
/insights [days]     Usage analytics
/status              Session info (gateway)
/profile             Active profile info
```

### Exit
```
/quit (/exit, /q)    Exit CLI
```

---

## Key Paths & Config

```
~/.hermes/config.yaml       Main configuration
~/.hermes/.env              API keys and secrets
$HERMES_HOME/skills/        Installed skills
~/.hermes/sessions/         Session transcripts
~/.hermes/logs/             Gateway and error logs
~/.hermes/auth.json         OAuth tokens and credential pools
~/.hermes/hermes-agent/     Source code (if git-installed)
```

Profiles use `~/.hermes/profiles/<name>/` with the same layout.

### Config Sections

Edit with `hermes config edit` or `hermes config set section.key value`.

| Section | Key options |
|---------|-------------|
| `model` | `default`, `provider`, `base_url`, `api_key`, `context_length` |
| `agent` | `max_turns` (90), `tool_use_enforcement` |
| `terminal` | `backend` (local/docker/ssh/modal), `cwd`, `timeout` (180) |
| `compression` | `enabled`, `threshold` (0.50), `target_ratio` (0.20) |
| `display` | `skin`, `tool_progress`, `show_reasoning`, `show_cost` |
| `stt` | `enabled`, `provider` (local/groq/openai/mistral) |
| `tts` | `provider` (edge/elevenlabs/openai/minimax/mistral/neutts) |
| `memory` | `memory_enabled`, `user_profile_enabled`, `provider` |
| `security` | `tirith_enabled`, `website_blocklist` |
| `delegation` | `model`, `provider`, `base_url`, `api_key`, `max_iterations` (50), `reasoning_effort` |
| `checkpoints` | `enabled`, `max_snapshots` (50) |

Full config reference: https://hermes-agent.nousresearch.com/docs/user-guide/configuration

### Providers

20+ providers supported. Set via `hermes model` or `hermes setup`.

| Provider | Auth | Key env var |
|----------|------|-------------|
| OpenRouter | API key | `OPENROUTER_API_KEY` |
| Anthropic | API key | `ANTHROPIC_API_KEY` |
| Nous Portal | OAuth | `hermes auth` |
| OpenAI Codex | OAuth | `hermes auth` |
| GitHub Copilot | Token | `COPILOT_GITHUB_TOKEN` |
| Google Gemini | API key | `GOOGLE_API_KEY` or `GEMINI_API_KEY` |
| DeepSeek | API key | `DEEPSEEK_API_KEY` |
| xAI / Grok | API key | `XAI_API_KEY` |
| Hugging Face | Token | `HF_TOKEN` |
| Z.AI / GLM | API key | `GLM_API_KEY` |
| MiniMax | API key | `MINIMAX_API_KEY` |
| MiniMax CN | API key | `MINIMAX_CN_API_KEY` |
| Kimi / Moonshot | API key | `KIMI_API_KEY` |
| Alibaba / DashScope | API key | `DASHSCOPE_API_KEY` |
| Xiaomi MiMo | API key | `XIAOMI_API_KEY` |
| Kilo Code | API key | `KILOCODE_API_KEY` |
| AI Gateway (Vercel) | API key | `AI_GATEWAY_API_KEY` |
| OpenCode Zen | API key | `OPENCODE_ZEN_API_KEY` |
| OpenCode Go | API key | `OPENCODE_GO_API_KEY` |
| Qwen OAuth | OAuth | `hermes login --provider qwen-oauth` |
| Custom endpoint | Config | `model.base_url` + `model.api_key` in config.yaml |
| Custom (unregistered, multi-model) | Config | `custom_providers` list in config.yaml (see below) |
| GitHub Copilot ACP | External | `COPILOT_CLI_PATH` or Copilot CLI |

Full provider docs: https://hermes-agent.nousresearch.com/docs/integrations/providers

### Custom Providers (Unregistered API Endpoints)

For API providers NOT in the built-in registry (e.g. Perceptron, Together AI, or any OpenAI-compatible endpoint with its own model list), use the `custom_providers` list in `config.yaml`. This is distinct from the `providers:` map, which only overrides settings for KNOWN providers.

**Format:**
```yaml
custom_providers:
  - name: perceptron
    base_url: https://api.perceptron.inc/v1
    api_key: sk-...                                    # inline — REQUIRED (no env-var auto-detection)
    models:
      - isaac-0.2-2b-preview
      - isaac-0.2-1b
      - perceptron-mk1
```

**Key facts:**
- Provider ID becomes `custom:<name>` (e.g. `custom:perceptron`)
- API key MUST be inline in the config entry — custom providers do NOT auto-resolve from `{NAME}_API_KEY` env vars (`api_key_env_vars=()` by design)
- To use a custom model for an auxiliary task (vision, web_extract, etc.), set the provider to `custom:<name>`:
  ```yaml
  auxiliary:
    vision:
      provider: custom:perceptron
      model: isaac-0.2-2b-preview
  ```
- Models listed under `custom_providers` are discoverable via `hermes model` picker
- All custom providers assume OpenAI-compatible chat completions transport

### Toolsets

Enable/disable via `hermes tools` (interactive) or `hermes tools enable/disable NAME`.

| Toolset | What it provides |
|---------|-----------------|
| `web` | Web search and content extraction |
| `browser` | Browser automation (Browserbase, Camofox, or local Chromium) |
| `terminal` | Shell commands and process management |
| `file` | File read/write/search/patch |
| `code_execution` | Sandboxed Python execution |
| `vision` | Image analysis |
| `image_gen` | AI image generation |
| `tts` | Text-to-speech |
| `skills` | Skill browsing and management |
| `memory` | Persistent cross-session memory |
| `session_search` | Search past conversations |
| `delegation` | Subagent task delegation |
| `cronjob` | Scheduled task management |
| `clarify` | Ask user clarifying questions |
| `messaging` | Cross-platform message sending |
| `search` | Web search only (subset of `web`) |
| `todo` | In-session task planning and tracking |
| `rl` | Reinforcement learning tools (off by default) |
| `moa` | Mixture of Agents (off by default) |
| `homeassistant` | Smart home control (off by default) |

Tool changes take effect on `/reset` (new session). They do NOT apply mid-conversation to preserve prompt caching.

---

## Security & Privacy Toggles

Common "why is Hermes doing X to my output / tool calls / commands?" toggles — and the exact commands to change them. Most of these need a fresh session (`/reset` in chat, or start a new `hermes` invocation) because they're read once at startup.

### Secret redaction in tool output

Secret redaction is **off by default** — tool output (terminal stdout, `read_file`, web content, subagent summaries, etc.) passes through unmodified. If the user wants Hermes to auto-mask strings that look like API keys, tokens, and secrets before they enter the conversation context and logs:

```bash
hermes config set security.redact_secrets true       # enable globally
```

**Restart required.** `security.redact_secrets` is snapshotted at import time — toggling it mid-session (e.g. via `export HERMES_REDACT_SECRETS=true` from a tool call) will NOT take effect for the running process. Tell the user to run `hermes config set security.redact_secrets true` in a terminal, then start a new session. This is deliberate — it prevents an LLM from flipping the toggle on itself mid-task.

Disable again with:
```bash
hermes config set security.redact_secrets false
```

### PII redaction in gateway messages

Separate from secret redaction. When enabled, the gateway hashes user IDs and strips phone numbers from the session context before it reaches the model:

```bash
hermes config set privacy.redact_pii true    # enable
hermes config set privacy.redact_pii false   # disable (default)
```

### Command approval prompts

By default (`approvals.mode: manual`), Hermes prompts the user before running shell commands flagged as destructive (`rm -rf`, `git reset --hard`, etc.). The modes are:

- `manual` — always prompt (default)
- `smart` — use an auxiliary LLM to auto-approve low-risk commands, prompt on high-risk
- `off` — skip all approval prompts (equivalent to `--yolo`)

```bash
hermes config set approvals.mode smart       # recommended middle ground
hermes config set approvals.mode off         # bypass everything (not recommended)
```

Per-invocation bypass without changing config:
- `hermes --yolo …`
- `export HERMES_YOLO_MODE=1`

Note: YOLO / `approvals.mode: off` does NOT turn off secret redaction. They are independent.

### Shell hooks allowlist

Some shell-hook integrations require explicit allowlisting before they fire. Managed via `~/.hermes/shell-hooks-allowlist.json` — prompted interactively the first time a hook wants to run.

### Disabling the web/browser/image-gen tools

To keep the model away from network or media tools entirely, open `hermes tools` and toggle per-platform. Takes effect on next session (`/reset`). See the Tools & Skills section above.

---

## Voice & Transcription

### STT (Voice → Text)

Voice messages from messaging platforms are auto-transcribed.

Provider priority (auto-detected):
1. **Local faster-whisper** — free, no API key: `pip install faster-whisper`
2. **Groq Whisper** — free tier: set `GROQ_API_KEY`
3. **OpenAI Whisper** — paid: set `VOICE_TOOLS_OPENAI_KEY`
4. **Mistral Voxtral** — set `MISTRAL_API_KEY`

Config:
```yaml
stt:
  enabled: true
  provider: local        # local, groq, openai, mistral
  local:
    model: base          # tiny, base, small, medium, large-v3
```

### TTS (Text → Voice)

| Provider | Env var | Free? |
|----------|---------|-------|
| Edge TTS | None | Yes (default) |
| ElevenLabs | `ELEVENLABS_API_KEY` | Free tier |
| OpenAI | `VOICE_TOOLS_OPENAI_KEY` | Paid |
| MiniMax | `MINIMAX_API_KEY` | Paid |
| Mistral (Voxtral) | `MISTRAL_API_KEY` | Paid |
| NeuTTS (local) | None (`pip install neutts[all]` + `espeak-ng`) | Free |

Voice commands: `/voice on` (voice-to-voice), `/voice tts` (always voice), `/voice off`.

---

## Remote Agent Access via OpenClaw Gateway + AionUi

Expose Hermes as a remote WebSocket agent so AionUi (or any OpenClaw-compatible client) can connect from any machine.

**Architecture:** `AionUi → ws://VPS:18790 → Caddy proxy → OpenClaw Gateway (loopback:18789) → hermes acp`

### Quick Setup

1. Install OpenClaw: `curl -fsSL https://openclaw.ai/install.sh | bash`
2. Write `~/.openclaw/openclaw.json` — register Hermes as acpx agent with `"hermes acp"` command
3. Install gateway service: `openclaw gateway install --token <TOKEN> --port 18789 && openclaw gateway start`
4. Add Caddy reverse proxy from a public port (e.g. 18790) to `localhost:18789`
5. Open firewall: `sudo ufw allow 18790/tcp`
6. In AionUi → Settings → Remote Agents → Add: URL `ws://VPS_IP:18790`, Token auth

### AionUi Client Fields

- **Name:** `Hermes Agent`
- **URL:** `ws://<VPS_IP>:18790`
- **Authentication:** Token → paste the gateway token

### Key Pitfalls

- **`runtime.type` validation** — do NOT set `agents.list[].runtime.type = "acp"`. Use the acpx plugin's `agents` override instead. See reference for valid config.
- **Gateway refuses non-loopback without auth** — always set `auth.token` in config.
- **Install wizard fails without TTY** — safe to ignore; write config manually.
- **Streaming not supported** — Hermes ACP responses arrive in full, not token-by-token.

Full setup guide with config template, pitfalls, and service management: `references/openclaw-gateway-remote-agent.md`

---

## Hermes WebUI Deployment

Use this workflow when the user wants `nesquena/hermes-webui` installed or served from a domain/subdomain. Full session-specific deployment notes and templates live in `references/hermes-webui-systemd-subdomain.md`.

Recommended production shape on a VPS:
1. Clone WebUI to a stable path such as `/home/ubuntu/hermes-webui`.
2. Create `/home/ubuntu/hermes-webui/.env` with `HERMES_WEBUI_AGENT_DIR`, `HERMES_WEBUI_PYTHON`, `HERMES_HOME`, `HERMES_CONFIG_PATH`, `HERMES_WEBUI_STATE_DIR`, and `HERMES_WEBUI_PASSWORD`.
3. Bind WebUI to `127.0.0.1:8787` by default. Do not expose it directly on `0.0.0.0` unless password auth and network controls are deliberate.
4. Run `server.py` directly under systemd using the Hermes Agent venv python. Avoid using `bootstrap.py` as a long-running service command because it starts `server.py` as a child and exits after health check.
5. Verify `/health` returns HTTP 200 and `/` redirects to `/login` when auth is enabled.
6. For public access, add a Caddy or Nginx reverse proxy from the requested subdomain to `127.0.0.1:8787`; validate config before reload.

**Cloudflare Tunnel subdomain pattern:** `references/cloudflare-tunnel-subdomain.md` — step-by-step for adding new subdomains to the existing tunnel ingress config. Covers DNS CNAME records, tunnel restart, and common pitfalls.

**Dashboard user theme YAML format:** `references/dashboard-theme-yaml.md` — complete schema for creating custom dashboard themes in `~/.hermes/dashboard-themes/*.yaml` with palette, typography, colorOverrides, componentStyles, and customCSS.

**Dashboard plugin creation:** `references/dashboard-plugins.md` — manifest.json structure, React vs IIFE plugins, slot injection, Agent Squad Bar pattern.

7. If the user has a domain but has not provided the exact subdomain, complete the local install/service first, then ask for the exact FQDN and DNS A/CNAME target.

Security notes:
- Generate a strong WebUI password and store it in a local `0600` file such as `/home/ubuntu/.hermes/webui-password.txt`; do not put secrets into wiki pages, memory, or skills.
- Keep `.env` permission-restricted (`chmod 600`) because it contains auth material.
- When documenting in the wiki, include non-secret service paths and verification results only.

---

## Hermes Workspace UI (outsourc-e/hermes-workspace)

The Hermes Workspace is a modern Next.js web UI for Hermes Agent — distinct from the older Flask-based WebUI. It provides chat, conductor (multi-agent orchestrator), dashboard, memory browser, terminal, and settings in one interface.

**Repo:** `https://github.com/outsourc-e/hermes-workspace`
**Landing page:** `https://hermes-workspace.com`
**Session install log:** `references/hermes-workspace-install-flow.md`

### Quick Install

```bash
curl -fsSL https://hermes-workspace.com/install.sh | bash
```

The installer detects Node 22+, Python 3.11+, pnpm — installs what's missing, installs hermes-agent from PyPI, clones the workspace to `~/hermes-workspace`, and configures `.env`. Re-runnable; skips already-installed components.

### Startup

Two daemons needed:

```bash
hermes gateway run          # terminal 1 · port 8642
cd ~/hermes-workspace && pnpm dev   # terminal 2 · port 3000

# Or both at once:
cd ~/hermes-workspace && pnpm start:all
```

Open `http://localhost:3000`.

### Critical Pitfall: API_SERVER_ENABLED

**The Workspace UI CANNOT connect to the gateway unless `API_SERVER_ENABLED=true` is set in `~/.hermes/.env`.** This is opt-in and the install script does not mention it. Without it, the gateway serves messaging platforms but does NOT expose port 8642 for HTTP API access.

```bash
echo -e "\nAPI_SERVER_ENABLED=true" >> ~/.hermes/.env
hermes gateway restart       # systemd-controlled; expect ~60s restart backoff
```

Verify: `curl http://127.0.0.1:8642/health` should return `{"status":"ok","platform":"hermes-agent"}`.

The `~/.hermes/.env` file is protected from direct file writes — use terminal commands to modify it.

### Port Reference

| Component | Port | Command |
|-----------|------|---------|
| Hermes Gateway API | 8642 | `hermes gateway run` |
| Workspace UI (dev) | 3000 | `pnpm dev` |
| Workspace UI (prod) | 3002 | `PORT=3002` in `.env`, then `pnpm start` |

### Security

The workspace exposes terminals, file read/write, agent control, and job management. Bind to loopback (default) unless you also set `CLAUDE_PASSWORD` in the workspace's `.env`. Without a password, the server refuses to start on a non-loopback host.

Remote access: proxy behind Caddy/Nginx with TLS, set `CLAUDE_PASSWORD`, `HOST=127.0.0.1`, `TRUST_PROXY=1`, and `COOKIE_SECURE=1` in `~/hermes-workspace/.env`.

### Docker Deployment

A `docker-compose.yml` and `Dockerfile` ship with the workspace. Set provider API keys in the workspace `.env` or pass them through to the `hermes-agent` container.

---

## Hermes WebUI (Legacy Flask-based)

**Note:** This section covers the older Flask-based WebUI at `nesquena/hermes-webui`. For the modern Next.js interface, see "Hermes Workspace UI" above.

---

## Spawning Additional Hermes Instances

Run additional Hermes processes as fully independent subprocesses — separate sessions, tools, and environments.

### When to Use This vs delegate_task

| | `delegate_task` | Spawning `hermes` process |
|-|-----------------|--------------------------|
| Isolation | Separate conversation, shared process | Fully independent process |
| Duration | Minutes (bounded by parent loop) | Hours/days |
| Tool access | Subset of parent's tools | Full tool access |
| Interactive | No | Yes (PTY mode) |
| Use case | Quick parallel subtasks | Long autonomous missions |

### One-Shot Mode

```
terminal(command="hermes chat -q 'Research GRPO papers and write summary to ~/research/grpo.md'", timeout=300)

# Background for long tasks:
terminal(command="hermes chat -q 'Set up CI/CD for ~/myapp'", background=true)
```

### Interactive PTY Mode (via tmux)

Hermes uses prompt_toolkit, which requires a real terminal. Use tmux for interactive spawning:

```
# Start
terminal(command="tmux new-session -d -s agent1 -x 120 -y 40 'hermes'", timeout=10)

# Wait for startup, then send a message
terminal(command="sleep 8 && tmux send-keys -t agent1 'Build a FastAPI auth service' Enter", timeout=15)

# Read output
terminal(command="sleep 20 && tmux capture-pane -t agent1 -p", timeout=5)

# Send follow-up
terminal(command="tmux send-keys -t agent1 'Add rate limiting middleware' Enter", timeout=5)

# Exit
terminal(command="tmux send-keys -t agent1 '/exit' Enter && sleep 2 && tmux kill-session -t agent1", timeout=10)
```

### Multi-Agent Coordination

```
# Agent A: backend
terminal(command="tmux new-session -d -s backend -x 120 -y 40 'hermes -w'", timeout=10)
terminal(command="sleep 8 && tmux send-keys -t backend 'Build REST API for user management' Enter", timeout=15)

# Agent B: frontend
terminal(command="tmux new-session -d -s frontend -x 120 -y 40 'hermes -w'", timeout=10)
terminal(command="sleep 8 && tmux send-keys -t frontend 'Build React dashboard for user management' Enter", timeout=15)

# Check progress, relay context between them
terminal(command="tmux capture-pane -t backend -p | tail -30", timeout=5)
terminal(command="tmux send-keys -t frontend 'Here is the API schema from the backend agent: ...' Enter", timeout=5)
```

### Profile Export & Migration

`hermes profile export` creates a tar.gz of an entire profile including session history. With large `state.db` files (500MB+), this can time out (default 30s terminal timeout).

**Workaround — manual export for migration:**

```bash
# Build a lean export (skip state.db for speed)
mkdir -p /tmp/hermes-export
cp ~/.hermes/config.yaml /tmp/hermes-export/
cp ~/.hermes/.env /tmp/hermes-export/
cp ~/.hermes/SOUL.md /tmp/hermes-export/
cp -r ~/.hermes/skills /tmp/hermes-export/
cp -r ~/.hermes/memory /tmp/hermes-export/
cp ~/.hermes/cron/jobs.json /tmp/hermes-export/
tar -czf hermes-profile.tar.gz -C /tmp/hermes-export .
```

To also include session history, add `cp ~/.hermes/state.db /tmp/hermes-export/` (expect 200MB+ compressed).

**Transfer options (when cloud storage tokens are expired):**

1. **Google Drive** (if OAuth is active):
   ```bash
   $GAPI drive upload hermes-profile.tar.gz --name "hermes-profile.tar.gz"
   ```

2. **One-time download link via existing web server:**
   ```bash
   mkdir -p /path/to/flask-app/static
   cp hermes-profile.tar.gz /path/to/flask-app/static/
   # Available at: https://example.com/static/hermes-profile.tar.gz
   ```

3. **SCP** (if user can SSH in): `scp user@host:/tmp/hermes-profile.tar.gz ~/Downloads/`

**Import on target machine:**
```bash
tar xzf hermes-profile.tar.gz -C ~/.hermes/
hermes
```

Hermes reads everything from `~/.hermes/` — no additional config needed after extract.

### Session Resume

```bash
# Resume most recent session
terminal(command="tmux new-session -d -s resumed 'hermes --continue'", timeout=10)

# Resume specific session
terminal(command="tmux new-session -d -s resumed 'hermes --resume 20260225_143052_a1b2c3'", timeout=10)
```

### Tips

- **Prefer `delegate_task` for quick subtasks** — less overhead than spawning a full process
- **Use `-w` (worktree mode)** when spawning agents that edit code — prevents git conflicts
- **Set timeouts** for one-shot mode — complex tasks can take 5-10 minutes
- **Use `hermes chat -q` for fire-and-forget** — no PTY needed
- **Use tmux for interactive sessions** — raw PTY mode has `\r` vs `\n` issues with prompt_toolkit
- **For scheduled tasks**, use the `cronjob` tool instead of spawning — handles delivery and retry

---

## Migrating Hermes to a New Machine\n\nTransfer your full Hermes setup (config, API keys, skills, memory, session history) to a new computer.\n\n### Quick migration (config + skills only, ~7MB)\n\n```bash\n# On old machine\nmkdir /tmp/hermes-export\ncp ~/.hermes/config.yaml ~/.hermes/.env ~/.hermes/SOUL.md /tmp/hermes-export/\ncp -r ~/.hermes/skills ~/.hermes/memory /tmp/hermes-export/ 2>/dev/null\ncp ~/.hermes/cron/jobs.json /tmp/hermes-export/ 2>/dev/null\ntar -czf /tmp/hermes-config-backup.tar.gz -C /tmp/hermes-export .\n\n# Transfer the file (scp, Drive, Dropbox, etc.)\n\n# On new machine\ncurl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash\ntar xzf ~/Downloads/hermes-config-backup.tar.gz -C ~/.hermes/\nhermes\n```\n\n### Full migration (including session history, ~200MB+)\n\nSame as above but include `state.db`:\n\n```bash\ncp ~/.hermes/state.db /tmp/hermes-export/\n```\n\n### Transfer methods\n\n- **Google Drive** — if `google-workspace` skill is configured: `$GAPI drive upload /tmp/backup.tar.gz --name \"hermes-backup.tar.gz\"`\n- **SCP** — if SSH key is set up: `scp user@host:/tmp/backup.tar.gz ~/Downloads/`\n- **Web download** — copy to an existing web server's static folder and serve via Cloudflare Tunnel\n- **Dropbox** — if rclone token is fresh: `rclone copy /tmp/backup.tar.gz dropbox:`\n\n### Pitfalls\n\n- **Rclone tokens expire** after extended inactivity. Both `dropbox-wiki:` and `gdrive-backup:` remotes may show \"empty token found\" errors. Reconnect with `rclone config reconnect <remote>:` (requires browser).\n- **`hermes profile export` may time out** on large profiles (500MB+ session databases). Use manual `tar` instead — it's faster and doesn't parse session files.\n- **Google Drive uploads >200MB** may exceed terminal timeout (60s). The upload often succeeds despite the timeout; verify with `drive search` afterward.\n- **Don't put API keys in chat messages.** The export files contain .env with credentials — transfer via encrypted channels or expiring download links.\n\n## Troubleshooting

### Voice not working
1. Check `stt.enabled: true` in config.yaml
2. Verify provider: `pip install faster-whisper` or set API key
3. In gateway: `/restart`. In CLI: exit and relaunch.

### Tool not available
1. `hermes tools` — check if toolset is enabled for your platform
2. Some tools need env vars (check `.env`)
3. `/reset` after enabling tools

### Model/provider issues
1. `hermes doctor` — check config and dependencies
2. `hermes login` — re-authenticate OAuth providers
3. Check `.env` has the right API key
4. **Copilot 403**: `gh auth login` tokens do NOT work for Copilot API. You must use the Copilot-specific OAuth device code flow via `hermes model` → GitHub Copilot.

### Changes not taking effect
- **Tools/skills:** `/reset` starts a new session with updated toolset
- **Config changes:** In gateway: `/restart`. In CLI: exit and relaunch.
- **Code changes:** Restart the CLI or gateway process

### Skills not showing
1. `hermes skills list` — verify installed
2. `hermes skills config` — check platform enablement
3. Load explicitly: `/skill name` or `hermes -s name`

### Gateway issues
Check logs first:
```bash
grep -i "failed to send\|error" ~/.hermes/logs/gateway.log | tail -20
```

Common gateway problems:
- **Gateway dies on SSH logout**: Enable linger: `sudo loginctl enable-linger $USER`
- **Gateway dies on WSL2 close**: WSL2 requires `systemd=true` in `/etc/wsl.conf` for systemd services to work. Without it, gateway falls back to `nohup` (dies when session closes).
- **Gateway crash loop**: Reset the failed state: `systemctl --user reset-failed hermes-gateway`
- **Workspace UI / external tools can't reach gateway on port 8642**: The HTTP API server is **opt-in**. Add `API_SERVER_ENABLED=true` to `~/.hermes/.env` and restart the gateway. Without it, the gateway serves messaging platforms but does NOT expose the HTTP API. Verify with `curl http://127.0.0.1:8642/health` — should return `{"status":"ok"}`.
- **Gateway restart backoff**: Systemd services have `RestartSec=60` — wait at least 60 seconds after `hermes gateway restart` before checking if the gateway is back up.

### Platform-specific issues
- **Discord bot silent**: Must enable **Message Content Intent** in Bot → Privileged Gateway Intents.
- **Slack bot only works in DMs**: Must subscribe to `message.channels` event. Without it, the bot ignores public channels.
- **Windows HTTP 400 "No models provided"**: Config file encoding issue (BOM). Ensure `config.yaml` is saved as UTF-8 without BOM.

### Dashboard Themes

The dashboard supports a 3-layer theming system:

1. **Built-in themes** — defined in `web/src/themes/presets.ts` as `DashboardTheme` objects with palette/typography/layout/colorOverrides/componentStyles/customCSS. Listed in `_BUILTIN_DASHBOARD_THEMES` in `web_server.py`.

2. **User YAML themes** — placed in `~/.hermes/dashboard-themes/*.yaml`. Loaded by `_discover_user_themes()` in `web_server.py` on every API call (no restart needed). Full definition shipped to frontend under `definition` key. Set active via `hermes config set dashboard.theme <name>` or `PUT /api/dashboard/theme`.

3. **Theme YAML format:**
```yaml
name: my-theme
label: My Theme
description: Description
palette:
  background: {hex: "#f5f0e8", alpha: 1.0}
  midground: {hex: "#2d2926", alpha: 1.0}      # text/accent color
  foreground: {hex: "#ffffff", alpha: 0.0}       # top highlight
  warmGlow: "rgba(74, 124, 89, 0.15)"           # backdrop vignette
  noiseOpacity: 0.25                              # grain intensity
typography:
  fontSans: "\"Inter\", system-ui, sans-serif"
  fontMono: "\"JetBrains Mono\", ui-monospace, monospace"
  fontUrl: "https://fonts.googleapis.com/..."     # injected as <link>
  baseSize: "15px"
  lineHeight: "1.55"
  letterSpacing: "0"
layout:
  radius: "1rem"           # component corner-radius
  density: comfortable      # compact | comfortable | spacious
colorOverrides:             # direct hex overrides for shadcn tokens
  card: "#ffffff"
  cardForeground: "#2d2926"
  primary: "#4a7c59"
  primaryForeground: "#ffffff"
  border: "#d9d3c7"
  ring: "#4a7c59"
  # ... cardForeground, popover, popoverForeground, secondary,
  #     secondaryForeground, muted, mutedForeground, accent,
  #     accentForeground, destructive, destructiveForeground,
  #     success, warning, border, input, ring
componentStyles:            # per-component CSS var overrides
  card:
    boxShadow: "0 1px 4px rgba(0,0,0,0.04)"
  header:
    background: "rgba(255,255,255,0.6)"
    backdropFilter: "blur(16px)"
  sidebar:
    background: "rgba(255,255,255,0.7)"
    backdropFilter: "blur(16px)"
customCSS: |                # raw CSS, injected as <style> tag, max 32KB
  .my-custom-class { ... }
assets:                     # image URLs exposed as --theme-asset-* vars
  bg: "url(...)"
  hero: "url(...)"
```

**Key pitfalls:**
- palette midground is the PRIMARY text/accent color — for light themes, set it to a dark text color (#2d2926); for dark themes, a cream (#ffe6cb)
- palette foreground with alpha 0 drives ring/glow accents
- customCSS pseudo-elements (`body::before`) work for grain textures and floating blobs
- Themes read from YAML on every API call — no restart needed for edits
- Set active theme: `hermes config set dashboard.theme natural`

### Dashboard Plugins

Plugins live in `~/.hermes/plugins/<name>/dashboard/` with:
- `manifest.json` — name, label, icon, tab config, slots, entry, css
- `dist/index.js` — plugin entry (React component or IIFE)
- `dist/style.css` — plugin styles

**Manifest format:**
```json
{
  "name": "my-plugin",
  "label": "My Plugin",
  "icon": "Puzzle",
  "tab": {"hidden": true},           // hidden: slot-only, no tab
  "slots": ["kanban-header"],        // slot names to render into
  "entry": "dist/index.js",
  "css": "dist/style.css"
}
```

**How plugins load** (`web/src/plugins/usePlugins.ts`):
1. Fetches manifests from `GET /api/dashboard/plugins`
2. Injects CSS as `<link rel="stylesheet">` via `/dashboard-plugins/<name>/<path>`
3. Injects JS as `<script async>` — executes immediately on load
4. Calls `notifyPluginRegistry()` on script load
5. Checks `getPluginComponent(name)` — sets `NO_REGISTER` error if missing (harmless for hidden plugins)

**Plugin JS patterns:**
- **React component** — calls `window.__HERMES_PLUGINS__.register(name, Component)` to register a tab component. Component renders when the plugin tab is visited.
- **DOM-enhancement IIFE** — for hidden plugins, use a self-executing function with MutationObserver to enhance existing dashboard elements. No `register()` call needed.
- **Slot injection** — calls `window.__HERMES_PLUGINS__.registerSlot(pluginName, slotName, Component)` to inject into named slots. Requires matching `<PluginSlot name="..."/>` in the target component.

**API:** `window.__HERMES_PLUGINS__ = { register, registerSlot }` and `window.__HERMES_PLUGIN_SDK__` exposes React, hooks, UI components, and utilities.

**Force plugin rescan:** `curl http://127.0.0.1:9119/api/dashboard/plugins/rescan`

### Dashboard issues

The dashboard (`hermes dashboard`) is a long-lived FastAPI+uvicorn server with no service manager — it runs as a raw process. When it "stops working" but still responds on its port, multiple stale processes have accumulated.

**Quick fix (covers 90% of cases):**
```bash
hermes dashboard --stop        # kill all running dashboard processes
hermes dashboard --port 9119 --host 127.0.0.1 --no-open &
```

**Behind Cloudflare Tunnel — 502 Bad Gateway:** This usually means the dashboard process died. Check the chain:
1. Is the process running? `ps aux | grep "hermes dashboard"`
2. If not, try starting it — if it exits immediately, the web build is broken
3. Rebuild: `cd ~/.hermes/hermes-agent/web && npm run build`
4. Fix any TypeScript errors (common: variable renames with stale references)
5. Restart: `hermes dashboard --port 9119 --host 0.0.0.0 --insecure --no-open &`
6. Verify: `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:9119/` should return 200

**⚠️ "Hermes dashboard" / "kanban board" — which one?**
When the user says "dashboard" or "kanban board", there are three possibilities. Always clarify which one unless context makes it obvious:
| Dashboard | Port | What it is | Has kanban? |
|-----------|------|------------|-------------|
| Native Hermes Dashboard | 9119 | Built-in FastAPI+SPA (`hermes dashboard`) | Yes — native Kanban tab |
| Hermes WebUI (Flask) | 8787 | External `nesquena/hermes-webui` project | No |
| Hermes Workspace (Next.js) | 3000 | External `outsourc-e/hermes-workspace` | No |

**The native dashboard (9119) is the one with the kanban board.** When the user says "kanban board" or "dashboard with kanban," start the native dashboard, not the WebUI. The WebUI is a separate Flask project with login/password — it does NOT host the kanban board.

**Behind Cloudflare Tunnel / reverse proxy — use `--insecure`:**
The native dashboard rejects requests with a Host header that doesn't match its bind address. When exposed through a Cloudflare Tunnel or reverse proxy, the Host header comes from the external domain (e.g. `hermesdash.humangood.ai`) and the dashboard returns HTTP 400 with `"Invalid Host header."`. Fix:
```bash
hermes dashboard --port 9119 --host 0.0.0.0 --insecure --no-open &
```
The `--insecure` flag disables the Host header check. Note: this also exposes the session token on the network path between the proxy and the dashboard process — only use this behind a trusted tunnel or proxy that terminates at localhost (Cloudflare Tunnel does). Never bind `--insecure` directly to a public interface without TLS.

**Diagnostic checklist** (when "fix the dashboard" is the request):

**User-created themes:** YAML files in `~/.hermes/dashboard-themes/*.yaml` let you create custom themes without rebuilding the web bundle. See `references/dashboard-user-themes.md` for the full format, light-theme palette behavior, and customCSS capabilities. Restart the dashboard process to pick up new/changed themes; switch via `hermes config set dashboard.theme <name>` or the theme picker in the UI.

**Dashboard extension (new endpoints + React components):** Pattern for adding API routes to the kanban plugin and React components to the main SPA — backend endpoint, React component, App.tsx wiring, rebuild, and restart. Full walkthrough: `references/dashboard-extension-pattern.md`.

1. **Stale processes** — the #1 culprit:
   ```bash
   ps aux | grep "hermes dashboard" | grep -v grep
   ```
   If you see more than one process, stop and restart.

2. **HTTP reachability** — is the port alive?
   ```bash
   curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:9119/
   ```

3. **Token injection** — extract the session token from the HTML and test protected endpoints:
   ```python
   import subprocess, re
   r = subprocess.run(['curl', '-s', 'http://127.0.0.1:9119/'], capture_output=True, text=True)
   token = re.search(r'window\.__HERMES_SESSION_TOKEN__="([^"]*)"', r.stdout).group(1)
   # Test with: curl -H "X-Hermes-Session-Token: $token" http://127.0.0.1:9119/api/status
   ```

4. **Smoke-test key endpoints** — if all return 200, the backend is fine:
   `/api/status`, `/api/config`, `/api/sessions`, `/api/cron`, `/api/env`

5. **Gateway health** — `/api/status` includes `gateway_running`, `gateway_platforms`, and platform connection states. If the dashboard shows gateway as "not running" but it is, the issue is likely a stale dashboard process.

6. **Frontend rebuild** — the web build output lives at `hermes_cli/web_dist/` (NOT `web/dist/`). Rebuild if source files are newer than dist:
   ```bash
   cd ~/.hermes/hermes-agent/web && npm run build
   ```
   The build is auto-triggered on dashboard start when source files are newer, so this is rarely needed manually.

7. **Version skew** — if the dashboard was started before an `hermes update`, the running process uses old code. `hermes dashboard --stop && hermes dashboard ...` picks up the latest.

**Auth architecture note:** ... (unchanged)

**User theme YAML creation:** Dashboard themes can be created as YAML files in `~/.hermes/dashboard-themes/` — no web rebuild needed. Full format, cascade explanation, kanban selector reference: `references/dashboard-user-themes.md`. A working Natural light-theme example is at `templates/dashboard-theme-natural.yaml` — copy it to `~/.hermes/dashboard-themes/` and edit. **User preference:** white background, dark readable fonts (midground near-black, green only for accents), 16px base, no light font weights.

**Agent roster:** The kanban plugin's `/agents` endpoint returns all 17 agents with live task counts. Add new agents to `_AGENT_META` in `plugins/kanban/dashboard/plugin_api.py`. Full roster and format: `references/kanban-agent-roster.md`.

Full diagnostic script with token extraction, endpoint smoke tests, and process checks: `references/dashboard-smoke-test.md`

### Auxiliary models not working
If `auxiliary` tasks (vision, compression, session_search) fail silently, the `auto` provider can't find a backend. Either set `OPENROUTER_API_KEY` or `GOOGLE_API_KEY`, or explicitly configure each auxiliary task's provider:
```bash
hermes config set auxiliary.vision.provider <your_provider>
hermes config set auxiliary.vision.model <model_name>
```

---

## OpenClaw Gateway — Remote Agent Access (AionUi)

Expose Hermes Agent as a remote agent that AionUi (desktop app) can connect to over WebSocket via an OpenClaw Gateway.

### Architecture

```
AionUi (desktop/laptop)
  → wss://agent.example.com (Cloudflare Tunnel)
  → OpenClaw Gateway (127.0.0.1:18789)
  → hermes acp
  → Full Hermes Agent
```

### Setup Steps

**1. Install OpenClaw:**
```bash
curl -fsSL https://openclaw.ai/install.sh | bash
openclaw --version
```

**2. Configure gateway** (`~/.openclaw/openclaw.json`):
```json
{
  "gateway": {
    "mode": "local",
    "port": 18789,
    "bind": "loopback",
    "auth": {
      "token": "<generate-strong-token>"
    }
  },
  "acp": {
    "enabled": true,
    "dispatch": { "enabled": true },
    "backend": "acpx",
    "defaultAgent": "hermes",
    "allowedAgents": ["hermes"],
    "maxConcurrentSessions": 4
  },
  "plugins": {
    "entries": {
      "acpx": {
        "enabled": true,
        "config": {
          "agents": {
            "hermes": {
              "command": "hermes acp"
            }
          }
        }
      }
    }
  },
  "agents": {
    "defaults": {
      "workspace": "/home/ubuntu"
    }
  }
}
```

**3. Install and start gateway service:**
```bash
openclaw gateway install --token "<your-token>" --port 18789
openclaw gateway start
openclaw gateway status
```

**4. Expose via Cloudflare Tunnel** (recommended) — add an ingress rule:
```yaml
# In ~/.cloudflared/config.yml ingress section:
  - hostname: agent.example.com
    service: ws://127.0.0.1:18789
```
Create a CNAME DNS record: `agent` → `<tunnel-id>.cfargotunnel.com` (proxied).

**5. AionUi connection details:**
- **URL:** `wss://agent.example.com`
- **Authentication:** Token
- **Token:** `<your-gateway-token>`

### Pitfalls — OpenClaw Gateway Remote Agent

1. **Caddy/Nginx reverse proxy DOES NOT WORK for OpenClaw WebSocket.** The gateway sees the forwarded `X-Forwarded-For` IP and rejects the connection as "unauthorized" even with `trustedProxies` set. Use Cloudflare Tunnel instead — it terminates the connection cleanly and the gateway sees it as local.

2. **`bind: "all"` may not take effect** if the systemd service doesn't pass a `--bind` flag. The service file may need manual editing to add `--bind 0.0.0.0` to `ExecStart`. Prefer staying on loopback + Cloudflare Tunnel.

3. **`agents.list[].runtime.type` only accepts** `"embedded"`, `"persistent"`, or `"oneshot"` — NOT `"acp"`. The ACP routing is configured via the `acp` and `plugins.entries.acpx` sections, not in `agents.list`.

4. **Gateway requires auth when bind is not loopback.** If you do bind to `0.0.0.0`, a token is mandatory or the gateway refuses to start.

5. **`gateway.*` config changes require restart.** Most config hot-reloads, but `gateway.port`, `gateway.bind`, `gateway.auth`, and `gateway.tls` need `openclaw gateway restart`.

6. **Hermes is not a built-in harness.** OpenClaw doesn't ship with Hermes as a bundled ACP agent. It must be registered via `plugins.entries.acpx.config.agents.hermes.command = "hermes acp"`. See OpenClaw issue #68496.

---

## Self-Evolution Tool

[hermes-agent-self-evolution](https://github.com/NousResearch/hermes-agent-self-evolution) — evolutionary skill/prompt optimization using DSPy + GEPA. Installed at `~/hermes-agent-self-evolution/`. Configured for DeepSeek v4-pro. See `references/hermes-self-evolution.md` for full usage, pitfalls, and model config.

```bash
cd ~/hermes-agent-self-evolution
python -m evolution.skills.evolve_skill --skill github-code-review --iterations 10
```

---

## Where to Find Things

| Looking for... | Location |
|----------------|----------|
| Config options | `hermes config edit` or [Configuration docs](https://hermes-agent.nousresearch.com/docs/user-guide/configuration) |
| Available tools | `hermes tools list` or [Tools reference](https://hermes-agent.nousresearch.com/docs/reference/tools-reference) |
| Slash commands | `/help` in session or [Slash commands reference](https://hermes-agent.nousresearch.com/docs/reference/slash-commands) |
| Skills catalog | `hermes skills browse` or [Skills catalog](https://hermes-agent.nousresearch.com/docs/reference/skills-catalog) |
| Provider setup | `hermes model` or [Providers guide](https://hermes-agent.nousresearch.com/docs/integrations/providers) |
| Platform setup | `hermes gateway setup` or [Messaging docs](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/) |
| MCP servers | `hermes mcp list` or [MCP guide](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp) |
| Profiles | `hermes profile list` or [Profiles docs](https://hermes-agent.nousresearch.com/docs/user-guide/profiles) |
| Cron jobs | `hermes cron list` or [Cron docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron) |
| Memory | `hermes memory status` or [Memory docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory) |
| Env variables | `hermes config env-path` or [Env vars reference](https://hermes-agent.nousresearch.com/docs/reference/environment-variables) |
| CLI commands | `hermes --help` or [CLI reference](https://hermes-agent.nousresearch.com/docs/reference/cli-commands) |
| Gateway logs | `~/.hermes/logs/gateway.log` |
| Session files | `~/.hermes/sessions/` or `hermes sessions browse` |
| Source code | `~/.hermes/hermes-agent/` |
| Installed plugins | `~/.hermes/plugins/<name>/` |

---

## Contributor Quick Reference

For occasional contributors and PR authors. Full developer docs: https://hermes-agent.nousresearch.com/docs/developer-guide/

### Project Layout

```
hermes-agent/
├── run_agent.py          # AIAgent — core conversation loop
├── model_tools.py        # Tool discovery and dispatch
├── toolsets.py           # Toolset definitions
├── cli.py                # Interactive CLI (HermesCLI)
├── hermes_state.py       # SQLite session store
├── agent/                # Prompt builder, context compression, memory, model routing, credential pooling, skill dispatch
├── hermes_cli/           # CLI subcommands, config, setup, commands
│   ├── commands.py       # Slash command registry (CommandDef)
│   ├── config.py         # DEFAULT_CONFIG, env var definitions
│   └── main.py           # CLI entry point and argparse
├── tools/                # One file per tool
│   └── registry.py       # Central tool registry
├── gateway/              # Messaging gateway
│   └── platforms/        # Platform adapters (telegram, discord, etc.)
├── cron/                 # Job scheduler
├── tests/                # ~3000 pytest tests
└── website/              # Docusaurus docs site
```

Config: `~/.hermes/config.yaml` (settings), `~/.hermes/.env` (API keys).

### Adding a Tool (3 files)

**1. Create `tools/your_tool.py`:**
```python
import json, os
from tools.registry import registry

def check_requirements() -> bool:
    return bool(os.getenv("EXAMPLE_API_KEY"))

def example_tool(param: str, task_id: str = None) -> str:
    return json.dumps({"success": True, "data": "..."})

registry.register(
    name="example_tool",
    toolset="example",
    schema={"name": "example_tool", "description": "...", "parameters": {...}},
    handler=lambda args, **kw: example_tool(
        param=args.get("param", ""), task_id=kw.get("task_id")),
    check_fn=check_requirements,
    requires_env=["EXAMPLE_API_KEY"],
)
```

**2. Add to `toolsets.py`** → `_HERMES_CORE_TOOLS` list.

Auto-discovery: any `tools/*.py` file with a top-level `registry.register()` call is imported automatically — no manual list needed.

All handlers must return JSON strings. Use `get_hermes_home()` for paths, never hardcode `~/.hermes`.

### Adding a Slash Command

1. Add `CommandDef` to `COMMAND_REGISTRY` in `hermes_cli/commands.py`
2. Add handler in `cli.py` → `process_command()`
3. (Optional) Add gateway handler in `gateway/run.py`

All consumers (help text, autocomplete, Telegram menu, Slack mapping) derive from the central registry automatically.

### Agent Loop (High Level)

```
run_conversation():
  1. Build system prompt
  2. Loop while iterations < max:
     a. Call LLM (OpenAI-format messages + tool schemas)
     b. If tool_calls → dispatch each via handle_function_call() → append results → continue
     c. If text response → return
  3. Context compression triggers automatically near token limit
```

### Testing

```bash
python -m pytest tests/ -o 'addopts=' -q   # Full suite
python -m pytest tests/tools/ -q            # Specific area
```

- Tests auto-redirect `HERMES_HOME` to temp dirs — never touch real `~/.hermes/`
- Run full suite before pushing any change
- Use `-o 'addopts='` to clear any baked-in pytest flags

### Commit Conventions

```
type: concise subject line

Optional body.
```

Types: `fix:`, `feat:`, `refactor:`, `docs:`, `chore:`

### Key Rules

- **Never break prompt caching** — don't change context, tools, or system prompt mid-conversation
- **Message role alternation** — never two assistant or two user messages in a row
- Use `get_hermes_home()` from `hermes_constants` for all paths (profile-safe)
- Config values go in `config.yaml`, secrets go in `.env`
- New tools need a `check_fn` so they only appear when requirements are met
