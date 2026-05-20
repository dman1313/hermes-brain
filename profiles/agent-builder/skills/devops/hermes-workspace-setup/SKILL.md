---
name: hermes-workspace-setup
description: Install and configure the Hermes Workspace web UI (Next.js dashboard) for Hermes Agent — chat, conductor, memory, terminal, and settings in one interface.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, workspace, web-ui, dashboard, installation, tunnel]
    category: devops
---

# Hermes Workspace Setup

Install and configure the Hermes Workspace — an open-source web UI for Hermes Agent (Next.js app by outsourc-e). Provides chat, mission conductor, memory browser, integrated terminal, and settings in one interface.

**Repo:** https://github.com/outsourc-e/hermes-workspace
**Landing:** https://hermes-workspace.com

## Triggers

- "install hermes workspace" / "install workspace UI"
- "remove hermes workspace" / "remove workspace dashboard" / "uninstall workspace"
- "setup workspace dashboard"
- "hermes-workspace.com"

## Prerequisites

- Node 22+, Python 3.11+, pnpm
- Hermes Agent already installed (`hermes` on PATH)
- The workspace UI requires the Hermes gateway HTTP API (port 8642)

## Installation

### Step 1: One-liner install

```bash
curl -fsSL https://hermes-workspace.com/install.sh | bash
```

This detects prerequisites, installs hermes-agent if missing (via Nous upstream installer), clones `~/hermes-workspace`, creates `.env`, runs `pnpm install`, and links bundled skills into `~/.hermes/skills/`. Re-runnable — skips anything already done.

### Step 2: Enable the gateway HTTP API (CRITICAL)

The workspace communicates with Hermes Agent through its WebAPI on port 8642. This is **opt-in** and off by default. Add to `~/.hermes/.env`:

```
API_SERVER_ENABLED=true
```

Without this, the workspace will start but cannot reach the agent — you'll get connection errors in the browser UI.

### Step 3: Restart the gateway

The gateway must restart to pick up `API_SERVER_ENABLED`:

```bash
hermes gateway restart
```

This triggers a systemd user-service restart. Verify the API is up:

```bash
curl -s http://127.0.0.1:8642/health
# → {"status": "ok", "platform": "hermes-agent"}
```

### Step 4: Start the workspace UI

```bash
cd ~/hermes-workspace && pnpm dev
```

Runs on port 3000 by default in dev mode (Vite ignores `PORT=3002` in `.env`). Verify the actual port:

```bash
ss -tlnp | grep node | grep -E "300[0-9]"
# Should show LISTEN on 0.0.0.0:3000
```

Open `http://localhost:3000`. The production build (`pnpm start`) does respect the PORT env var.

### Optional: Expose via Cloudflare Tunnel

Add to `~/.cloudflared/config.yml` ingress rules:

```yaml
  - hostname: workspace.humangood.ai
    service: http://127.0.0.1:3000
```

Create the DNS CNAME record pointing to the tunnel (see `cloudflare-tunnel-setup` skill), then restart: `sudo systemctl restart hermes-tunnel`.

## Updating an Existing Workspace

When the workspace shows "23 commits behind" or similar, update manually (the install script only handles fresh installs):

```bash
cd ~/hermes-workspace

# Stash any local patches (e.g. onboarding fix, message-item tweaks)
git stash push -m "pre-update-local-fixes-$(date +%Y%m%d)"

# Pull latest
git pull origin main

# Reapply local patches — expect conflicts if upstream touched same files
git stash pop
# → CONFLICT in src/routes/__root.tsx, src/screens/chat/components/message-item.tsx

# If conflicts: inspect both sides, usually upstream is correct
git checkout --theirs <conflicted-file>
git add <conflicted-file>

# Drop the stash after resolution
git stash drop

# Install any new dependencies (Electron, framer-motion, etc.)
pnpm install

# Kill old process and restart
pkill -f "pnpm dev" 2>/dev/null
# Then restart (background task or separate terminal):
cd ~/hermes-workspace && pnpm dev
```

After restart, verify: `curl -s http://127.0.0.1:3000 | grep -o '<title>[^<]*</title>'` should return `Hermes Workspace`.

### Hermes Agent Itself

Separate from the workspace UI — update Hermes Agent core:
```bash
hermes update
```
This pulls the latest commits, updates Python/Node deps, syncs bundled skills, checks config for new options, and restarts the gateway. The workspace UI must also be restarted afterward since the backend API may have changed.

## Pitfalls

1. **Workspace connects but shows errors / "agent unreachable":** `API_SERVER_ENABLED=true` is missing from `~/.hermes/.env` or the gateway wasn't restarted after adding it. The workspace `.env.example` warns about this but it's easy to miss.

