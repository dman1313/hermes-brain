#!/usr/bin/env python3
"""Reddit scanner — searches Reddit for trading-related posts.

Three backends, in order of preference (auto-detected):
1. PRAW (OAuth) — full post content, requires Reddit app credentials
2. RSS feeds — limited (WSB only, rate-limited), real post content
3. DuckDuckGo search — no auth, returns titles only (body content masked)

Supports REDDIT_CLIENT_ID + REDDIT_CLIENT_SECRET env vars for PRAW.

Usage:
    REDDIT_CLIENT_ID=xxx REDDIT_CLIENT_SECRET=xxx python3 -m scanners.reddit_scanner
"""

import sys
import json
import os
import re
import time
import html
import urllib.request
import urllib.parse
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

# Rate limiting between requests
REQUEST_DELAY = 1.5  # seconds


# ─── Backend 1: PRAW (OAuth) — full content, best quality ───

def scan_praw(verbose: bool = False) -> list[dict]:
    """Scan Reddit using PRAW with OAuth (requires Reddit app credentials).

    Create a free Reddit app at https://www.reddit.com/prefs/apps
    Then set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET in the environment.
    """
    client_id = os.environ.get("REDDIT_CLIENT_ID")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET")

    if not client_id or not client_secret:
        if verbose:
            print("  [praw] REDDIT_CLIENT_ID or REDDIT_CLIENT_SECRET not set — skipping PRAW")
        return None

    try:
        import praw
    except ImportError:
        if verbose:
            print("  [praw] praw not installed — install with: pip install praw (or uv pip install praw)")
        return None

    try:
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent="WolfTradingAgent/1.0 (by /u/humangoodai)",
        )
        all_posts = []
        seen_urls = set()

        for sub_name in SUBREDDITS:
            if verbose:
                print(f"  [praw] r/{sub_name}...", end=" ", flush=True)
            try:
                sub = reddit.subreddit(sub_name)
                count = 0
                for post in sub.hot(limit=25):
                    if post.url in seen_urls:
                        continue
                    seen_urls.add(post.url)
                    all_posts.append({
                        "id": post.id,
                        "title": post.title or "",
                        "selftext": post.selftext or "",
                        "full_text": f"{post.title}\n{post.selftext}" if post.selftext else post.title,
                        "score": post.score,
                        "num_comments": post.num_comments,
                        "upvote_ratio": post.upvote_ratio,
                        "url": f"https://www.reddit.com{post.permalink}",
                        "subreddit": sub_name,
                        "created_utc": int(post.created_utc),
                        "flair": post.link_flair_text or "",
                        "source": "reddit",
                        "backend": "praw",
                    })
                    count += 1
                if verbose:
                    print(f"{count} posts")
            except Exception as e:
                if verbose:
                    print(f"ERROR: {e}")
            time.sleep(REQUEST_DELAY / 2)

        return all_posts

    except Exception as e:
        if verbose:
            print(f"  [praw] PRAW initialization failed: {e}")
        return None


# ─── Backend 2: RSS Feeds — limited, works for WSB ───

