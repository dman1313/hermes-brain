# Agent Brain — Repo Structure & Migration Notes

## Overview

The agent-brain repo (`dman1313/agent-brain`) is the NEW canonical shared brain for Dwayne's agent fleet. Replaces the agent-memory vault as the primary session ritual target.

**Repo:** https://github.com/dman1313/agent-brain
**VPS path:** `~/agent-brain/`
**Mac path:** `/Volumes/M2 Media/DROPBOX/Dropbox/All Agents/` (Dropbox-synced, git handles merge)
**BRAIN_ROOT:** Set in `~/.bashrc` — `export BRAIN_ROOT="/home/ubuntu/agent-brain"`

## Directory Structure

```
agent-brain/
├── AGENTS.md           # Core operating rules — read every session
├── REFERENCE.md        # Setup, sync, onboarding, filing details
├── NOW.md              # Auto-generated fleet state (don't hand-edit)
├── ACTIVITY.md         # Auto-generated merged activity (don't hand-edit)
├── agents/             # Per-agent profiles
│   ├── _roster.md      # Auto-generated roster (don't hand-edit)
│   ├── hermes.md
│   ├── claude-code.md
│   ├── cursor.md
│   └── ...
├── activity/           # Per-agent activity logs (append-only)
│   ├── hermes.md
│   ├── claude-code.md
│   └── ...
├── projects/           # Per-project resume state
│   └── {slug}.md
├── inbox/              # Inter-agent messaging
│   └── {recipient}/
├── memory/             # Fleet/user preferences, reference material
│   ├── user/
│   ├── feedback/
│   └── reference/
├── raw/                # Inbound raw material (curator promotes to wiki/)
├── wiki/               # Curated knowledge graph
│   └── index.md        # Auto-generated wiki catalog
├── schema/             # Curator rules
│   └── AGENTS.md
├── scripts/
│   └── janitor.sh      # Enforcement: rotates, regenerates, flags duplicates
├── templates/
│   └── agent.md        # Template for new agent profiles
└── .git/
```

## Key Differences from Agent-Memory Vault

| Aspect | Agent-Memory (old) | Agent-Brain (new) |
|--------|--------------------|-------------------|
| Activity log | Single `ACTIVITY.md` (all agents) | Per-agent `activity/{name}.md` (merged view auto-generated) |
| Agent profiles | `Agents/{name}.md` | `agents/{name}.md` |
| Inter-agent msgs | `AGENT-CHANNEL.md` | `inbox/{recipient}/` (one file per message) |
| Projects | No formal tracking | `projects/{slug}.md` with resume state |
| Standing orders | `STANDING-ORDERS.md` | Embedded in `AGENTS.md` |
| Context generation | `build-context.sh` | `scripts/janitor.sh` |
| Sync | Git (manual) | Git + 15-min cron on VPS |

## VPS Setup (completed 2026-06-15)

```bash
# Clone
git clone https://github.com/dman1313/agent-brain ~/agent-brain

# Set BRAIN_ROOT
echo 'export BRAIN_ROOT="/home/ubuntu/agent-brain"' >> ~/.bashrc

# Install sync cron (15-min)
(crontab -l 2>/dev/null; echo "*/15 * * * * cd /home/ubuntu/agent-brain && git pull --rebase --autostash -q && git add -A && git diff --cached --quiet || git commit -m 'auto-sync' -q && git push -q 2>/dev/null") | crontab -
```

REF.md also documents a bootstrap script:
```bash
curl -fsSL https://raw.githubusercontent.com/dman1313/agent-brain/main/scripts/hermes-bootstrap.sh | bash
```

## Pitfalls

- **Don't hand-edit generated files:** ACTIVITY.md, NOW.md, wiki/index.md, agents/_roster.md are rebuilt by janitor.sh.
- **Activity goes to YOUR file:** `activity/{your-name}.md`, not ACTIVITY.md. The merged view is auto-generated.
- **Pull before edit:** Always `git pull --rebase --autostash` to avoid merge conflicts across machines.
- **Two systems coexist:** Agent-brain for session ritual + agent profiles. Agent-memory for wiki/raw content. Don't duplicate.