2. **Gateway crashes on restart with model routing errors:** If the gateway has in-flight conversations when signalled to restart, it tries to finish them. Model routing errors (wrong model names for the provider, unsupported `developer` role) can cause crash loops. These are pre-existing conversation issues, not caused by the restart itself. The gateway will recover after the systemd backoff period (RestartSec=60).

3. **`pnpm dev` port conflict:** Default port is 3000. If another service uses it, set `PORT=3002` in `~/hermes-workspace/.env`. **However, Vite dev server ignores the PORT env var and binds to 3000 even when PORT=3002 is set in .env.** Always verify the actual bound port with `ss -tlnp | grep node` after starting — don't trust the .env alone.

4. **Replacing an existing web UI with the workspace:** If an older Hermes web UI (e.g., a Python Flask server on port 8787) is already running behind a Cloudflare Tunnel, the migration steps are:
   - Kill the old web UI process (`sudo kill <PID>`)
   - Start the new workspace (`cd ~/hermes-workspace && pnpm dev`)
   - Update CF tunnel ingress rules to point the relevant hostnames from old port → 3000
   - **Full restart** the cloudflared tunnel (`sudo pkill`, then restart) — SIGHUP does NOT reliably pick up ingress changes
   - Verify each hostname individually — some may return 200 while others return 404 due to Cloudflare edge caching or DNS propagation delays

5. **Port 3000 vs 3002 discrepancy:** The `.env.example` and install script default to `PORT=3002`, but the Vite dev server (`pnpm dev`) ignores this and binds to port 3000. The production build (`pnpm start` with the Node server) does respect the PORT variable. For dev mode, always assume port 3000 regardless of what the .env says.

6. **Missing `HermesOnboarding` component (pre-May 2026):** Older versions of the workspace failed with `Can't find variable: HermesOnboarding` on page load. This was an unfinished feature. **As of the May 2026 update (commit 6485d200+), the component was renamed to `ClaudeOnboarding` and is properly implemented.** If you're on a recent version, this pitfall no longer applies.

7. **Password may appear truncated in .env:** The `.env` file's `CLAUDE_PASSWORD` value may display with literal `...` dots in some tools. Use `xxd` or `sed -n 'Lp' file | xxd` to see the full raw bytes and confirm the password is complete vs actually truncated.

8. **Gateway port may drift from memory:** The Hermes gateway can auto-bind to a different port on restart (e.g., 8642 instead of 18789). Always discover the actual port with `ss -tlnp | grep python` — never trust a port from memory or config alone.

9. **Install script needs curl and bash:** On minimal systems, ensure both are available. The script detects and reports missing prerequisites before proceeding.

10. **h1.humangood.ai returns 502 or "not working":** The Hermes Workspace UI (Next.js on port 3000) may have stopped while the Cloudflare tunnel is still running. Diagnosis:
    ```bash
    # Check if Next.js is running
    ss -tlnp | grep 3000
    # If not running, start it
    cd ~/hermes-workspace && pnpm dev &
    # Verify
    curl -s -o /dev/null -w '%{http_code}' http://localhost:3000
    ```
    The Cloudflare tunnel routes `h1.humangood.ai` → `127.0.0.1:3000`. If port 3000 isn't listening, Cloudflare returns 502. This has been observed recurring (the dev server crashes or gets killed during updates). If the tunnel itself is down, check `ss -tlnp | grep cloudflared` and restart with `sudo systemctl restart hermes-tunnel`.

11. **Agent doesn't know what "h1" is:** If a user asks about "h1" or "h1 password", `h1.humangood.ai` is the Hermes Workspace UI. The password is `CLAUDE_PASSWORD` in `~/hermes-workspace/.env`. The agent should not ask "what is h1?" — it should check the workspace config directly.

## Pre-Declaration Checklist (MANDATORY)

Before telling the user "it's done" or "it's working," run EVERY check below. The user expects thorough verification — not optimistic declarations. A single 200 doesn't mean the system works. Check:

1. Local page loads (HTML > 5KB, no Vite error overlay)
2. External page loads via tunnel (same domain)
3. Login API works (POST /api/auth → `{"ok":true}` + session cookie)
4. Auth-check endpoint confirms session (`{"authenticated":true}`)
5. Gateway health (`/health` → `{"status":"ok"}`)
6. Each CF tunnel hostname responds individually (not just one — some may 404 while others work)

Only report success after all checks pass. If ANY check fails, report what failed and fix it before re-verifying.

## Removal / Uninstall

