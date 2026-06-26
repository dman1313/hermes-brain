---
name: pre-earnings-quant-scan
description: Pre-earnings quantitative scan — assesses whether a stock is safe to hold through earnings. Combines price data, options flow, analyst targets, and risk/reward synthesis.
version: 1.0.0
author: Hermes Agent
tags: [trading, earnings, options, quant, risk-assessment, pre-earnings]
related_skills: [wolf-trading-agent, alpaca-volume-scanner, ai-trader]
---

# Pre-Earnings Quant Scan

Systematic pre-earnings risk assessment. Answers: *"Is it safe to hold this ticker through earnings?"*

## Data Sources (in priority order)

| Source | What it gives | Auth |
|--------|---------------|------|
| Nasdaq API (`api.nasdaq.com`) | Price, previous close, volume, 52w range, market cap, sector, analyst target, dividend | None (free) |
| Alpaca Options Scanner (`alpaca_options_scan.py`) | Call/put volume, P/C ratio, IV, directional bias | Alpaca API key (free tier) |
| Finviz / Web scrape (fallback) | Technical support/resistance, short interest | None |

Yahoo Finance (yfinance) is heavily rate-limited from this VPS. Use the Nasdaq API as primary price source.

## Workflow

### Step 1 — Pull Price & Fundamentals

```python
python3 -c "
import urllib.request, json, time
time.sleep(1)
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'}
req = urllib.request.Request('https://api.nasdaq.com/api/quote/<TICKER>/summary?assetclass=stocks', headers=headers)
data = json.loads(urllib.request.urlopen(req, timeout=10).read())
d = data.get('data', {}).get('summaryData', {})
for k, v in d.items():
    if isinstance(v, dict):
        print(f'{v.get(\"label\",k)}: {v.get(\"value\",\"?\")}')
"
```

Key fields to extract:
- **Previous Close** — current price baseline
- **52 Week High/Low** — where it trades in the range
- **1 Year Target** — analyst consensus (critical! compare to price)
- **Market Cap** — size context
- **Share Volume** — today vs average (elevated = distribution risk)

### Step 2 — Options Flow (Alpaca)

```bash
cd ~/.hermes/skills/trading/wolf-trading-agent/scripts
python3 alpaca_options_scan.py --symbol <TICKER>
```

Key metrics from output:
- **P/C Ratio** — < 0.35 = extremely bullish, < 0.70 = bullish, 0.70-1.30 = neutral, > 1.30 = bearish
- **Call/Put Volume** — absolute volume levels
- **cIV% / pIV%** — implied volatility (high IV = earnings crush risk, favors credit spreads)
- **BIAS** — Alpaca's directional classification

### Step 3 — Risk/Reward Assessment

Calculate the three key numbers:

| Metric | How |
|--------|-----|
| **Upside to analyst target** | (Target - Price) / Price |
| **Downside to target** | (Price - Target) / Price — if negative, stock is ABOVE consensus |
| **Distance to 52w high** | (High - Price) / Price |
| **Distance to 52w low** | (Price - Low) / Price |

### Step 4 — Synthesis

Structure the verdict around these factors:

1. **Hype level** — Near 52w high? Elevated volume? Bullish P/C?
2. **Price vs fundamentals** — Trading above/below analyst consensus?
3. **IV regime** — High IV coming into earnings?
4. **Earnings gap risk** — What's the asymmetric move?

**Decision framework:**
- Price **below** analyst target + neutral/bullish P/C = ✅ safer to hold
- Price **above** analyst target + any P/C = ⚠️ priced for perfection, asymmetric downside
- Near 52w high + bullish P/C = risk-on earnings bet
- Elevated volume near highs = potential distribution

### Step 5 — Recommendation Templates

| Situation | Recommendation |
|-----------|---------------|
| Price < target, bullish P/C | Hold through earnings, consider debit spread for upside |
| Price > target, bullish P/C | Sell half, sell call credit spread to monetize IV |
| Price < target, neutral/bearish P/C | Lighten position, buy put protection |
| Price > target, bearish P/C | Reduce substantially — risk of double whammy |

## Pitfalls

