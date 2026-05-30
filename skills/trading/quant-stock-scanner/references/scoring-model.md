# Scoring Model — Detailed Rubric

## Factor Weights
| Factor | Weight | Rationale |
|--------|--------|-----------|
| Momentum | 25% | Near-term price action drives trade timing |
| Value | 20% | Prevents chasing overextended names |
| Quality | 20% | Balance sheet + margin durability |
| Growth | 20% | Revenue trajectory drives multiples |
| Technicals | 15% | Confirms trend structure |

## Momentum Scoring Detail

The momentum factor captures recent price performance and volume dynamics.

**Ideal profile**: Steady climb with accelerating volume and RSI in the 50-70 zone. A stock up 5-10% on the week with RSI 55-65 and rising volume scores highest.

**Edge cases**:
- **Gap-up days** (>15% single-day move): Score capped at +20 from the 1D component. Prevents a single parabolic day from dominating.
- **Mean-reversion setups**: A stock that's down 20% in 20 days but RSI <30 gets a +10 oversold bonus, partially offsetting the negative trend. This captures bounce trades.
- **Low-vol grind-up**: Stocks with vol_ratio <0.8 but positive trend get penalized on volume component. Low-volume rallies are suspect.

## Value Scoring Detail

Value is the most sector-dependent factor. High-growth SaaS companies will perpetually score low here. That's intentional — it forces the user to acknowledge they're paying up.

**Sector adjustments** (manual, not in script):
- For REITs: Use Price/FFO instead of P/E. If P/E < 0 but FFO positive, don't penalize.
- For banks: Use Price/TBV (tangible book). P/B < 1.5 is cheap for banks.
- For unprofitable growth: P/S < 10 with >30% revenue growth can still score well overall via growth factor offset.

## Quality Scoring Detail

Quality captures balance sheet strength and margin profile.

**Key insight**: Gross margin is the strongest quality signal. A company with 90%+ gross margin (like SaaS) can burn cash on growth and still be fundamentally sound. The +20 point bonus for high GM reflects this.

**D/E ratio quirk**: yfinance returns debt-to-equity as a percentage (e.g., 140 = 140%), not a ratio. The script divides by 100 internally. If you see D/E > 100 in the raw data, it means debt exceeds equity — common for capital-intensive or acquisition-heavy companies.

## Growth Scoring Detail

Revenue growth is the primary growth signal. Analyst upside is secondary.

**Important**: If `rev_growth` is None (yfinance sometimes returns null for recent IPOs or companies that changed fiscal year), the score defaults to -10. This penalizes opacity.

## Technicals Scoring Detail

Technicals confirm the price structure. They're weighted lowest (15%) because they're the most noisy and mean-reverting.

**Bollinger Band positioning**:
- 30-70% of the band range = "sweet spot" — trending but not extended
- >90% = overbought, likely to revert
- <10% = oversold, potential bounce

**52W high proximity**: Stocks within 10% of their 52W high get a +10 bonus (strong trend). Stocks >40% below get -10 (broken trend, potential value trap or cyclical downturn).

## Options Analysis Playbook

### IV Regime Classification
- **Extreme IV** (>150%): Credit spreads only. Sell premium. Weekly put credit spreads on momentum days.
- **High IV** (100-150%): Credit spreads preferred. Bull call spreads only if strong directional conviction.
- **Moderate IV** (50-100%): Either credit or debit. Match to thesis.
- **Low IV** (<50%): Debit spreads preferred. Buy options when cheap.

### Trade Selection Matrix

| Scenario | Trade Type | Structure |
|----------|-----------|-----------|
| Bullish + High IV | Put credit spread | Sell ATM put, buy lower strike |
| Bullish + Low IV | Bull call spread | Buy ATM call, sell OTM call |
| Strong catalyst (binary) | Lotto call | Buy OTM weekly, size for 100% loss |
| Neutral + High IV | Iron condor | Sell both sides, define risk |
| Bearish + High IV | Call credit spread | Sell ATM call, buy higher strike |

### Position Sizing Rules
- **Defined-risk spreads**: Max 2% of account per trade
- **Weekly lottos**: Max 0.5% of account (100% loss expected)
- **If max loss > 2%**: Tighten spread width to 1.5%
- **Scale-in**: Enter 50% position, add on confirmation

### Entry Timing
- Don't chase gap-ups at open. Wait for 9:45-10:00 AM consolidation.
- If stock opens flat after a catalyst, that's a better entry (cheaper premium).
- Set mental stop at 50% loss for debit spreads.
- Take profit at 50% of max for credit spreads, 2-3x for debit spreads.

## Composite Score Interpretation

| Score | Meaning | Action |
|-------|---------|--------|
| 80-100 | Exceptional across all factors | High-conviction position |
| 70-79 | Strong, 1-2 minor weaknesses | Standard position size |
| 60-69 | Good, some caution needed | Smaller position or wait for pullback |
| 45-59 | Mixed signals | Watchlist only, or pair trade |
| 30-44 | Multiple red flags | Avoid or short candidate |
| 0-29 | Broken across factors | Avoid entirely |

## Common Score Profiles

**Momentum trap**: High momentum (80+), low value (<30), low quality (<40). Stock is running on hype. Example: meme stocks after a squeeze.

**Value trap**: High value (80+), low momentum (<30), low growth (<40). Cheap for a reason. Example: legacy retail in secular decline.

**Quality compounder**: High quality (80+), high growth (70+), moderate value (40-60). The sweet spot for longer-term holds. Example: mid-cap SaaS with strong margins.

**Turnaround play**: Low momentum (<40), high value (70+), improving growth (50+). Requires patience and catalyst identification.
