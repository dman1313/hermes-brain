# Alpaca Real-Time Data Setup

Use Alpaca for real-time prices and options data. yfinance for fundamentals only.

## Credentials

```python
import sys, os
sys.path.insert(0, '/home/ubuntu/alpaca-bot')
from dotenv import load_dotenv
load_dotenv('/home/ubuntu/alpaca-bot/.env')

key = os.environ['ALPACA_API_KEY']
secret = os.environ['ALPACA_SECRET_KEY']
```

## Real-Time Price

```python
from alpaca.data import StockHistoricalDataClient
from alpaca.data.requests import StockLatestTradeRequest

client = StockHistoricalDataClient(key, secret)
trade = client.get_stock_latest_trade(StockLatestTradeRequest(symbol_or_symbols='AAPL'))
price = trade['AAPL'].price
timestamp = trade['AAPL'].timestamp
```

## Options Chain (with Greeks)

```python
from alpaca.data import OptionHistoricalDataClient
from alpaca.data.requests import OptionChainRequest

opt_client = OptionHistoricalDataClient(key, secret)
chain = opt_client.get_option_chain(OptionChainRequest(
    underlying_symbol='AAPL',
    expiration_date_gte='2026-06-06',
    expiration_date_lte='2026-06-27',
    type='put',
))

# chain = dict of OCC symbol → {latest_quote, greeks, implied_volatility}
for sym, data in chain.items():
    q = data.latest_quote
    delta = data.greeks.delta if data.greeks else None
    iv = data.implied_volatility
```

### OCC Symbol Format

`AAPL260612P00310000` = `TICKER` + `YYMMDD` + `C/P` + `STRIKE×1000` (8 digits, zero-padded)

Parse:
```python
strike = float(occ_sym[-8:]) / 1000
exp_date_str = f"20{occ_sym[4:10]}"  # "20260612"
option_type = occ_sym[10]  # 'C' or 'P'
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

No auth required. Returns real-time bid/ask, volume, and company name. Good for quick lookups when you don't need full OHLCV data.

## What Works on Free Tier

| Feature | Status |
|---------|--------|
| Latest trade/quote | ✅ Unlimited |
| Historical bars (1D+) | ✅ Works |
| Minute bars | ❌ 403 on free tier |
| Options chain | ✅ Works (300+ options per request) |
| Options Greeks | ✅ Real delta/gamma/theta/vega |
| Paper trading | ✅ Works |
| Nasdaq API (company info) | ✅ No auth needed |
