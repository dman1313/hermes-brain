---
name: market-regime
description: "Detect current market regime using Massive API data — bull/bear/ranging/volatile/recovery/bubble classification with recommended strategies. Replaces ruflo neural-trader regime detection."
version: 1.0.0
author: Hermes Agent
license: MIT
tags: [trading, regime, market-classification, rsi, macd, adx, vix, massive-api]
category: trading
triggers:
  - "detect market regime"
  - "what regime is SYMBOL in"
  - "regime classification"
  - "market environment analysis"
---

# Market Regime Detector

Classifies the current market regime (bull/bear/ranging/volatile/recovery/bubble) using Massive API data and a multi-factor scoring system. Replaces the ruflo `neural-trader --regime-detect` CLI and `neural_predict`/`memory_search` MCP calls with direct Python HTTP requests and deterministic classification logic.

## Usage

```bash
# Default (SPY)
python3 ~/.hermes/skills/trading/market-regime/scripts/market_regime.py

# Specific symbol
python3 ~/.hermes/skills/trading/market-regime/scripts/market_regime.py --symbol AAPL

# Multiple symbols
python3 ~/.hermes/skills/trading/market-regime/scripts/market_regime.py --symbols AAPL,MSFT,GOOGL,SPY
```

## What It Does

1. **Fetches 200 days of OHLCV data** from Massive API for each symbol
2. **Fetches macro data** from FRED API (VIXCLS series) for volatility context
3. **Calculates technical indicators**: RSI(14), MACD(12,26,9), Bollinger Bands(20,2), ADX(14), SMA crossovers
4. **Scores each regime type** using a decision-rule system with weighted features:
   - **Bull** (uptrend): price above all SMAs, positive MACD, rising price
   - **Bear** (downtrend): price below SMAs, negative MACD, falling price
   - **Ranging** (sideways): low ADX (<25), neutral RSI, flat price
   - **Volatile** (extreme): high VIX (>30), high daily volatility, extreme RSI
   - **Recovery** (bouncing): positive 20d return but negative 50d
   - **Bubble** (extended): >30% 200d return, RSI > 75, VIX < 12
5. **Returns**: regime classification, confidence score, recommended strategies, caution notes
6. **Saves results** to `/home/ubuntu/trading-data/regime-{SYMBOL}-{TIMESTAMP}.json`

## Regime Definitions

| Regime | Description | Recommended Strategies | Caution |
|---|---|---|---|
| BULL 🟢 | Strong uptrend | Trend-following, momentum, long-biased | Overbought possible |
| BEAR 🔴 | Strong downtrend | Short-biased, put-credit, defensive | Don't catch knives |
| RANGING 🟡 | Sideways | Mean-reversion, iron-condors | Breakout risk |
| VOLATILE 🟠 | High uncertainty | Long-straddles, strangles | Cut size 50% |
| RECOVERY 🔵 | Bouncing from lows | Dip-buying, bull-put-spreads | Retest possible |
| BUBBLE 💎 | Extended rally | Profit-taking, trailing stops | Don't short it |

## Scoring Features

The classifier uses these features weighted per regime:
- SMA position: 20/50/200 crossover status
- RSI value and zone (oversold/neutral/overbought)
- MACD histogram sign
- Bollinger Band % position
- ADX trend strength
- 20d, 50d, 200d price changes
- VIX level

## Dependencies

- Python 3.8+
- Standard library only (urllib, json, os, sys)

## Files

```
scripts/
  market_regime.py      # Main regime detection script
```

## Pitfalls

- **VIX data from FRED**: The FRED API has VIXCLS as a daily series that may lag by a day. For real-time VIX, use an alternative source.
- **Minimum data**: Requires at least 50 bars of price data. Shorter timeframes may produce unreliable classifications.
- **No portfolio-level regime**: This analyzes individual symbols. Market-wide regime (e.g. SPY for US equities) is a proxy for everything.
- **Decision rules vs ML**: This uses deterministic scoring, not ML. For production, consider training a classifier on labeled regime data.
- **Massive API limits**: Free tiers may throttle. Space out multi-symbol scans.

## Verification

```bash
# Test with SPY (default)
python3 ~/.hermes/skills/trading/market-regime/scripts/market_regime.py --symbol SPY

# Check saved output
cat /home/ubuntu/trading-data/regime-SPY-*.json | python3 -m json.tool | head -20
```
