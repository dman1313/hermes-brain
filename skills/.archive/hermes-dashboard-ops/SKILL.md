---
name: hermes-dashboard-ops
description: "Operational patterns for the Hermes native dashboard — securing it behind reverse proxies, authoring custom themes with real DOM selectors, and debugging common issues. Companion to the hermes-agent skill's dashboard references."
version: 1.0.0
author: Hermes
metadata:
  hermes:
    tags: [hermes, dashboard, themes, caddy, cloudflare, auth, css, kanban]
    related_skills: [hermes-agent]
---

# Hermes Dashboard Operations

Operational patterns for running, securing, and customizing the Hermes native dashboard (port 9119). Covers what the `hermes-agent` skill's dashboard references don't: real-world deployment, auth workarounds, and discovered DOM selectors.

**Companion to:** `hermes-agent` skill → `references/dashboard-user-themes.md`, `references/dashboard-plugins.md`.

## Securing the Dashboard — Auth Options

### Option 1: Cookie Auth Proxy (Recommended for SPAs)

**Caddy basic auth causes login loops with SPAs.** The browser prompts for credentials, the proxy accepts, but the backend's own 401 responses (from session-token checks) re-trigger the browser's auth prompt. The browser can't distinguish proxy-level 401 from backend-level 401.

**Solution:** A lightweight Python auth proxy with cookie-based auth. No browser popup, no loops.

**Architecture:** `Cloudflare Tunnel → Auth Proxy (:9121) → Dashboard (:9119)`

**How it works:**
1. User visits the URL → sees a styled login page (no browser popup)
2. Clicks "Open Dashboard" → proxy sets an HttpOnly cookie and redirects to `/`
3. All subsequent requests carry the cookie → proxy forwards to dashboard
4. Backend 401s don't trigger auth prompts because the browser sees them as normal API responses, not auth challenges

**Steps:**

1. Generate a token:
   ```bash
   TOKEN=$(openssl rand -hex 32)
   echo "Token: $TOKEN"
   ```

2. Create the auth proxy (`~/dashboard-auth-proxy.py`). See `references/auth-proxy-cookie.md` for the full template.

3. Create systemd service:
   ```bash
   sudo cp dashboard-auth-proxy.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable --now dashboard-auth-proxy
   ```

4. Update Cloudflare tunnel ingress (`~/.cloudflared/config.yml`):
   ```yaml
   - hostname: hermesdash.humangood.ai
     service: http://127.0.0.1:9121  # proxy port, not dashboard
   ```

5. Restart tunnel:
   ```bash
   sudo systemctl restart cloudflared-proxy
   ```

6. Verify:
   ```bash
   # Without cookie → login page
   curl -s https://hermesdash.humangood.ai/ | grep "Open Dashboard"
   # With cookie → dashboard
   curl -s -b "hermes_token=$TOKEN" https://hermesdash.humangood.ai/ | grep "Hermes Agent - Dashboard"
   # Auth endpoint → sets cookie + redirects
   curl -s -D - https://hermesdash.humangood.ai/auth | grep -i "set-cookie\|location"
   ```

### Option 2: Caddy Basic Auth (Simple, but loops with SPAs)

**Warning:** This approach causes login loops with SPAs. Use Option 1 instead. Documented here for non-SPA backends.

**Architecture:** `Cloudflare Tunnel → Caddy (:9120, basic auth) → Dashboard (:9119)`

**Steps:**

1. Generate a password hash:
   ```bash
   PASSWORD=$(openssl rand -base64 16 | tr -d '/+=' | head -c 16)
   echo "Password: $PASSWORD"
   HASH=$(caddy hash-password --plaintext "$PASSWORD")
   ```

2. Add to `/etc/caddy/Caddyfile`:
   ```
   :9120 {
       basic_auth {
           <username> <hash>
       }
       reverse_proxy localhost:9119
   }
   ```

3. Validate and reload:
   ```bash
   caddy validate --config /etc/caddy/Caddyfile
   sudo systemctl reload caddy
   ```

4. Update Cloudflare tunnel ingress and restart tunnel service.

### Pitfalls

- **Caddy basic_auth causes login loops with SPAs.** The browser can't distinguish proxy-level 401 from backend-level 401. Use the cookie auth proxy instead. See `references/auth-proxy-cookie.md`.
- **Caddy `basic_auth` block format:** username and hash must be on the SAME line inside the block. A comment line above the hash causes a parse error: `"username and password cannot be empty or missing"`.
- **Cloudflare tunnel service name:** The main tunnel config is usually served by `cloudflared-proxy.service` (check with `systemctl list-units | grep cloudflared`). Don't restart the wrong one.
- **Dashboard restart kills the port:** If the dashboard process dies, Caddy returns 502. Use `hermes dashboard --stop` then restart with `terminal(background=true)`.
- **`--insecure` is still needed:** The dashboard process itself must still run with `--insecure` because Caddy forwards the original Host header from Cloudflare.

## Theme Authoring Workflow

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

```javascript
// Get card HTML structure
document.querySelector('.hermes-kanban-card')?.innerHTML
```

### Step 2: Write Targeted CSS

Use the real class names. See `references/kanban-dom-selectors.md` for the full map.

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
- **`colorOverrides` are required for light themes** — the palette's `color-mix()` derivation produces inverted results for light backgrounds. Pin all shadcn tokens explicitly.
- **`midground` is the primary text/accent color** — for light themes, set it to near-black (`#1a1816`), not an accent color. Use `colorOverrides.primary` for accent color.
- **`customCSS` max 32KB** — keep it focused. Remove unused selectors.
- **`:nth-child()` for column borders** — columns don't have unique IDs. Use positional selectors for per-column styling.
- **Stale card classes:** `.hermes-kanban-card--stale-amber` and `.hermes-kanban-card--stale-red` are applied automatically by the kanban plugin based on task age.

## Dashboard Process Management

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
