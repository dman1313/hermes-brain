---
name: openclaw-gateway-setup
description: Install and configure OpenClaw Gateway for remote agent access via WebSocket. Covers ACP backend registration, auth, Cloudflare tunnel exposure, and device pairing approval.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [openclaw, gateway, websocket, remote-agent, aionui, acp]
    category: devops
    related_skills: [cloudflare-tunnel-setup, hermes-agent]
---

# OpenClaw Gateway Setup

Run an OpenClaw Gateway on a VPS to expose Hermes Agent (or any ACP harness) as a remote agent accessible from AionUi, OpenClaw apps, or any WebSocket client.

## Architecture

> **⚠️ SUPERSEDED on this system (humangood.ai).** The OpenClaw Gateway (port 18789) has been replaced by the native **Hermes Gateway** (`hermes gateway run --replace`, port 8642). The Hermes gateway provides equivalent ACP/WSS functionality and is the active remote-agent endpoint at `wss://agent.humangood.ai`. This skill remains for reference on systems still running OpenClaw.

```
AionUi (client device)
  → wss://agent.example.com (Cloudflare Tunnel)
  → Hermes Gateway (127.0.0.1:8642)   ← CURRENT
  → hermes acp (ACP subprocess)
  → Full Hermes Agent
```

### Legacy (OpenClaw) Architecture

```
AionUi (client device)
  → wss://agent.example.com (Cloudflare Tunnel)
  → OpenClaw Gateway (127.0.0.1:18789)   ← DEPRECATED
  → hermes acp (ACP subprocess)
  → Full Hermes Agent
```

## Installation

```bash
# Install OpenClaw CLI
curl -fsSL https://openclaw.ai/install.sh | bash

# Verify
openclaw --version
```

## Configuration

### Step 1: Create config file

Save as `~/.openclaw/openclaw.json`:

```json
{
  "gateway": {
    "mode": "local",
    "port": 18789,
    "bind": "loopback",
    "trustedProxies": ["127.0.0.1"]
  },
  "acp": {
    "enabled": true,
    "dispatch": { "enabled": true },
    "backend": "acpx",
    "defaultAgent": "hermes",
    "allowedAgents": ["hermes"],
    "maxConcurrentSessions": 4
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

### Step 2: Install as systemd service

```bash
openclaw gateway install --port 18789
```

This creates `~/.config/systemd/user/openclaw-gateway.service`.

### Step 3: Verify

```bash
openclaw gateway status
# Should show: running, port 18789, connectivity probe: ok
```

## Authentication

**Critical pitfall:** The gateway regenerates its auth token if the config is missing the `meta` field or if the `auth` block is reformatted. Always read the actual token from the config file after any restart:

```bash
python3 -c "import json; d=json.load(open('$HOME/.openclaw/openclaw.json')); print(d['gateway']['auth']['token'])"
```

Do NOT assume the token you wrote is the token the gateway loaded.

## Cloudflare Tunnel Exposure

**Do NOT use Caddy/Nginx as a reverse proxy** for the OpenClaw Gateway WebSocket. The gateway inspects `X-Forwarded-For` headers and rejects proxied connections from "untrusted" addresses, even with `trustedProxies` configured. Cloudflare Tunnel avoids this entirely because the gateway sees loopback connections.

Add to `~/.cloudflared/config.yml`:

```yaml
ingress:
  # ... existing rules ...
  - hostname: agent.example.com
    service: ws://127.0.0.1:18789
  - service: http_status:404
```

Create DNS via Cloudflare API:

```bash
curl -s -X POST "https://api.cloudflare.com/client/v4/zones/<ZONE_ID>/dns_records" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"type":"CNAME","name":"agent","content":"<TUNNEL_ID>.cfargotunnel.com","proxied":true}'
```

Then restart the tunnel service.

## Device Pairing Approval

Remote clients (AionUi) must be paired before they can connect. The pairing flow:

1. Client connects with token → gateway returns "pairing required"
2. Agent admin must approve the device via WebSocket RPC
3. Client retries and connects successfully

### Approve via Python script

```python
import json, asyncio, websockets

TOKEN = "<gateway-auth-token>"
URI = "ws://127.0.0.1:18789"

