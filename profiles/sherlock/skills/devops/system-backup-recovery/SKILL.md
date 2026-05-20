---
name: system-backup-recovery
description: >-
  Hermes state backup and disaster recovery. Covers the Google Drive backup
  system (script, cron, retention), recovery procedures, and known failure
  modes. Use whenever a user asks about backups, restoring from failure,
  crash recovery, or backup health.
trigger: >
  User asks about backup status ('when did you back up', 'restore from backup',
  'crash recovery', 'disaster recovery', 'backup health'), or a backup cron
  job fails and needs diagnosis.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [backup, recovery, disaster-recovery, google-drive, state-persistence]
    category: devops
---

# System Backup & Recovery

## Architecture

Hermes state is backed up to **two independent destinations**:

## Google Drive (primary)
Runs daily at **3:00 AM SGT** via cron.

| Detail | Value |
|--------|-------|
| **Script** | `/home/ubuntu/scripts/hermes-backup.py` |
| **Cron name** | `hermes-gdrive-backup` |
| **Cron ID** | `2bac775e7d28` |
| **Destination** | Google Drive (via `google-workspace` skill API) |
| **Retention** | 7 most recent backups |
| **Typical size** | ~6-7 MB compressed |
| **Token file** | `~/.hermes/google_token.json` |
| **Google API glue** | `~/.hermes/skills/productivity/google-workspace/scripts/google_api.py` |

## Dropbox (secondary)
Created 2026-05-11. Manual run only (no cron yet).

| Detail | Value |
|--------|-------|
| **Script** | `/home/ubuntu/scripts/hermes-dropbox-backup.py` |
| **Cron** | None (manual / ad-hoc) |
| **Destination** | Dropbox `/hermes-backups/` (via dropbox SDK) |
| **Retention** | 7 most recent backups |
| **Typical size** | ~6-7 MB compressed |
| **Token file** | `/home/ubuntu/.dropbox-wiki-token` (shared with wiki sync) |
| **Auth** | Reuses Dropbox refresh token from wiki sync skill |

See `references/dropbox-backup.md` for details.

## What's Backed Up

Both Google Drive and Dropbox backups cover the same scope:

| Included | Excluded (regeneratable) |
|----------|--------------------------|
| `skills/` | `sessions/` (~432 MB) |
| `cron/` | `models_dev_cache.json` |
| `SOUL.md` | `ollama_cloud_models_cache.json` |
| `config.yaml` | `context_length_cache.yaml` |
| `gateway_state.json` | `google_token.json` |
| `channel_directory.json` | `google_client_secret.json` |
| `tasks.json` | `auth.json` |
| `workspace-sessions.json` | |
| `processes.json` | |
| `.skills_prompt_snapshot.json` | |
| `.restart_last_processed.json` | |

## Procedure: Check Backup Status

```bash
# 1. Check cron job status
cronjob(action='list') | grep backup

# 2. Read latest backup output
ls -lt /home/ubuntu/.hermes/cron/output/2bac775e7d28/

# 3. Query backups on Drive directly
python /home/ubuntu/.hermes/skills/productivity/google-workspace/scripts/google_api.py \
  drive search "hermes-backup-"
```

## Procedure: Run Backup Manually

```bash
# Using system Python (NOT the hermetic venv — run via cron agent which uses terminal)
python3 /home/ubuntu/scripts/hermes-backup.py
```

Or use the hermetic venv directly:

```bash
/home/ubuntu/.hermes/hermes-agent/venv/bin/python \
  /home/ubuntu/scripts/hermes-backup.py
```

## Procedure: Run Dropbox Backup Manually

```bash
/home/ubuntu/.hermes/hermes-agent/venv/bin/python \
  /home/ubuntu/scripts/hermes-dropbox-backup.py
```

## Procedure: Check Dropbox Backup Status

```bash
python3 <<'PYEOF'
import dropbox
APP_KEY = "2d11cei1cq7w7bs"
APP_SECRET = "lyzrnschxa3x7wc"
TOKEN = open("/home/ubuntu/.dropbox-wiki-token").read().strip()
dbx = dropbox.Dropbox(oauth2_refresh_token=TOKEN, app_key=APP_KEY, app_secret=APP_SECRET)
dbx.users_get_current_account()
res = dbx.files_list_folder("/hermes-backups")
for e in sorted(res.entries, key=lambda x: x.server_modified, reverse=True):
    print(f"{e.name:50s} {e.server_modified}")
PYEOF
```

