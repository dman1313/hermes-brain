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
| youtubetranscript.com | `https://youtubetranscript.com/?v=VIDEO_ID` | Reliable when not blocked |
| youtubetotranscript.com | `https://youtubetotranscript.com/?v=VIDEO_ID` | Alternative |
| tubetranscript.com | `https://tubetranscript.com/en?vid=VIDEO_ID` | Try if others fail |

All third-party services use cloud backends themselves, so they're subject to the same IP blocks. If one works, it means their IP pool hasn't been rate-limited yet.

## Rung 5: Page scraping (no transcript, but context)

If all rungs fail, extract what you can from the video page itself:

- **Title, creator, duration, publish date** — from the page snapshot
- **Description** — click "…more" in the browser to expand, then snapshot
- **Top comments** — scroll down and snapshot for community context
- **Topic inference** — from title + description + comments

Then offer the user: (a) the scraped context, (b) news search for the topic, or (c) retry later.

## Root Cause

YouTube categorically blocks requests from known cloud provider IP ranges (AWS, GCP, Azure, etc.). The block applies to:
- `youtube-transcript-api` Python package
- `yt-dlp` without browser cookies
- Direct timedtext API calls
- Browser-console `fetch()` and `XMLHttpRequest` from cloud-hosted browser instances (Browserbase, Firecrawl, etc.)
- Third-party transcript sites that themselves run on cloud infra

The only reliable workaround is running from a residential IP or using authenticated browser cookies from a real YouTube account (not recommended — risks account ban).
