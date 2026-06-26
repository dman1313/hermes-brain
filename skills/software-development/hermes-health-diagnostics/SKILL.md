---
name: hermes-health-diagnostics
description: Systematic approach to diagnosing Hermes Agent health issues - comprehensive checks for gateway, platform connectivity, cron jobs, and system status
version: 2.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, diagnostics, health, monitoring, troubleshooting]
    related_skills: [hermes-agent]
---

# Hermes Health Diagnostics

Systematic approach to diagnosing Hermes Agent health issues. Use this skill when running health checks, troubleshooting connectivity problems, or monitoring system status.

## Quick Health Check

```bash
# Run the built-in diagnostic script (located in ~/.hermes/scripts/)
python3 ~/.hermes/scripts/agent_health_diagnostic.py

# Check gateway process
ps aux | grep "gateway run" | grep -v grep

# Check system resources
free -h  # Memory usage
swapon --show  # Swap usage — high swap indicates memory pressure even if free looks OK
df -h /home/ubuntu  # Disk usage
ps aux | wc -l  # Process count
uptime  # Load average

# Verify logs are actively being written (not stale)
tail -3 ~/.hermes/logs/agent.log

# Quick cron job output check — fastest way to verify recent job health
ls -lt ~/.hermes/cron/output/*/ 2>/dev/null | head -10

# Use hermes doctor
hermes doctor
hermes doctor --fix  # Attempt automatic fixes

# Check non-Hermes systemd services (dashboards, tunnels, etc.)
systemctl list-units --type=service --state=running | head -20
```

## Comprehensive Diagnostic Workflow

### 1. Core System Checks

**Gateway Process:**
```bash
ps aux | grep "gateway run" | grep -v grep
```
Expected: Python process running gateway

> **Note:** The gateway may run as a foreground process (e.g., via `hermes gateway run --replace`) even when `systemctl --user status hermes-gateway` shows inactive. Trust the actual process over systemd status when they disagree.

**Gateway Port Discovery (critical — port changes on restart):**
The Hermes gateway auto-generates a port on startup with `--replace`. The port from a previous run is NOT preserved. Always discover the current port rather than assuming a remembered value:

```bash
# Find the actual port the gateway is listening on
ss -tlnp | grep python | grep -v "8787\|5000\|8766"
# 8787 = webUI, 5000 = other services, 8766 = Agent Ready — filter these out

# Alternatively, grep the gateway process's listening fd
ss -tlnp | grep "$(pgrep -f 'gateway run' | head -1)"
```

The gateway health endpoint lives at `http://localhost:<PORT>/health`. Test it:
```bash
GW_PORT=$(ss -tlnp | grep "$(pgrep -f 'gateway run' | head -1)" | awk '{print $4}' | cut -d: -f2 | head -1)
curl -s http://localhost:$GW_PORT/health
# Expected: {"status": "ok", "platform": "hermes-agent"}
```

**System Resources:**
```bash
date && uptime
```
Check time synchronization and system load

### 2. Log Analysis

Check multiple log sources (gateway may log to different files):

```bash
# Recent gateway activity (may be in agent.log)
tail -50 ~/.hermes/logs/agent.log | grep -i "gateway\|telegram\|discord"

# Gateway-specific log (may be stale)
tail -20 ~/.hermes/logs/gateway.log

# Error logs — CHECK THIS EVEN IF agent.log LOOKS CLEAN
# Historical cron failures often accumulate here while current gateway logs stay clean
tail -50 ~/.hermes/logs/errors.log

# Historical errors (last 100 lines with error/fail/warn)
find ~/.hermes/logs -name "*.log" -type f -exec tail -100 {} \; 2>/dev/null | grep -i "error\|fail\|warn" | head -20
```

**Key log patterns to look for:**
- ✅ "Connected to Telegram" - Telegram working
- ✅ "Gateway running with X platform(s)" - Gateway active
- ⚠️ "Command exceeds maximum size (8000)" - Discord sync issue (commonly affects the 'skill' command group)
- ⚠️ "HTTP status 400, error code 50035" - Discord command structure issue (often related to 8000-character limit)
- ⚠️ "Unauthorized user: [ID] ([Name]) on telegram" - Telegram allowlist configuration needed
- ⚠️ "Shard ID None has successfully RESUMED session" - Discord reconnecting after network hiccups (non-critical if infrequent)
- ❌ "Timed out" - Network/connectivity issues
- 📅 Check timestamps - ensure logs are recent (not stale)

