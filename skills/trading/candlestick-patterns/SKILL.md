---
name: candlestick-patterns
description: "Detect and classify candlestick patterns from Massive API OHLCV data — doji, hammer, engulfing, morning/evening star, head & shoulders, double top/bottom. Replaces ruflo market-pattern skill."
version: 1.0.0
author: Hermes Agent
license: MIT
tags: [trading, patterns, candlestick, technical-analysis, doji, engulfing, head-shoulders, massive-api]
category: trading
triggers:
  - "scan candlestick patterns on SYMBOL"
  - "detect chart patterns"
  - "pattern scan"
  - "what patterns do you see on SYMBOL"
---

# Candlestick Pattern Scanner

Detects and classifies candlestick patterns from Massive API OHLCV data. Runs entirely in Python with no external dependencies. Replaces ruflo's `market-pattern` skill and its `memory_search`/`memory_list`/`agentdb_pattern-*` MCP calls.

## Usage

```bash
# Single symbol
python3 ~/.hermes/skills/trading/candlestick-patterns/scripts/candlestick_patterns.py --symbol AAPL

# Multiple symbols
python3 ~/.hermes/skills/trading/candlestick-patterns/scripts/candlestick_patterns.py --symbols AAPL,MSFT,GOOGL

# Custom lookback period
python3 ~/.hermes/skills/trading/candlestick-patterns/scripts/candlestick_patterns.py --symbol SPY --periods 200
```

## What It Does

1. **Fetches OHLCV data** from Massive API
2. **Scans for single-candle patterns** (last 20 candles):
   - **Doji**: open ≈ close — indecision
   - **Hammer**: small body, long lower wick — potential bullish reversal
   - **Inverted hammer**: small body, long upper wick — potential bottom
3. **Two-candle patterns** (last 10 pairs):
   - **Bullish engulfing**: green candle engulfs red — strong buy signal
   - **Bearish engulfing**: red candle engulfs green — strong sell signal
4. **Three-candle patterns**:
   - **Morning star**: red → small → green — bullish reversal
   - **Evening star**: green → small → red — bearish reversal
   - **Three white soldiers**: 3 consecutive tall green candles — strong buying
   - **Three black crows**: 3 consecutive tall red candles — strong selling
5. **Multi-candle patterns**:
   - **Head & shoulders**: 3 peaks with middle highest — bearish top reversal
   - **Double top**: 2 peaks at similar level — bearish
   - **Double bottom**: 2 dips at similar level — bullish
6. **Ranks patterns** by reliability score descending
7. **Saves results** to `/home/ubuntu/trading-data/patterns-{SYMBOL}-{TIMESTAMP}.json`

## Pattern Reliability Guide

| Pattern | Reliability | Type | Notes |
|---|---|---|---|
| Morning star | 0.80 | Reversal | One of the most reliable bullish reversals |
| Evening star | 0.80 | Reversal | One of the most reliable bearish reversals |
| Three white soldiers | 0.75 | Continuation | Strong sustained buying |
| Three black crows | 0.75 | Continuation | Strong sustained selling |
| Bullish/bearish engulfing | 0.70 | Reversal | More reliable on higher timeframes |
| Head & shoulders | 0.70 | Reversal | Classic top pattern |
| Double top/bottom | 0.65 | Reversal | Requires volume confirmation |
| Hammer | 0.60 | Reversal | Best after a downtrend |
| Doji | 0.50 | Reversal | Neutral — context dependent |

## Output Format

```json
{
  "symbol": "AAPL",
  "timestamp": "2026-06-03T20:30:00+00:00",
  "price": 195.50,
  "change_pct": 1.23,
  "patterns_found": 3,
  "patterns": [
    {"pattern": "bullish_engulfing", "type": "reversal", "direction": "bullish", "reliability": 0.7, "note": "..."},
    {"pattern": "doji", "type": "reversal", "direction": "neutral", "reliability": 0.5, "note": "..."},
    {"pattern": "double_bottom", "direction": "bullish", "reliability": 0.65,
     "dip1": 185.0, "dip2": 185.5, "peak": 192.0, "target": 199.0}
  ]
}
```

## Dependencies

- Python 3.8+
- Standard library only

## Files

```
scripts/
  candlestick_patterns.py    # Main pattern detection script
```

## Pitfalls

- **Pattern reliability varies by timeframe**: The reliability scores are rough heuristics. Daily patterns are more significant than intraday.
- **No volume confirmation**: The current implementation doesn't use volume for pattern scoring. Engulfing + high volume is much more significant than low-volume.
- **Head & shoulders detection is simplistic**: Uses a local maxima approach that works well for clear patterns but may miss complex formations.
- **No sector/industry context**: A doji in isolation means little. Context (trend, support/resistance) matters significantly.
- **Massive API data**: Works best on actively traded US equities. Penny stocks and illiquid names may produce unreliable patterns.

## Verification

```bash
# Test with a major stock
python3 ~/.hermes/skills/trading/candlestick-patterns/scripts/candlestick_patterns.py --symbol AAPL

# Check saved output
cat /home/ubuntu/trading-data/patterns-AAPL-*.json | python3 -m json.tool | head -40
```
