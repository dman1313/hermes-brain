---
name: vps-proxy-dashboard
description: Deploy a dark-themed Flask proxy dashboard for any local service on a VPS, with Cloudflare quick tunnel for public HTTPS access and optional Hermes integration.
version: "1.0"
---

# VPS Proxy Dashboard

Create a monitoring/proxy dashboard for any service running on localhost. Useful when you have a backend on a VPS port and want a public web UI with status, metrics, and raw proxy access.

## When to Use

- You have a service on localhost:PORT (e.g. 9119) and want a web dashboard
- You need public HTTPS access via Cloudflare quick tunnels
- You want VPS metrics (CPU, memory, disk) alongside backend status
- You want to integrate Hermes gateway status and logs (optional)
- You want to display a live Hermes agent roster — see references/hermes-agents.md

## Step 1: Check Target Port

```bash
ss -tlnp | grep <PORT>
curl -s http://127.0.0.1:<PORT> | head -5
```

## Step 2: Create Dashboard Directory

```bash
sudo mkdir -p /opt/proxy-dashboard
```

## Step 3: Write Dashboard App

**CRITICAL:** Do NOT use `write_file` tool for system paths — it fails with permission denied. Use `sudo tee` or `sudo python3 -c` instead.

```bash
sudo tee /opt/proxy-dashboard/dashboard.py > /dev/null << 'PYEOF'
from flask import Flask, Response, jsonify
import requests
import psutil
import datetime
import json
import os

app = Flask(__name__)
BACKEND = "http://127.0.0.1:<PORT>"

# If integrating Hermes, hardcode the path. Do NOT use os.path.expanduser
# when running as root via systemd — it resolves to /root/, not /home/ubuntu/
HERMES_DIR = "/home/ubuntu/.hermes"


def backend_status():
    try:
        r = requests.get(BACKEND, timeout=3)
        return {"up": True, "status": r.status_code, "content_type": r.headers.get("Content-Type", "")}
    except Exception as e:
        return {"up": False, "error": str(e)}


def hermes_status():
    try:
        with open(os.path.join(HERMES_DIR, "gateway_state.json")) as f:
            return json.load(f)
    except Exception as e:
        return {"error": str(e)}


def hermes_logs(lines=10):
    try:
        log_path = os.path.join(HERMES_DIR, "logs", "agent.log")
        with open(log_path, "r") as f:
            return "".join(f.readlines()[-lines:])
    except Exception as e:
        return f"Error reading logs: {e}"


@app.route("/")
def index():
    status = backend_status()
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    uptime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    hermes_state = hermes_status()
    hermes_log_text = hermes_logs(15)

    if status["up"]:
        backend_html = f'<span style="color:#0f0">&#9679; ONLINE</span> (HTTP {status["status"]})'
    else:
        backend_html = f'<span style="color:#f44">&#9679; OFFLINE</span> &mdash; {status.get("error", "unknown")}'

    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Proxy Dashboard :<PORT></title>
<style>
body {{ background:#0d1117; color:#c9d1d9; font-family:system-ui,sans-serif; margin:0; padding:2rem; }}
.card {{ background:#161b22; border:1px solid #30363d; border-radius:12px; padding:1.5rem; margin-bottom:1rem; max-width:800px; }}
h1 {{ color:#58a6ff; margin-top:0; }}
h2 {{ color:#79c0ff; font-size:1.1rem; margin-top:0; }}
.metric {{ display:flex; justify-content:space-between; padding:.5rem 0; border-bottom:1px solid #21262d; }}
.metric:last-child {{ border-bottom:none; }}
.value {{ color:#58a6ff; font-weight:600; }}
.btn {{ display:inline-block; background:#238636; color:#fff; padding:.5rem 1rem; border-radius:6px; text-decoration:none; margin-right:.5rem; }}
.btn:hover {{ background:#2ea043; }}
pre {{ background:#0d1117; border:1px solid #30363d; padding:1rem; border-radius:8px; overflow:auto; max-height:400px; }}
</style></head><body>
<div class="card">
<h1>Proxy Dashboard</h1>
<p>Forwards to <code>{BACKEND}</code></p>
</div>
<div class="card">
<h2>Backend Status</h2>
<p style="font-size:1.2rem">{backend_html}</p>
<a class="btn" href="/proxy">Open Backend (proxy)</a>
<a class="btn" href="/api/raw">Raw JSON</a>
</div>
<div class="card">
<h2>VPS Metrics</h2>
<div class="metric"><span>CPU Usage</span><span class="value">{psutil.cpu_percent(interval=0.5)}%</span></div>
<div class="metric"><span>Memory Used</span><span class="value">{mem.percent}% ({mem.used//(1024**2)} MB / {mem.total//(1024**2)} MB)</span></div>
<div class="metric"><span>Disk Used</span><span class="value">{disk.percent}% ({disk.used//(1024**3)} GB / {disk.total//(1024**3)} GB)</span></div>
<div class="metric"><span>Dashboard Time</span><span class="value">{uptime}</span></div>
</div>
<div class="card">
<h2>Hermes Gateway</h2>
<div class="metric"><span>State</span><span class="value">{hermes_state.get("gateway_state", "unknown")}</span></div>
<div class="metric"><span>PID</span><span class="value">{hermes_state.get("pid", "-")}</span></div>
<div class="metric"><span>Telegram</span><span class="value">{hermes_state.get("platforms", {}).get("telegram", {}).get("state", "-")}</span></div>
<div class="metric"><span>Discord</span><span class="value">{hermes_state.get("platforms", {}).get("discord", {}).get("state", "-")}</span></div>
<div class="metric"><span>Active Agents</span><span class="value">{hermes_state.get("active_agents", "-")}</span></div>
</div>
<div class="card">
<h2>Hermes Recent Logs</h2>
<pre>{hermes_log_text}</pre>
</div>
<div class="card">
<h2>Backend Response (Preview)</h2>
"""

    if status["up"]:
        try:
            r = requests.get(BACKEND, timeout=5)
            text = r.text[:2000]
            if r.headers.get("Content-Type", "").startswith("application/json"):
                try:
                    parsed = json.dumps(r.json(), indent=2)
                    html += f"<pre>{parsed}</pre>"
                except:
                    html += f"<pre>{text}</pre>"
            else:
                html += f"<pre>{text}</pre>"
        except Exception as e:
            html += f"<p style='color:#f44'>Error fetching: {e}</p>"
    else:
        html += "<p style='color:#888'>Backend is offline. Start the service on port <PORT>.</p>"

    html += """
</div>
<div style="text-align:center; color:#484f58; font-size:.85rem; margin-top:2rem;">
  Proxy Dashboard &middot; Port <PORT> &middot; <a href="/api/status" style="color:#58a6ff">JSON API</a>
</div>
</body></html>"""
    return html


@app.route("/proxy")
def proxy():
    try:
        r = requests.get(BACKEND, timeout=10)
        return Response(r.content, status=r.status_code, content_type=r.headers.get("Content-Type", "text/html"))
    except Exception as e:
        return f"<h1>Backend Error</h1><p>{e}</p>", 502


@app.route("/api/raw")
def api_raw():
    try:
        r = requests.get(BACKEND, timeout=5)
        return Response(r.content, status=r.status_code, content_type=r.headers.get("Content-Type", "application/json"))
    except Exception as e:
        return jsonify({"error": str(e)}), 502


@app.route("/api/status")
def api_status():
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    return jsonify({
        "backend": backend_status(),
        "hermes": hermes_status(),
        "cpu_percent": psutil.cpu_percent(interval=0.5),
        "memory_percent": mem.percent,
        "disk_percent": disk.percent,
        "timestamp": datetime.datetime.utcnow().isoformat()
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=<DASHBOARD_PORT>)
PYEOF
```

