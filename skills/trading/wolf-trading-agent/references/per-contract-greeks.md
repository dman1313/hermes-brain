# Per-Contract Greeks Extraction from Alpaca

The aggregate options scanner (`alpaca_options_scan.py`) tells you counts and volume — but for trade construction you need per-strike Greeks: **delta, gamma, IV, bid/ask** at individual strikes and expirations.

## Endpoint

```
GET https://data.alpaca.markets/v1beta1/options/snapshots/{ticker}?feed=indicative&limit=500
```

**Headers:**
```
APCA-API-KEY-ID: <key>
APCA-API-SECRET-KEY: <secret>
```

**Returns** `{"snapshots": { "NFLX250605C00082000": { ... }, ... }}` — up to 500 contracts per ticker.

Each snapshot contains:
- `latestQuote.bp` / `latestQuote.ap` — bid/ask
- `impliedVolatility` — IV (decimal, e.g. 0.353 = 35.3%)
- `greeks.delta` / `greeks.gamma` / `greeks.theta` — Greeks
- `dailyBar.v` — volume for the day

## Parsing the OCC Symbol

The key format is `TICKER + YYMMDD + P/C + STRIKE` with zero-padded strike as 8 digits.
```
NFLX250605C00082000 → NFLX + 250605 (Jun 5 2025) + C (call) + 00082000 ($82.00)
```

Parse with:
```python
suffix = symbol[len(ticker):]       # e.g. "250605C00082000"
expiry = suffix[:6]                  # "250605"
opt_type = "CALL" if "C" in suffix[6:7] else "PUT"
strike = int(suffix[-8:]) / 1000.0  # 82.0
```

## Filtering by Moneyness

```python
price = 81.73  # from StockSnapshot
atm_low = price * 0.9
atm_high = price * 1.1
atm = [s for s in contracts if atm_low <= s['strike'] <= atm_high]
```

## Stock Price Source

Get current price from stock snapshot:
```python
snap = requests.get(
    f"https://data.alpaca.markets/v2/stocks/{ticker}/snapshot",
    headers=HEADERS
).json()
price = float(snap.get("latestTrade", {}).get("p", 0))
```

## Working Example (Full Script)

See `~/hermes-trading/agents/signal-scanner/` for the production version, but the ad-hoc pattern used in-session:

```python
import os, requests, json
from dotenv import load_dotenv
load_dotenv(os.path.expanduser("~/alpaca-bot/.env"))

API_KEY = os.environ.get("ALPACA_API_KEY")
SECRET = os.environ.get("ALPACA_SECRET_KEY")
HEADERS = {"APCA-API-KEY-ID": API_KEY, "APCA-API-SECRET-KEY": SECRET}

ticker = "NFLX"

# Stock price
stock = requests.get(
    f"https://data.alpaca.markets/v2/stocks/{ticker}/snapshot",
    headers=HEADERS, timeout=10
).json()
price = float(stock.get("latestTrade", {}).get("p", 0))

# Options snapshots
r = requests.get(
    f"https://data.alpaca.markets/v1beta1/options/snapshots/{ticker}",
    headers=HEADERS,
    params={"feed": "indicative", "limit": 500},
    timeout=15
)
snaps = r.json().get("snapshots", {})

calls, puts = [], []
for sym, snap in snaps.items():
    suffix = sym[len(ticker):]
    strike = int(suffix[-8:]) / 1000.0
    opt_type = "CALL" if "C" in suffix[6:7] else "PUT"
    expiry = suffix[:6]

    iv = snap.get("impliedVolatility", 0) or 0
    g = snap.get("greeks", {})
    delta = float(g.get("delta", 0)) if g.get("delta") else None
    quote = snap.get("latestQuote", {})
    bid = float(quote.get("bp", 0) or 0)
    ask = float(quote.get("ap", 0) or 0)

    entry = {'strike': strike, 'delta': delta, 'iv': iv,
             'bid': bid, 'ask': ask, 'expiry': expiry, 'type': opt_type}
    (calls if opt_type == "CALL" else puts).append(entry)
```

## Output Interpretation

From the June 4 NFLX scan:

| Strike | Delta | IV | Volume | Expiry | Note |
|--------|-------|-----|--------|--------|------|
| $82 | **0.440** | 35.3% | 13,157 | Weekly (6/5) | Huge concentration |
| $83 | 0.242 | 40.6% | 12,130 | Weekly (6/5) | OTM lotto |
| $81 | 0.684 | 37.8% | 3,319 | Weekly (6/5) | ATM |
| $82 | 0.492 | 31.9% | 1,669 | 6/12 | Next week |

Key insight: **0.40-0.50 delta** (slightly OTM call) is the sweet spot for bull call spread long legs. These strikes have the best gamma-to-premium ratio — enough directional exposure without overpaying for deep ITM options.

## Comparison with Aggregate Scanner

| | Aggregate (alpaca_options_scan.py) | Per-Contract (this pattern) |
|---|---|---|
| **What you see** | Total call/put count, IV, vol | Delta, gamma, theta per strike |
| **Best for** | Finding unusual activity | Building specific trades |
| **Speed** | ~4 min for 61 tickers | ~1 sec per ticker |
| **Limit** | 500 per ticker | 500 per ticker |

## Pitfalls

- **After-hours prices**: Alpaca snapshots return the last trade of the day, which may be stale. Don't rely on Alpaca quotes for display prices after hours — use them only for ATM filtering.
- **Expiry format**: `YYMMDD` — `250605` = June 5, 2025 (not 2025 — Alpaca uses the full date in the OCC symbol). Parse the first two digits as century: `25` = 2025, `26` = 2026.
- **IV is decimal**: 0.353 = 35.3%. Multiply by 100 for percentage display.
- **Delta for puts is negative**: Alpaca returns -0.50 for an ATM put. When filtering by absolute delta, take `abs(delta)`.
- **Bid/ask can be zero**: For illiquid strikes, both bid and ask may be 0. Skip strikes with `bid == 0 and ask == 0`.
