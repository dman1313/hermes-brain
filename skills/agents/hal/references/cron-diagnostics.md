# Cron Diagnostics Reference

Quick reference for diagnosing cron job failures in the Hermes agent office.

## Checking Job Status

List all cron jobs and their last status:
```
cronjob(action="list")
```

Key fields to check:
- `last_status` — "ok", "error", or null (never run)
- `last_delivery_error` — details if delivery failed
- `enabled` — true/false. Paused jobs show `state: "paused"`
- `last_run_at` — timestamp of last execution. Manual `run` actions may not update this field for "local" delivery jobs.

## Injection Scanner Blocks

The cron injection scanner inspects the assembled prompt (user prompt + loaded skill content) before running the agent. It blocks execution if it detects threat patterns.

### Invisible Unicode Block

**Symptom:** Job output file shows `Status: BLOCKED` with message:
> Blocked: prompt contains invisible unicode U+200D (possible injection).

**Root cause:** Compound emoji like 🧘‍♂️ (man meditating + U+200D zero-width joiner + male modifier) contain invisible characters that trigger the scanner.

**Fix:** Remove the compound emoji or replace with a non-compound equivalent. Check the offending skill file:

```bash
grep -n $'\u200d' /path/to/skill/SKILL.md
```

Other invisible characters that may trigger the scanner: U+200B (zero-width space), U+200C (zero-width non-joiner), U+200E/U+200F (LTR/RTL marks), U+FEFF (BOM), U+00AD (soft hyphen), U+180E (mongolian vowel separator), U+2060-2064 (word joiners/invisibles).

**Scan entire file:**
```python
python3 -c "
with open('SKILL.md') as f:
    for i, line in enumerate(f, 1):
        for ch in line:
            cp = ord(ch)
            if cp in (0x200B, 0x200C, 0x200D, 0x200E, 0x200F, 0xFEFF, 0x00AD, 0x180E, 0x2060, 0x2061, 0x2062, 0x2063, 0x2064):
                print(f'Line {i}: U+{cp:04X} at: {line.strip()[:80]}')
                break
print('Scan complete')
"
```

## Output File Locations

Cron job output is stored at:
```
~/.hermes/cron/output/<job_id>/<timestamp>.md
```

For blocked jobs, the output file contains the BLOCKED status and reason.
For successful runs, `last_status: "ok"` but output files for "local" delivery may not exist.

## Paused Jobs

Jobs paused for multiple days without reason — check with `cronjob(action="list")` and look for `state: "paused"`. Resume with `cronjob(action="resume", job_id="...")`.

## Testing Jobs

Always test-fire a job after fixing it:
```
cronjob(action="run", job_id="...")
```

Wait 15-30 seconds, then check `last_status` via `cronjob(action="list")`. Note: `run` may not update `last_run_at` for "local" delivery jobs even when the execution succeeds — verify by checking for a new output file or re-checking `last_status` after the next scheduled run.

## Job Delivery Targets

| Delivery | Behavior |
|---|---|
| `telegram` | Delivers to the default Telegram channel |
| `telegram:<id>:<thread>` | Delivers to specific chat + thread |
| `local` | Output stored in output files only, no external delivery |
| `origin` | Delivers to the channel where the last user interaction occurred |
