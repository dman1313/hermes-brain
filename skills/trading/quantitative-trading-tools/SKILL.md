---
name: quantitative-trading-tools
description: >
  Quantitative trading analysis toolkit — commodity COT positioning monitoring (CFTC data,
  options flow anomalies) and LSTM-based stock directional edge scanning (walk-forward
  validation, 18 stationary features). Covers data sourcing, anomaly detection, neural
  network pipeline architecture, and interpreting results.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [trading, quant, lstm, cot, commodity, neural-networks, stock-scanner, walk-forward]
    category: trading
triggers:
  - "quantitative trading"
  - "quant tools"
  - "commodity positioning"
  - "COT data"
  - "stock scanner neural network"
  - "LSTM trading"
  - "walk-forward scan"
  - "crude oil positioning"
  - "directional edge scan"
---

# References

- `references/free-data-sources.md` — Curated free financial APIs (stocks, crypto, sentiment, prediction markets, macro) with auth requirements and rate limits
- `references/presentation-workflow.md` — Presentation workflow notes

---

# Quantitative Trading Tools

Two complementary quant analysis systems: commodity positioning intelligence via CFTC COT data, and stock directional edge detection via walk-forward LSTM neural networks.

---

## References

- `references/presentation-workflow.md`
- `references/free-data-sources.md` — Verified free financial data APIs (no-auth + free-key tiers), includes Massive grouped endpoint technique

## Part A: Commodity Market Intelligence (COT Data)

Monitor crude oil / Brent / energy positioning and options flow to detect anomalies that typically precede headline-driven narrative shifts.

### Core Insight

When concentrated short-dated options flow doesn't fit the current narrative, the narrative usually shifts within 48 hours. This is a watchlist trigger, not a trade signal.

### Data Sources — What Actually Works

#### Free & Scriptable

**CFTC Public Reporting API** (BEST free source)
- Base: `https://publicreporting.cftc.gov/resource/{dataset_id}.json`
- No auth required, reliable, SQL-like `$where` queries
- **Disaggregated COT** (`72hh-3qpy`) — managed money, swap dealers, producer/merchant
- **Legacy COT** (`jun7-fc8e`) — noncommercial, concentration ratios
- Released every Friday 3:30 PM ET (positions as of prior Tuesday)
- 3-4 day lag but authoritative for weekly positioning shifts

**Working contract names (verified current as of 2026-05):**
- `CRUDE OIL, LIGHT SWEET-WTI - ICE FUTURES EUROPE` (disagg) — ICE WTI, current
- `BRENT LAST DAY - NEW YORK MERCANTILE EXCHANGE` (both datasets) — Brent, current
- `CRUDE OIL, LIGHT SWEET - NEW YORK MERCANTILE EXCHANGE` (legacy only) — NYMEX WTI, **STALE: only through Feb 2022**

#### FRED (Federal Reserve Economic Data) — NOW LIVE

- API key in `~/.hermes/scripts/fred_query.py`
- No rate limits on basic queries, 800K+ time series
- Key series: GDP, FEDFUNDS, CPIAUCSL, UNRATE, DGS10, DGS2, T10Y2Y, SP500, VIXCLS, ICSA, MORTGAGE30US
- Usage: `python3 ~/.hermes/scripts/fred_query.py <SERIES_ID> [--limit N] [--start YYYY-MM-DD] [--end YYYY-MM-DD]`
- List all common series: `python3 ~/.hermes/scripts/fred_query.py list`

#### Massive.com (Polygon.io rebrand)

- API key in memory (`I_NK53ie5NuBz_VP1f6cMporEkozLxzi`)
- Free tier: 5 calls/min, 2 years historical data
- Best endpoint: `GET /v2/aggs/grouped/locale/us/market/stocks/{date}` — returns OHLCV for ALL US stocks in ONE call (12K+ tickers). This is the killer feature for batch scanning.
- Also: snapshots, technical indicators (SMA/EMA/MACD/RSI built-in), news with sentiment
- Paid-only on free tier: snapshots, gainers/losers, fundamentals, short interest
- MCP server: `github.com/massive-com/mcp_massive`
- Pitfall: Free tier is strict 5/min. Use the grouped endpoint for bulk scans instead of per-ticker calls.

#### MarketAux — Stock News + Sentiment

- API key in memory (`NEFhMjB2KY7rXyyuJgR9u6NaLetL6lUWV10AQPpM`)
- Endpoint: `GET https://api.marketaux.com/v1/news/all?symbols=AAPL,NVDA&api_token=KEY&limit=10&language=en`
- Entity search: `GET https://api.marketaux.com/v1/entity/search?search=Tesla&api_token=KEY`
- Free tier: 100 req/day
- Sentiment field present but often N/A on free tier

#### Blocked / Not Scriptable

- **CME Group** — blocks automated access (403 + anti-scraping message)
- **Barchart** — JS-rendered, internal API requires session cookies/tokens
- **Yahoo Finance** — rate-limits yfinance for commodity futures options
- **Alpaca** — US equities/index options only, no commodity futures options
- **ICE** — no free analytics suite comparable to CME QuikStrike

