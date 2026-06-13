# Vault Canonical Instructions

The vault itself contains its own operating instructions. These are the source of truth — if they conflict with this skill, the vault files win.

## Key instruction files (read in order)

1. **`CLAUDE.md`** — Session startup protocol, knowledge routing table, memory file format, activity log format, rules
2. **`STANDING-ORDERS.md`** — Fleet-wide standing orders. Every agent reads this at every session. Covers: conditional startup, logging protocol, SDD protocol, session closeout, rules, agent roster
3. **`AGENT-SETUP.md`** — Per-agent setup instructions (Hermes, Claude Code, Codex, Goose, Kimi, Kiro, Cursor). Sync architecture diagram. File format spec.
4. **`schema/AGENTS.md`** — Knowledge Curator master rules (only needed for wiki/raw work)

## What changed (2026-06-10)

Hermes was not using the vault at all. Dwayne pointed out that:
- The vault is the shared wiki for the ENTIRE fleet, not just a coding agent memory store
- All agents read NOW.md to coordinate — if Hermes doesn't log, the fleet doesn't know what we're doing
- The vault protocol should be treated as mandatory, not optional

Hermes added section 22b to SOUL.md to enforce this. The `agent-memory-daily` cron (c9bd43fed803) acts as a safety net but is NOT the primary mechanism.
