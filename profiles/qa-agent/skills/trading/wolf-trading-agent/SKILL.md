---
name: wolf-trading-agent
description: Wolf Trading Agent — daily scanner of Reddit, Twitter/X, and financial news for stock/options trade signals. Scores and ranks potential trades using multi-source fusion.
version: 1.0.0
author: Hermes Agent
license: MIT
tags: [trading, reddit, twitter, news, stock-scanner, options, signals, wolf]
related_skills: [alpaca-volume-scanner, de-bono-stock-analysis, xurl, cronjob-model-management]
---

# 🐺 Wolf Trading Agent

Daily stock/options signal scanner. Monitors Reddit, Twitter/X, and financial news for ticker mentions, sentiment, and momentum. Fuses multi-source signals into a ranked daily digest.

```
┌──────────────────────────────────────────────────────────┐
│  📡 Reddit (DuckDuckGo)  🐦 Twitter (xurl)  📰 News (GNews) │
│         ↓                      ↓                ↓        │
│  ┌──────────────────────────────────────────────────┐    │
│  │         🧠 Scoring Engine                        │    │
│  │  mentions × sentiment × source_diversity × tier  │    │
│  └──────────────────────────────────────────────────┘    │
│                        ↓                                 │
│  🟢 STRONG BUY   🟡 WATCH   ⚪ NEUTRAL                  │
│                        ↓                                 │
│              📱 Telegram Digest                          │
└──────────────────────────────────────────────────────────┘
```

## Quick Start

```bash
# Full scan (all 3 sources: Reddit + Twitter + GNews)
# Requires: GNEWS_API_KEY in environment (free — sign up at gnews.io/register)
cd ~/.hermes/skills/trading/wolf-trading-agent/scripts
python3 wolf_scan.py

# Single scanner test
python3 wolf_scan.py --scanner reddit
python3 wolf_scan.py --scanner twitter
python3 wolf_scan.py --scanner news     # GNews API — structured JSON, 14 financial queries

# With explicit API key
GNEWS_API_KEY=your_key python3 wolf_scan.py

# JSON output
python3 wolf_scan.py --json
```

## Architecture

### Scanners
| Scanner | Backend | Auth Required | Notes |
|---------|---------|---------------|-------|
| Reddit | DuckDuckGo `site:reddit.com` | No | Searches r/WSB, r/stocks, r/options, etc. |
| Twitter/X | `xurl` CLI | Yes (OAuth 2.0) | Falls back gracefully if not configured |
| News | GNews API | No (free tier) | Structured JSON, works standalone + cron. 100 req/day, 12h delay. |

### Scoring Formula

```
Total Score = source_weight × (mention_score × 0.6 + sentiment_bonus × 0.2 + velocity_bonus × 0.2)
```

- **mention_score**: Normalized ticker mentions across all sources (0-1)
- **sentiment_bonus**: Lexicon-based bullish/bearish analysis (-1 to 1)
- **velocity_bonus**: Multi-source signal (1 source=0.33, 2=0.66, 3=1.0)
- **source_weight**: Reddit 0.35, Twitter 0.35, News 0.30

### Signal Tiers
- 🟢 **STRONG BUY** — score ≥ 0.70
- 🟡 **WATCH** — score ≥ 0.40
- ⚪ **NEUTRAL** — score < 0.40

### Spread Strategist

Wolf includes a vertical spread evaluator (`spread_evaluator.py`) that applies Dwayne's Small-Account Vertical Spread Playbook (see `references/vertical-spread-playbook.md`).

**Decision flow:**
1. Take top-scored signals (≥ 0.35 score)
2. Classify directional bias (bullish/bearish/neutral) from sentiment + source count
3. Determine IV regime → credit spreads (high IV) or debit spreads (low IV)
4. Suggest strikes: credit → short at ~30 delta, debit → long at ~60/short at ~40 delta
5. Small-account check: if max loss > 2% of account, auto-tighten to 1.5% width
6. Flag: IV unknown, weak conviction, or skip conditions

