# Extending the Native Dashboard (Kanban Plugin + React)

How to add new data endpoints and UI components to the native Hermes dashboard.

## Architecture

```
Browser (React SPA)
  → /api/plugins/kanban/*  (plugin API routes, auth-bypassed)
  → /api/*                 (core dashboard API, session-token auth)
  ↑
Dashboard process (FastAPI + uvicorn, port 9119)
  ├── web_server.py              (core routes, theme API, plugin loading)
  ├── web_dist/                  (built React SPA, from web/ → npm run build)
  └── plugins/kanban/dashboard/
       ├── plugin_api.py         (backend routes, mounted at /api/plugins/kanban/)
       ├── dist/                 (built plugin frontend)
       └── manifest.json
```

The kanban board is a **dashboard plugin** — its Python routes are mounted at
`/api/plugins/kanban/` and its React code is built separately. The core
dashboard SPA loads plugin manifests from `/api/dashboard/plugins` and
renders plugin tabs via `<PluginSlot>` and `<PluginPage>`.

## Pattern A: New API Endpoint (No Frontend Rebuild)

Add a route to `plugins/kanban/dashboard/plugin_api.py`:

```python
@router.get("/agents")
def get_agents(board: Optional[str] = Query(None)):
    """Return agent roster with live task counts for the Squad Bar."""
    board = _resolve_board(board)
    conn = _conn(board=board)
    try:
        rows = conn.execute(
            "SELECT assignee, status, COUNT(*) AS cnt "
            "FROM tasks WHERE status != 'archived' "
            "GROUP BY assignee, status"
        ).fetchall()
        # ... build agent summaries with metadata ...
        return {"agents": agents}
    finally:
        conn.close()
```

Conventions:
- Use `_conn()` and `_resolve_board()` helpers (auto-init DB on first call)
- Always close connections in `finally`
- Routes under `/api/plugins/` are unauthenticated (dashboard binds localhost)
- Plugin reloads when dashboard restarts — no separate build step

## Pattern B: New React Component (Frontend Rebuild)

Create `web/src/components/AgentSquadBar.tsx`:

```tsx
import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";

export default function AgentSquadBar() {
  const [agents, setAgents] = useState([]);

  useEffect(() => {
    fetch("/api/plugins/kanban/agents")
      .then((r) => r.json())
      .then((d) => setAgents(d.agents))
      .catch(() => {});
  }, []);

  return (/* JSX using theme CSS vars */);
}
```

Wire into `web/src/App.tsx`:
```tsx
import AgentSquadBar from "@/components/AgentSquadBar";
// ... in the JSX, after <PluginSlot name="header-banner" />:
<AgentSquadBar />
```

Rebuild: `cd ~/.hermes/hermes-agent/web && npm run build`
Restart: `hermes dashboard --stop && hermes dashboard --port 9119 --host 0.0.0.0 --insecure --no-open &`

## Pattern C: CSS-Only Dashboard Plugin (No Web Rebuild)

For pure styling enhancements, create a hidden plugin at `~/.hermes/plugins/<name>/`:

**manifest.json:**
```json
{
  "name": "natural-kanban",
  "label": "Natural Kanban",
  "icon": "Palette",
  "version": "1.0.0",
  "tab": { "hidden": true },
  "slots": ["kanban-header"],
  "entry": "dist/index.js",
  "css": "dist/style.css"
}
```

**dist/style.css:** Theme-variable-aware CSS that styles kanban cards, badges,
progress rings, empty states, etc. Use `var(--color-*)` for theme compliance.

**dist/index.js:** Minimal export (can be a null component for CSS-only plugins):
```js
export default function NaturalKanbanHeader() { return null; }
```

This pattern needs no web rebuild — drop the files, rescan plugins
(`/api/dashboard/plugins/rescan`), and the CSS loads automatically.

## Theme Integration for Components

- Use `var(--color-foreground)` etc. for theme-responsive colors
- Use `var(--theme-font-sans)` / `var(--theme-font-mono)` for fonts
- Use `cn()` for conditional Tailwind classes
- Components auto-restyle when the active theme changes (CSS vars cascade)

## Pitfalls

- **TypeScript strict mode** — unused imports fail `tsc -b`. Remove any unused imports.
- **Build takes 10-30 seconds** — output goes to `hermes_cli/web_dist/`.
- **Backend changes need dashboard restart** — plugin API loaded at process startup.
- **Frontend changes need `npm run build` + dashboard restart**.
- **Auth bypass** — plugin routes under `/api/plugins/` skip auth middleware. Fine on localhost, exposed on `0.0.0.0`.
- **Component must handle loading/empty states** — API may take a moment or return empty data.
- **Background processes** — use the background tool to start `hermes dashboard`, not shell `&` inside a background block. Shell `&` gets swallowed.
