# GitHub Brain Backup (hermes-brain)

Third backup destination — a public Git repo that mirrors skills, profiles, config (redacted), and identity files. No secrets, no sessions, no cache.

| Detail | Value |
|--------|-------|
| **Repo** | https://github.com/dman1313/hermes-brain |
| **Local** | `/home/ubuntu/hermes-brain/` |
| **Script** | `/home/ubuntu/hermes-brain/scripts/backup.sh` |
| **Restore** | `/home/ubuntu/hermes-brain/scripts/restore.sh` |
| **Cron** | `2a095420f77e` (Sundays 3am SGT) |
| **Secrets** | Excluded via .gitignore + find-delete of token/secret/credential/env files |

## What's Backed Up

- All 231+ skills (~/.hermes/skills/)
- All 16 agent profiles (no .env files)
- config.yaml (redacted — secrets replaced with [REDACTED])
- SOUL.md, AGENTS.md, MEMORY.md
- webhook_subscriptions.json
- Daily memory files

## How to Update

```bash
cd /home/ubuntu/hermes-brain
bash scripts/backup.sh
git add -A && git commit -m "backup: $(date +%Y-%m-%d-%H%M)"
git push origin main
```

## How to Restore

Clone the repo and run restore.sh. Secrets (.env, tokens) must be restored manually.

## Differences from Google Drive / Dropbox Backups

- **Public** — no secrets, safe to push
- **Skills-focused** — the Drive/Dropbox backups are tarballs of everything; this is a browsable Git repo
- **Incremental** — Git tracks changes over time naturally
- **Portable** — can be cloned anywhere without Hermes-specific tools
