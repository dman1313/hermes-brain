---
name: quant-stock-scanner
description: "Quantitative stock scanner — technicals, fundamentals, options chain, and composite scoring. Produces a single 0-100 quant score across 5 factors: momentum, value, quality, growth, technicals."
version: 1.0.0
author: Hermes Agent
license: MIT
tags: [trading, quant, technicals, fundamentals, options, scoring, stock-scanner]
related_skills: [wolf-trading-agent, de-bono-stock-analysis, alpaca-volume-scanner, quantitative-trading-tools]
---

# 📊 Quant Stock Scanner

Quantitative stock analysis: technicals, fundamentals, options chain, and composite scoring. Produces a single 0-100 quant score to drive trade decisions.

Complements wolf-trading-agent (social/news sentiment) with hard numbers.

## Quick Start

```bash
# Full quant scan on a ticker (uses yfinance — may hit rate limits)
python3 ~/.hermes/skills/trading/quant-stock-scanner/scripts/quant_scan.py AAPL

# Just the composite score
python3 ~/.hermes/skills/trading/quant-stock-scanner/scripts/quant_scan.py AAPL --score-only

# With options chain analysis
python3 ~/.hermes/skills/trading/quant-stock-scanner/scripts/quant_scan.py AAPL --options
```

**⚠️ quant_scan.py uses yfinance for everything.** For reliable real-time prices, always supplement with Alpaca (see Workflow below). For options spreads, use the Alpaca options chain directly (see `references/alpaca-data-setup.md`).

## Workflow (Manual / In-Conversation)

When a user asks for a "quant scan" on a ticker:

1. **Pull OHLCV + fundamentals** via yfinance (6mo daily data). **Use Alpaca for real-time price** (`StockLatestTradeRequest` from `~/alpaca-bot/.env`) — yfinance prices are unreliable under rate limits.
2. **Calculate technicals**: SMA(20/50/200), EMA(12/26), RSI(14), MACD(12,26,9), Bollinger(20,2), ATR(14), volume ratios, price changes (1D/5D/20D/60D), 52W range positioning
3. **Extract fundamentals**: P/E (trailing + forward), P/S, P/B, EV/EBITDA, revenue growth, margins (gross/op/profit), ROE, debt/equity, current ratio, FCF, cash position
4. **Scrape news** from MarketWatch, Yahoo Finance, or TipRanks (use bulk_get or fetch)
5. **Pull options chain** via Alpaca `OptionChainRequest` for nearest 3 expirations if requested — filter near-ATM (±30% of price). Returns real Greeks (delta/gamma/theta/vega) and IV. See `references/alpaca-data-setup.md`.
6. **Score** using the 5-factor composite model (see below)
7. **Present** as a structured report with clear bull/bear signals

## Composite Scoring Model (5 Factors)

Each factor scores 0-100. Composite = weighted average.

### Momentum (25% weight)
- Base: 50
- +min(1D_pct × 2, 20) — today's move
- +min(5D_pct, 15) — weekly trend
- +min(20D_pct × 0.5, 10) — monthly trend
- +5 if RSI 50-70 (ideal zone), -10 if >70, +10 if <30
- +5 if MACD histogram positive
- +10 if volume ratio >1.5x, +5 if >1.2x

### Value (20% weight)
- Base: 50
- Forward P/E: <15 → +20, <25 → +10, <35 → 0, <50 → -10, else -20
- P/S: <5 → +15, <10 → +5, <20 → -5, else -10
- PEG: <1 → +15, <1.5 → +10, <2 → 0, else -10
- EV/EBITDA: <15 → +10, <25 → 0, else -10
- +min(analyst_upside × 50, 15)

### Quality (20% weight)
- Base: 50
- +min(gross_margin × 40, 20) — software-like margins rewarded
- Operating margin: >30% → +15, >15% → +10, >0 → +5, else -10
- Profit margin: >20% → +10, >10% → +5, >0 → 0, else -10
- ROE: >20% → +10, >10% → +5
- Current ratio: >2 → +5, >1 → 0, else -10
- D/E: <0.5 → +5, <1 → 0, <2 → -5, else -10

### Growth (20% weight)
- Base: 50
- Revenue growth: >30% → +25, >20% → +15, >10% → +10, >5% → +5, else -10
- +min(analyst_upside × 40, 15)
- +5 if 20D price change positive

### Technicals (15% weight)
- Base: 50
- +5 if above SMA20, +5 if above SMA50
- Bollinger position: 30-70% → +10, >90% → -10, <10% → +5
- RSI: 40-65 → +10, >75 → -10
- +10 if MACD histogram positive
- +5 if volume ratio >1.2x
- 52W high proximity: >-10% → +10, >-20% → +5, >-40% → 0, else -10

