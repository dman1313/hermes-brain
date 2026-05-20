---
name: dropbox-obsidian-wiki-sync
description: Manage the event-driven Dropbox sync for ~/wiki and ~/photo.news using the inotifywait watcher daemon. Also covers token repair when sync fails with auth errors.
version: 2.0.0
author: Hermes Agent
license: MIT
---

# Dropbox Obsidian Wiki Sync

Use this when the Dropbox wiki push job needs to run or when `/home/ubuntu/.local/bin/dropbox-sync.sh` fails with Dropbox auth errors.

## Paths
- Sync script: `/home/ubuntu/.local/bin/dropbox-sync.sh`
- Auth start script: `/home/ubuntu/.local/bin/dropbox-auth.py`
- Auth finish script: `/home/ubuntu/.local/bin/dropbox-finish.py`
- Token file: `/home/ubuntu/.dropbox-wiki-token`
- Local wiki dir: `/home/ubuntu/wiki`
- Dropbox target: `/Obsidian-Wiki`

## Normal run
```bash
/home/ubuntu/.local/bin/dropbox-sync.sh
```

Success ends with:
```text
Sync complete! Uploaded N file(s).
```

## Common failure: expired access token
Symptoms:
- `invalid_access_token` in refresh-token mode
- `expired_access_token` in access-token mode
- Message like `Unable to refresh access token without refresh token and app key`

Most commonly this means the token file contains only a short-lived access token instead of a refresh token, but it can also mean the stored refresh token was revoked or is otherwise unusable. Check token length/prefix before assuming the file only contains an access token.

In this environment, `.dropbox-wiki-token` values beginning with `sl.` or `sl.u.` indicate stored access tokens, not refresh tokens; once they expire, both `/home/ubuntu/.local/bin/dropbox-sync.sh` and `/home/ubuntu/.local/bin/photo-news-sync.sh` will fail until Dropbox is reauthorized.

## Reauthorize
1. Start auth flow:
```bash
python3 /home/ubuntu/.local/bin/dropbox-auth.py
```
2. Open the printed Dropbox authorization URL in a browser.
3. Log in to the intended Dropbox account and click **Allow**.
4. Copy the auth code.
5. Finish auth and save the new token:
```bash
python3 /home/ubuntu/.local/bin/dropbox-finish.py '<AUTH_CODE>'
```
6. Re-run sync:
```bash
/home/ubuntu/.local/bin/dropbox-sync.sh
```

## Notes
- `dropbox-finish.py` stores `refresh_token` if Dropbox returns one, otherwise it falls back to storing `access_token`.
- If Dropbox does not return a refresh token, future syncs will expire again and need reauthorization.
- `/home/ubuntu/.local/bin/photo-news-sync.sh` uses the same Dropbox token file and should follow the same refresh-token pattern as `dropbox-sync.sh`; if it fails with `expired_access_token`, inspect whether it still assumes access-token-only auth.
- Browser automation can reach the auth page, but if Dropbox requires login and there are no stored credentials, the flow must be completed by a human.
- **This Dropbox token now also powers full Hermes state backups.** The script `/home/ubuntu/scripts/hermes-dropbox-backup.py` (created 2026-05-11) reuses the same `/home/ubuntu/.dropbox-wiki-token` to upload a tarball of Hermes skills, config, cron, and gateway state to Dropbox `/hermes-backups/`. If the token expires, both wiki sync AND Hermes state backup will break — re-auth fixes both.

## Event-driven watcher (primary — replaces polling)

Sync is **event-driven** via `inotifywait`. A systemd service watches both directories in real time and only syncs when files actually change. No more wasted cron runs.

**Prerequisite:** `inotify-tools` package (provides `inotifywait`).

**How it works:**
- Watcher daemon: `/home/ubuntu/.local/bin/dropbox-watcher.py`
- Systemd service: `~/.config/systemd/user/dropbox-watcher.service`
- Watches: `~/wiki/` → Dropbox `/Obsidian-Wiki` and `~/photo.news/` → Dropbox `/photo.news`
- Detects: `close_write`, `create`, `delete`, `move`, `modify` events
- Debounce: waits **60 seconds** after the last change before syncing (batches rapid edits like Obsidian auto-saves)
- Skips: temp files (`*~`, `*.swp`, `*.tmp`), hidden dotfiles (except `.gitignore`), and `.git/` internals
- Log: `~/.local/log/dropbox-watcher.log`
- Design doc: `references/watcher-daemon-design.md` — architecture, design decisions, log format, installation

**Service management:**
```bash
systemctl --user status dropbox-watcher     # check status
systemctl --user restart dropbox-watcher    # restart after config changes
systemctl --user stop dropbox-watcher       # stop temporarily
journalctl --user -u dropbox-watcher -f     # tail logs
```

**Verifying sync worked:**
```bash
tail -20 ~/.local/log/dropbox-watcher.log
# Look for: ✓ wiki sync OK: Sync complete! Uploaded N file(s).
```

**Systemd config details:** User-level service with `Restart=always`, `RestartSec=15`, and `WantedBy=default.target`. Lingering enabled (`loginctl enable-linger`) so it survives SSH logout.

## Cron jobs (paused — fallback only)

The old polling cron jobs are **paused**, not deleted. If the watcher ever fails, unpause them:

- `wiki-dropbox-sync` (ID `233d2e3c4fbe`) — paused 2026-05-15
- `photo-news-dropbox-sync` (ID `bcca6a98591b`) — paused 2026-05-15

Paused via `hermes cron pause <job_id>`. Unpause: `hermes cron unpause <job_id>`.

Wrapper scripts (still present if cron approach is ever revived):
- `scripts/dropbox_wiki_sync.py` — wraps `dropbox-sync.sh` and reports exit code + output
- `scripts/dropbox_photo_sync.py` — wraps `photo-news-sync.sh` and reports exit code + output

**Pitfall — silently broken cron jobs:** If a cron job has `model: null` AND no `script` attached, every run produces `(No response generated)` — the sync never runs, and there is no error message. The `last_status` shows `error` but the output file says nothing useful. Even with a script attached, a null-model job may still show `last_status: error` because no LLM agent processes the script output. The fix: attach a wrapper script AND assign a model (even a cheap one like `mimo-v2-pro`).

**Pitfall — delivery field misleading:** Cron job delivery `local` means output is saved but never sent anywhere. The `last_status: ok` / `error` field only means the Hermes cron run completed, not that files were synced. Always read the output file under `~/.hermes/cron/output/<job_id>/` to verify actual sync results.

## Monitoring / status checks
- **Primary:** `systemctl --user status dropbox-watcher` and `tail ~/.local/log/dropbox-watcher.log`
- **Fallback:** If watcher is down and cron revived, inspect output files under `~/.hermes/cron/output/233d2e3c4fbe/` and `~/.hermes/cron/output/bcca6a98591b/`.
