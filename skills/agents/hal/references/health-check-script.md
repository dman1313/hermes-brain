# Daily Brief Health Check Script Template

The `/tmp/check_procs.sh` batch pattern. Write one script, run it, read the output once. Never dump 10 sequential commands.

## Template

```bash
cat > /tmp/check_procs.sh << 'EOF'
#!/bin/bash
echo "=== DISK ==="
df -h / | tail -1
echo "=== SWAP ==="
free -h | grep -E "^(Mem|Swap):"
echo "=== SERVICES ==="
for svc in 5000 8766 9999 3001 20128 8089 3002 9121; do
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 3 http://localhost:$svc 2>/dev/null)
  echo ":$svc → $code"
done
echo "=== CRON_PROVIDER_NONE ==="
python3 -c "
import json
jobs = json.load(open('/home/ubuntu/.hermes/cron/jobs.json')).get('jobs', [])
for j in jobs:
    if not j.get('provider'):
        e = 'enabled' if j.get('enabled', True) else 'DISABLED'
        print(f\"{j['id'][:12]} | {j.get('name','?')} | {j.get('schedule','?')} | {e}\")
"
echo "=== CRON_ERRORS ==="
python3 -c "
import json
jobs = json.load(open('/home/ubuntu/.hermes/cron/jobs.json')).get('jobs', [])
for j in jobs:
    s = j.get('state', 'active')
    ls = j.get('last_status', '?')
    if s == 'paused' or ls == 'error':
        print(f\"  {j['id'][:12]} {j.get('name','?')[:40]} state={s} last_status={ls}\")
"
echo "=== SELF_IMPROVING ==="
cat ~/.hermes/skills/_metrics/self-improving-agent.json 2>/dev/null || echo "FILE NOT FOUND"
echo "=== UPDATES ==="
apt list --upgradable 2>/dev/null | grep -v "Listing..." | wc -l
echo "=== DEFAULT_PROVIDER ==="
python3 -c "
import yaml, os
cfg = yaml.safe_load(open(os.path.expanduser('~/.hermes/config.yaml')))
default = cfg.get('model', {}).get('provider', cfg.get('provider', '?'))
print(f'Default provider: {default}')
key_var = default.upper() + '_API_KEY'
print(f'{key_var} set: {bool(os.getenv(key_var))}')
"
echo "=== DONE ==="
EOF
bash /tmp/check_procs.sh
```

## Port Reference

| Port | Service | Expected |
|------|---------|----------|
| 5000 | Human Good AI landing | 200 |
| 8766 | Agent Ready | 200 |
| 9999 | Dashboard | 200 |
| 3001 | Hermes Office (3D) | 307 (redirect, normal) |
| 20128 | 9Router | 307 (redirect, normal) |
| 8089 | WeKnora | 200 |
| 3002 | FreeLLMAPI | 200 |
| 9121 | Dashboard auth proxy | 200 |

## Additions for Specific Checks

Append before `=== DONE ===`:

```bash
# Provider=None cascade detection
echo "=== PROVIDER_NONE_CASCADE ==="
python3 -c "
import json, yaml, os
jobs = json.load(open('/home/ubuntu/.hermes/cron/jobs.json')).get('jobs', [])
cfg = yaml.safe_load(open(os.path.expanduser('~/.hermes/config.yaml')))
default = cfg.get('model', {}).get('provider', cfg.get('provider', '?'))
key_var = default.upper() + '_API_KEY'
has_key = bool(os.getenv(key_var))
none_jobs = [j for j in jobs if not j.get('provider') and j.get('enabled', True)]
errors = [j for j in none_jobs if j.get('last_status') == 'error']
print(f'Provider=None jobs: {len(none_jobs)}, in error: {len(errors)}')
print(f'Default provider: {default}')
print(f'{key_var} set: {has_key}')
if errors and not has_key:
    print('CRITICAL: Provider=None cascade active — default provider has no API key')
"
```