async def approve(request_id):
    async with websockets.connect(URI, additional_headers={"Authorization": f"Bearer {TOKEN}"}) as ws:
        # Connect with protocol v3
        await ws.send(json.dumps({
            "type": "req", "id": "c1", "method": "connect",
            "params": {
                "role": "operator", "auth": {"token": TOKEN},
                "client": {"id": "gateway-client", "platform": "linux", "mode": "backend", "version": "1.0.0"},
                "minProtocol": 3, "maxProtocol": 3,
                "scopes": ["operator", "operator.admin"]
            }
        }))
        for _ in range(3):
            resp = await asyncio.wait_for(ws.recv(), timeout=5)
            r = json.loads(resp)
            if r.get("ok"): break

        # List pending (drains health event first)
        try: await asyncio.wait_for(ws.recv(), timeout=2)
        except: pass
        await ws.send(json.dumps({"type": "req", "id": "l1", "method": "device.pair.list", "params": {}}))
        resp = await asyncio.wait_for(ws.recv(), timeout=5)
        data = json.loads(resp)

        # Approve
        await ws.send(json.dumps({"type": "req", "id": "a1", "method": "device.pair.approve", "params": {"requestId": request_id}}))
        resp = await asyncio.wait_for(ws.recv(), timeout=5)
        print("Result:", resp)

asyncio.run(approve("<request-id>"))
```

### RPC Method Reference

Key methods (all require `scopes: ["operator", "operator.admin"]`):

- `device.pair.list` — list pending and paired devices
- `device.pair.approve` — approve a pending device (params: `requestId`)
- `device.pair.reject` — reject a pending device
- `device.pair.remove` — remove a paired device

### Finding the requestId

Check gateway logs:

```bash
grep "pairing required" /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log | tail -1 | \
  python3 -c "import sys,json,re; line=sys.stdin.readline(); d=json.loads(line); m=re.search(r'requestId:\s*(\S+)', d['message']); print(m.group(1).rstrip(')'))"
```

Or call `device.pair.list` and look in `result.pending[].requestId`.

## AionUi Client Configuration

In AionUi → Settings → Add Remote Agent:

- **Name:** anything (e.g., "Hermes Agent")
- **URL:** `wss://agent.example.com`
- **Authentication:** Token
- **Token:** (the gateway auth token from config)

## Pitfalls

1. **Gateway regenerates token on restart.** If you edit `~/.openclaw/openclaw.json` and the `meta` field is missing or the `auth` block structure changes, the gateway generates a new token and saves it back. Always re-read the token after restarts.

2. **Caddy/Nginx proxy breaks auth.** Even with `trustedProxies: ["127.0.0.1"]`, the gateway rejects proxied WebSocket connections. Use Cloudflare Tunnel instead.

3. **Protocol version is 3.** When connecting via WebSocket RPC, use `minProtocol: 3, maxProtocol: 3`. Version 1 will fail with "protocol mismatch".

4. **client object is validated.** The connect params `client` field requires `{id, platform, mode}` — use `"id": "gateway-client"` (it's an enum). The `scopes` field needs `["operator", "operator.admin"]` for device-pair operations.

5. **`hermes acp` must be on PATH.** The acpx plugin spawns `hermes acp` as a subprocess. Ensure `hermes` is in the PATH of the systemd service environment.

6. **Gateway logs at `/tmp/openclaw/`.** Daily rotation: `openclaw-YYYY-MM-DD.log`. Use these for debugging auth, pairing, and connection issues.

## Service Management

```bash
openclaw gateway start      # Start
openclaw gateway stop       # Stop
openclaw gateway restart    # Restart
openclaw gateway status     # Check status + connectivity probe
openclaw gateway install    # Install as systemd service
openclaw gateway uninstall  # Remove service
openclaw doctor             # Health check
```

## Complete Removal

To fully remove the OpenClaw Gateway from a system:

1. Stop the service: `openclaw gateway stop`
2. Uninstall the systemd unit: `openclaw gateway uninstall`
3. Remove all config and data: `rm -rf ~/.openclaw/`
4. Remove the Cloudflare Tunnel ingress entry for the agent hostname from `~/.cloudflared/config.yml` (or `/etc/cloudflared/config.yml` if system-level)
5. Restart the Cloudflare tunnel service (name varies — may be `cloudflared`, `hermes-tunnel`, or a custom unit)
6. Optionally remove the DNS CNAME record from Cloudflare (manual via dashboard, or API if a token is available)
7. Verify: `ss -tlnp | grep 18789` should return nothing; `openclaw gateway status` should report config as "missing"

The `openclaw` CLI itself can be left installed or removed separately: `npm uninstall -g openclaw`.

## Key Paths

- `~/.openclaw/openclaw.json` — gateway configuration
- `~/.openclaw/openclaw.json.bak` — config backup
- `~/.config/systemd/user/openclaw-gateway.service` — systemd unit
- `/tmp/openclaw/openclaw-YYYY-MM-DD.log` — daily logs

## Support Files

- `scripts/approve-device.py` — Approve pending device pairings via WebSocket RPC. Reads token from config or env `OPENCLAW_GATEWAY_TOKEN`. Use `--list` to see pending, or run without args to approve the most recent.
- `references/deployment-notes.md` — Live deployment details for VM-6 (humangood.ai tunnel, config paths, quick commands).
