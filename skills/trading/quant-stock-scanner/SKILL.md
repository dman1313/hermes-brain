---
name: quant-stock-scanner
description: "Quantitative stock scanner — technicals, fundamentals, options chain, and composite scoring. Produces a single 0-100 quant score across 5 factors: momentum, value, quality, growth, technicals."
version: 1.1.0
author: Hermes Agent
license: MIT
tags: [trading, quant, technicals, fundamentals, options, scoring, stock-scanner]
related_skills: [wolf-trading-agent, de-bono-stock-analysis, alpaca-volume-scanner, quantitative-trading-tools]
---

# 📊 Quant Stock Scanner

Quantitative stock analysis: technicals, fundamentals, options chain, and composite scoring. Produces a single 0-100 quant score to drive trade decisions.

Complements wolf-trading-agent (social/news sentiment) with hard numbers.

## Quick Start

```bash
# Full quant scan on a ticker (uses yfinance — may hit rate limits)
python3 ~/.hermes/skills/trading/quant-stock-scanner/scripts/quant_scan.py AAPL

# Just the composite score
python3 ~/.hermes/skills/trading/quant-stock-scanner/scripts/quant_scan.py AAPL --score-only

# With options chain analysis
python3 ~/.hermes/skills/trading/quant-stock-scanner/scripts/quant_scan.py AAPL --options
```

**⚠️ quant_scan.py uses yfinance for everything — which frequently hits YFRateLimitError.** For reliable quant scans, follow the manual data pipeline below (EVERY data source in this pipeline works independently when yfinance is blocked). For the full fallback strategy, see `references/yahoo-chart-api.md` and `references/nasdaq-api-fallback.md`.

## Workflow (Manual / In-Conversation)

For **single-ticker analysis**, follow the steps below. For **multi-ticker scans** across the full options universe (60+ tickers, diverse spread setups), see `references/enhanced-multi-ticker-scan.md`.

When a user asks for a "quant scan" on a ticker:

1. **Pull historical OHLCV** — FIRST try the Yahoo Finance chart API (`query1.finance.yahoo.com/v8/finance/chart/{TICKER}?range=6mo&interval=1d`) with a proper User-Agent header. This endpoint does NOT need a crumb/cookie and works when yfinance is rate-limited. See `references/yahoo-chart-api.md` for the full pipeline. **If that also 429s**, wait 60s and retry. **If yfinance works** (no rate limit), use it.
2. **Pull fundamentals** via Nasdaq API summary endpoint (`api.nasdaq.com/api/quote/{TICKER}/summary?assetclass=stocks`) — returns P/E, EPS, Market Cap, 52W range, Sector/Industry, Previous Close. No auth needed. See `references/nasdaq-api-fallback.md`. For deeper fundamentals (margins, ROE, debt), try yfinance `t.info` if available.
3. **Get real-time price** via Alpaca (`StockLatestTradeRequest` from `~/alpaca-bot/.env`). The env file uses `ALPACA_API_KEY` and `ALPACA_SECRET_KEY` (NOT `APCA_API_KEY_ID`). Alpaca SDK is in Python 3.12 (`/usr/bin/python3`), NOT in the Hermes venv (3.11). If Alpaca auth fails, use the Nasdaq summary endpoint's "Previous Close".
4. **Calculate technicals**: SMA(20/50/200), EMA(12/26), RSI(14), MACD(12,26,9), Bollinger(20,2), ATR(14), volume ratios, price changes (1D/5D/20D/60D), 52W range positioning. All can be computed from raw OHLCV arrays (see `references/yahoo-chart-api.md` for formulas) — no pandas or yfinance needed.
5. **Extract fundamentals**: P/E (trailing + forward), P/S, P/B, EV/EBITDA, revenue growth, margins (gross/op/profit), ROE, debt/equity, current ratio, FCF, cash position
4. **Scrape news** from MarketWatch, Yahoo Finance, or TipRanks (use bulk_get or fetch)
5. **Pull options chain** via Alpaca `OptionChainRequest` for nearest 3 expirations if requested — filter near-ATM (±30% of price). Returns real Greeks (delta/gamma/theta/vega) and IV. See `references/alpaca-data-setup.md`.
6. **Score** using the 5-factor composite model (see below)
7. **Present** as a structured report with clear bull/bear signals

## Composite Scoring Model (5 Factors)

Each factor scores 0-100. Composite = weighted average.

