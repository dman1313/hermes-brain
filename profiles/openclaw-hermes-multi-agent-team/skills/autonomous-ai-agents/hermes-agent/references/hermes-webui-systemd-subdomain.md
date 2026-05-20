# Hermes WebUI systemd + subdomain deployment notes

Use this when installing `https://github.com/nesquena/hermes-webui` on a VPS where Hermes Agent already exists and the user wants access from a subdomain.

## Known-good local install shape

```bash
git clone --depth 1 https://github.com/nesquena/hermes-webui.git /home/ubuntu/hermes-webui
cd /home/ubuntu/hermes-webui
```

Create `/home/ubuntu/hermes-webui/.env` with restrictive permissions. Prefer binding to loopback and exposing only via a reverse proxy:

```env
HERMES_WEBUI_AGENT_DIR=/home/ubuntu/.hermes/hermes-agent
HERMES_WEBUI_PYTHON=/home/ubuntu/.hermes/hermes-agent/venv/bin/python
HERMES_WEBUI_HOST=127.0.0.1
HERMES_WEBUI_PORT=8787
HERMES_WEBUI_STATE_DIR=/home/ubuntu/.hermes/webui
HERMES_WEBUI_DEFAULT_WORKSPACE=/home/ubuntu
HERMES_HOME=/home/ubuntu/.hermes
HERMES_CONFIG_PATH=/home/ubuntu/.hermes/config.yaml
HERMES_WEBUI_BOT_NAME=Hermes
HERMES_WEBUI_PASSWORD=<generate-a-strong-password>
```

Generate a password without exposing it in shell history:

```bash
PW="$('/home/ubuntu/.hermes/hermes-agent/venv/bin/python' - <<'PY'
import secrets
print(secrets.token_urlsafe(24))
PY
)"
printf '%s\n' "$PW" > /home/ubuntu/.hermes/webui-password.txt
chmod 600 /home/ubuntu/.hermes/webui-password.txt
```

## systemd service

Run the server directly rather than using `bootstrap.py`; bootstrap starts a detached process and is better for interactive first-run use than managed services.

```ini
[Unit]
Description=Hermes WebUI
After=network.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/.hermes/hermes-agent
EnvironmentFile=/home/ubuntu/hermes-webui/.env
ExecStart=/home/ubuntu/.hermes/hermes-agent/venv/bin/python /home/ubuntu/hermes-webui/server.py
Restart=always
RestartSec=5
KillSignal=SIGTERM
TimeoutStopSec=20

[Install]
WantedBy=multi-user.target
```

Commands:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now hermes-webui.service
sudo systemctl status hermes-webui.service --no-pager -l
```

## Verification

```bash
systemctl is-active hermes-webui.service
curl -i --max-time 10 http://127.0.0.1:8787/health
curl -i --max-time 10 http://127.0.0.1:8787/ | sed -n '1,20p'
```

Expected:
- `/health` returns HTTP 200 with `"status": "ok"`.
- `/` returns HTTP 302 to `/login` when `HERMES_WEBUI_PASSWORD` is set.

## Subdomain via Caddy

Prerequisite: DNS A record points the subdomain to the VPS public IP.

Caddyfile snippet:

```caddyfile
hermes.example.com {
    encode gzip zstd
    reverse_proxy 127.0.0.1:8787
}
```

Then:

```bash
sudo caddy validate --config /etc/caddy/Caddyfile
sudo systemctl reload caddy
```

Caddy handles HTTPS automatically if ports 80/443 are reachable and DNS is correct.

## Subdomain via Cloudflare Tunnel

Use when the VPS cannot accept inbound connections (no open ports, behind NAT, or user prefers Cloudflare edge). Two modes:

### Quick tunnel (no Cloudflare account needed)

Immediate temporary URL on `*.trycloudflare.com`. URL changes on restart.

```bash
# One-off
cloudflared tunnel --url http://127.0.0.1:8787

# As systemd service
sudo tee /etc/systemd/system/hermes-tunnel.service << 'EOF'
[Unit]
Description=Cloudflare Tunnel for Hermes WebUI
After=network.target hermes-webui.service
Requires=hermes-webui.service