### Verdict Thresholds
- ≥75: **STRONG BUY** 🟢
- ≥60: **BUY** 🟢
- ≥45: **HOLD** 🟡
- ≥30: **WEAK** 🔴
- <30: **AVOID** 🔴

## Options Analysis

When options are requested, pull the chain for the nearest 3 expirations and propose 2-4 trades:

1. **Bull call spread** (debit) — for momentum plays. Buy ATM call, sell OTM call. Capped risk.
2. **Bull put credit spread** — sell fear in high-IV environments. Sell ATM/OTM put, buy lower put.
3. **Weekly lotto call** — small-size directional bet on catalysts. Size for 100% loss.
4. **Put credit spread (weekly)** — premium selling on momentum days.

Apply the vertical spread playbook from wolf-trading-agent when evaluating:
- High IV → credit spreads favored
- Low IV → debit spreads favored
- Max loss check: >2% of account → tighten to 1.5% width

## Presentation Format

Structure the report in this order:
1. Company overview (1 line)
2. Price & momentum snapshot
3. Last 5 days table
4. Technicals (RSI, MACD, BB, SMA positioning)
5. Fundamentals (margins, valuation, balance sheet)
6. Analyst consensus
7. Short interest
8. News catalysts (if scraped)
9. Bull/bear signal summary
10. Composite quant score (if computed)

Keep it data-dense. No fluff. Dwayne prefers bullet points over paragraphs.

## Pitfalls

### yfinance / Python
- **yfinance is UNRELIABLE for real-time prices** — returns stale/cached data during rate limits (which happen frequently). User confirmed "price data is way off" (2026-05-29). **Use Alpaca for real-time prices** (`StockLatestTradeRequest`), keep yfinance for fundamentals only.
- **yfinance options chain hits rate limits** — `t.options` and `t.option_chain()` throw `YFRateLimitError` frequently. Use Alpaca's `OptionChainRequest` instead — returns real Greeks and IV on free tier. See `references/alpaca-data-setup.md` or wolf-trading-agent `references/alpaca-options-chain.md`.
- **For quick ticker identification** — use Nasdaq API (`api.nasdaq.com/api/quote/TICKER/info?assetclass=stocks`), no auth needed. Returns company name, exchange, real-time price, 52W range. Faster than yfinance for lookups.
- **execute_code cannot use `terminal`** — it's not available in that sandbox. Use `terminal()` tool directly for yfinance scripts, or write a .py file and run it.
- **Bitwise `&` on pandas in shell heredocs** — the `&` gets interpreted as backgrounding. Write to a .py file first, then execute.
- **String multiplication with floats** — `"#" * (v // 5)` fails if v is a float. Cast to int first: `"#" * int(v // 5)`.
- **yfinance returns empty on some tickers** — always check `hist.empty` before processing.

### News Scraping
- Yahoo Finance news page returns 429 (rate limited) frequently. Use `marketwatch.com/investing/stock/TICKER` as primary news source.
- StockTwits returns 403 (blocked). Don't bother.
- Seeking Alpha requires JS rendering — use scrapling browser tools, not bulk_get.
- TipRanks and GuruFocus are reliable via bulk_get for recent headlines.

### Options Data
- yfinance options chain may be empty for small-cap tickers.
- IV on weeklies can be 200-300%+ — always note this is a volatility premium, not a directional signal.
- Check bid-ask spread — if spread > 30% of midprice, the option is illiquid. Warn the user.

### Scoring Model
- The model is calibrated for US-listed equities. REITs, MLPs, and financial companies with unusual capital structures may score oddly on the quality factor.
- A stock can score BUY on momentum while scoring AVOID on value — present both, let the user decide which factor matters more for their timeframe.
- The scoring model doesn't account for sector rotation, macro regime, or correlation. It's a single-stock factor model.

## Files

```
scripts/
  quant_scan.py    # Full quant scan: technicals + fundamentals + composite score
references/
  scoring-model.md # Detailed scoring rubric with edge cases
  alpaca-data-setup.md  # Alpaca real-time prices + options chain setup
```

## Verification

```bash
# Test with a known ticker
python3 ~/.hermes/skills/trading/quant-stock-scanner/scripts/quant_scan.py NVDA --score-only

# Test options chain pull
python3 ~/.hermes/skills/trading/quant-stock-scanner/scripts/quant_scan.py AAPL --options
```
