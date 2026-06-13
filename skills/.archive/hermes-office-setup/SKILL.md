---
name: hermes-office-setup
description: Install and configure Hermes Office (Claw3D) — the 3D workspace web dashboard for Hermes Agent. Clones hermes-office, sets up the Hermes adapter + Next.js dev server as systemd services, and exposes it via Cloudflare Tunnel.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, office, claw3d, dashboard, web-ui, installation, tunnel]
    category: devops
---

# Hermes Office (Claw3D) Setup

Install and configure Hermes Office (Claw3D) — an open-source 3D workspace web UI for Hermes Agent. Built by LukeTheDev (fathah/hermes-desktop and fathah/hermes-office). Provides a 3D retro-office where agents appear as workers, with chat, fleet management, code review, QA monitoring, and skill training gym.

**Repo:** https://github.com/fathah/hermes-office
**Desktop app:** https://github.com/fathah/hermes-desktop (Electron app — separate from this web dashboard)

## Triggers

- "install hermes office" / "install claw3d"
- "setup 3D dashboard" / "install hermes desktop dashboard"
- "install HD1" / "setup office dashboard"
- "hermes office dashboard on domain"

## Clarify First (mandatory)

When the user says "hermes dashboard," there are now **four** things that could mean. Ask which one unless context is unambiguous:

| Dashboard | Stack | Port | Source | Service |
|-----------|-------|------|--------|---------|
| **Hermes Office (Claw3D)** | Next.js 16 | 3001 | fathah/hermes-office | hermes-office |
| **Hermes Workspace** | Next.js | 3000 | outsourc-e/hermes-workspace | (manual) |
| **Native Hermes Dashboard** | FastAPI + SPA | 9119 | Built into Hermes Agent | hermes-dashboard |
| **Hermes WebUI** (legacy) | Flask | 8787 | nesquena/hermes-webui | (manual) |

If they say "the 3D one," "Claw3D," "HD1," or "the office," they mean Hermes Office (this skill).

## Prerequisites

- Node.js 20+ and npm 10+
- Hermes Agent already installed with gateway API running on port 8642
- Cloudflare Tunnel configured (for external access)

## Architecture

Claw3D has two components that must both run:

1. **Hermes Gateway Adapter** (`server/hermes-gateway-adapter.js`) — WebSocket bridge on port 18789 that translates between the Hermes HTTP API (8642) and the Claw3D WebSocket protocol
2. **Dev Server** (`server/index.js --dev`) — Next.js 16 app on the configured port that serves the 3D UI and proxies WebSocket connections to the adapter

```
Browser → Cloudflare Tunnel → Dev Server (3001) → Gateway Adapter (18789) → Hermes Gateway (8642)
```

## Installation

### Step 1: Clone and install dependencies

```bash
cd ~
git clone https://github.com/fathah/hermes-office.git
cd hermes-office
npm install
```

### Step 2: Create .env

Create `~/hermes-office/.env`:

```
NEXT_PUBLIC_GATEWAY_URL=ws://localhost:18789
CLAW3D_GATEWAY_URL=ws://localhost:18789
CLAW3D_GATEWAY_TOKEN=
CLAW3D_GATEWAY_ADAPTER_TYPE=hermes

HERMES_API_URL=http://localhost:8642
HERMES_API_KEY=
HERMES_ADAPTER_PORT=18789
HERMES_MODEL=hermes
HERMES_AGENT_NAME=Hermes

DEBUG=true

PORT=3001
HOST=127.0.0.1
```

### Step 3: Create systemd services

**Adapter service** (`/etc/systemd/system/hermes-office-adapter.service`):

```ini
[Unit]
Description=Hermes Office (Claw3D) Gateway Adapter
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/hermes-office
Environment=HERMES_API_URL=http://localhost:8642
Environment=HERMES_ADAPTER_PORT=18789
ExecStart=/home/ubuntu/.local/bin/node server/hermes-gateway-adapter.js
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Dev server service** (`/etc/systemd/system/hermes-office.service`):

```ini
[Unit]
Description=Hermes Office (Claw3D) Dev Server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/hermes-office
Environment=PORT=3001
Environment=HOST=127.0.0.1
ExecStart=/home/ubuntu/.local/bin/node server/index.js --dev
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable hermes-office-adapter hermes-office
sudo systemctl start hermes-office-adapter
sleep 2
sudo systemctl start hermes-office
```

### Step 4: Cloudflare Tunnel ingress

Add to `~/.cloudflared/config.yml`:

```yaml
  - hostname: hd1.humangood.ai
    service: http://127.0.0.1:3001
