# News-Driven Momentum Detection

## Overview

Complementary to Wolf's social sentiment approach. Instead of "what are people talking about," this answers "what's actually moving on a news catalyst right now."

**Script:** `~/.hermes/scripts/momentum-scanner.py`

**When to use:** Catching catalyst-driven momentum runs (QBTs, ARM-style). When a stock gaps up on news and volume explodes — detect it early, not after the move.

## Pipeline

```
NEWS LAYER (catch the catalyst)
├── yfinance news (no key) or Finnhub (free key, better)
├── Entity extraction — company/sector from headlines
├── Sentiment scoring — keyword-based bullish/bearish
└── Velocity detection — 3x+ article volume in 6h window

PRICE LAYER (confirm the move)
├── yfinance historical — current price, volume, gaps
├── Volume confirmation — 1.5x+ avg daily volume
├── Price confirmation — gap up >2%, broke 5d high
└── Sector spillover — other stocks in same theme moving

SIGNAL (the alert)
├── News catalyst detected ✓
├── Sentiment shift confirmed ✓
├── Volume confirming ✓
└── → ALERT with composite score
```

## Scoring Formula

```
score = base_severity (1-2)
      + keyword_hits (up to +3)
      + volume_confirms (+3 if vol >= 1.5x avg)
      + price_confirms (+3 if gap up or broke high)
      + gap_up (+2)
      + broke_5d_high (+2)
      + compound_signals (+3 if multiple signal types for same ticker)
```

Score >= 8: strong momentum run
Score >= 4: worth watching
Score < 4: noise

## Signal Types (adapted from FinceptTerminal)

1. **sentiment_shift** — Headlines shift from neutral to bullish (avg keyword score >= 1.5 across recent articles)
2. **velocity_spike** — 5+ articles in 6 hours for a single ticker (normal is 0-2)
3. **triangulation** — Same story covered by 3+ different sources (high confidence)
4. **sector_heat** — Sector-wide news volume + positive sentiment (spillover detection)

## Data Sources

### yfinance (default, no API key)
- `yf.Ticker(ticker).news` — returns recent articles
- `yf.Ticker(ticker).history()` — price/volume data
- **PITFALL: Aggressive rate limits** — see below

### Finnhub (preferred, free tier)
- Sign up: finnhub.io/register (instant, no credit card)
- Free tier: 60 calls/min, real-time US stocks, company news with sentiment
- Set `FINNHUB_API_KEY` environment variable
- Better news quality than yfinance, no rate limit issues at 60/min

### FinceptTerminal patterns (reference architecture)
- `fetch_company_news.py` — GNews wrapper (Google News, no key)
- `news_nlp.py` — Entity extraction (countries, orgs, people, tickers), sentiment
- `news_correlation.py` — Signal detection (velocity, triangulation, keyword spikes, geo-convergence)
- Repo: github.com/Fincept-Corporation/FinceptTerminal (AGPL-3.0 + commercial dual license)

## Sector Watchlists

Pre-configured in the scanner:
- **quantum** — IONQ, RGTI, QUBT, QBTS, ARQQ, QSI
- **ai** — ARM, NVDA, AMD, SMCI, MRVL, AVGO, TSM, MU
- **semiconductors** — NVDA, AMD, INTC, MU, AVGO, MRVL, QCOM, ARM, TSM
- **ev** — TSLA, RIVN, LCID, NIO, XPEV, LI
- **crypto_mara** — MARA, RIOT, CLSK, MSTR, COIN, HUT, BITF
- **robotics** — SOUN, PLTR, PATH, SYM, SERV, WKSP
- **space** — RKLB, ASTR, MNTS, RDW, SPCE, ASTS
- **energy** — XOM, CVX, COP, EOG, SLB, OXY, FANG
- **defense** — LMT, RTX, NOC, GD, LHX, BA

Custom tickers: `--tickers IONQ,ARM`
Custom sectors: `--sectors quantum,ai`

## Pitfalls

### yfinance News Rate Limits
- **The #1 operational issue.** yfinance aggressively rate-limits news endpoints.
- ~8-10 tickers per batch before hitting "Too Many Requests"
- Need **1.5 second delay** between ticker calls
- Rate limit persists for 60-90 seconds after being hit
- Workaround: Finnhub free key eliminates this entirely
- If rate-limited: wait 2 minutes, reduce ticker count

### News Quality
- yfinance news is delayed and sometimes stale (hours old)
- GNews has 12-hour delay on free tier
- Finnhub is real-time for company news
- For catching EARLY catalysts, speed matters — Finnhub > yfinance > GNews

### Sentiment Keywords
- Keyword-based sentiment (not ML) — directional, not precise
- Add new bullish/bearish terms to POSITIVE_KEYWORDS / NEGATIVE_KEYWORDS as market language evolves
- "moon", "rocket", "pops" are valid bullish signals for meme/momentum stocks
- "hits all-time high", "rocketing" should also match — check for substring matches

### Sector Auto-Detection
- SECTOR_KEYWORDS maps headlines to sectors
- Some keywords overlap (e.g., "nvidia" triggers both "ai" and "semiconductors")
- This is intentional — dual-sector signals are stronger

## Cron Setup

```bash
# Pre-market scan (8:05 AM ET = 12:05 UTC)
5 12 * * 1-5 python3 ~/.hermes/scripts/momentum-scanner.py --sectors quantum,ai,semiconductors --alert --json

# Mid-day scan (12:05 PM ET = 16:05 UTC)
5 16 * * 1-5 python3 ~/.hermes/scripts/momentum-scanner.py --sectors quantum,ai,semiconductors --alert
```

## Relationship to Wolf

Wolf = social sentiment scanner (what people are talking about)
Momentum = catalyst scanner (what's actually moving on news)

Use Wolf for discovery (find the tickers). Use Momentum for timing (confirm the move is real).
Run both pre-market for maximum coverage.