### 3. Platform Connectivity Verification

**Telegram:**
- Look for "Connected to Telegram (polling mode)" in logs
- Check for recent "Flushing text batch" messages (user activity)
- Quick verification of recent Telegram activity:
  ```bash
  grep -iE "telegram|flushing text batch|response ready" ~/.hermes/logs/agent.log | tail -15
  ```
  Expect to see inbound messages, response-ready lines, and "Sending response" entries with today's timestamps.

**Discord:**
- Look for command sync errors (8000-character limit common)
- Note: Discord may connect even with sync errors
- Session resumes (`Shard ID None has successfully RESUMED session`) indicate transient reconnects — quantify frequency to determine if it's concerning:
  ```bash
  grep -nE "Shard ID None has successfully RESUMED session" ~/.hermes/logs/agent.log | tail -20
  ```
  If resumes occur more than once per hour consistently, investigate network stability or gateway memory pressure. Count total occurrences to gauge severity: `grep -c "RESUMED session" ~/.hermes/logs/agent.log`.

### 4. Service Status Commands

```bash
# Gateway service status (if installed as service)
hermes gateway status

# Cron job health (important: gateway can be healthy while automations are failing)
hermes cron list | cat  # pipe to cat avoids less pager in cron/shell context

# Session store health
hermes sessions stats
```

**Non-Hermes Services (dashboards, tunnels, custom apps):**

```bash
# List all running systemd services
systemctl list-units --type=service --state=running

# Check a specific service (e.g., openclaw-dashboard, cloudflared-bot, etc.)
systemctl status <service-name> --no-pager -l 2>/dev/null

# Query service logs for errors in the last 24 hours
journalctl -u <service-name> --since "24 hours ago" --no-pager | grep -iE "error|timeout|fail|critical" | tail -20

# Check web-accessible services with curl
curl -s -o /dev/null -w "%{http_code}" http://localhost:<port>/  # HTTP status check
time curl -s -o /dev/null http://localhost:<port>/  # Also check response time (hang check)
```

### 5. Distinguish Current Health vs Historical Failures

A common trap: the built-in diagnostic script may report `All systems operational` even when some cron jobs still show failed last runs from earlier model/provider misconfiguration.

Use these checks together:

```bash
# Current infrastructure health
python3 ~/.hermes/scripts/agent_health_diagnostic.py
hermes gateway status

# Historical job health / last-run state
hermes cron list

# Definitive recent gateway connectivity evidence
# Prefer agent.log lines around the latest gateway restart; journalctl can include echoed tool commands.
grep -nE "Connected to Telegram|Connected as Hermes|Gateway running with|Synced [0-9]+ slash command" ~/.hermes/logs/agent.log | tail -20
```

Interpretation:
- If the diagnostic script is green **and** gateway/platform logs show recent Telegram/Discord connection, core infrastructure is healthy now.
- If `hermes cron list` still shows `last_status=error` / `error: Agent completed but produced empty response`, inspect `agent.log` around each job's `last_run_at` timestamp to find the real cause.
- Treat stale failed cron runs as a **job reliability issue**, not necessarily a live gateway outage.

### 6. Green Script Deep Dive Validation

When the built-in diagnostic script reports `All systems operational`, run this exact ordered checklist to surface hidden issues:

```bash
# 1. Confirm errors.log isn't hiding historical cron failures
date && tail -10 ~/.hermes/logs/errors.log

# 2. Check cron jobs for failed last runs
hermes cron list

# 3. Confirm cron jobs are actually producing session files today
ls -la ~/.hermes/sessions/session_cron_* 2>/dev/null | tail -5

# 4. Verify gateway is actively logging (not stale)
tail -3 ~/.hermes/logs/agent.log

# 5. Check system resources including swap
free -h && swapon --show && uptime

# 6. Verify Telegram has processed recent messages
grep -iE "telegram|flushing text batch|response ready" ~/.hermes/logs/agent.log | tail -10

# 7. Quantify Discord reconnect frequency
grep -nE "Shard ID None has successfully RESUMED session" ~/.hermes/logs/agent.log | tail -10
```

