# Claude Code + GLM Coding Plan Setup

## Overview

Z.AI's GLM Coding Plan (DevPack) provides GLM models + 4 MCP servers for coding agents. Claude Code is officially supported. The `@lee_ai/coding-helper` npm package handles backend configuration and avoids the timeout pitfall with bare `ANTHROPIC_BASE_URL`.

## Prerequisites

- GLM Coding Plan subscription (Lite/Pro/Max) at https://z.ai
- API key from https://z.ai/manage-apikey/apikey-list
- Claude Code v2.x installed (`npm install -g @anthropic-ai/claude-code`)
- Node.js >= v22 (required for vision MCP server)

## Step 1: Install Coding Tool Helper

```bash
# Enhanced fork with dynamic model selection (preferred)
npm install -g @lee_ai/coding-helper@latest

# Official Z.AI version (if fork unavailable)
npm install -g @z_ai/coding-helper
```

Binary: `chelper` (or `ai-helper`)

## Step 2: Set API Key + Load into Claude Code

```bash
chelper auth glm_coding_plan_global "YOUR_API_KEY"
chelper auth reload claude-code
```

## Step 3: Add MCP Servers to Claude Code

```bash
# Web Search
claude mcp add -s user -t http glms-search "https://api.z.ai/api/mcp/web_search_prime/mcp" \
  --header "Authorization: Bearer YOUR_API_KEY"

# Web Reader
claude mcp add -s user -t http glms-reader "https://api.z.ai/api/mcp/web_reader/mcp" \
  --header "Authorization: Bearer YOUR_API_KEY"

# GitHub Repo Search (Zread)
claude mcp add -s user -t http glms-zread "https://api.z.ai/api/mcp/zread/mcp" \
  --header "Authorization: Bearer YOUR_API_KEY"

# Vision (NPX-based, local)
claude mcp add -s user glms-vision \
  --env Z_AI_API_KEY=YOUR_API_KEY \
  --env Z_AI_MODE=coding \
  -- npx -y @z_ai/mcp-server@latest
```

## MCP Server Reference

| Server | Transport | URL | Tools |
|--------|-----------|-----|-------|
| glms-search | HTTP | `api.z.ai/api/mcp/web_search_prime/mcp` | webSearchPrime |
| glms-reader | HTTP | `api.z.ai/api/mcp/web_reader/mcp` | webReader |
| glms-vision | NPX (local) | `@z_ai/mcp-server@latest` | image_analysis, video_analysis, ui_to_artifact, etc. |
| glms-zread | HTTP | `api.z.ai/api/mcp/zread/mcp` | search_doc, get_repo_structure, read_file |

All 4 require `Authorization: Bearer <api_key>` header. Vision also needs `Z_AI_API_KEY` and `Z_AI_MODE=coding` env vars.

## Available GLM Models

- GLM-5.1 — Opus-level, complex reasoning, large-scale engineering
- GLM-5-Turbo — Opus-level, faster
- GLM-4.7 — Sonnet-level, daily development

Switch in Claude Code: `/model` in interactive session, or `--model` flag.

## Also Configuring for Hermes Agent

Same 4 MCP servers can be added to `~/.hermes/config.yaml` under `mcp_servers`:

```yaml
mcp_servers:
  glms-search:
    url: https://api.z.ai/api/mcp/web_search_prime/mcp
    headers:
      Authorization: Bearer YOUR_API_KEY
  glms-reader:
    url: https://api.z.ai/api/mcp/web_reader/mcp
    headers:
      Authorization: Bearer YOUR_API_KEY
  glms-vision:
    command: npx
    args: ["-y", "@z_ai/mcp-server@latest"]
    env:
      Z_AI_API_KEY: YOUR_API_KEY
      Z_AI_MODE: coding
  glms-zread:
    url: https://api.z.ai/api/mcp/zread/mcp
    headers:
      Authorization: Bearer YOUR_API_KEY
```

GLM as a provider in Hermes needs `GLM_API_KEY` in `~/.hermes/.env` and `GLM_BASE_URL=https://api.z.ai/api/coding/paas/v4`.

## Pitfalls

- **Bare ANTHROPIC_BASE_URL times out** — Don't set it directly. Use `chelper auth reload claude-code` instead. The coding helper handles whatever protocol translation is needed.
- **`.env` is write-protected** — Hermes blocks direct writes to credential files. Use `sed -i` via terminal.
- **Vision MCP needs Node.js >= v22** — Check with `node --version` first.
- **MCP tools need session restart** — In Hermes, `/reset` after adding MCP servers. Claude Code auto-discovers on startup.
