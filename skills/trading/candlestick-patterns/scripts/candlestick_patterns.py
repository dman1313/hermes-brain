#!/usr/bin/env python3
"""
Candlestick Pattern Detector — standalone Hermes skill.
Replaces ruflo market-pattern's memory_search/memory_list with Massive grouped daily data.
Detects doji, hammer, engulfing, morning star, evening star, head & shoulders, and more.

Usage:
  python3 candlestick_patterns.py --symbol AAPL
  python3 candlestick_patterns.py --symbols AAPL,MSFT --periods 5,20,50
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
    req.add_header("User-Agent", "Hermes-Candlestick-Patterns/1.0")
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


def get_stock_data(symbol, days=120):
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


# ---------------------------------------------------------------------------
# CANDLESTICK PATTERN DETECTION
# ---------------------------------------------------------------------------

def detect_doji(candle, tolerance_pct=0.1):
    """Doji: open ≈ close. Body is very small relative to range."""
    o, h, l, c = candle["o"], candle["h"], candle["l"], candle["c"]
    body = abs(c - o)
    range_total = h - l
    if range_total == 0:
        return False
    body_ratio = body / range_total
    return body_ratio < tolerance_pct


def detect_hammer(candle, body_to_wick_ratio=3.0):
    """Hammer: small body at top, long lower wick (2-3x body)."""
    o, h, l, c = candle["o"], candle["h"], candle["l"], candle["c"]
    body = abs(c - o)
    if body == 0:
        return False
    lower_wick = min(o, c) - l
    if lower_wick <= 0:
        return False
    return lower_wick / body >= body_to_wick_ratio


def detect_inverted_hammer(candle, body_to_wick_ratio=3.0):
    """Inverted hammer: small body at bottom, long upper wick."""
    o, h, l, c = candle["o"], candle["h"], candle["l"], candle["c"]
    body = abs(c - o)
    if body == 0:
        return False
    upper_wick = h - max(o, c)
    if upper_wick <= 0:
        return False
    return upper_wick / body >= body_to_wick_ratio


def detect_bullish_engulfing(candle1, candle2):
    """Bullish engulfing: red candle followed by larger green candle that engulfs it."""
    o1, c1 = candle1["o"], candle1["c"]
    o2, c2 = candle2["o"], candle2["c"]
    bearish = c1 < o1  # first candle is red
    bullish = c2 > o2  # second is green
    engulfs = o2 <= c1 and c2 >= o1  # green engulfs red body
    return bearish and bullish and engulfs


def detect_bearish_engulfing(candle1, candle2):
    """Bearish engulfing: green candle followed by larger red candle that engulfs it."""
    o1, c1 = candle1["o"], candle1["c"]
    o2, c2 = candle2["o"], candle2["c"]
    bullish = c1 > o1  # first candle is green
    bearish = c2 < o2  # second is red
    engulfs = c2 <= o1 and o2 >= c1  # red engulfs green body
    return bearish and bullish and engulfs


def detect_morning_star(candles):
    """Morning star (3-candle reversal pattern)."""
    if len(candles) < 3:
        return False
    c1, c2, c3 = candles[-3], candles[-2], candles[-1]
    # First: tall red candle
    body1 = abs(c1["c"] - c1["o"])
    range1 = c1["h"] - c1["l"]
    if range1 == 0:
        return False
    tall_bearish = (c1["c"] < c1["o"]) and (body1 / range1 > 0.5)
    # Second: small body (doji-like)
    body2 = abs(c2["c"] - c2["o"])
    range2 = c2["h"] - c2["l"]
    small_body = range2 > 0 and (body2 / range2) < 0.3
    # Gap down to second candle
    gap_down = c2["h"] < c1["c"] if c1["c"] < c1["o"] else c2["h"] < c1["o"]
    # Third: tall green candle closing above midpoint of first
    body3 = abs(c3["c"] - c3["o"])
    tall_bullish = c3["c"] > c3["o"] and (body3 / range2 if range2 > 0 else True)
    closes_above_mid = c3["c"] > (c1["o"] + c1["c"]) / 2
    return tall_bearish and small_body and gap_down and tall_bullish and closes_above_mid


def detect_evening_star(candles):
    """Evening star (3-candle top reversal)."""
    if len(candles) < 3:
        return False
    c1, c2, c3 = candles[-3], candles[-2], candles[-1]
    body1 = abs(c1["c"] - c1["o"])
    range1 = c1["h"] - c1["l"]
    if range1 == 0:
        return False
    tall_bullish = (c1["c"] > c1["o"]) and (body1 / range1 > 0.5)
    body2 = abs(c2["c"] - c2["o"])
    range2 = c2["h"] - c2["l"]
    small_body = range2 > 0 and (body2 / range2) < 0.3
    gap_up = c2["l"] > c1["c"]
    body3 = abs(c3["c"] - c3["o"])
    tall_bearish = c3["c"] < c3["o"]
    closes_below_mid = c3["c"] < (c1["o"] + c1["c"]) / 2
    return tall_bullish and small_body and gap_up and tall_bearish and closes_below_mid


def detect_three_white_soldiers(candles):
    """Three white soldiers: three consecutive tall green candles with higher closes."""
    if len(candles) < 3:
        return False
    result = True
    for i in range(-3, 0):
        c = candles[i]
        if c["c"] <= c["o"]:
            result = False
            break
    if result:
        opens_rising = all(candles[i]["o"] > candles[i - 1]["o"] for i in range(-2, 0))
        closes_rising = all(candles[i]["c"] > candles[i - 1]["c"] for i in range(-2, 0))
        result = opens_rising and closes_rising
    return result


def detect_three_black_crows(candles):
    """Three black crows: three consecutive tall red candles with lower closes."""
    if len(candles) < 3:
        return False
    result = True
    for i in range(-3, 0):
        c = candles[i]
        if c["c"] >= c["o"]:
            result = False
            break
    if result:
        opens_falling = all(candles[i]["o"] < candles[i - 1]["o"] for i in range(-2, 0))
        closes_falling = all(candles[i]["c"] < candles[i - 1]["c"] for i in range(-2, 0))
        result = opens_falling and closes_falling
    return result


def detect_head_and_shoulders(candles, min_bars=30):
    """Simple head & shoulders detection on price levels."""
    if len(candles) < min_bars:
        return None
    recent_highs = [max(candles[i]["h"], candles[i - 1]["h"], candles[i - 2]["h"]) for i in range(2, len(candles))]
    if len(recent_highs) < 20:
        return None
    # Find local maxima
    peaks = []
    for i in range(2, len(recent_highs) - 2):
        if (recent_highs[i] > recent_highs[i - 1] and
            recent_highs[i] > recent_highs[i - 2] and
            recent_highs[i] > recent_highs[i + 1] and
            recent_highs[i] > recent_highs[i + 2]):
            peaks.append({"index": i, "price": recent_highs[i]})

    if len(peaks) < 3:
        return None

    # Look for 3-peak pattern: left shoulder < head > right shoulder
    for i in range(len(peaks) - 2):
        ls, h, rs = peaks[i], peaks[i + 1], peaks[i + 2]
        if h["price"] > ls["price"] and h["price"] > rs["price"]:
            # Shoulders roughly equal
            if abs(ls["price"] - rs["price"]) / h["price"] < 0.05:
                # Neckline at the troughs between shoulders
                trough_between = min(candles[h["index"]]["l"], candles[h["index"] - 1]["l"])
                return {
                    "pattern": "head_and_shoulders",
                    "direction": "bearish",  # Head & shoulders is typically a top reversal
                    "reliability": 0.7,
                    "neckline": round(trough_between, 2),
                    "left_shoulder_price": round(ls["price"], 2),
                    "head_price": round(h["price"], 2),
                    "right_shoulder_price": round(rs["price"], 2),
                }

    return None


def detect_double_top(candles):
    """Double top: two peaks at similar price levels."""
    if len(candles) < 30:
        return None
    highs = [c["h"] for c in candles]
    # Find top 3 local maxima
    peaks = []
    for i in range(2, len(highs) - 2):
        if (highs[i] > highs[i - 1] and highs[i] > highs[i - 2] and
            highs[i] > highs[i + 1] and highs[i] > highs[i + 2] and
            highs[i] == max(highs[max(0, i - 5):min(len(highs), i + 6)])):
            peaks.append({"index": i, "price": highs[i]})

    if len(peaks) < 2:
        return None

    for i in range(len(peaks) - 1):
        p1, p2 = peaks[i], peaks[i + 1]
        gap = p2["index"] - p1["index"]
        if 5 <= gap <= 30:  # 5-30 bars between peaks
            diff_pct = abs(p1["price"] - p2["price"]) / max(p1["price"], p2["price"])
            if diff_pct < 0.03:  # Peaks within 3%
                # Check for a trough between them
                trough = min(c["l"] for c in candles[p1["index"]:p2["index"] + 1])
                return {
                    "pattern": "double_top",
                    "direction": "bearish",
                    "reliability": round(0.7 - diff_pct * 10, 2),
                    "peak1": round(p1["price"], 2),
                    "peak2": round(p2["price"], 2),
                    "trough": round(trough, 2),
                    "target": round(trough - (p1["price"] - trough), 2),
                }

    return None


def detect_double_bottom(candles):
    """Double bottom: two dips at similar price levels."""
    if len(candles) < 30:
        return None
    lows = [c["l"] for c in candles]
    dips = []
    for i in range(2, len(lows) - 2):
        if (lows[i] < lows[i - 1] and lows[i] < lows[i - 2] and
            lows[i] < lows[i + 1] and lows[i] < lows[i + 2] and
            lows[i] == min(lows[max(0, i - 5):min(len(lows), i + 6)])):
            dips.append({"index": i, "price": lows[i]})

    if len(dips) < 2:
        return None

    for i in range(len(dips) - 1):
        d1, d2 = dips[i], dips[i + 1]
        gap = d2["index"] - d1["index"]
        if 5 <= gap <= 30:
            diff_pct = abs(d1["price"] - d2["price"]) / max(d1["price"], d2["price"])
            if diff_pct < 0.03:
                peak = max(c["h"] for c in candles[d1["index"]:d2["index"] + 1])
                return {
                    "pattern": "double_bottom",
                    "direction": "bullish",
                    "reliability": round(0.7 - diff_pct * 10, 2),
                    "dip1": round(d1["price"], 2),
                    "dip2": round(d2["price"], 2),
                    "peak": round(peak, 2),
                    "target": round(peak + (peak - d1["price"]), 2),
                }

    return None


# ---------------------------------------------------------------------------
# MAIN SCANNER
# ---------------------------------------------------------------------------

def scan_patterns(candles):
    """Scan all candles for known patterns. Returns list of detections."""
    patterns = []

    # Single-candle patterns (check last 20 candles)
    for i in range(max(0, len(candles) - 20), len(candles)):
        c = candles[i]
        if detect_doji(c):
            patterns.append({"index": i, "pattern": "doji", "type": "reversal", "direction": "neutral",
                             "reliability": 0.5, "note": "Indecision / potential reversal"})
        if detect_hammer(c):
            direction = "bullish" if c["c"] >= c["o"] else "bearish"
            patterns.append({"index": i, "pattern": "hammer", "type": "reversal", "direction": direction,
                             "reliability": 0.6, "note": "Bullish reversal after downtrend"})
        if detect_inverted_hammer(c):
            direction = "bullish" if c["c"] <= c["o"] else "bearish"
            patterns.append({"index": i, "pattern": "inverted_hammer", "type": "reversal", "direction": direction,
                             "reliability": 0.5, "note": "Potential bottom reversal"})

    # Two-candle patterns (check recent pairs)
    for i in range(max(1, len(candles) - 10), len(candles)):
        c1, c2 = candles[i - 1], candles[i]
        if detect_bullish_engulfing(c1, c2):
            patterns.append({"index": i, "pattern": "bullish_engulfing", "type": "reversal", "direction": "bullish",
                             "reliability": 0.7, "note": "Strong bullish reversal signal"})
        if detect_bearish_engulfing(c1, c2):
            patterns.append({"index": i, "pattern": "bearish_engulfing", "type": "reversal", "direction": "bearish",
                             "reliability": 0.7, "note": "Strong bearish reversal signal"})

    # Three-candle patterns
    if len(candles) >= 3:
        for i in [len(candles)]:
            subset = candles[i - 3:i] if i >= 3 else []
            if len(subset) == 3:
                if detect_morning_star(subset):
                    patterns.append({"index": i - 1, "pattern": "morning_star", "type": "reversal",
                                     "direction": "bullish", "reliability": 0.8, "note": "Strong bullish reversal"})
                if detect_evening_star(subset):
                    patterns.append({"index": i - 1, "pattern": "evening_star", "type": "reversal",
                                     "direction": "bearish", "reliability": 0.8, "note": "Strong bearish reversal"})

    if len(candles) >= 3:
        c_last3 = candles[-3:]
        if detect_three_white_soldiers(c_last3):
            patterns.append({"index": len(candles) - 1, "pattern": "three_white_soldiers", "type": "continuation",
                             "direction": "bullish", "reliability": 0.75, "note": "Strong sustained buying"})
        if detect_three_black_crows(c_last3):
            patterns.append({"index": len(candles) - 1, "pattern": "three_black_crows", "type": "continuation",
                             "direction": "bearish", "reliability": 0.75, "note": "Strong sustained selling"})

    # Multi-candle patterns
    hs = detect_head_and_shoulders(candles)
    if hs:
        patterns.append({"index": len(candles) - 1, **hs})

    dt = detect_double_top(candles)
    if dt:
        patterns.append({"index": len(candles) - 1, **dt})

    db = detect_double_bottom(candles)
    if db:
        patterns.append({"index": len(candles) - 1, **db})

    # Sort by reliability descending, remove duplicates
    seen = set()
    unique = []
    for p in sorted(patterns, key=lambda x: x.get("reliability", 0), reverse=True):
        key = p["pattern"]
        if key not in seen:
            seen.add(key)
            unique.append(p)

    return unique


def main():
    parser = argparse.ArgumentParser(description="Hermes Candlestick Pattern Scanner")
    parser.add_argument("--symbol", help="Single ticker symbol")
    parser.add_argument("--symbols", help="Comma-separated tickers")
    parser.add_argument("--periods", default="120", help="Days of data to fetch (default: 120)")
    args = parser.parse_args()

    symbols_str = args.symbols if args.symbols else args.symbol
    if not symbols_str:
        print("Usage: python3 candlestick_patterns.py --symbol AAPL")
        sys.exit(1)

    symbols = [s.strip().upper() for s in symbols_str.split(",")]
    days = int(args.periods)

    all_results = []

    for symbol in symbols:
        print(f"\n{'='*60}")
        print(f"[{symbol}] Fetching {days} days of data...")
        data = get_stock_data(symbol, days)
        if not data:
            print(f"[{symbol}] SKIP — no data")
            continue

        print(f"[{symbol}] Got {len(data)} bars")
        candles = data

        patterns = scan_patterns(candles)
        current_price = candles[-1]["c"]
        previous_close = candles[-2]["c"] if len(candles) >= 2 else current_price
        change_pct = round((current_price - previous_close) / previous_close * 100, 2)

        result = {
            "symbol": symbol,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "price": current_price,
            "change_pct": change_pct,
            "patterns_found": len(patterns),
            "patterns": patterns,
        }
        all_results.append(result)

        print(f"\n  Price: ${current_price:.2f} ({change_pct:+.2f}%)")
        print(f"  Patterns found: {len(patterns)}")
        if patterns:
            print()
            for p in patterns:
                rel = p.get("reliability", 0.5) * 100
                direction = p.get("direction", "neutral")
                dir_icon = {"bullish": "🟢", "bearish": "🔴", "neutral": "⚪"}.get(direction, "⚪")
                ptype = p.get("type", "")
                print(f"    {dir_icon} {p['pattern'].replace('_', ' ').title():30s} "
                      f"{ptype:15s} {direction:10s} {rel:.0f}% confidence")
                if "note" in p:
                    print(f"       → {p['note']}")
                if "neckline" in p:
                    print(f"       → Neckline: ${p['neckline']:.2f}")
                if "target" in p:
                    print(f"       → Target: ${p['target']:.2f}")
        else:
            print("  No significant patterns detected")

        # Save
        os.makedirs(TRADING_DATA_DIR, exist_ok=True)
        filename = f"{TRADING_DATA_DIR}/patterns-{symbol}-{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        with open(filename, "w") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"  Saved: {filename}")

    # Summary
    if len(all_results) > 1:
        print(f"\n{'='*60}")
        print("PATTERN SCAN SUMMARY")
        for r in all_results:
            print(f"  {r['symbol']}: {r['patterns_found']} patterns, price ${r['price']:.2f} ({r['change_pct']:+.2f}%)")


if __name__ == "__main__":
    main()
