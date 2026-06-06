# GitHub Topic Page Research — Pitfalls & Patterns

## Problem

GitHub topic pages (`github.com/topics/<tag>`) are often near-empty for niche tags. Scraping them wastes time and returns 1-5 repos, many of which are low-quality spam from the same author stuffing tags.

**Example:** `quant-trading-framework` (5 repos), `quant-trading-source` (1 repo), `quant-trading-toolkit` (1 repo) — all dominated by one user (Krexibd) cross-posting the same repo with different tags.

## What Works Better

### 1. Broad topic pages first
Instead of narrow tags, try the broadest relevant topic:
- `quantitative-analysis` → 341 repos (vs 5 for `quant-trading-framework`)
- `algorithmic-trading` → much larger
- `quantitative-finance` → large

### 2. Curated lists (awesome-*)
- `github.com/wilsonfreitas/awesome-quant` — massive curated list
- Search: `github.com/topics/awesome-<domain>`
- These have already been filtered for quality

### 3. Article-based discovery
Search for "best GitHub repos for X" articles:
- KDnuggets, Medium, Towards Data Science
- These do the curation work for you
- Extract repo names from the article, then inspect each

### 4. Star-count filtering
When you find a good repo, check its "Related repositories" and the topic tags it uses. High-star repos in a topic signal the topic is active.

### 5. Multi-tool approach
Combine web search (for curated lists and articles) + zread (for repo structure and docs) + web reader (for specific README sections). Don't rely on a single source.

## Research Workflow for Domain Exploration

1. **Web search** for "best GitHub repos for [domain]" — get curated lists
2. **Fetch the broadest topic page** — see what's actually tagged
3. **Inspect top 3-5 repos** via zread (structure + README)
4. **Cross-reference** with awesome-lists
5. **Synthesize ideas** — don't just list repos, extract patterns and concepts

## Anti-Patterns

- Scraping 3 narrow topic pages in sequence hoping for different results
- Trusting topic page descriptions (they're often auto-generated)
- Including repos with <10 stars without checking if they're real projects
- Listing repos without understanding what they actually do
