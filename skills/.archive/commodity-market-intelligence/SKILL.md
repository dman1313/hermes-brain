---
name: commodity-market-intelligence
description: Monitor crude oil and commodity positioning data (CFTC COT), options flow anomalies, and concentration shifts as early-warning signals for narrative changes in energy markets. Includes working COT scanner script and knowledge of data source accessibility.
triggers:
  - crude oil positioning
  - COT data
  - commodity options flow
  - unusual options activity commodities
  - Brent WTI positioning
  - managed money crude
  - energy market intelligence
  - CFTC data
  - block trades commodities
---

# Commodity Market Intelligence

Monitor crude oil / Brent / energy positioning and options flow to detect anomalies that typically precede headline-driven narrative shifts.

## Core Insight

When concentrated short-dated options flow doesn't fit the current narrative, the narrative usually shifts within 48 hours. This is a watchlist trigger, not a trade signal.

## Data Sources — What Actually Works

### Free & Scriptable

**CFTC Public Reporting API** (BEST free source)
- Base: `https://publicreporting.cftc.gov/resource/{dataset_id}.json`
- No auth required, reliable, SQL-like `$where` queries
- **Disaggregated COT** (`72hh-3qpy`) — managed money, swap dealers, producer/merchant
- **Legacy COT** (`jun7-fc8e`) — noncommercial, concentration ratios
- Released every Friday 3:30 PM ET (positions as of prior Tuesday)
- 3-4 day lag but authoritative for weekly positioning shifts

**Working contract names (verified current as of 2026-05):**
- `CRUDE OIL, LIGHT SWEET-WTI - ICE FUTURES EUROPE` (disagg) — ICE WTI, current
- `BRENT LAST DAY - NEW YORK MERCANTILE EXCHANGE` (both datasets) — Brent, current
- `CRUDE OIL, LIGHT SWEET - NEW YORK MERCANTILE EXCHANGE` (legacy only) — NYMEX WTI, **STALE: only through Feb 2022**

### Blocked / Not Scriptable

- **CME Group** — blocks automated access (403 + anti-scraping message on any programmatic request)
- **Barchart** — JS-rendered, internal API requires session cookies/tokens from browser
- **Yahoo Finance** — rate-limits yfinance for commodity futures options
- **Alpaca** — US equities/index options only, no commodity futures options
- **ICE** — no free analytics suite comparable to CME QuikStrike

### Manual (Free)

- **CME QuikStrike** (free with CME account) — Most Active Strikes, Open Interest Heatmap, Globex Trade Browser. Best for WTI. JS-rendered, not scriptable.
- **Barchart options chains** (free) — Brent/WTI option chains with volume + OI. JS-rendered.

### Paid / API

- **Databento** (~$0.50/GB) — CME + ICE options tick data, Python client. Best for building a systematic scanner. $125 free trial.
- **Interactive Brokers TWS API** — free with funded account, covers CME + ICE options on futures.

## Anomaly Detection Criteria

Flag when any metric exceeds 2σ vs 26-week rolling baseline:
- Managed money net position change
- Short position spike (week-over-week)
- Spread position change (options-adjacent)
- Top-4/8 trader concentration ratio shift
- Unusual OI buildup

For options-level anomalies (when you have the data):
- Volume/OI ratio > 150% on a single strike outside expiration week
- Block trade > $5M notional (quantity × premium × contract multiplier)
- Single-strike OI spike vs rest of chain
- Short-dated (<30 DTE) + large concentrated size

## COT Query Patterns

```
# Disaggregated — get managed money for ICE WTI
GET /resource/72hh-3qpy.json
  ?$where=market_and_exchange_names='CRUDE OIL, LIGHT SWEET-WTI - ICE FUTURES EUROPE'
  &$order=report_date_as_yyyy_mm_dd DESC
  &$limit=28

# Legacy — get concentration ratios for Brent
GET /resource/jun7-fc8e.json
  ?$where=market_and_exchange_names='BRENT LAST DAY - NEW YORK MERCANTILE EXCHANGE'
    AND futonly_or_combined='Combined'
  &$order=report_date_as_yyyy_mm_dd DESC
  &$limit=28
```

URL-encode the `$where` value (spaces, commas, quotes). Use `urllib.parse.quote()` in Python.

## Pitfalls

1. **NYMEX WTI disaggregated data ended Feb 2022** — CFTC consolidated to ICE Europe. Use the ICE FUTURES EUROPE contract name, not NYMEX.
2. **URL encoding** — CFTC API rejects spaces/unencoded characters in query string. Always encode the `$where` parameter.
3. **`futonly_or_combined` filter** — Legacy COT has both rows. Use `futonly_or_combined='Combined'` for futures+options positioning.
4. **Spread field naming differs** — Legacy uses `noncomm_postions_spread_all` (note typo in CFTC data). Disaggregated uses `m_money_positions_spread_all`.
5. **CME will block your IP** — Do not attempt to scrape CME programmatically. They respond with 403 and explicit anti-scraping warning.
6. **Barchart UOA/options flow pages are equity-only** — Their "Unusual Options Activity" and "Options Flow" pages do NOT cover commodity futures options, despite Barchart having extensive futures options quote data.
7. **Weekly cadence only** — CFTC COT is weekly (Friday release). For daily/intraday monitoring you need paid feeds (Databento, IB) or manual QuikStrike scans.

## Running Implementation

Cron job `CFTC COT Crude Oil Scanner` (job ID: `db1264296679`):
- Script: `~/.hermes/scripts/cot-scanner.py`
- Schedule: Fridays 21:45 Paris (15 min after CFTC release)
- Mode: `no_agent=True` (script-only, no LLM reasoning needed)
- Delivers output directly to Telegram

The script pulls 26 weeks of history, calculates z-scores on week-over-week changes, and flags anything >2σ. Covers WTI (ICE Europe) + Brent Last Day (NYMEX) for both managed money and concentration data.