```

Restart tunnel:

```bash
sudo systemctl restart hermes-tunnel
```

### Step 5: DNS CNAME record

Create in Cloudflare Dashboard:

| Type | Name | Target | Proxy |
|------|------|--------|-------|
| CNAME | hd1 | f6fdf864-d25d-4be9-b5ef-ff9ac3c21b88.cfargotunnel.com | Proxied (orange) |

The tunnel ID comes from `grep tunnel ~/.cloudflared/config.yml`.

## Pitfalls

1. **PORT in .env is not picked up by the dev server:** The custom server (`server/index.js`) calls `resolvePort()` which reads `process.env.PORT` before Next.js loads `.env`. You MUST pass `Environment=PORT=3001` in the systemd service or `PORT=3001` on the command line. Do not rely on `.env` for PORT. If you omit this, the server silently binds to port 3000 regardless of what `.env` says — `ss -tlnp | grep 3000` confirms it, and the "Open in browser: http://localhost:3000" startup message is the giveaway.

2. **HOST must be set to 127.0.0.1 for security:** Without `HOST=127.0.0.1` (or `Environment=HOST=127.0.0.1`), Next.js binds to `0.0.0.0` and the dashboard is exposed directly on the network. Always bind to localhost when using Cloudflare Tunnel.

3. **Next.js workspace root warning:** If `/home/ubuntu/package.json` or `/home/ubuntu/package-lock.json` exist, Next.js detects them as a parent workspace and emits: `"Warning: Next.js inferred your workspace root, but it may not be correct. We detected multiple lockfiles..."` Remove stale root-level lockfiles with `rm ~/package.json ~/package-lock.json` to silence this.

4. **Both adapter AND dev server must run:** The adapter bridges Hermes HTTP API ↔ WebSocket. Without it, the dev server starts but shows a gateway connection form instead of the office. The adapter auto-reads `.env` for `HERMES_API_URL` and `HERMES_ADAPTER_PORT`. Start the adapter FIRST, wait 2s, then start the dev server — the dev server connects to the adapter on startup.

5. **First page load is slow:** Next.js dev server compiles on first request. The `/office` route with Three.js and Phaser takes 10-30 seconds on first hit. Subsequent loads are fast. The root path `/` redirects to `/office` (307). `curl -sI http://127.0.0.1:3001` confirms the redirect is working.

6. **Background processes vs systemd:** Starting with `terminal(background=true)` works for testing but processes die when the session ends. Always create systemd services for production use. The migration steps: kill the ephemeral processes (`sudo kill <pid>`), create the service files, `daemon-reload`, `enable`, `start`. Verify with `ss -tlnp | grep -E "18789|3001"`.

7. **hermes-desktop ≠ hermes-office:** The user may say "install hermes-desktop" meaning the Electron desktop app. Clarify: the Electron app can't run on a headless VPS, but the web dashboard component (hermes-office/Claw3D) CAN. Point them to this skill instead. The hermes-desktop repo's claw3d.ts module is what auto-clones and manages hermes-office — the end result is the same web dashboard.

8. **Hermes Gateway must be running and healthy:** Verify with `curl -s http://127.0.0.1:8642/health` before starting the adapter. Expected response: `{"status":"ok","platform":"hermes-agent"}`. If the gateway is down, the adapter still starts but Claw3D shows connection errors.

9. **Adapter port conflict with OpenClaw:** The default adapter port 18789 may conflict with an OpenClaw gateway instance (which also uses 18789). If both are installed, change `HERMES_ADAPTER_PORT` to a different port (e.g., 18790) in both the .env and systemd service files, and update `NEXT_PUBLIC_GATEWAY_URL` and `CLAW3D_GATEWAY_URL` in .env accordingly.

10. **DNS CNAME is the manual bottleneck:** Adding the tunnel ingress and restarting the tunnel is automated. But the DNS CNAME record requires Cloudflare Dashboard access (no API token available). Without the CNAME, the hostname won't resolve. The record needed: `CNAME hd1 → <tunnel-id>.cfargotunnel.com` (proxied/orange cloud). The tunnel ID is in `~/.cloudflared/config.yml` under `tunnel:`.

## Verification

```bash
# Adapter health
curl -s http://127.0.0.1:18789
# → "Hermes Gateway Adapter – OK"

# Dev server responds
curl -sI http://127.0.0.1:3001 | head -1
# → HTTP/1.1 307 Temporary Redirect

# Gateway healthy
curl -s http://127.0.0.1:8642/health
# → {"status":"ok","platform":"hermes-agent"}

# Both services running
sudo systemctl status hermes-office-adapter --no-pager | head -3
sudo systemctl status hermes-office --no-pager | head -3
```

## Troubleshooting

**Office loads but shows connection form instead of 3D scene:**
The adapter isn't running or isn't reachable. Check `sudo systemctl status hermes-office-adapter` and `curl http://127.0.0.1:18789`.

**hd1.humangood.ai returns 502:**
Dev server isn't running. Check `sudo systemctl status hermes-office` and `ss -tlnp | grep 3001`.

**hd1.humangood.ai doesn't resolve:**
DNS CNAME record hasn't been created yet. This is a manual step — the Cloudflare API token isn't available for automated creation.

**Page loads but shows error overlay:**
Check the adapter can reach the gateway: `curl http://127.0.0.1:8642/health`. If the gateway is down, restart it: `hermes gateway restart`.
