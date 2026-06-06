# Alpaca Stock Snapshots — Real-Time Prices (Free Tier)

Confirmed working 2026-06-04. yfinance was rate-limited from the VPS — Alpaca snapshots worked instantly.

## Quick Price + Volume Check

```python
import os, json
from dotenv import load_dotenv
load_dotenv('/home/ubuntu/alpaca-bot/.env')

API_KEY = os.getenv('ALPACA_API_KEY')
SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')

import urllib.request

def stock_snapshot(symbol):
    """Get real-time price + daily volume for a stock."""
    url = f'https://data.alpaca.markets/v2/stocks/{symbol}/snapshot'
    req = urllib.request.Request(url, headers={
        'APCA-API-KEY-ID': API_KEY,
        'APCA-API-SECRET-KEY': SECRET_KEY
    })
    data = json.loads(urllib.request.urlopen(req, timeout=15).read())
    trade = data.get('latestTrade', {})
    bar = data.get('dailyBar', {})
    return {
        'price': trade.get('p', 0),
        'volume': bar.get('v', 0),
        'prev_close': bar.get('c', 0)
    }
```

## Batch Price Check

```python
symbols = ['MU', 'NFLX', 'META', 'HOOD', 'ARM']
for sym in symbols:
    snap = stock_snapshot(sym)
    change = ((snap['price'] - snap['prev_close']) / snap['prev_close']) * 100 if snap['prev_close'] else 0
    print(f"{sym:6s} | ${snap['price']:<8.2f} | vol {snap['volume']:<10,} | {change:+.2f}%")
```

## What Works vs Doesn't

| Field | Endpoint | Works on Free? |
|-------|----------|----------------|
| Current price | StockSnapshot.latestTrade.p | ✅ |
| Daily volume | StockSnapshot.dailyBar.v | ✅ |
| Previous close | StockSnapshot.dailyBar.c | ✅ |
| Historical bars | StockBarsRequest | ❌ (403 on all timeframes) |
| Options volume/OI | OptionsSnapshot | ❌ (no daily_bar) |
| Options Greeks/IV | OptionsSnapshot | ✅ |
| Options quotes | OptionsSnapshot.latestQuote | ✅ |

## When to Use vs Nasdaq API

- **Alpaca snapshots**: When you need% change, have many tickers, need volume data
- **Nasdaq API** (`api.nasdaq.com/api/quote/TICKER/info`): When Alpaca is down or you just need a quick name + price check with no auth. No % change on Nasdaq's info endpoint.
