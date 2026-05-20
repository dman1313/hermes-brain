#!/usr/bin/env python3
"""Wolf Scoring Engine — fuses signals from Reddit, Twitter, and News into ranked trade ideas.

Scoring formula:
    Total Score = sum(source_weight × (mention_score × 0.6 + sentiment_bonus × 0.2 + velocity_bonus × 0.2))

Source weights (configurable):
    Reddit:  0.35  (highest — retail sentiment leader)
    Twitter: 0.35  (fastest moving, fin-twit)
    News:    0.30  (fundamental catalysts)

Signal tiers:
    🟢 STRONG BUY   (score ≥ 0.70)
    🟡 WATCH         (score ≥ 0.40)
    ⚪ NEUTRAL       (score < 0.40)
"""

import json
import sys
from datetime import datetime
from collections import defaultdict
from ticker_extractor import extract_tickers, sentiment_score, get_company_name

# ── Configuration ──────────────────────────────────────────────────────
SOURCE_WEIGHTS = {
    "reddit": 0.35,
    "twitter": 0.35,
    "news": 0.30,
}

MENTION_THRESHOLD = 3       # Minimum mentions across all sources to consider
SIGNAL_TIERS = [
    ("🟢 STRONG BUY", 0.70),
    ("🟡 WATCH", 0.40),
    ("⚪ NEUTRAL", 0.0),
]

# ── Signal aggregation ─────────────────────────────────────────────────

def aggregate_signals(reddit_posts: list[dict], twitter_tweets: list[dict], news_articles: list[dict]) -> list[dict]:
    """Combine all source signals into per-ticker aggregates."""
    ticker_data = defaultdict(lambda: {
        "ticker": "",
        "mentions": 0,
        "sources": set(),
        "total_sentiment": 0.0,
        "sentiment_count": 0,
        "reddit_score": 0,
        "reddit_mentions": 0,
        "twitter_mentions": 0,
        "news_mentions": 0,
        "top_posts": [],
        "reddit_urls": [],
    })

    # Process Reddit posts
    for post in reddit_posts:
        text = post.get("full_text", "")
        tickers = extract_tickers(text)
        sent = sentiment_score(text)
        engagement = (post.get("score", 0) + post.get("num_comments", 0) * 2) / 1000.0  # normalize
        for t in tickers:
            tk = t["ticker"]
            td = ticker_data[tk]
            td["ticker"] = tk
            td["mentions"] += t["mentions"]
            td["sources"].add("reddit")
            td["total_sentiment"] += sent * t["mentions"]
            td["sentiment_count"] += t["mentions"]
            td["reddit_mentions"] += t["mentions"]
            td["reddit_score"] = max(td["reddit_score"], engagement)
            if post.get("url"):
                td["reddit_urls"].append(post["url"])
            if len(td["top_posts"]) < 3:
                td["top_posts"].append({
                    "text": post.get("title", "")[:120],
                    "source": "reddit",
                    "subreddit": post.get("subreddit", ""),
                    "score": post.get("score", 0),
                    "url": post.get("url", ""),
                })

    # Process Twitter tweets
    for tweet in twitter_tweets:
        text = tweet.get("text", "")
        tickers = extract_tickers(text)
        sent = sentiment_score(text)
        metrics = tweet.get("metrics", {})
        engagement = (metrics.get("like_count", 0) + metrics.get("retweet_count", 0) * 3 + metrics.get("reply_count", 0) * 2) / 100.0
        for t in tickers:
            tk = t["ticker"]
            td = ticker_data[tk]
            td["ticker"] = tk
            td["mentions"] += t["mentions"]
            td["sources"].add("twitter")
            td["total_sentiment"] += sent * t["mentions"]
            td["sentiment_count"] += t["mentions"]
            td["twitter_mentions"] += t["mentions"]
            if len(td["top_posts"]) < 3:
                td["top_posts"].append({
                    "text": text[:120],
                    "source": "twitter",
                    "author": tweet.get("author", ""),
                    "score": engagement,
                    "url": f"https://x.com/i/status/{tweet.get('id', '')}" if tweet.get("id") else "",
                })

    # Process News articles (supports both legacy {text} and GNews {title, description, content} formats)
    for article in news_articles:
        text = article.get("text", "")
        if not text:
            # GNews format: build text from title + description + content
            parts = []
            if article.get("title"):
                parts.append(article["title"])
            if article.get("description"):
                parts.append(article["description"])
            if article.get("content"):
                parts.append(article["content"])
            text = ". ".join(parts)
        tickers = extract_tickers(text)
        sent = sentiment_score(text)
        for t in tickers:
            tk = t["ticker"]
            td = ticker_data[tk]
            td["ticker"] = tk
            td["mentions"] += t["mentions"]
            td["sources"].add("news")
            td["total_sentiment"] += sent * t["mentions"]
            td["sentiment_count"] += t["mentions"]
            td["news_mentions"] += t["mentions"]

    return list(ticker_data.values())


