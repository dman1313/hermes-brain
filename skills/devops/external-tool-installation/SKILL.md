---
name: external-tool-installation
description: Install external tools and services from GitHub repos — AI agent toolkits, npm packages, Docker Compose stacks. Covers systemd headless wrapping, port conflict resolution, Caddy reverse proxy integration, and post-install polish.
version: 1.1.0
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
- `references/9router-vps-install.md` — VPS installation paths, systemd debugging journey, and `app/server.js` workaround (2026-05-16).
- `references/weknora-vps-install.md` — Docker Compose deployment: port conflicts, Caddy integration, container inventory, first-time setup notes (2026-05-16).

---

## Docker Compose Services

When a user provides a GitHub repo that deploys via Docker Compose:

### 1. Check prerequisites

```bash
docker --version && docker compose version 2>&1
```

If missing: `curl -fsSL https://get.docker.com | sudo sh` installs Docker Engine + Compose plugin.

### 2. Assess resources before pulling

```bash
df -h / && free -h && nproc
```

Docker Compose stacks with PostgreSQL + Redis + app server need ~2-4 GB RAM and ~5-10 GB disk. Pulling large images (100-700MB each) needs bandwidth and patience.

### 3. Clone and configure

```bash
git clone <repo> /tmp/<name>
cd /tmp/<name>
cp .env.example .env
```

**Port conflicts**: if `docker compose up -d` fails with "address already in use", find the offending port mappings in `docker-compose.yml` and override them in `.env`:

```bash
# docker-compose.yml uses ${APP_PORT:-8080}:8080
# Set in .env:
APP_PORT=8088   # shift away from conflict
```

Common conflict sources: Caddy, nginx, Cloudflare Tunnel on 80/443, other Docker stacks.

### 4. Start and verify

```bash
sudo docker compose up -d
sudo docker compose ps          # all "healthy"
curl -s http://localhost:<port>  # HTTP 200
```

### 5. Move to permanent location

```bash
mv /tmp/<name> /home/<user>/<name>
```

Compose `restart: unless-stopped` ensures containers survive reboots. The Docker daemon auto-starts via systemd, so no separate systemd unit needed.

### 6. Add Caddy reverse proxy

Add an IP-based entry (NOT domain-based unless you control port 443):

```
# /etc/caddy/Caddyfile
http://<public-ip>:<external-port> {
    reverse_proxy localhost:<internal-port>
}
```

**Why IP-based, not domain-based?** Domain entries (`example.com { ... }`) trigger Caddy's auto-HTTPS which binds port 443. If another process already owns 443 (Cloudflare Tunnel, nginx, another Caddy instance), the reload fails. IP-based entries on arbitrary ports avoid this.

```bash
sudo caddy validate --config /etc/caddy/Caddyfile
sudo systemctl reload caddy
```

### 7. Polish — don't stop at "it runs"

After the service is up, add value layers:
- **Reverse proxy** for external access
- **Pre-configure integrations** (LLM providers, IM channels, storage backends)
- **Enable optional profiles** (tracing, object storage, knowledge graphs)
- **Verify end-to-end** (dashboard loads, API responds, auth works)

The difference between "installed" and "production-ready" is these polish layers.

---

## npm Tools as Systemd Services

When a user wants an npm-installed tool running persistently:

### 1. Install globally

```bash
npm install -g <tool-name>
```

### 2. Don't trust the CLI wrapper for headless use

Many CLI tools (`9router`, `gptme`, etc.) wrap a server with an interactive TUI menu. This breaks in systemd (no TTY, stdin not connected). The CLI may:
- Hang waiting for input → systemd kills it after timeout
- Exit cleanly after setup → `Restart=on-failure` won't catch it
- Spawn the real server as a detached child → parent exits, child orphaned

### 3. Locate the actual server entry point

```bash
# Check package structure
ls node_modules/<tool>/app/
# Common patterns: server.js, dist/server.js, app/index.js, standalone/server.js
```

### 4. Write the systemd unit against the server, not the CLI

```ini
[Service]
Type=simple
User=<user>
Environment=NODE_ENV=production
Environment=PORT=<port>
Environment=PATH=/home/<user>/.local/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=/home/<user>/.local/bin/node /path/to/server.js
Restart=always        # NOT on-failure — server may exit cleanly
RestartSec=5
```

Key differences from the CLI wrapper approach:
- **`ExecStart`**: full path to `node` + full path to `server.js` (not the CLI binary, not `#!/usr/bin/env node`)
- **`Environment`**: set PORT, HOSTNAME, etc. directly (the CLI would have parsed `--port` and set these; replicate what it does)
- **`Restart=always`**: CLI wrappers often exit 0 after setup; `on-failure` won't restart them

### 5. Verify

```bash
sudo systemctl daemon-reload
sudo systemctl enable <service>
sudo systemctl start <service>
sleep 3
ss -tlnp | grep <port>
curl -s -o /dev/null -w "%{http_code}" http://localhost:<port>
```

### Example: 9Router

The CLI (`9router --no-browser`) spawns a detached child and enters an interactive menu. The actual server is a Next.js app at `node_modules/9router/app/server.js`. Systemd unit runs `server.js` directly with `PORT=20128 HOSTNAME=0.0.0.0`.

---

## Pitfalls

1. **pipx unavailable inside Hermes venv** — Hermes sessions run inside a virtualenv. `pipx` won't be on PATH. Fall back to `pip install` directly, or install pipx system-wide first.
2. **rdt-cli version pinning** — the Agent Reach guide says `>=0.4.2` but PyPI may only have up to 0.4.1. Use `>=0.4.0` instead.
3. **gh CLI not in apt** — on some Ubuntu versions, `gh` isn't in the default repos. Download the binary from GitHub releases.
4. **ffmpeg requires sudo** — only system package that needs elevation. Ask or use `sudo apt install -y ffmpeg`.
5. **Agent Reach install guide is AI-readable** — always fetch `docs/install.md` from the repo; it contains step-by-step instructions written for AI agents.