### Momentum (25% weight)
- Base: 50
- +min(1D_pct × 2, 20) — today's move
- +min(5D_pct, 15) — weekly trend
- +min(20D_pct × 0.5, 10) — monthly trend
- +5 if RSI 50-70 (ideal zone), -10 if >70, +10 if <30
- +5 if MACD histogram positive
- +10 if volume ratio >1.5x, +5 if >1.2x

### Value (20% weight)
- Base: 50
- Forward P/E: <15 → +20, <25 → +10, <35 → 0, <50 → -10, else -20
- P/S: <5 → +15, <10 → +5, <20 → -5, else -10
- PEG: <1 → +15, <1.5 → +10, <2 → 0, else -10
- EV/EBITDA: <15 → +10, <25 → 0, else -10
- +min(analyst_upside × 50, 15)

### Quality (20% weight)
- Base: 50
- +min(gross_margin × 40, 20) — software-like margins rewarded
- Operating margin: >30% → +15, >15% → +10, >0 → +5, else -10
- Profit margin: >20% → +10, >10% → +5, >0 → 0, else -10
- ROE: >20% → +10, >10% → +5
- Current ratio: >2 → +5, >1 → 0, else -10
- D/E: <0.5 → +5, <1 → 0, <2 → -5, else -10

### Growth (20% weight)
- Base: 50
- Revenue growth: >30% → +25, >20% → +15, >10% → +10, >5% → +5, else -10
- +min(analyst_upside × 40, 15)
- +5 if 20D price change positive

### Technicals (15% weight)
- Base: 50
- +5 if above SMA20, +5 if above SMA50
- Bollinger position: 30-70% → +10, >90% → -10, <10% → +5
- RSI: 40-65 → +10, >75 → -10
- +10 if MACD histogram positive
- +5 if volume ratio >1.2x
- 52W high proximity: >-10% → +10, >-20% → +5, >-40% → 0, else -10

### Verdict Thresholds
- ≥75: **STRONG BUY** 🟢
- ≥60: **BUY** 🟢
- ≥45: **HOLD** 🟡
- ≥30: **WEAK** 🔴
- <30: **AVOID** 🔴

## Options Analysis

When options are requested, pull the chain for the nearest 3 expirations and propose 2-4 trades:

1. **Bull call spread** (debit) — for momentum plays. Buy ATM call, sell OTM call. Capped risk.
2. **Bull put credit spread** — sell fear in high-IV environments. Sell ATM/OTM put, buy lower put.
3. **Weekly lotto call** — small-size directional bet on catalysts. Size for 100% loss.
4. **Put credit spread (weekly)** — premium selling on momentum days.

Apply the vertical spread playbook from wolf-trading-agent when evaluating:
- High IV → credit spreads favored
- Low IV → debit spreads favored
- Max loss check: >2% of account → tighten to 1.5% width

**For actual spread construction with real bid/ask data**, see `references/options-spread-construction.md`. Covers REST API parsing, OCC symbol decoding, spread math, and presentation format.

### Relative Strength Screening

When the user wants "quant action" or trade ideas across multiple names:

1. Get stock snapshots for 50+ tickers via Alpaca REST API
2. Sort by % change
3. Identify names that are **GREEN while sector is RED** — these are the best spread candidates
4. Run options chain analysis on top 3-5 relative strength names
5. Present 2-4 spread setups with real bid/ask, RoR, breakeven

**Why relative strength works**: Stocks that hold up during sector-wide selling have institutional buyers. The spread gives defined-risk exposure to that thesis.

## Earnings Proximity Assessment

When a stock is close to its earnings date, include an earnings risk/reward section in the quant scan. The key metric is **price vs consensus analyst target** — this reveals whether the stock has already priced in good news.

### Framework

| Factor | What to Check | Signal |
|--------|---------------|--------|
| Price vs target | Gap above/below median 1Y target | 🔴 >10% above = priced for perfection |
| Options flow | Put/Call ratio from options scan | 🟢 <0.7 = bullish positioning |
| IV crush risk | Earnings-week IV vs normal | 🔴 High IV = premium gets crushed post-ER |
| Recent run-up | 1mo / 3mo % gain | 🔴 3mo >30% = expectations elevated |
| Sector headwinds | Memory cycle position, peer earnings | 🟡 Correlates with macro read |

