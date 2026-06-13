---
name: twitter-research-no-api
description: Search and research Twitter/X without the paid API — browser automation, free tier, and alternative data sources.
version: 1.1.0
author: Hermes
metadata:
  hermes:
    tags: [twitter, x, research, search, no-api, social-media]
    related_skills: [xitter, xurl, thing2, duckduckgo-search]
triggers:
  - "search twitter without api"
  - "twitter research no api"
  - "find tweets without paying"
  - "twitter search free"
  - "x.com search"
  - "scrape twitter"
  - "login to twitter from cli"
  - "fxtwitter"
  - "vxtwitter"
  - "extract tweet content"
---

# Twitter/X Research Without the Paid API

Search, read, and research Twitter/X content without paying for the X API ($5+/mo). Covers what works and what's a dead end as of mid-2026.

## TL;DR — Skip the Dead Ends

**These do NOT work anymore (2026):**
- `curl` + Google/Bing with `site:x.com` — JS challenge / CAPTCHA
- `curl` + DuckDuckGo with `site:` filter — rate-limited from VPS IPs
- Nitter instances — all behind Cloudflare JS challenges (SHA1 proof-of-work)
- SearXNG public instances — unreliable, most time out
- Raw HTTP scraping of twitter.com — requires JS rendering

**These DO work:**
1. **fxtwitter / vxtwitter API** — Free, no auth needed. `curl https://api.fxtwitter.com/user/status/ID` returns full tweet JSON including text, author, media, and article content. `api.vxtwitter.com` variant returns richer data including quote-tweets and article blocks. Prefer vxtwitter when you need article content or thread context.
3. X API free tier — $0/mo, 100 tweets/month read
4. Alternative data sources — StockTwits, Reddit, financial news for market-related tweets

## Approach 0: fxtwitter / vxtwitter API (First Try for Specific Tweets)

When you have a specific tweet URL or tweet ID, use these zero-auth read APIs **before** attempting browser automation. They return structured JSON in ~2 seconds with no credentials, no JS rendering, and no rate-limit issues from VPS IPs.

**fxtwitter** (`api.fxtwitter.com/<user>/status/<tweet_id>`): Best for full tweet content, author info, media URLs, and X Article content blocks.

**vxtwitter** (`api.vxtwitter.com/<user>/status/<tweet_id>`): Best for quote-tweet (QRT) discovery. When a tweet says "read the article below" but has no link, the QRT field often contains the referenced article.

**Important:** These are unofficial/community APIs — could break. Always have browser automation as fallback. Not for search queries; these fetch specific tweets by ID only. X Articles can be 50KB+ JSON — pipe through Python to extract only needed fields.

## Approach 1: Browser Automation (for Search and Discovery)

Use a headless browser to visit `https://x.com/search?q=...&f=live` or `https://twitter.com/search?q=...`.

**Prerequisites:**
- `hermes tools enable browser` (or ensure browser toolset is active)
- Chromium/Chrome installed on the system
- No login required for public tweet search

**Workflow:**
1. Navigate to `https://x.com/search?q=<url-encoded query>&f=live`
2. Wait for page load (JS rendering)
3. Extract tweet text, usernames, timestamps from rendered DOM
4. Scroll for more results if needed

**For authenticated access (DMs, private accounts, posting):**
- Log in via the browser: navigate to x.com/login, enter credentials
- Handle 2FA if enabled (may need user to supply the code)
- Store credentials in `~/.hermes/.env`: `TWITTER_EMAIL`, `TWITTER_USERNAME`, `TWITTER_PASSWORD`

## Approach 2: fxtwitter / vxtwitter Embed APIs

**These work for tweet + article extraction without browser or X API credentials (2026-05 verified):**

- `api.fxtwitter.com/<user>/status/<id>` — returns full tweet JSON including article content blocks (Draft.js-style), media URLs, quote-tweet data
- `api.vxtwitter.com/<user>/status/<id>` — returns tweet data + `article` field with title/preview/image for X Articles, and `qrt` (quote-retweet) data
- Both resolve t.co links, extract media URLs, and return structured JSON — no JS rendering needed, works from VPS IPs

**Commands:**
```bash
# Get tweet + article content (full blocks)
curl -sL "https://api.fxtwitter.com/DeRonin_/status/2054832499209974081" | python3 -c "
import json, sys
t = json.load(sys.stdin)['tweet']
# Check article content blocks
article = t.get('article', {})
for block in article.get('content', {}).get('blocks', []):
    print(block.get('text', ''))
"

# Get tweet + quote-tweet data (vxtwitter)
curl -sL "https://api.vxtwitter.com/RohOnChain/status/2052043443766194272" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(data.get('article', {}).get('title', ''))
print(data.get('qrt', {}).get('text', '')[:200])
"
```

**When to use fxtwitter vs vxtwitter:**
- **fxtwitter**: Better for X Articles — returns full `content.blocks` array with text, inline styles, and block types (header, blockquote, code-block, etc.). Use this when you need the complete article body.
- **vxtwitter**: Better for tweet metadata — returns `article` summary (title + preview only) plus `qrt` (quote-retweet) data with the quoted tweet's full text. Use for quick extraction and thread context.

## Approach 3: X API Free Tier

X offers a free tier with 100 tweets/month read access.

**Setup:**
1. Go to https://developer.x.com/
2. Sign up for free tier
3. Get API key + secret + bearer token
4. Store in `~/.hermes/.env`: `X_API_KEY`, `X_API_SECRET`, `X_BEARER_TOKEN`
5. Use existing `xurl` or `xitter` skills for interaction

**Commands:**
```bash
xurl search "energy stocks" --max 10    # search tweets
xurl user "username" --tweets 5         # get user timeline
```

## Approach 4: Alternative Data Sources

For financial/market tweets specifically:
- **StockTwits** — free, API-friendly, stock-specific chatter
- **Reddit** — r/wallstreetbets, r/options, r/stocks, r/energy
- **Financial news** — Bloomberg, Reuters, Yahoo Finance aggregate tweets

For general research:
- Google News search finds articles that embed/quote tweets
- Blog posts and newsletters that curate Twitter threads

## Pitfalls

1. **Do not attempt curl-based scraping of Twitter search results.** Google, Bing, DuckDuckGo, and Nitter all block headless requests from VPS IPs as of 2026. This approach burned 8+ tool calls confirming every path is dead. Go straight to browser automation or use the free API tier.

2. **Twitter login via browser may trigger suspicious login detection.** If the account is logged in from a VPS IP that doesn't match the user's normal location, X may require email/phone verification. Have a recovery path ready.

3. **The free X API tier is very limited (100 tweets/mo read).** It's fine for light research but not for building a monitoring agent. For ongoing monitoring, use browser automation or upgrade to Basic ($100/mo).

4. **Browser-based Twitter search is slower than API.** Expect 5-15 seconds per search due to JS rendering. Batch queries when possible.
