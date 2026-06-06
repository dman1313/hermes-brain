# Options Volume Scanner — Working Pattern

Scans 80+ tickers for unusual options activity. **Two backends**: yfinance (primary) and Alpaca options snapshots (fallback when yfinance is rate-limited).

## Backend 1: yfinance (primary)

```bash
python3 /tmp/options_volume_scan.py
```

## Backend 2: Alpaca Options Snapshots (fallback)

When yfinance is rate-limited (e.g. after running wolf_scan + momentum-scanner back-to-back):

Use `OptionSnapshotRequest` from `alpaca.data.requests` for options data. Use `StockSnapshotRequest` for stock volume.

```python
from alpaca.data import StockHistoricalDataClient, OptionHistoricalDataClient
from alpaca.data.requests import StockSnapshotRequest, OptionSnapshotRequest
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOptionContractsRequest

# Stock volume via snapshots (StockBarsRequest returns 403 on free tier)
stock_snap = stock_client.get_stock_snapshot(StockSnapshotRequest(symbol_or_symbols=["NVDA"]))
vol = stock_snap["NVDA"].daily_bar.volume

# Options: get contracts, then snapshots for Greeks + IV
contracts = trading.get_option_contracts(GetOptionContractsRequest(underlying_symbols=["NVDA"], limit=500)).option_contracts
# Filter ATM, get snapshots
opt_snaps = opt_client.get_option_snapshot(OptionSnapshotRequest(symbol_or_symbols=atm_symbols))
for sym, s in opt_snaps.items():
    iv = s.implied_volatility      # float (0.98 = 98%)
    delta = s.greeks.delta
    # NO volume/OI — OptionsSnapshot has no daily_bar on free tier
```

Requires `ALPACA_API_KEY` + `ALPACA_SECRET_KEY` in `~/alpaca-bot/.env`.

**Key details:**
- Use `OptionSnapshotRequest` → returns Greeks, IV, bid/ask, last trade for BOTH calls AND puts
- **No volume or OI on free tier** — `OptionsSnapshot` has no `daily_bar`
- `c.type` is `ContractType` enum — use `'call' in str(c.type).lower()` not `c.type == "call"`
- `StockSnapshotRequest` returns stock volume via `snap.daily_bar.volume`
- `StockBarsRequest` returns 403 for ALL timeframes on free tier
- No rate sleep needed (Alpaca is much more generous than yfinance)
- See alpaca-volume-scanner `references/options-data-patterns.md` for full data matrix

## Key Design Decisions

1. **Always write to .py file first** — never use bash heredocs for scripts containing `&` (pandas boolean indexing). The `&` gets interpreted as shell backgrounding.
2. **time.sleep(2) between yfinance requests** — Yahoo Finance rate-limits aggressively. At 20 tickers with 2s delay, works reliably. At 80+ tickers without delay, gets rate-limited hard. Alpaca backend needs no sleep.
3. **ATM ±10% filter** — only count options within ±10% of current price for volume/OI stats. Avoids noise from deep OTM lottery tickets.
4. **volume.fillna(0).sum()** — yfinance sometimes returns NaN volume. Always fillna before summing.
5. **fast_info for price** — use `getattr(info, 'last_price', None) or getattr(info, 'previous_close', None)` as fallback.
6. **Cascade rate-limit awareness** — if wolf_scan.py and momentum-scanner.py both ran yfinance calls, the options scanner will fail. Use Alpaca backend as fallback.
7. **Use stock volume ranking when options volume unavailable** — On Alpaca free tier, rank by `StockSnapshotRequest` volume instead. Sort by absolute volume or volume vs 20-day average (if available from another source).

## Output Format

When options volume IS available (yfinance / paid feed):
```
TICKER      PRICE          EXP   CALL_V    PUT_V    TOTAL    P/C   V/OI
----------------------------------------------------------------------
NVDA       215.91   2026-05-29 1,013,678  319,404 1,333,082   0.32   1.91
```

When only stock volume + options Greeks available (Alpaca free tier):
```
TICKER      PRICE    DAY%    VOLUME    CALL_IV   PUT_IV   ATM_DELTA  ATM_SPREAD
----------------------------------------------------------------------
NVDA       226.57   -0.2%   3,698,781    51%      55%       0.48      $0.09
```

- **P/C ratio**: put_volume / call_volume. < 0.7 = bullish, > 1.3 = bearish, 0.7-1.3 = neutral
- **V/OI ratio**: total_volume / total_open_interest. > 1.5 = unusual (fresh positioning), > 2.5 = extreme
- **IV skew**: put IV > call IV at same moneyness = bearish premium

## Signal Tiers (when volume data available)

| V/OI | P/C < 0.6 | P/C 0.6-1.0 | P/C > 1.0 |
|------|-----------|-------------|-----------|
| > 2.5 | 🔥 Extreme bullish | Fresh activity | Hedging/bearish |
| 1.5-2.5 | Bullish conviction | Moderate | Put buying |
| < 1.5 | Normal call volume | Neutral | Normal put volume |

## Deep Dive Pattern

After initial scan, run detail script on top 8-10 tickers:
- Get nearest 2 expirations
- Show top 3 calls and top 3 puts by volume per expiration
- Include strike, volume, OI, IV, last price, and ITM/OTM label
- When volume unavailable (Alpaca free): show Greeks, IV, bid/ask, spread width

## Pitfalls

- yfinance returns IV as decimal (0.13 = 13%), display as percentage
- 0DTE options show high V/OI because OI is low (hasn't built up yet)
- Some tickers (small caps, SPACs) have empty options chains — always wrap in try/except
- Market hours: data is stale after close. Best to run during market hours or right after close for same-day data
- **Alpaca OptionsSnapshot has NO daily_bar**: Free tier snapshots return Greeks, IV, quotes, and last trade — but NOT volume or open interest. Cannot compute V/OI ratio with Alpaca free tier alone.
- **ContractType enum**: `c.type` returns `ContractType.CALL` (enum). `str(c.type)` = `"ContractType.CALL"`, not `"call"`. Use `'call' in str(c.type).lower()`.
- **StockBarsRequest 403**: Returns "subscription does not permit querying recent SIP data" for ALL timeframes on free tier. Use `StockSnapshotRequest` for stock volume.
- **Alpaca endpoint mismatch**: The paper-trading URL (`paper-api.alpaca.markets/v1beta1/options/snapshots/`) returns 404. Use the data URL (`data.alpaca.markets/v1beta1/options/snapshots/`) — confirmed working 2026-06-02.
- **Cascading yfinance rate limits**: Running wolf_scan.py + momentum-scanner.py + options scanner all in sequence exhausts yfinance. Switch to Alpaca backend if you hit `YFRateLimitError`.
- **Alpaca snapshot price discrepancy**: After-hours bid/ask from Alpaca can be stale or wide. Prices may look wrong (e.g. NFLX showing $85). Don't rely on Alpaca quotes for display prices — use them only for ATM filtering. Get display prices from a separate source or cache before market close.
