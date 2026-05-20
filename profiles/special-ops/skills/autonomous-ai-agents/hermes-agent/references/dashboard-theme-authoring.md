# Dashboard Theme Authoring

User themes live at `~/.hermes/dashboard-themes/*.yaml` and are loaded
on every API call — no restart needed. The dashboard reads from YAML via
`_discover_user_themes()` in `web_server.py`.

## Palette: the 3-layer model

The three palette layers drive ALL shadcn-compat tokens via `color-mix()`:

| Layer | Role | Light theme value | Dark theme value |
|-------|------|-------------------|------------------|
| `background` | Page canvas | `#ffffff` | near-black |
| `midground` | **Text color** + accent base | near-black `#1a1816` | cream `#ffe6cb` |
| `foreground` | Top highlight (often invisible) | white α=0 | white α=0 |

**CRITICAL PITFALL**: `midground` is the PRIMARY TEXT COLOR. If you set
midground to a brand color (green, blue, etc.), ALL text turns that color.
Keep brand colors in `colorOverrides.primary` instead. Midground should
be dark for light themes and light for dark themes.

## colorOverrides — shadcn token mapping

These override the derived shadcn tokens. Keys are camelCase, values are hex:

| Key | CSS var | Typical light-theme value |
|-----|---------|--------------------------|
| `primary` | `--color-primary` | `#4a7c59` (brand green) |
| `primaryForeground` | `--color-primary-foreground` | `#ffffff` |
| `card` | `--color-card` | `#ffffff` |
| `cardForeground` | `--color-card-foreground` | `#1a1816` |
| `muted` | `--color-muted` | `#f0ece6` |
| `mutedForeground` | `--color-muted-foreground` | `#78716c` (warm gray, NOT too light) |
| `border` | `--color-border` | `#d9d3c7` |
| `ring` | `--color-ring` | matches primary |
| `destructive` | `--color-destructive` | `#c47d7d` |
| `accent` | `--color-accent` | matches primary |

## componentStyles — per-bucket CSS vars

Emitted as `--component-<bucket>-<kebab-prop>` on `:root`. Buckets:
`card`, `header`, `footer`, `sidebar`, `tab`, `progress`, `badge`,
`backdrop`, `page`. Values are raw CSS strings.

Example:
```yaml
componentStyles:
  card:
    boxShadow: "0 1px 4px rgba(0,0,0,0.04)"
  header:
    background: "rgba(255,255,255,0.6)"
    backdropFilter: "blur(16px)"
```

## customCSS — raw CSS injection

Injected as a `<style id="hermes-theme-custom-css">` tag on theme apply.
Capped at 32 KiB. Use for selectors, pseudo-elements, animations, etc.

Common targets:
- `.hermes-kanban-*` — kanban board selectors
- `[data-slot="sidebar"]` — Nous DS sidebar
- `[data-component="card"]` — Nous DS card
- `::-webkit-scrollbar` — scrollbar styling
- `input, select` — form elements

The dashboard uses Nous Design System + Tailwind. Kanban uses
`plugins/kanban/dashboard/dist/style.css` with its own class namespace.

## Typography

Fonts load via Google Fonts URL. Light themes need 400-800 weights.
Drop 300 (too thin on light backgrounds). `baseSize: "16px"` is more
readable than the default 15px. `letterSpacing: "0"` avoids the
condensed feel of negative letter-spacing on light themes.

Good light-theme typography:
```yaml
typography:
  fontSans: "Inter, system-ui, sans-serif"
  fontMono: "JetBrains Mono, ui-monospace, monospace"
  fontUrl: "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap"
  baseSize: "16px"
  lineHeight: "1.6"
  letterSpacing: "0"
```

## Plugin JS patterns

Dashboard plugins live at `~/.hermes/plugins/<name>/dashboard/` with
`manifest.json`, `dist/index.js`, `dist/style.css`.

For hidden plugins (no tab) that do DOM manipulation:
- Use a plain IIFE — do NOT use `window.__HERMES_PLUGINS__.register()`.
  `register()` stores a React component that's only rendered on tab visit.
  Hidden plugins never get visited, so the function is never called.
- IIFE executes immediately when the `<script async>` tag loads.
- Use MutationObserver to catch React re-renders.
- Multiple `setTimeout()` calls (500ms, 1500ms, 3000ms) catch initial
  render and any delayed React hydration.

For plugins that need data from the kanban API:
- Fetch from `/api/plugins/kanban/agents` (returns agent roster)
- Fetch from `/api/plugins/kanban/board` (returns full board state)
- Plugin API routes are unauthenticated by default (localhost-only dashboard)

## Dashboard startup

```bash
# Stop stale processes
hermes dashboard --stop

# Start (use --insecure for Cloudflare Tunnel / reverse proxy)
hermes dashboard --port 9119 --host 0.0.0.0 --insecure --no-open &

# Verify
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:9119/
```

Behind Cloudflare Tunnel, the Host header check rejects non-localhost
requests. `--insecure` disables this check.