#### Manual (Free)

- **CME QuikStrike** (free with CME account) — Most Active Strikes, Open Interest Heatmap, Globex Trade Browser. Best for WTI. JS-rendered, not scriptable.
- **Barchart options chains** (free) — Brent/WTI option chains with volume + OI. JS-rendered.

#### Paid / API

- **Databento** (~$0.50/GB) — CME + ICE options tick data, Python client. $125 free trial.
- **Interactive Brokers TWS API** — free with funded account, covers CME + ICE options on futures.

### Anomaly Detection Criteria

Flag when any metric exceeds 2σ vs 26-week rolling baseline:
- Managed money net position change
- Short position spike (week-over-week)
- Spread position change (options-adjacent)
- Top-4/8 trader concentration ratio shift
- Unusual OI buildup

For options-level anomalies (when you have the data):
- Volume/OI ratio > 150% on a single strike outside expiration week
- Block trade > $5M notional (quantity × premium × contract multiplier)
- Single-strike OI spike vs rest of chain
- Short-dated (<30 DTE) + large concentrated size

### COT Query Patterns

```
# Disaggregated — get managed money for ICE WTI
GET /resource/72hh-3qpy.json
  ?$where=market_and_exchange_names='CRUDE OIL, LIGHT SWEET-WTI - ICE FUTURES EUROPE'
  &$order=report_date_as_yyyy_mm_dd DESC
  &$limit=28

# Legacy — get concentration ratios for Brent
GET /resource/jun7-fc8e.json
  ?$where=market_and_exchange_names='BRENT LAST DAY - NEW YORK MERCANTILE EXCHANGE'
    AND futonly_or_combined='Combined'
  &$order=report_date_as_yyyy_mm_dd DESC
  &$limit=28
```

URL-encode the `$where` value (spaces, commas, quotes). Use `urllib.parse.quote()` in Python.

### COT Pitfalls

1. **NYMEX WTI disaggregated data ended Feb 2022** — CFTC consolidated to ICE Europe. Use the ICE FUTURES EUROPE contract name, not NYMEX.
2. **URL encoding** — CFTC API rejects spaces/unencoded characters. Always encode `$where`.
3. **`futonly_or_combined` filter** — Legacy COT has both rows. Use `'Combined'` for futures+options.
4. **Spread field naming differs** — Legacy: `noncomm_postions_spread_all` (note typo). Disagg: `m_money_positions_spread_all`.
5. **CME blocks programmatic access** — Do not attempt to scrape.
6. **Barchart UOA is equity-only** — Their "Unusual Options Activity" pages don't cover commodity futures options.
7. **Weekly cadence only** — CFTC COT is weekly (Friday release). Daily/intraday needs paid feeds.

### Running Implementation

Cron job `CFTC COT Crude Oil Scanner` (job ID: `db1264296679`):
- Script: `~/.hermes/scripts/cot-scanner.py`
- Schedule: Fridays 21:45 Paris (15 min after CFTC release)
- Mode: `no_agent=True` (script-only)
- Pulls 26 weeks, calculates z-scores on week-over-week changes, flags >2σ
- Covers WTI (ICE Europe) + Brent Last Day (NYMEX) for managed money and concentration data

---

## Part B: Quant NN Scanner (LSTM Stock Scanner)

Walk-forward LSTM pipeline that scans stocks for directional edge. Based on Marcos Lopez de Prado's framework.

### What It Does

For each ticker: fetches daily OHLCV → engineers 18 stationary features (ADF-tested) → trains LSTM with walk-forward validation (39 independent windows) → reports directional accuracy.

**Target range: 52–57% directional accuracy.** Above 57% = overfit suspicion. Below 52% = no edge found.

### Project Location

`/home/ubuntu/quant-nn/`

```
quant-nn/
├── config.py          # Central config (ticker, dates, model params)
├── data.py            # Dual-source: Alpaca (default) or yfinance, with caching
├── features.py        # 18 stationary features + ADF tests
├── model.py           # LSTM (2 layers, 64 hidden, 20% dropout, sigmoid output)
├── train.py           # Walk-forward, early stopping, gradient clipping
├── evaluate.py        # Directional accuracy, Sharpe, Kelly fraction
├── main.py            # CLI: single ticker or batch scan
├── requirements.txt
└── .cache/            # Auto-populated parquet/CSV cache
```

### Quick Start

```bash
cd /home/ubuntu/quant-nn

# Single ticker (Alpaca — no rate limits)
python3 main.py --ticker SPY --source alpaca

# Single ticker (Yahoo Finance)
python3 main.py --ticker NVDA --source yfinance

# Batch scan — outputs ranked leaderboard with tier verdicts
python3 main.py --tickers "QQQ,MSFT,AVGO,AMZN,AAPL" --source alpaca
```

### Data Sources

