# Natural Kanban Plugin Pattern

A hidden dashboard plugin that enhances the kanban board with DOM manipulation
(MutationObserver + fetch). Lives at `~/.hermes/plugins/natural-kanban/dashboard/`.

## Structure

```
natural-kanban/dashboard/
├── manifest.json     — hidden plugin, no tab, CSS + JS entry
├── dist/
│   ├── style.css     — card, badge, progress ring, squad bar styles
│   └── index.js      — IIFE: MutationObserver + fetch-based DOM injection
```

## manifest.json

```json
{
  "name": "natural-kanban",
  "label": "Natural Kanban",
  "icon": "Palette",
  "version": "1.0.0",
  "tab": {"hidden": true},
  "slots": ["kanban-header"],
  "entry": "dist/index.js",
  "css": "dist/style.css"
}
```

## Key patterns

### IIFE, not register()

Hidden plugins should NOT call `window.__HERMES_PLUGINS__.register()`.
`register()` stores a React component that only renders when the plugin tab
is visited. Hidden plugins have no tab, so the component is never mounted.

Instead, use a plain IIFE:

```js
(function() {
  'use strict';
  // DOM manipulation code runs immediately when <script async> loads
})();
```

### MutationObserver for React re-renders

The kanban board is a React SPA. Navigation between pages causes re-renders
that replace DOM elements. Use MutationObserver to re-apply enhancements:

```js
var observer = new MutationObserver(function() { runAll(); });
observer.observe(document.body, { childList: true, subtree: true });
```

### Multiple timeouts for initial render

React hydration can take several render cycles. Use staggered timeouts:

```js
setTimeout(runAll, 500);   // first SPA render
setTimeout(runAll, 1500);  // delayed hydration
setTimeout(runAll, 3000);  // catch stragglers
```

### Fetch from plugin API

Plugin API routes are unauthenticated (localhost-only dashboard):

```js
fetch('/api/plugins/kanban/agents')
  .then(function(r) { return r.json(); })
  .then(function(data) {
    var active = data.agents.filter(function(a) { return a.totalTasks > 0; });
    // Build DOM from agent data
  });
```

### Inject keyframes dynamically

CSS animations can be injected via JS to avoid polluting global styles:

```js
var style = document.createElement('style');
style.id = 'nat-kanban-styles';
style.textContent = '@keyframes agent-pulse{...}';
document.head.appendChild(style);
```

### Check for existing injection

Always guard against double-injection with a data attribute or class check:

```js
if (board.querySelector('.squad-grid')) return;  // already injected
if (card.dataset.enhanced) return;               // already enhanced
```

## CSS targeting

Complete kanban DOM selector reference: `references/kanban-dom-selectors.md`.

Key classes used by the plugin:
- `.hermes-kanban` — board root
- `.hermes-kanban-columns` — columns grid
- `.hermes-kanban-column` — single column (use `:nth-child(N)` for per-column)
- `.hermes-kanban-column-header` — column title
- `.hermes-kanban-column-label` — column name text
- `.hermes-kanban-column-sub` — column description
- `.hermes-kanban-column-count` — count badge
- `.hermes-kanban-card` — card wrapper (`<button>`, not `<div>`)
- `.hermes-kanban-card-content` — card inner (use this for styling)
- `.hermes-kanban-card-id` — task ID span
- `.hermes-kanban-card-title` — title span
- `.hermes-kanban-assignee` — assignee badge
- `.hermes-kanban-unassigned` — unassigned label
- `.hermes-kanban-priority` — priority badge (has inline styles, use `!important`)
- `.hermes-kanban-progress` — progress ring wrapper (SVG inside)
- `.hermes-kanban-count` — dependency/comment count
- `.hermes-kanban-ago` — age timestamp
- `.hermes-kanban-empty` — empty column placeholder
- `.kanban-empty` — alternate empty state
- `.hermes-kanban-dot-{status}` — status color dots (triage/todo/ready/running/blocked/done)
- `.hermes-kanban-card--stale-amber` — overdue card modifier
- `.hermes-kanban-card--stale-red` — very overdue card modifier

## Force dashboard to discover the plugin

The dashboard caches plugins per-process. After creating/modifying a plugin:

```bash
curl http://127.0.0.1:9119/api/dashboard/plugins/rescan
```

Then refresh the browser. The frontend's `usePlugins` hook fetches manifests
on mount and injects CSS/JS for each discovered plugin.
