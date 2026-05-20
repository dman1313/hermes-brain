# 🔍 API Discovery Scan — 2026-05-14

Scan time: 2026-05-14T14:06:34.117724

## 📊 Summary

**Tested:** 21 endpoints

**✅ Working:** 4
  - Alpha Vantage
  - Twelve Data (RapidAPI)
  - CoinGecko
  - Yahoo Finance (unofficial)

**🔒 Needs Key/Auth:** 14
  - MarketAux
  - Finnhub
  - Twelve Data
  - Polygon.io
  - MarketStack
  - Financial Modeling Prep
  - EOD Historical Data
  - Alpaca Markets
  - IEX Cloud
  - Tiingo
  - Intrinio
  - Stock Data
  - Yahoo Finance (RapidAPI)
  - EOD Historical Data (RapidAPI)

**❌ Dead/Not Found:** 0

**🤔 Other:** 3
  - GNews API
  - OpenFIGI
  - World Trading Data

## 🔬 Detailed Endpoint Tests

  ⚠️ **GNews API** — unexpected-status
     Endpoint: `https://gnews.io/api/v4/search?q=test&lang=en&max=1&token=__KEY__`
     Status: unexpected-status (HTTP 400)
     Notes: HTTP 400 — unexpected.

  🔒 **MarketAux** — forbidden
     Endpoint: `https://api.marketaux.com/v1/news/all?symbols=AAPL,TSLA&filter_entities=true&api`
     Status: forbidden (HTTP 401)
     Notes: HTTP 401 — needs valid API key or subscription.

  ✅ **Alpha Vantage** — working
     Endpoint: `https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=IBM&apikey=TEST_O`
     Status: working (HTTP 200)
     Notes: Endpoint tested and returned expected data.

  🔒 **Finnhub** — forbidden
     Endpoint: `https://finnhub.io/api/v1/quote?symbol=AAPL`
     Status: forbidden (HTTP 401)
     Notes: HTTP 401 — needs valid API key or subscription.

  ⚠️ **Twelve Data** — needs-key
     Endpoint: `https://api.twelvedata.com/quote?symbol=AAPL&apikey=TEST_ONLY`
     Status: needs-key (HTTP 200)
     Notes: Endpoint returned error requesting API key.

  ✅ **Twelve Data (RapidAPI)** — reachable
     Endpoint: `https://rapidapi.com/twelvedata/api/twelve-data`
     Status: reachable (HTTP 200)
     Notes: Endpoint responded with HTTP 200.

  🔒 **Polygon.io** — forbidden
     Endpoint: `https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers/AAPL?apiKey=`
     Status: forbidden (HTTP 401)
     Notes: HTTP 401 — needs valid API key or subscription.

  🔒 **MarketStack** — forbidden
     Endpoint: `https://api.marketstack.com/v1/eod?access_key=TEST_ONLY&symbols=AAPL&limit=1`
     Status: forbidden (HTTP 401)
     Notes: HTTP 401 — needs valid API key or subscription.

  🔒 **Financial Modeling Prep** — forbidden
     Endpoint: `https://financialmodelingprep.com/api/v3/profile/AAPL?apikey=TEST_ONLY`
     Status: forbidden (HTTP 401)
     Notes: HTTP 401 — needs valid API key or subscription.

  🔒 **EOD Historical Data** — forbidden
     Endpoint: `https://eodhd.com/api/eod/AAPL.US?api_token=TEST_ONLY&fmt=json`
     Status: forbidden (HTTP 401)
     Notes: HTTP 401 — needs valid API key or subscription.

  ⏭️ **Alpaca Markets** — needs-auth-header
     Endpoint: `https://paper-api.alpaca.markets/v2/account`
     Status: needs-auth-header (HTTP 0)
     Notes: Requires API key header auth (not currently configured for automated test).

  ✅ **CoinGecko** — working
     Endpoint: `https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd`
     Status: working (HTTP 200)
     Notes: Endpoint tested and returned expected data.

  ⚠️ **OpenFIGI** — unexpected-status
     Endpoint: `https://api.openfigi.com/v3/mapping`
     Status: unexpected-status (HTTP 405)
     Notes: HTTP 405 — unexpected.

  🔒 **IEX Cloud** — forbidden
     Endpoint: `https://cloud.iexapis.com/stable/stock/aapl/quote?token=TEST_ONLY`
     Status: forbidden (HTTP 403)
     Notes: HTTP 403 — needs valid API key or subscription.

  🔒 **Tiingo** — forbidden
     Endpoint: `https://api.tiingo.com/tiingo/daily/aapl/prices?token=TEST_ONLY`
     Status: forbidden (HTTP 403)
     Notes: HTTP 403 — needs valid API key or subscription.

  🔒 **Intrinio** — forbidden
     Endpoint: `https://api-v2.intrinio.com/securities/AAPL/prices?api_key=TEST_ONLY`
     Status: forbidden (HTTP 401)
     Notes: HTTP 401 — needs valid API key or subscription.

  ✅ **Yahoo Finance (unofficial)** — working
     Endpoint: `https://query1.finance.yahoo.com/v8/finance/chart/AAPL?range=1d&interval=1d`
     Status: working (HTTP 200)
     Notes: Endpoint tested and returned expected data.

  🤔 **World Trading Data** — unexpected-format
     Endpoint: `https://api.worldtradingdata.com/api/v1/stock?symbol=AAPL&api_token=TEST_ONLY`
     Status: unexpected-format (HTTP 200)
     Notes: HTTP 200 but response format unexpected (expected 'data' not found).

  🔒 **Stock Data** — forbidden
     Endpoint: `https://api.stockdata.org/v1/data/quote?symbols=AAPL&api_token=TEST_ONLY`
     Status: forbidden (HTTP 401)
     Notes: HTTP 401 — needs valid API key or subscription.

  🔒 **Yahoo Finance (RapidAPI)** — forbidden
     Endpoint: `https://yh-finance.p.rapidapi.com/stock/v2/get-summary?symbol=AAPL`
     Status: forbidden (HTTP 403)
     Notes: HTTP 403 — needs valid API key or subscription.

  🔒 **EOD Historical Data (RapidAPI)** — forbidden
     Endpoint: `https://eodhistoricaldata.com/api/real-time/AAPL.US?api_token=TEST_ONLY&fmt=json`
     Status: forbidden (HTTP 401)
     Notes: HTTP 401 — needs valid API key or subscription.