If any step surfaces errors, warnings, or stale timestamps, investigate the corresponding subsystem even though the diagnostic script is green.

## Common Issues & Solutions

### API Server (api_server) Platform Fails to Start ("API_SERVER_KEY is required")

**Symptom:** Logs show repeated `[Api_Server] Refusing to start: API_SERVER_KEY is required for the API server` errors every ~5 minutes, but `API_SERVER_KEY` is correctly set in `~/.hermes/.env`.

**CRITICAL FIRST STEP — check if the api_server is ACTUALLY down right now:**
```bash
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8642/health
```
If this returns `200`, the api_server is **running** and the errors are from a previous process — skip to issue resolution below.

**Root cause:** This is a **process-lifecycle mismatch**, not an env var misconfiguration. The error logs are from a **previous** gateway process that had a stale environment or import-order issue. When the gateway restarts (via systemd auto-restart or manual `hermes gateway restart`), the new process loads `.env` correctly and the api_server starts fine.

**Diagnosis — distinguish current vs historical:**
```bash
# 1. Check when the running gateway started (compare with log error timestamps)
ps -o pid,lstart,cmd --pid "$(pgrep -f 'gateway run' | head -1)"

# 2. Check when the LAST error occurred in logs
grep "API_SERVER_KEY is required" ~/.hermes/logs/gateway.log | tail -3

# 3. If the current process started AFTER the last error, the issue is already resolved
# Verify: the api_server should be running now
curl -s http://127.0.0.1:8642/health

# 4. Check for gateway restarts around the error window
journalctl --user -u hermes-gateway --since "10 minutes ago" --no-pager | grep -iE "started|stopped"
```

**Why it happens:**
- In rare cases, the import chain in `gateway/run.py` can have a race where `gateway/config.py`'s `os.getenv("API_SERVER_KEY", "")` reads an empty value before `load_hermes_dotenv()` has populated `os.environ`.
- This is a transient startup condition that self-resolves on the next gateway restart.
- Once `.env` is loaded, the config properly reads the key and the `APIServerAdapter` constructor receives it via `config.platforms[Platform.API_SERVER].extra["key"]`.

**Fix:**
```bash
# The current solution: just restart the gateway
hermes gateway restart
# Wait ~60s for restart backoff
sleep 60
# Verify
curl -s http://127.0.0.1:8642/health
```

**Why NOT to chase a config fix:** The `.env` file is correctly formatted and contains the key. Systemd service definition doesn't need to `EnvironmentFile` the `.env` because Hermes loads it at import time via `load_hermes_dotenv()`. This is not a config problem — it's a transient process lifecycle issue that a restart resolves.

**Health check reporting guidance:** When the health monitor shows this error, always verify the CURRENT gateway process start time against the error timestamp. Report "historical" vs "active" so the operator doesn't chase ghosts.

### Discord Command Sync Failure
**Symptom:** "Command exceeds maximum size (8000)" in logs OR "HTTP status 400, error code 50035"
**Cause:** Discord API limits total command descriptions to 8000 characters. Commonly affects the 'skill' command group which aggregates many skill-related commands.
**Error Code 50035:** Usually indicates malformed request data (invalid command names, descriptions too long, or invalid options). Often appears alongside "Command exceeds maximum size (8000)" warnings.
**Impact:** Slash commands may not sync, but gateway still runs and responds to mentions. Note: This error may appear in logs even when Discord platform is not actively running.
**Fix:** 
1. Check command name/description length limits (Discord total limit: 8000 characters for all commands combined)
2. Verify command structure follows Discord API requirements
3. Consider reducing command count or implementing command grouping
4. Check for special characters or invalid formatting in command names
5. If Discord not needed, the error is non-critical but indicates configuration may need cleanup
6. For the 'skill' command group specifically: consider splitting into subcommands or reducing descriptions
7. **Common cause**: The 'skill' command group aggregates many skill-related subcommands, often exceeding the 8000-character limit. This is a known limitation that doesn't affect core functionality.

### Stale Gateway Logs
**Symptom:** `gateway.log` not updated recently
**Cause:** Gateway may be logging to `agent.log` after restarts
**Diagnosis:** Check `agent.log` for recent gateway activity
**Fix:** No action needed - check both log files

