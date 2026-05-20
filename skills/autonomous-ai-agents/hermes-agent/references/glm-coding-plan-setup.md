# GLM Coding Plan — Hermes Setup

Z.AI DevPack (GLM Coding Plan) provides 4 MCP servers + a coding-optimized API
endpoint for GLM models (GLM-4.7, GLM-5.1, GLM-5-Turbo).

Docs: https://docs.z.ai/devpack/overview

## Quick Setup

```bash
# 1. Set env vars in ~/.hermes/.env (use terminal — .env is write-protected)
GLM_API_KEY=<your-key>
GLM_BASE_URL=https://api.z.ai/api/coding/paas/v4  # CRITICAL: coding endpoint, NOT /api/paas/v4

# 2. Add MCP servers to ~/.hermes/config.yaml under mcp_servers:
```

### MCP Server Config

```yaml
mcp_servers:
  glms-search:                          # Web Search — remote HTTP
    url: https://api.z.ai/api/mcp/web_search_prime/mcp
    headers:
      Authorization: Bearer <api_key>

  glms-reader:                          # Web Reader — remote HTTP
    url: https://api.z.ai/api/mcp/web_reader/mcp
    headers:
      Authorization: Bearer <api_key>

  glms-vision:                          # Vision — LOCAL NPX (requires Node.js >= v22)
    command: npx
    args: ["-y", "@z_ai/mcp-server@latest"]
    env:
      Z_AI_API_KEY: <api_key>           # NOTE: uses Z_AI_API_KEY, not Bearer auth
      Z_AI_MODE: coding

  glms-zread:                           # Zread (GitHub repo search) — remote HTTP
    url: https://api.z.ai/api/mcp/zread/mcp
    headers:
      Authorization: Bearer <api_key>
```

## Tool Capabilities

| Server | Tools | Transport | Notes |
|--------|-------|-----------|-------|
| glms-search | web search, real-time info (news, stocks, weather) | Remote HTTP | No local install needed |
| glms-reader | full page extraction, structured data | Remote HTTP | API docs, repos, articles |
| glms-vision | image analysis, video understanding (GLM-4.6V) | Local NPX | Node >= v22 required |
| glms-zread | repo search, file read, repo structure | Remote HTTP | Powered by zread.ai |

## Pitfalls

- **GLM_BASE_URL must use coding endpoint** — `https://api.z.ai/api/coding/paas/v4` not `https://api.z.ai/api/paas/v4`. The standard endpoint won't accept Coding Plan keys.
- **Vision MCP needs `Z_AI_API_KEY` env var**, not the `Authorization` header pattern used by the HTTP servers.
- **Vision MCP is local (NPX/stdin)**, not remote HTTP. It spawns as `npx @z_ai/mcp-server@latest` subprocess.
- **`.env` is write-protected** — use terminal `sed` or `echo >>` to edit, not `write_file` or `patch`.
- **Tool names are prefixed**: `mcp_glms_search_*`, `mcp_glms_reader_*`, `mcp_glms_vision_*`, `mcp_glms_zread_*`
- **Model discovery**: GLM models (glm-5.1, glm-4.7, etc.) are available via the built-in `zai` provider once `GLM_API_KEY` is set. Switch with `/model glm-5.1` in-session.

## Verification

```bash
# Check MCP server status
hermes mcp list

# Test API key
curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer $GLM_API_KEY" \
  "https://api.z.ai/api/coding/paas/v4/models"
# Expected: 200

# After config changes, restart gateway
hermes gateway restart
# Then /reset in session to pick up MCP tool discovery
```
