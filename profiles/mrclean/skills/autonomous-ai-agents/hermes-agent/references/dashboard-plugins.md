# Dashboard Plugin Creation

Plugins extend the Hermes dashboard with custom components, CSS, and API routes.
Located at `~/.hermes/plugins/<name>/dashboard/` or bundled at `plugins/<name>/dashboard/`.

## Files

```
~/.hermes/plugins/<name>/dashboard/
├── manifest.json     # plugin metadata
├── plugin_api.py     # FastAPI routes (optional)
└── dist/
    ├── index.js      # React component or IIFE
    └── style.css     # plugin styles
```

## manifest.json

```json
{
  "name": "natural-kanban",
  "label": "Natural Kanban",
  "description": "Earth-tone kanban enhancements",
  "icon": "Palette",
  "version": "1.0.0",
  "tab": { "hidden": true },
  "slots": ["kanban-header"],
  "entry": "dist/index.js",
  "css": "dist/style.css"
}
```

- `tab.hidden: true` — no sidebar tab, just slot injection + side effects
- `slots` — named slots this plugin renders into (from `PluginSlot` components)
- `entry` — JS bundle (React component registered via `window.__HERMES_PLUGINS__.register()`)
- `css` — stylesheet auto-injected as `<link>`

## Plugin Types

### React Component Plugin
Registers via `window.__HERMES_PLUGINS__.register(name, Component)`.
Component renders when plugin tab is visited. For slot-only plugins, use `registerSlot()`.

### IIFE Plugin (DOM Enhancement)
Plain JS IIFE that executes on script load. Uses MutationObserver to watch for
DOM changes and enhance elements. No `register()` call needed.

**Caveat**: The dashboard sets `NO_REGISTER` error on script load if no component
registered. For hidden plugins this error is harmless (never displayed).
For visible plugins, call `register()` with at least a null component.

```js
(function() {
  'use strict';
  // DOM manipulation here
  var observer = new MutationObserver(function() { /* enhance */ });
  observer.observe(document.body, { childList: true, subtree: true });
})();
```

## Agent Squad Bar Pattern

A common pattern is a React component that:
1. Fetches agent data from a backend endpoint
2. Renders a grid of agent cards with avatars, progress rings, status dots
3. Provides quick task assignment

### Backend endpoint (plugin_api.py)
```python
@router.get("/agents")
def get_agents():
    # Query kanban.db for per-assignee task counts + active run progress
    # Return { agents: [{ name, display, emoji, gradient, color, totalTasks, status, progress }] }
```

### Frontend component (React)
```tsx
export default function AgentSquadBar() {
  const [agents, setAgents] = useState([]);
  useEffect(() => {
    fetch("/api/plugins/kanban/agents").then(r => r.json()).then(setAgents);
    const interval = setInterval(() => /* refetch */, 10000);
    return () => clearInterval(interval);
  }, []);

  // Filter active-only, render grid with SVG progress rings, green glow for busy
  const active = agents.filter(a => a.totalTasks > 0);
  return <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(140px, 1fr))" }}>...</div>;
}
```

Wire into `App.tsx`:
```tsx
import AgentSquadBar from "@/components/AgentSquadBar";
// ...
<PluginSlot name="header-banner" />
<AgentSquadBar />  // renders on all pages
```

### Key design decisions
- **Active-only**: hide agents with zero tasks (reduces noise)
- **Grid layout**: `auto-fill, minmax(140px, 1fr)` wraps naturally
- **Green glow**: `box-shadow` animation on busy agents
- **Progress ring**: SVG circle with `stroke-dashoffset` computed from progress %
- **Quick assign**: click agent card → inline task creation form pre-filled with assignee
- **Auto-refresh**: 10-second polling interval

## Plugin Discovery

Dashboard scans three locations (via `web_server.py` → `_discover_dashboard_plugins()`):
1. `~/.hermes/plugins/<name>/dashboard/manifest.json` (user)
2. Bundled memory plugins
3. Bundled plugins root

Force rescan: `curl http://127.0.0.1:9119/api/dashboard/plugins/rescan`

## Plugin Asset Loading

`usePlugins.ts` handles:
1. Fetch manifests from `/api/dashboard/plugins`
2. Inject CSS `<link>` tags
3. Load JS `<script async>` tags
4. Wait for `register()` calls, resolve components
