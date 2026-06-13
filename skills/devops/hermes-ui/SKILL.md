---
name: hermes-ui
description: "Hermes web UI interfaces — native dashboard theming/plugins and Hermes Office (Claw3D) 3D workspace. Covers YAML themes, kanban CSS, auth proxies, systemd services, and Cloudflare Tunnel exposure."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [dashboard, theming, kanban, claw3d, office, web-ui, plugins, cloudflare]
    related_skills: [hermes-agent, cloudflare-tunnel-setup]
---

# Hermes Web UIs

Hermes has multiple web interfaces. This skill covers the **native dashboard (port 9119)** and **Hermes Office / Claw3D (port 3001)**.

**Don't confuse them:**

| Dashboard | Stack | Port | What it is | Has Kanban? |
|-----------|-------|------|------------|-------------|
| **Native Hermes Dashboard** | FastAPI + SPA | 9119 | Built into Hermes Agent | Yes |
| **Hermes Office (Claw3D)** | Next.js 16 | 3001 | 3D workspace with agent workers | No |
| **Hermes Workspace** | Next.js | 3000 | Chat + conductor + terminal | No |
| **Hermes WebUI** (legacy) | Flask | 8787 | Older Flask-based UI | No |

---

## Part 1: Native Dashboard (Port 9119)

Customize the native Hermes dashboard — YAML themes, kanban board styling, authentication, and plugins.

### YAML Themes

User themes live at `~/.hermes/dashboard-themes/*.yaml`. Loaded on every API call — no restart needed for edits.

```bash
hermes config set dashboard.theme <name>
```

#### Theme YAML Structure

```yaml
name: my-theme
label: My Theme
description: What it does

palette:
  background: {hex: "#ffffff", alpha: 1.0}
  midground:  {hex: "#1a1816", alpha: 1.0}   # primary text/accent
  foreground: {hex: "#ffffff", alpha: 0.0}    # highlights
  warmGlow: "rgba(193,127,89,0.12)"
  noiseOpacity: 0.15

typography:
  fontSans: '"Inter", system-ui, sans-serif'
  fontMono: '"JetBrains Mono", ui-monospace, monospace'
  fontUrl: "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap"
  baseSize: "15px"
  lineHeight: "1.55"
  letterSpacing: "0"

layout:
  radius: "0.75rem"
  density: comfortable

colorOverrides:
  primary: "#3d7a4f"
  primaryForeground: "#ffffff"
  card: "#ffffff"
  cardForeground: "#1a1816"
  border: "#e2ddd5"
  ring: "#3d7a4f"
  # ... all shadcn tokens

componentStyles:
  card: {boxShadow: "0 1px 3px rgba(0,0,0,0.06)"}
  header: {background: "rgba(255,255,255,0.85)", backdropFilter: "blur(20px)"}
  sidebar: {background: "rgba(255,255,255,0.9)", backdropFilter: "blur(16px)"}

customCSS: |
  /* Your CSS here — max 32KB */
```

#### Key Theme Pitfalls