### Telegram Authorization Issues
**Symptom:** "Unauthorized user: [ID] ([Name]) on telegram" warnings in logs
**Cause:** User not listed in `TELEGRAM_ALLOWED_USERS` environment variable
**Impact:** User messages are rejected, gateway remains functional for authorized users
**Fix:** 
1. Add user ID to `TELEGRAM_ALLOWED_USERS` in `.env` file (comma-separated)
2. Or set `GATEWAY_ALLOW_ALL_USERS=true` for open access (less secure)
3. Restart gateway after configuration changes

**Example configuration:**
```
TELEGRAM_ALLOWED_USERS=7824646153,1234567890
# OR for open access:
GATEWAY_ALLOW_ALL_USERS=true
```

### Gateway Process Dead
**Symptom:** No gateway process in `ps aux`
**Fix:**
```bash
hermes gateway restart
# Or start manually:
hermes gateway run --replace
```

### Diagnostic Script Shows Extra Gateway PID
**Symptom:** The health script reports multiple gateway PIDs, but `systemctl --user status hermes-gateway` shows only one real main process.
**Cause:** Grep-based process matching can accidentally include the diagnostic shell itself or a transient subprocess whose command line contains `gateway run --replace`.
**Impact:** Cosmetic false positive in the PID count; not usually a real duplicate gateway.
**Diagnosis:** Trust the systemd main PID first, then confirm with a stricter process check if needed.
**Fix:**
1. Check `hermes gateway status` for the service `Main PID`
2. Confirm the actual long-lived process command line matches the gateway
3. Ignore extra transient shell PIDs unless multiple long-lived Python gateway processes are present

### Gateway Health Endpoint Not Accessible
**Symptom:** `curl http://localhost:8080/health` returns no response
**Cause:** Gateway health endpoint may not be enabled by default. The gateway runs but doesn't expose an HTTP health endpoint unless explicitly configured. The diagnostic script may check for this endpoint but it's not a standard feature.
**Impact:** Cannot check gateway health via HTTP endpoint - this is expected behavior
**Fix:** This is expected behavior unless health endpoint is explicitly configured. Use process checks instead:
```bash
ps aux | grep "gateway run" | grep -v grep
systemctl --user status hermes-gateway  # If running as service
```

### Session Message Counts: Fastest Diagnostic Signal

When a cron job shows `last_status: error`, the quickest diagnosis is examining the session file's message count — specifically whether the model produced any assistant responses.

```bash
# Quick check: count messages in the latest cron session
python3 -c "
import json, glob, os
sessions = sorted(glob.glob(os.path.expanduser('~/.hermes/sessions/session_cron_<job_id>_*.json')))
if not sessions:
    print('No session files found')
else:
    latest = sessions[-1]
    d = json.load(open(latest))
    msgs = d.get('messages', [])
    user_msgs = [m for m in msgs if m.get('role') == 'user']
    asst_msgs = [m for m in msgs if m.get('role') == 'assistant']
    print(f'Session: {os.path.basename(latest)}')
    print(f'Total msgs: {len(msgs)}, User: {len(user_msgs)}, Asst: {len(asst_msgs)}')
    print(f'Model: {d.get(\"model\",\"?\")}, Provider/URL: {d.get(\"base_url\",\"?\")}')
"
```

**Key signal: 1 message total = model never responded.** If the session has exactly 1 user message (the skill injection + prompt) and 0 assistant messages, the model silently failed to generate any response. This is fundamentally different from a session where the model responded but hit errors during tool execution (those will have 10+ messages).

**Compare with working sessions** — if earlier sessions for the same job show 60+ messages with the same prompt but a different model, the model switch is the root cause:

```bash
# Compare working vs failed sessions at a glance
python3 -c "
import json, glob, os
sessions = sorted(glob.glob(os.path.expanduser('~/.hermes/sessions/session_cron_<job_id>_*.json')))
for f in sessions[-6:]:
    d = json.load(open(f))
    msgs = d.get('messages', [])
    asst = len([m for m in msgs if m.get('role') == 'assistant'])
    model = d.get('model', '?')
    print(f'{os.path.basename(f)}: {asst} asst msgs, model={model}')
"
```

**Pattern:** If older sessions have 25+ assistant messages (working) and recent sessions have 0 (dead), the model or provider change is the culprit. No need to parse log files — the session metadata tells the whole story.

