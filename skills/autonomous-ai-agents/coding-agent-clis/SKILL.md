---
name: coding-agent-clis
description: "Hermes orchestration of external coding agent CLIs — Claude Code, Codex, OpenCode. Covers prerequisites, one-shot tasks, interactive sessions, PR reviews, parallel work patterns, and per-tool pitfalls."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Coding-Agent, CLI, Claude, Codex, OpenCode, Automation, PTY, Orchestration]
    related_skills: [hermes-agent, github-pr-workflow, github-code-review]
---

# Coding Agent CLIs — Hermes Orchestration Guide

Hermes orchestrates external coding agent CLIs (Claude Code, Codex, OpenCode) via terminal/process tools. Each tool has the same integration shape: prerequisites → one-shot mode → interactive mode → PR review → parallel work → pitfalls.

## Choosing the Right Tool

| Tool | Provider | Best for | Auth |
|------|----------|----------|------|
| **Claude Code** | Anthropic | Complex multi-step reasoning, deep code review, autonomous refactoring | API key or Claude Max/Team/Enterprise |
| **Codex** | OpenAI | Quick one-shot tasks, batch issue fixing, sandboxed execution | OpenAI API key or Codex OAuth |
| **OpenCode** | Multi-provider | Provider-agnostic work, when you want model flexibility | OpenRouter, Anthropic, OpenAI, etc. |

**Decision tree:**
1. User explicitly requests a tool → use that one
2. Need deep reasoning / complex multi-file changes → Claude Code
3. Need fast sandboxed one-shot tasks → Codex
4. Need provider flexibility or model choice → OpenCode
5. None installed → use Hermes `delegate_task` as fallback

## Shared Orchestration Patterns

All three tools follow the same integration patterns:

### One-Shot Tasks (PREFERRED for most work)
Run a bounded task, get the result, exit. No PTY overhead.

### Interactive Sessions (for iterative work)
Start a TUI in background, send prompts, monitor progress, exit when done. Requires `pty=true`.

### PR Reviews
Clone to temp dir, check out PR branch, run review, post results.

### Parallel Work
Use separate workdirs/worktrees to avoid file collisions. Launch multiple instances in background.

---

## Claude Code

