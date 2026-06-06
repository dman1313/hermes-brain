# Full Offline Backup + Drive Upload — 2026-06-04

## Context

Triggered by "clean up the server" then "back up to Google Drive with migration guide". Server was at 80% disk usage. Required safe backup before system update.

## What was backed up

| Tarball | Size | Contents |
|---------|------|----------|
| hermes-config-and-state.tar.gz | 127 MB | config.yaml, .env, skills/, plugins/, cron/, sessions/, checkpoints/, profiles/, SOUL.md, AGENTS.md, MEMORY.md, USER.md, HEARTBEAT.md, CLAUDE.md |
| hermes-source.tar.gz | 492 MB | hermes-agent/ source (excluded node_modules, __pycache__, .venv, dist, .next) |
| state-snapshots.tar.gz | 214 MB | ~/.hermes/state-snapshots/ |
| agent-memory.tar.gz | 454 KB | ~/agent-memory/ (Git vault, shared with Mac) |
| scripts-and-extras.tar.gz | 17 MB | ~/scripts/, ~/.hermes/scripts/, hermes-brain/, dashboard-auth-proxy.py |
| RESTORE.md | 5 KB | 11-step migration guide |
| cron-jobs-export.json | 34 KB | All 18 cron job definitions |

Total: ~850 MB

## Procedure

### Build tarballs

```bash
cd ~
# Config + state
tar czf backups/$DATE/hermes-config-and-state.tar.gz \
  .hermes/config.yaml .hermes/.env .hermes/skills/ .hermes/scripts/ \
  .hermes/plugins/ .hermes/cron/ .hermes/sessions/ .hermes/checkpoints/ \
  .hermes/data/ .hermes/kanban/ .hermes/profiles/ .hermes/state-snapshots/ \
  .hermes/obsidian_workspace/ \
  SOUL.md AGENTS.md CLAUDE.md USER.md HEARTBEAT.md MEMORY.md

# Source (no deps)
tar czf backups/$DATE/hermes-source.tar.gz \
  --exclude='node_modules' --exclude='.next' --exclude='dist' \
  --exclude='__pycache__' --exclude='.venv' --exclude='venv' \
  .hermes/hermes-agent/

# Agent memory
tar czf backups/$DATE/agent-memory.tar.gz agent-memory/

# Scripts/extras
tar czf backups/$DATE/scripts-and-extras.tar.gz \
  scripts/ .hermes/scripts/ hermes-brain/ dashboard-auth-proxy.py
```

### Upload to Drive (GAPI)

```bash
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
GAPI="$HERMES_HOME/hermes-agent/venv/bin/python \
  $HERMES_HOME/skills/productivity/google-workspace/scripts/google_api.py"

# Upload small files first (they're fast)
$GAPI drive upload RESTORE.md --name "hermes-backup-2026-06-04-RESTORE.md"
$GAPI drive upload cron-jobs-export.json --name "hermes-backup-2026-06-04-cron-jobs.json"
$GAPI drive upload agent-memory.tar.gz --name "hermes-backup-2026-06-04-agent-memory.tar.gz"
$GAPI drive upload scripts-and-extras.tar.gz --name "hermes-backup-2026-06-04-scripts-and-extras.tar.gz"

# Then larger files (these take 30-120s)
$GAPI drive upload hermes-config-and-state.tar.gz --name "hermes-backup-2026-06-04-config-and-state.tar.gz"
$GAPI drive upload state-snapshots.tar.gz --name "hermes-backup-2026-06-04-state-snapshots.tar.gz"

# Biggest last (~500MB, set terminal timeout to 600s)
$GAPI drive upload hermes-source.tar.gz --name "hermes-backup-2026-06-04-hermes-source.tar.gz"
```

### Prune old backups

```bash
$GAPI drive delete "hermes-backup-" --keep 7
```

### Clean local files

After verifying uploads on Drive, delete the local tarballs to reclaim space:

```bash
rm -f ~/backups/$DATE/*.tar.gz
```

Keep RESTORE.md and cron-jobs-export.json locally for reference.

## Drive upload notes

- The `--name` flag in `$GAPI drive upload` creates a new file or replaces one with the same name.
- File naming convention: `hermes-backup-YYYY-MM-DD-<component>.tar.gz` for components, `hermes-backup-YYYY-MM-DD-HHMM.tar.gz` for the old monolithic format.
- Large file uploads (200MB+) may cause the terminal tool to time out. The upload continues on the Google side — verify with `$GAPI drive search "hermes-backup-"` after the timeout.
- The prune pattern matches the `hermes-backup-` prefix, so both naming conventions are caught.

## Migration guide (RESTORE.md)

The RESTORE.md covers 11 steps:
1. Install Hermes Agent fresh
2. Restore config + .env from tarball
3. Restore skills/scripts/plugins
4. Restore cron jobs (import jobs.json)
5. Restore agent-memory vault (Git re-sync)
6. Restore scripts and extras
7. Restore state snapshots (optional)
8. Set up systemd services + Cloudflare tunnel + Caddy
9. Reinstall Python deps
10. Verify all systems
11. Re-auth for Google Workspace, X/Twitter, GitHub as needed
