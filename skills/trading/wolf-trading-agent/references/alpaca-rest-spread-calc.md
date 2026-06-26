# Alpaca REST API: Options Spread Calculation

Fetch real-time options chain data via **Alpaca's REST API** (no SDK needed) and calculate vertical bull/put credit spreads with real bid/ask prices, Greeks, RoC, and breakeven.

## Why This Exists

The Alpaca Python SDK (`alpaca-py`) works but adds complexity (separate client classes, async, version incompatibility with Python 3.11). The raw REST API at `data.alpaca.markets` is simpler, lighter, and works from any Python 3.x. Use this when you need a quick per-ticker spread calculation without importing the SDK.

## Auth

Credentials in `~/alpaca-bot/.env`:
```env
ALPACA_API_KEY=your_key
ALPACA_SECRET_KEY=your_secret
```

Load from python:
```python
from dotenv import load_dotenv
load_dotenv(os.path.expanduser('~/alpaca-bot/.env'))
API_KEY=os.env..._KEY = os.environ.get('ALPACA_SECRET_KEY')
headers = {'APCA-API-KEY-ID': API_KEY, 'APCA-API-SECRET-KEY': SECRET_KEY}
```

## Step 1: Get Current Stock Price

```python
r = requests.get('https://data.alpaca.markets/v2/stocks/MRVL/bars?timeframe=1Day&limit=2&adjustment=raw&feed=iex', headers=headers)
bars = r.json().get('bars', [])
price = bars[-1]['c']  # latest close price
```

The `iex` feed is free-tier accessible. Returns daily bars. Use `bars[-1]` for latest.

## Step 2: Fetch Options Snapshots

```python
r = requests.get('https://data.alpaca.markets/v1beta1/options/snapshots/MRVL', headers=headers, params={'feed': 'indicative', 'limit': 500}, timeout=15)
snaps = r.json().get('snapshots', {})
```

**Limitations on free tier:**
- Returns up to 500 contracts (capped)
- Only near-term expirations (typically 2-3 weeks out)
- No open interest data
- Greeks + IV available, but IV may be 0 for deep OTM/ITM contracts
- `latestQuote` gives bid/ask prices, NOT `dailyBar` (dailyBar returns volume/count only)

## Step 3: Decode Option Symbols

Alpaca format: `MRVLYYMMDD[C/P]SSSSSSS`

Example: `MRVL260626P00270000`
- `260626` = expiry 2026-06-26
- `P` = Put (`C` = Call)
- `00270000` = strike × 1000 → `270.00`

```python
after = sym[len('MRVL'):]  # '260626P00270000'
date = after[:6]            # '260626'
opt_type = after[6]         # 'P'
strike = int(after[7:]) / 1000  # 270.0
```

## Step 4: Extract Bid/Ask and Greeks

```python
q = snap.get('latestQuote', {})
bid = q.get('bp', 0) or 0
ask = q.get('ap', 0) or 0
greeks = snap.get('greeks', {})
delta = abs(greeks.get('delta', 0) or 0) if greeks else 0
iv = snap.get('impliedVolatility', 0) or 0
```

- `bp` = bid price, `ap` = ask price (from `latestQuote`)
- Use `or 0` fallback because Alpaca returns `null` for missing values (not 0)

## Step 5: Calculate Bull Put Credit Spread

**Structure:** Sell a higher-strike put (short leg), buy a lower-strike put (long leg) — both OTM.

```python
# net_credit = premium received from short leg - premium paid for long leg
# SELL at bid, BUY at ask (worst-case fills)
net_credit = short_put['bid'] - long_put['ask']

# Spread width = difference between strikes
width = short_strike - long_strike

# Max loss per share = spread width - net credit
max_loss_per_share = width - net_credit

# Max profit per share = net credit
max_profit_per_share = net_credit

# Return on Capital (RoC)
roc = (net_credit / (width - net_credit)) * 100

# Breakeven = short strike - net credit
breakeven = short_strike - net_credit

# Probability OTM ≈ 1 - delta_of_short_leg (rough approximation)
prob_otm = 1 - short_put['delta']
```

**Per-contract values:** multiply per-share values by 100.

## Spread Selection Heuristics

| Spread Type | Short Leg Delta | Long Leg Delta | Width |
|---|---|---|---|
| **Conservative** | 0.15-0.20 | < 0.10 | 5-10 pts |
| **Balanced** | 0.20-0.30 | 0.10-0.15 | 10-15 pts |
| **Aggressive** | 0.30-0.35 | 0.15-0.20 | 5-10 pts |

**Best RoC:** Usually found with 10-point wide spreads where the short leg is at 0.20-0.25 delta and the long leg is 10 points below (at ~0.10-0.15 delta). Tighter spreads (5 pts) have lower absolute credit but better RoC when the premium/width ratio is favorable.

## Working Example

MRVL at $321.63, Jun 26 expiry (7 DTE):

| Short | Long | Credit | Width | Max Profit | Max Loss | RoC | BE | Prob OTM |
|---|---|---|---|---|---|---|---|---|
| $270P ($3.68b) | $260P ($2.63a) | **$1.05** | $10 | $105 | -$895 | **11.7%** | $268.95 | 87% |
| $275P ($3.68b) | $265P ($2.83a) | **$0.85** | $10 | $85 | -$915 | **9.3%** | $274.15 | 85% |
| $270P ($3.68b) | $265P ($2.83a) | **$0.44** | $5 | $44 | -$456 | **9.6%** | $269.56 | 87% |

## Common Issues

- **Strike parsing off by factor**: Alpaca encodes strike × 1000 in the symbol. `00270000` = $270.00. Some older contracts use a different format — verify by checking the underlying price vs strike.
- **No bids on deep OTM strikes**: Puts with strike < 50% of spot often have bid=0. Skip them.
- **Indicative feed ≠ real-time**: `feed='indicative'` returns snapshot data, not streaming. Good enough for spread construction but verify against live quotes before execution.
- **500 contract limit**: The API returns max 500 snapshots. For liquid tickers with many strikes/expiries, you may miss some. Increase `limit` or filter by expiration.
- **REST API URL vs Paper URL**: Use `data.alpaca.markets` (not `paper-api.alpaca.markets`). Paper API returns 404 on the options snapshots endpoint.
- **Alpaca Python SDK vs REST**: If you need complex queries (by expiration range, option type, etc.), use the SDK with `python3.12` (Python 3.12 has `alpaca-py` installed). The REST API is best for simple snapshot pulls.
