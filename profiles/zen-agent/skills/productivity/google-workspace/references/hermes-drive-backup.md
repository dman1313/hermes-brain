# Hermes State Backup to Google Drive + GitHub

Dual backup: GitHub (private repo, skills + wiki) + Google Drive (tarball, config + skills + wiki).

## GitHub Backup

Repo: `dman1313/hermes-backup` (private)
Contents: `~/.hermes/skills/` (all skills, references, scripts, templates) + `~/wiki` snapshot
Excluded: `.env`, tokens, auth.json, keys, sessions, logs, pycache, node_modules, venv

Push pattern:
```bash
cd /tmp/hermes-backup && \
cp -r ~/.hermes/skills hermes/ && \
cp -r ~/wiki wiki-snapshot/ && \
git add -A && git commit -m "Hermes backup $(date +%Y%m%d_%H%M)" && git push
```

## Drive Backup

Script: `/home/ubuntu/scripts/hermes-backup.py` — creates a timestamped tarball and uploads via `google_api.py drive upload`.

**Included:** `skills/`, `cron/`, `SOUL.md`, `config.yaml`, `gateway_state.json`, `channel_directory.json`, `tasks.json`, `workspace-sessions.json`, `processes.json`

**Excluded:** `sessions/`, OAuth tokens, model caches, `auth.json` — all regeneratable or sensitive.

## Cron

Job: `hermes-gdrive-backup` — runs daily at 3 AM local, keeps last 7 backups via `drive delete --keep 7`.

## Drive Upload Mechanics

The `google_api.py drive upload` command upserts by name: if a file with the same name exists, it replaces it. If not, it creates a new one. Rotation is handled by `drive delete <pattern> --keep N` which trashes older matching files beyond the retention count.

## Troubleshooting

### Backup cron shows "error" status but a file was uploaded

The backup script previously had a **double-call bug** where `drive upload` was called twice, with the first call's output discarded. This could cause confusing error/noise in cron output. Fixed May 11, 2026 — if you're seeing phantom errors, verify the script at `/home/ubuntu/scripts/hermes-backup.py` only calls `drive upload` once.

### `RuntimeError: checking third-party user token: bad request: Personal Access Tokens are not supported for this endpoint`

This is a **transient Google OAuth token refresh glitch**. Not a permanent failure. The token auto-refreshes on next use. If this fires during a cron run:
1. Try running the backup manually — it will likely succeed after token refresh.
2. If it persists, run `setup.py --check` to verify the token state.
3. If the token is genuinely invalid (unlikely), follow the reset procedure below.

### Token reset / re-authorization

When the Google OAuth token needs a full reset (revoke + re-auth):

```bash
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
GWORKSPACE_SKILL_DIR="$HERMES_HOME/skills/productivity/google-workspace"
PYTHON_BIN="$HERMES_HOME/hermes-agent/venv/bin/python"
GSETUP="$PYTHON_BIN $GWORKSPACE_SKILL_DIR/scripts/setup.py"

# Step 1: Revoke and delete local token
$GSETUP --revoke

# Step 2: Generate auth URL (send this to the user)
$GSETUP --auth-url

# Step 3: User visits URL, authorizes, provides the code
# Step 4: Exchange code for new token
$GSETUP --auth-code "CODE_FROM_USER"

# Step 5: Verify
$GSETUP --check
```

**Known bug (fixed May 2026):** The `--revoke` function in `setup.py` previously had a literal `***` placeholder instead of `{creds.token}` in the revoke URL (line 323). This meant the remote revocation silently failed while still deleting the local token file. Fixed: the URL now correctly includes the token. If you're on an older version of the script, patch line 323.

## Restoration

To restore from a backup:
1. Download the tarball from Google Drive (use `drive search "hermes-backup-"` to find the latest)
2. Extract into `$HOME/.hermes/`: `tar xzf hermes-backup-*.tar.gz -C $HOME/.hermes/`
3. Restart Hermes