def scan_rss(verbose: bool = False) -> list[dict]:
    """Scan Reddit via RSS feeds. Limited to subreddits with accessible RSS."""
    all_posts = []
    seen_urls = set()

    # RSS feeds for targeted subreddits
    # Only WSB RSS is consistently accessible; others hit rate limits
    rss_subs = ["wallstreetbets"]  # the one that works

    for sub_name in rss_subs:
        if verbose:
            print(f"  [rss] r/{sub_name}...", end=" ", flush=True)
        try:
            url = f"https://www.reddit.com/r/{sub_name}/.rss?limit=25"
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "WolfTradingAgent/1.0 (by /u/humangoodai)"},
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read().decode("utf-8", errors="ignore")

            # Parse RSS entries
            entries = re.findall(r'<entry>(.*?)</entry>', data, re.DOTALL)
            if verbose:
                print(f"{len(entries)} raw entries", end=" ")

            # Check for rate-limit / empty
            if len(entries) < 2 and "429" in data:
                if verbose:
                    print("(rate-limited)")
                continue

            for entry_xml in entries:
                # Extract title
                title_match = re.search(r'<title[^>]*>(.*?)</title>', entry_xml, re.DOTALL)
                title = html.unescape(title_match.group(1).strip()) if title_match else ""

                # Extract content (has full HTML body for text posts)
                content_match = re.search(r'<content[^>]*>(.*?)</content>', entry_xml, re.DOTALL)
                content_html = html.unescape(content_match.group(1).strip()) if content_match else ""

                # Clean HTML tags from content
                content_text = re.sub(r'<[^>]+>', ' ', content_html)
                content_text = re.sub(r'\s+', ' ', content_text).strip()

                # Extract link
                link_match = re.search(r'<link[^>]*href="([^"]*)"', entry_xml)
                post_url = link_match.group(1) if link_match else ""

                if post_url in seen_urls or not title:
                    continue
                seen_urls.add(post_url)

                # Extract author
                author_match = re.search(r'<author>.*?<name>(.*?)</name>', entry_xml, re.DOTALL)
                author = author_match.group(1).strip() if author_match else ""

                # Extract ID (post id from <id>t3_XXXXX</id>)
                id_match = re.search(r'<id>(.*?)</id>', entry_xml)
                post_id = id_match.group(1).split("_")[-1] if id_match else ""

                all_posts.append({
                    "id": post_id,
                    "title": title[:500],
                    "selftext": content_text[:5000],
                    "full_text": f"{title}\n{content_text}" if content_text else title,
                    "score": 0,  # RSS doesn't provide scores
                    "num_comments": 0,
                    "upvote_ratio": 0,
                    "url": post_url,
                    "subreddit": sub_name,
                    "created_utc": 0,
                    "flair": "",
                    "source": "reddit",
                    "backend": "rss",
                })

            if verbose:
                print(f"→ {sum(1 for p in all_posts if p.get('subreddit') == sub_name)} kept")

            time.sleep(REQUEST_DELAY)

        except urllib.error.HTTPError as e:
            if verbose:
                print(f"HTTP {e.code}")
        except Exception as e:
            if verbose:
                print(f"error: {e}")

    return all_posts


# ─── Backend 3: DuckDuckGo — no auth, titles only (body masked) ───

def scan_ddg(verbose: bool = False) -> list[dict]:
    """Scan Reddit via DuckDuckGo search. Returns titles+URLs only.

    Since May 2026, DDG Reddit results have masked body content.
    We still get titles (which often contain tickers) and post URLs.
    """
    all_results = []
    seen_urls = set()

    # Build search queries: subreddit + term combinations
    queries = []
    for sub in SUBREDDITS:
        for term in SEARCH_TERMS[:3]:  # Limit terms
            queries.append(f"site:reddit.com/r/{sub} {term}")

    # Also do broader subreddit searches for general content
    for sub in SUBREDDITS:
        queries.append(f"site:reddit.com/r/{sub}")

    # Remove duplicates
    queries = list(dict.fromkeys(queries))

    consecutive_failures = 0

    for query in queries[:8]:  # Cap at 8 queries to avoid timeouts
        try:
            encoded = urllib.parse.quote(query)
            url = f"https://html.duckduckgo.com/html/?q={encoded}&t=h_&ia=web"
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                },
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                html_content = resp.read().decode("utf-8", errors="ignore")

            # Extract results from DDG HTML
            snippets = re.findall(
                r'class="result__snippet"[^>]*>(.*?)</a>', html_content, re.DOTALL
            )
            titles = re.findall(
                r'class="result__title"[^>]*>.*?<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>',
                html_content, re.DOTALL
            )

            for i, (post_url, title_html) in enumerate(titles):
                if post_url in seen_urls:
                    continue
                seen_urls.add(post_url)

                title = re.sub(r'<[^>]+>', '', title_html).strip()
                title = html.unescape(title)

                snippet = snippets[i] if i < len(snippets) else ""
                snippet = re.sub(r'<[^>]+>', '', snippet).strip()
                snippet = html.unescape(snippet)

                # Extract subreddit from URL
                sub_match = re.search(r'reddit\.com/r/([^/]+)', post_url)
                subreddit = sub_match.group(1) if sub_match else ""

                all_results.append({
                    "id": "",
                    "title": title[:500],
                    "selftext": "",  # DDG masks body content
                    "full_text": title,  # Use title only for ticker extraction
                    "score": 0,
                    "num_comments": 0,
                    "upvote_ratio": 0,
                    "url": post_url,
                    "subreddit": subreddit,
                    "created_utc": 0,
                    "flair": "",
                    "source": "reddit",
                    "backend": "ddg",
                })

            time.sleep(REQUEST_DELAY)

        except Exception as e:
            if verbose:
                print(f"  [ddg error] '{query[:40]}...': {e}", file=sys.stderr)
            consecutive_failures += 1
            if consecutive_failures >= 3:
                if verbose:
                    print("  [ddg] 3 consecutive failures — aborting DDG scan", file=sys.stderr)
                break
            time.sleep(REQUEST_DELAY)

    # Content quality check
    # Titles alone are better than nothing - they often contain ticker cashtags ($AAPL)
    total_text = sum(len(r.get("full_text", "") or "") for r in all_results)

    if total_text < 200:
        if verbose:
            print("  ⚠️  [reddit] DDG returned very little content (known partial block).", file=sys.stderr)
            print("  ⚠️  [reddit] Titles may still contain cashtags. Using what we have.", file=sys.stderr)

    return all_results


