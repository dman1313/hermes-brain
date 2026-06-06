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

## Limitations

- **No historical OHLCV** — only current snapshot. Can't compute RSI, MACD, SMA.
- **No options data** — the Nasdaq option-chain endpoint is unreliable (often returns empty).
- **No % change** — the `pctChange` field frequently returns `N/A`.
- **Rate limit**: ~30 req/min is safe. More aggressive and you may get 429.
- **No analyst ratings, no fundamentals beyond P/E/EPS/Market Cap**.

## When to Use

Use this when yfinance raises `YFRateLimitError`. Order of fallback:

1. **Alpaca StockSnapshot** (if creds available) — best for price + real-time
2. **Nasdaq API** — good for price + fundamentals, no auth needed
3. **yfinance with sleep delays** — after a 60s cooldown

The Nasdaq API is especially useful for quick pre-scan ticker checks: "Is this ticker real? What's the price? Market cap?" — faster than yfinance (no cookie/crumb dance) and works every time.
