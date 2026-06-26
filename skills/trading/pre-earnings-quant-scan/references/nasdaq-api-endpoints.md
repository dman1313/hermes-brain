# Nasdaq API Endpoints Reference

Consolidated notes on which Nasdaq API endpoints work and which don't for US equity data.

## Summary Table

| Endpoint | URL Suffix | Works For | Notes |
|----------|-----------|-----------|-------|
| Info | `/quote/{TICKER}/info?assetclass=stocks` | Company name, exchange | Price is STALE — do not use for current price |
| Summary | `/quote/{TICKER}/summary?assetclass=stocks` | ✅ Price, 52w range, volume, analyst target, market cap | Best source for fundamentals |
| Key Stats | `/quote/{TICKER}/key-statistics?assetclass=stocks` | ❌ Returns empty for most tickers | Skip |
| Options Chain | `/quote/{TICKER}/option-chain?assetclass=stocks&fromdate=...&todate=...&limit=50` | ⚠️ Partial | Returns split-adjusted strikes for post-split stocks (e.g. MU $35-$525 for actual $1,043 price). May miss ATM strikes. |
| Earnings Calendar | `/api/calendar/earnings?date=YYYY-MM-DD` | ⚠️ Partial | Results may not include the ticker you want. Search results are paginated/limited. |
| Analyst Research | `/quote/{TICKER}/analyst-research?assetclass=stocks` | ❌ Returns empty | No useful data |
| Holdings (ETF) | `/quote/{TICKER}/holdings?assetclass=etf` | ❌ Returns empty/malformed | Holdings are loaded client-side on Nasdaq.com, not available via API |
| Real-time Quote | `/quote/{TICKER}/realtime?assetclass=stocks` | ❌ 404 | Not a real endpoint |

## Working Pattern

```python
import urllib.request, json, time
time.sleep(1)  # Rate limit: 1 req/s minimum
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'}

# GET FUNDAMENTALS (reliable)
req = urllib.request.Request(
    'https://api.nasdaq.com/api/quote/MU/summary?assetclass=stocks',
    headers=headers
)
data = json.loads(urllib.request.urlopen(req, timeout=10).read())
summary = data.get('data', {}).get('summaryData', {})
for k, v in summary.items():
    if isinstance(v, dict):
        print(f'{v.get("label",k)}: {v.get("value","?")}')

# GET OPTIONS CHAIN (may have split-adjusted strikes)
req = urllib.request.Request(
    'https://api.nasdaq.com/api/quote/MU/option-chain?assetclass=stocks&fromdate=2026-06-25&todate=2026-06-26&limit=50',
    headers=headers
)
data = json.loads(urllib.request.urlopen(req, timeout=10).read())
rows = data.get('data', {}).get('table', {}).get('rows', [])

# GET COMPANY NAME
req = urllib.request.Request(
    'https://api.nasdaq.com/api/quote/MU/info?assetclass=stocks',
    headers=headers
)
data = json.loads(urllib.request.urlopen(req, timeout=10).read())
name = data.get('data', {}).get('companyName', '?')
```

## Known Issues

- **Info endpoint price is stale** — for MU it returned $1,133.99 when actual price was $1,043.19. Never use `lastSalePrice` from the `info` endpoint.
- **Options strikes are pre-split** — for stocks that have split, the `strike` field in options chain data may still show pre-split values. Alpaca options data handles splits correctly.
- **No auth required** — all endpoints work without authentication on free tier
- **Rate limit** — ~1 request per second is safe; 429 errors mean wait and retry
