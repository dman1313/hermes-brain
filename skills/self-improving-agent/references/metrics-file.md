# Self-Improving Agent — Metrics File

**Install path:** `~/.hermes/skills/_metrics/self-improving-agent.json`

This is where the observability metrics (Section 10 of the SKILL.md) are written. The SKILL.md references `<skills_root>/_metrics/self-improving-agent.json` as a generic path; on this Hermes install the resolved path is `~/.hermes/skills/_metrics/self-improving-agent.json`.

## File schema

```json
{
  "installed": "2026-05-13",
  "skills_proposed": 0,
  "skills_approved": 0,
  "skills_reverted": 0,
  "recall_hits": 0,
  "recall_misses": 0,
  "repeated_errors": 0,
  "memory_prunes": 0,
  "memory_utilisation_percent": 94,
  "last_self_check": "2026-05-13",
  "notes": "Free text for context"
}
```

## Who reads it

- **HAL** checks this during the 08:00 daily brief (System Health step 4)
- **DREAM** may include it in nightly reflection if configured
- The agent running this skill should write to it after each self-check

## Who writes to it

The agent executing the self-improving-agent skill. Currently, no trigger has fired (metrics remain at initial values). The first 15+ tool call session will trigger a self-check and update the file.

## Pitfalls

- Do not hardcode the numeric identifiers from this file into memory — they change. Read the file fresh each session.
- If `memory_utilisation_percent` stays static for multiple days, the learning loop hasn't fired yet. That's not an error — the skill waits for a complex task (5+ tool calls) or periodic trigger to activate.
