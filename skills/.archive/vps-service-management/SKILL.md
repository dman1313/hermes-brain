---
name: vps-service-management
description: Create and debug systemd services, Docker Compose stacks, and background processes on the VPS. Use when deploying a new tool as a persistent service, when a systemd service is failing to start or in a restart loop, when resolving port conflicts between services, or when a CLI tool needs to run headless.
---

# VPS Service Management

Patterns for deploying and debugging background services on the VPS.

## Systemd Service Creation

### Basic Template

```ini
[Unit]
Description=Service Name
After=network.target

[Service]
Type=simple
User=ubuntu
Environment=KEY=value
Environment=PATH=/home/ubuntu/.hermes/node/bin:/home/ubuntu/.local/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=/absolute/path/to/binary --flags
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=servicename

[Install]
WantedBy=multi-user.target
```

### Key Decisions

| Setting | When to Use |
|---------|-------------|
| `Restart=always` | Service should never stay down (daemons, servers) |
| `Restart=on-failure` | Service exits 0 when done (one-shot tasks) |
| `Type=simple` | Default — process stays in foreground |
| `Type=forking` | Process daemonizes itself |

### Installation

```bash
sudo cp service.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now servicename
```

## Debugging Restart Loops

When a service starts then immediately exits and restarts:

1. **Check the journal**: `sudo journalctl -u servicename --no-pager -n 30`
2. **Exit code 127**: command not found — check PATH and binary path
3. **Exit code 0 with `Restart=always`**: process exits cleanly, restarts forever
4. **Exit code 1**: application error — read stderr in journal

## Node.js CLI Tools as Systemd Services

**The core problem**: Many Node.js CLI tools are designed for interactive terminal use. They spawn child processes, enter menu loops, or require a TTY. They fail silently under systemd.

### Detection

Signs a CLI tool won't work directly under systemd:
- Tool has an interactive menu or prompt on startup
- Tool spawns child processes (`spawn()`, `fork()`)
- Journal shows "Exiting..." immediately after start
- Process launches then exits code 0 in a loop

### Solution: Bypass the CLI Wrapper

1. **Read the CLI source** to find the actual server entry point
   ```bash
   # Find what the CLI actually starts
   grep -n 'spawn\|fork\|serverPath\|standaloneDir' cli.js
   ```

2. **Identify the server entry point** — typically `app/server.js` in Next.js projects, or a `dist/server.js`

3. **Extract required environment variables** from the source (PORT, HOSTNAME, NODE_ENV, etc.)

4. **Run the server directly as the ExecStart**:
   ```ini
   ExecStart=/path/to/node /path/to/app/server.js
   Environment=PORT=XXXX
   Environment=HOSTNAME=0.0.0.0
   ```

5. **Set PATH explicitly** so `node` and npm dependencies resolve:
   ```ini
   Environment=PATH=/home/ubuntu/.hermes/node/bin:/home/ubuntu/.local/bin:/usr/local/bin:/usr/bin:/bin
   ```

### Example: 9Router

9Router's `cli.js` spawns the Next.js server as a detached child process and enters an interactive menu loop. Systemd can't handle this.

**Fix**: Run the Next.js server directly.
```ini
ExecStart=/home/ubuntu/.hermes/node/bin/node /home/ubuntu/.hermes/node/lib/node_modules/9router/app/server.js
Environment=PORT=20128
Environment=HOSTNAME=0.0.0.0
Environment=NODE_ENV=production
```

See `references/9router-debugging.md` for the full debugging walkthrough.

## Docker Compose Service Management

### Starting

```bash
cd /path/to/project
sudo docker compose up -d
```

### Port Conflicts

When a container port conflicts with a host service:

1. **Identify what's using the port**: `sudo lsof -i :PORT`
2. **Don't blindly kill** — Caddy, nginx, or other reverse proxies may be serving other apps
3. **Override ports in `.env`** before starting:
   ```bash
   APP_PORT=8088          # was 8080, conflicted with Caddy
   FRONTEND_PORT=8089     # was 80, conflicted with Caddy
   ```
4. **Re-run** `docker compose up -d`

### Health Checks

```bash
sudo docker compose ps                    # container status
curl -s -o /dev/null -w "%{http_code}" http://localhost:PORT/health
```

### Persistence

Docker Compose files with `restart: unless-stopped` survive reboots automatically when the Docker daemon starts. No systemd unit needed.

## Quick Checks

```bash
# What's listening on what ports
ss -tlnp

# What's using a specific port
sudo lsof -i :PORT

# Systemd service status
sudo systemctl status servicename

# Docker containers
sudo docker compose -f /path/to/docker-compose.yml ps
```

## Pitfalls

- **`&` in terminal foreground**: Hermes rejects foreground commands with `&`. Use `terminal(background=true)` for long-lived processes.
- **Group membership not immediate**: `sudo usermod -aG docker ubuntu` doesn't take effect until next login. Use `sudo docker` in the same session.
- **`Restart=on-failure` with exit 0**: The process exiting cleanly is NOT a failure. Use `Restart=always` for daemons.
- **Don't kill Caddy/nginx without checking**: Port 80/443/8080 are often serving other apps. Override the new service's ports instead.
