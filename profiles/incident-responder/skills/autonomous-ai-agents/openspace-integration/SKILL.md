---
name: openspace-integration
description: Integrate OpenSpace with Hermes as an MCP server for skill evolution and task delegation. OpenSpace provides autonomous task execution, skill auto-evolution, and cloud community skill sharing.
---

# OpenSpace Integration for Hermes

Integrate OpenSpace (HKUDS) as an MCP server with Hermes Agent, enabling skill evolution, cloud community access, and complex task delegation.

## When to use

- You need to delegate complex tasks beyond Hermes' current capabilities
- You want access to OpenSpace's skill evolution and cloud community
- You need to search, upload, or fix skills across local/cloud registries
- User provides an OpenSpace API key and asks to connect

## Prerequisites

1. **OpenSpace API key** from https://open-space.cloud/profile
2. **Python 3.12+** (OpenSpace requires 3.12)
3. **Hermes Agent** with MCP support

## Steps

### 1. Clone OpenSpace repository (optional, for reference)
```bash
git clone https://github.com/HKUDS/OpenSpace.git /tmp/OpenSpace
cd /tmp/OpenSpace
```

### 2. Install OpenSpace package
```bash
cd /tmp/OpenSpace
python3.12 -m pip install --break-system-packages -e .
```
**Note:** On Debian/Ubuntu systems with externally-managed Python, you must use `--break-system-packages` or create a virtual environment.

### 3. Copy essential host skills to Hermes
```bash
cp -r /tmp/OpenSpace/openspace/host_skills/delegate-task ~/.hermes/hermes-agent/skills/
cp -r /tmp/OpenSpace/openspace/host_skills/skill-discovery ~/.hermes/hermes-agent/skills/
```

### 4. Add OpenSpace as MCP server to Hermes
```bash
yes | hermes mcp add openspace \
  --command openspace-mcp \
  --env "OPENSPACE_API_KEY=sk-your-key-here" \
  --env "OPENSPACE_HOST_SKILL_DIRS=/home/ubuntu/.hermes/hermes-agent/skills" \
  --env "OPENSPACE_WORKSPACE=/tmp/OpenSpace"
```

**Why `yes |`?** Hermes MCP setup is interactive and asks whether to enable the discovered tools. Piping `yes` auto-accepts enabling all 4 OpenSpace tools in non-interactive sessions.

**Environment variables:**
- `OPENSPACE_API_KEY`: Your API key from open-space.cloud
- `OPENSPACE_HOST_SKILL_DIRS`: Path to Hermes skills directory
- `OPENSPACE_WORKSPACE`: Path to OpenSpace repository (optional)

### 5. Enable all tools
If you do not use `yes |`, when prompted `Enable all 4 tools? [Y/n/select]:`, press Enter or type `y`.

## Available Tools

Once integrated, Hermes gains 4 OpenSpace MCP tools:

1. **`execute_task`** - Delegate complex tasks to OpenSpace's full grounding engine
2. **`search_skills`** - Search skills across local registry and cloud community
3. **`fix_skill`** - Manually fix broken skills (the only manual intervention point)
4. **`upload_skill`** - Upload evolved skills to the cloud

## Verification

1. Check installation and importability:
```bash
which openspace-mcp  # Should return /home/ubuntu/.local/bin/openspace-mcp
openspace-mcp --help 2>&1 | head -20
python3 - <<'PY'
try:
    import openspace
    print('openspace import OK', getattr(openspace, '__file__', ''))
except Exception as e:
    print(type(e).__name__ + ': ' + str(e))
PY
```

If `which openspace-mcp` succeeds but `openspace-mcp --help` or `import openspace` returns `ModuleNotFoundError: No module named 'openspace'`, the console script exists but the Python package is missing from the runtime environment. Reinstall with the same Python environment used by the console script (or remove/re-add the MCP server after installing):
```bash
python3.12 -m pip install --break-system-packages -e /tmp/OpenSpace
# then restart Hermes/gateway so MCP discovery reruns
hermes gateway restart
```

2. Verify API key works at the known live endpoints:
```bash
# Health endpoint
curl -s -H "X-API-Key: sk-your-key" https://open-space.cloud/api/v1/health

# Cloud skill search endpoint
curl -s -H "X-API-Key: sk-your-key" \
  -H "Content-Type: application/json" \
  -d '{"query":"python","limit":3}' \
  https://open-space.cloud/api/v1/records/embeddings/search

# Metadata listing endpoint
curl -s -H "X-API-Key: sk-your-key" \
  'https://open-space.cloud/api/v1/records/metadata?limit=3'
```

**Important:** During live testing, generic endpoints like `/api/v1/profile`, `/api/v1/me`, `/api/v1/user`, and `/api/v1/docs` returned `404 Not Found`. Do not use those to validate the API key.

3. List configured MCP servers:
```bash
hermes mcp list
```

## Pitfalls

- **Python version mismatch**: OpenSpace requires Python 3.12+. Use `python3.12` explicitly.
- **Externally-managed environment**: Debian/Ubuntu systems may require `--break-system-packages` flag.
- **API endpoint changes**: The default API base is `https://open-space.cloud/api/v1`. If self-hosting, adjust `OPENSPACE_API_BASE`.
- **MCP connection timeout**: If `openspace-mcp` fails to start, check Python dependencies and environment variables.
- **Package disappears after /tmp cleanup**: The OpenSpace repo is typically cloned to `/tmp/OpenSpace`, which gets wiped on reboot or by tmpwatch. The `openspace-mcp` binary at `~/.local/bin/openspace-mcp` survives, but the underlying Python package is referenced via the editable install and vanishes. Symptom: `hermes mcp list` shows "✓ enabled" but the server fails to start with `ModuleNotFoundError: No module named 'openspace'`.

### Recovery when the package disappears

**Symptoms:** `openspace-mcp --help` prints `ModuleNotFoundError: No module named 'openspace'`. `python3 -c "import openspace"` also fails. `hermes mcp list` shows "enabled" but the server is dead at runtime.

**Recovery (3 commands):**
```bash
# 1. Re-clone (repo was in /tmp, wiped by reboot or cleanup)
git clone https://github.com/HKUDS/OpenSpace.git /tmp/OpenSpace

# 2. Reinstall
cd /tmp/OpenSpace && python3.12 -m pip install --break-system-packages -e .

# 3. Fix the workspace path if it drifted (common: config still points to old path like /tmp/OpenSpace-test)
hermes config set mcp_servers.openspace.env.OPENSPACE_WORKSPACE /tmp/OpenSpace

# 4. Verify
openspace-mcp --help      # should print usage, not ModuleNotFoundError
hermes mcp test openspace  # should show ✓ Connected + 4 tools
```

**Permanent fix:** Clone to a non-tmp location (e.g. `~/.hermes/openspace/`) so it survives reboots. Then update the config workspace path:
```bash
git clone https://github.com/HKUDS/OpenSpace.git ~/.hermes/openspace/
cd ~/.hermes/openspace && python3.12 -m pip install --break-system-packages -e .
hermes config set mcp_servers.openspace.env.OPENSPACE_WORKSPACE /home/ubuntu/.hermes/openspace
```

## Cloud Community Access

With a valid `OPENSPACE_API_KEY`, you get:
- Skill search across community repository
- Skill upload/download
- Access to evolved skills from other users

## Related Skills

- `delegate-task` (OpenSpace host skill) - Teaches when and how to delegate to OpenSpace
- `skill-discovery` (OpenSpace host skill) - Enables skill search
- `native-mcp` - Using Hermes' built-in MCP client