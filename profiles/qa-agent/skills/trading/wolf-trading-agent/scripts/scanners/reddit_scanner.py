#!/usr/bin/env python3
"""Reddit scanner — searches Reddit via DuckDuckGo for trading-related posts.

Uses the duckduckgo_search Python library (free, no API key needed).
Fallback: raw HTML scraping if library isn't installed.
"""

import sys
import json
from datetime import datetime

# Subreddits to scan
SUBREDDITS = [
    "wallstreetbets",
    "stocks",
    "options",
    "investing",
    "pennystocks",
    "StockMarket",
    "thetagang",
]

# Search terms that surface trading signals
SEARCH_TERMS = [
    "DD", "YOLO", "earnings", "calls", "puts", "tendies",
    "rocket", "moon", "breakout", "squeeze", "upgrade",
    "downgrade", "buyout", "merger", "FDA", "IPO",
]


def try_import_ddgs():
    """Try importing ddgs (duckduckgo_search replacement)."""
    try:
        from ddgs import DDGS
        return DDGS
    except ImportError:
        try:
            from duckduckgo_search import DDGS
            return DDGS
        except ImportError:
            return None


def search_reddit_ddgs(DDGS, subreddit: str, term: str, max_results: int = 10) -> list[dict]:
    """Search Reddit via DuckDuckGo."""
    query = f"site:reddit.com/r/{subreddit} {term}"
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results, timelimit="d"):
                results.append({
                    "title": r.get("title", ""),
                    "body": r.get("body", ""),
                    "url": r.get("href", ""),
                    "subreddit": subreddit,
                    "search_term": term,
                    "source": "reddit",
                })
    except Exception as e:
        print(f"  [ddgs error] r/{subreddit} '{term}': {e}", file=sys.stderr)
    return results


def search_reddit_fallback(subreddit: str, max_results: int = 10) -> list[dict]:
    """Fallback: use urllib to scrape Reddit search HTML (no library needed)."""
    import urllib.request
    import urllib.parse
    import re

    results = []
    query = urllib.parse.quote(f"site:reddit.com/r/{subreddit}")
    url = f"https://html.duckduckgo.com/html/?q={query}&t=h_&ia=web"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="ignore")

        # Extract result snippets from DuckDuckGo HTML
        snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)
        titles = re.findall(r'class="result__title"[^>]*>.*?<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', html, re.DOTALL)

        for i, (url, title) in enumerate(titles[:max_results]):
            snippet = snippets[i] if i < len(snippets) else ""
            snippet = re.sub(r'<[^>]+>', '', snippet).strip()
            results.append({
                "title": re.sub(r'<[^>]+>', '', title).strip(),
                "body": snippet,
                "url": url,
                "subreddit": subreddit,
                "source": "reddit",
            })
    except Exception as e:
        print(f"  [fallback error] r/{subreddit}: {e}", file=sys.stderr)

    return results


def scan_reddit(verbose: bool = False) -> list[dict]:
    """Run full Reddit scan. Returns list of parsed post dicts."""
    DDGS = try_import_ddgs()
    all_results = []
    seen_urls = set()

    for sub in SUBREDDITS:
        if verbose:
            print(f"  scanning r/{sub}...")

        if DDGS:
            # Search with multiple terms per subreddit
            for term in SEARCH_TERMS[:3]:  # Limit terms to avoid rate limits
                results = search_reddit_ddgs(DDGS, sub, term, max_results=5)
                for r in results:
                    if r["url"] not in seen_urls:
                        seen_urls.add(r["url"])
                        all_results.append(r)
        else:
            results = search_reddit_fallback(sub, max_results=15)
            for r in results:
                if r["url"] not in seen_urls:
                    seen_urls.add(r["url"])
                    all_results.append(r)

        if verbose:
            print(f"    → {len([r for r in all_results if r.get('subreddit') == sub])} posts")

    # Reformat for compatibility with scoring engine
    parsed = []
    for r in all_results:
        parsed.append({
            "id": r.get("url", "").split("/")[-1] if r.get("url") else "",
            "title": r.get("title", ""),
            "selftext": r.get("body", ""),
            "full_text": f"{r.get('title', '')}\n{r.get('body', '')}",
            "score": 0,  # DDG doesn't provide scores
            "num_comments": 0,
            "upvote_ratio": 0,
            "url": r.get("url", ""),
            "subreddit": r.get("subreddit", ""),
            "created_utc": 0,
            "flair": "",
            "source": "reddit",
        })

    return parsed


if __name__ == "__main__":
    import sys
    from ticker_extractor import extract_tickers, sentiment_score

    verbose = "--quiet" not in sys.argv
    print("🐺 Reddit Scanner (DuckDuckGo backend)")
    posts = scan_reddit(verbose=verbose)
    print(f"\nTotal posts: {len(posts)}")

    for post in sorted(posts, key=lambda p: len(p.get("full_text", "")), reverse=True)[:10]:
        tickers = extract_tickers(post.get("full_text", ""))
        sentiment = sentiment_score(post.get("full_text", ""))
        source_tag = f"r/{post.get('subreddit', '?')}"
        print(f"  [{source_tag}] {post['title'][:100]}")
        if tickers:
            ticker_str = ", ".join([f"${t['ticker']}({t['mentions']})" for t in tickers[:5]])
            print(f"    tickers: {ticker_str}")