### Key Numbers
- **Stock trading above consensus target = asymmetric downside risk.** The burden of proof is on the company to deliver a beat big enough to drag the whole analyst community higher.
- **Stock with 10-15%+ gap below target = asymmetric upside.** The bar is already low.
- **P/C ratio < 0.5 on a stock near ATH** = high call skew but also high risk — long calls are betting on a beat that's already priced in.

### Decision Heuristics

| Scenario | Verdict |
|----------|---------|
| Stock at ATH, above target, P/C bullish | ⚠️ **De-risk.** Sell half or hedge with puts. Market already expects perfection. |
| Stock well below target, P/C neutral/bearish | 📈 **Hold or add.** Expectations are low, beat-and-raise is easier. |
| Stock near target, P/C bullish | 🟡 **Mixed.** Hold but size conservatively. Use spreads to cap risk. |
| Stock above target, P/C bearish | 🔴 **Sell or hedge.** Smart money is protecting downside. |

### Presentation Format

Structure the report in this order:
1. Company overview (1 line)
2. Price & momentum snapshot
3. Last 5 days table
4. Technicals (RSI, MACD, BB, SMA positioning)
5. Fundamentals (margins, valuation, balance sheet)
6. Analyst consensus
7. Short interest
8. News catalysts (if scraped)
9. Bull/bear signal summary
10. Composite quant score (if computed)

Keep it data-dense. No fluff. Dwayne prefers bullet points over paragraphs.

### Trade Recommendation Format (Critical)

When the user asks for "exactly which option," "tell me what to do," or wants a specific trade to execute:

- **Give ONE trade**, not a menu. Pick the best risk/reward and commit.
- **Exact execution steps**: spell out which leg to sell, which to buy, the order type (vertical spread), and the expected credit/debit.
- **Defined risk first**: lead with max loss, then max profit, then RoR. Dwayne wants to know what he can lose before what he can make.
- **Breakeven as % from current**: e.g. "AMD can drop 2.9% and you still win" — more useful than raw dollar breakeven.
- **Broker terminology varies**: note both "Sell Put Spread" and "Bear Put Spread" / "Bull Put Credit Spread" so the user finds it in their broker UI.
- Do NOT present 4-5 setups and ask which one. Pick one. If the user wants alternatives, they'll ask.

## Pitfalls

### yfinance / Python
- **quant_scan.py crashes on YFRateLimitError** with no fallback — it calls `t.info` which raises an unhandled exception. When this happens, use the Nasdaq API or Alpaca fallback pattern manually (see `references/nasdaq-api-fallback.md`).
- **yfinance is UNRELIABLE for real-time prices** — returns stale/cached data during rate limits (which happen frequently). User confirmed "price data is way off" (2026-05-29). **Use Alpaca for real-time prices** (`StockLatestTradeRequest`), keep yfinance for fundamentals only.
- **yfinance options chain hits rate limits** — `t.options` and `t.option_chain()` throw `YFRateLimitError` frequently. Use Alpaca's `OptionChainRequest` instead — returns real Greeks and IV on free tier. See `references/alpaca-data-setup.md` or wolf-trading-agent `references/alpaca-options-chain.md`.
- **For quick ticker identification** — use Nasdaq API (`api.nasdaq.com/api/quote/TICKER/info?assetclass=stocks`), no auth needed. Returns company name, exchange, real-time price, 52W range. Faster than yfinance for lookups.
- **execute_code cannot use `terminal`** — it's not available in that sandbox. Use `terminal()` tool directly for yfinance scripts, or write a .py file and run it.
- **Bitwise `&` on pandas in shell heredocs** — the `&` gets interpreted as backgrounding. Write to a .py file first, then execute.
- **String multiplication with floats** — `"#" * (v // 5)` fails if v is a float. Cast to int first: `"#" * int(v // 5)`.
- **yfinance returns empty on some tickers** — always check `hist.empty` before processing.

### News Scraping
- Yahoo Finance news page returns 429 (rate limited) frequently. Use `marketwatch.com/investing/stock/TICKER` as primary news source.
- StockTwits returns 403 (blocked). Don't bother.
- Seeking Alpha requires JS rendering — use scrapling browser tools, not bulk_get.
- TipRanks and GuruFocus are reliable via bulk_get for recent headlines.

