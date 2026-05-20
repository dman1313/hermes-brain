---
name: public-apis-directory
description: Search and discover free public APIs for integration into agent tools, projects, or MCP servers. Use when looking for APIs in a specific domain, when building tools that need external data sources, or when evaluating free API options for a project.
---

# Public APIs Directory

## Overview

Searchable index of 1000+ free public APIs from the [public-apis](https://github.com/public-apis/public-apis) repository. Cached locally at `~/.hermes/data/public-apis.md`. Use this to discover APIs, then wrap them as Hermes tools or MCP tools.

## When to Use

- "Find me a free weather API"
- "What APIs exist for cryptocurrency data?"
- "I need an API for <domain> — what's available?"
- Building a tool that needs external data and evaluating options

## How to Search

The list is a markdown file organized by category. Search it with `search_files`:

```bash
# Search by category or keyword
search_files(pattern="Weather", path="~/.hermes/data/public-apis.md", output_mode="content", context=2)
```

Categories include: Animals, Anime, Anti-Malware, Art & Design, Authentication, Blockchain, Books, Business, Calendar, Cloud, Continuous Integration, Cryptocurrency, Currency Exchange, Data Validation, Development, Dictionaries, Documents, Entertainment, Environment, Events, Finance, Food, Games, Geocoding, Government, Health, Jobs, Machine Learning, Music, News, Open Data, Open Source, Patent, Personality, Photography, Science, Security, Shopping, Social, Sports, Test Data, Text Analysis, Tracking, Transportation, URL Shorteners, Vehicle, Video, Weather

## API Entry Format

Each entry shows:
```
| API Name | Description | Auth | HTTPS | CORS | Link |
```

**Auth types:**
- `No` — No auth needed (easiest to integrate)
- `apiKey` — Requires API key (usually free tier available)
- `OAuth` — OAuth flow required (more complex)
- `User-Agent` — Requires custom User-Agent header
- `X-Mashape-Key` — Requires Mashape key

## Integration Path

### Level 1: curl-based tool (fastest)
For simple GET APIs, use `web_extract` or `curl` directly:
```python
# In execute_code or terminal
web_extract(urls=["https://api.example.com/data?param=value"])
```

### Level 2: MCP tool (reusable)
For APIs you'll use repeatedly, wrap as an MCP tool. See `native-mcp` skill.

### Level 3: Hermes skill (full integration)
For complex APIs with multiple endpoints, create a dedicated skill. See `write-a-skill`.

## Quick Integration Template (Python)

```python
import requests
import os

API_KEY = os.environ.get("API_KEY_NAME")
BASE_URL = "https://api.example.com/v1"

def call_api(endpoint: str, params: dict = None) -> dict:
    headers = {"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}
    resp = requests.get(f"{BASE_URL}/{endpoint}", params=params, headers=headers)
    resp.raise_for_status()
    return resp.json()
```

## Health Scanner

Run the concurrent health scanner to test every API link and produce a live/dead report:

```bash
python3 scripts/scan_public_apis.py
```

The scanner tests all 1,483 APIs with 20 concurrent connections at 8s timeout (~5-7 min). Produces:
- **stdout**: summary stats, category survival rates, ready-to-use APIs (no auth + alive)
- **file**: `~/.hermes/data/public-apis-scan.txt` — dead API list with failure reasons

Re-run periodically — APIs come and go. A scan from 2026-05-19 found 78% alive (1,159/1,483).

## Update the Cache

The list updates frequently. Refresh with:
```bash
curl -sL "https://raw.githubusercontent.com/public-apis/public-apis/master/README.md" \
  -o ~/.hermes/data/public-apis.md
```

## Pitfalls

1. **Free ≠ unlimited** — Check rate limits before building. Many free APIs throttle hard.
2. **Auth can change** — An API listed as "No" auth may add auth later. Always check the docs.
3. **Some are deprecated** — The list is community-maintained, not all entries are active. Test before committing (use the Health Scanner above).
4. **CORS = No = server-side only** — If CORS is "No," you can't call it from a browser; use a backend proxy or Hermes server-side.
5. **HTTPS = No = avoid** — Prefer HTTPS APIs. HTTP-only APIs are a security risk.
6. **Markdown table parsing is fragile** — The README uses non-standard table formatting (some rows have a trailing `[Go!](url)` link column, some don't; auth values may or may not be backtick-wrapped). The scanner handles both patterns but edge cases can slip through. If parsing seems off, visually spot-check a few entries against the raw markdown.
7. **Many dead APIs are Heroku free-tier casualties** — Heroku ended its free tier in 2022. APIs hosted on `*.herokuapp.com` are almost certainly dead. The scanner flags these automatically.
