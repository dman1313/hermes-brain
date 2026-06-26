#!/usr/bin/env python3
"""News scanner — searches financial news via GNews API (free tier, structured JSON).

GNews free tier: 100 req/day, 12-hour article delay. More than enough for
a daily scan of 14 financial queries. No web_search tool dependency — works
standalone AND in cron context equally well.

API key: set GNEWS_API_KEY in the environment, or pass via --apikey flag.
"""

import os
import sys
import json
import time
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime

# Financial news search queries — high-signal, trade-relevant
NEWS_QUERIES = [
    "stock market movers",
    "earnings report",
    "analyst upgrade",
    "FDA approval",
    "merger acquisition",
    "stock breakout",
    "stock crash",
    "crypto stocks",
    "semiconductor stocks",
    "AI stocks",
    "defense stocks",
    "oil energy stocks",
    "EV stocks",
    "IPO today",
]

GNews_API = "https://gnews.io/api/v4/search"
REQUEST_DELAY = 1.2  # seconds between API calls (stay under rate limit)


def get_api_key() -> str:
    """Get GNews API key from environment or command-line arg."""
    # Check for --apikey flag
    for i, arg in enumerate(sys.argv):
        if arg == "--apikey" and i + 1 < len(sys.argv):
            return sys.argv[i + 1]
        if arg.startswith("--apikey="):
            return arg.split("=", 1)[1]

    # Check environment
    key = os.environ.get("GNEWS_API_KEY", "")
    if key:
        return key

    return ""


def search_gnews(query: str, api_key: str, max_results: int = 5,
                 lang: str = "en", country: str = "us") -> list[dict]:
    """Search GNews API for articles matching query.

    Returns list of article dicts with keys:
        title, description, content, url, image, publishedAt, source
    """
    params = {
        "q": query,
        "apikey": api_key,
        "lang": lang,
        "country": country,
        "max": max_results,
    }
    url = f"{GNews_API}?{urllib.parse.urlencode(params)}"

    req = urllib.request.Request(url)
    req.add_header("User-Agent", "WolfTradingAgent/1.0")

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            return data.get("articles", [])
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:500] if e.fp else ""
        print(f"  [gnews HTTP {e.code}] {query[:50]}...: {body}", file=sys.stderr)
        return []
    except urllib.error.URLError as e:
        print(f"  [gnews URL error] {query[:50]}...: {e.reason}", file=sys.stderr)
        return []
    except json.JSONDecodeError as e:
        print(f"  [gnews JSON error] {query[:50]}...: {e}", file=sys.stderr)
        return []
    except OSError as e:
        print(f"  [gnews IO error] {query[:50]}...: {e}", file=sys.stderr)
        return []


def scan_news(api_key: str = "", verbose: bool = False) -> list[dict]:
    """Scan financial news via GNews API. Returns list of article dicts.

    Each article dict:
        title, description, content, url, image, publishedAt,
        source: {name, url},
        query: the search query that found it
    """
    if not api_key:
        api_key = get_api_key()

    if not api_key:
        print("  [gnews] No API key — set GNEWS_API_KEY env var or pass --apikey",
              file=sys.stderr)
        return []

    all_articles = []
    seen_urls = set()

    if verbose and os.environ.get("DEBUG"):
        print(f"  GNews API key: {api_key[:8]}... ({len(NEWS_QUERIES)} queries)")

    for i, query in enumerate(NEWS_QUERIES):
        if verbose:
            print(f"  [{i+1}/{len(NEWS_QUERIES)}] {query[:60]}...", end="", flush=True)

        articles = search_gnews(query, api_key, max_results=5)
        new_count = 0
        for article in articles:
            url = article.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                article["query"] = query
                all_articles.append(article)
                new_count += 1

        if verbose:
            print(f" {len(articles)} results, {new_count} new")

        # Rate-limit courtesy delay
        if i < len(NEWS_QUERIES) - 1:
            time.sleep(REQUEST_DELAY)

    return all_articles


def format_news_for_scoring(articles: list[dict]) -> str:
    """Join article titles + descriptions into a single string for ticker extraction."""
    lines = []
    for a in articles:
        title = a.get("title", "")
        desc = a.get("description", "")
        source = a.get("source", {}).get("name", "")
        lines.append(f"{title}. {desc} (source: {source})")
    return "\n".join(lines)


# ── Standalone test ──────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    json_out = "--json" in sys.argv

    api_key = get_api_key()
    if not api_key:
        print("ERROR: No GNews API key found.")
        print("Set GNEWS_API_KEY in environment or pass --apikey=YOUR_KEY")
        sys.exit(1)

    print(f"📰 GNews Scanner — {len(NEWS_QUERIES)} queries")
    t0 = time.time()
    articles = scan_news(api_key=api_key, verbose=verbose)
    elapsed = time.time() - t0

    print(f"\n✅ {len(articles)} unique articles in {elapsed:.1f}s")

    if json_out:
        # Strip content field for cleaner JSON output (content is long)
        short = [{k: v for k, v in a.items() if k != "content"} for a in articles]
        print(json.dumps(short, indent=2, default=str))
    else:
        from ticker_extractor import extract_tickers, sentiment_score

        text = format_news_for_scoring(articles)
        tickers = extract_tickers(text)
        sentiment = sentiment_score(text)

        print(f"\n📊 Ticker extraction:")
        print(f"   Sentiment: {sentiment:+.2f}")
        print(f"   Tickers found: {len(tickers)}")
        for t in sorted(tickers, key=lambda x: x["mentions"], reverse=True)[:15]:
            print(f"     ${t['ticker']}: {t['mentions']} mentions")

        print(f"\n📋 Top articles:")
        for a in articles[:10]:
            src = a.get("source", {}).get("name", "?")
            print(f"  • {a['title'][:100]}")
            print(f"    {src} | {a.get('publishedAt','?')[:10]}")
            print(f"    {a['url']}")
            print()
