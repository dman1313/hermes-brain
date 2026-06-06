---
name: trading-signal
description: "Generate trading signals using Massive API real-time data — anomaly detection, Z-score scoring, and composite signal scoring. Replaces ruflo neural-trader with direct Python/requests."
version: 1.0.0
author: Hermes Agent
license: MIT
tags: [trading, signals, anomaly-detection, rsi, macd, bollinger, massive-api]
category: trading
triggers:
  - "scan for signals"
  - "generate trading signals on SYMBOLS"
  - "signal scan"
  - "check SYMBOLS for entry signals"
---

# Trading Signal Generator

Generates trading signals using Massive API for real-time data, with anomaly detection (Z-score classification into spike/drift/flatline/oscillation), technical indicators (RSI, MACD, Bollinger Bands, ATR), and a composite 0-100 signal score.

Replaces the ruflo `neural-trader` CLI + `memory_store`/`neural_predict`/`agentdb_pattern-search` with direct Python HTTP requests and local file persistence.

## Usage

```bash
# Single symbol
python3 ~/.hermes/skills/trading/trading-signal/scripts/trading_signal.py --symbols AAPL

# Multiple symbols
python3 ~/.hermes/skills/trading/trading-signal/scripts/trading_signal.py --symbols AAPL,MSFT,GOOGL,SPY

# With strategy context for filtering
python3 ~/.hermes/skills/trading/trading-signal/scripts/trading_signal.py --symbols AAPL --strategy mean-reversion
```

## What It Does

1. **Fetches 120 days of OHLCV data** from the Massive API (`/stocks/aggregates` endpoint) for each symbol
2. **Calculates technical indicators**: RSI(14), MACD(12,26,9), Bollinger Bands(20,2), ATR(14)
3. **Detects market anomalies** using Z-score classification:
   - **spike** (maxZ > 2.5 + volume surge): breakout — momentum entry or fade
   - **drift** (sustained directional returns for 4+ bars): trend forming
   - **flatline** (low Z-scores): consolidation — prepare for breakout
   - **oscillation** (alternating signs): range-bound — mean-reversion
   - **normal**: standard price action
4. **Computes composite signal score** (0-100) from RSI, MACD, Bollinger position, ATR, and anomaly type
5. **Saves results** to `/home/ubuntu/trading-data/signal-{SYMBOL}-{TIMESTAMP}.json`

## Signal Score Breakdown

| Score Range | Direction | Action |
|---|---|---|
| 75-100 | STRONG BUY | Enter long / add to position |
| 60-74 | BUY | Accumulate on dips |
| 40-59 | NEUTRAL | Hold / wait |
| 25-39 | SELL | Reduce position |
| 0-24 | STRONG SELL | Exit / short |

## Signal Output Format

```json
{
  "symbol": "AAPL",
  "timestamp": "2026-06-03T20:30:00+00:00",
  "price": 195.50,
  "change_pct": 1.23,
  "direction": "buy",
  "signal_score": 72,
  "confidence": 0.72,
  "anomaly": {
    "type": "drift",
    "confidence": 0.88,
    "max_z": 2.8,
    "details": "Sustained bullish drift (2.8z) — trend forming",
    "direction": "bullish"
  },
  "indicators": {
    "rsi": 58.3,
    "macd": {"macd": 0.45, "signal": 0.32, "histogram": 0.13},
    "bollinger": {"upper": 200.5, "middle": 190.0, "lower": 179.5, "width": 21.0, "position_pct": 62.3},
    "atr": 2.45
  },
  "action": "Accumulate on dips"
}
```

## Configuration

The Massive API key is hardcoded in the script (`MASSIVE_API_KEY`). To use a different key, edit the script or set env var:
```bash
export MASSIVE_API_KEY="your_key_here"
```

## Dependencies

- Python 3.8+
- Standard library only: `requests` (not needed — uses `urllib.request`)

## Files

```
scripts/
  trading_signal.py     # Main signal generation script
```

## Pitfalls

- **Massive API rate limits**: The free tier may have request limits. Space out scans of many symbols.
- **Missing data**: Some tickers may return empty results on Massive. The script handles this gracefully (skips with message).
- **Anomaly detection is heuristic**: The Z-score based detection is a simplified model. For production, consider walking-forward validation on labeled data.
- **120-day default window**: Short for long-term trend analysis. Adjust `days` param in script for your timeframe.
- **No portfolio-level signals**: This scans individual symbols. For portfolio-wide risk, use the `portfolio-risk` skill.

## Verification

```bash
# Quick test with a major index
python3 ~/.hermes/skills/trading/trading-signal/scripts/trading_signal.py --symbols SPY

# Check saved output
cat /home/ubuntu/trading-data/signal-SPY-*.json | python3 -m json.tool | head -30
```