## Procedure: Restore From Backup

1. **List available backups** on Drive:
```bash
python /home/ubuntu/.hermes/skills/productivity/google-workspace/scripts/google_api.py \
  drive search "hermes-backup-"
```

2. **Download** the desired backup file (via Google Drive web UI or API).

3. **Extract** into Hermes home:
```bash
tar xzf hermes-backup-YYYY-MM-DD-HHMM.tar.gz -C ~/.hermes/
```

4. **Restart** Hermes:
```bash
hermes restart   # or hermes reload
```

## Procedure: Re-Authenticate Google Token

If the backup fails with a token error, follow the google-workspace skill's OAuth setup:

1. Load the skill: `skill_view("google-workspace")`
2. Follow the "First-Time Setup" steps starting from Step 3 (run `--auth-url` to get a URL, user visits it and authorizes, then `--auth-code` to exchange)
3. Verify with `setup.py --check`:
```bash
$GSETUP --check
```
4. Confirm Drive API works:
```bash
python /home/ubuntu/.hermes/skills/productivity/google-workspace/scripts/google_api.py drive search "hermes-backup-" | head -5
```

## Known Failure Modes

### 1. Token Auth Failure

**Symptoms in cron output:**
```
RuntimeError: checking third-party user token: bad request:
Personal Access Tokens are not supported for this endpoint
```

**Causes:**
- Google OAuth token expired and refresh token also stale
- Token file corrupted
- Token was issued with a different scope set than currently requested
- Token refresh rate-limited (transient — retry often works)

**Immediate check:**
```bash
# Check token expiry
cat /home/ubuntu/.hermes/google_token.json | python3 -c \
  "import json,sys; d=json.load(sys.stdin); print('Expiry:', d.get('expiry','unknown'))"

# Try a quick Drive API call to see if it works
python /home/ubuntu/.hermes/skills/productivity/google-workspace/scripts/google_api.py \
  drive search "hermes-backup-"
```

**Resolution:**
1. If Drive search works, the token is fine — the backup error was transient. Retry.
2. If Drive search fails, re-auth (see above).

### 2. Script Bug — Double Upload Call (FIXED 2026-05-11)

**Bug was:** The `upload()` function in `hermes-backup.py` called `drive upload` **twice**:
```python
def upload(path: Path) -> dict:
    run(*GAPI, "drive", "upload", str(path), "--name", path.name, check=False)  # ← first call: output discarded
    result = run(*GAPI, "drive", "upload", str(path), "--name", path.name, check=False)  # ← second call: parsed
```

This wasted time, API quota, and could confuse cron output parsing.

**Fix applied:** Removed the first call. See `references/2026-05-11-backup-failure.md` for the full incident report.

### 3. Dropbox Token Expiry

**Symptoms:**
```
Dropbox authentication failed.
Refresh-token mode error: ...
Access-token mode error: ...
```

**Resolution:** Re-auth via the `dropbox-obsidian-wiki-sync` skill.

## Pitfalls

- **Token expiry isn't always the problem.** Check if Drive API search works before assuming the token is bad. The token has a refresh_token that auto-renews, but if the refresh was issued by a revoked app or different scopes, it silently fails.
- **Backup file naming changed.** The script outputs `hermes-backup-YYYY-MM-DD-HHMM.tar.gz`. Older backups from early May used `YYYYMMDD_HHMM` (no dashes). The `drive delete` prune function only matches `hermes-backup-` prefix, so naming variations don't affect deletion.
- **Don't restore blindly.** The backup includes config files like `config.yaml`. If you restore an old backup over a newer Hermes installation, restart is mandatory.
- **Sessions are not backed up.** This is intentional (~432 MB, regeneratable from logs). If you need session history, back up `~/.hermes/sessions/` separately.
- **The google-workspace skill's google_api.py lives inside the skills tree**, which IS backed up. So a restore brings the API tooling back too.
- **Dropbox backup uses the same token as wiki sync.** If the wiki sync stops working, the Dropbox backup will too. They share `/home/ubuntu/.dropbox-wiki-token`.
- **No cron for Dropbox backup yet.** Only manual runs. Consider adding a cron job if you want automated dual-destination coverage.

## Monitoring

Check backup health via:
- Cron job output logs: `~/.hermes/cron/output/2bac775e7d28/`
- Drive query for backup files (above)
- The Agent Health Monitor cron job checks system health every 4 hours
