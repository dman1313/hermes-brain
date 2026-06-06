# High-IV Stock Options: BE (Bloom Energy) Pattern

Bloom Energy (BE) consistently trades at 130-160% implied volatility across all expiration dates due to its volatile fuel cell technology business model. This reference documents the BE-specific options playbook.

## BE Profile

- **Stock price range**: $270-300 range (June 2026)
- **IV range**: 130-160% across all expirations
- **P/C ratio**: Typically near-neutral (0.90-1.00) on aggregate volume
- **Sector**: Clean energy / fuel cells
- **Volume**: ~5M shares/day, options chain has 500+ contracts (3-5 expirations)

## Key Behaviors

### IV Term Structure
BE's IV term structure is often **backwardated** — weekly IV (150-160%) can be higher than 2-week IV (130%). This means the market prices the highest uncertainty into the immediate expiration.

**Implication:** For weekly plays, the premium is richest. For multi-week plays, the IV drop is a headwind (theta isn't the only decay — IV itself contracts).

### ATM Delta Profile
Because IV is so extreme, ATM delta barely changes across durations:
- 1d ATM: call delta ~0.52
- 7d ATM: call delta ~0.54  
- 13d ATM: call delta ~0.58

Compare to a normal-IV stock where 7d ATM delta would be ~0.45 and 13d ~0.50.

### Breadth vs Depth of Chain
BE has ~260 calls and ~240 puts across its expirations (~500 total contracts). This is narrower than megacaps (NFLX has 500 contracts for a single expiration alone), so:
- Strike gaps are $2.50 wide (vs $1.00 for active names)
- Bid-ask spreads are wide (often $1-3 non-ATM)
- Deep OTM strikes (>20% away) may have no quotes or stale data

## When to Trade BE Options

### Best Setups

1. **Bull Put Credit Spread** (preferred for BE's high IV)
   - Sell high IV → collect fat premium
   - Example: BE $280/$270 weekly put spread
   - Short put at ~0.30 delta, wide $10 strikes
   - Premium can be 30-40% of max risk width
   - Exit at 50% profit or hold to expiry

2. **Bear Call Credit Spread** (when stock is near resistance)
   - If BE is near $300 resistance
   - Sell $300/$310 call spread
   - Same logic: high IV → elevated credit

3. **Avoid**: Long naked calls/puts (IV crush kills even directional winners)

### When NOT to Trade BE
- **Avoid vertical debit spreads**: The high IV means you overpay for the long leg. A $280/$290 bull call debit spread needs a $290+ move just to break even.
- **Avoid 0DTE**: IV on 0DTE can hit 200%+. The premium is lottery-ticket pricing.
- **Avoid during sector-wide clean energy selloffs**: BE correlates with other clean energy names on macro days. The high IV won't save you from a gap.

### Price Anchor Points
Key technical levels to watch (from Alpaca stock snapshots):
- Support $272-275 (recent low from intraday swings)
- Resistance $295-300 (large call volume clusters)
- 52-week range informs strike selection width

## Reading the BE Chain

When a user asks "what delta" or "how far out" for BE:

1. List all available expirations (usually 3: this Fri, next Fri, the one after)
2. Show ATM delta for each — the surprising fact is they barely change
3. Explain that this is an IV artifact, not a feature of the stock
4. Recommend credit spreads explicitly (the IV rewards sellers, not buyers)
5. Give concrete strike suggestions: short leg ~0.30 delta, wide $10-$15 strikes for safety

### Example Script for Quick Display

```python
# Get expirations from raw Alpaca snapshots
exps = set()
for sym in snaps.keys():
    suffix = sym[len("BE"):]
    exps.add(suffix[:6])
# Sort, convert to dates, compute DTE
# Find ATM strike per expiry from the parsed calls list
```

See `references/occ-symbol-parsing.md` for the OCC parsing pattern.
