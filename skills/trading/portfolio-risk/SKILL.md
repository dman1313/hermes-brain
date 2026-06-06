---
name: portfolio-risk
description: "Assess portfolio and position risk — VaR(95%), CVaR(95%), Sharpe ratio, Sortino ratio, Kelly fraction, position sizing, and circuit breaker checks using Massive API data."
version: 1.0.0
author: Hermes Agent
license: MIT
tags: [trading, risk, var, cvar, sharpe, kelly, position-sizing, circuit-breaker, massive-api]
category: trading
triggers:
  - "assess risk on SYMBOL"
  - "calculate position size"
  - "portfolio risk assessment"
  - "what is the risk on SYMBOL"
---

# Portfolio Risk Assessor

Computes comprehensive risk metrics for individual positions and portfolios using Massive API data. Replaces the ruflo `neural-trader --risk` CLI with pure Python calculations.

## Usage

```bash
# Single position
python3 ~/.hermes/skills/trading/portfolio-risk/scripts/portfolio_risk.py --symbol AAPL --investment 10000

# Portfolio view with multiple symbols
python3 ~/.hermes/skills/trading/portfolio-risk/scripts/portfolio_risk.py --symbols AAPL,MSFT,GOOGL --investment 50000
```

## What It Does

1. **Fetches 1 year (252 days) of OHLCV data** from Massive API for each symbol
2. **Computes risk metrics**:
   - **VaR(95%)** — Value at Risk: daily loss threshold at 95% confidence (historical simulation)
   - **CVaR(95%)** — Conditional VaR: expected loss beyond VaR (tail risk)
   - **Sharpe Ratio** — Risk-adjusted return (annualized)
   - **Sortino Ratio** — Downside deviation only
   - **Max Drawdown** — Peak-to-trough decline
   - **Win Rate** — Percentage of positive return days
   - **Kelly Criterion** — Optimal bet sizing fraction
   - **Daily Volatility** — 20-day average absolute return
3. **Calculates position sizes** for 1% risk, 2% risk, and half-Kelly
4. **Checks circuit breakers**: daily loss >3%, weekly loss >5%, volatility regime, concentration
5. **Produces aggregate risk score** (0-100) and portfolio summary for multi-symbol scans
6. **Saves results** to `/home/ubuntu/trading-data/risk-{SYMBOL}-{TIMESTAMP}.json`

## Risk Score Interpretation

| Score | Label | Meaning |
|---|---|---|
| 0-29 | LOW | Low risk — favorable risk profile |
| 30-54 | MODERATE | Manageable risk — standard sizing OK |
| 55-74 | HIGH | Elevated risk — reduce position size |
| 75-100 | CRITICAL | Very high risk — consider avoiding |

## Circuit Breakers

The skill checks these conditions automatically:
- **Daily loss >3%** — single-day loss limit triggered
- **Weekly loss >5%** — trailing 5-day loss threshold exceeded
- **Volatility regime** — flagged as "high" or "extreme"
- **Concentration >10%** — single position over-weighted

## Dependencies

- Python 3.8+
- Standard library only

## Files

```
scripts/
  portfolio_risk.py     # Main risk assessment script
```

## Pitfalls

- **Historical VaR/CVaR** assumes the past distribution of returns is representative of future risk. This fails during regime changes.
- **Kelly fraction** is capped at 25% to prevent overbetting. Full Kelly is mathematically optimal but practically dangerous — always use fractional Kelly.
- **Correlation not included**: Multi-symbol runs show each position independently. For portfolio-level VaR, correlation between positions needs separate calculation.
- **252 trading days** (~1 year) is standard but may not capture rare tail events (e.g., 2008, 2020). Consider longer lookback for long-term investors.
- **No options/leverage risk**: The risk model only uses equity data. Options positions have different risk profiles (gamma, theta, vega).

## Verification

```bash
# Test with a major stock
python3 ~/.hermes/skills/trading/portfolio-risk/scripts/portfolio_risk.py --symbol AAPL --investment 10000

# Multi-symbol portfolio
python3 ~/.hermes/skills/trading/portfolio-risk/scripts/portfolio_risk.py --symbols SPY,AAPL,MSFT --investment 50000
```