**Credit spread default:** short ~30 delta, ~4% OTM, profit target 50% of max
**Debit spread default:** long ~60 delta (~3% ITM buy), short ~40 delta (~2% OTM sell)

### Newsletter Generator

Wolf can produce a daily Google Doc newsletter (`wolf_newsletter.py`) with:
- Title + date header, color-coded signal tiers (green/yellow/neutral)
- Spread trade suggestions with strike details, max loss, probability OTM
- Source breakdown and metadata summary
- Formatted via Google Docs API batchUpdate (rich text, borders, alignment)

Requires Google OAuth with `documents` + `drive.file` scopes (see Pitfalls).


### Google Docs Newsletter
Creates a formatted daily trading brief as a Google Doc:
- Color-coded signal tiers (🟢🟡⚪)
- Spread trade suggestions with strike prices
- Market overview and source breakdown
- Requires Google OAuth with Docs write scope

```bash
cd ~/.hermes/skills/trading/wolf-trading-agent/scripts
python3 wolf_newsletter.py --scan /tmp/wolf_scan.json --spreads /tmp/wolf_spreads.json
```

## Files

```
scripts/
├── wolf_scan_gnews.sh        # Wrapper: exports GNEWS_API_KEY then runs scan
├── ticker_extractor.py       # Ticker symbol extraction + sentiment
├── scoring_engine.py         # Signal fusion + scoring + digest formatting
├── spread_evaluator.py       # Vertical spread playbook applied to signals
├── wolf_newsletter.py        # Google Docs daily newsletter generator
└── scanners/
    ├── reddit_scanner.py     # Reddit via DuckDuckGo
    ├── twitter_scanner.py    # Twitter via xurl CLI (or skip)
    └── news_scanner.py       # News via GNews API (free tier, structured JSON)
references/
└── vertical-spread-playbook.md  # Dwayne's small-account spread rules
└── google-docs-borderbottom-bug.md  # borderBottom API bug → workaround
```
## Daily Cron Job

The recommended setup is a daily cron job that:
## Pitfalls
## Pitfalls

