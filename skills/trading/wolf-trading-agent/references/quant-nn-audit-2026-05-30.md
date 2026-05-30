# Quant-NN Audit Findings (2026-05-30)

Full audit of `/home/ubuntu/quant-nn/` — walk-forward LSTM trading pipeline.

## Critical Issues

### LSTM Training Data Leakage (train.py:84)
`torch.randperm` shuffles overlapping sequences (stride-1 sliding window). Adjacent sequences share `lookback-1` out of `lookback` time steps. Shuffling puts nearly-identical sequences in different batches → model memorizes patterns from correlated samples → inflated validation accuracy.

**The 52-57% "expected accuracy range" may be artifactual.** Fix: remove shuffling or use non-overlapping sequences.

### Reads Other Projects' Secrets (data.py:120-134)
`_get_alpaca_client()` reads `~/alpaca-bot/.env` and `~/.hermes/.env` directly by parsing files line-by-line. Reaches into other projects' credential files without permission. Fix: use env vars only.

### No Risk Management Layer
No position sizing, stop-losses, take-profits, or exposure limits anywhere in the pipeline. Kelly fraction is computed but output-only. Must build risk layer before any live use.

## High Issues

### Test Returns Misaligned by 1 Day (train.py:273-277)
`log_ret_1d` at index `lookback + i` is the return ON that day, not the FORWARD return. Should use `lookback + i + 1`. Affects all risk metrics (Sharpe, win-rate, drawdown).

### Kelly Fraction on Full Series (evaluate.py:110-120)
Kelly computed on entire backtest return series, not individual trades. Financial returns are autocorrelated/heteroskedastic — Kelly on full series dramatically overstates optimal bet size.

### No Secret Masking in Errors (data.py)
If Alpaca client creation throws an exception, error message could leak API key info.

## Medium Issues

- Manual .env parsing instead of python-dotenv (brittle, fails on comments/multiline)
- No `.gitignore` — cached data could get committed
- Loss function and optimizer hardcoded (not configurable)
- Target is binary direction only (loses magnitude information)
- yfinance data cached unsorted vs alpaca sorted — inconsistency
- `win_rate()` measures signal-change days, not actual trades
- Window returns concatenated without handling 63-day gaps
- RSI deviates from Wilder's smoothing (minor)
- Variable scope leak (`upside` reused across sections)
- Division by zero risk in feature normalization

## Positive Findings

- Proper walk-forward validation (no future test leakage in split)
- Modular feature engineering (momentum, volatility, trend indicators)
- Good NaN handling in options parsing
- Excellent pitfalls documentation in SKILL.md
- Overfit flag at >57% accuracy (heuristic but directionally correct)
