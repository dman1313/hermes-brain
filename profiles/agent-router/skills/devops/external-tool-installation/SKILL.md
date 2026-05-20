---
name: external-tool-installation
description: Install external AI agent toolkits (Agent Reach, Get Shit Done, Skill Seekers) — follow each tool's install guide, fix broken deps, verify with doctor.
version: 1.0.0
author: Hermes
metadata:
  hermes:
    tags: [installation, tools, agent-reach, gsd, skill-seekers, devops]
---

# External Tool Installation

Install companion tools that extend an AI agent's internet access, meta-prompting, and skill-generation capabilities.

## When to Use

- User asks to install Agent Reach, Get Shit Done (GSD), Skill Seekers, or similar external agent toolkits
- User provides a GitHub repo URL for an agent-companion tool

## General Workflow

1. **Fetch repo info** — `curl` the GitHub API for name/description/language/topics
2. **Read install guide** — check README.md AND any `docs/install.md` for AI-agent-oriented instructions
3. **Check prerequisites** — verify Node.js, pipx, ffmpeg, etc. before installing
4. **Install** — follow the tool's canonical install method (pipx > venv pip > npm)
5. **Fix broken deps** — run the tool's doctor/check command, fix anything below ✅
6. **Verify** — final health check

---

## Agent Reach

Full internet access for AI agents (Twitter, Reddit, YouTube, GitHub, Bilibili, XiaoHongShu, etc.) — zero API fees.

### Install

```bash
# Preferred: pipx
pipx install https://github.com/Panniantong/agent-reach/archive/main.zip

# Fallback: venv (when pipx unavailable or in a virtualenv)
pip install https://github.com/Panniantong/agent-reach/archive/main.zip
```

### Core Channels

```bash
agent-reach install --env=auto
```

### Fix Common Issues

| Problem | Fix |
|---------|-----|
| `gh` not found | Download binary: `curl -fsSL https://github.com/cli/cli/releases/download/v2.76.0/gh_2.76.0_linux_amd64.tar.gz -o /tmp/gh.tar.gz && tar -xzf /tmp/gh.tar.gz -C /tmp && mkdir -p ~/.local/bin && cp /tmp/gh_*_linux_amd64/bin/gh ~/.local/bin/` |
| rdt-cli 0.4.2 not found | Install 0.4.1: `pip install 'rdt-cli>=0.4.0'` (0.4.2 wasn't on PyPI as of 2026-04-30) |
| ffmpeg missing | `sudo apt install -y ffmpeg` (Ubuntu/Debian) |
| `externally-managed-environment` | Use venv fallback, not `--break-system-packages` |

### Optional Channels

```bash
agent-reach install --env=auto --channels=all    # Everything
agent-reach install --env=auto --channels=twitter,weibo,xiaohongshu  # Specific
```

Supported channel names: `twitter`, `weibo`, `wechat`, `xiaoyuzhou`, `xueqiu`, `xiaohongshu`, `reddit`, `bilibili`, `douyin`, `linkedin`, `all`

### Verify

```bash
agent-reach doctor
```

Channels needing user credentials (can't be automated):
- Twitter/X — needs browser cookie
- XiaoHongShu — needs `xhs login` or cookie
- Xiaoyuzhou podcast — needs Groq API key (free at console.groq.com)
- Xueqiu — needs browser cookie
- Reddit — needs `rdt login` or cookie
- GitHub — needs `gh auth login`
- LinkedIn — needs `linkedin-scraper-mcp` + browser login
- Douyin — MCP server needs manual start

### Skill Output

Agent Reach auto-installs a skill at:
- Hermes: `~/.agents/skills/agent-reach`
- Claude Code: `~/.claude/skills/agent-reach`

---

## Get Shit Done (GSD)

Meta-prompting and spec-driven development for Claude Code, OpenCode, Gemini, Kilo, Codex, and others.

```bash
npx get-shit-done-cc@latest               # Interactive (pick runtimes)
npx get-shit-done-cc@latest --claude --global  # Non-interactive, Claude Code
```

Installs to `~/.claude/` (85 skills, hooks, agents, SDK). Verify with `/gsd-help` in Claude Code.

---

## Skill Seekers

Convert documentation sites, GitHub repos, and PDFs into Claude/Gemini/OpenAI skills.

```bash
pip install skill-seekers

# Usage
skill-seekers create <url|repo|pdf|dir>
skill-seekers package output/<name> --target claude
```

---

### Reference Files

- `references/agent-reach-channel-states.md` — exact channel statuses, install commands, and version pinning notes from the 2026-04-30 VPS install.

---

## Pitfalls

1. **pipx unavailable inside Hermes venv** — Hermes sessions run inside a virtualenv. `pipx` won't be on PATH. Fall back to `pip install` directly, or install pipx system-wide first.
2. **rdt-cli version pinning** — the Agent Reach guide says `>=0.4.2` but PyPI may only have up to 0.4.1. Use `>=0.4.0` instead.
3. **gh CLI not in apt** — on some Ubuntu versions, `gh` isn't in the default repos. Download the binary from GitHub releases.
4. **ffmpeg requires sudo** — only system package that needs elevation. Ask or use `sudo apt install -y ffmpeg`.
5. **Agent Reach install guide is AI-readable** — always fetch `docs/install.md` from the repo; it contains step-by-step instructions written for AI agents.
