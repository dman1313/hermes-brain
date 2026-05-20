# Hermes Dropbox Backup

## Script
- Path: `/home/ubuntu/scripts/hermes-dropbox-backup.py`
- Created: 2026-05-11
- Token: reuses `/home/ubuntu/.dropbox-wiki-token` (same as wiki sync)
- Dropbox path: `/hermes-backups/`
- Retention: 7 most recent (prunes older)

## What's Backed Up
Same as Google Drive backup: skills/, cron/, SOUL.md, config.yaml, gateway_state.json, channel_directory.json, tasks.json, workspace-sessions.json, processes.json, .skills_prompt_snapshot.json, .restart_last_processed.json.

Excludes: sessions/, caches, OAuth tokens, auth files.

## Manual Run
```bash
/home/ubuntu/.hermes/hermes-agent/venv/bin/python \
  /home/ubuntu/scripts/hermes-dropbox-backup.py
```

## Auth
Uses the same `dropbox.Dropbox(oauth2_refresh_token=...)` pattern as `dropbox-sync.sh`. Falls back to access-token auth if refresh-token mode fails.

## Token File
- Path: `/home/ubuntu/.dropbox-wiki-token`
- Current token starts with `lwem34...` (a refresh token, confirmed working 2026-05-11)
- If token expires, re-auth via the `dropbox-obsidian-wiki-sync` skill procedure.
