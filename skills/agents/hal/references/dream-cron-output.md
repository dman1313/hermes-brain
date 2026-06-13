# DREAM Cron Output — Reference for Daily Brief

DREAM runs nightly at 3am. Its output is the primary source of overnight intelligence for the HAL daily brief.

## Cron Job IDs

| Cron ID | Function | Schedule |
|---------|----------|----------|
| `28bd7873af01` | DREAM Nightly Reflection | 0 3 * * * (3am daily) |
| `2bac775e7d28` | gdrive-backup (same time) | 0 3 * * * (3am daily) |

DREAM and gdrive-backup run at the same time but use different providers — no contention observed.

## Output Location

```
~/.hermes/cron/output/28bd7873af01/YYYY-MM-DD_HH-MM-SS.md
```

Latest file is the most recent run. To find it:
```bash
ls -t ~/.hermes/cron/output/28bd7873af01/*.md | head -1
```

## What to Extract from DREAM Output

Read the last ~50 lines for the morning brief section (starts with `## DREAM Morning Brief`). Key intelligence:

- **Provider health**: DREAM reports HTTP error counts (451, 503, etc.) across providers. If errors dropped to zero, a blocked provider has recovered — clear the NOW.md blocker.
- **Gateway outages**: DREAM monitors Telegram gateway health. Brief outages (Bad Gateway → Timeout → self-recovered) are noted.
- **User session count**: Zero user sessions = quiet day, no user-facing problems to report.
- **Skill proposals**: If DREAM auto-proposes a skill, it'll be in `~/.hermes/obsidian_workspace/agent_shared/workflow_templates/dream_proposal_YYYYMMDD.md`

## Cross-Reference Pattern

When DREAM reports a provider recovered (zero errors), compare against NOW.md Blockers section. If the blocker is stale, clear it and log a `blocker-resolve` entry to ACTIVITY.md.

Example from 2026-06-12:
- DREAM: "xiaomi provider is working again. Zero cross-border (451) errors yesterday."
- NOW.md blocker: "DeepSeek/xiaomi provider blocked — HTTP 451" (since June 5)
- Action: Clear blocker, update NOW.md, log to ACTIVITY.md
