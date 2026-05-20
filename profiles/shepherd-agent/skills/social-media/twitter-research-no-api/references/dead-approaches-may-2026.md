# Dead Approaches: Evidence (May 2026)

This documents actual failure modes encountered when attempting curl-based
Twitter/X search from a VPS (Japan region). All approaches returned zero
usable tweet results.

## DuckDuckGo (`ddgs` CLI)

```bash
$ ddgs text -q "python programming" -m 3 -o json
# Exit 0, zero output. Rate-limited from this VPS IP.
$ ddgs text -q "site:x.com energy stocks" -m 8 -t w -o json
# Same — exit 0, empty output.
```

**Root cause:** DuckDuckGo rate-limits/throttles requests from known cloud/VPS
IP ranges. The CLI exits cleanly (code 0) but returns no results — a silent
failure that wastes tool calls.

## Google (curl)

```bash
$ curl -sL -H "User-Agent: Chrome/120..." \
  "https://www.google.com/search?q=site:x.com+energy+stocks"
```

**Result:** 91KB HTML page, but it's a JS challenge:
```html
<noscript>
  <meta content="0;url=/httpservice/retry/enablejs?sei=..." http-equiv="refresh">
</noscript>
```

The page redirects to `/httpservice/retry/enablejs`, requiring JavaScript
execution. Raw curl cannot proceed.

## Bing (curl)

```bash
$ curl -sL -H "User-Agent: Chrome/120..." \
  "https://www.bing.com/search?q=site:x.com+energy+stocks&count=5"
```

**Result:** 68KB HTML page, HTTP 200, proper `<title>`, but zero search result
blocks (`b_algo` class) in the raw HTML. Results are loaded dynamically via
JavaScript after page render.

**Key indicators:**
- Region: JP, Market: ja-JP (wrong locale for English search)
- 0 occurrences of `b_algo`, `tweet`, `timeline-item` in raw HTML
- All result containers injected by JS post-load

## Nitter Instances

```bash
$ curl -sL -H "User-Agent: Mozilla/5.0" \
  "https://nitter.poast.org/search?f=tweets&q=energy+stocks"
```

**Result:** 20KB HTML page. Instead of tweets, the body contains a SHA-1
proof-of-work JavaScript challenge (`JS_SHA1_NO_NODE_JS`). This is Cloudflare
bot protection. The page must compute a hash in-browser before it reveals
content.

Other Nitter instances (nitter.net, nitter.privacydev.net) timed out entirely.

## SearXNG Public Instances

Multiple public instances (`search.sapti.me`, `searx.be`, `search.bus-hit.me`)
either timed out (15s) or returned empty JSON—no search results.

## Bottom Line

As of May 2026, there is no curl-based path to Twitter/X search results from
a VPS. All major search engines and Twitter frontends require either:
1. JavaScript execution (browser), or
2. API authentication (X API bearer token)