- **Reddit API changes**: Reddit's JSON API now returns 403 for all unauthenticated requests. Using DuckDuckGo search as backend instead. If DuckDuckGo rate-limits, reduce SEARCH_TERMS per subreddit. Free OAuth app at https://www.reddit.com/prefs/apps (type: script) would restore direct API access — not yet implemented.
- **Twitter without xurl**: Gracefully skips Twitter if `xurl` not installed/authenticated. Score still works with Reddit + News alone. xurl installation is one-liner (`curl -fsSL https://raw.githubusercontent.com/xdevplatform/xurl/main/install.sh | bash`), but X API is paid ($5 min credits required). OAuth setup is user-only (secrets).
- **Market hours**: Best run before market open (8 AM ET) on weekdays. Running on weekends produces low-signal results.
- **GNews API free tier**: 100 requests/day, 12-hour article delay. The scanner runs 14 queries × 5 results = 70 req per scan. Works in standalone AND cron context — no `web_search` dependency. Set `GNEWS_API_KEY` env var or pass `--apikey`. Sign up free at gnews.io/register — no credit card.
- **Ticker false positives**: The `FALSE_POSITIVES` set in `ticker_extractor.py` filters common words. If new false positives appear, add them there.
- **Sentiment lexicon**: Simple word-count based. Not an ML model. Scores are directional, not precise.
- **Google Docs newsletter auth**: `wolf_newsletter.py` requires Google OAuth scopes `documents` + `drive.file` (not the old `documents.readonly` / `drive.readonly`). If Google Workspace was set up before 2026-04-30, the token likely has read-only scopes — revoke and re-authenticate via `setup.py --revoke` then `setup.py --auth-url`.
- **Google Docs API borderBottom bug (v2.188.0)**: The `updateParagraphStyle` with `borderBottom` returns `Unsupported dimension unit: UNIT_UNSPECIFIED` regardless of properties. Workaround: use `borderBetween` with `padding` instead. See `references/google-docs-borderbottom-bug.md`.
- **Spread evaluator needs prices**: Strike suggestions require a current stock price. In cron context, either fetch prices via Alpaca API or provide approximate prices from the scan metadata. The standalone `spread_evaluator.py` uses hardcoded mock data (AAPL/NVDA) — it does NOT read scan JSON. Must be called programmatically with real prices.
- **Scan data `sources` field**: The scanner emits `sources` as a string repr of a Python dict (e.g., `"{'reddit'}"`) instead of a proper list. The newsletter generator iterates `s.get("sources", [])` which iterates characters. Fix: convert with `ast.literal_eval()` before passing to newsletter.
- **Free news sources that work**: GNews API (primary, free tier, 12h delay). CNBC RSS (`search.cnbc.com/rs/search/combinedcms/view.xml`) and MarketWatch RSS (`feeds.marketwatch.com/marketwatch/topstories`) as fallback. Yahoo Finance RSS returns empty. DuckDuckGo HTML search is too slow from VPS.
- **Alpaca free tier limits**: Quotes API works fine (unlimited). Bars/minute-level historical data returns 403 ("subscription does not permit querying recent SIP data") — requires paid data plan. Paper trading account works for order execution.
- **Alpaca options**: Paper accounts get Options Level 3 (spreads). Single-leg option orders work via `MarketOrderRequest` with option contract symbols. Naked call selling is blocked (403 — "account not eligible to trade uncovered option contracts"). Multi-leg/spread orders not supported via API. Option contract lookup uses `GetOptionContractsRequest`.
- **Scan `sources` field is string, not list**: The Wolf scan JSON stores `sources` as a string like `"{'reddit'}"` rather than a list. The newsletter iterates over `s.get("sources", [])` which iterates characters of the string, producing garbage source counts and potentially breaking Google Docs formatting. Fix: `ast.literal_eval(sources)` then convert set to list before passing to newsletter.
- **News scanner uses GNews API (free tier)**: Works standalone AND in cron context — no `web_search` dependency. Free tier limitations: 100 requests/day (14 queries × 5 results = 70 req/scan max), 12-hour article delay. API key via `GNEWS_API_KEY` env var or `--apikey` flag. Some queries may return 0 results — this is normal for narrow financial searches on the free tier.
- **Spread evaluator uses mock data standalone**: `spread_evaluator.py` ignores CLI args and uses hardcoded AAPL/NVDA signals when invoked standalone. Real integration requires: (1) fetch live prices from Alpaca, (2) build signal dicts manually, (3) call `evaluate_signals(signals, prices, iv_regimes)` directly, not via CLI.
- **`borderBottom` broken in google-api-python-client 2.188.0**: Any `updateParagraphStyle` with `borderBottom` (even with valid `unit: "PT"`) returns `UNIT_UNSPECIFIED` error. Use `borderBetween` with a required `padding` sub-field instead. Also avoid mixing `namedStyleType` with custom paragraph properties in the same request — this triggers the same error.
- **Scan `sources` field is a Python `set`**: The `scoring_engine.py` aggregate function stores sources as a `set()`. When serialized via `json.dumps(..., default=str)`, it becomes a string like `"{'reddit'}"` instead of a list. The newsletter's source breakdown loop iterates over this string character-by-character, producing garbage. Fixed in `score_tickers` by converting sets to sorted lists. If you see the error again, the scan JSON was produced before the fix — preprocess with `ast.literal_eval` to convert string-set to list.
- **Spread evaluator needs prices**: Strike suggestions require a current stock price. In cron context, either fetch prices via Alpaca API or provide approximate prices from the scan metadata.
- **Scan JSON `sources` field is a string, not a list**: `wolf_scan.py --json` outputs the `sources` field as a string repr of a Python set/dict (e.g., `"{'reddit'}"`). The newsletter's source breakdown loop iterates over characters instead of source names, producing garbage. Fix in calling code with `ast.literal_eval()` to convert the string back to a list before passing to `wolf_newsletter.py`. The newsletter script itself should also be patched to auto-detect and parse string-type sources on load.
- **Google Docs `borderBottom` broken in API client 2.188.0**: `updateParagraphStyle` with `borderBottom` (any config — color, width, dashStyle, even alone) returns `Unsupported dimension unit: UNIT_UNSPECIFIED` with google-api-python-client 2.188.0. `spaceBelow` works fine. `borderBetween` works correctly and provides a visual equivalent for horizontal rules. Use `borderBetween` with `padding` + `dashStyle` + `color` + `width` instead of `borderBottom`.

