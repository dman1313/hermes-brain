---
name: micro-saas-starter
description: Build a complete Flask-based micro-SaaS product with payments, landing page, scanner/certification tool, and deploy-ready structure. Use when Dwayne wants to build a new paid web service.
---

# Micro-SaaS Starter

Build a complete micro-SaaS product end-to-end: Flask backend, dark-themed landing page, payment integration, scanner/certification tool with upsell funnel, and Zeabur deployment.

## When to Use

Dwayne says "build me a site that does X and charges money" or "fire up the software team" for a new paid web product.

## Architecture

```
project/
├── app.py              # Flask app — routes, middleware, payments
├── checker.py           # Domain logic (scanner, certifier, validation)
├── requirements.txt     # flask, gunicorn, stripe, httpx, etc.
├── Procfile             # web: gunicorn app:app --bind 0.0.0.0:$PORT
├── templates/
│   ├── index.html       # Landing page — hero, scanner, pricing, CTA
│   ├── pay.html         # Payment page — Stripe + crypto
│   ├── success.html     # Post-payment confirmation
│   └── fix.html         # How-to guides (if applicable)
└── static/
    └── styles.css       # Dark theme, green accent, responsive
```

## Key Patterns

### 1. Flask App Structure (`app.py`)

- Content negotiation middleware via `@app.after_request` — auto-converts HTML to Markdown for AI agents. **Only set `Vary: Accept` on HTML responses** — never on static files or it fragments CDN caching. Always update `Content-Length` after Markdown transformation.
- `llms.txt` and `ai.txt` routes for agent discovery
- Schema.org JSON-LD injection in templates
- All routes return `render_template()` with `site_name`, `site_desc`, `site_url` as context
- Config via `os.environ.get()` — SITE_URL, STRIPE_SECRET_KEY, COINBASE_API_KEY, etc.
- **API hardening** (see `references/api-hardening-patterns.md`): rate limiting via `ratelimit.py`, CORS headers for badge.js embed, SSRF protection (block internal IPs), OPTIONS preflight handling, try/except error wrapping on scanner logic

### 2. Payment Integration

**Stripe (credit card):**
- Use Stripe Checkout Sessions — zero PCI burden
- `/api/create-checkout` POST endpoint → creates session → returns `session.url` for redirect
- `/webhook/stripe` POST endpoint for webhook events
- Needs: `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_WEBHOOK_SECRET`

**Crypto (Coinbase Commerce):**
- Use Coinbase Commerce hosted checkout — no wallet management
- `/api/create-crypto-charge` POST endpoint → creates charge → returns `hosted_url`
- Graceful fallback: if no API key, returns wallet address + USD amount for manual payment
- `/webhook/coinbase` POST endpoint for charge confirmed events
- Needs: `COINBASE_API_KEY`, `CRYPTO_WALLET` (BTC address fallback)

**Payment page (`pay.html`):**
- Two buttons: "Pay with Credit Card" (purple) and "Pay with Crypto" (orange)
- Loads Stripe.js via CDN
- Crypto fallback displays wallet address if Coinbase not configured
- Takes `?plan=` query param to pre-select tier

### 3. Scanner/Certification Tool

- Domain logic in `checker.py` — synchronous, no framework dependency
- Uses `httpx.Client` + `BeautifulSoup` for web checks
- Each check returns `CertCheck(name, status, detail, fix_guide)` 
- `FIX_GUIDES` dict maps check name → Markdown string with copy-paste code snippets
- Results page: collapsible `<details>` elements, FAILs open by default
- Upsell CTA: when `not certified`, show "Fix It For Me — $99" linking to `/pay`

### 4. Landing Page (`index.html`)

- Dark theme: `#0a0a0a` background, `#4ade80` green accent
- Sections: Hero → Scanner → Features Grid → Pricing → Testimonial → Footer
- Hero: green gradient text, badge, CTA buttons
- Pricing: 3-tier (Free/Certified/Enterprise), featured card highlighted
- Scanner form: URL input + certify button → shows results inline
- All "Get Certified" and "Fix It For Me" buttons link to `/pay?plan=`

### 5. Dwayne's Preferences

