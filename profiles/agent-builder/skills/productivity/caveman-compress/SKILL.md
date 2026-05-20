---
name: caveman-compress
description: >
  Compress natural language memory files (CLAUDE.md, todos, preferences) into caveman format
  to save input tokens. Preserves all technical substance, code, URLs, and structure.
  Compressed version overwrites the original file. Human-readable backup saved as FILE.original.md.
  Trigger: /caveman:compress <filepath> or "compress memory file"
---

# Caveman Compress

## Purpose

Compress natural language files (CLAUDE.md, MEMORY.md, AGENTS.md, todos, preferences) into caveman-speak to reduce input tokens. Compressed version overwrites original. Human-readable backup saved as `<filename>.original.md`.

## Trigger

`/caveman:compress <filepath>` or when user asks to compress a memory file.

## Process

1. This SKILL.md lives alongside `scripts/` in the same directory. Find that directory.
2. Run: `cd <skill_dir> && python3 -m scripts <absolute_filepath>`
3. The CLI compresses, validates, retries on failures, and returns result.

## Compression Rules

### Remove
- Articles: a, an, the
- Filler: just, really, basically, actually, simply, essentially, generally
- Pleasantries: "sure", "certainly", "of course", "happy to"
- Hedging: "it might be worth", "you could consider", "it would be good to"
- Redundant phrasing: "in order to" → "to", "make sure to" → "ensure"
- Connective fluff: "however", "furthermore", "additionally"

### Preserve EXACTLY (never modify)
- Code blocks (fenced ``` and indented)
- Inline code (`backtick content`)
- URLs and links
- File paths
- Commands
- Technical terms
- Dates, version numbers, numeric values

### Preserve Structure
- All markdown headings (compress body below, keep heading text)
- Bullet point hierarchy
- Numbered lists
- Tables (compress cell text, keep structure)
- Frontmatter/YAML headers

## Boundaries

- ONLY compress natural language files (.md, .txt, extensionless)
- NEVER modify: .py, .js, .ts, .json, .yaml, .yml, .toml, .env, .lock, .css, .html, .xml, .sql, .sh
- Original file backed up as FILE.original.md before overwriting
- Never compress FILE.original.md
