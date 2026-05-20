# 9Router Installation — VPS Reference

**Date:** 2026-05-16
**Version:** 0.4.46
**Repo:** https://github.com/decolua/9router

## Paths

| Item | Path |
|------|------|
| npm global root | `/home/ubuntu/.hermes/node/` |
| node binary | `/home/ubuntu/.hermes/node/bin/node` |
| package | `/home/ubuntu/.hermes/node/lib/node_modules/9router/` |
| CLI entry | `cli.js` (DO NOT use for systemd — interactive TUI) |
| Actual server | `app/server.js` (Next.js 16.2.1) |
| Runtime dir | `/home/ubuntu/.9router/runtime/` |
| Database | `/home/ubuntu/.9router/db/data.sqlite` (better-sqlite3) |

## Service

- **File:** `/etc/systemd/system/9router.service`
- **Port:** 20128
- **Dashboard:** `http://localhost:20128/dashboard` (redirects to `/login` for first setup)

## Debugging Journey (what we tried → what worked)

1. **First attempt:** `ExecStart=9router --no-browser` → exit 127 (node not in systemd PATH)
2. **Second attempt:** full node path + full cli.js path → npm install ran, server started, then exited 0 (CLI wrapper exited after setup)
3. **Third attempt:** changed `Restart=on-failure` → `Restart=always` → restart loop: CLI ran, spawned server, entered TUI menu, hung, killed, restarted
4. **Root cause:** cli.js uses `spawn(RUNTIME, [serverPath], {detached: true})` to start the Next.js server, then enters an interactive `showInterfaceMenu()` loop. In systemd with no TTY, this hangs.
5. **Fix:** Run `app/server.js` directly with `PORT=20128 HOSTNAME=0.0.0.0 NODE_ENV=production`

## Runtime dependency

`better-sqlite3@12.6.2` is a native module compiled at `/home/ubuntu/.9router/runtime/node_modules/`. Server won't start without it. If it goes missing:

```bash
cd /home/ubuntu/.9router/runtime
npm install better-sqlite3@12.6.2 --no-audit --no-fund --prefer-online --no-save
```
