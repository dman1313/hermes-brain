#!/usr/bin/env python3
"""Twitter/X scanner — uses xurl CLI for cashtag/ticker searches, falls back to web_search."""

import subprocess
import json
import os
import sys

# Fin-twit accounts to pull timelines from
FIN_TWIT_ACCOUNTS = [
    "unusual_whales",
    "stockdweebs",
    "deitaone",
    "KobeissiLetter",
    "FXhedgers",
    "NorthmanTrader",
    "MacroAlf",
    "Gurgavin",
    "SquawkStreet",
    "bespokeinvest",
]

# Cashtag searches — scan these daily
CASHTAG_SEARCHES = [
    "$SPY OR $QQQ OR $IWM",
    "$AAPL OR $MSFT OR $GOOGL OR $AMZN OR $NVDA",
    "$TSLA",
    "$MSTR OR $COIN OR $RIOT OR $MARA OR $CLSK",
    "$PLTR OR $SOFI OR $HOOD OR $AFRM",
    "$RKLB OR $ASTS OR $LUNR",
    "$IONQ OR $QBTS OR $RGTI",
    "stock market today",
]


def xurl_installed() -> bool:
    """Check if xurl CLI is available."""
    try:
        result = subprocess.run(["xurl", "--help"], capture_output=True, timeout=5)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def xurl_search(query: str, max_results: int = 10) -> list[dict]:
    """Search X/Twitter using xurl. Returns list of tweet dicts."""
    try:
        result = subprocess.run(
            ["xurl", "search", query, "-n", str(max_results)],
            capture_output=True,
            timeout=30,
            text=True,
        )
        data = json.loads(result.stdout) if result.stdout.strip() else {}
        tweets = data.get("data", [])
        return tweets
    except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception) as e:
        print(f"  [xurl error] {query}: {e}", file=sys.stderr)
        return []


def xurl_timeline(username: str, max_results: int = 5) -> list[dict]:
    """Pull a user's timeline."""
    try:
        result = subprocess.run(
            ["xurl", "user", username, "-n", str(max_results)],
            capture_output=True,
            timeout=30,
            text=True,
        )
        data = json.loads(result.stdout) if result.stdout.strip() else {}
        tweets = data.get("data", [])
        return tweets
    except Exception as e:
        return []


def scan_twitter_xurl(verbose: bool = False) -> list[dict]:
    """Scan Twitter using xurl CLI. Returns parsed tweet objects."""
    all_tweets = []

    # Search cashtags
    for query in CASHTAG_SEARCHES:
        if verbose:
            print(f"  xurl search: {query[:60]}...")
        tweets = xurl_search(query)
        for t in tweets:
            all_tweets.append({
                "id": t.get("id", ""),
                "text": t.get("text", ""),
                "author": t.get("author_id", "unknown"),
                "source": "twitter",
                "query": query,
                "created_at": t.get("created_at", ""),
                "metrics": t.get("public_metrics", {}),
            })

    # Pull fin-twit timelines
    for account in FIN_TWIT_ACCOUNTS:
        if verbose:
            print(f"  xurl timeline: @{account}")
        tweets = xurl_timeline(account)
        for t in tweets:
            all_tweets.append({
                "id": t.get("id", ""),
                "text": t.get("text", ""),
                "author": account,
                "source": "twitter",
                "query": f"timeline:@{account}",
                "created_at": t.get("created_at", ""),
                "metrics": t.get("public_metrics", {}),
            })

    return all_tweets


def scan_twitter_fallback(verbose: bool = False) -> dict:
    """Fallback scan when xurl is not available. Returns a status dict for the orchestrator."""
    return {
        "status": "unavailable",
        "reason": "xurl CLI not installed or not authenticated",
        "setup_hint": "Install xurl (see xurl skill) and run: xurl auth oauth2 --app my-app",
        "tweets": [],
    }


def scan_twitter(verbose: bool = False) -> list[dict] | dict:
    """Scan Twitter, using xurl if available, fallback otherwise."""
    if xurl_installed():
        return scan_twitter_xurl(verbose=verbose)
    else:
        if verbose:
            print("  [twitter] xurl not available — skipping Twitter scan")
            print("  [twitter] Install: curl -fsSL https://raw.githubusercontent.com/xdevplatform/xurl/main/install.sh | bash")
        return scan_twitter_fallback(verbose=verbose)


if __name__ == "__main__":
    import sys
    from ticker_extractor import extract_tickers, sentiment_score

    verbose = "--quiet" not in sys.argv
    result = scan_twitter(verbose=verbose)

    if isinstance(result, dict) and result.get("status") == "unavailable":
        print(f"Twitter unavailable: {result['reason']}")
        sys.exit(1)

    tweets = result if isinstance(result, list) else []
    print(f"\nTotal tweets: {len(tweets)}")
    for tweet in tweets[:15]:
        tickers = extract_tickers(tweet.get("text", ""))
        sentiment = sentiment_score(tweet.get("text", ""))
        print(f"  [{tweet.get('author', '?')}] {tweet.get('text', '')[:100]}")
        if tickers:
            print(f"    $: {', '.join([t['ticker'] for t in tickers[:5]])} sent:{sentiment:+.1f}")
