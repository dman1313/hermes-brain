#!/usr/bin/env python3
"""
Portfolio Risk Assessor — standalone Hermes skill.
Replaces ruflo neural-trader risk engine with Python calculations.
Computes VaR, CVaR, Kelly sizing, Sharpe, and position sizing from API data.

Usage:
  python3 portfolio_risk.py --symbol AAPL --investment 10000
  python3 portfolio_risk.py --symbols AAPL,MSFT,GOOGL --investment 50000 --portfolio my_portfolio
"""
import argparse
import json
import math
import os
import sys
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

MASSIVE_API_KEY="I_NK53ie5NuBz_VP1f6cMporEkozLxzi"
BASE_URL = "https://api.massiveapi.io"
TRADING_DATA_DIR = "/home/ubuntu/trading-data"


def fetch_json(url, headers=None):
    req = Request(url)
    req.add_header("User-Agent", "Hermes-Portfolio-Risk/1.0")
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    try:
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except HTTPError as e:
        print(f"[ERROR] HTTP {e.code}: {e.reason}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return None


def get_stock_data(symbol, days=252):
    """Fetch ~1 year of OHLCV data (252 trading days)."""
    url = (
        f"{BASE_URL}/stocks/aggregates?ticker={symbol}"
        f"&multiplier=1&timespan=day&from={days}d&to=today"
        f"&apikey={MASSIVE_API_KEY}"
    )
    data = fetch_json(url)
    if data and "results" in data:
        return data["results"]
    alt = (
        f"{BASE_URL}/v1/aggs/ticker/{symbol}/range/1/day/"
        f"{days}d/today?apikey={MASSIVE_API_KEY}"
    )
    data = fetch_json(alt)
    if data and "results" in data:
        return data["results"]
    return None


def calc_returns(prices):
    """Calculate daily returns."""
    if len(prices) < 2:
        return []
    return [(prices[i] - prices[i - 1]) / prices[i - 1] for i in range(1, len(prices))]


def calc_var(returns, confidence=0.95):
    """
    Value at Risk — historical simulation method.
    Returns the loss threshold at given confidence level.
    """
    if len(returns) < 10:
        return 0.0
    sorted_rets = sorted(returns)
    idx = int((1 - confidence) * len(sorted_rets))
    idx = max(0, min(idx, len(sorted_rets) - 1))
    return round(abs(sorted_rets[idx]) * 100, 2)


def calc_cvar(returns, confidence=0.95):
    """
    Conditional VaR (Expected Shortfall) — average of losses beyond VaR.
    """
    if len(returns) < 10:
        return 0.0
    sorted_rets = sorted(returns)
    idx = int((1 - confidence) * len(sorted_rets))
    idx = max(0, min(idx, len(sorted_rets) - 1))
    tail = sorted_rets[:idx]
    if not tail:
        return round(abs(sorted_rets[0]) * 100, 2) if sorted_rets else 0.0
    return round(abs(sum(tail) / len(tail)) * 100, 2)


def calc_sharpe(returns, risk_free_rate=0.05):
    """Annualized Sharpe ratio."""
    if len(returns) < 5:
        return 0.0
    avg_return = sum(returns) / len(returns)
    daily_rf = risk_free_rate / 252
    excess = avg_return - daily_rf
    var_ret = sum((r - avg_return) ** 2 for r in returns) / len(returns)
    std = math.sqrt(var_ret) if var_ret > 0 else 0.0001
    daily_sharpe = excess / std
    return round(daily_sharpe * math.sqrt(252), 2)


def calc_sortino(returns, risk_free_rate=0.05):
    """Annualized Sortino ratio (downside deviation only)."""
    if len(returns) < 5:
        return 0.0
    avg_return = sum(returns) / len(returns)
    daily_rf = risk_free_rate / 252
    excess = avg_return - daily_rf
    downside = [r for r in returns if r < 0]
    if not downside:
        return 10.0  # No downside = infinite sortino proxy
    downside_var = sum((d - avg_return) ** 2 for d in downside) / len(downside)
    downside_std = math.sqrt(downside_var) if downside_var > 0 else 0.0001
    daily_sortino = excess / downside_std
    return round(daily_sortino * math.sqrt(252), 2)


def calc_max_drawdown(prices):
    """Maximum drawdown as percentage."""
    if len(prices) < 2:
        return 0.0
    peak = prices[0]
    max_dd = 0.0
    for p in prices:
        if p > peak:
            peak = p
        dd = (peak - p) / peak * 100
        if dd > max_dd:
            max_dd = dd
    return round(max_dd, 2)


def calc_win_rate(returns):
    """Percentage of positive returns."""
    if not returns:
        return 0.0
    wins = sum(1 for r in returns if r > 0)
    return round(wins / len(returns) * 100, 1)


def calc_kelly_fraction(win_rate, avg_win, avg_loss):
    """
    Kelly Criterion: fraction of capital to risk.
    f* = p/a - q/b where:
    p = win probability, q = loss probability
    a = avg loss / 1 (loss ratio), b = avg win / 1 (win ratio)
    Simplified: f* = p - (1-p) / (avg_win/avg_loss)
    """
    if avg_loss == 0 or avg_win == 0:
        return 0.0
    win_loss_ratio = avg_win / abs(avg_loss) if avg_loss != 0 else 1
    p = win_rate / 100
    if win_loss_ratio == 0:
        return 0.0
    kelly = p - (1 - p) / win_loss_ratio
    return round(max(0, min(kelly, 0.25)), 4)  # Cap at 25%


def calc_position_size(investment, risk_per_trade_pct, stop_loss_pct, atr, price):
    """
    Calculate position size based on account risk.
    Returns shares and dollar amount.
    """
    if stop_loss_pct == 0 or price == 0:
        return 0, 0.0
    risk_amount = investment * (risk_per_trade_pct / 100)
    if atr > 0:
        # ATR-based stop: 2x ATR
        stop_distance = 2 * atr
        stop_pct = stop_distance / price * 100
    else:
        stop_pct = stop_loss_pct

    shares = int(risk_amount / (price * stop_pct / 100)) if stop_pct > 0 else 0
    position_value = round(shares * price, 2)
    return shares, position_value


def assess_risk(symbol, data, investment=10000):
    """Compute comprehensive risk metrics for a symbol."""
    prices = [bar.get("c", 0) for bar in data]
    volumes = [bar.get("v", 0) for bar in data]
    highs = [bar.get("h", 0) for bar in data]
    lows = [bar.get("l", 0) for bar in data]

    if not prices:
        return {"symbol": symbol, "error": "No price data"}

    current_price = prices[-1]
    returns = calc_returns(prices)

    # ATR calculation
    atr = 0
    if len(highs) > 14 and len(lows) > 14:
        trs = []
        for i in range(1, len(highs)):
            tr = max(highs[i] - lows[i], abs(highs[i] - prices[i-1]), abs(lows[i] - prices[i-1]))
            trs.append(tr)
        if trs:
            atr = sum(trs[-14:]) / 14

    # Risk metrics
    var_95 = calc_var(returns)
    cvar_95 = calc_cvar(returns)
    sharpe = calc_sharpe(returns)
    sortino = calc_sortino(returns)
    max_dd = calc_max_drawdown(prices)
    win_rate = calc_win_rate(returns)

    # Win/loss stats for Kelly
    wins = [r for r in returns if r > 0]
    losses = [r for r in returns if r < 0]
    avg_win = abs(sum(wins) / len(wins)) if wins else 0
    avg_loss = abs(sum(losses) / len(losses)) if losses else 0
    kelly = calc_kelly_fraction(win_rate, avg_win, avg_loss)

    # Position sizing
    shares_2pct, value_2pct = calc_position_size(investment, 2.0, 5.0, atr, current_price)
    shares_1pct, value_1pct = calc_position_size(investment, 1.0, 5.0, atr, current_price)
    shares_half_kelly, value_half_kelly = calc_position_size(investment, kelly * 100 * 0.5, 5.0, atr, current_price)

    # Volatility regime
    daily_vol = (sum(abs(r) for r in returns[-20:]) / 20) if len(returns) >= 20 else 0
    volatility_label = "low" if daily_vol < 0.01 else "normal" if daily_vol < 0.025 else "high" if daily_vol < 0.04 else "extreme"

    # Circuit breaker checks
    recent_returns = returns[-5:] if len(returns) >= 5 else returns
    daily_loss_3pct = sum(1 for r in recent_returns if r < -0.03)
    weekly_loss_5pct = (sum(returns[-5:]) < -0.05) if len(returns) >= 5 else False
    concentration_pct = round(investment / (investment + 10000) * 100, 1) if investment > 0 else 0

    breakers = []
    if daily_loss_3pct >= 1:
        breakers.append("Daily loss >3% limit hit")
    if weekly_loss_5pct:
        breakers.append("Weekly loss >5% threshold")
    if volatility_label in ("high", "extreme"):
        breakers.append(f"Volatility regime: {volatility_label}")
    if concentration_pct > 10:
        breakers.append(f"Concentration >10% ({concentration_pct:.0f}%)")

    risk_score = 50  # neutral baseline
    if var_95 > 3: risk_score += 15
    elif var_95 > 2: risk_score += 8
    if cvar_95 > 5: risk_score += 10
    elif cvar_95 > 3: risk_score += 5
    if max_dd > 30: risk_score += 20
    elif max_dd > 20: risk_score += 10
    elif max_dd > 10: risk_score += 5
    if sharpe < 0: risk_score += 10
    if sharpe > 2: risk_score -= 10
    risk_score = min(100, max(0, risk_score))

    risk_label = "low" if risk_score < 30 else "moderate" if risk_score < 55 else "high" if risk_score < 75 else "critical"

    result = {
        "symbol": symbol,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "price": current_price,
        "investment": investment,
        "risk_metrics": {
            "var_95": var_95,
            "cvar_95": cvar_95,
            "sharpe": sharpe,
            "sortino": sortino,
            "max_drawdown_pct": max_dd,
            "win_rate_pct": win_rate,
            "kelly_fraction": kelly,
            "daily_volatility_pct": round(daily_vol * 100, 2),
            "volatility_regime": volatility_label,
            "atr": round(atr, 2),
        },
        "position_sizing": {
            "2pct_risk": {"shares": shares_2pct, "value": value_2pct},
            "1pct_risk": {"shares": shares_1pct, "value": value_1pct},
            "half_kelly": {"shares": shares_half_kelly, "value": value_half_kelly},
        },
        "circuit_breakers": breakers,
        "risk_score": risk_score,
        "risk_label": risk_label,
        "concentration_pct": concentration_pct,
    }
    return result


def main():
    parser = argparse.ArgumentParser(description="Hermes Portfolio Risk Assessor")
    parser.add_argument("--symbol", help="Single ticker symbol")
    parser.add_argument("--symbols", help="Comma-separated tickers")
    parser.add_argument("--investment", type=float, default=10000, help="Total investment amount (default: 10000)")
    parser.add_argument("--portfolio", default=None, help="Portfolio name for tracking")
    args = parser.parse_args()

    symbols_str = args.symbols if args.symbols else args.symbol
    if not symbols_str:
        print("Usage: python3 portfolio_risk.py --symbol AAPL [--investment 10000]")
        sys.exit(1)

    symbols = [s.strip().upper() for s in symbols_str.split(",")]
    all_results = []

    for symbol in symbols:
        print(f"\n{'='*60}")
        print(f"[{symbol}] Fetching data...")
        data = get_stock_data(symbol)
        if not data:
            print(f"[{symbol}] SKIP — no data")
            continue
        print(f"[{symbol}] Got {len(data)} bars")

        result = assess_risk(symbol, data, args.investment)
        all_results.append(result)

        r = result["risk_metrics"]
        ps = result["position_sizing"]
        print(f"\n  Price:   ${result['price']:.2f}")
        print(f"\n  RISK METRICS:")
        print(f"    VaR(95%):      {r['var_95']:.2f}% (daily loss threshold)")
        print(f"    CVaR(95%):     {r['cvar_95']:.2f}% (expected loss beyond VaR)")
        print(f"    Sharpe:        {r['sharpe']}")
        print(f"    Sortino:       {r['sortino']}")
        print(f"    Max DD:        {r['max_drawdown_pct']:.1f}%")
        print(f"    Win Rate:      {r['win_rate_pct']:.1f}%")
        print(f"    Kelly Fraction: {r['kelly_fraction']:.1%}")
        print(f"    Volatility:    {r['volatility_regime'].upper()} ({r['daily_volatility_pct']:.2f}%/day)")
        print(f"    ATR:           ${r['atr']:.2f}")
        print(f"\n  POSITION SIZING (${result['investment']:,.0f} account):")
        print(f"    2% risk:       {ps['2pct_risk']['shares']} shares = ${ps['2pct_risk']['value']:,.2f}")
        print(f"    1% risk:       {ps['1pct_risk']['shares']} shares = ${ps['1pct_risk']['value']:,.2f}")
        if ps['half_kelly']['shares'] > 0:
            print(f"    Half-Kelly:    {ps['half_kelly']['shares']} shares = ${ps['half_kelly']['value']:,.2f}")
        print(f"\n  RISK SCORE:    {result['risk_score']}/100 — {result['risk_label'].upper()}")
        if result["circuit_breakers"]:
            print(f"  ⚠ BREAKERS: {', '.join(result['circuit_breakers'])}")
        else:
            print("  ✓ No circuit breakers active")

        # Save
        os.makedirs(TRADING_DATA_DIR, exist_ok=True)
        filename = f"{TRADING_DATA_DIR}/risk-{symbol}-{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        with open(filename, "w") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"  Saved: {filename}")

    # Portfolio summary
    if len(all_results) > 1:
        print(f"\n{'='*60}")
        print("PORTFOLIO RISK SUMMARY")
        avg_risk = sum(r["risk_score"] for r in all_results) / len(all_results)
        avg_sharpe = sum(r["risk_metrics"]["sharpe"] for r in all_results) / len(all_results)
        print(f"  Positions:  {len(all_results)}")
        print(f"  Avg Risk:   {avg_risk:.0f}/100")
        print(f"  Avg Sharpe: {avg_sharpe:.2f}")
        high_risk = [r for r in all_results if r["risk_score"] >= 65]
        if high_risk:
            print(f"  ⚠ High risk: {', '.join(r['symbol'] for r in high_risk)}")


if __name__ == "__main__":
    main()