**Common root causes for 0-assistant sessions:**
1. **Model switch** — a model was changed on the cron job that can't handle the context (e.g., ~15K char skill injection + system prompt + memory + tool definitions exceeds the model's effective capacity)
2. **Provider auth failure** — API key expired or provider returned an unrecoverable auth error
3. **Context overflow** — the combined system prompt + memory + skill injection is too large for the model

**Fix:** Switch the cron job's model/provider to one proven to work. To find a working model, check the last successful session's model and use the same one. For skill-heavy cron jobs with 10K+ char injections, GLM 5.1 (ZAI) and DeepSeek V4 (1M ctx) are proven reliable.

### Cron Jobs Failing While Gateway Looks Healthy
**Symptom:** `hermes cron list` shows jobs with `error: Agent completed but produced empty response`, while gateway, Telegram, and Discord all look healthy.

**Important false-green case:** Hermes cron may mark a run `ok` even when the job's delivered markdown response is only `API call failed after 3 retries: HTTP 429...` or another model/provider failure string. Do not trust `last_status: ok` alone for scheduled monitor jobs. Always inspect the latest human-readable output file in `~/.hermes/cron/output/<job_id>/` and grep recent logs for that `cron_<job_id>_<timestamp>` session.

```bash
# Fast check for false-green cron failures
latest=$(ls -t ~/.hermes/cron/output/<job_id>/*.md 2>/dev/null | head -1)
echo "$latest"
grep -nEi "API call failed|HTTP 429|HTTP 5..|usage limit|rate limit|empty response|Traceback|Exception" "$latest" ~/.hermes/logs/agent.log ~/.hermes/logs/errors.log 2>/dev/null | tail -30

# If cron list says ok but the output contains API/model failure text,
# report it as a job/provider reliability issue, not as healthy.
```

**Common underlying causes:**
1. Unsupported model override such as `codex-mini-latest` when using OpenAI Codex via ChatGPT-account auth
2. Provider/model parameter mismatch, especially `invalid temperature: only 0.6 is allowed for this model`

**Diagnosis:**
```bash
# List job status and last-run errors
hermes cron list | cat  # pipe to cat to avoid less pager in non-interactive context

# Quickest check: read the per-job markdown output files
# Each cron run writes a readable .md report to ~/.hermes/cron/output/<job_id>/
# This is faster and more readable than parsing session JSONs
ls -lt ~/.hermes/cron/output/*/ 2>/dev/null | head -20

# Job status when hermes cron list fails or times out — read raw registry
python3 -m json.tool ~/.hermes/cron/jobs.json 2>/dev/null | head -100

# Quick check: are cron jobs actually producing session files today?
ls -la ~/.hermes/sessions/session_cron_* 2>/dev/null | tail -10

# Recent cron/model errors (check BOTH agent.log and errors.log)
grep -nE "codex-mini-latest|invalid temperature|only 0.6 is allowed|Agent completed but produced empty response" ~/.hermes/logs/agent.log ~/.hermes/logs/errors.log

# Count total occurrences of a specific error to gauge severity
grep -c "codex-mini-latest" ~/.hermes/logs/errors.log

# Determine if errors are historical or active: compare error timestamps with last gateway restart
grep "2026-04-19" ~/.hermes/logs/errors.log | tail -10
grep -E "Gateway running|gateway run" ~/.hermes/logs/agent.log | tail -5

# Inspect the cron registry for job IDs, prompts, schedule, and last-run timestamps
python3 -m json.tool ~/.hermes/cron/jobs.json | less

# Inspect the exact failed cron session to see which model/base_url actually ran
python3 -m json.tool ~/.hermes/sessions/session_cron_<job_id>_<YYYYMMDD_HHMMSS>.json | less

# Most reliable: inspect the request dump captured for the failed run
python3 -m json.tool ~/.hermes/sessions/request_dump_cron_<job_id>_<timestamp>_*.json | less
```

> **Tip:** `errors.log` often accumulates cron failures even when `agent.log` looks clean after a gateway restart. Always check `errors.log` timestamps against the last restart to distinguish resolved issues from active ones. Correlate failing job IDs (e.g., `cron_233d2e3c4fbe`) with `hermes cron list` names to identify which automations are affected.

