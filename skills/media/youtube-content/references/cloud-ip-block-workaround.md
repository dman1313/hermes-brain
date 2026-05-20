# YouTube Cloud IP Block — Escalation Ladder

When the primary `fetch_transcript.py` script fails with an IP-block error, work through these rungs in order. Each rung attempts to bypass YouTube's cloud-IP detection differently.

## Rung 1: Retry with `--language`

Sometimes specifying a language changes the request path enough to succeed:

```bash
python3 SKILL_DIR/scripts/fetch_transcript.py "VIDEO_ID" --language en
```

## Rung 2: Browser-based extraction (most promising)

If you have browser access (`browser_navigate`, `browser_console`):

1. Navigate to the video page:
   ```
   browser_navigate → https://www.youtube.com/watch?v=VIDEO_ID
   ```

2. Extract captions metadata from `ytInitialPlayerResponse`:
   ```js
   const pr = window.ytInitialPlayerResponse;
   const tracks = pr?.captions?.playerCaptionsTracklistRenderer?.captionTracks;
   // Returns array of {name, languageCode, baseUrl, kind}
   ```

3. Fetch transcript XML via XHR from within the page context (may bypass IP checks since the browser session is already authenticated):
   ```js
   const xhr = new XMLHttpRequest();
   xhr.open('GET', tracks[0].baseUrl + '&fmt=srv3', true);
   // Parse response: regex /<text\s+start="([\d.]+)"\s+dur="([\d.]+)"[^>]*>([\s\S]*?)<\/text>/g
   ```

4. **Common failure**: HTTP 200 with 0-byte body = YouTube still detected the cloud IP. Move to Rung 3.

## Rung 3: yt-dlp with `--write-auto-subs`

```bash
yt-dlp --write-auto-subs --sub-format srv3 --sub-lang en --skip-download \
  -o "/tmp/transcript_%(id)s" "https://www.youtube.com/watch?v=VIDEO_ID"
```

**Common failure**: "Sign in to confirm you're not a bot." This is terminal for cloud IPs without cookies. Move to Rung 4.

## Rung 4: Third-party transcript services

Try these in order (all are free, no auth required):

| Service | URL Pattern | Notes |
|---------|------------|-------|
| youtubetranscript.com | `https://youtubetranscript.com/?v=VIDEO_ID` | Increasingly blocked — may show "YouTube is blocking us" message |
| youtubetotranscript.com | `https://youtubetotranscript.com/?v=VIDEO_ID` | Alternative |
| tubetranscript.com | `https://tubetranscript.com/en?vid=VIDEO_ID` | Try if others fail |

All third-party services use cloud backends themselves, so they're subject to the same IP blocks. These are JS-rendered pages — `web_extract` and `curl` only get the HTML shell. Use ScrapingBee with `--render-js` and `--premium-proxy` (see Rung 4.5).

**Common failure (2026)**: even premium-proxy ScrapingBee renders the youtubetranscript.com page successfully, but the page's JS fetches subtitles from YouTube's own timedtext API — and YouTube blocks that second request. The page shows: *"YouTube is currently blocking us from fetching subtitles."* This means YouTube's block has expanded to cover residential proxies fetching timedtext data specifically.

## Rung 4.5: ScrapingBee premium proxy (last-ditch transcript attempt)

If you have ScrapingBee API access (skill: `scrapingbee-web-scraper`), use premium residential proxies to access the YouTube video page directly. This can retrieve the page HTML including `ytInitialPlayerResponse` with caption track metadata, even when all other routes are blocked:

```bash
# Fetch the YouTube video page via residential proxy (expensive: ~25+ credits)
~/.hermes/scripts/scrapingbee.sh --render-js --premium-proxy --wait 3000 \
  "https://www.youtube.com/watch?v=VIDEO_ID" > /tmp/yt_page.html

# Extract caption track URLs from the rendered page
grep -oP '"baseUrl":"https://www\.youtube\.com/api/timedtext[^"]*' /tmp/yt_page.html | head -3
```

**What this gets you:** video title, channel, caption track base URLs (even if the tracks themselves can't be fetched), and page metadata. The caption URLs contain `&fmt=srv3` — append this parameter and try fetching via ScrapingBee to retrieve the XML transcript.

**Pitfalls:**
- The rendered YouTube page is ~2.4MB — grep/sed on it can time out. Extract the caption URLs with the grep command above, not by loading the full file into Python.
- The timedtext API may STILL return HTTP 200 with an empty body (the classic cloud-IP block), even through ScrapingBee's residential proxy. YouTube appears to treat timedtext requests differently from page loads.
- If timedtext fails, move to Rung 5 — you at least have the title and channel.

## Rung 5: Page scraping + oembed fallback (no transcript, but context)

If all rungs fail, extract what you can:

**Reliable fallback — YouTube oembed API** (always works, lightweight, no IP blocks):
```bash
curl -s "https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=VIDEO_ID&format=json"
```
Returns: `title`, `author_name`, `author_url`, `thumbnail_url`, `provider_name`. Use this as the first metadata grab — it's fast and has never been observed blocked.

**Page scraping** (if you have browser access or ScrapingBee):
- **Title, creator, duration, publish date** — from the page snapshot
- **Description** — expand "…more" and snapshot
- **Top comments** — scroll and snapshot for community context
- **Topic inference** — from title + description + comments

Then offer the user: (a) the scraped context + video info, (b) search for articles/discussions about the video's topic, or (c) retry later when YouTube's blocks may have eased.

## Root Cause

YouTube categorically blocks requests from known cloud provider IP ranges (AWS, GCP, Azure, etc.). The block applies to:
- `youtube-transcript-api` Python package
- `yt-dlp` without browser cookies
- Direct timedtext API calls
- Browser-console `fetch()` and `XMLHttpRequest` from cloud-hosted browser instances (Browserbase, Firecrawl, etc.)
- Third-party transcript sites that themselves run on cloud infra

The only reliable workaround is running from a residential IP or using authenticated browser cookies from a real YouTube account (not recommended — risks account ban).
