---
name: sherlock-api-discovery
description: "Subskill: Daily API endpoint testing for Wolf Trading Agent. Sherlock tests actual data endpoints, not homepage HEAD checks. 'Always check APIs before using' — this is how."
version: "2.0"
parent_skill: sherlock
created: "2026-05-14"
updated: "2026-05-14"
owner: Dwayne (Sherlock)
---

# Sherlock API Discovery — Wolf API Scanner Subskill

## Mission

Daily scan for new financial data APIs that could feed Wolf Trading Agent.
The RULE: **Always test an API endpoint before marking it usable.**
A 200 on a homepage means NOTHING. Hit the actual data endpoint.

## Script

```
~/.hermes/skills/agents/sherlock/scripts/api_discovery_scanner.py
```

## What It Does (Phase 1 — Real Endpoint Tests)

Every API in the known list gets a real API endpoint test, not a homepage HEAD:

| Status | Meaning |
|--------|---------|
| ✅ working | Endpoint returned 200 + expected data field |
| ✅ reachable | Endpoint returned 200 (no expected field to match) |
| ⚠️ needs-key | Returns 200 but body says "provide API key" |
| 🔒 forbidden | 401/403 — needs valid API key or subscription |
| 🔴 dead | Domain unreachable or server error |
| 🤔 unexpected | Needs manual inspection |

Credential-dependent tests:
- **GNews API**: tests if `GNEWS_API_KEY` env var is set
- **Alpha Vantage**: tests if `ALPHA_VANTAGE_API_KEY` env var is set
- All others: tests without a key → expects 401/403 (confirms endpoint exists)

## What It Does (Phase 2 — Discovery)

- RapidAPI marketplace page checks (8 finance APIs)
- GitHub search (trending financial API repos)

## Output

Report written to:
```
wolf-trading-agent/output/api_discovery_YYYY-MM-DD.md
```

Known API state persisted to:
```
wolf-trading-agent/output/api_discovery_known.json
```

## Usage

```bash
# Full scan (endpoint tests + RapidAPI + GitHub discovery)
cd ~/.hermes/skills/agents/sherlock
python3 scripts/api_discovery_scanner.py

# Daily: endpoint tests only (the cron job uses this)
python3 scripts/api_discovery_scanner.py --quick

# JSON output
python3 scripts/api_discovery_scanner.py --json
```

## Truth Table — Current Wolf Data Sources

| Source | Tested? | Status |
|--------|---------|--------|
| **GNews API** | No key available | ❓ Needs GNEWS_API_KEY env var |
| **Alpaca Markets** | No headers configured | ⏭️ Needs API key auth headers |
| **Alpha Vantage** | ✅ Tested with key | ✅ Working |
| **Yahoo Finance (unofficial)** | ✅ Public endpoint | ✅ Working |
| **CoinGecko** | ✅ Public endpoint | ✅ Working |
| **Finnhub** | 🔒 No key available | 🔒 Needs free API key to test |

## Quality Checks

- Every report date-stamps and shows HTTP status codes
- Every report lists APIs that passed REAL endpoint testing separately from "domain is up"
- Status changes are tracked across days (same persistent file)
- If an API that was "working" becomes "dead", it's flagged