## Extending

### Adding a subreddit
Edit `SUBREDDITS` in `reddit_scanner.py`.

### Adding a Twitter account
Edit `FIN_TWIT_ACCOUNTS` in `twitter_scanner.py`.

### Free Twitter via twikit

Wolf's Twitter scanner uses `xurl` CLI (paid X API, $5 min). An alternative free backend is the `twikit` Python library (`pip install twikit`) which scrapes Twitter's internal API without an API key. `twikit` supports `search_tweet()`, `get_trends()`, and `get_user_tweets()` — enough to replace xurl in the Wolf scanner at zero cost.

**Trade-off:** twikit violates Twitter ToS (scraping). Use a dedicated burner account, not a personal one. Single-developer project (bus factor of 1). Fragile — breaks when Twitter changes its internal API. Last commit: 2026-03-10.

To swap: replace `twitter_scanner.py`'s xurl calls with `twikit.Client` async calls, handling login + cookie persistence. Install: `pip install twikit`.

### Institutional-Grade Successor

Wolf has a full agent-suite successor at `/home/ubuntu/hermes-trading/` — 10 trading agents (signal-scanner, trade-pitch, risk-auditor, pre-market-brief, earnings-analyzer, strategy-backtester, technical-analyst, weekly-pnl, position-tracker, regime-detector) built on the Anthropic FSI plugin architecture. The `signal-scanner` agent is the direct Wolf upgrade, adding options flow, unusual volume, and Alpaca screener to the existing Reddit+Twitter+News sources.

### Adding a ticker
Edit `KNOWN_TICKERS` and `NAME_TO_TICKER` in `ticker_extractor.py`.

### Adjusting scoring weights
Edit `SOURCE_WEIGHTS` in `scoring_engine.py`.

### Adding a new data source
1. Create `scripts/scanners/your_scanner.py`
2. Return list of dicts — can use either format:
   - **Legacy**: `{text, source, ...}` — `text` is the raw content for ticker extraction
   - **Structured** (like GNews): `{title, description, content, url, ...}` — the scoring engine auto-builds `text` from these fields
3. Import and call in `wolf_scan.py`
4. Add to scoring engine's `SOURCE_WEIGHTS`

## Verification

```bash
# Test ticker extraction
cd ~/.hermes/skills/trading/wolf-trading-agent/scripts
python3 -c "
from ticker_extractor import extract_tickers, sentiment_score
text = 'AAPL calls mooning! NVDA breakout. Bearish on INTC.'
tickers = extract_tickers(text)
for t in tickers:
    print(f'\${t[\"ticker\"]}: {t[\"mentions\"]} mentions')
print(f'Sentiment: {sentiment_score(text):+.2f}')
"

# Test individual scanners (requires internet)
python3 wolf_scan.py --scanner reddit
python3 wolf_scan.py --scanner news    # requires GNEWS_API_KEY

# Test full pipeline (all 3 scanners → score → digest)
GNEWS_API_KEY=your_key python3 wolf_scan.py
```
