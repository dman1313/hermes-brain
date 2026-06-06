#!/usr/bin/env python3
"""
Trading Signal Generator — standalone Hermes skill.
Replaces ruflo's neural-trader anomaly detection with Massive API + scoring logic.

Usage:
  python3 trading_signal.py --symbols AAPL,MSFT,GOOGL
  python3 trading_signal.py --symbols SPY --strategy mean-reversion
"""
import argparse
import json
import os
import sys
import time
import hashlib
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

MASSIVE_API_KEY = "I_NK53ie5NuBz_VP1f6cMporEkozLxzi"
BASE_URL = "https://api.massiveapi.io"
TRADING_DATA_DIR = "/home/ubuntu/trading-data"

def fetch_json(url, headers=None):
    """Fetch JSON from URL with error handling."""
    req = Request(url)
    req.add_header("User-Agent", "Hermes-Trading-Signal/1.0")
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
        print(f"[ERROR] JSON parse error: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return None


def get_stock_data(symbol, days=120):
    """Fetch OHLCV data for a symbol using Massive aggregates endpoint."""
    url = (
        f"{BASE_URL}/stocks/aggregates?ticker={symbol}"
        f"&multiplier=1&timespan=day&from={days}d&to=today"
        f"&apikey={MASSIVE_API_KEY}"
    )
    data = fetch_json(url)
    if data and "results" in data:
        return data["results"]
    # Fallback: try a different endpoint pattern
    alt_url = (
        f"{BASE_URL}/v1/aggs/ticker/{symbol}/range/1/day/"
        f"{days}d/today?apikey={MASSIVE_API_KEY}"
    )
    data = fetch_json(alt_url)
    if data and "results" in data:
        return data["results"]
    return None


def calc_rsi(prices, period=14):
    """Calculate RSI from price list."""
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
    """Simple MACD: EMA12, EMA26, histogram."""
    if len(prices) < 26:
        return {"macd": 0, "signal": 0, "histogram": 0}
    ema12 = 0
    ema26 = 0
    mult12 = 2 / (12 + 1)
    mult26 = 2 / (26 + 1)
    for i, p in enumerate(prices):
        if i == 0:
            ema12 = p
            ema26 = p
        else:
            ema12 = p * mult12 + ema12 * (1 - mult12)
            ema26 = p * mult26 + ema26 * (1 - mult26)
    macd = ema12 - ema26
    signal = macd * (2 / (9 + 1)) + (macd if len(prices) < 35 else 0) * (1 - 2 / (9 + 1))
    return {"macd": round(macd, 4), "signal": round(signal, 4), "histogram": round(macd - signal, 4)}


def calc_bollinger(prices, period=20, std_dev=2):
    """Bollinger Bands."""
    if len(prices) < period:
        return {"upper": 0, "middle": prices[-1] if prices else 0, "lower": 0, "width": 0, "position_pct": 50}
    recent = prices[-period:]
    sma = sum(recent) / period
    variance = sum((p - sma) ** 2 for p in recent) / period
    std = variance ** 0.5
    upper = sma + std_dev * std
    lower = sma - std_dev * std
    current = prices[-1]
    band_width = upper - lower
    position_pct = ((current - lower) / band_width * 100) if band_width > 0 else 50
    return {
        "upper": round(upper, 2),
        "middle": round(sma, 2),
        "lower": round(lower, 2),
        "width": round(band_width, 2),
        "position_pct": round(position_pct, 1),
    }


def calc_atr(candles, period=14):
    """Average True Range from OHLC data."""
    if len(candles) < period + 1:
        return 0
    trs = []
    for i in range(1, len(candles)):
        high = candles[i]["h"]
        low = candles[i]["l"]
        prev_close = candles[i - 1]["c"]
        tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
        trs.append(tr)
    if not trs:
        return 0
    return round(sum(trs[-period:]) / period, 2)


def z_score(values):
    """Compute Z-scores for a list of values."""
    n = len(values)
    if n < 2:
        return [0] * n
    mean = sum(values) / n
    var = sum((v - mean) ** 2 for v in values) / n
    std = var ** 0.5
    if std == 0:
        return [0] * n
    return [(v - mean) / std for v in values]


def detect_anomaly(prices, volumes):
    """Classify the latest price action into anomaly types."""
    if len(prices) < 20:
        return {"type": "insufficient_data", "confidence": 0.0, "max_z": 0, "details": "Need at least 20 data points"}

    returns = [(prices[i] - prices[i - 1]) / prices[i - 1] * 100 for i in range(1, len(prices))]
    volume_ratios = [volumes[i] / volumes[i - 1] if volumes[i - 1] > 0 else 1.0 for i in range(1, len(volumes))]
    recent_returns = returns[-10:] if len(returns) >= 10 else returns
    recent_volumes = volume_ratios[-10:] if len(volume_ratios) >= 10 else volume_ratios

    return_z = z_score(recent_returns)
    vol_z = z_score(recent_volumes)
    if not return_z or not vol_z:
        return {"type": "error", "confidence": 0.0, "max_z": 0}

    max_return_z = max(abs(z) for z in return_z)
    avg_vol_z = sum(abs(z) for z in vol_z) / len(vol_z)
    last_price = prices[-1]
    sma_20 = sum(prices[-20:]) / 20

    # Check for alternating signs (oscillation / range-bound)
    signs = [1 if r > 0 else -1 for r in recent_returns]
    alternations = sum(1 for i in range(1, len(signs)) if signs[i] != signs[i - 1])
    alternation_ratio = alternations / (len(signs) - 1) if len(signs) > 1 else 0

    # Flatline detection (low Z-score = consolidation)
    recent_z_mean = sum(abs(z) for z in return_z) / len(return_z)

    classification = "normal"
    confidence = 0.0
    details = ""

    if avg_vol_z > 2.0 and max_return_z > 2.0:
        classification = "spike"
        confidence = min(max_return_z / 8, 0.95)
        direction = "bullish" if returns[-1] > 0 else "bearish"
        details = f"Volume spike ({avg_vol_z:.1f}z) with price movement ({max_return_z:.1f}z) — {direction} breakout"
    elif max_return_z > 2.5:
        # Check if it's sustained drift
        recent_pos = sum(1 for r in returns[-5:] if r > 0)
        recent_neg = sum(1 for r in returns[-5:] if r < 0)
        if recent_pos >= 4 or recent_neg >= 4:
            direction = "bullish" if recent_pos >= 4 else "bearish"
            classification = "drift"
            confidence = min(max_return_z / 6, 0.90)
            details = f"Sustained {direction} drift ({max_return_z:.1f}z) — trend forming"
        else:
            classification = "spike"
            confidence = min(max_return_z / 8, 0.85)
            direction = "bullish" if returns[-1] > 0 else "bearish"
            details = f"Price spike ({max_return_z:.1f}z) — {direction} momentum"
    elif alternation_ratio > 0.6 and recent_z_mean < 1.0:
        classification = "oscillation"
        confidence = min(alternation_ratio, 0.8)
        details = f"Alternating returns ({alternation_ratio:.0%}) — range-bound, mean-reversion opportunity"
    elif recent_z_mean < 0.5 and avg_vol_z < 0.5:
        classification = "flatline"
        confidence = 0.6
        details = "Low volatility / consolidation — prepare for breakout"
    else:
        classification = "normal"
        confidence = 0.3
        details = "Normal price action"

    return {
        "type": classification,
        "confidence": round(confidence, 2),
        "max_z": round(max_return_z, 2),
        "details": details,
        "direction": details.split("—")[-1].strip() if "—" in details else "neutral",
    }


def score_signal(symbol, anomaly, rsi, macd, bollinger, atr, prices):
    """Compute a composite signal score 0-100."""
    score = 50  # neutral baseline

    # RSI contribution (±15)
    if rsi < 30:
        score += 15  # oversold buy signal
    elif rsi < 40:
        score += 8
    elif rsi > 70:
        score -= 15  # overbought sell signal
    elif rsi > 60:
        score -= 8

    # MACD contribution (±10)
    if macd["histogram"] > 0:
        score += 10
    else:
        score -= 10

    # Bollinger position contribution (±10)
    if bollinger["position_pct"] < 15:
        score += 10  # near lower band — potential bounce
    elif bollinger["position_pct"] > 85:
        score -= 10  # near upper band — potential reversal

    # ATR volatility contribution (±5)
    atr_pct = (atr / prices[-1] * 100) if prices else 0
    if atr_pct > 3:
        score -= 5  # high vol — risky
    elif atr_pct < 0.5:
        score += 5  # low vol — stable

    # Anomaly contribution
    if anomaly["type"] == "drift":
        score += 8 if "bullish" in anomaly["details"] else -8
    elif anomaly["type"] == "spike":
        if "bullish" in anomaly.get("details", ""):
            score += 5
        elif "bearish" in anomaly.get("details", ""):
            score -= 5

    return max(0, min(100, score))


def build_signal(symbol, data):
    """Build a complete signal for one symbol from OHLCV data."""
    prices = [bar.get("c", 0) for bar in data]
    closes = [bar.get("c", 0) for bar in data]
    highs = [bar.get("h", 0) for bar in data]
    lows = [bar.get("l", 0) for bar in data]
    volumes = [bar.get("v", 0) for bar in data]

    if not prices:
        return {"symbol": symbol, "error": "No price data"}

    current_price = prices[-1]
    prev_close = prices[-2] if len(prices) >= 2 else current_price
    change_pct = round((current_price - prev_close) / prev_close * 100, 2)

    # Indicators
    rsi = calc_rsi(closes)
    macd = calc_macd(closes)
    bollinger = calc_bollinger(closes)
    atr = calc_atr([{"h": h, "l": l, "c": c} for h, l, c in zip(highs, lows, closes)])

    # Anomaly detection
    anomaly = detect_anomaly(closes, volumes)

    # Signal score
    signal_score = score_signal(symbol, anomaly, rsi, macd, bollinger, atr, closes)

    confidence = signal_score / 100.0
    if signal_score >= 75:
        direction = "strong_buy"
        action = "Enter long / add to position"
    elif signal_score >= 60:
        direction = "buy"
        action = "Accumulate on dips"
    elif signal_score >= 40:
        direction = "neutral"
        action = "Hold / wait for clearer signal"
    elif signal_score >= 25:
        direction = "sell"
        action = "Reduce position / take partial profits"
    else:
        direction = "strong_sell"
        action = "Exit / short"

    signal = {
        "symbol": symbol,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "price": current_price,
        "change_pct": change_pct,
        "direction": direction,
        "signal_score": signal_score,
        "confidence": round(confidence, 2),
        "anomaly": anomaly,
        "indicators": {
            "rsi": round(rsi, 1),
            "macd": macd,
            "bollinger": bollinger,
            "atr": atr,
        },
        "action": action,
    }
    return signal


def save_signal(signal):
    """Save signal to /home/ubuntu/trading-data/."""
    os.makedirs(TRADING_DATA_DIR, exist_ok=True)
    symbol = signal["symbol"]
    filename = f"{TRADING_DATA_DIR}/signal-{symbol}-{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    with open(filename, "w") as f:
        json.dump(signal, f, indent=2, default=str)
    print(f"[SAVED] {filename}")
    return filename


def main():
    parser = argparse.ArgumentParser(description="Hermes Trading Signal Generator")
    parser.add_argument("--symbols", required=True, help="Comma-separated ticker symbols")
    parser.add_argument("--strategy", default=None, help="Strategy name for context (e.g., mean-reversion, trend-following)")
    args = parser.parse_args()

    symbols = [s.strip().upper() for s in args.symbols.split(",")]
    all_signals = []

    for symbol in symbols:
        print(f"\n{'='*60}")
        print(f"[{symbol}] Fetching data...")
        data = get_stock_data(symbol, days=120)

        if not data:
            print(f"[{symbol}] SKIP — no data returned")
            continue

        print(f"[{symbol}] Got {len(data)} bars")
        signal = build_signal(symbol, data)
        all_signals.append(signal)

        # Print summary
        print(f"\n--- {symbol} Signal ---")
        print(f"  Price:     ${signal['price']:.2f} ({signal['change_pct']:+.2f}%)")
        print(f"  Score:     {signal['signal_score']}/100 — {signal['direction'].upper()}")
        print(f"  Confidence: {signal['confidence']:.0%}")
        print(f"  Anomaly:   {signal['anomaly']['type']} (conf: {signal['anomaly']['confidence']:.0%})")
        if signal['anomaly']['details']:
            print(f"  Details:   {signal['anomaly']['details']}")
        print(f"  RSI:       {signal['indicators']['rsi']}")
        print(f"  MACD:      {signal['indicators']['macd']['histogram']:+.4f}")
        print(f"  Bollinger:  {signal['indicators']['bollinger']['position_pct']:.0f}% band position")
        print(f"  ATR:       ${signal['indicators']['atr']:.2f}")
        print(f"  Action:    {signal['action']}")

        # Save
        save_signal(signal)

    # Summary
    print(f"\n{'='*60}")
    print(f"Generated {len(all_signals)} signals")
    buy_signals = [s for s in all_signals if s["direction"] in ("buy", "strong_buy")]
    sell_signals = [s for s in all_signals if s["direction"] in ("sell", "strong_sell")]
    if buy_signals:
        print(f"BUY signals:  {', '.join(s['symbol'] for s in buy_signals)}")
    if sell_signals:
        print(f"SELL signals: {', '.join(s['symbol'] for s in sell_signals)}")

    if args.strategy:
        print(f"\nStrategy context: {args.strategy}")


if __name__ == "__main__":
    main()
