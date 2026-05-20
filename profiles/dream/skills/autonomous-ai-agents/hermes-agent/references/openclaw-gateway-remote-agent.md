# OpenClaw Gateway + Hermes ACP — Remote Agent Setup Reference

Session-specific notes from 2026-04-29 setup on VM-6 (43.167.176.156).

## Installed Components

- **OpenClaw CLI:** v2026.4.26 via npm (`curl -fsSL https://openclaw.ai/install.sh | bash`)
- **Binary:** `/home/ubuntu/.hermes/node/bin/openclaw`
- **Config:** `~/.openclaw/openclaw.json`
- **Logs:** `/tmp/openclaw/openclaw-YYYY-MM-DD.log`
- **Service:** `openclaw-gateway.service` (systemd user service)
- **Gateway port:** 18789 (loopback)

## Working Config (as of 2026-04-29)

```json
{
  "gateway": {
    "mode": "local",
    "port": 18789,
    "bind": "loopback",
    "auth": {
      "token": "<stored-separately>"
    }
  },
  "acp": {
    "enabled": true,
    "dispatch": { "enabled": true },
    "backend": "acpx",
    "defaultAgent": "hermes",
    "allowedAgents": ["hermes", "claude", "codex", "gemini", "opencode"],
    "maxConcurrentSessions": 4,
    "stream": {
      "coalesceIdleMs": 300,
      "maxChunkChars": 1200
    },
    "runtime": {
      "ttlMinutes": 120
    }
  },
  "plugins": {
    "entries": {
      "acpx": {
        "enabled": true,
        "config": {
          "agents": {
            "hermes": {
              "command": "hermes acp"
            }
          }
        }
      }
    }
  },
  "agents": {
    "defaults": {
      "workspace": "/home/ubuntu"
    }
  }
}
```

## Cloudflare Tunnel Integration

The tunnel `f6fdf864-d25d-4be9-b5ef-ff9ac3c21b88` runs via `hermes-tunnel.service` with config at `~/.cloudflared/config.yml`.

Ingress for OpenClaw:
```yaml
  - hostname: agent.humangood.ai
    service: ws://127.0.0.1:18789
```

DNS: `agent.humangood.ai` CNAME → `f6fdf864-d25d-4be9-b5ef-ff9ac3c21b88.cfargotunnel.com` (proxied).
**Status: DNS record still needs to be created** (requires Cloudflare API token or manual dashboard entry).

## AionUi Connection (pending DNS)

- **URL:** `wss://agent.humangood.ai`
- **Authentication:** Token
- **Token:** See gateway config `auth.token`

## Debugging Log Excerpts

### Token mismatch via Caddy proxy
When using Caddy as reverse proxy (port 18790 → 18789), the gateway logged:
```
unauthorized ... auth=none ... reason=token_mismatch
Proxy headers detected from untrusted address. Connection will not be treated as local.
Configure gateway.trustedProxies to restore local client detection behind your proxy.
```
Even after setting `trustedProxies: ["127.0.0.1"]` and removing auth entirely, the gateway still rejected connections. Root cause: OpenClaw gateway's trust model doesn't work well behind Caddy for WebSocket auth. Cloudflare Tunnel bypasses this entirely.

### Config validation: runtime.type
```
Problem: agents.list.0.runtime: Invalid input (allowed: "embedded", "persistent", "oneshot")
```
The `runtime.type` field in `agents.list` does NOT accept `"acp"`. ACP routing is configured via the top-level `acp` and `plugins.entries.acpx` sections only.

## Key Commands

```bash
openclaw gateway status --url ws://127.0.0.1:18789 --token "<token>"
openclaw gateway restart
openclaw gateway install --token "<token>" --port 18789
openclaw config get gateway.auth
tail -f /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log
```

## External References

- OpenClaw Gateway docs: https://docs.openclaw.ai/cli/gateway
- OpenClaw Remote Access: https://docs.openclaw.ai/gateway/remote
- AionUi Remote Agent PR: https://github.com/iOfficeAI/AionUi/pull/1739
- Hermes ACP harness request (closed as plugin-scoped): https://github.com/openclaw/openclaw/issues/68496
- ACP agents setup: https://docs.openclaw.ai/tools/acp-agents-setup
