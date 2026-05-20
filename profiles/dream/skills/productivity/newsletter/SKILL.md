---
name: newsletter
description: Deprecated alias for the master-newsletter workflow. Use this when a user asks for a newsletter pipeline, email campaign draft, or voice/photo-to-newsletter conversion and route the work to master-newsletter.
triggers:
  - newsletter
  - email newsletter
  - campaign draft
---

# Newsletter (Deprecated Alias)

This skill is deprecated.

Use `master-newsletter` for all real work.

## Redirect rule

If the user invokes `newsletter`, immediately follow the `master-newsletter` skill instead.

## Why this exists

This preserves compatibility with older workflows and references.

## Short note to preserve behavior

Legacy system:
- `newsletter` -> redirects to `master-newsletter`
- `clark` refers to the communications-officer role used inside `master-newsletter`

Platform exports supported through `master-newsletter` include:
- Beehiiv-ready copy
- ConvertKit-ready copy
- HTML email export