## 🆕 New/Marketplace Discoveries

  - **Twelve Data (RapidAPI)** (rapidapi) — active-page
    RapidAPI marketplace page.

  - **Alpha Vantage (RapidAPI)** (rapidapi) — active-page
    RapidAPI marketplace page.

  - **FMP (RapidAPI)** (rapidapi) — active-page
    RapidAPI marketplace page.

  - **Yahoo Finance (RapidAPI)** (rapidapi) — active-page
    RapidAPI marketplace page.

  - **Stock Data (RapidAPI)** (rapidapi) — active-page
    RapidAPI marketplace page.

  - **MarketAux (RapidAPI)** (rapidapi) — active-page
    RapidAPI marketplace page.

  - **EOD HD (RapidAPI)** (rapidapi) — active-page
    RapidAPI marketplace page.

  - **World Trading Data (RapidAPI)** (rapidapi) — active-page
    RapidAPI marketplace page.

  - **CTradeExchange/free-quote** (github) — active
    Stars: 124. Updated: 2026-05-07

  - **0xramm/Indian-Stock-Market-API** (github) — active
    Stars: 88. Updated: 2026-05-14

  - **apilayer/marketstack** (github) — active
    Stars: 78. Updated: 2026-05-07

  - **ideas4u/Trading-Platform** (github) — active
    Stars: 21. Updated: 2026-01-23

  - **faysal515/bd-stock-api** (github) — active
    Stars: 20. Updated: 2026-04-22

  - **RomelTorres/alpha_vantage** (github) — active
    Stars: 4815. Updated: 2026-05-14

  - **FinMind/FinMind** (github) — active
    Stars: 2550. Updated: 2026-05-13

  - **Finnhub-Stock-API/finnhub-python** (github) — active
    Stars: 1003. Updated: 2026-05-14

  - **twelvedata/twelvedata-python** (github) — active
    Stars: 717. Updated: 2026-05-13

  - **alltick/alltick-realtime-forex-crypto-stock-tick-finance-websocket-api** (github) — active
    Stars: 565. Updated: 2026-05-12

  - **maximedegreve/TinyFaces** (github) — active
    Stars: 550. Updated: 2026-04-15

  - **5mehulhelp5/MagentoExtensions** (github) — active
    Stars: 121. Updated: 2026-02-04

  - **ZhuJD-China/RainbowGPT** (github) — active
    Stars: 109. Updated: 2026-01-11

## 🧹 Recommendations for Wolf

Sources checked: rapidapi, github

**APIs worth integrating right now (tested working):**
  - Alpha Vantage
  - Twelve Data (RapidAPI)
  - CoinGecko
  - Yahoo Finance (unofficial)

**Could work with a free API key (register → test → integrate):**
  - MarketAux
  - Finnhub
  - Twelve Data
  - Polygon.io
  - MarketStack
  - Financial Modeling Prep
  - EOD Historical Data
  - Alpaca Markets
  - IEX Cloud
  - Tiingo
  - Intrinio
  - Stock Data
  - Yahoo Finance (RapidAPI)
  - EOD Historical Data (RapidAPI)

---
_Generated by Sherlock API Discovery Scanner — endpoint tests are REAL_