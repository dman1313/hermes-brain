---
name: twitter-x
description: "X/Twitter integration — official API via xurl CLI and no-API research via browser automation + fxtwitter. Covers posting, searching, reading, media, DMs, and free-tier research."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [twitter, x, social-media, xurl, research, search, no-api]
    related_skills: [thing2, xitter]
---

# X/Twitter — Official API + No-API Research

Two approaches for interacting with X/Twitter: the **official API** (via xurl CLI, requires credentials + credits) and **no-API research** (browser automation + free community APIs, no credentials needed for reading).

**Decision tree:**
1. Need to post/reply/like/DM → use **xurl** (requires API credits)
2. Need to search/read specific tweets → try **fxtwitter/vxtwitter** first (free, instant)
3. Need to search/discover tweets → use **browser automation** (free, slower)
4. Need ongoing monitoring → use **xurl** or browser automation

---

## No-API Research (Free, No Credentials)

Search, read, and research Twitter/X content without paying for the X API.

### Approach 1: fxtwitter / vxtwitter APIs (First Try for Specific Tweets)

When you have a specific tweet URL or ID, use these zero-auth read APIs **before** attempting browser automation. They return structured JSON in ~2 seconds with no credentials.

**fxtwitter** (`api.fxtwitter.com/<user>/status/<tweet_id>`): Best for full tweet content, author info, media URLs, and X Article content blocks.

**vxtwitter** (`api.vxtwitter.com/<user>/status/<tweet_id>`): Best for quote-tweet (QRT) discovery and tweet metadata.

```bash
# Get tweet + article content (full blocks)
curl -sL "https://api.fxtwitter.com/DeRonin_/status/2054832499209974081" | python3 -c "
import json, sys
t = json.load(sys.stdin)['tweet']
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
- **fxtwitter**: Better for X Articles — returns full `content.blocks` array
- **vxtwitter**: Better for tweet metadata — returns `article` summary + `qrt` (quote-retweet) data

**Important:** These are unofficial/community APIs — could break. Always have browser automation as fallback. Not for search queries; these fetch specific tweets by ID only.

### Approach 2: Browser Automation (for Search and Discovery)

Use a headless browser to visit `https://x.com/search?q=...&f=live`.

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
- Handle 2FA if enabled
- Store credentials in `~/.hermes/.env`: `TWITTER_EMAIL`, `TWITTER_USERNAME`, `TWITTER_PASSWORD`

### Approach 3: Alternative Data Sources

For financial/market tweets:
- **StockTwits** — free, API-friendly, stock-specific chatter
- **Reddit** — r/wallstreetbets, r/options, r/stocks
- **Financial news** — Bloomberg, Reuters, Yahoo Finance aggregate tweets

For general research:
- Google News search finds articles that embed/quote tweets
- Blog posts and newsletters that curate Twitter threads

### No-API Pitfalls

1. **Do not attempt curl-based scraping of Twitter search results.** Google, Bing, DuckDuckGo, and Nitter all block headless requests from VPS IPs as of 2026. Go straight to browser automation or fxtwitter.
2. **Twitter login via browser may trigger suspicious login detection.** Have a recovery path ready.
3. **Browser-based Twitter search is slower than API.** Expect 5-15 seconds per search due to JS rendering.

---

## Official API via xurl (Paid, Full Functionality)

`xurl` is the X developer platform's official CLI for the X API. Supports shortcut commands for common actions AND raw curl-style access to any v2 endpoint. All commands return JSON to stdout.

### Secret Safety (MANDATORY)

- **Never** read, print, parse, summarize, upload, or send `~/.xurl` to LLM context.
- **Never** ask the user to paste credentials/tokens into chat.
- **Never** use `--verbose` / `-v` in agent sessions — it can expose auth headers/tokens.
- To verify credentials exist, only use: `xurl auth status`.

### Installation

```bash
# Shell script (installs to ~/.local/bin, no sudo)
curl -fsSL https://raw.githubusercontent.com/xdevplatform/xurl/main/install.sh | bash

# Homebrew (macOS)
brew install --cask xdevplatform/tap/xurl

# npm
npm install -g @xdevplatform/xurl

# Go
go install github.com/xdevplatform/xurl@latest
```

### One-Time User Setup (user runs these outside the agent)

These steps must be performed by the user directly, NOT by the agent, because they involve pasting secrets:

1. Create or open an app at https://developer.x.com/en/portal/dashboard
2. Set the redirect URI to `http://localhost:8080/callback`
3. Copy the app's Client ID and Client Secret
4. Register: `xurl auth apps add my-app --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET`
5. Authenticate: `xurl auth oauth2 --app my-app` (opens browser for OAuth 2.0 PKCE flow)
6. Set default: `xurl auth default my-app`
7. Verify: `xurl auth status && xurl whoami`