1. **Kill the dev server process** — find the PID bound to port 3000 and kill it:

   ```bash
   kill $(ss -tlnp | grep :3000 | grep -oP 'pid=\K[0-9]+') 2>/dev/null
   ss -tlnp | grep 3000 || echo "Port 3000 cleared"
   ```

2. **Remove the workspace directory:**

   ```bash
   rm -rf ~/hermes-workspace
   ```

3. **Clean up Cloudflare tunnel ingress** — remove hostname entries that point to port 3000 from `~/.cloudflared/config.yml`, then restart:

   ```bash
   sudo systemctl restart hermes-tunnel
   ```

4. **Remove systemd service** (if one was created):

   ```bash
   sudo systemctl stop hermes-workspace 2>/dev/null
   sudo systemctl disable hermes-workspace 2>/dev/null
   sudo rm /etc/systemd/system/hermes-workspace.service 2>/dev/null
   sudo systemctl daemon-reload
   ```

5. **DNS CNAME cleanup** — the subdomains (hermes, h1, workspace on humangood.ai) still have DNS records in Cloudflare. These return 404 after tunnel ingress is removed and are harmless, but delete them manually in the Cloudflare dashboard to keep DNS tidy.

### Pitfall: four different "Hermes dashboards" — always clarify

When the user says "Hermes dashboard," "Hermes web UI," or "the dashboard," there are **four** different things this could mean. Do NOT guess — ask which one unless the context is already unambiguous:

| Dashboard | Stack | Port | Source | Command |
|-----------|-------|------|--------|---------|
| **Hermes Workspace** (this skill) | Next.js | 3000 (dev) | outsourc-e/hermes-workspace | `pnpm dev` in `~/hermes-workspace` |
| **Hermes Office (Claw3D)** | Next.js 16 | 3001 | fathah/hermes-office | `node server/index.js --dev` in `~/hermes-office` |
| **Native Hermes Dashboard** | FastAPI + SPA | 9119 (default) | Built into Hermes Agent | `hermes dashboard --port 9119` |
| **Hermes WebUI** (legacy) | Flask | 8787 | nesquena/hermes-webui | `python server.py` |

If the user says "the 3D one," "Claw3D," "HD1," or "the office," they mean Hermes Office. If they say "the native one" or "the one that ships with Hermes," they mean the FastAPI dashboard. If they say "the Workspace" or "H1" or "the Next.js one," they mean this Workspace UI. If it's unclear, ask.
If the user says "the native one" or "the one that ships with Hermes," they mean the FastAPI dashboard. If they say "the Workspace" or "H1" or "the Next.js one," they mean this Workspace UI. If they say "Claw3D," "the 3D one," "HD1," or "the office," they mean Hermes Office — see the `hermes-office-setup` skill. If it's unclear, ask: *"Which dashboard do you mean — the native Hermes one (built-in, FastAPI), the Workspace UI (Next.js, at h1.humangood.ai), Hermes Office/Claw3D (3D, at hd1.humangood.ai), or the legacy WebUI?"*

### Pitfall: confusing Hermes Workspace with other Hermes dashboards

When the user says "remove hermes dashboard," clarify which one. The system may have up to four dashboards:
- **Hermes Workspace** (Next.js, `~/hermes-workspace/`, port 3000) — the modern UI from `outsourc-e/hermes-workspace`
- **Hermes Office / Claw3D** (Next.js 16, `~/hermes-office/`, port 3001) — the 3D office from `fathah/hermes-office`
- **Hermes WebUI** (Flask, port 8787) — the legacy Flask UI from `nesquena/hermes-webui`
- **Native Hermes Dashboard** (FastAPI, port 9119) — built into Hermes Agent

Ask explicitly before removing. The tunnel config may route different hostnames to different ports.

## Verification

```bash
# Gateway API healthy
curl -s http://127.0.0.1:8642/health

# Workspace serving HTML
curl -s http://127.0.0.1:3000 | grep -o '<title>[^<]*</title>'
# → <title>Hermes Workspace</title>

# Login flow
curl -s -X POST http://127.0.0.1:3000/api/auth \
  -H "Content-Type: application/json" \
  -d '{"password":"<CLAUDE_PASSWORD>"}'
# → {"ok":true}

# Auth check with session cookie
curl -s -b "claude-auth=<TOKEN>" http://127.0.0.1:3000/api/auth-check
# → {"authenticated":true,"authRequired":true}

# Tunnel (if configured) — test EVERY hostname individually
curl -sI https://workspace.humangood.ai | head -3
curl -sI https://h1.humangood.ai | head -3
curl -s https://agent.humangood.ai/health
# → HTTP/2 200 for each
```
