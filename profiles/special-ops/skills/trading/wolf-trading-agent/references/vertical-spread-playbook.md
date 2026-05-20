# Small-Account Vertical Spread Playbook

Tastytrade-style vertical spreads for small accounts. Defined risk, high probability, repeatable.

## Core Rules
1. Trade only liquid underlyings
2. Use vertical spreads only
3. Prefer 30-45 DTE for most entries
4. Risk only a small part of the account on each trade
5. Take profits early instead of waiting for expiration

## Credit Spreads (IV High)
- Short strike target: 15-30 delta (30 delta = ~70% prob OTM)
- Take profit at 50% of max profit
- Bullish put credit: sell ATM-Δ put, buy lower put
- Bearish call credit: sell ATM+Δ call, buy higher call
- Width: tight enough to cap loss, wide enough for decent credit

## Debit Spreads (IV Low)
- Long leg: ~60 delta, Short leg: ~40 delta
- Take profit when directional move happens
- Bullish call debit: buy ITM call, sell OTM call
- Bearish put debit: buy ITM put, sell OTM put
- If move stalls, exit before theta decay eats gains

## Decision Flow
1. Check IV → high=credit, low=debit
2. Determine directional bias
3. Select strikes based on delta targets
4. Verify liquidity (tight bid-ask, good OI)
5. Confirm max loss is acceptable
6. Enter or skip

## Sizing (Small Account)
- Max loss per trade ≤ small % of account
- Several consecutive losses must be survivable
- Never widen a losing spread

## Skip Conditions
- Spread hard to understand
- Too wide / too expensive
- Max loss too large for account
- IV/delta don't align with rules
- Low liquidity / wide markets
