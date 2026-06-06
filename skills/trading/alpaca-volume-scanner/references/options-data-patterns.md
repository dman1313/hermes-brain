# Alpaca Options Data — Working Patterns

Tested against live Alpaca paper API (June 2026). Free tier limitations noted.

## Get options chain for a ticker

```python
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOptionContractsRequest
from alpaca.data.historical import StockHistoricalDataClient, OptionHistoricalDataClient
from alpaca.data.requests import StockSnapshotRequest, OptionSnapshotRequest
from datetime import datetime, timedelta
from collections import defaultdict

client = TradingClient(api_key, secret_key, paper=True)
data_client = StockHistoricalDataClient(api_key, secret_key)
opt_data = OptionHistoricalDataClient(api_key, secret_key)

# 1. Get stock price + volume via snapshots (StockBarsRequest returns 403 on free tier)
snap_req = StockSnapshotRequest(symbol_or_symbols="AAPL")
snaps = data_client.get_stock_snapshot(snap_req)
s = snaps["AAPL"]
price = float(s.latest_trade.price)
vol = int(s.daily_bar.volume)
# NOTE: s.prev_daily_bar does NOT exist on free tier

# 2. Get option contracts
req = GetOptionContractsRequest(underlying_symbols=["AAPL"], limit=500)
result = client.get_option_contracts(req)
contracts = result.option_contracts  # NOT list(result)

# 3. Group by expiration and type
# IMPORTANT: c.type is ContractType enum, NOT a string
# str(c.type) = "ContractType.CALL", not "call"
exp_data = defaultdict(lambda: {"calls": [], "puts": []})
for c in contracts:
    exp = str(c.expiration_date)
    if 'call' in str(c.type).lower():
        exp_data[exp]["calls"].append(c)
    else:
        exp_data[exp]["puts"].append(c)

# 4. Get options snapshots — works for BOTH calls and puts, includes Greeks + IV
for exp in sorted(exp_data.keys())[:3]:
    call_symbols = [c.symbol for c in exp_data[exp]["calls"][:20]]
    put_symbols = [c.symbol for c in exp_data[exp]["puts"][:20]]
    all_symbols = call_symbols + put_symbols

    if all_symbols:
        snap_req = OptionSnapshotRequest(symbol_or_symbols=all_symbols)
        snaps = opt_data.get_option_snapshot(snap_req)
        for sym, osnap in snaps.items():
            iv = osnap.implied_volatility       # float (0.98 = 98%) or None
            delta = osnap.greeks.delta if osnap.greeks else None
            gamma = osnap.greeks.gamma if osnap.greeks else None
            theta = osnap.greeks.theta if osnap.greeks else None
            vega = osnap.greeks.vega if osnap.greeks else None
            bid = float(osnap.latest_quote.bid_price) if osnap.latest_quote else 0
            ask = float(osnap.latest_quote.ask_price) if osnap.latest_quote else 0
            last = float(osnap.latest_trade.price) if osnap.latest_trade else 0
            size = int(osnap.latest_trade.size) if osnap.latest_trade else 0
            # NOTE: osnap has NO daily_bar on free tier — no options volume data
```

## Key fields on OptionContract

```
c.symbol          # "AAPL260605C00068000" (OCC format)
c.type            # ContractType.CALL or ContractType.PUT (ENUM, not string!)
c.strike_price    # Decimal("68.00")
c.expiration_date # date(2026, 6, 5)
c.root_symbol     # "AAPL"
c.underlying_symbol  # "AAPL"
c.style           # "american"
c.size            # "100" (contract multiplier)
```

**PITFALL**: `c.type` is a `ContractType` enum. `str(c.type)` returns `"ContractType.CALL"`, NOT `"call"`.
```python
# WRONG
if c.type == "call": ...
if str(c.type).lower() in ('call', 'c'): ...

# CORRECT
if 'call' in str(c.type).lower(): ...
if 'put' in str(c.type).lower(): ...
```

## Key fields on OptionsSnapshot (OptionSnapshotRequest)

```
snap.symbol               # str
snap.implied_volatility   # float or None (0.98 = 98%)
snap.greeks               # OptionsGreeks or None
  .delta                  # float
  .gamma                  # float
  .theta                  # float (negative for long options)
  .vega                   # float
  .rho                    # float
snap.latest_quote         # Quote or None
  .bid_price              # Decimal or None
  .ask_price              # Decimal or None
  .bid_size               # int
  .ask_size               # int
snap.latest_trade         # Trade or None
  .price                  # float
  .size                   # int
  .timestamp              # datetime
# NO daily_bar on free tier — volume and OI unavailable
```

