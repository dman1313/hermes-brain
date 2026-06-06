# Kanban DOM Selectors — For Theme CSS Targeting

The kanban board uses `hermes-kanban-*` prefixed classes. Use these exact names
when writing `customCSS` in dashboard theme YAML files. Do NOT guess — the
board is a React app and class names are specific.

## Column Structure

```
.hermes-kanban-columns              — flex container for all columns
.hermes-kanban-column               — single column wrapper
.hermes-kanban-column-header        — header row (checkbox, dot, label, count, add button)
.hermes-kanban-column-label         — column name text (e.g. "Triage", "Todo")
.hermes-kanban-column-count         — task count badge
.hermes-kanban-column-sub           — column description (italic, below header)
.hermes-kanban-column-body          — card container within column
.hermes-kanban-column-add           — "+" button to create task
.hermes-kanban-col-check            — select-all checkbox
```

## Status Dots (inside column header)

```
.hermes-kanban-dot                  — base dot
.hermes-kanban-dot-triage           — purple #9b7eb5
.hermes-kanban-dot-todo             — blue #7a9eb5
.hermes-kanban-dot-ready            — amber #d4a843
.hermes-kanban-dot-running          — green #3d7a4f
.hermes-kanban-dot-blocked          — red #c47d7d
.hermes-kanban-dot-done             — sage #6b9e7a
```

## Card Structure

```
.hermes-kanban-card                 — card wrapper (button element)
.hermes-kanban-card--stale-amber    — modifier: overdue (amber left border)
.hermes-kanban-card--stale-red      — modifier: very overdue (red left border)
.hermes-kanban-card-content         — inner content div (.kanban-card also present)
.hermes-kanban-card-row             — flex row (used for header row and meta row)
.hermes-kanban-card-check-wrap      — checkbox wrapper
.hermes-kanban-card-check           — checkbox button
.hermes-kanban-card-id              — task ID text (e.g. "t_1466032f")
.hermes-kanban-priority             — priority badge (P1-P5, inline-styled bg/color)
.hermes-kanban-progress             — progress ring wrapper (SVG circle inside)
.hermes-kanban-card-title           — task title text
.hermes-kanban-card-meta            — metadata row (assignee, deps, age)
.hermes-kanban-assignee             — assignee badge (e.g. "@coder")
.hermes-kanban-unassigned           — "unassigned" label
.hermes-kanban-count                — dependency/comment count
.hermes-kanban-ago                  — age timestamp (e.g. "26d ago")
```

## Warning/Attention

```
.hermes-kanban-attention             — attention banner wrapper
.hermes-kanban-attention--critical   — critical modifier (red tint)
.hermes-kanban-attention-icon        — icon span
.hermes-kanban-attention-text        — text span
.hermes-kanban-attention-toggle      — show/hide button
.hermes-kanban-attention-dismiss     — dismiss (✕) button
.hermes-kanban-warning-badge         — warning badge on cards
.hermes-kanban-warning-badge--critical — critical warning modifier
.hermes-kanban-needs-assignee        — needs-assignee indicator
```

## Board-Level

```
.hermes-kanban                       — top-level wrapper
.hermes-kanban-boardswitcher         — board selector row
.hermes-kanban-boardswitcher-inner   — inner wrapper
.hermes-kanban-docs-link             — "?" documentation link
```

## Empty States

```
.kanban-empty                        — empty column placeholder
.kanban-empty-icon                   — empty icon
.hermes-kanban-empty                 — alternate empty state
```

## Other

```
.hermes-kanban-trash                 — trash zone
.hermes-kanban-trash-icon            — trash icon
.hermes-kanban-trash-label           — trash label
```

## Column Order

The columns appear in DOM order: Triage, Todo, Scheduled, Ready, In Progress,
Blocked, review, Done. Use `:nth-child(N)` on `.hermes-kanban-column` to target
specific columns for left-border accents:

| Column       | nth-child | Suggested Color |
|-------------|-----------|-----------------|
| Triage      | 1         | #9b7eb5 (purple) |
| Todo        | 2         | #7a9eb5 (blue) |
| Scheduled   | 3         | #d4a843 (amber) |
| Ready       | 4         | #3d7a4f (green) |
| In Progress | 5         | #3d7a4f (green) |
| Blocked     | 6         | #c47d7d (red) |
| review      | 7         | #7a9eb5 (blue) |
| Done        | 8         | #6b9e7a (sage) |

## Pitfalls

- Priority badges (`.hermes-kanban-priority`) have inline `background-color` and
  `color` styles. Use `!important` to override, or accept the inline values.
- Progress rings are SVG (`<circle>` elements with `.progress-ring-bg` and
  `.progress-ring-fill` classes). Target stroke properties, not background.
- Cards are `<button>` elements, not `<div>`. Use `.hermes-kanban-card` not
  `[class*="card"]` to avoid hitting unrelated card components on other pages.
- The board re-renders on filter/search. CSS changes apply immediately via
  the theme's `customCSS` (loaded on every API call, no restart needed).
- To inspect live class names: `browser_console` with
  `document.querySelectorAll('[class*="kanban"]')` and map className values.

## How to Extract More Selectors

Run this in browser_console on the kanban page:

```javascript
[...new Set(
  Array.from(document.querySelectorAll('*')).flatMap(el =>
    Array.from(el.classList).filter(c => c.includes('kanban'))
  )
)]
```

This returns all kanban-prefixed class names currently in the DOM.
