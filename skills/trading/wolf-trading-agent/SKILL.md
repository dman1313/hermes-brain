---
name: wolf-trading-agent
description: Wolf Trading Agent — daily scanner of Reddit, Twitter/X, and financial news for stock/options trade signals. Scores and ranks potential trades using multi-source fusion.
version: 1.2.0
author: Hermes Agent
license: MIT
tags: [trading, reddit, twitter, news, stock-scanner, options, signals, wolf]
related_skills: [alpaca-volume-scanner, de-bono-stock-analysis, xurl, cronjob-model-management, ragflow-dataset]
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

# RAGFlow enhancement (post-scan — enriches signals with trading context)
# Requires: RAGFLOW_API_URL + RAGFLOW_API_KEY in env (set in ~/.hermes/.env)
python3 ~/.hermes/skills/ragflow/scripts/wolf_ragflow_enhancer.py --scan output/wolf_scan_$(date +%F).json
python3 ~/.hermes/skills/ragflow/scripts/wolf_ragflow_enhancer.py --scan output/wolf_scan_$(date +%F).json --attach-digest
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
├── vertical-spread-playbook.md  # Dwayne's small-account spread rules
├── google-docs-borderbottom-bug.md  # borderBottom API bug → workaround
└── massive-api-notes.md  # Massive.com API notes (pending auth setup)
output/
└── api_discovery_*.md  # Daily Sherlock endpoint test reports
```

**External: Sherlock API Discovery Scanner**
```
~/.hermes/skills/agents/sherlock/scripts/api_discovery_scanner.py
```
Sherlock runs daily endpoint tests on 21+ financial APIs and reports which ones are actually working. Trigger with `--quick` for daily health checks or full scan for market discovery. See `~/.hermes/skills/agents/sherlock/api-discovery-subskill.md`.
## Daily Cron Job

The daily cron triggers Wolf's market scan, RAGFlow enhancement, and Sherlock's API discovery:

```bash
# Wolf daily scan (weekdays, pre-market)
0 12 * * 1-5 cd ~/.hermes/skills/trading/wolf-trading-agent/scripts && python3 wolf_scan.py --json

# RAGFlow context enrichment (5 min after scan so file exists)
5 12 * * 1-5 cd ~/.hermes/skills/ragflow/scripts && python3 wolf_ragflow_enhancer.py --scan ../trading/wolf-trading-agent/output/wolf_scan_$(date +\%F).json

# Sherlock API endpoint health check (daily)
0 12 * * * cd ~/.hermes/skills/agents/sherlock && python3 scripts/api_discovery_scanner.py --quick
```

See cronjob-model-management for setup.

### RAGFlow Enhancement

Wolf has a post-scan enhancer at `~/.hermes/skills/ragflow/scripts/wolf_ragflow_enhancer.py` that enriches top signals with relevant context from the RAGFlow wiki and wolf-trading-docs datasets. Use this to inject strategy knowledge (spread playbooks, company background) into the output.

Usage:
```bash
python3 wolf_ragflow_enhancer.py --scan output/wolf_scan_YYYY-MM-DD.json
python3 wolf_ragflow_enhancer.py --scan output/wolf_scan_YYYY-MM-DD.json --attach-digest
```

The `--attach-digest` flag injects context footnotes directly into the human-readable digest. The enhancer also adds a RAGFlow market context section with broader wiki knowledge.

Requires `RAGFLOW_API_URL` + `RAGFLOW_API_KEY` (already in `~/.hermes/.env`). The RAGFlow datasets must finish parsing before the enhancer returns results — if it returns empty context, check parse status with the ragflow-dataset skill.

## Pitfalls

### Data Sources
- **Reddit API changes**: Reddit's JSON API now returns 403 for all unauthenticated requests. Using DuckDuckGo search as backend instead. If DuckDuckGo rate-limits, reduce SEARCH_TERMS per subreddit.
- **Twitter without xurl**: Gracefully skips Twitter if `xurl` not installed/authenticated. Score still works with Reddit + News alone.
- **Market hours**: Best run before market open (8 AM ET) on weekdays. Running on weekends produces low-signal results.
- **GNews API free tier**: 100 requests/day, 12-hour article delay. 14 queries × 5 results = 70 req/scan. Set `GNEWS_API_KEY` env var or pass `--apikey`. Sign up free at gnews.io/register — no credit card.
- **Free news sources that work**: GNews API (primary, free tier, 12h delay). CNBC RSS (`search.cnbc.com/rs/search/combinedcms/view.xml`) and MarketWatch RSS (`feeds.marketwatch.com/marketwatch/topstories`) as fallback. Yahoo Finance RSS returns empty.
- **Alpaca free tier limits**: Quotes API works fine (unlimited). Minute bars/options return 403 on free tier. Paper trading works for execution.

### Scoring & Data Quality
- **Ticker false positives**: The `FALSE_POSITIVES` set in `ticker_extractor.py` filters common words. Add new false positives there.
- **Sentiment lexicon**: Simple word-count based, not ML. Scores are directional, not precise.
- **Scan `sources` field is a string, not a list**: The scan JSON stores sources as `"{'reddit'}"` (string repr of a set). The newsletter iterates `s.get("sources", [])` which iterates characters. Fix: `ast.literal_eval(sources)` to convert back to a list before passing to newsletter. The latest `scoring_engine.py` converts sets to sorted lists on output, but old JSON files still have the string format.

### Spread Evaluator
- **Spread evaluator needs prices**: Strike suggestions require a current stock price. `spread_evaluator.py` standalone uses hardcoded AAPL/NVDA mocks — it does NOT read scan JSON. Real integration: (1) fetch prices from Alpaca, (2) build signal dicts manually, (3) call `evaluate_signals(signals, prices, iv_regimes)` directly.
- **Credit vs debit**: High IV → credit spreads (short ~30 delta, ~4% OTM). Low IV → debit spreads (long ~60 delta, short ~40 delta). Max loss check: if > 2% of account, tighten to 1.5% width.

### Google Docs Newsletter
- **Auth scopes**: Requires `documents` + `drive.file` scopes. If token was created before 2026-04-30 it likely has read-only scopes — revoke and re-auth via `setup.py --revoke`.
- **`borderBottom` broken in google-api-python-client 2.188.0**: Returns `UNIT_UNSPECIFIED` error. Use `borderBetween` with `padding` + `dashStyle` + `color` + `width` as workaround.
- **`borderBetween` requires `padding` sub-field**: The insert-table/cell call needs `padding` property on cells or the border won't render. See `references/google-docs-borderbottom-bug.md`.

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

**⛔ Golden Rule: Test the API endpoint, not the homepage.**
A 200 on `finnhub.io` means NOTHING. Hit `finnhub.io/api/v1/quote?symbol=AAPL` with a real API key before you trust it. Sherlock's API discovery scanner automates this — it hits each API's actual data endpoint and reports whether it returned real data, a 401, or an error. Never add a source that hasn't passed endpoint validation.

1. **Discovery first** — Run `~/.hermes/skills/agents/sherlock/scripts/api_discovery_scanner.py` to find new financial APIs, check their status via real endpoint tests, and get recommendations. Sherlock tracks 21+ known APIs with per-endpoint status.
2. Create `scripts/scanners/your_scanner.py`
3. Return list of dicts — can use either format:
   - **Legacy**: `{text, source, ...}` — `text` is the raw content for ticker extraction
   - **Structured** (like GNews): `{title, description, content, url, ...}` — the scoring engine auto-builds `text` from these fields
4. Import and call in `wolf_scan.py`
5. Add to scoring engine's `SOURCE_WEIGHTS`

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