**Alpaca Markets (default):** No rate limits. Uses paper trading API key. Keys in `~/alpaca-bot/.env`. Requires timezone-aware datetimes (`ZoneInfo("US/Eastern")`). Use `adjustment="all"` for split + dividend adjusted data.

**Environment variable loading:** data.py checks `ALPACA_API_KEY`/`ALPACA_SECRET_KEY` from environment, then falls back to `~/alpaca-bot/.env` and `~/.hermes/.env`.

**Yahoo Finance:** Fallback. Prone to rate limiting — includes retry logic (3 attempts, exponential backoff) and local caching. **Critical:** yfinance returns empty DataFrame on rate limits without throwing — data.py handles this with empty-response retry loop.

### Architecture

**Features (18 total, all ADF-validated):**
- Log returns (1d, 5d, 20d windows)
- Volatility ratios (short/long realized vol)
- Momentum normalized by volatility
- Volume z-score (vs rolling mean)
- Spread signals (high-low range vs historical)
- Regime indicators (VWAP deviation, distance from extremes)

**Target:** Binary direction (up/down) on risk-adjusted forward return.

**Model:** LSTM: 2 layers, 64 hidden units, 20% dropout. Input: 18 features × 20-day lookback. Output: Sigmoid → probability. ~25K trainable parameters.

**Training:** Walk-forward: 252-day training window, 63-day step. Sequential 3-way split (60/20/20, never shuffled). Early stopping. Gradient clipping at 1.0. Fresh model per window. 39 independent validations per ticker.

### Interpreting Results

| Accuracy | Verdict | Action |
|----------|---------|--------|
| 52–57% | ✅ Target range | Genuine edge — consistent across windows |
| >57% | 🚩 Overfit suspicion | Check for short history, strong trend, micro-cap |
| 50–52% | ⚠️ Marginal | May need regime detection or shorter windows |
| <50% | ❌ Below target | Asset not suitable for this architecture |

### 21-Stock Benchmark (May 2026, Alpaca data)

| Ticker | Accuracy | Verdict |
|--------|----------|---------|
| QQQ | 54.7% | ✅ Indices lead |
| SPY | 54.0% | ✅ |
| NVDA | 53.3% | ✅ |
| PLTR | 52.7% | ✅ (16 windows — short history) |
| MSFT | 52.6% | ✅ |
| GOOGL | 52.5% | ✅ |
| META | 52.2% | ✅ (tightest std: 4.7%) |
| ANET | 52.2% | ✅ |
| MP | 52.0% | ✅ (17 windows) |
| HOOD | 51.8% | ⚠️ (13 windows) |
| NOW | 51.6% | ⚠️ |
| AVGO | 51.5% | ⚠️ |
| ENTG | 51.3% | ⚠️ |
| MU | 51.2% | ⚠️ cyclical |
| AMZN | 51.1% | ⚠️ |
| COIN | 51.0% | ⚠️ (14 windows) |
| SMCI | 50.0% | ⚠️ |
| CRWD | 49.4% | ❌ (21 windows) |
| AAPL | 49.2% | ❌ too efficient |
| FCX | 48.3% | ❌ worst — deep cyclical |
| POET | 61.4% | 🚩 micro-cap overfit |

### What Works / Struggles

**Works:** Broad indices (QQQ, SPY), AI platforms (MSFT, GOOGL, META), AI infrastructure (ANET, NVDA), supply chain (MP, PLTR).

**Struggles:** Deep cyclicals (MU, FCX) — regime shifts break stationary features. Micro-caps (POET) — short history → overfit. Commodity plays — structural breaks require HMM.

### Three Fixes for Struggling Tickers

1. **Regime-aware model** — Hidden Markov layer to detect cycle phase
2. **Shorter retraining** — Cut window from 252d → 90d
3. **Cycle features** — Add distance from 200d MA, relative strength vs sector

### Large Batch Scans

Each ticker takes ~15–18s. Foreground timeout is 600s — max ~15 tickers per foreground command. Split larger scans into parallel background jobs of ≤15 tickers each.

### NN Scanner Pitfalls

- **Foreground timeout on large batches**: ~17s/ticker × 36 tickers ≈ 10 min > 600s limit. Split into parallel background jobs of ≤15 tickers each.
- **Massive grouped endpoint for bulk scans**: Instead of calling per-ticker OHLCV, use `GET /v2/aggs/grouped/locale/us/market/stocks/{date}` to get all 12K+ US stocks in one call. Filter client-side for volume, % change, dollar volume. This is free-tier friendly (1 call vs thousands).
- **POET trap**: >60% accuracy on short-history stocks is almost certainly overfit.
- **Yahoo rate limits**: YFinance 429s after ~5 rapid requests. Use Alpaca for batch scans.
- **Empty Alpaca response**: Can happen if ticker delisted or no data in range.
- **Cache staleness**: `.cache/` stores by ticker+date+source. Delete to force re-fetch.
- **Walk-forward minimums**: Need at least 500 trading days for meaningful results.

### Dependencies

```
torch numpy pandas yfinance alpaca-py scikit-learn scipy statsmodels matplotlib pyarrow
```
