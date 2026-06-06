# Kanban DOM Selectors

Discovered from Hermes v0.15.1 live dashboard. Use these for theme CSS targeting.

## Board Structure

```
.hermes-kanban                          # Root container
.hermes-kanban-boardswitcher            # Board selector area
.hermes-kanban-boardswitcher-inner      # Board selector inner
.hermes-kanban-docs-link                # "?" documentation link
.hermes-kanban-columns                  # All columns container (flex, gap: 16px)
.hermes-kanban-column                   # Single column wrapper
```

## Column Structure

```
.hermes-kanban-column                   # Column wrapper
  .hermes-kanban-column-header          # Header row
    .hermes-kanban-col-check            # Bulk select checkbox
    .hermes-kanban-dot                  # Status dot (base class)
    .hermes-kanban-dot-triage           # Purple: #9b7eb5
    .hermes-kanban-dot-todo             # Blue: #7a9eb5
    .hermes-kanban-dot-ready            # Amber: #d4a843
    .hermes-kanban-dot-running          # Green: #3d7a4f (animated pulse)
    .hermes-kanban-dot-blocked          # Red: #c47d7d
    .hermes-kanban-dot-done             # Sage: #6b9e7a
    .hermes-kanban-column-label         # Column name (uppercase text)
    .hermes-kanban-column-count         # Task count badge
    .hermes-kanban-column-add           # "+" add task button
  .hermes-kanban-column-sub             # Column description (italic helper text)
  .hermes-kanban-column-body            # Card container
    .hermes-kanban-card                 # Task card
    ...cards...
  .hermes-kanban-empty                  # Empty column placeholder
  .kanban-empty                         # Empty state wrapper
  .kanban-empty-icon                    # Empty state icon
```

## Column Order (positional :nth-child for border styling)

1. Triage (purple)
2. Todo (blue)
3. Scheduled (amber)
4. Ready (green)
5. In Progress / Running (green, animated)
6. Blocked (red)
7. review (blue)
8. Done (sage)

## Card Structure

```
.hermes-kanban-card                     # Card wrapper (button role)
  .hermes-kanban-card--stale-amber      # Modifier: overdue (amber left border)
  .hermes-kanban-card--stale-red        # Modifier: very overdue (red left border)
  .hermes-kanban-card-content           # Inner content wrapper (p-4)
    .hermes-kanban-card-row             # Top row: id + priority + progress
      .hermes-kanban-card-check-wrap    # Checkbox wrapper
      .hermes-kanban-card-check         # Checkbox button
      .hermes-kanban-card-id            # Task ID (monospace, e.g. "t_1466032f")
      .hermes-kanban-priority           # Priority badge (P1-P10, inline styles)
      .hermes-kanban-progress           # Progress ring (SVG, child tasks)
        .progress-ring                  # SVG container (32x32)
          .progress-ring-bg             # Background circle (#e2ddd5)
          .progress-ring-fill           # Fill circle (#3d7a4f)
    .hermes-kanban-card-title           # Task title (most important text)
    .hermes-kanban-card-row.hermes-kanban-card-meta  # Metadata row
      .hermes-kanban-assignee           # Assignee badge (e.g. "@coder")
      .hermes-kanban-unassigned         # Unassigned indicator
      .hermes-kanban-count              # Dependency/comment count
      .hermes-kanban-ago                # Age timestamp (e.g. "26d ago")
```

## Warning/Attention Elements

```
.hermes-kanban-attention                # Attention banner wrapper
.hermes-kanban-attention--critical      # Critical severity modifier
.hermes-kanban-attention-bar            # Banner bar
.hermes-kanban-attention-icon           # Icon ("!!!")
.hermes-kanban-attention-text           # Text content
.hermes-kanban-attention-toggle         # Show/hide toggle
.hermes-kanban-attention-dismiss        # Dismiss button ("✕")

.hermes-kanban-warning-badge            # Card warning badge
.hermes-kanban-warning-badge--critical  # Critical warning
.hermes-kanban-needs-assignee           # Needs assignment indicator
```

## Other Elements

```
.hermes-kanban-trash                    # Trash zone
.hermes-kanban-trash-icon               # Trash icon
.hermes-kanban-trash-label              # Trash label
```

## CSS Gotchas

- **Priority badges use inline styles** — `background-color` and `color` are set via `style=""`, not classes. Override with `!important` on the `.hermes-kanban-priority` class.
- **Progress ring is SVG** — style `.progress-ring-bg` and `.progress-ring-fill` for colors. `stroke-dashoffset` controls fill amount (dynamic).
- **Columns have no unique IDs** — use `.hermes-kanban-column:nth-child(N)` for per-column styling.
- **Cards are buttons** — the outer `.hermes-kanban-card` has `role="button"`. Inner content uses Tailwind classes mixed with hermes classes.
- **Column descriptions** (`.hermes-kanban-column-sub`) are only visible when the column has a description defined. Empty columns may not show this element.
