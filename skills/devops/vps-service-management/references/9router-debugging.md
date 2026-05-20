# 9Router Systemd Debugging Walkthrough

## Problem

9Router's `cli.js` is an interactive CLI wrapper that:
1. Calls `ensureSqliteRuntime()` to install `better-sqlite3`
2. Spawns the Next.js server as a detached child via `spawnServer()`
3. Enters an interactive menu loop (`showInterfaceMenu()`)

Under systemd, this fails because:
- No TTY available for the menu
- The process exits cleanly after starting the server (child is detached)
- `Restart=on-failure` doesn't catch clean exit, `Restart=always` creates a restart loop

## Debugging Steps

### 1. Initial failure — status 127
```
9router.service: Main process exited, code=exited, status=127
```
**Cause**: `#!/usr/bin/env node` shebang — `node` not in systemd PATH.
**Fix**: Added explicit `Environment=PATH=...` with node bin path.

### 2. Restart loop — exit code 0
```
[9router][runtime] npm install better-sqlite3@12.6.2
✓ Ready in 0ms
Exiting...
```
**Cause**: Server spawned as detached child, parent exits after menu timeout.
**Fix**: Changed to `Restart=always` — but this just restarted the loop.

### 3. Read the source
Found in `cli.js`:
```javascript
const standaloneDir = path.join(__dirname, "app");
const serverPath = path.join(standaloneDir, "server.js");
// ...
const child = spawn(RUNTIME, ["--max-old-space-size=6144", serverPath], {
  cwd: standaloneDir,
  env: {
    ...buildEnvWithRuntime(process.env),
    PORT: port.toString(),
    HOSTNAME: host
  }
});
```

### 4. Solution — run server.js directly
Bypass the interactive wrapper entirely:
```ini
ExecStart=/home/ubuntu/.hermes/node/bin/node /home/ubuntu/.hermes/node/lib/node_modules/9router/app/server.js
Environment=PORT=20128
Environment=HOSTNAME=0.0.0.0
Environment=NODE_ENV=production
```

**Result**: Server running, listening on :20128, HTTP 307 redirect to /dashboard.

## Key Takeaway

When a CLI tool spawns its server as a child process and the parent is interactive, the parent is not suitable as a systemd ExecStart. Find the underlying server entry point and run it directly with the required environment variables.