- **Nasdaq API doesn't have real-time streaming** — the `info` endpoint returns stale data. Use `summary` endpoint instead for close-to-reliable Previous Close.
- **Yahoo Finance rate limits** — yfinance returns YFRateLimitError after ~5 requests from this VPS. Don't rely on it.
- **Alpaca free tier**: `StockBarsRequest` returns 403. Use `StockSnapshotRequest` for price + volume. Use `OptionSnapshotRequest` for options data.
- **For tickers not in Nasdaq** (e.g., TSX, LSE) — use MarketWatch or Google Finance scraping with proper User-Agent headers.
- **Analyst targets are slow-moving** — check the date of the consensus. Some targets from Q1 may not reflect semi cycle shifts.
- **Earnings date verification** — Nasdaq summary doesn't give earnings dates. Cross-check on MarketWatch or Google Finance.

### Step 6 — Distinguish: Direct Stock vs ETF Holding

If the user says they "hold" a stock name (e.g. "I hold DRAM"), **clarify which** before running the scan:

| They mean | What they hold | Risk profile |
|-----------|---------------|--------------|
| $MU | Direct stock | HIGH — binary earnings gap, full exposure |
| $DRAM | **Roundhill Memory ETF** | MEDIUM — MU is ~30%, diluted by Samsung/Hynix/equipment |
| Sector ETF (e.g. $SMH, $SOXX) | Semi ETF | LOWER — broad semi exposure, very diluted |
| The product (DRAM chips) | N/A — clarify "do you mean $MU or $DRAM ETF?" |

**When user holds an ETF that contains the earnings-reporting stock:**
- Compute the **effective exposure** = fund weight × expected move
- Example: $MU at 30% of $DRAM, MU gap risk ±10% → DRAM impact is ~±3%
- Add sector sympathy: if MU gaps, SK Hynix and Samsung (also in DRAM) often follow — boosts total impact to ~60-70% of the ETF
- Recommendation is always more restrained than for direct stock holding

### Step 7 — Handle the User's Next Question

After delivering the assessment, expect either:
- **"So should I sell/hedge?"** — give a concrete action (reduce size, buy put, sell call credit spread)
- **"What's the read-through to X?"** — check related tickers/ETFs
- **No follow-up** — assessment was clear, move on

## Pitfalls

- **Nasdaq API doesn't have real-time streaming** — the `info` endpoint returns stale data. Use `summary` endpoint instead for close-to-reliable Previous Close.
- **Nasdaq options chain endpoint returns split-adjusted strikes for post-split stocks** — the `option-chain` endpoint may return $35-$525 strikes even for a $1,043 stock (pre-split adjustment). Cross-check with Alpaca options data which handles splits correctly.
- **Earnings date from Nasdaq calendar** — use `api.nasdaq.com/api/calendar/earnings?date=YYYY-MM-DD` but search results may not include the ticker. Cross-check on MarketWatch or Google Finance.
- **Yahoo Finance rate limits** — yfinance returns YFRateLimitError after ~5 requests from this VPS. Don't rely on it. 
- **Alpaca free tier**: `StockBarsRequest` returns 403. Use `StockSnapshotRequest` for price + volume. Use `OptionSnapshotRequest` for options data.
- **For tickers not in Nasdaq** (e.g., TSX, LSE, Korean) — use MarketWatch or Google Finance scraping with proper User-Agent headers.
- **Analyst targets are slow-moving** — check the date of the consensus. Some targets from Q1 may not reflect semi cycle shifts.
- **Earnings date verification** — Nasdaq summary doesn't give earnings dates. Cross-check on MarketWatch or Google Finance.
- **Nasdaq API returns inconsistent price data** — the `info` endpoint showed $1,133.99 for MU (wrong/old), while the `summary` endpoint showed $1,043.19 (correct previous close). Always use `summary`.

## Verification

After running the scan, confirm:
- [ ] Price source is Nasdaq summary endpoint (reliable)
- [ ] Options flow from Alpaca scanner (P/C, volume, IV)
- [ ] Analyst target vs price delta calculated correctly
- [ ] 52w range context noted
- [ ] Volume compared to average
- [ ] IV regime assessed for earnings crush
- [ ] Risk/reward asymmetry stated clearly
- [ ] Direct stock vs ETF holding distinguished
- [ ] Recommendation is actionable (hold / reduce / hedge)
