---
name: cloudflare-tunnel-setup
description: Expose local services to the internet via Cloudflare Tunnel — named tunnels with custom domains, using API tokens or dashboard credentials.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [cloudflare, tunnel, networking, service-exposure, dns]
    category: devops
---

# Cloudflare Tunnel Setup

Expose a local service (on `127.0.0.1:PORT`) to the internet via a permanent Cloudflare Tunnel with a custom domain.

## Prerequisites

- Cloudflare account with a domain managed on Cloudflare
- `cloudflared` installed (`/usr/local/bin/cloudflared`)
- The local service running and reachable on localhost

## Quick tunnel (testing only)

For a temporary URL (changes on restart):

```bash
cloudflared tunnel --url http://127.0.0.1:PORT --no-autoupdate
```

Creates a `*.trycloudflare.com` URL. Use only for testing — the URL is random and not permanent.

## Permanent named tunnel via API token

### Step 1: Create API token

Go to https://dash.cloudflare.com/profile/api-tokens → Create Custom Token:

| Setting | Value |
|---|---|
| Permissions | **Account** → **Cloudflare Tunnel** → **Edit** |
| | **Zone** → **DNS** → **Edit** |
| Account Resources | Your account |
| Zone Resources | Your domain |

**Common pitfall — wrong token type:** `cfut_` tokens that lack `Cloudflare Tunnel:Edit` permission fail with "Authentication error" on tunnel API calls. The token must have both tunnel and DNS permissions. Verify with:

```bash
curl -s "https://api.cloudflare.com/client/v4/user/tokens/verify" \
  -H "Authorization: Bearer <TOKEN>"
```

### Step 2: Get account and zone IDs

```bash
# Account ID
curl -s "https://api.cloudflare.com/client/v4/accounts" \
  -H "Authorization: Bearer <TOKEN>" | python3 -m json.tool

# Zone ID
curl -s "https://api.cloudflare.com/client/v4/zones?name=example.com" \
  -H "Authorization: Bearer <TOKEN>" | python3 -m json.tool
```

### Step 3: Create the tunnel

```bash
curl -s -X POST \
  "https://api.cloudflare.com/client/v4/accounts/<ACCOUNT_ID>/cfd_tunnel" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"name":"<tunnel-name>","config_src":"cloudflare"}'
```

Save the response — it contains `TunnelID` and `TunnelSecret` for the credentials file.

### Step 4: Create credentials file

Save as `~/.cloudflared/<tunnel-name>.json`:

```json
{
  "AccountTag": "<AccountTag from response>",
  "TunnelID": "<TunnelID from response>",
  "TunnelName": "<tunnel-name>",
  "TunnelSecret": "<TunnelSecret from response>"
}
```

### Step 5: Create cloudflared config

Save as `~/.cloudflared/config.yml`:

```yaml
tunnel: <TunnelID>
credentials-file: /home/ubuntu/.cloudflared/<tunnel-name>.json

ingress:
  - hostname: subdomain.example.com
    service: http://127.0.0.1:PORT
  - service: http_status:404
```

### Step 6: Create DNS record

If a CNAME already exists for the subdomain, PATCH it; otherwise POST:

```bash
# Check existing
curl -s "https://api.cloudflare.com/client/v4/zones/<ZONE_ID>/dns_records?name=subdomain.example.com" \
  -H "Authorization: Bearer <TOKEN>"

# Create or update CNAME pointing to tunnel
curl -s -X PATCH \
  "https://api.cloudflare.com/client/v4/zones/<ZONE_ID>/dns_records/<RECORD_ID>" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"type":"CNAME","name":"subdomain","content":"<TunnelID>.cfargotunnel.com","proxied":true}'
```

### Step 7: Install systemd service

```ini
[Unit]
Description=Cloudflare Tunnel for <service-name>
After=network.target <your-service>.service
Requires=<your-service>.service

[Service]
Type=simple
User=ubuntu
Group=ubuntu
ExecStart=/usr/local/bin/cloudflared tunnel --config /home/ubuntu/.cloudflared/config.yml run
Restart=always
RestartSec=10
KillSignal=SIGTERM
TimeoutStopSec=20

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable <tunnel-service>
sudo systemctl start <tunnel-service>
```

### Step 8: Verify

Start with HEAD (fast, low bandwidth):

```bash
curl -sI https://subdomain.example.com
```

If that returns `501` or empty output, fall back to GET:

```bash
curl -sv https://subdomain.example.com/ 2>&1 | tail -20
```

Look for `HTTP/2 302` or `HTTP/2 200` with `server: cloudflare` and a `cf-ray` header. Some backends (e.g. Hermes WebUI, custom Python HTTP servers) reject HEAD — a 501 here does NOT mean the tunnel is broken.

## Pitfalls

1. **DNS record already exists:** If you get error 81053, the CNAME already exists. Use PATCH on the existing record instead of POST.

2. **Quick tunnel URL changes:** `trycloudflare.com` URLs are random per start. For permanent URLs, use a named tunnel.

3. **Token permissions:** `cfut_` tokens without `Cloudflare Tunnel:Edit` silently fail. Create a custom token with explicit tunnel permissions.

4. **Browser login won't work headless:** `cloudflared tunnel login` opens a browser. On headless servers, use API tokens instead.

