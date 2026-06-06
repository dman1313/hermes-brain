#!/usr/bin/env python3
"""
Backtest Engine — standalone Hermes skill.
Replaces ruflo neural-trader --backtest with Massive historical aggregates + 
hash verification. Supports walk-forward validation and multiple strategies.

Usage:
  python3 backtest.py --strategy sma_crossover --symbol AAPL --period 2024-01-01,2024-12-31
  python3 backtest.py --strategy rsi_mean_reversion --symbol SPY --period 2020-01-01,2025-01-01 --walk-forward
"""
import argparse
import hashlib
import json
import math
import os
import sys
import time
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

MASSIVE_API_KEY="I_NK..._URL = "https://api.massiveapi.io"
TRADING_DATA_DIR = "/home/ubuntu/trading-data"


def fetch_json(url, headers=None):
    req = Request(url)
    req.add_header("User-Agent", "Hermes-Backtest/1.0")
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    try:
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except HTTPError as e:
        print(f"[WARN] HTTP {e.code}: {e.reason}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"[WARN] {e}", file=sys.stderr)
        return None


def get_historical_data(symbol, start_date, end_date):
    """Fetch OHLCV data for a date range."""
    url = (
        f"{BASE_URL}/stocks/aggregates?ticker={symbol}"
        f"&multiplier=1&timespan=day&from={start_date}&to={end_date}"
        f"&apikey={MASSIVE_API_KEY}"
    )
    data = fetch_json(url)
    if data and "results" in data and data["results"]:
        return data["results"]
    alt = (
        f"{BASE_URL}/v1/aggs/ticker/{symbol}/range/1/day/"
        f"{start_date}/{end_date}?apikey={MASSIVE_API_KEY}"
    )
    data = fetch_json(alt)
    if data and "results" in data:
        return data["results"]
    return None


# ---------------------------------------------------------------------------
# TECHNICAL INDICATORS
# ---------------------------------------------------------------------------

def calc_sma(prices, period):
    if len(prices) < period:
        return None
    return sum(prices[-period:]) / period


def calc_ema(prices, period):
    if len(prices) < period:
        return None
    multiplier = 2 / (period + 1)
    ema = sum(prices[:period]) / period
    for p in prices[period:]:
        ema = p * multiplier + ema * (1 - multiplier)
    return ema


def calc_rsi(prices, period=14):
    if len(prices) < period + 1:
        return 50.0
    gains, losses = 0.0, 0.0
    for i in range(1, period + 1):
        diff = prices[-i] - prices[-i - 1]
        if diff > 0:
            gains += diff
        else:
            losses += abs(diff)
    if losses == 0:
        return 100.0
    rs = (gains / period) / (losses / period)
    return 100.0 - (100.0 / (1.0 + rs))


def calc_macd(prices, fast=12, slow=26, signal=9):
    if len(prices) < slow:
        return 0, 0, 0
    fast_ema = calc_ema(prices, fast)
    slow_ema = calc_ema(prices, slow)
    if fast_ema is None or slow_ema is None:
        return 0, 0, 0
    macd_line = fast_ema - slow_ema
    return macd_line, 0, macd_line  # simplified


# ---------------------------------------------------------------------------
# STRATEGIES
# ---------------------------------------------------------------------------

def strategy_sma_crossover(prices, current_idx, fast_period=20, slow_period=50):
    """SMA crossover: buy when fast crosses above slow, sell when below."""
    if current_idx < slow_period:
        return "hold"
    fast_prev = calc_sma(prices[:current_idx], fast_period)
    fast_curr = calc_sma(prices[:current_idx + 1], fast_period)
    slow_prev = calc_sma(prices[:current_idx], slow_period)
    slow_curr = calc_sma(prices[:current_idx + 1], slow_period)
    if fast_prev is None or fast_curr is None or slow_prev is None or slow_curr is None:
        return "hold"
    if fast_prev <= slow_prev and fast_curr > slow_curr:
        return "buy"
    if fast_prev >= slow_prev and fast_curr < slow_curr:
        return "sell"
    return "hold"


def strategy_rsi_mean_reversion(prices, current_idx, period=14, oversold=30, overbought=70):
    """RSI mean reversion: buy when oversold, sell when overbought."""
    if current_idx < period:
        return "hold"
    subset = prices[:current_idx + 1]
    rsi = calc_rsi(subset, period)
    if rsi < oversold:
        return "buy"
    if rsi > overbought:
        return "sell"
    return "hold"


def strategy_macd_crossover(prices, current_idx, fast=12, slow=26, signal=9):
    """MACD crossover: buy when MACD crosses above signal line."""
    if current_idx < slow + signal:
        return "hold"
    # Simplified: use MACD histogram crossing zero
    macd_prev, _, _ = calc_macd(prices[:current_idx], fast, slow, signal)
    macd_curr, _, _ = calc_macd(prices[:current_idx + 1], fast, slow, signal)
    if macd_prev < 0 and macd_curr > 0:
        return "buy"
    if macd_prev > 0 and macd_curr < 0:
        return "sell"
    return "hold"


def strategy_bollinger_reversal(prices, current_idx, period=20, std_dev=2):
    """Bollinger reversal: buy near lower band, sell near upper band."""
    if current_idx < period:
        return "hold"
    subset = prices[:current_idx + 1]
    recent = subset[-period:]
    sma = sum(recent) / period
    variance = sum((p - sma) ** 2 for p in recent) / period
    std = variance ** 0.5
    lower = sma - std_dev * std
    upper = sma + std_dev * std
    current_price = subset[-1]
    if current_price <= lower:
        return "buy"
    if current_price >= upper:
        return "sell"
    return "hold"


STRATEGY_MAP = {
    "sma_crossover": strategy_sma_crossover,
    "rsi_mean_reversion": strategy_rsi_mean_reversion,
    "macd_crossover": strategy_macd_crossover,
    "bollinger_reversal": strategy_bollinger_reversal,
}


# ---------------------------------------------------------------------------
# BACKTEST ENGINE
# ---------------------------------------------------------------------------

def run_backtest(strategy_name, prices, holds, **params):
    """
    Run a backtest of the given strategy.
    Returns detailed trade log and performance metrics.
    """
    strategy_fn = STRATEGY_MAP.get(strategy_name)
    if not strategy_fn:
        print(f"[ERROR] Unknown strategy: {strategy_name}")
        print(f"  Available: {', '.join(STRATEGY_MAP.keys())}")
        return None

    trades = []
    position = 0  # 0 = cash, 1 = invested
    entry_price = 0
    entry_idx = 0
    cash = 10000.0  # starting capital
    shares = 0
    equity_curve = []

    for i in range(len(prices)):
        signal = strategy_fn(prices, i, **params)

        if signal == "buy" and position == 0:
            entry_price = prices[i]
            entry_idx = i
            shares = cash / entry_price
            position = 1
            equity = 0
            trade_type = "buy"
        elif signal == "sell" and position == 1:
            exit_price = prices[i]
            gross_return = (exit_price - entry_price) / entry_price
            cash = shares * exit_price
            shares = 0
            position = 0
            trade_type = "sell"
            trades.append({
                "entry_idx": entry_idx,
                "exit_idx": i,
                "entry_price": round(entry_price, 2),
                "exit_price": round(exit_price, 2),
                "return_pct": round(gross_return * 100, 2),
                "bars_held": i - entry_idx,
            })
        else:
            trade_type = None

        # Track equity
        if position == 1:
            equity = shares * prices[i]
        else:
            equity = cash
        equity_curve.append(round(equity, 2))

    # Close any open position at the end
    if position == 1:
        exit_price = prices[-1]
        gross_return = (exit_price - entry_price) / entry_price
        cash = shares * exit_price
        trades.append({
            "entry_idx": entry_idx,
            "exit_idx": len(prices) - 1,
            "entry_price": round(entry_price, 2),
            "exit_price": round(exit_price, 2),
            "return_pct": round(gross_return * 100, 2),
            "bars_held": len(prices) - 1 - entry_idx,
        })

    # Compute metrics
    total_return = round((cash / 10000 - 1) * 100, 2) if cash != 0 else 0
    final_equity = round(cash, 2)
    annualized_return = round(((cash / 10000) ** (252 / len(prices)) - 1) * 100, 2) if len(prices) > 0 else 0

    # Win rate
    wins = [t for t in trades if t["return_pct"] > 0]
    losses = [t for t in trades if t["return_pct"] <= 0]
    win_rate = round(len(wins) / len(trades) * 100, 1) if trades else 0

    # Average win/loss
    avg_win = round(sum(t["return_pct"] for t in wins) / len(wins), 2) if wins else 0
    avg_loss = round(abs(sum(t["return_pct"] for t in losses) / len(losses)), 2) if losses else 0

    # Profit factor
    gross_profit = sum(t["return_pct"] for t in wins) if wins else 0
    gross_loss = abs(sum(t["return_pct"] for t in losses)) if losses else 0
    profit_factor = round(gross_profit / gross_loss, 2) if gross_loss > 0 else float("inf")

    # Sharpe ratio
    returns_list = [(equity_curve[i] - equity_curve[i-1]) / equity_curve[i-1] for i in range(1, len(equity_curve)) if equity_curve[i-1] > 0]
    if returns_list:
        avg_ret = sum(returns_list) / len(returns_list)
        var_ret = sum((r - avg_ret) ** 2 for r in returns_list) / len(returns_list)
        std_ret = var_ret ** 0.5
        sharpe = round((avg_ret / std_ret) * math.sqrt(252), 2) if std_ret > 0 else 0
    else:
        sharpe = 0

    # Max drawdown
    peak = equity_curve[0] if equity_curve else 10000
    max_dd = 0.0
    for e in equity_curve:
        if e > peak:
            peak = e
        dd = (peak - e) / peak * 100
        if dd > max_dd:
            max_dd = dd
    max_dd = round(max_dd, 2)

    # Sortino
    if returns_list:
        downside = [r for r in returns_list if r < 0]
        if downside:
            downside_var = sum(r ** 2 for r in downside) / len(downside)
            downside_std = downside_var ** 0.5
            sortino = round((avg_ret / downside_std) * math.sqrt(252), 2) if downside_std > 0 else 0
        else:
            sortino = 999.0  # No downside = perfect
    else:
        sortino = 0

    result = {
        "strategy": strategy_name,
        "params": params,
        "total_return_pct": total_return,
        "annualized_return_pct": annualized_return,
        "final_equity": final_equity,
        "sharpe": sharpe,
        "sortino": sortino,
        "max_drawdown_pct": max_dd,
        "win_rate_pct": win_rate,
        "avg_win_pct": avg_win,
        "avg_loss_pct": avg_loss,
        "profit_factor": profit_factor,
        "num_trades": len(trades),
        "total_bars": len(prices),
        "trades": trades,
        "equity_curve": equity_curve,
    }
    return result


def walk_forward_backtest(strategy_name, prices, folds=4, **params):
    """Walk-forward validation: train on fold 1, test on fold 2, etc."""
    if len(prices) < 200:
        return {"error": f"Need at least 200 bars, got {len(prices)}"}

    fold_size = len(prices) // folds
    all_results = []

    for fold in range(folds - 1):
        train_end = (fold + 1) * fold_size
        test_end = min((fold + 2) * fold_size, len(prices))
        train_prices = prices[:train_end]
        test_prices = prices[train_end:test_end]

        if len(test_prices) < 30:
            continue

        result = run_backtest(strategy_name, test_prices, [], **params)
        if result:
            result["fold"] = fold + 1
            result["train_bars"] = len(train_prices)
            result["test_bars"] = len(test_prices)
            all_results.append(result)

    if not all_results:
        return {"error": "Walk-forward produced no results"}

    # Aggregate
    avg_return = sum(r["total_return_pct"] for r in all_results) / len(all_results)
    avg_sharpe = sum(r["sharpe"] for r in all_results) / len(all_results)
    avg_dd = sum(r["max_drawdown_pct"] for r in all_results) / len(all_results)

    return {
        "strategy": strategy_name,
        "params": params,
        "mode": "walk_forward",
        "folds": folds,
        "total_folds_with_data": len(all_results),
        "avg_return_pct": round(avg_return, 2),
        "avg_sharpe": round(avg_sharpe, 2),
        "avg_max_drawdown_pct": round(avg_dd, 2),
        "fold_results": all_results,
    }


def compute_hash(result):
    """Compute SHA-256 hash of the result for verification."""
    canonical = json.dumps(result, sort_keys=True)
    return hashlib.sha256(canonical.encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description="Hermes Backtest Engine")
    parser.add_argument("--strategy", required=True, help="Strategy name (sma_crossover, rsi_mean_reversion, macd_crossover, bollinger_reversal)")
    parser.add_argument("--symbol", required=True, help="Ticker symbol")
    parser.add_argument("--period", default="2023-01-01,2025-01-01", help="Date range: START,END (YYYY-MM-DD,YYYY-MM-DD)")
    parser.add_argument("--walk-forward", action="store_true", help="Use walk-forward validation")
    parser.add_argument("--folds", type=int, default=4, help="Number of folds for walk-forward")
    parser.add_argument("--fast-period", type=int, default=20, help="Fast period for SMA/MACD")
    parser.add_argument("--slow-period", type=int, default=50, help="Slow period for SMA/MACD")
    parser.add_argument("--oversold", type=int, default=30, help="RSI oversold threshold")
    parser.add_argument("--overbought", type=int, default=70, help="RSI overbought threshold")
    args = parser.parse_args()

    symbol = args.symbol.upper()

    # Parse date range
    try:
        parts = args.period.split(",")
        start_date = parts[0].strip()
        end_date = parts[1].strip()
    except (IndexError, ValueError):
        print("[ERROR] Period must be START,END (e.g., 2023-01-01,2025-01-01)")
        sys.exit(1)

    print(f"{'='*60}")
    print(f"Backtest: {args.strategy} on {symbol}")
    print(f"Period:   {start_date} to {end_date}")
    print()

    # Fetch data
    print(f"Fetching data...")
    data = get_historical_data(symbol, start_date, end_date)
    if not data:
        print(f"[ERROR] No data returned for {symbol} in period {start_date}..{end_date}")
        sys.exit(1)

    prices = [bar.get("c", 0) for bar in data]
    print(f"Got {len(prices)} bars")

    # Parameter setup
    params = {}
    if args.strategy == "sma_crossover":
        params["fast_period"] = args.fast_period
        params["slow_period"] = args.slow_period
    elif args.strategy == "rsi_mean_reversion":
        params["period"] = args.fast_period
        params["oversold"] = args.oversold
        params["overbought"] = args.overbought
    elif args.strategy == "macd_crossover":
        params["fast"] = args.fast_period
        params["slow"] = args.slow_period
    elif args.strategy == "bollinger_reversal":
        params["period"] = args.fast_period
        params["std_dev"] = 2

    # Run backtest
    print(f"\nRunning {'walk-forward' if args.walk_forward else 'standard'} backtest...\n")

    if args.walk_forward:
        result = walk_forward_backtest(args.strategy, prices, args.folds, **params)
    else:
        result = run_backtest(args.strategy, prices, [], **params)

    if result is None:
        print("[ERROR] Backtest failed")
        sys.exit(1)

    if "error" in result:
        print(f"[ERROR] {result['error']}")
        sys.exit(1)

    # Display results
    if args.walk_forward:
        print(f"WALK-FORWARD VALIDATION ({args.folds} folds)")
        print(f"  Avg Return:     {result['avg_return_pct']:+.2f}%")
        print(f"  Avg Sharpe:     {result['avg_sharpe']}")
        print(f"  Avg Max DD:     {result['avg_max_drawdown_pct']:.2f}%")
        print(f"  Folds w/ data:  {result['total_folds_with_data']}")
        print(f"\n  Fold breakdown:")
        for f in result["fold_results"]:
            print(f"    Fold {f['fold']}: train={f['train_bars']} test={f['test_bars']} bars, "
                  f"return={f['total_return_pct']:+.2f}%, sharpe={f['sharpe']}, dd={f['max_drawdown_pct']:.1f}%")
    else:
        print(f"PERFORMANCE METRICS")
        print(f"  Total Return:    {result['total_return_pct']:+.2f}%")
        print(f"  Annualized:      {result['annualized_return_pct']:+.2f}%")
        print(f"  Final Equity:    ${result['final_equity']:,.2f}")
        print(f"  Sharpe Ratio:    {result['sharpe']}")
        print(f"  Sortino Ratio:   {result['sortino']}")
        print(f"  Max Drawdown:    {result['max_drawdown_pct']:.2f}%")
        print(f"  Win Rate:        {result['win_rate_pct']:.1f}%")
        print(f"  Avg Win:         {result['avg_win_pct']:+.2f}%")
        print(f"  Avg Loss:        {result['avg_loss_pct']:.2f}%")
        print(f"  Profit Factor:   {result['profit_factor']}")
        print(f"  Trades:          {result['num_trades']}")
        print(f"  Data Bars:       {result['total_bars']}")

        if result["trades"]:
            top = sorted(result["trades"], key=lambda t: t["return_pct"], reverse=True)[:5]
            print(f"\n  Top 5 trades:")
            for t in top:
                print(f"    #{t['entry_idx']}→#{t['exit_idx']}: ${t['entry_price']:.2f}→${t['exit_price']:.2f} "
                      f"({t['return_pct']:+.2f}%), held {t['bars_held']} bars")

    # Compute verification hash
    result_hash = compute_hash(result)

    # Add metadata
    full_result = {
        "symbol": symbol,
        "strategy": args.strategy,
        "period": {"start": start_date, "end": end_date},
        "params": params,
        "walk_forward": args.walk_forward,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "hash": result_hash,
        "results": result,
    }

    # Save
    os.makedirs(TRADING_DATA_DIR, exist_ok=True)
    mode = "wf" if args.walk_forward else "bt"
    filename = f"{TRADING_DATA_DIR}/{mode}-{args.strategy}-{symbol}-{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    with open(filename, "w") as f:
        json.dump(full_result, f, indent=2, default=str)
    print(f"\nSaved: {filename}")
    print(f"Hash:  {result_hash}")
    print(f"\nVerify with: python3 -c \"import hashlib; import json; "
          f"d=json.load(open('{filename}')); "
          f"h=hashlib.sha256(json.dumps(d['results'], sort_keys=True).encode()).hexdigest(); "
          f"print('VERIFIED' if h == d['hash'] else 'TAMPERED')\"")


if __name__ == "__main__":
    main()
