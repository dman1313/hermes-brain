---
name: wolf-trading-agent
description: Wolf Trading Agent — daily scanner of Reddit, Twitter/X, and financial news for stock/options trade signals. Scores and ranks potential trades using multi-source fusion.
version: 1.3.0
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
## Scanners

### Reddit (⚠️ Broken as of 2026-05)

The DuckDuckGo-based Reddit scanner returns empty post content — titles are just "Link to reddit.com" and selftext is "The site owner hides the web page description." The scanner still returns results but they have no usable text for ticker extraction or sentiment analysis.

**Workaround**: Fetch each post URL with `.json` suffix (`curl <reddit_url>.json -H 'User-Agent: wolf/1.0'`) to get actual post content. Or switch to a different Reddit data source (PRAW, pushshift, etc.).

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

## Complementary: Quant Stock Scanner

Wolf finds what people are talking about. The quant scanner (`quant-stock-scanner` skill) scores fundamentals + technicals + options. Run both for a complete picture: Wolf for social discovery, quant scanner for hard numbers.

```bash
# Quick score check on a Wolf signal
python3 ~/.hermes/skills/trading/quant-stock-scanner/scripts/quant_scan.py TICKER --score-only

# Full quant report with options
python3 ~/.hermes/skills/trading/quant-stock-scanner/scripts/quant_scan.py TICKER --options
```

A ticker appearing in Wolf signals AND scoring >60 on the quant composite is the strongest setup.

## Files

```
scripts/
├── wolf_scan_gnews.sh        # Wrapper: exports GNEWS_API_KEY then runs scan
├── ticker_extractor.py       # Ticker extraction + sentiment
├── scoring_engine.py         # Signal fusion + scoring + digest formatting
├── spread_evaluator.py       # Vertical spread playbook applied to signals
├── wolf_newsletter.py        # Google Docs daily newsletter generator
├── alpaca_options_scan.py    # Options volume scan via Alpaca snapshots API (free tier)
└── scanners/
    ├── reddit_scanner.py     # Reddit via DuckDuckGo
    ├── twitter_scanner.py    # Twitter via xurl CLI (or skip)
    └── news_scanner.py       # News via GNews API (free tier, structured JSON)
references/
├── vertical-spread-playbook.md  # Dwayne's small-account spread rules
├── alpaca-options-chain.md      # Alpaca options API with real Greeks (free tier works)
├── per-contract-greeks.md       # Per-strike delta/IV/bid-ask extraction from Alpaca snapshots (for trade construction from aggregate scan results)
├── google-docs-borderbottom-bug.md  # borderBottom API bug → workaround
├── massive-api-notes.md  # Massive.com API notes (pending auth setup)
└── quant-nn-audit-2026-05-30.md  # Full audit of quant-nn LSTM pipeline (critical issues)
output/
└── api_discovery_*.md  # Daily Sherlock endpoint test reports
```
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

## Options Volume Scanner (In-Session)

When the user asks for "options plays" or "unusual volume", the working path order is:

### Step 1 — Alpaca Options Scan (works reliably)
Run the batch scanner across 61 known tickers (takes ~30s):
```bash
cd ~/.hermes/skills/trading/wolf-trading-agent/scripts
python3 alpaca_options_scan.py
```
Output: P/C ratio, total call/put volume, IV for calls and puts, and directional bias per ticker.

**Reading the scan:**
- **P/C ratio < 0.35** → extremely bullish call skew (e.g. MU 0.31, NFLX 0.29 today)
- **P/C ratio < 0.70** → bullish bias
- **P/C ratio 0.70-1.30** → neutral
- **P/C ratio > 1.30** → bearish
- **High IV (>30%)** favors credit spreads (premium selling)
- **Low IV (<25%)** favors debit spreads (directional)

### Step 2 — Get Real-Time Prices
yfinance is consistently rate-limited from this VPS. Use one of these instead:

**Option A — Alpaca stock snapshots** (fast, reliable):
```python
from alpaca.data.requests import StockSnapshotRequest
snap = stock_client.get_stock_snapshot(StockSnapshotRequest(symbol_or_symbols=["MU"]))
price = snap["MU"].latestTrade.p
volume = snap["MU"].dailyBar.volume
```

