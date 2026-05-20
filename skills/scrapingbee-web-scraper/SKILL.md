---
name: scrapingbee-web-scraper
description: Cloud-based web scraping via ScrapingBee REST API wrapper. Scrape any public URL with optional JS rendering, premium proxies, structured data extraction.
version: 1.0
---

# ScrapingBee Web Scraper

Scrape any public web page using ScrapingBee's API. Handles JS rendering, premium proxies, and structured data extraction.

## Prerequisites

- API key stored at `~/.hermes/scripts/scrapingbee.sh`
- Script at `~/.hermes/scripts/scrapingbee.sh`

## CLI Wrapper

```bash
~/.hermes/scripts/scrapingbee.sh <url> [options]
```

### Options

| Flag | Description | Credits |
|------|-------------|---------|
| (none) | Basic scrape (no JS rendering) | 5 |
| `--render-js` | Enable JavaScript rendering | 5+5=10 |
| `--premium-proxy` | Residential proxies for blocked sites | +5-20 |
| `--stealth-proxy` | Stealth/undetectable scraping | 75 |
| `--wait <ms>` | Wait for JS (max 12000ms) | varies |
| `--country <code>` | Country-specific proxy (e.g. US, FR) | varies |
| `--json` | Output as JSON object | same |
| `--extract-rules <json>` | CSS-selector based structured extraction | same |

### Structured Extraction

Use `--extract-rules` with a JSON rules object:

```json
{
  "headlines": {
    "selector": "h2",
    "type": "list",
    "output": {"text": "text"}
  },
  "main_article": {
    "selector": "article",
    "type": "text",
    "output": "text"
  }
}
```

## Common Use Cases

### Basic page scrape (fastest/cheapest, 5 credits)
```bash
~/.hermes/scripts/scrapingbee.sh "https://example.com"
```

### Scrape with JS rendering (10 credits)
```bash
~/.hermes/scripts/scrapingbee.sh --render-js "https://spa-site.com"
```

### Extract structured data (5 credits)
```bash
~/.hermes/scripts/scrapingbee.sh --json --extract-rules '{"links":{"selector":"a","type":"list","output":{"text":"text","href":"@href"}}}' "https://news.ycombinator.com"
```

### Blocked site with premium proxy
```bash
~/.hermes/scripts/scrapingbee.sh --premium-proxy --country US "https://site-that-blocks-scrapers.com"
```

## Integration with Hermes

Call via terminal tool:
```
terminal(command="~/.hermes/scripts/scrapingbee.sh --json 'https://target.com'", timeout=30)
```

## Credit Pricing

| Feature | Cost |
|---------|------|
| Basic scrape | 5 credits |
| + JS rendering | +5 credits |
| + Premium proxy | +5-20 credits |
| + Stealth proxy | 75 credits |
| + Wait time | up to +5 credits |

## Limits

- Max response: depends on plan
- Free tier typically 50-100 requests. Check ScrapingBee dashboard.
- JS rendering timeout: max 12000ms via `--wait`

## Pitfalls

- Very large pages may timeout (default 30s terminal timeout, increase with `timeout=60`)
- Some sites with aggressive anti-bot protection may need `--stealth-proxy` (expensive, 75 credits)
- CSS selectors in `--extract-rules` must match the rendered DOM after JS execution — if using `--render-js`, ensure the selector targets post-render elements
- URL must be properly URL-encoded (the wrapper handles this)
- The API key has limited credits — don't use for bulk scraping without checking remaining credits first
