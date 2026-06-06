# VPS Disk Cleanup Methodology

Systematic approach for reclaiming disk space on a Linux VPS running Hermes + services.

## Phase 1: Map the terrain

```bash
# Overall usage
df -h /

# Top-level breakdown
du -sh /* 2>/dev/null | sort -rh | head -20

# Home directory breakdown (where most user data lives)
du -sh /home/ubuntu/* 2>/dev/null | sort -rh | head -20

# Hidden directories (often the biggest consumers)
du -sh /home/ubuntu/.hermes /home/ubuntu/.local /home/ubuntu/.npm /home/ubuntu/.nvm /home/ubuntu/.cargo /home/ubuntu/.rustup /home/ubuntu/.cache /home/ubuntu/.claude 2>/dev/null | sort -rh
```

## Phase 2: Identify safe targets

### Rule: ALWAYS check before deleting

Before removing ANY directory or package, verify it's not used by a running service:

```bash
# Check systemd services for references
grep -r "<package-or-path>" /etc/systemd/system/*.service 2>/dev/null

# Check if process is running
pgrep -fa "<name>" 2>/dev/null

# Check if hermes config references it
grep -r "<name>" ~/.hermes/config.yaml 2>/dev/null
```

### Safe cleanup targets (in order of typical size)

| Target | Typical Size | Command | Notes |
|--------|-------------|---------|-------|
| `~/.npm/_npx/` | 1-3 GB | `rm -rf ~/.npm/_npx` | NOT cleared by `npm cache clean --force` |
| `~/.npm/_cacache/` | 500M-1G | `npm cache clean --force` | Standard npm cache |
| `~/.cache/uv/` | 300M-1G | `uv cache clean` | Python uv package manager cache |
| `pnpm store prune` | varies | `pnpm store prune` | Removes packages not linked to any project |
| Old pnpm store versions | varies | `rm -rf ~/.local/share/pnpm/store/v3` | Old format versions alongside v10 |
| Journal logs | 100-300M | `journalctl --vacuum-size=100M` | Keeps most recent 100M |
| Rotated logs | 10-50M | `find /var/log -name "*.gz" -delete` | Old compressed logs |
| Large active logs | varies | `truncate -s 1M /var/log/syslog` | Keeps last 1M, log continues |
| `.hermes/state-snapshots/` | varies | `rm -rf` old snapshots | Check date, keep recent |
| `.npm/_logs/` | small | `rm -rf ~/.npm/_logs` | npm install logs |

### Hermes-specific cleanup

```bash
# .hermes/node/ contains global npm packages used by systemd services
# NEVER delete this directory wholesale. Check which packages are safe:
du -sh ~/.hermes/node/lib/node_modules/* | sort -rh

# For each package, verify it's not referenced by a service:
grep -r "<package-name>" /etc/systemd/system/*.service

# Safe to remove packages with NO service references
rm -rf ~/.hermes/node/lib/node_modules/<unused-package>
```

### .hermes/hermes-agent/ dual-venv check

The hermes-agent directory can accumulate both `.venv` and `venv` directories. Only one is active:

```bash
# Check which one the hermes binary points to
ls -la $(which hermes)
# Output shows: ... -> /home/ubuntu/.hermes/hermes-agent/venv/bin/hermes

# The other one is safe to remove
# Services also reference the active one - verify:
grep -r "hermes-agent/venv" /etc/systemd/system/*.service
grep -r "hermes-agent/\.venv" /etc/systemd/system/*.service
```

### Rust toolchain check

`.rustup` (1-2 GB) and `.cargo` (100-200 MB) may coexist with system rustc:

```bash
# Check if system has rustc
/usr/bin/rustc --version

# Check if any service uses .rustup or .cargo
grep -r "rustup\|cargo" /etc/systemd/system/*.service

# If neither service nor active build process needs them:
rm -rf ~/.rustup ~/.cargo
```

## Phase 3: Docker cleanup

Docker images can consume 10-20+ GB on root filesystem:

```bash
# Check total Docker usage
docker system df

# Check what's running vs stopped
docker ps -a --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"

# Safe cleanup of stopped containers and dangling images
docker system prune -f

# For specific stopped containers, remove individually
docker rm <container-name>
docker rmi <image-name>
```

**Caution**: Only remove images for containers that are intentionally stopped/abandoned. Ask user before removing production service images.

## Phase 4: Verify

```bash
df -h /
```

## Pitfalls

- **`npm cache clean --force` does NOT clear `~/.npm/_npx/`** — must be removed manually
- **`~/.hermes/node/` is used by live services** (9router, paperclipai, freellmapi) — never bulk-delete
- **`~/.cache/electron/`** may be needed by browser automation tools — verify before clearing
- **`pnpm store prune`** only removes unlinked packages — old version dirs need manual removal
- **Docker images live on root filesystem** by default — `docker system df` shows true impact
- **`truncate` on active logs** is safe (log continues writing) but loses history
- **Swap usage > 50%** signals memory pressure — don't reduce swap size during cleanup
