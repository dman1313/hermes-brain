# Cloudflare Tunnel Deployment

Deploy micro-SaaS projects behind Cloudflare Tunnel on custom subdomains — no Zeabur needed.

## When to Use This Instead of Zeabur

- You already have a Cloudflare Tunnel running on the VPS
- You want a subdomain of an existing domain (e.g., `app.humangood.ai`)
- You don't need Zeabur's auto-scaling/Https/cron features
- Quick iteration — edit code, restart Flask, no git push cycle

## Setup

### 1. Add to tunnel config (`~/.cloudflared/config.yml`)

```yaml
ingress:
  - hostname: app.humangood.ai
    service: http://127.0.0.1:8766
  - service: http_status:404
```

### 2. Restart tunnel

```bash
pkill -f "cloudflared.*config.*run"
/usr/local/bin/cloudflared tunnel --config ~/.cloudflared/config.yml run &
```

### 3. Add DNS CNAME in Cloudflare dashboard

| Field | Value |
|-------|-------|
| Type | CNAME |
| Name | `app` |
| Target | `humangood.ai` |
| Proxy | Orange cloud (proxied) |

### 4. Open firewall port

```bash
sudo ufw allow 8766/tcp
```

## Multi-Service Tunneling

One tunnel can serve multiple services on different subdomains:

```yaml
ingress:
  - hostname: humangood.ai
    service: http://127.0.0.1:5000       # Main landing page
  - hostname: app.humangood.ai
    service: http://127.0.0.1:8766       # SaaS product
  - hostname: workspace.humangood.ai
    service: http://127.0.0.1:8787       # Hermes WebUI
  - hostname: agent.humangood.ai
    service: ws://127.0.0.1:18789        # WebSocket agent
  - service: http_status:404
```

## Pitfalls

- DNS CNAME records must be added manually in Cloudflare dashboard — cloudflared doesn't auto-create them
- The tunnel process must be restarted after config changes
- Port conflicts: check `fuser <port>/tcp` before starting new services
- Vary header on HTML only: setting `Vary: Accept` on static files fragments CDN caching