> **Common pitfall:** If you omit `--app my-app` from `xurl auth oauth2`, the OAuth token is saved to the built-in `default` app profile (no client-id/secret). Commands will fail with auth errors.

### ⚠️ API Credits Required

The X API uses a **pay-per-use** pricing model. All endpoints will fail with `CreditsDepleted` if your developer account has a $0 balance. Minimum top-up: **$5**.

### Quick Reference

| Action | Command |
|--------|---------|
| Post | `xurl post "Hello world!"` |
| Reply | `xurl reply POST_ID "Nice post!"` |
| Quote | `xurl quote POST_ID "My take"` |
| Delete | `xurl delete POST_ID` |
| Read | `xurl read POST_ID` |
| Search | `xurl search "QUERY" -n 10` |
| Who am I | `xurl whoami` |
| User lookup | `xurl user @handle` |
| Timeline | `xurl timeline -n 20` |
| Mentions | `xurl mentions -n 10` |
| Like / Unlike | `xurl like POST_ID` / `xurl unlike POST_ID` |
| Repost / Undo | `xurl repost POST_ID` / `xurl unrepost POST_ID` |
| Follow / Unfollow | `xurl follow @handle` / `xurl unfollow @handle` |
| Send DM | `xurl dm @handle "message"` |
| Upload media | `xurl media upload path/to/file.mp4` |
| Auth status | `xurl auth status` |

Notes:
- `POST_ID` accepts full URLs too — xurl extracts the ID.
- Usernames work with or without a leading `@`.

### Raw API Access

For anything the shortcuts don't cover:
```bash
# GET
xurl /2/users/me

# POST with JSON body
xurl -X POST /2/tweets -d '{"text":"Hello world!"}'

# Full URLs also work
xurl https://api.x.com/2/users/me
```

### Common Workflows

**Post with an image:**
```bash
xurl media upload photo.jpg
xurl post "Check out this photo!" --media-id MEDIA_ID
```

**Search and engage:**
```bash
xurl search "topic of interest" -n 10
xurl like POST_ID_FROM_RESULTS
xurl reply POST_ID_FROM_RESULTS "Great point!"
```

### Alternative Auth Methods

**OAuth 1.0a (User Context):**
```bash
xurl auth oauth1 \
  --consumer-key YOUR_CONSUMER_KEY \
  --consumer-secret YOUR_CONSUMER_SECRET \
  --access-token YOUR_ACCESS_TOKEN \
  --token-secret YOUR_TOKEN_SECRET
```

**App-Only Bearer Token** (search and public data only):
```bash
xurl auth app --bearer-token YOUR_BEARER_TOKEN
```

### xurl `user` subcommand lacks `-n`/`--max-results` flag

The `xurl user <username>` subcommand does NOT accept `-n` to limit results (unlike `xurl search`, which does). Calling `xurl user handle -n 5` returns a usage error, not tweet data. **Fix:** drop the `-n` flag and truncate at the application level (`tweets[:max_results]`).

### Agent Workflow

1. Verify prerequisites: `xurl --help` and `xurl auth status`
2. **Check default app has credentials.** Parse the `auth status` output. The default app is marked with `▸`. If it shows `oauth2: (none)` but another app has a valid oauth2 user, tell the user to run `xurl auth default <that-app>`.
3. If auth is missing entirely, stop and direct the user to the "One-Time User Setup" section.
4. Start with a cheap read (`xurl whoami`, `xurl search ... -n 3`) to confirm reachability.
5. Confirm the target post/user and the user's intent before any write action.
6. Never paste `~/.xurl` contents back into the conversation.

### Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Auth errors after successful OAuth | Token saved to `default` app instead of named app | `xurl auth oauth2 --app my-app` then `xurl auth default my-app` |
| `unauthorized_client` during OAuth | App type set to "Native App" in X dashboard | Change to "Web app, automated app or bot" |
| `CreditsDepleted` | $0 balance on X API | Buy credits (min $5) in Developer Console → Billing |
| 401 on every request | Token expired or wrong default app | Check `xurl auth status` |
| `UsernameNotFound` after OAuth | X not returning username reliably | Re-run `xurl auth oauth2 --app my-app YOUR_USERNAME` |
| `xurl user` returns usage error | `-n` flag used on `user` subcommand (not supported) | Drop `-n`. Truncate results at app level: `tweets[:max_results]` |
