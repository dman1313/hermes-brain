---
name: quant-nn-scanner
description: "Scan stocks with a walk-forward LSTM neural network to find directional edge. 18 stationary features, ADF-validated, 39 independent training windows. Identifies which tickers carry a stable conditional expectation."
version: 1.1.0
author: Hermes
metadata:
  hermes:
    tags: [trading, neural-networks, lstm, quant, stock-scanner, walk-forward, feature-engineering]
    related_skills: [alpaca-volume-scanner, powerpoint]
triggers:
  - "scan stocks with neural network"
  - "quant nn"
  - "run the LSTM scanner"
  - "test tickers for directional edge"
  - "walk-forward validation scan"
  - "neural network trading signal"
---

# Quant NN Scanner

Walk-forward LSTM pipeline that scans stocks for directional edge. Based on Marcos Lopez de Prado's framework and the Cornell lecture on neural networks for trading signals.

## What It Does

For each ticker: fetches daily OHLCV → engineers 18 stationary features (ADF-tested) → trains LSTM with walk-forward validation (39 independent windows) → reports directional accuracy.

**Target range: 52–57% directional accuracy.** Above 57% = overfit suspicion. Below 52% = no edge found (or regime-shifting asset).

## Project Location

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

## Quick Start

```bash
cd /home/ubuntu/quant-nn

# Single ticker (Alpaca — no rate limits)
python3 main.py --ticker SPY --source alpaca

# Single ticker (Yahoo Finance)
python3 main.py --ticker NVDA --source yfinance

# Batch scan — outputs ranked leaderboard with tier verdicts
python3 main.py --tickers "QQQ,MSFT,AVGO,AMZN,AAPL" --source alpaca
```

Output format (batch mode):
```
  Ticker     Accuracy  Windows      Std     Best    Worst Verdict
  ─────── ────────── ──────── ──────── ──────── ──────── ────────
  QQQ          54.7%       35    7.8%   71.4%   41.3%  ✅ Target range
  MSFT         52.6%       35    6.8%   65.1%   39.7%  ✅ Target range
  AAPL         49.2%       35    6.6%   63.5%   36.5%  ❌ Below target
```

## Data Sources

**Alpaca Markets (default):** No rate limits. Uses paper trading API key. Free tier supports daily bars. Keys in `~/alpaca-bot/.env`. Alpaca requires timezone-aware datetimes — use `ZoneInfo("US/Eastern")`. Use `adjustment="all"` for split + dividend adjusted data. Calls `StockHistoricalDataClient.get_stock_bars()` with `StockBarsRequest(timeframe=TimeFrame.Day)`.

**Environment variable loading:** data.py checks `ALPACA_API_KEY`/`ALPACA_SECRET_KEY` from environment, then falls back to parsing `~/alpaca-bot/.env` and `~/.hermes/.env`.

**Yahoo Finance:** Fallback. Prone to rate limiting — includes retry logic (3 attempts, exponential backoff) and local caching. **Critical:** yfinance returns empty DataFrame on rate limits without throwing — data.py handles this with empty-response retry loop.

## Architecture

### Features (18 total, all ADF-validated)
- Log returns (1d, 5d, 20d windows)
- Volatility ratios (short/long realized vol)
- Momentum normalized by volatility
- Volume z-score (vs rolling mean)
- Spread signals (high-low range vs historical)
- Regime indicators (VWAP deviation, distance from extremes)

### Target
Binary direction (up/down) on risk-adjusted forward return — more stable than raw price.

### Model
- LSTM: 2 layers, 64 hidden units, 20% dropout
- Input: 18 features × 20-day lookback window
- Output: Sigmoid → probability of upward move (0–1)
- ~25K trainable parameters

### Training
- Walk-forward: 252-day training window, 63-day step
- Sequential 3-way split (60/20/20 — never shuffled)
- Early stopping: halt when validation loss rises
- Gradient clipping at 1.0
- Fresh model trained from scratch per window
- 39 independent validations per ticker

## Interpreting Results

| Accuracy | Verdict | Action |
|----------|---------|--------|
| 52–57% | ✅ Target range | Genuine edge — consistent across windows |
| >57% | 🚩 Overfit suspicion | Check for short history, strong trend, micro-cap |
| 50–52% | ⚠️ Marginal | May need regime detection or shorter windows |
| <50% | ❌ Below target | Asset not suitable for this architecture |

**Edge is in consistency, not magnitude.** A 54% signal with Kelly sizing and Sharpe >1.0 compounds into real returns. Renaissance's Medallion Fund built on the same principle.

## What Works Best

- **Broad indices** (QQQ 54.7%, SPY 54.0%) — stable regimes, smooth E[Y|X]
- **AI platforms** (MSFT 52.6%, GOOGL 52.5%, META 52.2%) — secular growth survives volatility
- **AI infrastructure** (ANET 52.2%, NVDA 53.3%) — networking + compute backbone
- **Supply chain** (MP 52.0%, PLTR 52.7%) — upstream plays with strategic demand

### 21-Stock Benchmark (May 2026, Alpaca data)

9 in target range, 8 marginal, 4 below:

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

## What Struggles

- **Deep cyclicals** (MU, FCX) — regime shifts break stationary features
- **Micro-caps** (POET) — short history → overfit to trend direction
- **Commodity plays** — structural breaks require HMM regime detection

## Three Fixes for Struggling Tickers

1. **Regime-aware model** — Hidden Markov layer to detect cycle phase
2. **Shorter retraining** — Cut window from 252d → 90d
3. **Cycle features** — Add distance from 200d MA, relative strength vs sector

## Dependencies

```
torch numpy pandas yfinance alpaca-py scikit-learn scipy statsmodels matplotlib pyarrow
```

## Large Batch Scans

Each ticker takes ~15–18s (35 LSTM training windows). **Foreground timeout is 600s** — realistic max is ~15 tickers per foreground command. For anything larger, split into parallel background jobs:

```bash
cd /home/ubuntu/quant-nn

# Split a 36-ticker scan into 3 parallel batches of ~12 each
# Batch 1 (terminal, background=true, notify_on_complete=true)
python3 main.py --tickers "TICKER1,TICKER2,...,TICKER12" --source alpaca

# Batch 2 (same setup)
python3 main.py --tickers "TICKER13,TICKER14,...,TICKER24" --source alpaca

# Batch 3 (same setup)
python3 main.py --tickers "TICKER25,...,TICKER36" --source alpaca
```

All three run simultaneously — CPU-bound but parallelizable since each ticker trains independently. Results stream to the agent via notify_on_complete. **Do not run 30+ tickers in a single foreground command.**

When presenting partial results mid-scan: show the completed tickers immediately, note which batches are still running, and deliver the full ranked leaderboard once all batches finish.

## Pitfalls

- **Foreground timeout on large batches**: ~17s/ticker × 36 tickers ≈ 10 min > 600s limit. Split into parallel background jobs of ≤15 tickers each.
- **POET trap**: >60% accuracy on short-history stocks is almost certainly overfit, not edge. Check data length before celebrating.
- **Yahoo rate limits**: YFinance will 429 after ~5 rapid requests. Use Alpaca for batch scans.
- **Empty Alpaca response**: Can happen if ticker delisted or no data in range. Check ticker validity first.
- **Cache staleness**: `.cache/` stores by ticker+date+source. Delete to force re-fetch.
- **Walk-forward minimums**: Need at least 500 trading days for meaningful results.
