# OCC Option Symbol Parsing Guide (Alpaca Snapshots)

When pulling per-contract Greeks from `https://data.alpaca.markets/v1beta1/options/snapshots/{TICKER}`, the returned `snapshots` dict keys are OCC-standard option symbols. Correctly parsing the expiry, type, and strike from these symbols is essential for building a readable chain.

## Format

**`<TICKER><YYMMDD><C/P><STRIKE_ZERO_PADDED>`**

| Component | Length | Example |
|-----------|--------|---------|
| Ticker | Variable | `NFLX`, `BE`, `SPY` |
| Expiry (YYMMDD) | 6 chars | `260605` = 2026-06-05 |
| Type | 1 char | `C` = call, `P` = put |
| Strike | 8 chars (zeros-padded × 1000) | `00082000` = $82.000 |

### Examples

```
NFLX260605C00082000
|____||______|||________|
 ticker expiry C  strike=$82.00
```

```
BE260605C00305000
|_||______|||________|
BE 260605  C  $305.00
```

```
SPY260605P00550000
|__||______|||________|
SPY 260605  P  $550.00
```

## Parsing in Python

```python
suffix = symbol[len(ticker):]  # strip ticker prefix
expiry = suffix[:6]            # YYMMDD as string
opt_type = "CALL" if suffix[6] == "C" else "PUT"
strike = int(suffix[-8:]) / 1000.0  # e.g. 00082000 → 82.0
```

## KEY PITFALL: Ticker Prefix Length

The ticker prefix in the OCC symbol equals the ACTUAL ticker length with NO filler for short tickers.

```
NFLX260605C00082000   -> ticker='NFLX' (4 chars), suffix='260605C00082000'
SPY260605P00550000    -> ticker='SPY'  (3 chars), suffix='260605P00550000'
BE260605C00305000     -> ticker='BE'   (2 chars), suffix='260605C00305000'
```

The Alpaca `snapshots` dict is keyed by the FULL OCC symbol including the ticker. So:
- To get the suffix: `suffix = symbol[len(ticker):]`
- **Never** hardcode `symbol[2:]` or `symbol[3:]` — the offset depends on ticker length
- Tickers of different lengths exist in the same response (the snapshot endpoint groups by ticker)

## Helper for Alpaca Options Scan

When iterating over `snaps.items()` in `alpaca_options_scan.py`:

```python
for symbol, snap in snaps.items():
    suffix = symbol[len(TICKER):]     # dynamic offset, not hardcoded
    exp_str = suffix[:6]               # YYMMDD
    opt_type = "CALL" if suffix[6] == "C" else "PUT"
    strike = int(suffix[-8:]) / 1000.0
    
    iv = snap.get("impliedVolatility", 0)
    greeks = snap.get("greeks", {})
    delta = greeks.get("delta", None)
```

## Pitfall: REST API `details.expiration_date` is EMPTY

When calling the REST API directly (`/v1beta1/options/snapshots/{TICKER}`), the `details.expiration_date` field in the response is an empty string. You MUST parse the OCC symbol for expiry, type, and strike — do not rely on `details`.

```python
# WRONG — details.expiration_date is "" in REST responses
exp = item.get('details', {}).get('expiration_date', '')  # always ""

# CORRECT — parse from OCC symbol key
for sym, item in snaps.items():
    suffix = sym[len(TICKER):]
    exp = f"20{suffix[:2]}-{suffix[2:4]}-{suffix[4:6]}"
    opt_type = suffix[6]  # 'C' or 'P'
    strike = int(suffix[-8:]) / 1000.0
```

This pitfall does NOT affect the SDK (`OptionSnapshotRequest`) which returns proper `expiration_date` values.

## Expiration Date Conversion

```python
from datetime import datetime, timezone

yy = int(exp_str[:2])
mm = int(exp_str[2:4])
dd = int(exp_str[4:6])
expiry_dt = datetime(2000 + yy, mm, dd, 16, tzinfo=timezone.utc)

now = datetime.now(timezone.utc)
dte = (expiry_dt - now).days
```

## All Available Expirations

To find all unique expirations present in a response:

```python
exps = set()
for sym in snaps.keys():
    suffix = sym[len(TICKER):]
    exps.add(suffix[:6])

for e in sorted(exps):
    yy, mm, dd = int(e[:2]), int(e[2:4]), int(e[4:6])
    print(f"20{yy:02d}-{mm:02d}-{dd:02d}")
```
