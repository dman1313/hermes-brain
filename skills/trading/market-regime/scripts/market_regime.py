#!/usr/bin/env python3
"""
Market Regime Detector — standalone Hermes skill.
Replaces ruflo's neural-trader --regime-detect with Massive API indicators + classification logic.

Usage:
  python3 market_regime.py --symbol SPY
  python3 market_regime.py --symbols AAPL,MSFT,GOOGL
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

MASSIVE_API_KEY = "I_NK53ie5NuBz_VP1f6cMporEkozLxzi"
BASE_URL = "https://api.massiveapi.io"
DATE_FMT = "%Y-%m-%d"
TRADING_DATA_DIR = "/home/ubuntu/trading-data"

# Standard market regime definitions
REGIME_DEFINITIONS = {
    "bull": {
        "description": "Strong uptrend — risk-on environment",
        "recommended_strategies": ["trend-following", "momentum", "long-biased"],
        "caution": "Overbought conditions possible, watch for divergence",
    },
    "bear": {
        "description": "Strong downtrend — risk-off environment",
        "recommended_strategies": ["short-biased", "put-credit-spreads", "defensive"],
        "caution": "Avoid catching falling knives, wait for reversal confirmation",
    },
    "ranging": {
        "description": "Sideways movement — mean-reversion environment",
        "recommended_strategies": ["mean-reversion", "iron-condors", "short-straddles"],
        "caution": "Breakout risk — set stops outside the range",
    },
    "volatile": {
        "description": "High volatility — uncertainty regime",
        "recommended_strategies": ["long-straddles", "strangles", "reduced-position-sizing"],
        "caution": "Wide stops needed, position size down 50%",
    },
    "recovery": {
        "description": "Recovering from decline — improving conditions",
        "recommended_strategies": ["dip-buying", "bull-put-spreads", "gradual-accumulation"],
        "caution": "V-bottom recoveries often retest — scale in, don't go all-in",
    },
    "bubble": {
        "description": "Extended rally with extreme valuations",
        "recommended_strategies": ["profit-taking", "protective-puts", "trend-following-with-trailing-stops"],
        "caution": "Don't short a bubble — wait for the breakdown, then fade",
    },
}


def fetch_json(url, headers=None):
    """Fetch JSON from URL with error handling."""
    req = Request(url)
    req.add_header("User-Agent", "Hermes-Market-Regime/1.0")
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    try:
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except HTTPError as e:
        print(f"[ERROR] HTTP {e.code}: {e.reason} for {url}", file=sys.stderr)
        return None
    except URLError as e:
        print(f"[ERROR] {e.reason} for {url}", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON parse: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return None


def get_stock_data(symbol, days=180):
    """Fetch OHLCV data."""
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


def get_macro_data():
    """Fetch simplified VIX-like data from FRED or return simulated data."""
    # Try to get VIX directly from FRED
    url = (
        "https://api.stlouisfed.org/fred/series/observations"
        "?series_id=VIXCLS&sort_order=desc&limit=5"
        "&file_type=json&api_key=bb085e747e0fe9a68f1bc9c8a9f7a784"
    )
    data = fetch_json(url)
    if data and "observations" in data:
        observations = data["observations"]
        vals = [float(o["value"]) for o in observations if o["value"] != "."]
        if vals:
            return {"vix": vals[0], "vix_recent_high": max(vals), "vix_avg": sum(vals) / len(vals)}
    return {"vix": 18.0, "vix_recent_high": 22.0, "vix_avg": 17.0}


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


def calc_macd(prices):
    if len(prices) < 26:
        return {"macd": 0, "signal": 0, "histogram": 0}
    ema12, ema26 = prices[0], prices[0]
    mult12, mult26 = 2 / (12 + 1), 2 / (26 + 1)
    for p in prices[1:]:
        ema12 = p * mult12 + ema12 * (1 - mult12)
        ema26 = p * mult26 + ema26 * (1 - mult26)
    macd_line = ema12 - ema26
    signal_line = macd_line * (2 / (9 + 1)) + (macd_line if len(prices) < 35 else 0) * (1 - 2 / (9 + 1))
    return {"macd": round(macd_line, 4), "signal": round(signal_line, 4), "histogram": round(macd_line - signal_line, 4)}


def calc_bollinger(prices, period=20, std_dev=2):
    if len(prices) < period:
        return {"upper": 0, "middle": prices[-1] if prices else 0, "lower": 0}
    recent = prices[-period:]
    sma = sum(recent) / period
    variance = sum((p - sma) ** 2 for p in recent) / period
    std = variance ** 0.5
    return {
        "upper": round(sma + std_dev * std, 2),
        "middle": round(sma, 2),
        "lower": round(sma - std_dev * std, 2),
    }


def calc_adx(prices, period=14):
    """Simplified ADX-like trend strength indicator."""
    if len(prices) < period * 2:
        return 25.0
    # Directional movement proxy
    up_moves = [max(0, prices[i] - prices[i-1]) for i in range(1, len(prices))]
    down_moves = [max(0, prices[i-1] - prices[i]) for i in range(1, len(prices))]
    up_sum = sum(up_moves[-period:])
    down_sum = sum(down_moves[-period:])
    total = up_sum + down_sum
    if total == 0:
        return 25.0
    di_plus = up_sum / total * 100
    di_minus = down_sum / total * 100
    dx = abs(di_plus - di_minus) / (di_plus + di_minus) * 100 if (di_plus + di_minus) > 0 else 0
    return round(dx, 1)


def calc_sma(prices, period):
    if len(prices) < period:
        return None
    return sum(prices[-period:]) / period


def classify_regime(prices, volumes, macro_data):
    """Classify the current market regime based on technical indicators."""
    if len(prices) < 50:
        return {"regime": "insufficient_data", "confidence": 0.0, "reason": "Need at least 50 bars"}

    current_price = prices[-1]
    sma_20 = calc_sma(prices, 20)
    sma_50 = calc_sma(prices, 50)
    sma_200 = calc_sma(prices, 200)
    rsi = calc_rsi(prices)
    macd = calc_macd(prices)
    bb = calc_bollinger(prices)
    adx = calc_adx(prices)

    # Price change over various periods
    chg_20d = (prices[-1] - prices[-20]) / prices[-20] * 100 if len(prices) >= 20 else 0
    chg_50d = (prices[-1] - prices[-50]) / prices[-50] * 100 if len(prices) >= 50 else 0
    chg_200d = (prices[-1] - prices[-200]) / prices[-200] * 100 if len(prices) >= 200 else 0

    # Volatility
    returns = [(prices[i] - prices[i-1]) / prices[i-1] * 100 for i in range(1, len(prices))]
    volatility = (sum(abs(r) for r in returns[-20:]) / 20) if len(returns) >= 20 else 0

    vix = macro_data.get("vix", 18)
    vix_high = macro_data.get("vix_recent_high", 22)

    # Feature vector
    features = {
        "price_above_sma20": current_price > sma_20 if sma_20 else True,
        "price_above_sma50": current_price > sma_50 if sma_50 else True,
        "price_above_sma200": current_price > sma_200 if sma_200 else True,
        "sma20_above_sma50": sma_20 > sma_50 if (sma_20 and sma_50) else True,
        "sma50_above_sma200": sma_50 > sma_200 if (sma_50 and sma_200) else True,
        "rsi": rsi,
        "macd_positive": macd["histogram"] > 0,
        "bb_position": ((current_price - bb["lower"]) / (bb["upper"] - bb["lower"]) * 100) if (bb["upper"] - bb["lower"]) > 0 else 50,
        "adx": adx,
        "chg_20d": chg_20d,
        "chg_50d": chg_50d,
        "volatility": volatility,
        "vix": vix,
    }

    # Regime classification using decision rules
    scores = {regime: 0 for regime in REGIME_DEFINITIONS}
    reasons = []

    # BULL: strong uptrend
    bull_score = 0
    if features["price_above_sma20"]: bull_score += 15
    if features["price_above_sma50"]: bull_score += 15
    if features["price_above_sma200"]: bull_score += 15
    if features["sma20_above_sma50"]: bull_score += 10
    if features["sma50_above_sma200"]: bull_score += 10
    if chg_50d > 10: bull_score += 15
    if 40 < rsi < 70: bull_score += 10
    if features["macd_positive"]: bull_score += 10
    scores["bull"] = bull_score

    # BEAR: strong downtrend
    bear_score = 0
    if not features["price_above_sma20"]: bear_score += 15
    if not features["price_above_sma50"]: bear_score += 15
    if not features["price_above_sma200"]: bear_score += 10
    if not features["sma20_above_sma50"]: bear_score += 10
    if chg_50d < -10: bear_score += 15
    if rsi < 40: bear_score += 10
    if not features["macd_positive"]: bear_score += 10
    scores["bear"] = bear_score

    # RANGING: flat price action
    ranging_score = 0
    if abs(chg_20d) < 5: ranging_score += 20
    if abs(chg_50d) < 8: ranging_score += 15
    if 30 < rsi < 60: ranging_score += 15
    if adx < 25: ranging_score += 20
    if features["bb_position"] < 30 or features["bb_position"] > 70:
        pass  # near bands = potential breakout, not ranging
    else:
        ranging_score += 10
    scores["ranging"] = ranging_score

    # VOLATILE: extreme moves
    volatile_score = 0
    if features["volatility"] > 2.5: volatile_score += 20
    if vix > 30: volatile_score += 25
    if abs(chg_20d) > 8: volatile_score += 15
    if rsi > 75 or rsi < 25: volatile_score += 15
    if adx > 40: volatile_score += 15
    scores["volatile"] = volatile_score

    # RECOVERY: bounced from low but not full bull
    recovery_score = 0
    if chg_20d > 3 and chg_50d < 0: recovery_score += 25
    if features["price_above_sma20"] and not features["price_above_sma50"]: recovery_score += 20
    if rsi > 35 and rsi < 55 and chg_20d > 0: recovery_score += 15
    if features["macd_positive"] and not features["sma20_above_sma50"]: recovery_score += 15
    scores["recovery"] = recovery_score

    # BUBBLE: extended rally
    bubble_score = 0
    if chg_200d > 30: bubble_score += 20
    if rsi > 75: bubble_score += 20
    if features["bb_position"] > 90: bubble_score += 15
    if vix < 12: bubble_score += 15
    if features["price_above_sma200"] and chg_200d > 20: bubble_score += 10
    scores["bubble"] = bubble_score

    # Find best regime
    best_regime = max(scores, key=scores.get)
    best_score = scores[best_regime]
    total = sum(scores.values())
    confidence = best_score / total if total > 0 else 0.5
    confidence = round(min(max(confidence, 0.1), 0.95), 2)

    # Build reason
    if best_regime == "bull":
        reasons.append(f"Price above all key SMAs (+{chg_50d:.1f}% in 50d)")
        if features["macd_positive"]: reasons.append("MACD histogram positive")
    elif best_regime == "bear":
        reasons.append(f"Price below key SMAs ({chg_50d:.1f}% in 50d)")
        if rsi < 40: reasons.append(f"Oversold (RSI: {rsi:.0f})")
    elif best_regime == "ranging":
        reasons.append(f"Low ADX ({adx:.0f}) — no strong trend")
        reasons.append(f"RSI in neutral zone ({rsi:.0f})")
    elif best_regime == "volatile":
        reasons.append(f"VIX at {vix:.1f}, volatility at {volatility:.1f}%")
        if rsi > 75: reasons.append("Overbought territory")
    elif best_regime == "recovery":
        reasons.append(f"Up {chg_20d:.1f}% in 20d, down {abs(chg_50d):.1f}% in 50d — bounce in progress")
    elif best_regime == "bubble":
        reasons.append(f"Extended rally: +{chg_200d:.1f}% in 200d, RSI {rsi:.0f}")

    return {
        "regime": best_regime,
        "confidence": confidence,
        "scores": scores,
        "reasons": reasons,
        "description": REGIME_DEFINITIONS[best_regime]["description"],
        "recommended_strategies": REGIME_DEFINITIONS[best_regime]["recommended_strategies"],
        "caution": REGIME_DEFINITIONS[best_regime]["caution"],
        "features": {k: v for k, v in features.items() if isinstance(v, (int, float, bool))},
    }


def main():
    parser = argparse.ArgumentParser(description="Hermes Market Regime Detector")
    parser.add_argument("--symbol", default="SPY", help="Single ticker symbol (default: SPY)")
    parser.add_argument("--symbols", help="Comma-separated tickers (overrides --symbol)")
    args = parser.parse_args()

    symbols_str = args.symbols if args.symbols else args.symbol
    symbols = [s.strip().upper() for s in symbols_str.split(",")]

    macro = get_macro_data()
    if macro:
        print(f"Macro: VIX = {macro.get('vix', 'N/A')}")

    all_regimes = []

    for symbol in symbols:
        print(f"\n{'='*60}")
        print(f"[{symbol}] Fetching data...")
        data = get_stock_data(symbol, days=200)

        if not data:
            print(f"[{symbol}] SKIP — no data")
            continue

        prices = [bar.get("c", 0) for bar in data]
        volumes = [bar.get("v", 0) for bar in data]

        print(f"[{symbol}] Got {len(prices)} bars")

        analysis = classify_regime(prices, volumes, macro)
        all_regimes.append({"symbol": symbol, **analysis})

        regime = analysis["regime"]
        conf = analysis["confidence"]
        print(f"\n  Regime:      \033[1m{regime.upper()}\033[0m (confidence: {conf:.0%})")
        print(f"  Description: {analysis['description']}")
        for r in analysis["reasons"]:
            print(f"  → {r}")
        print(f"  Strategies:  {', '.join(analysis['recommended_strategies'])}")
        print(f"  Caution:     {analysis['caution']}")
        print(f"\n  Raw scores:  bull={analysis['scores']['bull']}  bear={analysis['scores']['bear']}  "
              f"ranging={analysis['scores']['ranging']}  volatile={analysis['scores']['volatile']}  "
              f"recovery={analysis['scores']['recovery']}  bubble={analysis['scores']['bubble']}")

        # Save
        os.makedirs(TRADING_DATA_DIR, exist_ok=True)
        filename = f"{TRADING_DATA_DIR}/regime-{symbol}-{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        with open(filename, "w") as f:
            json.dump({"symbol": symbol, "timestamp": datetime.now(timezone.utc).isoformat(), **analysis}, f, indent=2, default=str)
        print(f"  Saved: {filename}")

    # Summary
    print(f"\n{'='*60}")
    print("REGIME SUMMARY")
    for r in all_regimes:
        icon = {"bull": "🟢", "bear": "🔴", "ranging": "🟡", "volatile": "🟠", "recovery": "🔵", "bubble": "💎"}.get(r["regime"], "⚪")
        print(f"  {icon} {r['symbol']}: {r['regime'].upper()} ({r['confidence']:.0%})")


if __name__ == "__main__":
    main()
