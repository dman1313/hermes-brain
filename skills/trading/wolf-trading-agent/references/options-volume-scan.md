# Options Volume Scanner — Working Pattern

Scans 80+ tickers for unusual options activity using yfinance. Produces ranked lists by total volume, P/C ratio, and V/OI turnover.

## Usage

```bash
python3 /tmp/options_volume_scan.py
```

## Key Design Decisions

1. **Always write to .py file first** — never use bash heredocs for scripts containing `&` (pandas boolean indexing). The `&` gets interpreted as shell backgrounding.
2. **time.sleep(2) between requests** — Yahoo Finance rate-limits aggressively. At 20 tickers with 2s delay, works reliably. At 80+ tickers without delay, gets rate-limited hard.
3. **ATM ±10% filter** — only count options within ±10% of current price for volume/OI stats. Avoids noise from deep OTM lottery tickets.
4. **volume.fillna(0).sum()** — yfinance sometimes returns NaN volume. Always fillna before summing.
5. **fast_info for price** — use `getattr(info, 'last_price', None) or getattr(info, 'previous_close', None)` as fallback.

## Output Format

```
TICKER      PRICE          EXP   CALL_V    PUT_V    TOTAL    P/C   V/OI
----------------------------------------------------------------------
NVDA       215.91   2026-05-29 1,013,678  319,404 1,333,082   0.32   1.91
```

- **P/C ratio**: put_volume / call_volume. < 0.7 = bullish, > 1.3 = bearish, 0.7-1.3 = neutral
- **V/OI ratio**: total_volume / total_open_interest. > 1.5 = unusual (fresh positioning), > 2.5 = extreme

## Signal Tiers

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

## Pitfalls

- yfinance returns IV as decimal (0.13 = 13%), display as percentage
- 0DTE options show high V/OI because OI is low (hasn't built up yet)
- Some tickers (small caps, SPACs) have empty options chains — always wrap in try/except
- Market hours: data is stale after close. Best to run during market hours or right after close for same-day data
