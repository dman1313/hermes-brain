# MCP Zombie Process Recovery (June 2026)

## Symptom
20+ stale MCP subprocesses running (firecrawl-mcp, context7-mcp, scrapling) consuming ~1.4GB RAM. Each was a failed connection attempt that spawned a process that never exited.

## Root Cause
In `config.yaml`, `args` was set as a JSON string (`'["-y", "firecrawl-mcp"]'`) instead of a proper YAML list:
```yaml
# BROKEN
context7:
  command: npx
  args: '["-y", "@upstash/context7-mcp"]'  # ← JSON string, not YAML list

# FIXED
context7:
  command: npx
  args:
  - -y
  - "@upstash/context7-mcp"  # ← proper YAML list
```

Hermes' Pydantic validation rejected the JSON string with:
```
args: Input should be a valid list [type=list_type, input_value='["-y", "firecrawl-mcp"]', input_type=str]
```

But the gateway kept retrying instead of giving up permanently — each retry spawned a new process that accumulated as a zombie.

## Recovery Steps
1. Kill all zombie MCP processes:
   ```bash
   pkill -f "firecrawl-mcp"
   pkill -f "context7-mcp"  
   kill -9 $(ps aux | grep -E "firecrawl-mcp|context7-mcp" | grep -v grep | awk '{print $2}')
   ```
2. Fix the `args` format in config.yaml (via Python yaml library, not patch tool)
3. Disable broken MCP servers (`enabled: false`) until root cause is resolved
4. RAM recovered immediately (~1.4GB freed)

## Prevention
- Always write MCP server `args` as YAML list (dash-separated), never as a quoted JSON string
- Disable MCP servers that aren't currently usable rather than leaving them enabled with broken configs
- Monitor for unexpected process proliferation via `ps aux | grep npm exec`
