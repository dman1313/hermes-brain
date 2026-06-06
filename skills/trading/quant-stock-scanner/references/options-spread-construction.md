# Options Spread Construction — Working Patterns

How to build and evaluate vertical spreads with real Alpaca data.

## REST API Options Snapshots (Alternative to SDK)

When the SDK isn't available or you want fast batch data, use the REST API directly:

```python
import os, requests, json
from dotenv import load_dotenv
load_dotenv('/home/ubuntu/alpaca-bot/.env')

AK = os.environ.get('ALPACA_API_KEY')
SK = os.environ.get('ALPACA_SECRET_KEY')
BASE = 'https://data.alpaca.markets'
HEADERS = {'APCA-API-KEY-ID': AK, 'APCA-API-SECRET-KEY': SK}

# Get all options for a ticker (up to 500)
r = requests.get(f'{BASE}/v1beta1/options/snapshots/NFLX',
                 headers=HEADERS,
                 params={'feed': 'indicative', 'limit': 500}, timeout=15)
snaps = r.json().get('snapshots', {})
```

**CRITICAL PITFALL**: The `details.expiration_date` field is EMPTY in REST API responses. You MUST parse the OCC symbol to get expiry, type, and strike:

```python
for sym, item in snaps.items():
    # Find where ticker ends (first digit after letters)
    i = 0
    while i < len(sym) and sym[i].isalpha():
        i += 1
    rest = sym[i:]  # e.g. "260612C00082000"
    
    exp = f"20{rest[:2]}-{rest[2:4]}-{rest[4:6]}"  # "2026-06-12"
    opt_type = rest[6]   # 'C' or 'P'
    strike = int(rest[7:15]) / 1000.0  # e.g. 82.0
```

For simple tickers (all-alpha, like NFLX, MU, DRAM):
```python
exp_part = sym[4:10]    # "260612"
opt_type = sym[10]      # 'C' or 'P'
strike = int(sym[11:]) / 1000.0
```

**NOTE**: This simple fixed-offset parsing ONLY works for tickers with 1-4 alpha characters. Tickers with digits (e.g., BRK.B) need the dynamic parser above.

### Data structure from REST API

```python
item = {
    "latestQuote": {"bp": 1.63, "ap": 1.72, ...},  # bid/ask prices
    "latestTrade": {"p": 1.68, ...},
    "greeks": {"delta": 0.542, "iv": 0.85, ...},   # iv as decimal (0.85 = 85%)
    "details": {"expiration_date": "", ...},          # EMPTY — parse from sym
}
bid = float(item.get('latestQuote', {}).get('bp', 0))
ask = float(item.get('latestQuote', {}).get('ap', 0))
delta = float(item.get('greeks', {}).get('delta', 0) or 0)
```

## Building Vertical Spreads

### Bull Call Spread (Debit) — Bullish Directional

Buy ATM/ITM call, sell OTM call. Profit from upward move.

```
Buy lower strike call at ASK
Sell higher strike call at BID
Net Debit = buy_ask - sell_bid
Max Profit = (sell_strike - buy_strike) - net_debit
Max Risk = net_debit
Breakeven = buy_strike + net_debit
Return on Risk = max_profit / max_risk × 100
```

**Selection criteria:**
- Breakeven within 1-5% of current price
- Return on risk > 100% preferred
- Expiry 1-3 weeks out (sweet spot for time decay vs move probability)
- Delta on long leg 0.45-0.60 (near ATM)

### Bull Put Spread (Credit) — Premium Selling

Sell OTM put, buy further OTM put. Profit from stock staying above short strike.

```
Sell higher strike put at BID
Buy lower strike put at ASK
Net Credit = sell_bid - buy_ask
Max Profit = net_credit
Max Risk = (sell_strike - buy_strike) - net_credit
Breakeven = sell_strike - net_credit
Return on Risk = net_credit / max_risk × 100
```

**Selection criteria:**
- Short strike 5-10% below current price (OTM buffer)
- Return on risk > 20% preferred
- High IV environment favors credit spreads
- Expiry 1-3 weeks out

### When to Use Which

| Condition | Spread Type | Why |
|-----------|------------|-----|
| High IV (>80%) | Credit spread (put) | Collect rich premium |
| Low IV (<40%) | Debit spread (call) | Cheap directional bet |
| Strong relative strength | Either | Stock showing independent strength |
| Post-earnings IV crush | Credit spread | IV will collapse, benefit seller |
| Catalyst in 1-2 weeks | Debit spread (call) | Capture the move |

## Relative Strength Screening

The best setups often come from stocks that are GREEN while their sector/market is RED.

**Workflow:**
1. Get stock snapshots for a watchlist (50+ tickers via Alpaca)
2. Sort by % change
3. Identify names that are positive while sector peers are negative
4. Those names get options chain analysis
5. Build spreads on the strongest relative strength names

**Why it works**: If a stock holds up when everything else sells off, there's a buyer (institutional accumulation, short covering, catalyst). The spread gives you defined risk on that thesis.

## Spread Evaluation Checklist

Before presenting a spread to the user:

1. ✅ Calculate net debit/credit, max profit, max risk, breakeven, RoR
2. ✅ Check bid-ask spread — if spread > 30% of midprice, warn about illiquidity
3. ✅ Note any earnings within the trade duration
4. ✅ Compare RoR across multiple strikes — find the sweet spot
5. ✅ Size the risk — max loss should be tolerable
6. ✅ Check IV environment — credit vs debit decision
7. ✅ Note the breakeven as % from current price

## Presentation Format

Dwayne wants specific setups with numbers, not analysis:

```
**Ticker — Bull Call Spread, Expiry**
Buy $X C / Sell $Y C
- Buy @ $A.BC (ask)
- Sell @ $D.EF (bid)
- Net Debit: $G.HI
- Max Profit: $J.KL (if ≥$Y)
- Max Risk: $G.HI
- Return on Risk: XX%
- Breakeven: $M.NO (+X.X% from current)
```

Keep it clean. Numbers first, thesis second.
