#!/usr/bin/env python3
"""Quant Stock Scanner — technicals, fundamentals, composite scoring.

Usage:
    python3 quant_scan.py AAPL
    python3 quant_scan.py AAPL --score-only
    python3 quant_scan.py AAPL --options
    python3 quant_scan.py AAPL --json
"""

import sys
import json
import argparse
import os
import time
import csv
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np

try:
    import yfinance as yf
except ImportError:
    print("ERROR: yfinance not installed. Run: pip install yfinance", file=sys.stderr)
    sys.exit(1)


CACHE_DIR = Path("/tmp/quant-scan-cache")
CACHE_MAX_AGE = timedelta(hours=4)


def _cache_path(ticker):
    return CACHE_DIR / f"{ticker.upper()}_{datetime.now().strftime('%Y-%m-%d')}.json"


def _load_cache(ticker):
    """Load cached data if fresh (< 4 hours old). Returns None if stale/missing."""
    path = _cache_path(ticker)
    if not path.exists():
        return None
    mtime = datetime.fromtimestamp(path.stat().st_mtime)
    if datetime.now() - mtime > CACHE_MAX_AGE:
        path.unlink(missing_ok=True)
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def _save_cache(ticker, data):
    """Save data to cache directory."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = _cache_path(ticker)
    with open(path, "w") as f:
        json.dump(data, f, default=str)


def _safe_opt_int(val):
    """Safely convert options volume/OI to int, handling NaN and non-numeric types."""
    try:
        if val is None:
            return 0
        v = float(val)
        if v != v:  # NaN check
            return 0
        return int(v)
    except (ValueError, TypeError, OverflowError):
        return 0


def sma(data, n):
    return np.convolve(data, np.ones(n) / n, mode="valid")


def ema(data, n):
    k = 2 / (n + 1)
    e = [data[0]]
    for v in data[1:]:
        e.append(v * k + e[-1] * (1 - k))
    return np.array(e)


def rsi(data, n=14):
    deltas = np.diff(data)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    avg_gain = np.mean(gains[-n:])
    avg_loss = np.mean(losses[-n:])
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def macd(data, fast=12, slow=26, signal=9):
    ema_fast = ema(data, fast)
    ema_slow = ema(data, slow)
    ml = ema_fast[-len(ema_slow) :] - ema_slow
    sig = ema(ml, signal)
    return ml[-1], sig[-1], ml[-1] - sig[-1]


def bollinger(data, n=20, k=2):
    m = np.mean(data[-n:])
    s = np.std(data[-n:])
    return m + k * s, m, m - k * s


def atr(high, low, close, n=14):
    trs = []
    for i in range(1, len(close)):
        tr = max(
            high[i] - low[i],
            abs(high[i] - close[i - 1]),
            abs(low[i] - close[i - 1]),
        )
        trs.append(tr)
    return np.mean(trs[-n:])


def pull_data(ticker):
    """Pull OHLCV + fundamentals from yfinance with caching and retry."""
    # Try cache first
    cached = _load_cache(ticker)
    if cached is not None:
        return cached

    t = yf.Ticker(ticker)
    info = t.info

    retries = 3
    delays = [2, 4, 8]
    hist = None
    for attempt in range(retries):
        try:
            hist = t.history(period="6mo", interval="1d")
            break
        except yf.YFRateLimitError:
            if attempt < retries - 1:
                time.sleep(delays[attempt])
                continue
            print(f"ERROR: Rate-limited by yfinance for {ticker} after {retries} attempts", file=sys.stderr)
            return None
        except Exception:
            if attempt < retries - 1:
                time.sleep(delays[attempt])
                continue
            raise
    if hist.empty:
        return None

    close = hist["Close"].values
    volume = hist["Volume"].values
    high = hist["High"].values
    low = hist["Low"].values
    dates = [d.strftime("%Y-%m-%d") for d in hist.index]
    price = close[-1]

    sma20 = float(sma(close, 20)[-1]) if len(close) >= 20 else None
    sma50 = float(sma(close, 50)[-1]) if len(close) >= 50 else None
    sma200 = float(sma(close, 200)[-1]) if len(close) >= 200 else None
    ema12 = float(ema(close, 12)[-1])
    ema26 = float(ema(close, 26)[-1])
    rsi_val = float(rsi(close))
    macd_val, macd_sig, macd_hist_val = macd(close)
    bb_up, bb_mid, bb_low = bollinger(close)
    atr_val = float(atr(high, low, close))

    avg_vol_20 = float(np.mean(volume[-20:]))
    avg_vol_5 = float(np.mean(volume[-5:]))

    pct_1d = (close[-1] / close[-2] - 1) * 100 if len(close) >= 2 else 0
    pct_5d = (close[-1] / close[-6] - 1) * 100 if len(close) >= 6 else 0
    pct_20d = (close[-1] / close[-21] - 1) * 100 if len(close) >= 21 else 0
    pct_60d = (close[-1] / close[-61] - 1) * 100 if len(close) >= 61 else 0

    high_52w = float(max(hist["High"][-252:])) if len(hist) >= 252 else float(max(hist["High"]))
    low_52w = float(min(hist["Low"][-252:])) if len(hist) >= 252 else float(min(hist["Low"]))

    data = {
        "ticker": ticker.upper(),
        "name": info.get("longName", info.get("shortName", "N/A")),
        "sector": info.get("sector", "N/A"),
        "industry": info.get("industry", "N/A"),
        "price": round(float(price), 4),
        "market_cap": info.get("marketCap"),
        "enterprise_value": info.get("enterpriseValue"),
        "pe_trailing": info.get("trailingPE"),
        "pe_forward": info.get("forwardPE"),
        "pb": info.get("priceToBook"),
        "ps": info.get("priceToSalesTrailing12Months"),
        "ev_revenue": info.get("enterpriseToRevenue"),
        "ev_ebitda": info.get("enterpriseToEbitda"),
        "revenue": info.get("totalRevenue"),
        "rev_growth": info.get("revenueGrowth"),
        "gross_margin": info.get("grossMargins"),
        "op_margin": info.get("operatingMargins"),
        "profit_margin": info.get("profitMargins"),
        "fcf": info.get("freeCashflow"),
        "cash": info.get("totalCash"),
        "debt": info.get("totalDebt"),
        "debt_eq": info.get("debtToEquity"),
        "current_ratio": info.get("currentRatio"),
        "roe": info.get("returnOnEquity"),
        "beta": info.get("beta"),
        "short_ratio": info.get("shortRatio"),
        "short_pct_float": info.get("shortPercentOfFloat"),
        "analyst_target": info.get("targetMeanPrice"),
        "analyst_rec": info.get("recommendationKey"),
        "num_analysts": info.get("numberOfAnalystOpinions"),
        "sma20": round(sma20, 4) if sma20 else None,
        "sma50": round(sma50, 4) if sma50 else None,
        "sma200": round(sma200, 4) if sma200 else None,
        "ema12": round(ema12, 4),
        "ema26": round(ema26, 4),
        "rsi_14": round(rsi_val, 2),
        "macd": round(float(macd_val), 4),
        "macd_signal": round(float(macd_sig), 4),
        "macd_hist": round(float(macd_hist_val), 4),
        "bb_upper": round(float(bb_up), 4),
        "bb_middle": round(float(bb_mid), 4),
        "bb_lower": round(float(bb_low), 4),
        "atr_14": round(atr_val, 4),
        "vol_ratio_5_20": round(avg_vol_5 / avg_vol_20, 2) if avg_vol_20 > 0 else 1.0,
        "pct_1d": round(float(pct_1d), 2),
        "pct_5d": round(float(pct_5d), 2),
        "pct_20d": round(float(pct_20d), 2),
        "pct_60d": round(float(pct_60d), 2),
        "high_52w": round(high_52w, 4),
        "low_52w": round(low_52w, 4),
        "pct_from_52w_high": round((price / high_52w - 1) * 100, 2),
        "avg_vol": info.get("averageVolume"),
        "avg_vol_10d": info.get("averageVolume10days"),
        "last_5_days": [
            {
                "date": dates[i],
                "close": round(float(close[i]), 4),
                "volume": int(volume[i]),
            }
            for i in range(-5, 0)
        ],
    }
    _save_cache(ticker, data)
    return data


def score(d):
    """Compute 5-factor composite quant score (0-100)."""

    # MOMENTUM (25%)
    mom = 50.0
    mom += min(d.get("pct_1d", 0) * 2, 20)
    mom += min(d.get("pct_5d", 0), 15)
    mom += min(d.get("pct_20d", 0) * 0.5, 10)
    r = d.get("rsi_14", 50)
    if 50 <= r <= 70:
        mom += 5
    elif r > 70:
        mom -= 10
    elif r < 30:
        mom += 10
    if d.get("macd_hist", 0) > 0:
        mom += 5
    vr = d.get("vol_ratio_5_20", 1)
    if vr > 1.5:
        mom += 10
    elif vr > 1.2:
        mom += 5

    # VALUE (20%)
    val = 50.0
    pe_f = d.get("pe_forward") or 0
    if pe_f > 0 and pe_f < 15:
        val += 20
    elif pe_f > 0 and pe_f < 25:
        val += 10
    elif pe_f > 0 and pe_f < 35:
        val += 0
    elif pe_f > 0 and pe_f < 50:
        val -= 10
    elif pe_f > 0:
        val -= 20
    # else: missing data — no penalty
    ps = d.get("ps") or 0
    if ps > 0 and ps < 5:
        val += 15
    elif ps > 0 and ps < 10:
        val += 5
    elif ps > 0 and ps < 20:
        val -= 5
    elif ps > 0:
        val -= 10
    # else: missing data — no penalty
    ev_ebitda = d.get("ev_ebitda") or 0
    if ev_ebitda > 0 and ev_ebitda < 15:
        val += 10
    elif ev_ebitda > 0 and ev_ebitda < 25:
        val += 0
    elif ev_ebitda > 0:
        val -= 10
    # else: missing data — no penalty
    target = d.get("analyst_target")
    if target and d.get("price"):
        upside = (target - d["price"]) / d["price"]
        val += min(upside * 50, 15)

    # QUALITY (20%)
    qual = 50.0
    gm = d.get("gross_margin") or 0
    qual += min(int(gm * 40), 20)
    om = d.get("op_margin") or 0
    if om > 0.3:
        qual += 15
    elif om > 0.15:
        qual += 10
    elif om > 0:
        qual += 5
    else:
        qual -= 10
    pm = d.get("profit_margin") or 0
    if pm > 0.2:
        qual += 10
    elif pm > 0.1:
        qual += 5
    elif pm > 0:
        qual += 0
    else:
        qual -= 10
    roe = d.get("roe") or 0
    if roe > 0.2:
        qual += 10
    elif roe > 0.1:
        qual += 5
    cr = d.get("current_ratio") or 0
    if cr > 2:
        qual += 5
    elif cr > 1:
        qual += 0
    else:
        qual -= 10
    de_raw = d.get("debt_eq")
    if de_raw is not None and de_raw > 0:
        de = de_raw / 100
    else:
        de = None
    if de is None:
        pass  # missing data — no penalty
    elif de < 0.5:
        qual += 5
    elif de < 1:
        qual += 0
    elif de < 2:
        qual -= 5
    else:
        qual -= 10

    # GROWTH (20%)
    grw = 50.0
    rg = d.get("rev_growth") or 0
    if rg > 0.3:
        grw += 25
    elif rg > 0.2:
        grw += 15
    elif rg > 0.1:
        grw += 10
    elif rg > 0.05:
        grw += 5
    else:
        grw -= 10
    if target and d.get("price"):
        grw += min(int(upside * 40), 15)
    if d.get("pct_20d", 0) > 0:
        grw += 5

    # TECHNICALS (15%)
    tech = 50.0
    if d.get("sma20") and d["price"] > d["sma20"]:
        tech += 5
    if d.get("sma50") and d["price"] > d["sma50"]:
        tech += 5
    bb_u = d.get("bb_upper", 0)
    bb_l = d.get("bb_lower", 0)
    bb_m = d.get("bb_middle", 0)
    if bb_u > bb_l:
        bb_pos = (d["price"] - bb_l) / (bb_u - bb_l)
    else:
        bb_pos = 0.5
    if 0.3 < bb_pos < 0.7:
        tech += 10
    elif bb_pos > 0.9:
        tech -= 10
    elif bb_pos < 0.1:
        tech += 5
    if 40 <= r <= 65:
        tech += 10
    elif r > 75:
        tech -= 10
    if d.get("macd_hist", 0) > 0:
        tech += 10
    if vr > 1.2:
        tech += 5
    f52 = d.get("pct_from_52w_high", -50)
    if f52 > -10:
        tech += 10
    elif f52 > -20:
        tech += 5
    elif f52 > -40:
        tech += 0
    else:
        tech -= 10

    scores = {
        "momentum": int(min(max(mom, 0), 100)),
        "value": int(min(max(val, 0), 100)),
        "quality": int(min(max(qual, 0), 100)),
        "growth": int(min(max(grw, 0), 100)),
        "technical": int(min(max(tech, 0), 100)),
    }

    weights = {"momentum": 0.25, "value": 0.20, "quality": 0.20, "growth": 0.20, "technical": 0.15}
    composite = sum(scores[k] * weights[k] for k in weights)

    if composite >= 75:
        verdict = "STRONG BUY"
    elif composite >= 60:
        verdict = "BUY"
    elif composite >= 45:
        verdict = "HOLD"
    elif composite >= 30:
        verdict = "WEAK"
    else:
        verdict = "AVOID"

    return {"scores": scores, "composite": round(composite, 1), "verdict": verdict}


def options_scan(ticker, price):
    """Pull options chain for nearest 3 expirations."""
    t = yf.Ticker(ticker)
    expirations = t.options
    if not expirations:
        return None

    results = []
    for exp in list(expirations)[:3]:
        chain = t.option_chain(exp)
        calls = []
        for _, row in chain.calls.iterrows():
            if row["strike"] < price * 0.8 or row["strike"] > price * 1.3:
                continue
            vol = _safe_opt_int(row["volume"])
            oi = _safe_opt_int(row["openInterest"])
            calls.append({
                "strike": row["strike"],
                "bid": row["bid"],
                "ask": row["ask"],
                "volume": vol,
                "oi": oi,
                "iv": round(row["impliedVolatility"], 4),
            })

        puts = []
        for _, row in chain.puts.iterrows():
            if row["strike"] < price * 0.7 or row["strike"] > price * 1.1:
                continue
            vol = _safe_opt_int(row["volume"])
            oi = _safe_opt_int(row["openInterest"])
            puts.append({
                "strike": row["strike"],
                "bid": row["bid"],
                "ask": row["ask"],
                "volume": vol,
                "oi": oi,
                "iv": round(row["impliedVolatility"], 4),
            })

        results.append({"expiration": exp, "calls": calls, "puts": puts})

    return results


def main():
    parser = argparse.ArgumentParser(description="Quant Stock Scanner")
    parser.add_argument("ticker", help="Stock ticker symbol")
    parser.add_argument("--score-only", action="store_true", help="Only output composite score")
    parser.add_argument("--options", action="store_true", help="Include options chain")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    data = pull_data(args.ticker)
    if not data:
        print(f"ERROR: No data for {args.ticker}", file=sys.stderr)
        sys.exit(1)

    result = score(data)

    if args.json:
        output = {"data": data, "score": result}
        if args.options:
            output["options"] = options_scan(args.ticker, data["price"])
        print(json.dumps(output, indent=2, default=str))
        return

    if args.score_only:
        s = result["scores"]
        print(f"\n{data['ticker']} QUANT SCORE: {result['composite']}/100 — {result['verdict']}")
        for k, v in s.items():
            print(f"  {k.upper():>12}: {v}/100")
        return

    # Full report
    print(f"\n{'=' * 50}")
    print(f"  {data['ticker']} — {data['name']}")
    print(f"  {data['sector']} / {data['industry']}")
    print(f"{'=' * 50}")
    print(f"  Price: ${data['price']:.2f}  |  Market Cap: ${data.get('market_cap', 0) / 1e9:.1f}B")
    print(f"  1D: {data['pct_1d']:+.1f}%  5D: {data['pct_5d']:+.1f}%  20D: {data['pct_20d']:+.1f}%  60D: {data['pct_60d']:+.1f}%")
    print(f"  52W: ${data['low_52w']:.2f} – ${data['high_52w']:.2f}  ({data['pct_from_52w_high']:+.1f}% from high)")
    print(f"\n  TECHNICALS")
    print(f"  RSI: {data['rsi_14']}  MACD: {data['macd_hist']:+.4f}  ATR: {data['atr_14']:.2f}")
    print(f"  SMA20: {data.get('sma20', 'N/A')}  SMA50: {data.get('sma50', 'N/A')}")
    print(f"  BB: [{data['bb_lower']:.2f} — {data['bb_middle']:.2f} — {data['bb_upper']:.2f}]")
    print(f"  Vol ratio (5D/20D): {data['vol_ratio_5_20']:.2f}x")
    print(f"\n  FUNDAMENTALS")
    print(f"  P/E: {data.get('pe_trailing', 'N/A')} fwd {data.get('pe_forward', 'N/A')}  P/S: {data.get('ps', 'N/A')}  P/B: {data.get('pb', 'N/A')}")
    print(f"  Rev: ${data.get('revenue', 0) / 1e6:.0f}M  Growth: {(data.get('rev_growth') or 0) * 100:.1f}%")
    print(f"  Margins — Gross: {(data.get('gross_margin') or 0) * 100:.1f}%  Op: {(data.get('op_margin') or 0) * 100:.1f}%  Net: {(data.get('profit_margin') or 0) * 100:.1f}%")
    print(f"  Cash: ${data.get('cash', 0) / 1e6:.0f}M  Debt: ${data.get('debt', 0) / 1e6:.0f}M  D/E: {data.get('debt_eq', 'N/A')}")
    print(f"\n  ANALYSTS")
    print(f"  Target: ${data.get('analyst_target', 'N/A')}  Rec: {data.get('analyst_rec', 'N/A')}  ({data.get('num_analysts', 0)} analysts)")
    print(f"  Short: {(data.get('short_pct_float') or 0) * 100:.1f}% float  |  {data.get('short_ratio', 'N/A')} days to cover")

    s = result["scores"]
    print(f"\n{'=' * 50}")
    print(f"  QUANT SCORE: {result['composite']}/100 — {result['verdict']}")
    print(f"{'=' * 50}")
    for k, v in s.items():
        bar = "#" * (v // 5) + "-" * (20 - v // 5)
        print(f"  {k.upper():>12}: {v:>3}/100  [{bar}]")
    print()

    if args.options:
        opts = options_scan(args.ticker, data["price"])
        if opts:
            print(f"  OPTIONS CHAIN")
            for exp_data in opts:
                print(f"\n  === {exp_data['expiration']} ===")
                print("  CALLS:")
                for c in exp_data["calls"][:8]:
                    print(f"    K=${c['strike']:>8.2f}  Bid=${c['bid']:>6.2f}  Ask=${c['ask']:>6.2f}  Vol={c['volume']:>8}  OI={c['oi']:>8}  IV={c['iv']:.1%}")
                print("  PUTS:")
                for p in exp_data["puts"][:8]:
                    print(f"    K=${p['strike']:>8.2f}  Bid=${p['bid']:>6.2f}  Ask=${p['ask']:>6.2f}  Vol={p['volume']:>8}  OI={p['oi']:>8}  IV={p['iv']:.1%}")


if __name__ == "__main__":
    main()