- **midground** is the PRIMARY text/accent color. For light themes: set to near-black (#1a1816). For dark themes: set to cream (#ffe6cb).
- **colorOverrides** are REQUIRED for light themes — the `color-mix()` derivation produces inverted cards otherwise.
- User prefers: white bg (#ffffff, NOT cream), dark readable fonts (400-800 weight, no 300), 16px base, green only for accents.
- `customCSS` pseudo-elements work (`body::before` for grain, floating blobs).
- Themes are re-read on every API call — edit the YAML and refresh, no restart.

### Kanban Board DOM Classes

Real class names discovered via DOM inspection. Use these for customCSS targeting.

**Column Structure:**
```
.hermes-kanban-columns          — flex container for all columns
.hermes-kanban-column           — single column wrapper
.hermes-kanban-column-header    — header row
.hermes-kanban-column-label     — column name text
.hermes-kanban-column-count     — task count badge
.hermes-kanban-column-body      — card container
```

**Status Dots:**
```
.hermes-kanban-dot-triage       — purple #9b7eb5
.hermes-kanban-dot-todo         — blue #7a9eb5
.hermes-kanban-dot-ready        — amber #d4a843
.hermes-kanban-dot-running      — green #3d7a4f (pulse animation)
.hermes-kanban-dot-blocked      — red #c47d7d
.hermes-kanban-dot-done         — sage #6b9e7a
```

**Card Structure:**
```
.hermes-kanban-card                     — card wrapper
.hermes-kanban-card--stale-amber        — overdue warning
.hermes-kanban-card--stale-red          — very overdue
.hermes-kanban-card-title               — task title text
.hermes-kanban-assignee                 — assignee badge
.hermes-kanban-priority                 — priority badge (P1-P10)
```

**Full class list:** `references/kanban-dom-classes.md` (under hermes-dashboard-customization archive)

### Auth Proxy for Public Dashboard

When exposing via Cloudflare Tunnel, `--insecure` disables auth. Caddy basic auth loops with SPAs. Use a cookie-based auth proxy instead.

**Architecture:** `Cloudflare Tunnel → Auth Proxy (:9121) → Dashboard (:9119)`

A minimal Python proxy that checks for a `hermes_token` cookie, serves a login page if missing, and proxies to the dashboard if present.

**Full implementation:** `references/dashboard-auth-proxy.md` (under hermes-dashboard-customization archive)

### Dashboard as Systemd Service

```bash
sudo tee /etc/systemd/system/hermes-dashboard.service > /dev/null << 'EOF'
[Unit]
Description=Hermes Dashboard
After=network.target

[Service]
Type=simple
ExecStart=/path/to/python -m hermes_cli.web_server --port 9119 --host 0.0.0.0 --insecure --no-open
Restart=always
RestartSec=5
Environment=HERMES_HOME=/home/ubuntu/.hermes

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now hermes-dashboard
```

### Dashboard Troubleshooting

- **Stale processes** — the #1 culprit. `hermes dashboard --stop` then restart.
- **Port conflicts** — `lsof -ti :9119 | xargs kill -9`
- **Theme not appearing** — check `hermes config get dashboard.theme` matches the YAML `name` field.
- **502 behind Cloudflare Tunnel** — dashboard process died. Check `ps aux | grep "hermes dashboard"`.
- **"Invalid Host header"** — use `--insecure` flag when behind a reverse proxy.

---

## Part 2: Hermes Office / Claw3D (Port 3001)

Install and configure Hermes Office — an open-source 3D workspace web UI where agents appear as workers in a retro office.

**Repo:** https://github.com/fathah/hermes-office

### Architecture

Claw3D has two components:

1. **Hermes Gateway Adapter** (`server/hermes-gateway-adapter.js`) — WebSocket bridge on port 18789
2. **Dev Server** (`server/index.js --dev`) — Next.js 16 app on port 3001

```
Browser → Cloudflare Tunnel → Dev Server (3001) → Gateway Adapter (18789) → Hermes Gateway (8642)
```

### Installation

**Step 1: Clone and install**
```bash
cd ~
git clone https://github.com/fathah/hermes-office.git
cd hermes-office
npm install
```

**Step 2: Create .env**
```
NEXT_PUBLIC_GATEWAY_URL=ws://localhost:18789
CLAW3D_GATEWAY_URL=ws://localhost:18789
CLAW3D_GATEWAY_ADAPTER_TYPE=hermes
HERMES_API_URL=http://localhost:8642
HERMES_ADAPTER_PORT=18789
PORT=3001
HOST=127.0.0.1
```

**Step 3: Create systemd services**

Adapter service (`/etc/systemd/system/hermes-office-adapter.service`):
```ini
[Unit]
Description=Hermes Office Gateway Adapter
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

[Install]
WantedBy=multi-user.target
```

Dev server service (`/etc/systemd/system/hermes-office.service`):
```ini
[Unit]
Description=Hermes Office Dev Server
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

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable hermes-office-adapter hermes-office
sudo systemctl start hermes-office-adapter
sleep 2
sudo systemctl start hermes-office
```

**Step 4: Cloudflare Tunnel ingress**
```yaml
# In ~/.cloudflared/config.yml ingress section:
  - hostname: hd1.humangood.ai
    service: http://127.0.0.1:3001
```

**Step 5: DNS CNAME record** (manual — Cloudflare Dashboard)
`CNAME hd1 → <tunnel-id>.cfargotunnel.com` (proxied/orange cloud)

### Claw3D Pitfalls

1. **PORT in .env is not picked up by the dev server.** You MUST pass `Environment=PORT=3001` in the systemd service. The custom server reads `process.env.PORT` before Next.js loads `.env`.
2. **HOST must be 127.0.0.1 for security.** Without it, Next.js binds to `0.0.0.0`.
3. **Both adapter AND dev server must run.** Start adapter first, wait 2s, then dev server.
4. **First page load is slow.** Next.js dev server compiles on first request. 10-30 seconds on first hit.
5. **Adapter port conflict with OpenClaw.** Default port 18789 may conflict. Change `HERMES_ADAPTER_PORT` if both are installed.
6. **hermes-desktop ≠ hermes-office.** The Electron app can't run on a headless VPS, but the web dashboard (hermes-office) CAN.

### Claw3D Verification

```bash
curl -s http://127.0.0.1:18789          # → "Hermes Gateway Adapter – OK"
curl -sI http://127.0.0.1:3001 | head -1  # → HTTP/1.1 307 Temporary Redirect
curl -s http://127.0.0.1:8642/health     # → {"status":"ok","platform":"hermes-agent"}
sudo systemctl status hermes-office-adapter --no-pager | head -3
sudo systemctl status hermes-office --no-pager | head -3
```
