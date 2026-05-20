# Cloudflare Tunnel Subdomain Setup

Quick reference for adding a new subdomain to an existing Cloudflare Tunnel.

## 1. Update tunnel ingress config

```bash
# /home/ubuntu/.cloudflared/config.yml
ingress:
  - hostname: newsub.humangood.ai
    service: http://127.0.0.1:<PORT>
```

## 2. Restart the tunnel

```bash
# Kill existing tunnel process
kill $(pgrep -f "cloudflared.*config.*run")

# Start in background (preferred for Hermes)
terminal(background=true, command="/usr/local/bin/cloudflared tunnel --config /home/ubuntu/.cloudflared/config.yml run")
```

## 3. Add DNS CNAME record

**Preferred: Cloudflare API (if token is available)**

```python
import urllib.request, json

token = "<cfut_...>"  # Cloudflare API token with DNS:Edit permission
zone_id = "<zone_id>"  # From API: GET /client/v4/zones?name=humangood.ai
cname_target = "<tunnel-id>.cfargotunnel.com"  # e.g. f6fdf864-....cfargotunnel.com

data = {
    "type": "CNAME",
    "name": "newsub",
    "content": cname_target,
    "ttl": 1,
    "proxied": True
}
req = urllib.request.Request(
    f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records",
    data=json.dumps(data).encode(),
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    method="POST"
)
resp = urllib.request.urlopen(req)
result = json.loads(resp.read())
# result["success"] should be True
```

**Fallback: Manual (Cloudflare Dashboard)**

Cloudflare Dashboard → humangood.ai → DNS → Add Record:

| Field | Value |
|-------|-------|
| Type | CNAME |
| Name | `newsub` |
| Target | `<tunnel-id>.cfargotunnel.com` |
| Proxy | Orange cloud (proxied) |

**Note:** The CNAME target is the tunnel's CF address (e.g. `f6fdf864-d25d-4be9-b5ef-ff9ac3c21b88.cfargotunnel.com`), NOT the bare domain `humangood.ai`. Using the bare domain will not route through the tunnel.

## 4. Verify

```bash
curl -sI https://newsub.humangood.ai/
```

## Common pitfalls

- **`kill $(pgrep ...)` blocks** — the command runner sometimes rejects the kill. Use `fuser -k` as fallback, or just start a new tunnel process (old one dies on its own after a few seconds).
- **No cert.pem** — `cloudflared tunnel route dns` fails without it. Manual DNS is the fallback.
- **Wrong port** — double-check the service is actually running on the target port with `curl -sI http://localhost:<PORT>/`.
