# Gateway Process Lifecycle Debugging

Quick reference for distinguishing current vs historical gateway issues using systemd journals and process metadata.

## Key Commands

```bash
# Current gateway PID + start time
ps -o pid,lstart,cmd --pid "$(pgrep -f 'gateway run' | grep -v grep | head -1)"

# Journal for a specific time window
journalctl --user -u hermes-gateway --since "30 minutes ago" --no-pager

# Gatewway restarts in a window
journalctl --user -u hermes-gateway --since "1 hour ago" --no-pager | grep -iE "started|stopped|starting"

# Log errors from the current process only (after PID start time)
# Use journalctl's time filter to match the current PID's lifetime
GW_START=$(ps -o lstart= --pid "$(pgrep -f 'gateway run' | grep -v grep | head -1)" 2>/dev/null)
journalctl --user -u hermes-gateway --since "$GW_START" --no-pager | grep -iE "error|fail|refusing" | tail -10

# Check if api_server is running NOW
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8642/health
```

## Common Patterns

| Observation | Interpretation |
|---|---|
| Errors in log, but `curl :8642/health` returns 200 | Stale errors from prior process — resolved |
| Errors in log, no api_server listening | Active failure — current process has the issue |
| Gateway stopped & started within same minute | systemd auto-restart after crash |
| Errors every 5 min on the dot | 300s backoff cap — retrying indefinitely |

## Timeline Reconstruction

When logs show errors but current state is healthy:

1. Get the error timestamps: `grep "some error" ~/.hermes/logs/gateway.log | tail -5`
2. Get current PID start time: `ps -o lstart= -p $(pgrep -f 'gateway run' | head -1)`
3. If errors are before PID start → resolved (gateway restarted)
4. If errors are after PID start → gateway running in degraded state

```bash
# One-liner: are errors from before or after current gateway started?
GW_PID=$(pgrep -f 'gateway run' | grep -v grep | head -1)
GW_START_EPOCH=$(ps -o etime= -p "$GW_PID" 2>/dev/null | tr -d ' ')
echo "Gateway PID=$GW_PID up for $GW_START_EPOCH"
echo "Last error:"
grep "API_SERVER_KEY is required" ~/.hermes/logs/gateway.log | tail -1
```

## Key Insight

The `api_server` platform's `connect()` method reads `extra["key"]` (from config) or falls back to `os.getenv("API_SERVER_KEY", "")`. If neither is set at init time, the platform returns `False` from connect and never retries the env check. The error is permanent for that process — only a restart fixes it.
