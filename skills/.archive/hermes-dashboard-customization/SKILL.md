---
name: hermes-dashboard-customization
description: "Customize the Hermes native dashboard (port 9119) — YAML themes, custom CSS with real DOM selectors, kanban styling, auth proxy for public access, and plugin development."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [dashboard, theming, kanban, auth, css, cloudflare, plugins]
    related_skills: [hermes-agent, cloudflare-tunnel-setup]
---

# Hermes Dashboard Customization

Customize the native Hermes dashboard (v0.15+). Covers theming, kanban board styling, authentication, and plugins.

**Dashboard types:** There are THREE dashboards — don't confuse them:
| Dashboard | Port | Has Kanban? |
|-----------|------|-------------|
| Native Hermes Dashboard | 9119 | Yes |
| Hermes WebUI (Flask) | 8787 | No |
| Hermes Workspace (Next.js) | 3000 | No |

This skill covers the **native dashboard (9119)** only.

---

## 1. YAML Themes

User themes live at `~/.hermes/dashboard-themes/*.yaml`. Loaded on every API call — no restart needed for edits.

```bash
hermes config set dashboard.theme <name>
```

### Theme YAML Structure

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
  fontUrl: "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap"
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

### Key Pitfalls

- **midground** is the PRIMARY text/accent color. For light themes: set to near-black (#1a1816). For dark themes: set to cream (#ffe6cb).
- **colorOverrides** are REQUIRED for light themes — the `color-mix()` derivation produces inverted cards otherwise.
- User prefers: white bg (#ffffff, NOT cream), dark readable fonts (400-800 weight, no 300), 16px base, green only for accents.
- `customCSS` pseudo-elements work (`body::before` for grain, floating blobs).
- Themes are re-read on every API call — edit the YAML and refresh, no restart.

---

## 2. Kanban Board DOM Classes

Real class names discovered via DOM inspection. Use these for customCSS targeting.

**Full class list:** `references/kanban-dom-classes.md`

### Column Structure
```
.hermes-kanban-columns          — flex container for all columns
.hermes-kanban-column           — single column wrapper
.hermes-kanban-column-header    — header row (checkbox, dot, label, count, add button)
.hermes-kanban-column-label     — column name text
.hermes-kanban-column-count     — task count badge
.hermes-kanban-column-sub       — column description text
.hermes-kanban-column-body      — card container
.hermes-kanban-column-add       — "+" button
```

### Status Dots
```
.hermes-kanban-dot              — base dot (10x10px circle)
.hermes-kanban-dot-triage       — purple #9b7eb5
.hermes-kanban-dot-todo         — blue #7a9eb5
.hermes-kanban-dot-ready        — amber #d4a843
.hermes-kanban-dot-running      — green #3d7a4f (pulse animation)
.hermes-kanban-dot-blocked      — red #c47d7d
.hermes-kanban-dot-done         — sage #6b9e7a
```

### Card Structure
```
.hermes-kanban-card                     — card wrapper (button element)
.hermes-kanban-card--stale-amber        — overdue warning (amber left border)
.hermes-kanban-card--stale-red          — very overdue (red left border)
.hermes-kanban-card-content             — inner content div
.hermes-kanban-card-row                 — horizontal row
.hermes-kanban-card-check-wrap          — bulk select checkbox
.hermes-kanban-card-id                  — task ID (e.g. t_1466032f)
.hermes-kanban-priority                 — priority badge (P1-P10)
.hermes-kanban-progress                 — progress ring (SVG circle)
.hermes-kanban-card-title               — task title text
.hermes-kanban-card-meta                — metadata row (assignee, deps, age)
.hermes-kanban-assignee                 — assignee badge (@coder, @reviewer)
.hermes-kanban-unassigned               — "unassigned" label
.hermes-kanban-count                    — dependency/comment count
.hermes-kanban-ago                      — age timestamp
.hermes-kanban-warning-badge            — warning indicator
.hermes-kanban-warning-badge--critical  — critical warning
.hermes-kanban-needs-assignee           — needs assignment indicator
```

### Other Elements
```
.hermes-kanban                          — top-level board container
.hermes-kanban-boardswitcher            — board selector + task count
.hermes-kanban-attention                — attention banner
.hermes-kanban-attention--critical      — critical attention
.kanban-empty                           — empty column state
.kanban-empty-icon                      — empty state icon
```

### Column Descriptions (what each stage means)
- **Triage:** Raw ideas — a specifier will flesh out the spec
- **Todo:** Waiting on dependencies or unassigned
- **Scheduled:** Waiting on a known time delay or scheduled follow-up
- **Ready:** Dependencies satisfied; assign a profile to dispatch
- **In Progress:** Claimed by a worker — in-flight
- **Blocked:** Worker asked for human input
- **review:** (no description)
- **Done:** Completed

---

## 3. Auth Proxy for Public Dashboard

### The Problem

When exposing the dashboard via Cloudflare Tunnel:
- `--insecure` flag is needed (disables Host header check)
- `--insecure` also disables auth (`auth_required = False`)
- Caddy basic auth **loops** with SPAs — the browser sends credentials, Caddy proxies to dashboard, dashboard's own 401 on API calls triggers browser re-prompt

### The Solution: Cookie-Based Auth Proxy

A minimal Python proxy that:
1. Checks for a `hermes_token` cookie
2. If missing → serves a login page
3. If present → proxies to the dashboard

**Full implementation:** `references/dashboard-auth-proxy.md`

**Architecture:**
```
Cloudflare Tunnel → Auth Proxy (:9121) → Dashboard (:9119)
```

### Quick Setup

```bash
# Generate token
TOKEN=$(openssl rand -hex 32)

# Create proxy (see references/dashboard-auth-proxy.md for full script)
# Update Cloudflare tunnel config
sed -i 's|service: http://127.0.0.1:9119|service: http://127.0.0.1:9121|' ~/.cloudflared/config.yml

# Install as systemd service
sudo cp dashboard-auth-proxy.service /etc/systemd/system/
sudo systemctl enable --now dashboard-auth-proxy

# Restart tunnel
sudo systemctl restart cloudflared-proxy
```

### Pitfalls

- **Basic auth + SPA = loop.** Browser sends creds for initial page but not for XHR API calls. Dashboard returns 401 on API calls → browser re-prompts. Use cookie auth instead.
- **Dashboard must be running** for the proxy to work. Set up as systemd service.
- **Cookie is HttpOnly + SameSite=Strict.** Secure but means JavaScript can't read it.
- **Token is in the Python file.** Keep the script permissions restricted (chmod 600).

---

## 5. Theme Authoring Workflow

### Step 1: Inspect the Real DOM

Never guess CSS class names. Use `browser_console` to discover actual selectors:

```javascript
// Get all kanban-related class names
[...new Set(
  Array.from(document.querySelectorAll('*')).flatMap(el => 
    Array.from(el.classList).filter(c => c.includes('kanban'))
  )
)]
```

```javascript
// Get column structure
Array.from(document.querySelectorAll('.hermes-kanban-column')).map(col => ({
  label: col.querySelector('.hermes-kanban-column-label')?.textContent,
  count: col.querySelector('.hermes-kanban-column-count')?.textContent,
  dotClass: col.querySelector('.hermes-kanban-dot')?.className,
  desc: col.querySelector('.hermes-kanban-column-sub')?.textContent?.trim(),
  cardCount: col.querySelectorAll('.hermes-kanban-card').length
}))
```

### Step 2: Write Targeted CSS

Use the real class names from the kanban DOM reference.

### Step 3: Verify CSS Applied

```javascript
(() => {
  const col = document.querySelector('.hermes-kanban-column');
  const style = getComputedStyle(col);
  return { borderLeft: style.borderLeft, background: style.background?.substring(0, 50) };
})()
```

### Pitfalls

- **User themes reload on every API call** — no dashboard restart needed for YAML changes. Just refresh the browser.
- **`:nth-child()` for column borders** — columns don't have unique IDs. Use positional selectors for per-column styling.
- **Stale card classes:** `.hermes-kanban-card--stale-amber` and `.hermes-kanban-card--stale-red` are applied automatically by the kanban plugin based on task age.

## 6. Process Management & Troubleshooting

### Stale Processes

The #1 cause of "dashboard stopped working." Check and kill:

```bash
ps aux | grep "hermes dashboard" | grep -v grep
hermes dashboard --stop
hermes dashboard --port 9119 --host 0.0.0.0 --insecure --no-open &
```

### Port Conflicts

If `address already in use`:
```bash
lsof -ti :9119 | xargs kill -9
```

### Theme Not Appearing

1. Check `hermes config get dashboard.theme` — must match the YAML `name` field
2. User themes are in `~/.hermes/dashboard-themes/*.yaml`
3. Force rescan: `curl http://127.0.0.1:9119/api/dashboard/plugins/rescan`

### Caddy Basic Auth (Simple, but loops with SPAs)

**Warning:** Caddy basic auth causes login loops with SPAs. Use the cookie auth proxy (Section 3) instead. Documented here for non-SPA backends.

```bash
# Generate password hash
PASSWORD=$(openssl rand -base64 16 | tr -d '/+=' | head -c 16)
HASH=$(caddy hash-password --plaintext "$PASSWORD")

# Add to /etc/caddy/Caddyfile
# :9120 {
#     basic_auth { <username> <hash> }
#     reverse_proxy localhost:9119
# }

caddy validate --config /etc/caddy/Caddyfile
sudo systemctl reload caddy
```

**Pitfalls:**
- Caddy `basic_auth` block format: username and hash must be on the SAME line inside the block. A comment line above the hash causes a parse error.
- Dashboard must be running with `--insecure` because Caddy forwards the original Host header from Cloudflare.

## 7. Dashboard as Systemd Service

The dashboard dies on session close when run as a background process. Use systemd:

```bash
# Find the correct Python path
PYTHON=$(which python3)  # or use the hermes venv path

# Create service
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

### Pitfalls

- **Port conflicts:** If dashboard was already running as a background process, kill it first: `lsof -ti :9119 | xargs kill -9`
- **RestartSec backoff:** Systemd has 60s restart backoff. After `systemctl restart`, wait at least 60s before checking.
- **hermes dashboard --stop** kills ALL dashboard processes — use before switching between background and systemd modes.
