# Browser-Based Research Sources for Movie Recommender

Proven sites that load reliably from VPS IPs via `browser_navigate`. Order reflects effectiveness.

## Tier 1: Curation Articles (best discovery source)

### Editorialge
- **Hidden gems spring 2026:** `https://editorialge.com/hidden-gem-streaming-movies-spring-2026/`
- Published April 10, 2026 by Aaron Cunningham
- Lists 6+ films with: premise, director, cast, why it's a hidden gem, streaming platform
- Films covered: Thrash (Netflix), Feel My Voice (Netflix), Ladies First (Netflix), The Mortuary Assistant (Shudder), Broad Trip (Roku), Faces of Death (Shudder)
- Search for more: `https://editorialge.com/?s=hidden+gem+movies`

### Parade
- **Underrated movies on Netflix:** `https://parade.com/916853/samuelmurrian/best-underrated-movies-on-netflix/`
- Note: may require multiple scrolls to load full content (JavaScript-heavy)

## Tier 2: Score + Streaming Verification

### Rotten Tomatoes Search
- **URL pattern:** `https://www.rottentomatoes.com/search?search=[URL-encoded film title]`
- Returns film cards with: Tomatometer score (e.g., "Fresh score. 76%"), cast list, sometimes streaming date
- Example: `https://www.rottentomatoes.com/search?search=Ladies+First+2026`
- **No need to load the individual film page** — all key data is in search results
- RT individual film pages are often missing for obscure/foreign films (404)

### Rotten Tomatoes Browse Pages (limited value)
- "Movies to Stream at Home" sorted by Tomatometer: shows films alphabetically, not by score
- "Movies on Netflix" filtered: same issue — alphabetical, old films first
- These pages are only useful for verifying a specific film's presence, not for discovery

## Tier 3: Wikipedia (factual details, release dates)

### 2026 in Film
- `https://en.wikipedia.org/wiki/2026_in_film` — box office rankings, notable releases
- API: `https://en.wikipedia.org/w/api.php?action=parse&page=2026_in_film&prop=text&format=json&section=0`

### List of American Films 2026
- `https://en.wikipedia.org/wiki/List_of_American_films_of_2026` — chronological tables with cast/director/distributor
- Very large page — use browser_console to extract specific sections

### List of Netflix Original Films
- `https://en.wikipedia.org/wiki/List_of_Netflix_original_films_(since_2026)`

## Tier 4: Blocked / Unreliable

These sites block VPS/datacenter IPs — don't bother:
- **Google Search** — captcha blocks
- **Metacritic** — Cloudflare bot detection
- **DDG Lite** (terminal) — captcha after 1-3 queries
- **DDG HTML** (terminal) — returns empty results

## Extracting Article Text via Browser Console

For long articles, use browser_console instead of scrolling:

```js
// For most WordPress/article sites:
document.querySelector('.entry-content')?.innerText?.substring(0, 8000)
document.querySelector('main')?.innerText?.substring(0, 8000)

// For RT browse pages — filter recent films:
document.querySelector('main')?.innerText?.split('\n').filter(l => l.includes('2026'))
```
