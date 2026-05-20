#!/usr/bin/env python3
"""
🐺 WOLF TRADING AGENT — Main Orchestrator
==========================================
Scans Reddit, Twitter/X, and financial news for stock ticker signals.
Scores and ranks potential trades. Outputs a daily digest.

Usage:
    python3 wolf_scan.py                    # Full scan + print digest
    python3 wolf_scan.py --json             # Full scan + JSON output
    python3 wolf_scan.py --scanner reddit  # Reddit only
    python3 wolf_scan.py --scanner twitter # Twitter only
    python3 wolf_scan.py --scanner news    # News only
    python3 wolf_scan.py --dry-run         # Scan without final scoring
"""

import sys
import os
import json
import time
from datetime import datetime

# Add scripts dir to path for imports
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)

from scanners.reddit_scanner import scan_reddit
from scanners.twitter_scanner import scan_twitter
from scanners.news_scanner import scan_news, format_news_for_scoring
from scoring_engine import run_scoring, format_digest


def run_full_scan(verbose: bool = True) -> dict:
    """Run all three scanners and score the results."""
    metadata = {
        "scan_time": datetime.now().isoformat(),
        "scanner": "full",
    }

    # Phase 1: Reddit
    if verbose:
        print("📡 Phase 1/3: Scanning Reddit...")
    t0 = time.time()
    reddit_posts = scan_reddit(verbose=verbose)
    metadata["reddit_posts"] = len(reddit_posts)
    metadata["reddit_time"] = round(time.time() - t0, 1)
    if verbose:
        print(f"  ✅ {len(reddit_posts)} Reddit posts ({metadata['reddit_time']}s)")

    # Phase 2: Twitter
    if verbose:
        print("\n📡 Phase 2/3: Scanning Twitter/X...")
    t0 = time.time()
    twitter_result = scan_twitter(verbose=verbose)
    if isinstance(twitter_result, dict) and twitter_result.get("status") == "unavailable":
        twitter_tweets = []
        metadata["twitter_status"] = "unavailable"
        metadata["twitter_reason"] = twitter_result.get("reason", "")
    else:
        twitter_tweets = twitter_result if isinstance(twitter_result, list) else []
    metadata["twitter_tweets"] = len(twitter_tweets)
    metadata["twitter_time"] = round(time.time() - t0, 1)
    if verbose:
        if metadata.get("twitter_status") == "unavailable":
            print(f"  ⚠️ Twitter skipped — {metadata['twitter_reason']}")
        else:
            print(f"  ✅ {len(twitter_tweets)} tweets ({metadata['twitter_time']}s)")

    # Phase 3: News (GNews API — works standalone + cron)
    if verbose:
        print("\n📡 Phase 3/3: Scanning News (GNews API)...")
    t0 = time.time()
    news_articles = scan_news(verbose=verbose)
    metadata["news_articles"] = len(news_articles)
    metadata["news_time"] = round(time.time() - t0, 1)
    if verbose:
        if news_articles:
            sources = len(set(a.get("source", {}).get("name", "") for a in news_articles))
            print(f"  ✅ {len(news_articles)} articles from {sources} sources ({metadata['news_time']}s)")
        else:
            print(f"  ⚠️ No news articles — check GNEWS_API_KEY ({metadata['news_time']}s)")

    # Phase 4: Score
    if verbose:
        print("\n🧠 Scoring signals...")
    scored = run_scoring(reddit_posts, twitter_tweets, news_articles)
    metadata["signals_found"] = len(scored)

    return {
        "metadata": metadata,
        "signals": scored,
        "reddit_posts": reddit_posts,
        "twitter_tweets": twitter_tweets,
        "news_articles": news_articles,
    }


def run_single_scanner(scanner: str):
    """Run just one scanner for testing."""
    if scanner == "reddit":
        posts = scan_reddit(verbose=True)
        print(f"\n✅ {len(posts)} Reddit posts")
        for p in sorted(posts, key=lambda x: x["score"], reverse=True)[:5]:
            print(f"  r/{p['subreddit']} +{p['score']} {p['title'][:80]}")
    elif scanner == "twitter":
        result = scan_twitter(verbose=True)
        if isinstance(result, list):
            print(f"\n✅ {len(result)} tweets")
            for t in result[:10]:
                print(f"  @{t.get('author', '?')}: {t.get('text', '')[:100]}")
        else:
            print(f"⚠️ {result.get('reason', 'Twitter unavailable')}")
    elif scanner == "news":
        articles = scan_news(verbose=True)
        print(f"\n✅ {len(articles)} news articles")
        from ticker_extractor import extract_tickers, sentiment_score
        text = format_news_for_scoring(articles)
        tickers = extract_tickers(text)
        sentiment = sentiment_score(text)
        print(f"   Sentiment: {sentiment:+.2f} | Tickers: {len(tickers)}")
        for t in sorted(tickers, key=lambda x: x["mentions"], reverse=True)[:10]:
            print(f"     ${t['ticker']}: {t['mentions']} mentions")
        print(f"\n📋 Top articles:")
        for a in articles[:8]:
            src = a.get("source", {}).get("name", "?")
            print(f"  • {a['title'][:100]}")
            print(f"    {src} | {a.get('publishedAt','?')[:10]}")
            print(f"    {a['url']}")
    else:
        print(f"Unknown scanner: {scanner}")
        sys.exit(1)


def main():
    args = sys.argv[1:]
    json_mode = "--json" in args
    dry_run = "--dry-run" in args
    scanner = None

    for i, arg in enumerate(args):
        if arg == "--scanner" and i + 1 < len(args):
            scanner = args[i + 1]

    if scanner:
        run_single_scanner(scanner)
        return

    # Full scan
    print("🐺 WOLF TRADING AGENT")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 50)
    result = run_full_scan(verbose=not json_mode)

    if json_mode:
        # JSON output for programmatic use
        output = {
            "metadata": result["metadata"],
            "signals": result["signals"],
        }
        print(json.dumps(output, indent=2, default=str))
    else:
        # Human-readable digest
        digest = format_digest(result["signals"], result["metadata"])
        print("\n" + digest)

    # Save to file for cron/archiving
    output_dir = os.path.join(SCRIPTS_DIR, "..", "..", "..", "output")
    os.makedirs(output_dir, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    with open(os.path.join(output_dir, f"wolf_scan_{date_str}.json"), "w") as f:
        json.dump({
            "metadata": result["metadata"],
            "signals": result["signals"],
        }, f, indent=2, default=str)

    return result


if __name__ == "__main__":
    main()
