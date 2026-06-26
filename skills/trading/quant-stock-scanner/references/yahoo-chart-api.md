# Yahoo Finance Chart API (yfinance Bypass)

When yfinance raises `YFRateLimitError`, Yahoo's direct chart API works via the same endpoint yfinance uses internally — just with raw HTTP and proper `User-Agent` headers. This is the **most reliable fallback for historical OHLCV** (needed for RSI, MACD, SMA, Bollinger, etc.).

## Endpoint

```
GET https://query1.finance.yahoo.com/v8/finance/chart/{TICKER}?range=6mo&interval=1d
```

**Headers:** `User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36`

**No auth, no cookie, no crumb needed for the chart endpoint.** This is the same API the yfinance library calls under the hood. The `range` parameter supports: `1d`, `5d`, `1mo`, `3mo`, `6mo`, `1ytd`, `1y`, `2y`, `5y`, `max`.

## Rate Limits

The chart endpoint is more forgiving than the `quoteSummary` endpoint. You can get ~5-10 tickers per minute via curl before hitting 429. After a 429, wait 60s and retry.

The `quoteSummary` endpoint (`v10/finance/quoteSummary`) **requires a crumb** and is blocked without it. The chart endpoint (`v8/finance/chart`) does NOT require a crumb — use it instead.

## Shell Pipeline

```bash
curl -sL 'https://query1.finance.yahoo.com/v8/finance/chart/MSTR?range=6mo&interval=1d' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36' \
  | python3 -c "
import sys, json
data = json.load(sys.stdin)
r = data['chart']['result'][0]
ts = r['timestamp']
q = r['indicators']['quote'][0]
closes = q['close']
volumes = q['volume']
highs = q['high']
lows = q['low']
print(f'Days: {len(ts)}, Last: {closes[-1]:.2f}')
"
```

## Response Structure

```json
{
  "chart": {
    "result": [{
      "meta": {
        "currency": "USD",
        "symbol": "MSTR",
        "regularMarketPrice": 109.46,
        "fiftyTwoWeekHigh": 457.22,
        "fiftyTwoWeekLow": 104.17,
        "regularMarketDayHigh": 120.0,
        "regularMarketDayLow": 107.31,
        "regularMarketVolume": 23640399,
        "chartPreviousClose": 164.32,
        "exchangeName": "NMS"
      },
      "timestamp": [...],  // Unix timestamps
      "indicators": {
        "quote": [{
          "open": [...],
          "high": [...],
          "low": [...],
          "close": [...],
          "volume": [...]
        }]
      }
    }]
  }
}
```

## Computing Technicals from Chart Data

Use raw Python (no pandas/yfinance dependency) from the JSON response. The chart data is clean — no NaN gaps for active tickers.

**Python computation (no pandas needed):**

```python
closes = q['close']  # array of floats

# SMAs
sma20 = sum(closes[-20:]) / 20
sma50 = sum(closes[-50:]) / 50 if len(closes) >= 50 else None

# RSI(14)
gains = [max(closes[i]-closes[i-1], 0) for i in range(1, len(closes))]
losses = [max(closes[i-1]-closes[i], 0) for i in range(1, len(closes))]
avg_gain = sum(gains[-14:]) / 14
avg_loss = sum(losses[-14:]) / 14
rsi = 100 - 100 / (1 + avg_gain/avg_loss) if avg_loss > 0 else 100

# MACD
def ema(data, period):
    result = [data[0]]
    mult = 2 / (period + 1)
    for v in data[1:]:
        result.append(v * mult + result[-1] * (1 - mult))
    return result

ema12 = ema(closes, 12)
ema26 = ema(closes, 26)
macd_line = [a - b for a, b in zip(ema12, ema26)]
signal = [macd_line[0]]
for m in macd_line[1:]:
    signal.append(m * 0.2 + signal[-1] * 0.8)
macd_hist = macd_line[-1] - signal[-1]

# Bollinger
bb_std = (sum((c - sma20)**2 for c in closes[-20:]) / 20) ** 0.5
bb_upper = sma20 + 2 * bb_std
bb_lower = sma20 - 2 * bb_std
bb_pos = (closes[-1] - bb_lower) / (bb_upper - bb_lower) * 100

# Volume ratio
avg_vol_20 = sum(volumes[-20:]) / 20
vol_ratio = volumes[-1] / avg_vol_20 if avg_vol_20 > 0 else 0
```

## When to Use

Use this as **Tier 1 for historical data** when yfinance is rate-limited. The chart endpoint:
- ✅ Works without crumb/cookie
- ✅ Returns clean OHLCV for any US ticker
- ✅ Includes 52W high/low in meta
- ❌ Does NOT return fundamentals (P/E, EPS, etc.) — use Nasdaq API for that
- ❌ Does NOT return options chain

## Data Sourcing Flow (Revised)

```
1. Yahoo Chart API  → Historical OHLCV (technicals: RSI, MACD, SMA, BB)
2. Nasdaq Summary   → Fundamentals (P/E, EPS, Market Cap, 52W range)
3. Alpaca           → Real-time price + options chain
4. Raw Python calc  → All technical indicators (no yfinance/pandas needed)
```

This flow avoids yfinance entirely when it's rate-limited, and works with only `curl` + `python3` — no pip dependencies needed.
