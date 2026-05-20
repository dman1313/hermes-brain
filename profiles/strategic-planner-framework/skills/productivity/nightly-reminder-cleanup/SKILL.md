---
name: nightly-reminder-cleanup
description: Audit reminder/follow-up state across Hermes sources, separate active action items from cleared noise, and produce a concise nightly cleanup report.
---

# Nightly Reminder Cleanup

Use this when a cron job or user asks for a reminder cleanup, stale follow-up audit, or end-of-day check for ignored items.

## Goal
Find what actually still needs attention across Hermes-managed reminder sources, avoid reporting already-resolved noise, and return a short action-oriented summary.

## Sources to check
Check these in roughly this order:

1. **Structured todos**
   - Call `todo()` first.
   - If there are pending or in-progress items, treat them as the strongest signal.

2. **Recent session history**
   - Use `session_search` for reminder/follow-up terms, plus broader unresolved terms.
   - Good queries:
     - `reminder cleanup OR nightly reminder OR follow-up OR notifications`
     - `unresolved OR blocked OR waiting for user OR pending input OR follow up needed`
   - Use this to find cross-session blocked work not visible in the todo list.

3. **Wiki / notes**
   - Check `/home/ubuntu/wiki` if it exists.
   - Search markdown for `reminder|follow-up|pending|waiting|blocked|action item|todo`.
   - If the default Obsidian vault path does not exist, explicitly note that instead of assuming notes were checked.

4. **Local saved reminder artifacts**
   - Check for reminder/check-in files that were saved locally by cron jobs instead of sent.
   - Common paths to inspect:
     - `/home/ubuntu/morning-checkins/`
     - `/home/ubuntu/zen-morning-checkin.txt`
     - `/home/ubuntu/zen-nightly-reflection.md`
   - If these are same-day reminder artifacts and the cleanup is running at night, archive them into a dated folder such as `/home/ubuntu/reminder-archive/YYYY-MM-DD/` or otherwise mark them complete.
   - Distinguish between active same-day prompts and already-archived history.

5. **Cron outputs and system logs**
   - Inspect recent files under `~/.hermes/cron/output/` and `~/.hermes/obsidian_workspace/agent_shared/system_logs/`.
   - Especially useful for recurring reminders/check-ins that silently failed.
   - Do not rely only on `hermes cron list` status: the registry may show `ok` even when the saved `## Response` is `API call failed after 3 retries`, `HTTP 429`, or `(No response generated)`.
   - Parse the latest output file per job and scan the response section for real failure text.
   - Prioritize current or repeated failures over one-off historical warnings.

## How to classify findings
Split results into these buckets:

### Needs attention
Report only items that are still active, blocked, or repeatedly failing.
Examples:
- cron jobs that are still failing on latest/near-latest runs
- blocked requests waiting on user input
- reminders that produced no response
- follow-ups with missing required details

### Can be cleared
Explicitly clear stale noise if newer evidence shows the issue is resolved.
Examples:
- old health warnings that a newer health check shows are fixed
- old sync failures when the latest sync succeeded
- historical warnings that are no longer current

## Verification rules
Before reporting an issue as active:
1. Check for a newer successful run or newer healthy log.
2. Prefer the latest dated artifact over older session summaries.
3. If a monitor says something failed, verify against the job's own output directory when possible.

## Pitfalls
- Do **not** rely only on `todo()`; many real follow-ups live only in session history or cron outputs.
- Do **not** report a historical error as current without checking the latest artifact.
- Do **not** claim Obsidian was checked if the vault path does not exist.
- Avoid broad filesystem matches that surface unrelated example/test data unless corroborated by live session or cron evidence.

## Recommended report format
Use a concise structure:
- `Nothing is in the structured todo queue` (if applicable)
- `What still needs attention`
- `What can be cleared`
- `Action items`

Keep it short, specific, and operational.