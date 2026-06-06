#!/usr/bin/env python3
"""Options Volume Scanner via Alpaca Data API — unusual activity detector.
Usage: python3 alpaca_options_scan.py
Requires ALPACA_API_KEY + ALPACA_SECRET_KEY in ~/alpaca-bot/.env
"""
import os, sys, time
from datetime import datetime
from dotenv import load_dotenv
load_dotenv(os.path.expanduser("~/alpaca-bot/.env"))
import requests

def get_keys():
    return os.environ.get("ALPACA_API_KEY"), os.environ.get("ALPACA_SECRET_KEY")

def make_headers():
    a, s = get_keys()
    return {"APCA-API-KEY-ID": a, "APCA-API-SECRET-KEY": s}

BASE = "https://data.alpaca.markets/v1beta1/options/snapshots"

TICKERS = [
    "AAPL","MSFT","NVDA","AMZN","META","GOOGL","TSLA","AMD","NFLX","AVGO",
    "ARM","SMCI","PLTR","SOUN","IONQ","RGTI","QUBT","MARA","RIOT","COIN",
    "MSTR","CLSK","HOOD","SOFI","RKLB","ASTS",
    "INTC","MU","QCOM","MRVL","TSM",
    "RIVN","LCID","NIO","MRNA","CRSP",
    "SQ","SHOP","UBER","ABNB","CRWD","PANW","NET","DDOG","SNOW","AI",
    "PATH","SYM","BBAI","RBLX","U","TTD","ROKU",
    "SPY","QQQ","IWM","XLF","XLE","XLK","GLD","TLT",
]

def run():
    results = []
    errors = 0

    for i, tick in enumerate(TICKERS):
        try:
            r = requests.get(f"{BASE}/{tick}", headers=make_headers(),
                             params={"feed": "indicative", "limit": 500}, timeout=15)
            if r.status_code != 200:
                errors += 1
                continue
            snaps = r.json().get("snapshots", {})
            if not snaps:
                continue

            calls, puts = [], []
            for sym, snap in snaps.items():
                after = sym[len(tick):]
                iv = snap.get("impliedVolatility", 0) or 0
                g = snap.get("greeks", {})
                delta = abs(g.get("delta", 0) or 0)
                vol = snap.get("dailyBar", {}).get("v", 0) or 0
                if "C" in after[:8]:
                    calls.append({"iv": iv, "delta": delta, "vol": vol})
                elif "P" in after[:8]:
                    puts.append({"iv": iv, "delta": delta, "vol": vol})

            if not calls and not puts:
                continue

            total = len(calls) + len(puts)
            pc = len(puts) / len(calls) if calls else 99
            civ = sum(c["iv"] for c in calls) / max(len(calls), 1)
            piv = sum(p["iv"] for p in puts) / max(len(puts), 1)
            cvol = sum(c["vol"] for c in calls)
            pvol = sum(p["vol"] for p in puts)

            results.append({
                "t": tick, "calls": len(calls), "puts": len(puts), "total": total,
                "pc": round(pc, 2), "civ": round(civ, 3), "piv": round(piv, 3),
                "cvol": int(cvol), "pvol": int(pvol),
            })
            if (i + 1) % 15 == 0:
                print(f"  {i+1}/{len(TICKERS)}...", file=sys.stderr)
        except:
            errors += 1

    results.sort(key=lambda x: x["total"], reverse=True)

    def bias(r):
        if r["pc"] < 0.5: return "BULLISH"
        if r["pc"] > 2.0: return "BEARISH"
        return "NEUTRAL"

    print(f"\n{'='*75}")
    print(f"ALPACA OPTIONS VOLUME SCAN - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"   {len(TICKERS)} tickers | {len(results)} with options activity | {errors} errors")
    print(f"{'='*75}\n")

    hot = [r for r in results if r["total"] >= 80]
    warm = [r for r in results if 40 <= r["total"] < 80]
    active = [r for r in results if 20 <= r["total"] < 40]

    hdr = f"{'TICK':<6}{'CALLS':>6}{'PUTS':>6}{'TOTAL':>6}{'P/C':>6}{'cVol':>8}{'pVol':>8}{'cIV%':>7}{'pIV%':>7}  BIAS"

    if hot:
        print(f"HIGH ACTIVITY (80+ contracts)")
        print(hdr)
        print("-" * 75)
        for r in hot:
            print(f"{r['t']:<6}{r['calls']:>6}{r['puts']:>6}{r['total']:>6}{r['pc']:>6.2f}{r['cvol']:>8,}{r['pvol']:>8,}{r['civ']:>7.1%}{r['piv']:>7.1%}  {bias(r)}")

    if warm:
        print(f"\nMODERATE ACTIVITY (40-80)")
        print(hdr)
        print("-" * 75)
        for r in warm:
            print(f"{r['t']:<6}{r['calls']:>6}{r['puts']:>6}{r['total']:>6}{r['pc']:>6.2f}{r['cvol']:>8,}{r['pvol']:>8,}{r['civ']:>7.1%}{r['piv']:>7.1%}  {bias(r)}")

    if active:
        print(f"\nACTIVE (20-40)")
        print(f"{'TICK':<6}{'CALLS':>6}{'PUTS':>6}{'TOTAL':>6}{'P/C':>6}{'cVol':>8}{'pVol':>8}  BIAS")
        print("-" * 60)
        for r in active:
            print(f"{r['t']:<6}{r['calls']:>6}{r['puts']:>6}{r['total']:>6}{r['pc']:>6.2f}{r['cvol']:>8,}{r['pvol']:>8,}  {bias(r)}")

    if not hot and not warm and not active:
        print("Low activity across the board.")
        print(f"{'TICK':<6}{'CALLS':>6}{'PUTS':>6}{'TOTAL':>6}{'P/C':>6}  BIAS")
        print("-" * 40)
        for r in results[:20]:
            print(f"{r['t']:<6}{r['calls']:>6}{r['puts']:>6}{r['total']:>6}{r['pc']:>6.2f}  {bias(r)}")

    print(f"\nTotal tickers with options: {len(results)}")

if __name__ == "__main__":
    run()
