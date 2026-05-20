# Add a Hostname to an Existing Cloudflare Tunnel

Fastest path when you already have a named tunnel running and just need to expose a new local service on a subdomain.

## Recipe

### 1. Ensure the local service is running

```bash
ss -tlnp | grep <PORT>
curl -sI http://127.0.0.1:<PORT>/
```

If the service isn't running yet, set it up first (systemd unit, manual start, whatever).

### 2. Add hostname to tunnel ingress config

Edit `~/.cloudflared/config.yml`. Insert the new hostname before the catch-all `http_status:404`:

```yaml
  - hostname: newsub.example.com
    service: http://127.0.0.1:<PORT>
```

### 3. Restart the tunnel (full restart, not SIGHUP)

```bash
sudo pkill cloudflared
sleep 2
sudo cloudflared tunnel --config /home/ubuntu/.cloudflared/config.yml run &
```

### 4. Create DNS record

You MUST create a CNAME record pointing `<TunnelID>.cfargotunnel.com` for the new subdomain. Options:

- **API token:** `curl -X POST …/dns_records` with `cfut_` token (see Step 6 in main skill)
- **`cloudflared tunnel route dns`:** requires a valid `~/.cloudflared/cert.pem`
- **Cloudflare Dashboard:** manually add CNAME record

### 5. Verify

```bash
curl -sI https://newsub.example.com/
```

## Common pattern: deploy a static site from a GitHub repo

```bash
# Clone
git clone <repo-url> /tmp/repo-name

# Identify deployable files (index.html, style.css, app.js, etc.)
find /tmp/repo-name -type f -not -path '*/.git/*' | grep -E '\.(html|css|js)$'

# Copy to deployment directory
sudo mkdir -p /opt/site-name
sudo cp /tmp/repo-name/index.html /tmp/repo-name/style.css /tmp/repo-name/app.js /opt/site-name/
sudo chown -R ubuntu:ubuntu /opt/site-name

# Create systemd service
sudo tee /etc/systemd/system/site-name.service > /dev/null << 'EOF'
[Unit]
Description=Static Site Server for site-name
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/site-name
ExecStart=/usr/bin/python3 -m http.server <PORT> --bind 127.0.0.1
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable site-name.service
sudo systemctl start site-name.service

# Then add hostname to tunnel (steps 2-5 above)
```
