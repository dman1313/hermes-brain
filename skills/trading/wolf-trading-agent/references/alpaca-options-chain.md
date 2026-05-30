# Alpaca Options Chain API

Working pattern for fetching options chains with real Greeks on Alpaca free tier.

## Setup

```python
import sys
sys.path.insert(0, '/home/ubuntu/alpaca-bot')
from dotenv import load_dotenv
load_dotenv('/home/ubuntu/alpaca-bot/.env')

from alpaca.data import OptionHistoricalDataClient, StockHistoricalDataClient
from alpaca.data.requests import OptionChainRequest, StockLatestTradeRequest
import os

key = os.environ['ALPACA_API_KEY']
secret = os.environ['ALPACA_SECRET_KEY']
```

## Get Real-Time Stock Price

```python
stock_client = StockHistoricalDataClient(key, secret)
trade = stock_client.get_stock_latest_trade(StockLatestTradeRequest(symbol_or_symbols='AAPL'))
price = trade['AAPL'].price  # e.g. 314.03
```

## Get Options Chain

```python
opt_client = OptionHistoricalDataClient(key, secret)
req = OptionChainRequest(
    underlying_symbol='AAPL',
    expiration_date_gte='2026-06-06',
    expiration_date_lte='2026-06-27',
    type='put',  # or 'call'
)
chain = opt_client.get_option_chain(req)
```

Returns `dict` keyed by OCC symbol (e.g. `AAPL260612P00310000`).

## Parse Chain Data

Each value has:
- `.latest_quote` — `.bid_price`, `.ask_price`, `.bid_size`, `.ask_size`, `.timestamp`
- `.latest_trade` — `.price`, `.size`, `.timestamp`
- `.implied_volatility` — float (e.g. 0.229 = 22.9%)
- `.greeks` — `.delta`, `.gamma`, `.theta`, `.vega`, `.rho`

```python
for occ_sym, data in chain.items():
    q = data.latest_quote
    if not q or q.bid_price is None:
        continue
    strike = float(occ_sym[-8:]) / 1000  # OCC format
    greeks = data.greeks
    delta = greeks.delta if greeks else None
    iv = data.implied_volatility
```

## Key Notes

- Free tier supports this (confirmed 2026-05-29). The 403 restriction is on minute bars, not options.
- Chain returns ~300+ options per request for liquid names like AAPL.
- Greeks are real (from Alpaca's pricing model), not estimated.
- Filter to OTM puts: `strike < current_price` for bull put spreads.
- Filter by DTE: parse OCC symbol date portion (`sym[4:10]` → `YYMMDD`).
- Some options have `latest_quote` but no `greeks` or `implied_volatility` (far OTM/illiquid). Always check `data.greeks` before accessing.
- Ask prices on deep OTM options can be stale. Use `latest_quote` which is real-time.

## Bull Put Spread Evaluation

```python
# Find short put ~30 delta
short = min(puts, key=lambda p: abs(p['delta'] - (-0.30)))
# Find buy leg $5-10 below
buy = [p for p in puts if short['strike'] - p['strike'] >= 4 and short['strike'] - p['strike'] <= 12]
buy_put = min(buy, key=lambda p: abs(short['strike'] - p['strike'] - 5))

width = short['strike'] - buy_put['strike']
credit = short['bid'] - buy_put['ask']
max_loss = width - credit
breakeven = short['strike'] - credit
prob_profit = 1 + short['delta']  # delta is negative for puts
```

## Quick Company Lookup (Nasdaq API)

For fast ticker identification without yfinance rate limits:

```python
import json, urllib.request
url = f"https://api.nasdaq.com/api/quote/{TICKER}/info?assetclass=stocks"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
data = json.loads(urllib.request.urlopen(req, timeout=10).read())["data"]

# Returns: companyName, exchange, stockType, primaryData (lastSalePrice, volume, bid/ask)
# Also: keyStats (52W range, day range), notifications
```

No auth required. Returns real-time bid/ask, volume, and company name. Useful for quick lookups when you just need to identify what a ticker is.
