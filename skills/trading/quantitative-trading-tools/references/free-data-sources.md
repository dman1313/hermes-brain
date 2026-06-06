# Free Financial Data Sources (verified June 2026)

Tested from the Hermes VPS. Status reflects what actually responded.

## No Auth Needed -- Working

| Source | What | Endpoint | Notes |
|--------|------|----------|-------|
| CoinGecko | Crypto prices, trending, market data | api.coingecko.com/api/v3/ | Best free crypto API |
| Coinpaprika | Global crypto stats | api.coinpaprika.com/v1/global | BTC dominance, total mcap |
| Binance | Real-time crypto tickers | api.binance.com/api/v3/ticker/24hr | No key for market data |
| SEC EDGAR | Company filings | efts.sec.gov/LATEST/search-index | Requires User-Agent header |
| World Bank | Macro data | api.worldbank.org/v2/ | GDP, population, etc |
| Twelve Data | Stock OHLCV | api.twelvedata.com | 15 req/min free, no key basic |
| Polymarket CLOB | Prediction markets | clob.polymarket.com/markets | Already integrated |
| Kalshi | Event contracts | api.elections.kalshi.com/trade-api/v2/events | US-regulated prediction markets |

## Free API Key -- Working

| Source | What | Signup | Rate Limit |
|--------|------|--------|------------|
| FRED | 800K+ economic time series | fred.stlouisfed.org/docs/api/api_key.html | Generous |
| Massive.com | US stocks OHLCV, technicals, news | massive.com (Google OAuth) | 5 calls/min free |
| MarketAux | Stock news + sentiment | marketaux.com | 100 req/day |
| Alpha Vantage | Stocks + forex + crypto | alphavantage.co/support/#api-key | 25 req/day free |
| Finnhub | Stocks, crypto, news | finnhub.io | 60 calls/min free |

## Dead/Blocked from VPS (June 2026)

- CoinCap -- DNS resolution fails
- Messari -- API endpoint changed (404)
- WSB Sentiment (tradestie.com) -- Cloudflare 403
- BLS (Bureau of Labor Statistics) -- timeout
- Metaculus -- endpoint changed
- Helium (heliumtrades.com) -- DNS fails

## Key Technique: Massive Grouped Endpoint

For batch scanning all US stocks, use ONE call:
  GET /v2/aggs/grouped/locale/us/market/stocks/{date}
Returns OHLCV for 12K+ tickers. Filter client-side by volume, pct change, dollar volume. Free-tier friendly (1 call vs thousands).
