---
name: system-objective-agent-ready
description: Build and deploy the System Objective Agent-Ready middleware service. Transforms standard websites into LLM-optimized environments with content negotiation, Markdown mirrors, llms.txt/ai.txt generation, and Schema.org JSON-LD injection. Use when asked to build, extend, or fix the System Objective project.
version: 1.0.0
---

# System Objective — Agent-Ready Middleware

## Overview

A FastAPI middleware service that makes any website "Agent-Ready" for LLM agents. Features:

1. **Content Negotiation** — `Accept: text/markdown` → automatic HTML→Markdown conversion
2. **Markdown Mirrors** — Every page gets a `.md` alternate with `rel="alternate"` link
3. **Agent Discovery** — `llms.txt` (site map for LLMs) + `ai.txt` (agent permissions)
4. **JSON-LD Schema** — Automatic Schema.org structured data (Organization, Article, FAQPage)
5. **Certification CLI** — `system-objective certify <url>` validated against 7 checks

## Project Location

`/home/ubuntu/system-objective/` — Python 3.11+, FastAPI, virtual env at `.venv/`

## Architecture

```
src/system_objective/
├── app.py                    # FastAPI app factory (create_app)
├── cli.py                    # Click CLI: serve + certify
├── middleware/
│   └── content_negotiation.py  # Pure ASGI middleware for Accept: text/markdown
├── converters/
│   └── html_to_markdown.py     # HTML→Markdown via html2text + BS4 pre-processing
├── injectors/
│   ├── html_injector.py        # inject_alternate_link, inject_agent_links
│   ├── link_header.py          # build_canonical_link_header, build_markdown_link_headers
│   └── schema_injector.py      # generate_organization/article/faq_schema, inject_jsonld, extract_jsonld
├── generators/
│   ├── llms_txt.py             # LLMSTxtConfig, PageEntry, generate_llms_txt
│   └── ai_txt.py               # AITxtConfig, AgentDirective enum, generate_ai_txt
└── certifier/
    └── checker.py              # CertStatus, CertCheck, CertReport, certify_url()
```

## Key APIs

### Content Negotiation Middleware
```python
from system_objective.middleware.content_negotiation import ContentNegotiationMiddleware
app.add_middleware(ContentNegotiationMiddleware)
```
Pure ASGI middleware. Intercepts `Accept: text/markdown` requests, converts HTML→Markdown, adds `Vary: Accept`.

### App Factory
```python
from system_objective.app import create_app
app = create_app(
    site_name="My Site",
    site_url="https://mysite.com",
    site_description="Description",
    llms_config=custom_llms_config,  # optional
    ai_config=custom_ai_config,      # optional
)
```

### Certification CLI
```bash
.venv/bin/python -m system_objective.cli certify https://example.com
```

### Certification Programmatic
```python
from system_objective.certifier.checker import certify_url, CertReport
report = await certify_url("https://example.com", timeout=30)
print(report.certified)  # True/False
```

## Test Suite

- **155 tests** total, all passing in < 1 second
- Run: `cd /home/ubuntu/system-objective && .venv/bin/pytest tests/ -v`
- Integration tests in `tests/test_app.py` (24 tests covering all endpoints)

## Project Locations

Two living implementations — don't confuse them:

| Project | Path | Type | Purpose |
|---------|------|------|---------|
| System Objective lib | `/home/ubuntu/system-objective/` | FastAPI + Click CLI | Reusable Python package, 155 tests |
| Agent Ready standalone | `/home/ubuntu/agent-ready/` | Flask + landing page | Deployable certification SaaS, `/certify` + `/api/certify` |

**CRITICAL: Keep projects SEPARATE.** The user's HumanGood.AI landing page (`dman1313/goodhuman`) is a standalone static site. Do NOT inject Agent Ready certification into it. Agent Ready is its own project, its own domain (agentready.ai), its own everything. Mixing unrelated projects → force-push restore.

## Variations

### Synchronous checker (for Flask/WSGI)
The standalone Flask app at `/home/ubuntu/agent-ready/checker.py` uses a **synchronous** `certify_url(url)` with `httpx.Client` (not `httpx.AsyncClient`). This avoids asyncio in WSGI. The FastAPI lib uses the async version. Both share the same 7-check logic.

### Payments Integration (Stripe + Crypto)
The Agent Ready Flask app includes full payment processing — see `micro-saas-starter` skill for the reusable pattern:

