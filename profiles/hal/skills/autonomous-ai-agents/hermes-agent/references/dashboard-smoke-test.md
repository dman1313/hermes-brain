# Hermes Dashboard Smoke Test

Reusable diagnostic checks for the built-in `hermes dashboard` (port 9119 default).
Run when a user says "fix the dashboard" and nothing is obviously broken.

## One-liner quick check

```bash
# Is it alive?
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:9119/ && \
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:9119/api/status
```

## Full smoke test (Python)

```python
import subprocess, re, json

# Step 1: Get the HTML and extract the session token
r = subprocess.run(['curl', '-s', 'http://127.0.0.1:9119/'], capture_output=True, text=True)
match = re.search(r'window\.__HERMES_SESSION_TOKEN__="([^"]*)"', r.stdout)
if not match:
    print("FAIL: No session token in HTML — dashboard not serving properly")
    exit(1)
token = match.group(1)
print(f"Token: {token[:12]}... ({len(token)} chars)")

# Step 2: Test public endpoints (no auth needed)
public_eps = ['/api/status', '/api/config/defaults', '/api/config/schema', 
              '/api/dashboard/themes', '/api/dashboard/plugins']
for ep in public_eps:
    code = subprocess.run(['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}',
                          f'http://127.0.0.1:9119{ep}'], capture_output=True, text=True)
    status = "OK" if code.stdout == "200" else f"FAIL ({code.stdout})"
    print(f"  {ep} -> {status}")

# Step 3: Test protected endpoints (need token)
protected_eps = ['/api/config', '/api/sessions', '/api/cron', '/api/env']
for ep in protected_eps:
    code = subprocess.run(['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}',
                          '-H', f'X-Hermes-Session-Token: {token}',
                          f'http://127.0.0.1:9119{ep}'], capture_output=True, text=True)
    status = "OK" if code.stdout == "200" else f"FAIL ({code.stdout})"
    print(f"  {ep} -> {status}")

# Step 4: Check gateway health via dashboard
r2 = subprocess.run(['curl', '-s', '-H', f'X-Hermes-Session-Token: {token}',
                     'http://127.0.0.1:9119/api/status'], capture_output=True, text=True)
status = json.loads(r2.stdout)
print(f"\nGateway running: {status.get('gateway_running')}")
print(f"Version: {status.get('version')}")
print(f"Platforms: {list(status.get('gateway_platforms', {}).keys())}")

# Step 5: Check for duplicate processes
r3 = subprocess.run(['bash', '-c', 'ps aux | grep "hermes dashboard" | grep -v grep | wc -l'],
                    capture_output=True, text=True)
count = int(r3.stdout.strip())
print(f"Dashboard processes: {count}")
if count > 1:
    print("  WARNING: multiple processes — run: hermes dashboard --stop")
elif count == 0:
    print("  WARNING: no process found — dashboard may have crashed")
else:
    print("  OK: single process")

# Step 6: Asset availability
assets = ['/assets/index-Cht-9RvV.js', '/assets/index-ut94j-Vo.css', '/favicon.ico']
for a in assets:
    code = subprocess.run(['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}',
                          f'http://127.0.0.1:9119{a}'], capture_output=True, text=True)
    status = "OK" if code.stdout == "200" else f"FAIL ({code.stdout})"
    print(f"  {a} -> {status}")
```

## Process management

```bash
# List running dashboard processes
hermes dashboard --status

# Kill all and restart
hermes dashboard --stop
hermes dashboard --port 9119 --host 127.0.0.1 --no-open &
```

## Key paths

| Path | What |
|------|------|
| `hermes_cli/web_server.py` | FastAPI server (~4000 lines) |
| `hermes_cli/web_dist/` | Built frontend assets (Vite output) |
| `web/src/lib/api.ts` | Frontend API client (auth + endpoints) |
| `hermes_cli/main.py` | `cmd_dashboard()` — CLI entry point, `_build_web_ui()` |