Replace `<PORT>` with the backend port (e.g. 9119) and `<DASHBOARD_PORT>` with the dashboard port (e.g. 9999).

## Step 4: Create systemd Service

```bash
sudo tee /etc/systemd/system/proxy-dashboard.service > /dev/null << 'EOF'
[Unit]
Description=Proxy Dashboard for :<PORT>
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/proxy-dashboard
ExecStart=/usr/bin/gunicorn --bind 0.0.0.0:<DASHBOARD_PORT> --workers 1 --timeout 30 dashboard:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable proxy-dashboard.service
sudo systemctl start proxy-dashboard.service
```

## Step 5: Cloudflare Quick Tunnel

```bash
sudo tee /etc/systemd/system/cloudflared-proxy.service > /dev/null << 'EOF'
[Unit]
Description=Cloudflare Tunnel Proxy Dashboard
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/cloudflared tunnel --url http://localhost:<DASHBOARD_PORT>
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable cloudflared-proxy.service
sudo systemctl start cloudflared-proxy.service
```

Get the public URL:
```bash
sudo journalctl -u cloudflared-proxy.service --no-pager | grep -oP 'https://[a-zA-Z0-9-]+\.trycloudflare\.com' | tail -1
```

## Quick Tunnel for an Existing Service (No Dashboard)