## Free tier data availability (updated June 2026)

| Data | Endpoint | Available? | Notes |
|------|----------|-----------|-------|
| Stock price | StockSnapshotRequest | **Yes** | `snap.latest_trade.price` |
| **Stock volume** | **StockSnapshotRequest** | **Yes** | `snap.daily_bar.volume` — best source |
| Stock daily bars | StockBarsRequest | **No** | 403: "subscription does not permit querying recent SIP data" |
| Stock minute bars | StockBarsRequest | No | 403 on free tier |
| Options chain listing | GetOptionContractsRequest | Yes | Full chain with strikes/expirations |
| **Options Greeks** | **OptionSnapshotRequest** | **Yes** | delta, gamma, theta, vega, rho — both calls AND puts |
| **Options IV** | **OptionSnapshotRequest** | **Yes** | `snap.implied_volatility` |
| **Options bid/ask** | **OptionSnapshotRequest** | **Yes** | Both calls AND puts (unlike OptionLatestQuoteRequest which fails for puts) |
| Options last trade | OptionSnapshotRequest | Yes | price + size |
| Options volume | Any | **No** | OptionsSnapshot has no daily_bar on free tier |
| Options open interest | Any | **No** | Not in free tier |
| Call option quotes | OptionLatestQuoteRequest | Yes | Bid/ask from CBOE |
| Put option quotes | OptionLatestQuoteRequest | **No** | Returns empty — use OptionSnapshotRequest instead |

### Use OptionSnapshotRequest, NOT OptionLatestQuoteRequest

`OptionLatestQuoteRequest` only returns bid/ask and **does NOT work for puts** on free tier.
`OptionSnapshotRequest` returns Greeks, IV, bid/ask, and last trade for **both calls and puts**.

## REST API Direct (Alternative to SDK)

For fast batch data without the SDK overhead, call the REST API directly:

```python
import os, requests
from dotenv import load_dotenv
load_dotenv('/home/ubuntu/alpaca-bot/.env')

AK = os.environ.get('ALPACA_API_KEY')
SK = os.environ.get('ALPACA_SECRET_KEY')
BASE = 'https://data.alpaca.markets'
HEADERS = {'APCA-API-KEY-ID': AK, 'APCA-API-SECRET-KEY': SK}

r = requests.get(f'{BASE}/v1beta1/options/snapshots/NFLX',
                 headers=HEADERS,
                 params={'feed': 'indicative', 'limit': 500}, timeout=15)
snaps = r.json().get('snapshots', {})
```

**CRITICAL PITFALL**: `details.expiration_date` is EMPTY in REST responses. Parse from OCC symbol:

```python
for sym, item in snaps.items():
    i = 0
    while i < len(sym) and sym[i].isalpha():
        i += 1
    rest = sym[i:]  # "260612C00082000"
    exp = f"20{rest[:2]}-{rest[2:4]}-{rest[4:6]}"
    opt_type = rest[6]   # 'C' or 'P'
    strike = int(rest[7:15]) / 1000.0
```

For simple 1-4 char alpha tickers (NFLX, MU, DRAM):
```python
exp_part = sym[4:10]; opt_type = sym[10]; strike = int(sym[11:]) / 1000.0
```

REST response structure:
```python
bid = float(item.get('latestQuote', {}).get('bp', 0))
ask = float(item.get('latestQuote', {}).get('ap', 0))
delta = float(item.get('greeks', {}).get('delta', 0) or 0)
```

## Interpreting options data as sentiment

With snapshots providing Greeks + IV + bid/ask for both calls and puts:

- **Put/Call delta skew**: Compare ATM put delta vs call delta magnitude. If |put delta| > |call delta| at same strike distance, puts are more expensive = bearish skew.
- **IV skew**: If put IV > call IV at same moneyness, market is paying more for downside protection.
- **ATM IV as expected move**: IV of 0.98 on a weekly = ~6% expected move (IV / sqrt(52)).
- **Theta decay**: Weekly ATM options lose $0.35-$0.45/day at ~100% IV. Plan entries accordingly.
- **Spread width**: Tight bid-ask spread = liquid strike. Spread > 30% of mid = illiquid, avoid.
- **Gamma concentration**: High gamma near ATM = option price swings hard with small stock moves.