Delegate coding tasks to [Claude Code](https://code.claude.com/docs/en/cli-reference) (Anthropic's autonomous coding agent CLI). Claude Code v2.x can read files, write code, run shell commands, spawn subagents, and manage git workflows autonomously.

### Prerequisites

- **Install:** `npm install -g @anthropic-ai/claude-code`
- **Auth:** Requires API-key billing, NOT a Claude Pro subscription. Claude Pro ($20/mo) only works through claude.ai browser chat — it will NOT authenticate the CLI. You need one of:
  - `ANTHROPIC_API_KEY` env var + `claude auth login --console` (API key billing)
  - Claude Max/Team/Enterprise subscription
  - `claude auth login --sso` for Enterprise
- **Check status:** `claude auth status` (JSON) or `claude auth status --text` (human-readable). WARNING: this can show "logged in" even when the CLI can't make API calls (Pro subscription mismatch). Always follow up with the smoke test.
- **Health check:** `claude doctor` — checks auto-updater and installation health
- **Version check:** `claude --version` (requires v2.x+)

### Print Mode (`-p`) — Non-Interactive (PREFERRED)

Print mode runs a one-shot task, returns the result, and exits. No PTY needed. No interactive prompts. This is the cleanest integration path.

```
terminal(command="claude -p 'Add error handling to all API calls in src/' --allowedTools 'Read,Edit' --max-turns 10", workdir="/path/to/project", timeout=120)
```

**When to use:** One-shot coding tasks, CI/CD automation, structured data extraction with `--json-schema`, piped input processing.

**Print mode skips ALL interactive dialogs** — no workspace trust prompt, no permission confirmations.

### Interactive PTY via tmux — Multi-Turn Sessions

Interactive mode gives you a full conversational REPL. **Requires tmux orchestration.**

```
# Start a tmux session
terminal(command="tmux new-session -d -s claude-work -x 140 -y 40")

# Launch Claude Code inside it
terminal(command="tmux send-keys -t claude-work 'cd /path/to/project && claude' Enter")

# Wait for startup, then send your task
terminal(command="sleep 5 && tmux send-keys -t claude-work 'Refactor the auth module to use JWT tokens' Enter")

# Monitor progress
terminal(command="sleep 15 && tmux capture-pane -t claude-work -p -S -50")

# Send follow-up tasks
terminal(command="tmux send-keys -t claude-work 'Now add unit tests for the new JWT code' Enter")

# Exit when done
terminal(command="tmux send-keys -t claude-work '/exit' Enter")
```

### PTY Dialog Handling (CRITICAL for Interactive Mode)

Claude Code presents up to two confirmation dialogs on first launch:

**Dialog 1: Workspace Trust (first visit to a directory)**
```
❯ 1. Yes, I trust this folder    ← DEFAULT (just press Enter)
  2. No, exit
```
**Handling:** `tmux send-keys -t <session> Enter`

**Dialog 2: Bypass Permissions Warning (only with --dangerously-skip-permissions)**
```
❯ 1. No, exit                    ← DEFAULT (WRONG choice!)
  2. Yes, I accept
```
**Handling:** Must navigate DOWN first, then Enter:
```
tmux send-keys -t <session> Down && sleep 0.3 && tmux send-keys -t <session> Enter
```

### Key CLI Flags

| Flag | Effect |
|------|--------|
| `-p, --print` | Non-interactive one-shot mode |
| `--model <alias>` | Model selection: `sonnet`, `opus`, `haiku` |
| `--max-turns <n>` | Limit agentic loops (print mode only) |
| `--max-budget-usd <n>` | Cap API spend |
| `--dangerously-skip-permissions` | Auto-approve ALL tool use |
| `--allowedTools <tools...>` | Whitelist specific tools |
| `--output-format <fmt>` | `text`, `json`, `stream-json` |
| `--bare` | Skip hooks, plugins, MCP, CLAUDE.md |
| `--effort <level>` | `low`, `medium`, `high`, `max`, `auto` |
| `--fallback-model <model>` | Auto-fallback when overloaded |
| `-r, --resume <id>` | Resume specific session |
| `-c, --continue` | Resume most recent conversation |
| `-w, --worktree [name]` | Run in isolated git worktree |

### Structured JSON Output

```
terminal(command="claude -p 'Analyze auth.py for security issues' --output-format json --max-turns 5", workdir="/project", timeout=120)
```

Returns: `session_id` for resumption, `num_turns` for loop count, `total_cost_usd` for spend tracking, `subtype` for success/error detection.

### Session Continuation

```
# Resume with session ID
terminal(command="claude -p 'Continue and add connection pooling' --resume <session_id> --max-turns 5", workdir="/project", timeout=120)

# Or resume the most recent session
terminal(command="claude -p 'What did you do last time?' --continue --max-turns 1", workdir="/project", timeout=30)
```

### Slash Commands (Interactive Mode)

| Command | Purpose |
|---------|---------|
| `/compact [focus]` | Compress context to save tokens |
| `/review` | Request code review |
| `/model [model]` | Switch models mid-session |
| `/effort [level]` | Set reasoning effort |
| `/cost` | View token usage |
| `/context` | Visualize context usage |

### Pitfalls (Claude Code)

1. **Interactive mode REQUIRES tmux** — Claude Code is a full TUI app. Using `pty=true` alone works but tmux gives you `capture-pane` for monitoring.
2. **`--dangerously-skip-permissions` dialog defaults to "No, exit"** — you must send Down then Enter to accept. Print mode (`-p`) skips this entirely.
3. **`--max-budget-usd` minimum is ~$0.05** — system prompt cache creation alone costs this much.
4. **Claude Pro ($20/mo) does NOT work with Claude Code CLI** — `claude auth status` reports "logged in" but ALL API calls return 401. Always run the smoke test.
5. **Context degradation is real** — AI output quality measurably degrades above 70% context window usage. Monitor with `/compact`.
6. **ANTHROPIC_API_KEY alone does NOT authenticate `claude` CLI for print mode** — Claude Code v2.x checks OAuth first. Use `claude auth login --console` once to bind the key.
7. **Print mode with `pty=true` can hit the 600s Hermes timeout** — check `git diff --stat` afterward; changes are often written to disk even if Hermes reports a timeout.
- **Non-Anthropic backends consistently time out with bare `ANTHROPIC_BASE_URL`** — For GLM/Z.AI, use `@lee_ai/coding-helper` npm package. For other backends: fall back to building directly or use Goose CLI.
- **Claude Code `--model` only accepts Anthropic model aliases** — `sonnet`, `opus`, `haiku`, or full names like `claude-sonnet-4-6`. You CANNOT pass `--model glm-5.1` or `--model glm-5.2` — Claude Code will reject non-Anthropic model names. The Z.AI proxy translates Anthropic API calls to GLM on the backend, but model selection stays within the Anthropic family. To use GLM models directly, call them through Hermes (`hermes -z --provider zai -m glm-5.2`) instead of Claude Code.
- **Claude Code validates models via `/v1/models` endpoint** — Before making API calls, Claude Code queries `{BASE_URL}/v1/models?limit=1000` to verify the model exists. For Z.AI, the correct base URL is `https://api.z.ai/api` (NOT `/api/coding/paas/v4`) — this makes Claude Code hit `/api/v1/models` which returns the model list. If your inference key only works on the OpenAI-compatible endpoint (`/api/coding/paas/v4/chat/completions`), use the Anthropic→OpenAI proxy at `scripts/zai-anthropic-proxy.js`. See `references/zai-endpoint-discovery.md` for the full Z.AI endpoint map, key types, and model slugs.
- **Auth success ≠ model permissions (401 vs 403)** — An API key that authenticates (no 401) may still return 403 "No permission to access model" for every model. This happens when the key was issued for MCP/web tools only, not LLM inference. The z.ai dashboard issues different key types — MCP keys (for glms-search, glms-reader, etc.) and inference keys (for LLM calls). A single key may work for one but not the other. Test with: `python3 -c "import urllib.request, json; ... POST to /api/v1/messages ..."` to verify inference access before configuring Claude Code.
- **`~/.claude/settings.json` env vars for model routing** — Claude Code reads env vars from `settings.json`'s `env` object. Useful overrides: `ANTHROPIC_DEFAULT_SONNET_MODEL`, `ANTHROPIC_DEFAULT_HAIKU_MODEL`, `ANTHROPIC_DEFAULT_OPUS_MODEL` (set to proxy-specific model names), `ANTHROPIC_BASE_URL` (set to proxy endpoint), `CLAUDE_CODE_AUTO_COMPACT_WINDOW` (context window size). Format: `{ "env": { "KEY": "value" }, "model": "sonnet" }`. Note: model validation still applies — the env vars only change what name is sent, not whether the proxy accepts it.
- **Project files may live on Dwayne's Mac, not the VPS** — Before launching Claude Code on the VPS for a project task, verify the project directory and skill files exist locally. The PYP planner skill is at `~/.claude/skills/pyp-planner/SKILL.md` on the Mac. If files are Mac-only, either (a) sync them to the VPS first, (b) run Claude Code on the Mac via SSH, or (c) use Hermes directly with whatever context is available.
- **Z.AI correct base URL is `https://api.z.ai/api`** — NOT `/api/coding/paas/v4` or bare `https://api.z.ai`. Claude Code appends `/v1/models` to the base URL; only `https://api.z.ai/api/v1/models` returns 200. Model slugs exposed: `gpt-4o` (→ glm-5.1), `gpt-4o-mini` (→ glm-4.5-air), `o3-mini` (→ glm-5.1). Raw GLM names won't pass validation. See `references/zai-endpoint-discovery.md` for full endpoint map.
- **Simple path-rewriting proxies may not work with Claude Code's Bun binary** — A Node.js reverse proxy that only rewrites paths (e.g. `/v1/models` → `/models`) works with curl but Claude Code's compiled Bun binary may not hit it. The Anthropic→OpenAI translation proxy (`scripts/zai-anthropic-proxy.js`) DOES work — the difference is it translates the full API format (Anthropic Messages → OpenAI Chat Completions), not just paths.

### Proxy Provider Setup (Non-Anthropic Backends)

Full Z.AI endpoint discovery, key types, model slugs, and working configs: `references/zai-endpoint-discovery.md`.
Anthropic→OpenAI translation proxy (for keys that only work on OpenAI endpoint): `scripts/zai-anthropic-proxy.js`.
General proxy debugging flow: `references/claude-code-proxy-provider-setup.md`.

**Quick summary for Z.AI:**
1. Base URL: `https://api.z.ai/api` (model validation lands on `/api/v1/models`)
2. Model slugs: `gpt-4o` (→ glm-5.1), `gpt-4o-mini` (→ glm-4.5-air)
3. If key returns 403 on `/api/v1/messages` but works on `/api/coding/paas/v4/chat/completions`, run the proxy: `ANTHROPIC_API_KEY=<key> node scripts/zai-anthropic-proxy.js` and set `ANTHROPIC_BASE_URL=http://127.0.0.1:18765`

### Pre-Flight Check (MANDATORY before every invocation)

**Check 1: Auth Status**
```
terminal(command="claude auth status --text 2>&1", timeout=10)
```

**Check 2: API Smoke Test (catches Pro-vs-API mismatch)**
```
terminal(command="claude -p 'Say OK' --max-turns 1 --output-format json 2>&1 | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get(\"subtype\",\"UNKNOWN\"))'", timeout=30)
```

If not logged in: tell the user to run `claude auth login --console`. Do NOT attempt to pipe `ANTHROPIC_API_KEY` yourself — this requires interactive TTY confirmation.

### Fallback: Hermes subagent via delegate_task

If Claude Code is unavailable, use Hermes's own `delegate_task` as a fallback code reviewer.

---

## Codex CLI

Delegate coding tasks to [Codex](https://github.com/openai/codex) via the Hermes terminal. Codex is OpenAI's autonomous coding agent CLI.

### Prerequisites

- **Install:** `npm install -g @openai/codex`
- **Auth:** Either `OPENAI_API_KEY` or Codex OAuth credentials from the Codex CLI login flow
- **Must run inside a git repository** — Codex refuses to run outside one
- **Use `pty=true`** in terminal calls — Codex is an interactive terminal app

### One-Shot Tasks

```
terminal(command="codex exec 'Add dark mode toggle to settings'", workdir="~/project", pty=true)
```

For scratch work (Codex needs a git repo):
```
terminal(command="cd $(mktemp -d) && git init && codex exec 'Build a snake game in Python'", pty=true)
```

### Background Mode (Long Tasks)

```
terminal(command="codex exec --full-auto 'Refactor the auth module'", workdir="~/project", background=true, pty=true)

# Monitor progress
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")

# Send input if Codex asks a question
process(action="submit", session_id="<id>", data="yes")
```

### Key Flags

| Flag | Effect |
|------|--------|
| `exec "prompt"` | One-shot execution, exits when done |
| `--full-auto` | Sandboxed but auto-approves file changes in workspace |
| `--yolo` | No sandbox, no approvals (fastest, most dangerous) |
| `--sandbox danger-full-access` | No Codex sandbox; useful when the host service context breaks bubblewrap |

### PR Reviews

Clone to a temp directory for safe review:
```
terminal(command="REVIEW=$(mktemp -d) && git clone https://github.com/user/repo.git $REVIEW && cd $REVIEW && gh pr checkout 42 && codex review --base origin/main", pty=true)
```

### Parallel Issue Fixing with Worktrees

```
terminal(command="git worktree add -b fix/issue-78 /tmp/issue-78 main", workdir="~/project")
terminal(command="codex --yolo exec 'Fix issue #78: <description>. Commit when done.'", workdir="/tmp/issue-78", background=true, pty=true)
```

### Pitfalls (Codex)

1. **Always use `pty=true`** — Codex is an interactive terminal app and hangs without a PTY
2. **Git repo required** — Codex won't run outside a git directory. Use `mktemp -d && git init` for scratch
3. **`--full-auto` for building** — auto-approves changes within the sandbox
4. **Hermes gateway caveat** — In gateway/service context, Codex `workspace-write` sandboxing may fail (bubblewrap/user-namespace errors). Prefer `--sandbox danger-full-access` in that context.

---

## OpenCode CLI

Use [OpenCode](https://opencode.ai) as an autonomous coding worker orchestrated by Hermes terminal/process tools. OpenCode is a provider-agnostic, open-source AI coding agent with a TUI and CLI.

### Prerequisites

- **Install:** `npm i -g opencode-ai@latest` or `brew install anomalyco/tap/opencode`
- **Auth:** `opencode auth login` or set provider env vars (OPENROUTER_API_KEY, etc.)
- **Verify:** `opencode auth list` should show at least one provider
- **`pty=true`** for interactive TUI sessions

### One-Shot Tasks

Use `opencode run` for bounded, non-interactive tasks:

```
terminal(command="opencode run 'Add retry logic to API calls and update tests'", workdir="~/project")
```

Attach context files with `-f`:
```
terminal(command="opencode run 'Review this config for security issues' -f config.yaml -f .env.example", workdir="~/project")
```

Force a specific model:
```
terminal(command="opencode run 'Refactor auth module' --model openrouter/anthropic/claude-sonnet-4", workdir="~/project")
```

### Interactive Sessions (Background)

```
terminal(command="opencode", workdir="~/project", background=true, pty=true)

# Send a prompt
process(action="submit", session_id="<id>", data="Implement OAuth refresh flow and add tests")

# Monitor progress
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")

# Exit cleanly — Ctrl+C
process(action="write", session_id="<id>", data="\x03")
```

**Important:** Do NOT use `/exit` — it is not a valid OpenCode command and will open an agent selector dialog instead. Use Ctrl+C (`\x03`) or `process(action="kill")` to exit.

### Common Flags

| Flag | Use |
|------|-----|
| `run 'prompt'` | One-shot execution and exit |
| `--continue` / `-c` | Continue the last OpenCode session |
| `--model provider/model` | Force specific model |
| `--thinking` | Show model thinking blocks |
| `--file <path>` / `-f` | Attach file(s) to the message |

### PR Review

OpenCode has a built-in PR command:
```
terminal(command="opencode pr 42", workdir="~/project", pty=true)
```

### Pitfalls (OpenCode)

1. **Interactive `opencode` (TUI) sessions require `pty=true`.** The `opencode run` command does NOT need pty.
2. **`/exit` is NOT a valid command** — it opens an agent selector. Use Ctrl+C to exit the TUI.
3. **PATH mismatch can select the wrong OpenCode binary/model config.**
4. **Enter may need to be pressed twice** to submit in the TUI (once to finalize text, once to send).

---

## Merging Multiple Agent Reviews (Git Stash Pattern)

When multiple agents produce overlapping diffs, merge them with git stash:

```bash
# Stash current work (Agent A's changes)
git stash

# Run Agent B on clean base
claude -p "audit..." ...

# Check what Agent B did
git diff --stat

# Save Agent B's work to a stash
git stash       # stash@{0} = Agent B, stash@{1} = Agent A

# Apply Agent A first
git stash pop stash@{1}

# Cherry-pick non-overlapping improvements from Agent B
```

---

## Rules for Hermes Agents

1. **Prefer one-shot mode for single tasks** — cleaner, no dialog handling, structured output
2. **Use tmux/background for multi-turn interactive work** — the only reliable way to orchestrate TUIs
3. **Always set `workdir`** — keep the coding agent focused on the right project directory
4. **Set iteration limits** — prevents infinite loops and runaway costs
5. **Monitor background sessions** — use `tmux capture-pane` or `process(action="poll")` to check progress
6. **Clean up sessions** — kill them when done to avoid resource leaks
7. **Report results to user** — after completion, summarize what the agent did and what changed
8. **Use capability restrictions** — limit to what the task actually needs
9. **Check prerequisites before every invocation** — wasted timeouts are worse than a quick check