- `/pay?plan=certified|enterprise` — payment page with two buttons
- `/api/create-checkout` — Stripe Checkout Sessions (credit cards, $99/yr or $499/yr subscriptions)
- `/api/create-crypto-charge` — Coinbase Commerce hosted checkout (BTC, ETH, USDC). Falls back to manual wallet address display if no API key.
- `/webhook/stripe` + `/webhook/coinbase` — webhook handlers for payment confirmation
- `/success` — post-payment confirmation page
- **Env vars needed:** `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_WEBHOOK_SECRET`, `COINBASE_API_KEY`, `CRYPTO_WALLET`
- Without Stripe keys: graceful error message. Without Coinbase key: shows BTC wallet address + estimated amount.

### Fix Guides + Upsell Funnel (business conversion flow)
The `/certify` page converts failed scans into customers with a built-in support funnel:

1. **Failed checks auto-expand** — `<details open>` shows the fix guide inline (copy-paste code snippets for Python, Node.js, Nginx, Apache, HTML).
2. **"Fix It For Me" CTA** — green gradient box at the bottom of non-certified results: `$99 one-time setup` with a pre-filled `mailto:` link.
3. **Self-service escape hatch** — "I'll fix it myself →" links to `/fix` page with all 7 guides.
4. **Passing sites see no upsell** — only the green ✅ results, no CTA.

**Key implementation details:**
- `checker.py`: `FIX_GUIDES` dict maps check name → markdown fix guide. Each `CertCheck` carries a `fix_guide` field (populated for FAIL/WARN only).
- Template: `{% if not scan_result.certified %}` controls CTA visibility. `{% if c.status.value in ('FAIL', 'WARN') %}` controls fix guide display.
- API: `/api/certify?url=` returns `fix_guide` field for FAIL/WARN checks.
- `/fix` page: renders all `FIX_GUIDES` entries on a single page as a reference library.
- CSS: `.fix-guide` (bounded scroll), `.cta-fix` (green gradient border), `.check-summary` (flex row with `details`/`summary`).

See `references/fix-guides-cta-pattern.md` for the full reference.

## Pitfalls

- **Content negotiation is pure ASGI middleware** — NOT Starlette BaseHTTPMiddleware (Starlette 1.0 breaks body modification with BaseHTTPMiddleware). The middleware uses an interposed `send` callable pattern.
- **For Flask/WSGI apps**, use `@app.after_request` instead of ASGI middleware. See `references/flask-content-negotiation.md` for the recipe.
- **When deploying to PaaS** (Zeabur, Render, etc.), bundle `html_to_markdown.py` and `checker.py` into a local `agent_ready/` package instead of importing from `system_objective`. Editable installs (`pip install -e .`) don't work on most PaaS platforms.
- **Zeabur won't auto-redetect service type** when switching languages (Node.js↔Python, static↔Flask). Must manually change it in the dashboard BOTH directions. After a force-push restore, Zeabur may keep serving the old deployment until the service type is corrected and a redeploy is triggered. See `references/zeabur-deployment.md`.
- **Certifier may fail locally** with `peer closed connection` on Markdown negotiation check when running against uvicorn in single-worker mode alongside async httpx. Passes on properly deployed servers.
- **Git restore by timestamp:** User uses `<time>` as restore points e.g. "restore from GitHub at 1 pm today." Find the commit with `git log --format="%h %ci %s" -20`, match the timestamp, then `git reset --hard <hash>` + `git push --force origin main`. After force-push, Zeabur must be reconfigured to the correct service type before redeploy.
- **HTML injection order matters** — inject_agent_links before inject_jsonld. The BeautifulSoup parser normalizes HTML; subsequent injections operate on the normalized output.
- **Schema deduplication uses compact JSON** — `json.dumps(schema, separators=(",", ":"))` for comparison. Tests must generate seed HTML with the same compact format.

## Development Workflow

```bash
cd /home/ubuntu/system-objective
source .venv/bin/activate
pytest tests/ -v          # Run all tests
system-objective serve --reload  # Dev server
```

## Wiki
- [[system-objective]] — Full project documentation

## References
- `references/flask-content-negotiation.md` — Flask `@app.after_request` recipe for content negotiation (simpler than ASGI middleware for WSGI apps)

## Related Skills
- [[software-factory]] — Reference architecture used for multi-agent build
- [[subagent-driven-development]] — Pattern used for parallel implementation
