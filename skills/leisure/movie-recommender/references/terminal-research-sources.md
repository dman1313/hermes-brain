# Terminal-Accessible Movie Research Sources

Tested June 2026 from VPS/datacenter IP. Sources that returned usable content via `curl`.

## Reliable Content Sites

### micropsiacine.com
- **Access:** Full content loads via `curl`. WordPress-based, server-rendered HTML.
- **Page size:** ~64KB for full reviews.
- **Content:** Full review text, director, cast, genre, platform info, release date. JSON-LD structured data in head.
- **Extraction:** `sed 's/<[^>]*>//g'` tag stripping works perfectly. Filter by line length >40 chars.
- **Language:** Spanish (film titles and names are still English/Spanish readable).
- **Sample URL:** `https://www.micropsiacine.com/2026/06/mexico-86-review-diego-luna-tackles-football-corruption-with-wit-and-affection-in-this-netflix-comedy/`

### blog.cineswipe.app
- **Access:** Full content loads via `curl`. NextJS-based but server-rendered, ~131KB.
- **Content:** Structured film lists with "Hype" scores (1-100), genre tags, cast names, one-paragraph descriptions, streaming platform.
- **Extraction:** Tag stripping works. JSON-LD contains article metadata (title, description, date, section).
- **Sample URL:** `https://blog.cineswipe.app/blog/what-to-watch-on-netflix-june-2026`

### decider.com (partial — JSON-LD extraction)
- **Access:** Page body is JS-rendered but JSON-LD structured data in `<head>` is server-rendered.
- **Content:** The `@type: NewsArticle` JSON-LD block contains full tag lists with all film titles, cast members, genres, and platform slugs.
- **Extraction:** Parse the JSON-LD block to get the complete film list even when article text is hidden. Look for `"keywords"` array in the schema.org data.
- **Limitation:** No review text or scores without JS. Use for film discovery and cross-reference with other sources.

## Unreliable / Blocked Sites

### JS-rendered (content hidden from curl)
- **boston.com** — Returns JS boilerplate only (~237KB of New Relic scripts)
- **yahoo.com** — Returns 23 bytes (redirect/block)
- **buzzfeed.com** — Returns 0 bytes
- **aol.com** — Returns 23 bytes (redirect/block)
- **thewrap.com** — Downloads 253KB but content is JS-rendered, extraction yields nothing

### Cloudflare / 429 blocked
- **fictionhorizon.com** — Cloudflare challenge page
- **beebulletin.com** — WordPress.com 429 error
- **rogerebert.com** — 1.6KB Cloudflare page
- **metacritic.com** — 5.5KB Cloudflare/captcha page

### AI-slop sites (content looks real but is fabricated)
- **nishadil.com** — Published June 2026 article listing 6 films with completely fabricated titles and generic AI-written descriptions. Contains editorial note admitting AI assistance. All 6 film titles do not appear in any other source.

## Wikipedia API Notes

- **API endpoint:** `https://en.wikipedia.org/w/api.php?action=parse&page=PAGE_NAME&prop=text&section=N&format=json`
- **Rate limit:** Space requests 2+ seconds apart. Rapid calls return 228-byte error pages.
- **Very new films:** Films released in the current or previous month often have no page. The API may return a different film with the same title (e.g., "Mexico 86" returned a 2024 Belgian documentary).
- **Useful pages:** `List_of_American_films_of_2026` (release tables), `2026_in_film` (box office rankings)

## DDG Lite Usage

- **POST required:** `curl -s -A "Mozilla/5.0" -d "q=query&df=m" "https://lite.duckduckgo.com/lite/"`
- **Rate limit:** 3-4 queries before captcha. Check with `grep -c 'result-link'`.
- **Date filter:** `df=m` (month), `df=w` (week), omit for all time.
- **Extraction:** `grep 'result-link\|result-snippet' /tmp/ddg.html | head -40`