[Service]
Type=simple
User=ubuntu
Group=ubuntu
ExecStart=/usr/local/bin/cloudflared tunnel --url http://127.0.0.1:8787 --no-autoupdate
Restart=always
RestartSec=10
KillSignal=SIGTERM
TimeoutStopSec=20

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now hermes-tunnel.service
```

Find the generated URL:
```bash
sudo journalctl -u hermes-tunnel.service --no-pager -n 20 | grep trycloudflare.com
```

### Named tunnel (permanent domain, requires Cloudflare account)

Prerequisites:
- Domain on Cloudflare (zone active, DNS managed by Cloudflare)
- API token with **Account:Cloudflare Tunnel:Edit** and **Zone:DNS:Edit** permissions
- Or: tunnel created manually in Zero Trust dashboard → credentials JSON downloaded

**Pitfall — `cfut_` token without Tunnel permission:** Cloudflare API tokens with the `cfut_` prefix are valid tokens but may lack Cloudflare Tunnel:Edit permission. Verify with:
```bash
curl -s "https://api.cloudflare.com/client/v4/accounts/<account_id>/cfd_tunnel" \
  -H "Authorization: Bearer <token>" | python3 -m json.tool
```
A 401 "Authentication error" means the token lacks tunnel permission. The user must create a new token at https://dash.cloudflare.com/profile/api-tokens with `Account → Cloudflare Tunnel → Edit`.

**API-driven setup (full workflow, no dashboard needed):**

```bash
ACCOUNT_ID="5f41fa3b264101763c64cba53c7768b1"
ZONE_ID="59ff1b6bb0ceb75b2bc128c8dd57c7f9"
TOKEN="cfut_..."

# 1. Create the tunnel
curl -s -X POST \
  "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/cfd_tunnel" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"name":"hermes-webui","config_src":"cloudflare"}'

# The response includes:
#   result.id          → TUNNEL_ID (UUID)
#   result.account_tag → ACCOUNT_TAG
#   result.credentials_file.TunnelSecret → base64 secret

# 2. Save tunnel credentials JSON
cat > ~/.cloudflared/hermes-webui.json << EOF
{
  "AccountTag": "${ACCOUNT_ID}",
  "TunnelID": "<tunnel-uuid-from-response>",
  "TunnelName": "hermes-webui",
  "TunnelSecret": "<secret-from-response>"
}
EOF

# 3. Write cloudflared config
cat > ~/.cloudflared/config.yml << EOF
tunnel: <tunnel-uuid>
credentials-file: /home/ubuntu/.cloudflared/hermes-webui.json

ingress:
  - hostname: hermes.example.com
    service: http://127.0.0.1:8787
  - service: http_status:404
EOF

# 4. Check for existing DNS record, then create or update
RECORDS=$(curl -s \
  "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/dns_records?name=hermes.example.com" \
  -H "Authorization: Bearer ${TOKEN}")

# If record exists, PATCH it:
RECORD_ID=$(echo "$RECORDS" | python3 -c "import json,sys; print(json.load(sys.stdin)['result'][0]['id'])")
curl -s -X PATCH \
  "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/dns_records/${RECORD_ID}" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"type\":\"CNAME\",\"name\":\"hermes\",\"content\":\"<tunnel-uuid>.cfargotunnel.com\",\"proxied\":true}"

# If no record exists, POST a new one:
curl -s -X POST \
  "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/dns_records" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"type\":\"CNAME\",\"name\":\"hermes\",\"content\":\"<tunnel-uuid>.cfargotunnel.com\",\"proxied\":true}"

# 5. Create/replace systemd service (update if quick tunnel service already exists)
sudo tee /etc/systemd/system/hermes-tunnel.service << EOF
[Unit]
Description=Cloudflare Tunnel for Hermes WebUI (hermes.example.com)
After=network.target hermes-webui.service
Requires=hermes-webui.service

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
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now hermes-tunnel.service

# 6. Verify
curl -sI --max-time 10 https://hermes.example.com
# Expect HTTP/2 302 or 501 (HEAD not supported), server: cloudflare, cf-ray header
```

If the tunnel is created in the Zero Trust dashboard, use the tunnel token (a JSON credentials file, not the API token) with `cloudflared tunnel run --token`.

## Pitfalls

- Do not bind WebUI to `0.0.0.0` for public access unless password auth is enabled. Prefer `127.0.0.1` plus Caddy/Nginx/Cloudflare Tunnel.
- Do not paste generated WebUI passwords into durable wiki/memory/skill content. Store in a local `0600` file and tell the user the path.
- If Caddy is already serving another site, append a separate site block; validate before reload.
- `bootstrap.py` is useful for initial detection, but not ideal as `ExecStart` because it spawns `server.py` as a child process and exits after health check.
- **Quick tunnel URL instability:** `*.trycloudflare.com` URLs change on restart. For permanent URLs with a custom domain, use a named tunnel or Caddy/Nginx.
- **Cloudflared cache invalidation:** After changing the upstream service or restarting, the Cloudflare edge may cache stale 1033 errors for 3–15 minutes. Verify with `curl -v` and note the `cf-ray` header; wait or flush cache if needed.
