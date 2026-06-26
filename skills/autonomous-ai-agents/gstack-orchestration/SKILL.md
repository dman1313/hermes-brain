---
name: gstack-orchestration
description: Hermes orchestration of GStack — Garry Tan's AI engineering workflow suite. When Dwayne says "use gstack", fire up Claude Code (or Kimi CLI as fallback) with gstack skills loaded in the relevant project directory.
version: 1.0.0
---

# GStack Orchestration

GStack (~/.claude/skills/gstack/) is a collection of specialized AI engineering skills
that give AI agents structured roles for software development.

## When to Use

When Dwayne says **"use gstack"**, fire up a `claude` CLI session in the relevant project directory
with gstack capabilities available.

## Method: Claude Code Print Mode (PREFERRED)

For most tasks, use one-shot print mode:

```bash
claude -p "Run the /browse skill to..." --allowedTools 'Read,Edit,Bash,Write' --max-turns 20
```

For structured workflows (reviews, ships, etc.), gstack skills are invoked as slash commands inside Claude Code sessions.

## Key Rules

1. **Never use mcp__claude-in-chrome__\* tools** — use gstack's `/browse` skill for all web browsing
2. All gstack skills are available as `gstack-` prefixed Hermes skills
3. In Claude Code, skills are invoked as `/slash` commands (e.g., `/office-hours`, `/plan-ceo-review`, `/browse`)

## Available Skills

| Command | Purpose |
|---------|---------|
| `/office-hours` | Reframe product idea before coding |
| `/plan-ceo-review` | CEO-level product review |
| `/plan-eng-review` | Lock architecture, data flow, edge cases |
| `/plan-design-review` | Rate design dimensions 0-10 |
| `/plan-devex-review` | DX experience audit |
| `/design-consultation` | Build design system from scratch |
| `/design-shotgun` | Generate multiple AI design variants |
| `/design-html` | Production-quality HTML/CSS |
| `/review` | Pre-landing PR review |
| `/ship` | Tests, review, push, PR |
| `/land-and-deploy` | Merge, CI, deploy, verify |
| `/canary` | Post-deploy monitoring |
| `/benchmark` | Performance regression detection |
| `/browse` | **Headless browser — use THIS for web browsing** |
| `/connect-chrome` | Connect to real Chrome |
| `/qa` | Browser QA: find bugs, fix, re-verify |
| `/qa-only` | Browser QA: report only |
| `/design-review` | Live-site visual audit + fix |
| `/setup-browser-cookies` | Import cookies for authenticated testing |
| `/setup-deploy` | Deploy config detection |
| `/setup-gbrain` | Cross-machine session memory sync |
| `/retro` | Weekly retro |
| `/investigate` | Root-cause debugging |
| `/document-release` | Update docs for what shipped |
| `/document-generate` | Generate Diataxis docs from code |
| `/codex` | Second opinion via OpenAI Codex |
| `/cso` | OWASP Top 10 + STRIDE audit |
| `/autoplan` | CEO → design → eng → DX review in one command |
| `/careful` | Warn before destructive commands |
| `/freeze` | Lock edits to one directory |
| `/guard` | Both careful + freeze |
| `/unfreeze` | Remove directory restrictions |
| `/gstack-upgrade` | Update gstack |
| `/learn` | Manage what gstack learned |

## Prerequisites

- `claude` CLI (installed at ~/.hermes/node/bin/claude) — **check auth before use**
- `kimi` CLI (fallback, if Kimi is requested)
- Bun installed at ~/.bun/bin/bun
- GStack repo at ~/.claude/skills/gstack/

## One-Shot Task

```bash
claude -p "prompt" --allowedTools 'Read,Edit,Bash,Write' --max-turns 20
```

## Pre-Flight Auth Check

```bash
claude auth status --text 2>&1
```
If not logged in: user must run `claude auth login --console` themselves.