**Important nuance:** `~/.hermes/cron/jobs.json` may show `model: null` for a job even when the actual failed run used a routed/default model. In practice, the authoritative evidence is the failed session JSON plus `request_dump_cron_*`, which reveals the real model, base_url, and provider error returned at runtime.

**Impact:** Automations silently fail even though interactive gateway messaging still works.

**Fix:**
1. Pin failing cron jobs to a supported model (for ChatGPT-account Codex auth, use a supported model such as `gpt-5.4` rather than `codex-mini-latest`)
2. For Kimi/Coding-family jobs, set `temperature: 0.6` if required by that model
3. Re-run or monitor the affected jobs after updating model/temperature settings
4. Treat gateway/platform health and cron health as separate checks in reports

### Cron Job Is "Active" But Never Fires
**Symptom:** `hermes cron list` shows a job as active/scheduled, but its `next_run_at` is already in the past, `last_run_at` is still `null` (or stale), and there is no matching `session_cron_*` file or recent `cron.scheduler: Running job ...` log entry.

**Common cause:** The job was created or modified after the gateway/scheduler started, and the running scheduler did not pick up the new cron registry state. This can happen even while all core health checks are green.

**Diagnosis:**
```bash
# Check for overdue jobs
hermes cron list

# Compare cron registry update time with gateway start time
python3 - <<'PY'
import json, os
p=os.path.expanduser('~/.hermes/cron/jobs.json')
with open(p) as f:
    data=json.load(f)
print(data.get('updated_at'))
PY
systemctl --user show hermes-gateway --property=ActiveEnterTimestamp --value

# Look for a session or scheduler log for the missed job
find ~/.hermes/sessions -name 'session_cron_<job_id>_*'
grep -n "cron.scheduler: Running job" ~/.hermes/logs/agent.log | tail -50
```

**Interpretation:**
- If `jobs.json` was updated after the gateway started, and the job is overdue with no session/log evidence, suspect a stale scheduler rather than a model/provider failure.
- If other jobs around the same time executed normally, the problem may be limited to recently added jobs.
- **Always check `next_run_at` against the current time first.** A `null` `last_run_at` is expected if the job's scheduled time for today has not yet arrived. Do not flag it as missed until `next_run_at` is in the past.

**Fix:**
1. Restart or reload the Hermes gateway / cron scheduler so it re-reads the cron registry
2. Manually run the affected job once to verify it now executes
3. Check other newly created jobs from the same batch, because they may also be silently skipped
4. In health reports, distinguish "job missed by scheduler" from "job ran and failed"

## Health Report Structure

When reporting health status, use this standardized format:

```
## SYSTEM STATUS: [HEALTHY/WARNING/CRITICAL]

**Core Components:**
1. Gateway Process: ✅/❌ [PID/details]  
2. API Keys: ✅/❌ [provider]

**Platform Connectivity:**
1. Telegram: ✅/⚠️/❌ [connection status]
2. Discord: ✅/⚠️/❌ [sync status]

**System Resources:**
- Uptime: [hours/minutes]
- Load Average: [1min, 5min, 15min]
- Time Sync: ✅/❌ [current date/time]

**Recent Activity:**
- [Last user interaction from logs]
- [Last gateway restart timestamp]
- [Recent cron job executions]
- [Historical errors found (if any)]

**Issues Identified:**
- [Specific problem 1]
- [Specific problem 2]

**Recommendations:**
- [Actionable fix 1]
- [Actionable fix 2]
```

## Automated Health Monitoring

### Cron Job Iteration Limits

**Symptom:** Health check cron jobs fail with "You've reached the maximum number of tool-calling iterations allowed."

**Cause:** The comprehensive diagnostic workflow uses many tool calls (log greps, process checks, resource checks). When run as a cron job with a tool-call limit, deep dives can exceed the budget.

**Fix:**
1. **Keep cron health checks concise** — use the built-in script plus 2-3 targeted checks, not the full deep-dive workflow
2. **Prioritize checks** — if limited by iterations, check: (1) diagnostic script, (2) `hermes cron list`, (3) `errors.log` tail
3. **Save deep dives for manual runs** — the full "Green Script Deep Dive" should be run interactively, not as a scheduled cron job
4. **Use `execute_code` for batch checks** — combine multiple shell commands into a single Python script to reduce tool call count

