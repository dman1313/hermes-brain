# Second Brain Vault — Dwayne's Knowledge Base

## Setup (Hermes VPS)

```bash
# Clone
gh repo clone dman1313/second-brain ~/Documents/Obsidian\ Vault/second-brain

# Set vault path in ~/.hermes/.env
echo 'OBSIDIAN_VAULT_PATH=/home/ubuntu/Documents/Obsidian Vault/second-brain' >> ~/.hermes/.env

# Git config
cd ~/Documents/Obsidian\ Vault/second-brain
git config user.email "hermes@humangood.ai"
git config user.name "Hermes"
```

## Sync Script

`~/.hermes/scripts/sync-second-brain.sh` — pull + commit + push.

Run before and after vault operations:
```bash
bash ~/.hermes/scripts/sync-second-brain.sh
```

## Structure

```
second-brain/
├── AGENTS.md          # Ingestion rules (YouTube, Twitter, GitHub, articles)
├── index.md           # Top-level vault index
├── log.md             # Chronological activity log
├── wiki/              # AI-maintained knowledge pages
│   └── index.md       # Wiki table of contents
├── journal/           # Daily reflections
├── crm/               # Contact records
├── raw/               # Unprocessed source queue
│   └── processed/     # Archived after ingestion
│       ├── youtube/
│       ├── twitter/
│       ├── github/
│       ├── articles/
│       └── assets/
└── .obsidian/         # Obsidian config
```

## Ingestion Protocol (from AGENTS.md)

When a file appears in `raw/`:
1. Read the source
2. Summarize key insights
3. Extract people, companies, tools, ideas
4. Generate/update wiki pages in `wiki/`
5. Create/update CRM entries in `crm/`
6. Update `wiki/index.md` and `index.md`
7. Move source to `raw/processed/{type}/`
8. Log to `log.md`

## Current State (2026-05-31)

- 53 markdown files
- 14 sources already processed (raw queue empty)
- Wiki covers: AI tools, trading, frameworks, spec-driven development
- No pending ingestion work
