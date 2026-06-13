# Kanban Board DOM Classes

Real class names from Hermes dashboard v0.15 kanban plugin.
Discovered via `document.querySelectorAll('[class*="kanban"]')` DOM inspection.

## All Kanban Classes

```
hermes-kanban
hermes-kanban-boardswitcher
hermes-kanban-boardswitcher-inner
hermes-kanban-docs-link
hermes-kanban-attention
hermes-kanban-attention--critical
hermes-kanban-attention-bar
hermes-kanban-attention-icon
hermes-kanban-attention-text
hermes-kanban-attention-toggle
hermes-kanban-attention-dismiss
hermes-kanban-columns
hermes-kanban-column
hermes-kanban-column-header
hermes-kanban-col-check
hermes-kanban-dot
hermes-kanban-dot-triage
hermes-kanban-dot-todo
hermes-kanban-dot-ready
hermes-kanban-dot-running
hermes-kanban-dot-blocked
hermes-kanban-dot-done
hermes-kanban-column-label
hermes-kanban-column-count
hermes-kanban-column-add
hermes-kanban-column-sub
hermes-kanban-column-body
kanban-empty
kanban-empty-icon
hermes-kanban-card
hermes-kanban-card--stale-amber
hermes-kanban-card--stale-red
hermes-kanban-card-content
kanban-card
hermes-kanban-card-row
hermes-kanban-card-check-wrap
hermes-kanban-card-check
hermes-kanban-card-id
hermes-kanban-priority
hermes-kanban-progress
hermes-kanban-card-title
hermes-kanban-card-meta
hermes-kanban-assignee
hermes-kanban-count
hermes-kanban-ago
hermes-kanban-unassigned
hermes-kanban-empty
hermes-kanban-warning-badge
hermes-kanban-warning-badge--critical
hermes-kanban-needs-assignee
hermes-kanban-trash
hermes-kanban-trash-icon
hermes-kanban-trash-label
```

## Sample Card HTML Structure

```html
<div class="hermes-kanban-card hermes-kanban-card--stale-amber">
  <div class="p-4 hermes-kanban-card-content kanban-card" data-enhanced="true">
    <div class="hermes-kanban-card-row">
      <label class="hermes-kanban-card-check-wrap">
        <button class="... hermes-kanban-card-check" aria-label="Select task t_1466032f"></button>
      </label>
      <span class="hermes-kanban-card-id">t_1466032f</span>
      <span class="hermes-kanban-priority" style="background-color: ...; color: rgb(255,255,137);">P5</span>
      <span class="hermes-kanban-progress">
        <div class="progress-ring">
          <svg><circle class="progress-ring-bg"/><circle class="progress-ring-fill"/></svg>
          <div>0/2</div>
        </div>
      </span>
    </div>
    <div class="hermes-kanban-card-title">Implement the updog uptime checker CLI</div>
    <div class="hermes-kanban-card-row hermes-kanban-card-meta">
      <span class="hermes-kanban-assignee">@coder</span>
      <span class="hermes-kanban-count">↔ 4</span>
      <span class="hermes-kanban-ago">26d ago</span>
    </div>
  </div>
</div>
```

## Sample Column Header HTML

```html
<div class="hermes-kanban-column-header" title="Raw ideas — a specifier will flesh out the spec">
  <button class="... hermes-kanban-col-check" aria-label="Select all tasks in Triage"></button>
  <span class="hermes-kanban-dot hermes-kanban-dot-triage"></span>
  <span class="hermes-kanban-column-label">Triage</span>
  <span class="hermes-kanban-column-count">0</span>
  <button class="hermes-kanban-column-add">+</button>
</div>
```

## DOM Inspection Command

Run in browser console to get current state:
```js
(() => {
  const cols = document.querySelectorAll('.hermes-kanban-column');
  return Array.from(cols).map(col => ({
    label: col.querySelector('.hermes-kanban-column-label')?.textContent,
    count: col.querySelector('.hermes-kanban-column-count')?.textContent,
    dot: col.querySelector('.hermes-kanban-dot')?.className,
    desc: col.querySelector('.hermes-kanban-column-sub')?.textContent?.trim(),
    cards: col.querySelectorAll('.hermes-kanban-card').length
  }));
})()
```

## CSS Styling Tips

- **Column left borders:** Use `:nth-child(N)` to color-code columns since dot classes are the only distinguishing attribute
- **Stale cards:** `.hermes-kanban-card--stale-amber` and `--stale-red` get left border warnings
- **Progress rings:** SVG circles with `stroke-dashoffset` — target `.progress-ring-fill` for color
- **Priority badges:** Inline styles set by React — use `!important` to override
- **Assignee badges:** Green tint with `.hermes-kanban-assignee { background: rgba(61,122,79,0.08) }`
