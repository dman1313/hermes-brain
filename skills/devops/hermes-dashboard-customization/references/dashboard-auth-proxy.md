# Dashboard Auth Proxy

Cookie-based auth proxy for Hermes dashboard behind Cloudflare Tunnel.
Solves the basic-auth-SPA-loop problem.

## Why Not Basic Auth?

Caddy/nginx basic auth sends 401 with `WWW-Authenticate` header. Browser prompts for credentials, user enters them, page loads. But then the SPA makes XHR API calls — browser may not auto-send basic auth for these, OR the dashboard's own session-token 401 triggers a re-prompt. Result: infinite login loop.

## Python Auth Proxy

```python
#!/usr/bin/env python3
"""Minimal auth proxy for Hermes Dashboard."""
import http.server
import urllib.request
import urllib.error

TOKEN = "YOUR_HEX_TOKEN_HERE"  # openssl rand -hex 32
UPSTREAM = "http://127.0.0.1:9119"
PORT = 9121

LOGIN_HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Hermes Dashboard</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  body{font-family:Inter,system-ui,sans-serif;background:#f5f3ef;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0}
  .box{background:#fff;border-radius:12px;padding:40px;box-shadow:0 2px 12px rgba(0,0,0,.06);text-align:center;max-width:360px}
  h1{font-size:20px;color:#1a1816;margin:0 0 8px}
  p{font-size:14px;color:#6b6560;margin:0 0 24px}
  a{display:inline-block;background:#3d7a4f;color:#fff;padding:12px 32px;border-radius:8px;text-decoration:none;font-weight:600;font-size:14px}
  a:hover{background:#2d6a3f}
</style></head>
<body><div class="box">
  <h1>Hermes Agent</h1>
  <p>Click below to open the dashboard.</p>
  <a href="/auth">Open Dashboard</a>
</div></body></html>"""


class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if self.path == "/auth":
            self.send_response(302)
            self.send_header("Set-Cookie",
                "hermes_token=%s; Path=/; HttpOnly; SameSite=Strict; Max-Age=31536000" % TOKEN)
            self.send_header("Location", "/")
            self.end_headers()
            return

        cookie = self.headers.get("Cookie", "")
        if ("hermes_token=" + TOKEN) not in cookie:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(LOGIN_HTML.encode())
            return

        self._proxy()

    def do_POST(self):
        self._proxy()

    def do_PUT(self):
        self._proxy()

    def do_DELETE(self):
        self._proxy()

    def _proxy(self):
        url = UPSTREAM + self.path
        body = None
        if "Content-Length" in self.headers:
            body = self.rfile.read(int(self.headers["Content-Length"]))

        req = urllib.request.Request(url, data=body, method=self.command)
        for key, val in self.headers.items():
            if key.lower() not in ("host", "transfer-encoding"):
                req.add_header(key, val)

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                self.send_response(resp.status)
                for key, val in resp.getheaders():
                    if key.lower() not in ("transfer-encoding",):
                        self.send_header(key, val)
                self.end_headers()
                self.wfile.write(resp.read())
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            for key, val in e.headers.items():
                if key.lower() not in ("transfer-encoding",):
                    self.send_header(key, val)
            self.end_headers()
            if e.fp:
                self.wfile.write(e.fp.read())
        except Exception:
            self.send_response(502)
            self.end_headers()


if __name__ == "__main__":
    server = http.server.HTTPServer(("127.0.0.1", PORT), ProxyHandler)
    print("Auth proxy on :%d -> %s" % (PORT, UPSTREAM))
    server.serve_forever()
```

## Systemd Service

```ini
[Unit]
Description=Hermes Dashboard Auth Proxy
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /home/ubuntu/dashboard-auth-proxy.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

## Cloudflare Tunnel Config

```yaml
# ~/.cloudflared/config.yml
ingress:
  - hostname: hermesdash.humangood.ai
    service: http://127.0.0.1:9121  # auth proxy, NOT dashboard directly
```

## Flow

```
User → https://hermesdash.humangood.ai/
  → Cloudflare Tunnel → Auth Proxy (:9121)
  → No cookie? → Login page ("Open Dashboard" button)
  → Click → /auth sets cookie, redirects to /
  → Has cookie? → Proxy to Dashboard (:9119)
  → Dashboard serves SPA with session token embedded
  → SPA makes API calls with X-Hermes-Session-Token header
  → All requests carry cookie → proxied through
  → No loop!
```
