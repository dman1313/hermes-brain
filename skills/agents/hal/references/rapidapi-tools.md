# RapidAPI Tools & External API Keys

## Active Keys

### ScrapingBee
- **Key:** `0F4N4KIP50U1G9EEI30C16PSZH0NG1HCVW13RC7EWHURLA0L6DX06QFNSO8IFOZ2FASIK9WM4DHSWKYB`
- **Endpoint:** `https://app.scrapingbee.com/api/v1/`
- **Pricing:** 5 credits per request (basic, no JS render). Freemium tier.
- **Status:** Tested working 2026-05-14. Scraped Hacker News front page successfully.
- **Usage:** Pass `?api_key=KEY&url=TARGET` params. Returns rendered HTML. Use `extract_rules` query param (URL-encoded JSON) for structured extraction.
- **Pro tip:** Hacker News and similar sites need `render_js=false` (basic mode). JS-heavy sites need `render_js=true` (5 credits) or `premium_proxy=true` (10-25 credits) or `stealth_proxy=true` (75 credits).

### RapidAPI (Nokia API Hub)
- **Key:** `2c94489ce3mshd675512363df454p1b3228jsn3e6cf4b70215`
- **MCP Host:** `mcp.rapidapi.com`
- **Status:** Key authenticates. Each API on the marketplace needs individual subscription enrollment at `console.rapidapi.com` (even free tiers). Not yet subscribed to any specific APIs.
- **Usage:** Can either use MCP protocol with `mcp.rapidapi.com/sse`, or direct REST calls through api gateway:
  ```bash
  curl -H "x-rapidapi-key: $KEY" -H "x-rapidapi-host: $HOST" "https://$HOST/v1/endpoint"
  ```

## Tier 1 Recommendations (Subscribe if needed)

| API | Why | Pricing |
|-----|-----|---------|
| ScrapingBee | Web scraping for research & competitive intel | Already have direct key |
| The Old Bird | Twitter/X API for @humangoodai | Freemium |
| ZeroBounce | Email verification for newsletters | Freemium |
| SendGrid | Email delivery (alternative to Gmail SMTP) | 100/day free |
| MyMemory | Translation fallback | Free |

## General Approach for New APIs

1. Check if already configured here
2. Try the direct key/endpoint with `terminal` + `curl`
3. If it's via RapidAPI marketplace, need subscription -> flag to Dwayne
4. If it's a direct API (like ScrapingBee), save the key in memory
5. If the API will be used regularly, suggest wrapping as a Hermes tool or skill reference
