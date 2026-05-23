# VPS Service Management Patterns

Reference for creating, debugging, and managing systemd services, Docker Compose stacks, and background processes on the VPS. Consolidated from the `vps-service-management` skill.

## Systemd Service Template

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

## Debugging Restart Loops

1. Check journal: `sudo journalctl -u servicename --no-pager -n 30`
2. Exit code 127: command not found — check PATH and binary path
3. Exit code 0 with `Restart=always`: process exits cleanly, restarts forever
4. Exit code 1: application error — read stderr in journal

## Node.js CLI Tools as Systemd Services

**Core problem:** Many Node.js CLI tools spawn child processes, enter menu loops, or require a TTY. They fail silently under systemd.

**Detection signs:**
- Tool has an interactive menu or prompt on startup
- Tool spawns child processes (`spawn()`, `fork()`)
- Journal shows "Exiting..." immediately after start
- Process launches then exits code 0 in a loop

**Solution: Bypass the CLI Wrapper**

1. Read the CLI source to find the actual server entry point: `grep -n 'spawn\|fork\|serverPath\|standaloneDir' cli.js`
2. Identify the server entry point — typically `app/server.js` in Next.js projects
3. Extract required environment variables (PORT, HOSTNAME, NODE_ENV, etc.)
4. Run the server directly as ExecStart
5. Set PATH explicitly so `node` and npm dependencies resolve

**Example (9Router):** The `cli.js` spawns the Next.js server as a detached child and enters an interactive menu. Fix: run the Next.js server directly:
```ini
ExecStart=/home/ubuntu/.hermes/node/bin/node /home/ubuntu/.hermes/node/lib/node_modules/9router/app/server.js
Environment=PORT=20128
Environment=HOSTNAME=0.0.0.0
Environment=NODE_ENV=production
```

## Docker Compose Management

### Starting
```bash
cd /path/to/project
sudo docker compose up -d
```

### Port Conflicts
1. Identify what's using the port: `sudo lsof -i :PORT`
2. Don't blindly kill — Caddy/nginx may be serving other apps
3. Override ports in `.env` before starting
4. Re-run `docker compose up -d`

### Health Checks
```bash
sudo docker compose ps
curl -s -o /dev/null -w "%{http_code}" http://localhost:PORT/health
```

### Persistence
Docker Compose with `restart: unless-stopped` survives reboots when Docker daemon starts. No systemd unit needed.

## Quick Checks

```bash
ss -tlnp                           # What's listening on what ports
sudo lsof -i :PORT                 # What's using a specific port
sudo systemctl status servicename  # Systemd service status
sudo docker compose -f /path/to/docker-compose.yml ps  # Docker containers
```

## Pitfalls

- **`&` in terminal foreground**: Hermes rejects foreground commands with `&`. Use `terminal(background=true)` for long-lived processes.
- **Group membership not immediate**: `sudo usermod -aG docker ubuntu` doesn't take effect until next login. Use `sudo docker` in the same session.
- **`Restart=on-failure` with exit 0**: Clean exit is NOT a failure. Use `Restart=always` for daemons.
- **Don't kill Caddy/nginx without checking**: Port 80/443/8080 are often serving other apps. Override the new service's ports instead.
