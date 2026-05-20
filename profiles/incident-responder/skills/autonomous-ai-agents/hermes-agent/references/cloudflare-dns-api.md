# Cloudflare Tunnel — Adding Subdomains via API

## Quick Pattern

When a Cloudflare API token is available, create DNS CNAME records programmatically:

```python
import urllib.request, json

token = "<cf-token>"
zone_id = "<zone-id>"  # from GET /zones?name=domain.tld
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

data = {
    "type": "CNAME",
    "name": "subdomain",   # e.g. "kanban" -> kanban.humangood.ai
    "content": "<tunnel-id>.cfargotunnel.com",
    "ttl": 1,              # Auto TTL
    "proxied": True        # Orange cloud — routes through CF network
}

req = urllib.request.Request(
    f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records",
    data=json.dumps(data).encode(),
    headers=headers,
    method="POST"
)
resp = urllib.request.urlopen(req)
```

## Prerequisites

1. Cloudflare API token with Zone:DNS:Edit permission
2. Cloudflare Tunnel already configured in `~/.cloudflared/config.yml`:
   ```yaml
   tunnel: <tunnel-uuid>
   ingress:
     - hostname: subdomain.example.com
       service: http://127.0.0.1:<local-port>
   ```
3. Tunnel running: `systemctl --user status cloudflared`

## Common Pitfalls

- The Dashboard's Host-header check rejects external domains — must use `--insecure` flag:
  ```bash
  hermes dashboard --port 9119 --host 0.0.0.0 --insecure --no-open &
  ```
- DNS propagation for proxied (orange cloud) records is instant
- Token must be scoped to the specific zone or `All zones`