### Cron Job Setup
```bash
# Schedule health checks every 6 hours
hermes cron create "0 */6 * * *" \
  --prompt "Run comprehensive Hermes health diagnostic and report status" \
  --skills hermes-health-diagnostics \
  --name "Hermes Health Monitor"
```

### Efficient Health Check Script

For comprehensive checks in a single execution, use this `execute_code` approach:

```python
from hermes_tools import terminal
import json

# Run comprehensive health check
checks = []

# 1. Check disk space
result = terminal("df -h /")
checks.append(("Disk Space", "OK" if "Use%" in result["output"] and int(result["output"].split("Use%")[1].split()[0].replace("%", "")) < 80 else "WARNING", result["output"].strip()))

# 2. Check memory
result = terminal("free -h")
checks.append(("Memory", "OK" if "available" in result["output"] and "Gi" in result["output"] else "WARNING", result["output"].split('\\n')[1].strip()))

# 3. Check load average
result = terminal("uptime")
load = result["output"].split("load average:")[1].strip()
load_vals = [float(x.strip()) for x in load.split(",")]
checks.append(("Load Average", "OK" if all(x < 1.0 for x in load_vals) else "WARNING", load))

# 4. Check gateway process
result = terminal("ps aux | grep -E 'gateway run' | grep -v grep | wc -l")
gateway_count = int(result["output"].strip())
checks.append(("Gateway Process", "OK" if gateway_count >= 1 else "ERROR", f"{gateway_count} gateway processes"))

# 5. Run built-in diagnostic script
result = terminal("python3 ~/.hermes/scripts/agent_health_diagnostic.py")
checks.append(("Diagnostic Script", "OK" if "All systems operational" in result["output"] else "WARNING", result["output"].strip()))

# Print results
print("🔍 AGENT HEALTH DIAGNOSTIC REPORT")
print("=" * 50)

error_count = sum(1 for _, status, _ in checks if status == "ERROR")
warning_count = sum(1 for _, status, _ in checks if status == "WARNING")

for name, status, details in checks:
    icon = "✅" if status == "OK" else "⚠️" if status == "WARNING" else "❌"
    print(f"{icon} {name}: {status}")
    print(f"   {details}")
    print()

print("=" * 50)
print(f"Summary: {len(checks)} checks, {error_count} errors, {warning_count} warnings")

if error_count == 0 and warning_count == 0:
    print("✅ All systems operational - Agent is healthy!")
elif error_count == 0:
    print("⚠️  Some warnings detected but system is operational")
else:
    print("❌ Errors detected - System needs attention")
```

**Thresholds for healthy system:**
- Load average: < 1.0 for all periods (1min, 5min, 15min)
- Disk usage: < 80% (adjust based on total disk size)
- Memory: > 500MB available
- Gateway processes: ≥ 1 running process

**When disk exceeds 80%:** Load the `mrclean` skill and follow `references/vps-disk-cleanup.md` for systematic cleanup. Key targets in order: `~/.npm/_npx/` (1-3GB, NOT cleared by npm cache clean), pnpm store prune, unused packages in `~/.hermes/node/lib/node_modules/` (verify no systemd service references first), old venvs, .rustup if unused, Docker prune, journal vacuum.

## Troubleshooting Flowchart

1. **Gateway not responding?**
   → Check `ps aux | grep "gateway run"`
   → If missing: `hermes gateway restart`

2. **Telegram not receiving messages?**
   → Check logs for "Connected to Telegram"
   → Check user allowlist configuration

3. **Discord commands not appearing?**
   → Check for 8000-character limit error
   → Commands may still work via mentions
   → Consider reducing command count

4. **Cron jobs failing silently?**
   → `hermes cron list`
   → Check `errors.log` for model/provider failures
   → Pin jobs to known-working models

## Best Practices

1. **Regular Monitoring**: Set up cron jobs for automated health checks
2. **Log Retention**: Keep at least 7 days of logs for troubleshooting
3. **Documentation**: Record recurring issues and their solutions
4. **Proactive Checks**: Run diagnostics before critical tasks
5. **Status Page**: Consider creating a simple status dashboard for multi-agent systems

## Related Resources

- `hermes-agent` skill: Comprehensive Hermes guide
- Hermes docs: https://hermes-agent.nousresearch.com/docs/