# Nasdaq API Fallback (when yfinance is rate-limited)

yfinance (`YFRateLimitError`) fails frequently. Nasdaq's public API provides **price, fundamentals (P/E, EPS, market cap, 52W range, volume)** without authentication — usable as a drop-in fallback.

## Stock Info

```
GET https://api.nasdaq.com/api/quote/{ticker}/info?assetclass=stocks
```

Returns: price, net change, volume, 52W high/low, company name, exchange.

**Headers:** `User-Agent: Mozilla/5.0` only (no auth).

```python
import urllib.request, json

url = f'https://api.nasdaq.com/api/quote/{ticker}/info?assetclass=stocks'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
data = json.loads(urllib.request.urlopen(req, timeout=10).read())
d = data.get('data', {})

price = d['primaryData']['lastSalePrice']
change = d['primaryData']['netChange']
volume = d['primaryData']['volume']
wk_high = d['primaryData']['fiftyTwoWeekHigh']
name = d['companyName']
```

## Key Stats / Summary

```
GET https://api.nasdaq.com/api/quote/{ticker}/summary?assetclass=stocks
```

Returns `summaryData` array with label/value pairs including: P/E Ratio, EPS, Market Cap, Previous Close, Open, Day Range, Volume, Avg Volume, 52W High, 52W Low.

```python
url2 = f'https://api.nasdaq.com/api/quote/{ticker}/summary?assetclass=stocks'
data2 = json.loads(...)
for item in data2['data']['summaryData']:
    print(f"{item['label']}: {item['value']}")
```

## 🚨 Reliability Issue: `info` Endpoint Live Prices

The `info` endpoint (`GET /api/quote/{ticker}/info`) returned a **stale/wrong live price** for $MU in June 2026: it reported $1,133.99 when the real price was ~$1,043 (confirmed via Nasdaq `summary` endpoint's Previous Close). The `lastSalePrice` field on this endpoint should **NOT** be trusted for live pricing — it may be the previous day's close, a stale snapshot, or misparsed data.

**Use the `summary` endpoint for fundamentals** (P/E, EPS, Market Cap, Previous Close, 52W range, Volume — these are reliable). But get live prices from a different source.

## Limitations

- ⚠️ **`info` endpoint live prices can be wrong** — do NOT use `lastSalePrice` from `/info` for trading decisions. Use the `summary` endpoint for Previous Close instead.
- **No historical OHLCV** — only current snapshot. Can't compute RSI, MACD, SMA.
- **No options data** — the Nasdaq option-chain endpoint is unreliable (often returns empty).
- **No % change** — the `pctChange` field frequently returns `N/A` or is missing.
- **Rate limit**: ~30 req/min is safe. More aggressive and you may get 429.
- **No analyst ratings, no fundamentals beyond P/E/EPS/Market Cap**.
- **No real-time % change** — must compute from (current price / prev close) manually.

## Four-Tier Data Sourcing Fallback Chain

When yfinance raises `YFRateLimitError`, follow this order:

| Tier | Source | What You Get | Auth | Reliability |
|------|--------|-------------|------|-------------|
| 1 | **Alpaca StockLatestTrade** | Live price (real-time) | `~/alpaca-bot/.env` | ✅ Best |
| 2 | **Nasdaq Summary** | Prev Close, P/E, EPS, Mkt Cap, 52W, Vol | None | ✅ Fundamentals |
| 3 | **Yahoo finance (after cooldown)** | Historical OHLCV | Cookie | ⚠️ After 60s pause |
| 4 | **Google Finance scrape** | Last resort display price | None | ❌ Unreliable |

### Tier 1: Alpaca StockLatestTrade (best — real-time, reliable)
```python
from alpaca.data import StockHistoricalDataClient
from alpaca.data.requests import StockLatestTradeRequest
import os; from dotenv import load_dotenv
load_dotenv(os.path.expanduser('~/alpaca-bot/.env'))
client = StockHistoricalDataClient(os.getenv('ALPACA_API_KEY'), os.getenv('ALPACA_SECRET_KEY'))
trade = client.get_stock_latest_trade(StockLatestTradeRequest(symbol_or_symbols=['MU']))
price = trade['MU'].price
```
**Note:** `alpaca-py` is installed under Python 3.12 at `/usr/bin/python3` or `~/.local/bin/python3.12`, NOT in the Hermes venv (3.11). Use `python3.12` or `/usr/bin/python3` explicitly. If Alpaca import fails, fall through to Tier 2.

### Tier 2: Nasdaq Summary (fundamentals — P/E, EPS, Market Cap, Prev Close)
```python
import urllib.request, json
url = f'https://api.nasdaq.com/api/quote/{ticker}/summary?assetclass=stocks'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
data = json.loads(urllib.request.urlopen(req, timeout=10).read())
items = data.get('data', {}).get('summaryData', {})
# Each item is {'label': 'Previous Close', 'value': '$1,043.19'}
for k, v in items.items():
    label = v.get('label', k)
    value = v.get('value', '?')
```
The `summary` endpoint returns `{label, value}` objects — better for fundamentals than the `info` endpoint. Returns: Previous Close, Market Cap, 52W High/Low, Share Volume, Average Volume, Annualized Dividend, Sector/Industry.

### Tier 3: Alpaca StockSnapshot (fallback volume check)
When Alpaca StockLatestTrade fails (auth issue), try StockSnapshotRequest for volume data:
```python
from alpaca.data.requests import StockSnapshotRequest
snap = client.get_stock_snapshot(StockSnapshotRequest(symbol_or_symbols=['MU']))
vol = snap['MU'].daily_bar.volume
```

### Tier 4: Google Finance scrape (last resort)
Unreliable — may return JS-rendered pages or captchas. Only use when all other sources are blocked.

## When to Use

Use this when yfinance raises `YFRateLimitError`. The Nasdaq API is especially useful for quick pre-scan ticker checks: "Is this ticker real? What's the P/E? Market cap?" — faster than yfinance (no cookie/crumb dance) and works every time for fundamentals.

**Rule of thumb:** Get live prices from Alpaca, get fundamentals from Nasdaq Summary, keep yfinance for historical OHLCV (after a 60s cooldown).