**Option B — Nasdaq API** (no auth, quick price + name lookup):
```python
import urllib.request, json
url = f'https://api.nasdaq.com/api/quote/{ticker}/info?assetclass=stocks'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
data = json.loads(urllib.request.urlopen(req).read())
price = data['data']['primaryData']['lastSalePrice']
```
Note: Nasdaq API does not return % change on the info endpoint.

### Step 3 — Pick Candidates & Suggest Spreads
- Top candidates get 2-4 spread suggestions each
- Apply the vertical spread playbook: credit spreads in high IV, debit in low IV
- Max loss check: if > 2% of account → tighten width to 1.5%

### Step 4 — Act (fallback when Alpaca fails)
If `alpaca_options_scan.py` fails or you need per-ticker deep-dive, use the pattern in `references/options-volume-scan.md`. The `--symbol` flag on `alpaca_options_scan.py` may time out (>60s) for per-ticker chain queries — use the Alpaca Python SDK directly instead (see `references/alpaca-options-chain.md` for the pattern).

## Pitfalls

### Data Sources
- **🔴 GNEWS API KEY HARDCODED IN SHELL SCRIPT**: `scripts/wolf_scan_gnews.sh` line 3 has `export GNEWS_API_KEY="ef9382a7b540143cbc64e9a0148b674f"` in plaintext. This key is visible to any process on the system. **ROTATE THIS KEY** and source from environment only. Found in security audit 2026-05-30.
- **Reddit API changes**: Reddit's JSON API now returns 403 for all unauthenticated requests. Using DuckDuckGo search as backend instead. If DuckDuckGo rate-limits, reduce SEARCH_TERMS per subreddit.
- **Reddit scanner returns empty post text**: As of 2026-05, DuckDuckGo search results for Reddit return `title: "Link to reddit.com"` and `selftext: "The site owner hides the web page description."` — no actual post content. The scanner still counts mentions from titles/URLs but sentiment analysis gets nothing. Fix: fetch the actual Reddit JSON for each post URL (`curl <url>.json`) to get real content, or switch to a different Reddit data source.
- **Twitter without xurl**: Gracefully skips Twitter if `xurl` not installed/authenticated. Score still works with Reddit + News alone.
- **Market hours**: Best run before market open (8 AM ET) on weekdays. Running on weekends produces low-signal results.
- **GNews API free tier**: 100 requests/day, 12-hour article delay. 14 queries × 5 results = 70 req/scan. Set `GNEWS_API_KEY` env var (already in `~/.hermes/.env`, confirmed 2026-05-29) or pass `--apikey`. Sign up free at gnews.io/register — no credit card.
- **Free news sources that work**: GNews API (primary, free tier, 12h delay). CNBC RSS (`search.cnbc.com/rs/search/combinedcms/view.xml`) and MarketWatch RSS (`feeds.marketwatch.com/marketwatch/topstories`) as fallback. Yahoo Finance RSS returns empty.
- **Alpaca options endpoint**: Use `OptionSnapshotRequest` (NOT `OptionLatestQuoteRequest`) for options data — returns Greeks, IV, bid/ask, and last trade for both calls AND puts on free tier. The data endpoint `https://data.alpaca.markets/v1beta1/options/snapshots/{ticker}` works on free tier. The paper-trading endpoint `https://paper-api.alpaca.markets/v1beta1/options/snapshots/{ticker}` returns 404. Always use the data URL. `OptionSnapshotRequest` has no `daily_bar` on free tier — no volume or OI. See alpaca-volume-scanner `references/options-data-patterns.md` for full data matrix.
- **Alpaca free tier limits**: Quotes API works fine (unlimited). `StockSnapshotRequest` returns stock prices + volume via `daily_bar`. **`StockBarsRequest` returns 403 for ALL timeframes** (including daily) — "subscription does not permit querying recent SIP data". Use snapshots instead. **Options chain with real Greeks + IV works** (confirmed 2026-06-02) — use `OptionSnapshotRequest` not `OptionLatestQuoteRequest`. Paper trading works for execution.
- **Financial site browser blocking**: Barchart, Yahoo Finance, Finviz, and Unusual Whales all block automated browser access (Cloudfront 403, Cloudflare challenges, rate limits). CBOE market statistics page works (`cboe.com/markets/us/options/market-statistics`). For per-ticker options data, use yfinance directly with sleep delays (see below).
- **yfinance rate limiting**: Yahoo Finance aggressively rate-limits. When scanning 80+ tickers, add `time.sleep(2)` between requests. At ~20 tickers with 2s delay, yfinance works reliably. Never use bash heredocs for scripts containing `&` — write to a .py file first (the `&` gets interpreted as backgrounding). Always wrap options chain pulls in try/except since some tickers return empty chains. **Cascading failure**: running wolf_scan + momentum-scanner + options scanner back-to-back exhausts yfinance. Switch to Alpaca options backend when you hit `YFRateLimitError`.
- **Alpaca `--symbol` flag on alpaca_options_scan.py may time out**: Per-ticker chain queries via the `--symbol` flag can hang for >60s. Don't rely on it for deep dives. Use the Alpaca Python SDK `OptionChainRequest` directly for per-ticker chain analysis (pattern in `references/alpaca-options-chain.md`).
- **Nasdaq API no % change**: The Nasdaq `info` endpoint returns `lastSalePrice` and company name but no `pctChange` field. Use it for quick display prices only, not for movement analysis.
- **Alpaca stock snapshots work for real-time prices**: `StockSnapshotRequest` + `.latestTrade.p` gives the current price. `.dailyBar.volume` gives daily volume. Both work on free tier. Use these instead of yfinance for price checks.

