# Earnings Proximity Risk Assessment

Framework for assessing whether a stock is safe to hold through upcoming earnings.

## Primary Metric: Price vs Consensus Target

The single most important number for earnings risk assessment: **how much upside/downside is left to the median analyst 1-year target.**

- Stock trading **above** consensus target → priced for perfection. Any "good but not great" report causes a sell-off.
- Stock trading **10-15%+ below** consensus target → expectations are low. Beating is easier.
- Example from session (MU, June 2026): MU at $1,043, consensus target $900 = **13.7% below current price**. This was the clearest risk signal — the entire sell-side pointed lower.

## Options Flow as Secondary Signal

Pull these from the Alpaca options scan (via `alpaca_options_scan.py` in wolf-trading-agent):

- **P/C Ratio**: < 0.35 = extreme bullish skew, 0.35-0.70 = bullish, 0.70-1.30 = neutral
- **Call/Put Volume**: absolute numbers reveal positioning size
- **IV Regime**: high IV (>30%) = expensive options → credit spreads; low IV (<25%) → debit spreads

## Multi-Variable Risk Matrix

When consolidating:

```
Risk = bull case_weight × prob_beat + bear case_weight × (1 - prob_beat)
```

Where bull case = (target gap) + (sector tailwind) + (options P/C) and bear case = (stock extendedness) + (hype) + (cycle risk).

## Data Sourcing for Earnings Scans

This type of scan reliably hits multiple data source failures because:
1. Yahoo Finance rate-limit is triggered by the multi-ticker options scan that ran first
2. The scan itself uses yfinance/cookies, compounding the rate-limit
3. Nasdaq API's `info` endpoint may return stale prices (known bug: returns wrong live price vs real)
4. Alpaca credentials may not load if used from wrong Python version

**Fallback order for earnings scans specifically:**
1. Nasdaq `summary` endpoint → prev close, P/E, EPS, Market Cap, 52W range (reliable)
2. Alpaca options scan → P/C ratio, volume, IV (already ran; read from its output)
3. Manual comparison (price vs target from Nasdaq summary's `OneYrTarget` field)
4. Analyst consensus from Nasdaq `summaryData[OneYrTarget].value`

## Data Points to Present

| Data Point | Source | Reliability |
|------------|--------|-------------|
| Current Price | Alpaca StockLatestTrade | ✅ Best |
| Previous Close | Nasdaq Summary | ✅ Reliable |
| 52W Range | Nasdaq Summary | ✅ Reliable |
| Market Cap | Nasdaq Summary | ✅ Reliable |
| P/E, EPS | Nasdaq Summary | ✅ Reliable |
| Analyst Target | Nasdaq Summary (OneYrTarget) | ✅ Reliable |
| Options P/C | Alpaca Options Scan | ✅ Reliable |
| Option IV | Alpaca Options Scan | ✅ Reliable |
| Live % Change | Compute manually | ⚠️ (price/prevClose - 1) |
| Historical OHLCV | yfinance (after cooldown) | ⚠️ Rate-limited |