### Options Data
- yfinance options chain may be empty for small-cap tickers.
- IV on weeklies can be 200-300%+ — always note this is a volatility premium, not a directional signal.
- Check bid-ask spread — if spread > 30% of midprice, the option is illiquid. Warn the user.
- **Alpaca REST API: `details.expiration_date` is EMPTY** — must parse OCC symbol for expiry, type, and strike. See `references/options-spread-construction.md` for the correct parsing code.
- **Alpaca indicative feed returns only ~500 contracts per page** — for liquid tickers (AMD, NVDA, SPY), this only covers 1-2 expirations. You MUST paginate with `next_page_token` from the response to get all available expirations. Loop up to 5 pages: `params={'feed': 'indicative', 'limit': 500, 'page_token': page_token}`. Without pagination, you'll miss later expirations (e.g. July/Aug when June dominates liquidity).
- **Earnings-week options may not be listed yet** — the options chain typically only extends 6-8 weeks out. If a user asks for plays around an earnings date that's 8+ weeks away, the chain won't have those expirations. Tell the user directly and offer to scan again when they list (usually 2-4 weeks before earnings). Don't force a suboptimal setup just because the data is available.

### Python Environment Split
- **Hermes venv is Python 3.11** (`~/.hermes/hermes-agent/venv/bin/python3`). `alpaca-py` is installed in **Python 3.12** (`~/.local/lib/python3.12/site-packages/`). The venv python3 cannot `import alpaca`.
- **For Alpaca API calls**: use `/usr/bin/python3` (which resolves to 3.12), NOT the hermes venv python3.
- **For last30days sentiment**: requires `python3.12` explicitly — script checks version and exits on 3.11.
- **Alpaca credentials**: load from `~/alpaca-bot/.env` via `dotenv` or `source`. The env file uses `ALPACA_API_KEY` and `ALPACA_SECRET_KEY` (NOT `APCA_API_KEY_ID`). The Alpaca REST API accepts these via headers `APCA-API-KEY-ID` and `APCA-API-SECRET-KEY` — you need the values from the .env file regardless of the header name difference. Do NOT use `~/.hermes/.env` — it does not contain Alpaca keys.
- **yfinance rate limits**: quant_scan.py hits `YFRateLimitError` after 2-3 consecutive calls. When scanning multiple tickers, either batch with delays or use Alpaca for prices and skip yfinance fundamentals for the extras.

### Scoring Model
- The model is calibrated for US-listed equities. REITs, MLPs, and financial companies with unusual capital structures may score oddly on the quality factor.
- A stock can score BUY on momentum while scoring AVOID on value — present both, let the user decide which factor matters more for their timeframe.
- The scoring model doesn't account for sector rotation, macro regime, or correlation. It's a single-stock factor model.
- **MSTR/Strategy (and all Bitcoin-proxy stocks)** break the scoring model entirely — they trade on Bitcoin NAV premium/discount, not on software fundamentals. P/E is meaningless (negative earnings), quality/growth factors are noise. For MSTR: report the raw technicals (RSI, BB, SMA positioning, 52W range proximity) + Bitcoin correlation. Verdict should be "Speculative BTC proxy — use BTC price action as lead indicator." Do NOT try to force a composite score.
- **Penny stocks and sub-$5 tickers** may have unreliable OHLCV from the chart API (gaps, stale data). Always verify `closes[-1]` is non-None and reasonable before computing.

## Files

```
scripts/
  quant_scan.py    # Full quant scan: technicals + fundamentals + composite score
references/
  scoring-model.md              # Detailed scoring rubric with edge cases
  alpaca-data-setup.md          # Alpaca real-time prices + options chain setup
  nasdaq-api-fallback.md        # Nasdaq public API as yfinance fallback (price + P/E + EPS + 52W range, no auth)
  options-spread-construction.md # Vertical spread construction with real bid/ask, REST API patterns, OCC parsing, presentation format
  earnings-proximity-risk.md    # Earnings risk assessment: price vs target gap, P/C ratio, IV crush, decision heuristics
  yahoo-chart-api.md            # Yahoo Finance chart API as yfinance bypass for historical OHLCV (no crumb needed)
  enhanced-multi-ticker-scan.md # Multi-ticker scan workflow across 60+ tickers
```

## Verification

```bash
# Test with a known ticker
python3 ~/.hermes/skills/trading/quant-stock-scanner/scripts/quant_scan.py NVDA --score-only

# Test options chain pull
python3 ~/.hermes/skills/trading/quant-stock-scanner/scripts/quant_scan.py AAPL --options
```