- **Immediate implementation:** When he says "make it available," "do it," or "yes" to adding a feature — build it immediately. Don't keep discussing options or pitching alternatives once he's given the go signal.
- **"Can people actually use this?"** This question means: make it publicly accessible — deploy, add a domain, expose it. Don't just answer yes/no.
- **Business layer matters:** Provide sales copy, pricing strategy, and competitive positioning alongside code
- **Crypto + credit card:** Always include both payment methods
- **Original ideas:** If the concept is new (first-mover), highlight that in the pitch
- **Landing page quality:** He called previous sites "look like shit" — invest in professional copy, clean design, and the side-by-side demo (user's site failing vs agent-ready version)
- **Separation of concerns:** His main site (humangood.ai) is a static HTML landing page with no Flask, no certification tool. The SaaS product lives in its own project/repo on its own subdomain. Don't mix them.

### 6. Sales Copy Patterns (Dwayne's Positioning)

When writing copy for Dwayne's products, use this framing:

**Core pitch structure:**
1. Name the wave before it hits — "AI agent traffic is at 2010 mobile levels right now"
2. Compare to a past shift everyone now accepts — mobile-responsive, SEO, SSL
3. Show the invisible loss — "agents visit your site and see garbage"
4. Position the product as cutting-edge positioning, not just a tool — "we track where the internet is going before it arrives. Our customers don't chase trends — they're already positioned when the wave hits."
5. Scarcity framing — "don't get penalized in 2027. Get certified now."

**The "always cutting edge" angle:** Frame the product as forward-positioning, not just a utility. The customer buys because they want to be early, not because they have a problem today. "The Next Wave of Traffic Isn't Human" is stronger than "Your site isn't readable by AI."

**Feature → Benefit mapping (use this format):**
For each feature, lead with "What happens without it" (the fear), then "With it" (the relief). Example for llms.txt:
- *Without llms.txt:* Agents land on your homepage and guess. They might read your privacy policy and think you're a law firm.
- *With it:* "This is who we are. Here's our docs. Here's our pricing." — instant context.

**The 7 Standards Framing:** When explaining a certification/audit product, frame each standard with three beats:
1. **What it is** — one sentence, plain English
2. **What happens without it** — the invisible cost, the fear
3. **With it** — the relief, often phrased as a quote from the site to the agent

This pattern converts dry technical checks into emotional stakes. Use it for landing page copy and investor pitches.

**Revenue model transparency:** When Dwayne asks "how much can I make," give honest tiered projections (conservative/target/optimistic) with ARR numbers. Include the honest caveat: new category = market creation required. He appreciates straight talk over hype.

**Funnel design:** The free scanner is top of funnel. Every FAIL result shows a "Fix It For Me — $99" CTA. Passing sites see no upsell. The `/fix` page is the self-service escape hatch. Sales flow: scan → fail → fix guide → "want us to handle it?" → pay page.

## Pitfalls

- Port conflicts: The VPS may have old Flask apps on port 5000. Use `PORT=8766` or similar for testing.
- Stripe webhooks need a public URL — Zeabur or tunnel required for local testing
- Coinbase Commerce requires manual verification of crypto payments (blockchain confirmations take minutes)
- `checker.py` must be synchronous (not async) for Flask — use `httpx.Client`, not `httpx.AsyncClient`
- **Vary header on all responses:** Setting `Vary: Accept` on every response (including static files) fragments CDN caches. Only set it on `text/html` responses.
- **Missing CORS:** The badge.js embed needs `Access-Control-Allow-Origin: *` on the API endpoint to work cross-origin.
- **SSRF via scanner:** The certification scanner makes outbound HTTP requests to user-supplied URLs. Block internal IPs (`localhost`, `127.0.0.1`, `10.*`, `192.168.*`, `172.16.*`) to prevent internal network scanning.
- **No error handling on scanner:** Wrap `certify_url()` in try/except — return 502 on failure, not 500.
- **Stale Content-Length:** After converting HTML to Markdown in the middleware, update `Content-Length` to the new byte size, otherwise the original HTML Content-Length is wrong.

## Deployment

**Option A: Zeabur** — Push to GitHub, point Zeabur at repo. Auto-detects Python from `requirements.txt` + `Procfile`. Set env vars in Zeabur dashboard.

**Option B: Cloudflare Tunnel** — Run Flask on VPS port, add subdomain to tunnel config, add DNS CNAME in Cloudflare dashboard. Faster iteration cycle (no git push). See `references/cloudflare-tunnel-deploy.md` for full setup.

## References

- `references/agent-ready-example.md` — Full Agent Ready project as reference
- `references/api-hardening-patterns.md` — Rate limiting, CORS, SSRF protection, error handling
- `references/cloudflare-tunnel-deploy.md` — Deploy behind Cloudflare Tunnel on custom subdomains