### Scoring & Data Quality
- **Ticker false positives**: The `FALSE_POSITIVES` set in `ticker_extractor.py` filters common words. Add new false positives there.
- **Sentiment lexicon**: Simple word-count based, not ML. Scores are directional, not precise.
- **Scan `sources` field is a string, not a list**: The scan JSON stores sources as `"{'reddit'}"` (string repr of a set). The newsletter iterates `s.get("sources", [])` which iterates characters. Fix: `ast.literal_eval(sources)` to convert back to a list before passing to newsletter. The latest `scoring_engine.py` converts sets to sorted lists on output, but old JSON files still have the string format.

### Spread Evaluator
- **Spread evaluator needs prices**: Strike suggestions require a current stock price. `spread_evaluator.py` standalone uses hardcoded AAPL/NVDA mocks — it does NOT read scan JSON. Real integration: (1) fetch prices from Alpaca, (2) build signal dicts manually, (3) call `evaluate_signals(signals, prices, iv_regimes)` directly.
- **Use Alpaca options chain for real Greeks**: Pull options via `OptionChainRequest(underlying_symbol, expiration_date_gte, expiration_date_lte, type)` — returns real delta/gamma/theta/vega and IV. Far better than estimating delta from BSM. Load credentials from `~/alpaca-bot/.env` via dotenv. See `references/alpaca-options-chain.md`.
- **Credit vs debit**: High IV → credit spreads (short ~30 delta, ~4% OTM). Low IV → debit spreads (long ~60 delta, short ~40 delta). Max loss check: if > 2% of account, tighten to 1.5% width.

### Google Docs Newsletter
- **Auth scopes**: Requires `documents` + `drive.file` scopes. If token was created before 2026-04-30 it likely has read-only scopes — revoke and re-auth via `setup.py --revoke`.
- **`borderBottom` broken in google-api-python-client 2.188.0**: Returns `UNIT_UNSPECIFIED` error. Use `borderBetween` with `padding` + `dashStyle` + `color` + `width` as workaround.
- **`borderBetween` requires `padding` sub-field**: The insert-table/cell call needs `padding` property on cells or the border won't render. See `references/google-docs-borderbottom-bug.md`.

## News-Driven Momentum Scanner (Complementary)

Wolf finds what people are talking about. The momentum scanner finds what's actually moving on news catalysts. Script at `~/.hermes/scripts/momentum-scanner.py`. Full reference: `references/news-momentum-detection.md`.

**Quick start:**
```bash
python3 ~/.hermes/scripts/momentum-scanner.py --sectors quantum,ai --alert
```

**When to use alongside Wolf:** Pre-market, run both. Wolf for social discovery, momentum for catalyst confirmation. A ticker appearing in both Wolf signals AND momentum alerts is the strongest signal.

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
