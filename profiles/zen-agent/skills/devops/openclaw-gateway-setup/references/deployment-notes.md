# OpenClaw Gateway — Deployment Notes

## Status: REMOVED (2026-05-02)

The OpenClaw Gateway was fully removed from VM-6:
- systemd service uninstalled
- `~/.openclaw/` directory deleted
- Cloudflare Tunnel ingress entry (`agent.humangood.ai`) removed from `~/.cloudflared/config.yml`
- Port 18789 no longer in use

## Re-deployment Reference

If needed again, follow the main SKILL.md setup steps. Key historical details:

- Server: VM-6 (43.167.176.156)
- Zone: humangood.ai (zone ID 59ff1b6bb0ceb75b2bc128c8dd57c7f9)
- Tunnel ID: f6fdf864-d25d-4be9-b5ef-ff9ac3c21b88
- DNS CNAME: `agent.humangood.ai` → `f6fdf864-d25d-4be9-b5ef-ff9ac3c21b88.cfargotunnel.com` (record may still exist in CF dashboard)
- Tunnel service: `hermes-tunnel.service` (system) at `/etc/systemd/system/hermes-tunnel.service`
- ACP backend: `hermes acp`