# ─── Orchestrator ───

def scan_reddit(verbose: bool = False) -> list[dict]:
    """Run full Reddit scan. Tries backends in order and merges results.

    Returns list of parsed post dicts with keys:
        id, title, selftext, full_text, score, num_comments,
        upvote_ratio, url, subreddit, created_utc, flair, source, backend
    """
    if verbose:
        print("  [reddit] Scanning Reddit...")

    # Try PRAW first (best quality, needs free Reddit app)
    praw_posts = scan_praw(verbose=verbose)
    if praw_posts is not None and len(praw_posts) > 0:
        if verbose:
            print(f"  [reddit] ✅ Using PRAW backend — {len(praw_posts)} posts")
        return praw_posts

    # Fallback: RSS for WSB
    if verbose:
        print("  [reddit] PRAW not available — trying RSS backend...")
    rss_posts = scan_rss(verbose=verbose)

    # Fallback: DDG for all subreddits (titles only)
    if verbose:
        print("  [reddit] Also trying DuckDuckGo for broader coverage...")
    ddg_posts = scan_ddg(verbose=verbose)

    # Merge results (deduplicate by URL)
    all_posts = []
    seen = set()
    for post in rss_posts + ddg_posts:
        url = post.get("url", "")
        if url not in seen:
            seen.add(url)
            all_posts.append(post)

    if verbose:
        sources = {}
        for p in all_posts:
            b = p.get("backend", "?")
            sources[b] = sources.get(b, 0) + 1
        source_str = ", ".join(f"{k}={v}" for k, v in sources.items())
        print(f"  [reddit] ✅ {len(all_posts)} posts total ({source_str})")

    return all_posts


if __name__ == "__main__":
    verbose = "--quiet" not in sys.argv
    print("🐺 Reddit Scanner (auto-select backend)")
    posts = scan_reddit(verbose=verbose)
    print(f"\nTotal posts: {len(posts)}")

    from ticker_extractor import extract_tickers, sentiment_score

    for post in sorted(posts, key=lambda p: len(p.get("full_text", "")), reverse=True)[:10]:
        tickers = extract_tickers(post.get("full_text", ""))
        sentiment = sentiment_score(post.get("full_text", ""))
        source_tag = f"r/{post.get('subreddit', '?')}"
        print(f"  [{source_tag}/{post.get('backend','?')}] {post['title'][:100]}")
        if tickers:
            ticker_str = ", ".join([f"${t['ticker']}({t['mentions']})" for t in tickers[:5]])
            print(f"    tickers: {ticker_str}")