When you just need to expose an existing local service (e.g. Hermes WebUI on 127.0.0.1:8787) through Cloudflare — without building a proxy dashboard:

```bash
sudo tee /etc/systemd/system/<name>-tunnel.service > /dev/null << 'EOF'
[Unit]
Description=Cloudflare Tunnel for <service-name>
After=network.target <existing-service>.service
Requires=<existing-service>.service

[Service]
Type=simple
User=ubuntu
Group=ubuntu
ExecStart=/usr/local/bin/cloudflared tunnel --url http://127.0.0.1:<PORT> --no-autoupdate
Restart=always
RestartSec=10
KillSignal=SIGTERM
TimeoutStopSec=20

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable <name>-tunnel.service
sudo systemctl start <name>-tunnel.service
```

Key differences from the proxy dashboard pattern:
- No Flask/gunicorn needed — tunnels straight to the existing port
- Uses `Requires=` to ensure the main service is running before the tunnel starts
- `--no-autoupdate` avoids cloudflared auto-update issues on VPS
- The URL changes on each restart (quick tunnel limitation). Extract current URL:
  ```bash
  sudo journalctl -u <name>-tunnel.service --no-pager | grep -oP 'https://[a-zA-Z0-9-]+\.trycloudflare\.com' | tail -1
  ```

## Pitfalls & Lessons Learned

### Cloudflare Error 1033
Error 1033 means the tunnel connected to Cloudflare's edge but can't reach the local backend. Common causes:
- Local service isn't listening on 127.0.0.1:PORT yet (race condition — tunnel started before service)
- Service only listens on `0.0.0.0` but the tunnel points to `localhost` — both should work, but verify with `curl http://127.0.0.1:PORT/`
- Service redirects before serving content (e.g. 302 to /login) — this is fine, the tunnel handles redirects

Fix: check `systemctl status <service>` and `curl -v http://127.0.0.1:PORT/`, then restart the tunnel service.

### Cloudflare Quick Tunnel URLs are Ephemeral
The trycloudflare.com URL changes on every tunnel restart. For a fixed domain, use a named tunnel with Cloudflare API token authentication. Quick tunnels are fine for dev/staging but not for production URLs you share.

### File Writing to System Paths
`write_file` tool often fails with "Permission denied" for `/opt/` or `/etc/`. Always use `sudo tee` or `sudo python3 -c "open('/path','w').write(...)` for system paths.

### User Home Directory in systemd
When a service runs as `root`, `os.path.expanduser("~/.hermes")` resolves to `/root/.hermes/`, NOT `/home/ubuntu/.hermes/`. Hardcode the full path or use `os.environ.get("SUDO_USER", "ubuntu")` to construct it.

Same issue with CLI tools that read config from a user's home directory (e.g., the `gh` CLI reads `~/.config/gh/`). To run such tools from a root systemd service, use `sudo -u ubuntu <command>` so the tool finds the right config.

### Python String Manipulation Failures
Using `sed` or Python string replace on Python source code is fragile — can leave duplicate `app = Flask()` lines or break indentation. Always rewrite the full file with `tee` rather than patching in-place for code files.

### Cloudflare Quick Tunnel URLs
Quick tunnel URLs are ephemeral and change on restart. Always grep `journalctl` logs to get the current URL. Do not cache URLs across restarts.
