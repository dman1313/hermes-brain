# Cleanup-Before-Analysis Timeline (May–Jun 2026)

## Occurrences

| # | Dates | Sessions Lost | Audit Source | Notes |
|---|-------|--------------|-------------|-------|
| 1 | May 25–26 | Unknown | Error logs only | 293 combined errors |
| 2 | May 28 | All | Error logs only | GLMS rate limit cascade day |
| 3 | May 29 | All | Error logs only | 4th occurrence per skill |
| 4 | May 30 | All | Error logs only | 5th occurrence per skill |
| 5 | Jun 3 | 3 sessions (192004_384a11, 32a1e6, 1f2750) | Error logs + request dumps | 221 errors. Session 192004 had 708KB request dump |
| 6 | Jun 4 | 5 sessions (ebbaf6, 6b827c, 025855_cd9d2e, 023152_535ac54e, 584c9c8c) | Error logs + request dumps | 565 errors. Sessions 025855 (1.2MB dumps) and 023152 (13 skill_manage errors) |

## Root Cause

Cleanup cron `59ebc5bd5e4e` ("Daily Night Ignore Reminders") runs at **23:00 UTC** daily. DREAM runs at **03:00 UTC**. Session files are archived before DREAM can access them.

The cleanup cron is listed in `~/.hermes/cron/jobs.json` as:
- ID: 59ebc5bd5e4e
- Name: Daily Night Ignore Reminders
- Provider: xiaomi/mimo-v2-pro
- Schedule: 0 23 * * *

Note: This cron also uses the xiaomi/mimo provider, which is **blocked by cross-border isolation** (see Provider Cross-Border Isolation pattern). It may not actually be running successfully at 23:00 — the session cleanup might be happening through another mechanism.

## Proposed Fix

1. Reschedule cleanup to 05:00 UTC (after DREAM completes)
2. Or: have DREAM explicitly archive sessions it has finished analyzing
3. Or: change DREAM to run at 01:00 UTC (before cleanup)

## Impact Metric

6 occurrences in 11 days (May 25–Jun 4). 55% of DREAM runs are producing audit data from error logs only, with coverage scores of 0.3–0.4.

## June 2026 Detail

### Jun 3 Sessions (all lost, request dumps only)
- `20260603_191301_1f2750` — 2 errors
- `20260603_192004_384a11` — 17 errors, 708KB request dump, hit MEMORY.md round-trip
- `20260603_202534_32a1e6` — 4 errors

### Jun 4 Sessions (all lost, request dumps only)
- `20260604_023152_535ac54e` — 13 errors (skill_manage cascade: 9 ML skills not found)
- `20260604_025855_cd9d2e` — 15 errors, 1.2MB request dumps, hit mimo 451 twice + MEMORY.md round-trip
- `20260604_051625_ebbaf6` — 19 errors (background review, read_file not whitelisted, skill_manage patches)
- `20260604_135415_584c9c8c` — 5 errors
- `20260604_195157_6b827c` — 18 errors
