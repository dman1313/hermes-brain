# Agent Ready — Full Reference Implementation

This is the canonical micro-SaaS built with this pattern. Located at `/home/ubuntu/agent-ready/`.

## Files (991 lines, 39KB)

- `app.py` (153 lines) — Flask app with content negotiation, scanner routes, payment endpoints, agent discovery files, webhook handlers
- `checker.py` (334 lines) — Synchronous certification engine with 7 checks and per-check fix guides (copy-paste code snippets)
- `requirements.txt` — flask, gunicorn, httpx, beautifulsoup4, markdownify, lxml, stripe
- `Procfile` — `web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 2`
- `templates/index.html` (210 lines) — Landing page: hero, scanner with results + fix guides + CTA, features grid, 3-tier pricing, testimonial, footer
- `templates/pay.html` — Payment page: Stripe Checkout button + Coinbase Commerce button + crypto wallet fallback
- `templates/fix.html` (72 lines) — Dedicated fix guides page with all 7 guides
- `templates/success.html` — Post-payment confirmation page
- `static/styles.css` (215 lines) — Dark theme, green accent, responsive, results display, CTA styling

## Payment Integration Details

**Stripe:**
- `/api/create-checkout` — POST with `{"plan": "certified|enterprise"}` → returns `{"url": "https://checkout.stripe.com/..."}`
- Creates subscription with yearly interval
- Webhook at `/webhook/stripe` handles `checkout.session.completed`

**Coinbase Commerce:**
- `/api/create-crypto-charge` — POST with `{"plan": "..."}` → returns `{"url": "https://commerce.coinbase.com/..."}`
- Fallback mode (no API key): returns wallet address + BTC estimate for manual payment
- Webhook at `/webhook/coinbase` handles `charge:confirmed`

## 7 Certification Standards

1. **llms.txt accessible** — GET /llms.txt returns 200
2. **Markdown negotiation** — Accept: text/markdown returns text/markdown content
3. **Alternate link tag** — `<link rel="alternate" type="text/markdown">` in HTML head
4. **JSON-LD structured data** — Valid schema.org JSON-LD script tag
5. **Vary header** (warning) — Vary: Accept response header
6. **Link canonical header** (warning) — Link: rel="canonical" in markdown response
7. **ai.txt present** (warning) — GET /ai.txt returns 200

Certification passes if all 4 required checks pass (1-4). Warnings don't block certification.

## Sales Pitch (used on site)

"AI agents are browsing the web on behalf of humans. If your site is a wall of HTML divs, agents skip right past you. This is the mobile-responsive moment for AI — the sites that get agent-ready now capture years of traffic."

## Running Locally

```bash
cd /home/ubuntu/agent-ready
pip install -r requirements.txt
PORT=8766 python app.py
# → http://localhost:8766
```