def score_tickers(aggregated: list[dict]) -> list[dict]:
    """Apply scoring formula and rank tickers."""
    scored = []
    for data in aggregated:
        if data["mentions"] < MENTION_THRESHOLD:
            continue

        # Mention score (0-1 normalized)
        max_mentions = max(a["mentions"] for a in aggregated) if aggregated else 1
        mention_score = min(1.0, data["mentions"] / max(max_mentions, 10))

        # Sentiment bonus
        avg_sentiment = data["total_sentiment"] / max(data["sentiment_count"], 1)
        sentiment_bonus = avg_sentiment  # already -1.0 to 1.0

        # Velocity bonus — multi-source signals score higher
        velocity_bonus = min(1.0, len(data["sources"]) / 3.0)

        # Weighted source score
        source_score = 0.0
        for src in data["sources"]:
            source_score += SOURCE_WEIGHTS.get(src, 0.0)

        # Total score
        total = source_score * (
            mention_score * 0.6 +
            max(0, sentiment_bonus) * 0.2 +
            velocity_bonus * 0.2
        )

        # Assign tier
        tier = "⚪ NEUTRAL"
        for tier_name, threshold in SIGNAL_TIERS:
            if total >= threshold:
                tier = tier_name
                break

        data["score"] = round(total, 3)
        data["tier"] = tier
        data["avg_sentiment"] = round(avg_sentiment, 3)
        data["velocity"] = len(data["sources"])
        data["company_name"] = get_company_name(data["ticker"])
        scored.append(data)

    # Convert sets to sorted lists for JSON-safe output
    for data in scored:
        if isinstance(data.get("sources"), set):
            data["sources"] = sorted(data["sources"])

    return sorted(scored, key=lambda x: x["score"], reverse=True)


def run_scoring(reddit_posts: list[dict], twitter_tweets: list[dict], news_articles: list[dict]) -> list[dict]:
    """Full scoring pipeline."""
    aggregated = aggregate_signals(reddit_posts, twitter_tweets, news_articles)
    scored = score_tickers(aggregated)
    return scored


# ── Output formatting ──────────────────────────────────────────────────

def format_digest(scored: list[dict], metadata: dict = None) -> str:
    """Generate a Telegram-friendly daily digest."""
    now = datetime.now()
    lines = [
        f"🐺 **WOLF TRADING SIGNALS** — {now.strftime('%A, %B %d %Y')}",
        "",
        "━" * 30,
    ]

    if metadata:
        sources_str = []
        if metadata.get("reddit_posts"):
            sources_str.append(f"Reddit: {metadata['reddit_posts']} posts")
        if metadata.get("twitter_tweets"):
            sources_str.append(f"Twitter: {metadata['twitter_tweets']} tweets")
        if metadata.get("news_articles"):
            sources_str.append(f"News: {metadata['news_articles']} queries")
        if sources_str:
            lines.append(f"📡 Scanned: {' · '.join(sources_str)}")
        if metadata.get("twitter_status") == "unavailable":
            lines.append("⚠️ Twitter scan skipped — xurl not configured")
        lines.append("")

    if not scored:
        lines.append("_No significant signals today. Market is quiet._ 🐺💤")
        return "\n".join(lines)

    # Strong Buy section
    strong_buys = [s for s in scored if s["tier"] == "🟢 STRONG BUY"]
    if strong_buys:
        lines.append("## 🟢 STRONG BUY")
        for s in strong_buys[:5]:
            lines.append(format_signal_line(s))
        lines.append("")

    # Watch section
    watches = [s for s in scored if s["tier"] == "🟡 WATCH"]
    if watches:
        lines.append("## 🟡 WATCH")
        for s in watches[:8]:
            lines.append(format_signal_line(s))
        lines.append("")

    # Neutral section (top 5)
    neutrals = [s for s in scored if s["tier"] == "⚪ NEUTRAL"][:5]
    if neutrals:
        lines.append("## ⚪ ALSO MENTIONED")
        for s in neutrals:
            lines.append(format_signal_line(s, compact=True))
        lines.append("")

    lines.append("━" * 30)
    lines.append(f"🐺 _Wolf scanned {len(scored)} tickers today · {now.strftime('%H:%M UTC')}_")
    lines.append("_Not financial advice. Do your own research._")

    return "\n".join(lines)


def format_signal_line(s: dict, compact: bool = False) -> str:
    """Format a single signal line."""
    sources = ", ".join(sorted(s["sources"]))
    name = s.get("company_name", s["ticker"])
    sent_emoji = "📈" if s["avg_sentiment"] > 0.1 else ("📉" if s["avg_sentiment"] < -0.1 else "➡️")
    if compact:
        return f"• ${s['ticker']} ({name}) — score:{s['score']:.2f} · {s['mentions']} mentions · {sources}"
    else:
        lines = [
            f"• **${s['ticker']}** — {name}  {sent_emoji}",
            f"  Score: {s['score']:.2f} · {s['mentions']} mentions · {s['velocity']} sources",
            f"  Sentiment: {s['avg_sentiment']:+.2f} · Sources: {sources}",
        ]
        if s.get("top_posts"):
            top = s["top_posts"][0]
            lines.append(f"  Top: _{top.get('text', '')[:100]}_")
        return "\n".join(lines)


if __name__ == "__main__":
    print("Scoring engine: use via wolf_scan.py orchestrator")