5. **Tunnel shows connected but returns 1033:** The tunnel registered but can't reach the local service. Check that the service is bound to `127.0.0.1:PORT` and responding.

6. **Self-signed cert warning:** Cloudflare provides its own SSL certificate. Ignore local self-signed cert issues — only Cloudflare's edge cert matters.

7. **WebSocket services need `ws://` not `http://` in ingress.** When tunneling a WebSocket server (e.g., OpenClaw Gateway), use `service: ws://127.0.0.1:18789` in the ingress rule, not `http://`. This tells cloudflared to upgrade the connection properly. Clients connect with `wss://subdomain.example.com`.

8. **Caddy/Nginx reverse proxy breaks some WebSocket auth.** OpenClaw Gateway inspects `X-Forwarded-For` and rejects proxied connections as unauthorized even with `trustedProxies` configured. Cloudflare Tunnel avoids this issue entirely because the gateway sees the connection as local (loopback).

9. **`cloudflared tunnel route dns` fails without `cert.pem`.** The command requires an origin certificate at `~/.cloudflared/cert.pem`. If one doesn't exist, you get: `ERR Cannot determine default origin certificate path. No file cert.pem in [...]`. Workarounds:
   - **Fastest: Add CNAME via Cloudflare Dashboard.** Go to DNS → Add Record → Type: `CNAME`, Name: `subdomain`, Target: `domain.com`, Proxy: 🟠 Proxied. This works when the tunnel already manages the parent domain via ingress rules — Cloudflare routes matching traffic to registered tunnels. Verify with `curl -sI https://subdomain.domain.com`.
   - **Generate cert via Cloudflare Dashboard:** SSL/TLS → Origin Server → Create Certificate → save as `~/.cloudflared/cert.pem`, then `cloudflared tunnel route dns` works.
   - **Use the API directly with curl:** Bypass the CLI and call `POST/PATCH /zones/<ZONE_ID>/dns_records` with the API token (see Step 6).
   - **If DNS already points to Cloudflare (proxied):** Adding the hostname to the tunnel ingress config is sufficient — no `route dns` needed. Test with `curl -sI https://yourdomain.com`.

10. **`curl -sI` returns 501 but tunnel is fine.** Some backends reject HEAD — Hermes WebUI and many custom Python HTTP servers return `501 Unsupported method ('HEAD')`. This does NOT mean the tunnel is broken. Verify with a GET request instead: `curl -sv https://subdomain.example.com/ 2>&1 | tail -20` and look for `server: cloudflare` + `cf-ray`.

11. **SIGHUP does NOT reload ingress config.** `kill -HUP` on cloudflared may not pick up new hostname entries added to `config.yml`. Always do a full restart when changing ingress rules:
    ```bash
    # Kill ALL config tunnel instances (there may be duplicates)
    sudo pkill -f "cloudflared tunnel --config.*config.yml"
    sleep 2
    # Start fresh
    sudo cloudflared tunnel --config /home/ubuntu/.cloudflared/config.yml run &
    ```
    A SIGHUP-only reload that returns 502 is the telltale sign you need a full restart.

12. **Multiple cloudflared instances accumulate.** Over time, restarts and manual runs can leave zombie cloudflared processes, including separate quick tunnels (`--url http://...`) running alongside the config tunnel. Before starting a fresh config tunnel, kill them all:\n    ```bash\n    ps aux | grep cloudflared | grep -v grep\n    sudo pkill cloudflared\n    sleep 2\n    # Then start the config tunnel fresh\n    sudo cloudflared tunnel --config /home/ubuntu/.cloudflared/config.yml run &\n    ```\n\n13. **Some hostnames return 200 while others return 404 after ingress changes.** After adding or modifying ingress rules and restarting the tunnel, Cloudflare edge may cache the old routing for some hostnames longer than others. If `workspace.example.com` works but `hermes.example.com` returns 404 despite identical tunnel config, wait 30-60 seconds and retry. If the issue persists:\n    - Verify the hostname resolves to Cloudflare IPs (`dig +short hostname.example.com`)\n    - Confirm there are no conflicting Page Rules, Worker Routes, or WAF rules in Cloudflare Dashboard\n    - Check that the DNS record exists and is proxied (orange cloud), not DNS-only (gray cloud)\n    - Test directly against localhost with the hostname header to confirm the backend accepts it\n    - As a workaround, use an alternate hostname that is known to work

14. **`cert.pem` exists but is corrupted.** Even if the file is present, `cloudflared tunnel route dns` may fail with `Error decoding origin cert: missing token in the certificate`. This means the cert file is incomplete or was not generated properly. Generate a fresh one from Cloudflare Dashboard (SSL/TLS → Origin Server → Create Certificate), or fall back to creating DNS records via the API token or Dashboard directly.

## Reference files

- `references/add-hostname-existing-tunnel.md` — Fastest path: add a hostname to an already-running tunnel, including a recipe for deploying a static site from a GitHub repo behind a subdomain.

## Service file locations

- `~/.cloudflared/config.yml` — main configuration
- `~/.cloudflared/<tunnel-name>.json` — tunnel credentials
- `/etc/systemd/system/<tunnel-service>.service` — systemd unit
