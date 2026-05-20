# Massive.com — Stock Market Data API

**URL:** https://massive.com | **Docs:** https://massive.com/docs

## Overview

Free-tier stock market data API with real-time and historical tick data, REST + WebSocket, JSON + CSV.

**Products covered:** Stocks, Options, Indices, Currencies, Futures
**Data scope:** All US Exchanges + Darkpools

## API Path Structure

The API lives on the main domain (NOT a subdomain):
```
GET massive.com/v1/quote/AAPL
GET massive.com/v1/snapshot?symbols=AAPL,TSLA
```

Auth method and exact header format still being determined. API key format observed: `0x...`.

## Comparison to Alpaca Free Tier

| Feature | Alpaca Free | Massive Free |
|---------|------------|--------------|
| Quotes | ✅ | ✅ |
| Minute bars | ❌ (403 — paid plan) | ? |
| Options data | ✅ (contract lookup) | ✅ (all trades + quotes) |
| Multi-leg options | ❌ | ? |
| Paper trading | ✅ | ❌ (data only) |

Massive could complement Alpaca by providing richer options data and volume metrics that Alpaca's free tier blocks.

## Status

- API key obtained (`0xLbuvp...`) — 2026-05-01
- All test requests return 404 — possibly needs account activation or specific auth header
- Docs are JS-rendered (Next.js), need browser access to read
- Pending: complete auth setup and integrate into Wolf scanner as data source
