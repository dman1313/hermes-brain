# Hermes Brain — Disaster Recovery Backup

This repo contains the durable knowledge of HAL (Hermes Agent Lead), running on Dwayne Primeau's VPS.

**What's backed up:**
- All agent skills (~/.hermes/skills/)
- Agent profiles (~/.hermes/profiles/)
- Configuration (redacted — no secrets)
- Long-term memory (MEMORY.md)
- Agent identity files (SOUL.md, AGENTS.md)
- Webhook subscriptions
- Backup/restore scripts

**What's NOT included (secrets, ephemera):**
- .env files, API keys, tokens
- Session logs, cache, venv
- Gateway state snapshots

## Restore

```bash
git clone https://github.com/dman1313/hermes-brain.git
./hermes-brain/scripts/restore.sh
```

## Update Backup

```bash
./scripts/backup.sh   # run from hermes-brain root
```
