---
name: web-to-llm-service
description: Convert websites and PDFs/CVs into clean markdown for LLMs, with llms.txt, INDEX.md, LLM-Friendly badge, Readiness Score, change detection, and Stripe billing. Sellable as a service.
version: 3.0.0
author: Dwayne Primeau / Human Good AI
license: MIT
metadata:
  hermes:
    tags: [service, llm, markdown, pdf, web-scraping, content-extraction, stripe, competitor-intelligence]

---

# Web-to-LLM Service v3

Turn any website into an LLM-ready content library. Includes badge, `llms.txt`, readiness score, change detection — and Stripe billing to sell it.

## v3 Improvements (April 2026)

### Multi-Strategy Extraction (Auto-Fallback)
The **critical fix**: v2's readability-lxml algorithm fails on Bootstrap/framework sites where content is distributed across many small `<section>` elements. MKIS got only 82 words from readability. v3 auto-detects and falls back:

| Strategy | When Used | Performance |
|----------|-----------|-------------|
| **readability** | Article/blog pages (high text density) | Fast, clean output |
| **section_text** | Bootstrap/Tailwind/framework sites (many sections) | 7.5x improvement on MKIS (82→615w) |
| **playwright** | JS-heavy SPAs (React, Vue, Angular) | Full JS rendering |

Auto-detection: if readability returns <100 words, automatically tries section_text. If HTML body is nearly empty (CSR shell), escalates to Playwright.

### Multi-Page Recursive Crawl
- `--recursive`: Follow internal links, respecting same-domain
- `--sitemap`: Discover all pages via sitemap.xml
- `--max-pages`: Cap crawl size (default 50)
- `--max-depth`: Limit crawl depth (default 3)
- Concurrent processing (4 workers)
- Polite crawling (0.5s delay between requests)

### Easy Customer Install Package
New command:
```bash
web-to-llm-v3 --package https://example.com/
```

Generates a ready-to-send zip in `~/agent-ready-packages/` with:
- `public/llm/*.md` — upload to `/llm/`
- `public/llms.txt` — upload to `/llms.txt`
- `snippets/html-head-sitewide.html` — copy into global `<head>`
- `snippets/badge.html` — optional footer badge
- `snippets/no-code-body-snippet.html` — fallback if the site only allows body embeds
- `robots-agent-ready-snippet.txt` — paste into robots.txt
- `README-INSTALL.md` — simple vendor instructions
- `install-checklist.md` — install/verification checklist
- `reports/agent-ready-report.json` — page inventory and generated URLs

MKIS trial package generated successfully:
`/home/ubuntu/agent-ready-packages/www.mkis.edu.my-agent-ready-20260429-065632.zip`

### Proper llms.txt (Jeremy Howard Spec)
v2 generated a non-standard llms.txt referencing local files. v3 follows the llmstxt.org spec:
```markdown
# domain.com
> Description
## Section Name
- [Page Title](https://actual-url): summary
```

### Real-World Trial: MKIS (mkis.edu.my)
| Metric | v2 | v3 |
|--------|----|----|
| Homepage words | 82 | 615 |
| Pages crawled | 1 | 33 |
| Total words | 82 | 15,697 |
| Time | 2s | 34s |
| Readiness score | A (85) | A (85) |

Strategy breakdown: 12 pages via readability, 21 via section_text (auto-fallback). Zero Playwright needed — site uses server-side Bootstrap, not JS rendering.
## The Full Output Library

```
~/.hermes/llm-reads/
├── INDEX.md                 ← LLMs read this FIRST (manifest)
├── llms.txt                 ← llmstxt.org standard (Jeremy Howard spec)
├── llm-friendly-badge.svg   ← Blue pill badge: "LLM-Friendly"
├── llm-readiness-badge.svg  ← "LLM Ready: A+ (92/100)" badge
├── readiness-report.json    ← Full 7-signal score breakdown
├── changes.log              ← Markdown.co-style diff tracking
└── page-slug-2026-04-28.md ← Individual page content
```

## Commands

```bash
web-to-llm https://example.com            # Convert + INDEX + llms.txt + score
web-to-llm https://example.com --deploy-badge   # Include the LLM-Friendly badge
web-to-llm ~/documents/cv.pdf             # PDF/CV support
web-to-llm --list                         # Browse library
web-to-llm --open 1                       # View entry by index
web-to-llm --serve 8080                   # Web UI

llm-badge index.html -o /llm/INDEX.md     # Inject badge + meta into HTML
llm-badge ~/my-site/                      # Batch all HTML files
llm-badge check index.html                # Check compliance
```

## Features Stolen from Competitors

### 1. llms.txt (from llmstxt.org / Jeremy Howard)
Every conversion generates `/llms.txt` following the emerging standard. Tells LLMs which pages to read and where the markdown versions live. Format:
```markdown
# Site Name
> LLM-optimized content from https://example.com

## Pages
- [Page Title](filename.md): Brief summary...

## Optional
- [INDEX.md](INDEX.md): Full library manifest
```

### 2. LLM Readiness Score (from AI-Signed)
Each site scored 0-100 across 7 signals:
- llms.txt present (15pts) — HTML headings (10pts) — Meta description (10pts)
- Schema.org data (15pts) — Content quality (15pts) — Robots.txt (10pts)
- Markdown library (25pts)

Generates grade badge (A+ through D) and JSON report. AI-Signed charges $5.99/mo for this.

### 3. Change Detection (from Markdown.co / "Digital Twin")
Every re-crawl logs a changes.log tracking word count differences:
```
page.md | 2026-04-28 | 1200 | first capture
page.md | 2026-05-28 | 1450 | 📈 +250 words added
```

### 4. LLM-Friendly Badge (from AI-Signed's trust badge concept)
Blue pill badge "LLM-Friendly" linking to INDEX.md, plus:
- `<meta name="llm-markdown" content="/llm-reads/INDEX.md">` in HTML head
- HTML comment block visible to any LLM parsing the page
- robots.txt directives guiding GPTBot/Claude-Web to the markdown dir

## Pricing (based on ContextKit's model)

| Tier | Setup | Monthly | Pages | Key Features |
|---|---|---|---|---|
| **Basic** 🌱 | **$99** | **$19/mo** | 50 | Web+PDF, INDEX.md, llms.txt, badge, score |
| **Pro** 🚀 | **$149** | **$49/mo** | 500 | All above + re-crawls, change detection, API, dashboard |
| **Enterprise** 🏢 | **$4,999** | **$499/mo** | Unlimited | Full site crawl, on-prem, SLA, custom branding |

ContextKit: $149 + $79/mo. You: $99 + $19/mo. Cheaper and faster.

## Stripe Billing (Self-Service)

```
web-to-llm-service/
├── app.py              ← Flask + Stripe Checkout, webhooks, portal
├── templates/
│   ├── pricing.html    ← 3-tier pricing with setup fee + monthly
│   └── success.html    ← Onboarding page
├── .env.example        ← Stripe key template
├── requirements.txt    ← Python deps
└── setup.sh            ← One-command setup
```

Run with: `cd ~/web-to-llm-service && bash setup.sh && python3 app.py`

### API Endpoints
| Route | Method | Purpose |
|---|---|---|
| `/` | GET | Pricing page |
| `/create-checkout-session` | POST | Stripe Checkout (setup + subscription) |
| `/create-payment-link` | POST | Shareable payment links |
| `/customer-portal` | POST | Stripe Customer Portal |
| `/webhooks/stripe` | POST | 5 event handlers (checkout, subscription, invoice) |
| `/admin/customers` | GET | Customer log |
| `/health` | GET | Status check |

## Crowdfund Token Extension

Do not lose the related product idea: **burnable API/LLM tokens for nonprofits and schools**.

Concept flow:
```text
Donor funds tokens → tokens allocated to nonprofit/school → organization uses AI/API gateway → token burns per successful request → usage is recorded transparently
```

How it connects:
- Agent-Ready Website Prep creates the clean markdown knowledge layer.
- The token gateway funds/meters the agents that consume and act on that knowledge.
- Schools/nonprofits can receive sponsored AI usage credits without managing provider accounts directly.
- Start with a database ledger and Stripe donations/sponsorships before considering blockchain.

Potential bundle:
- **Agent-Ready Website Prep** — installable `/llm/` + `/llms.txt` website layer.
- **AI Access Tokens** — donor-funded credits for LLM/API calls.
- **Gateway Add-on** — burns tokens per request and routes to the best provider.
- **Impact Dashboard** — tokens donated, spent, requests served, and use-case categories.

Canonical wiki note: `/home/ubuntu/wiki/concepts/agent-ready-website-prep.md`

## The Sales Pitch

> "Make your website **LLM-Ready**. When AI crawlers visit, they see the badge, find the llms.txt, read the meta tags, and automatically know to use the clean markdown version instead of your HTML. Your competitors aren't doing this yet. Get the badge first."

## Key Differentiators vs Competition

| Feature | You | ContextKit | AI-Signed | Markdown.co |
|---|---|---|---|---|
| llms.txt | ✅ | ✅ | ❌ | ❌ |
| INDEX.md manifest | ✅ | ❌ | ❌ | ❌ |
| LLM-Friendly badge | ✅ | ❌ | ✅ (trust badge) | ❌ |
| Readiness Score | ✅ | ❌ | ✅ ($5.99/mo) | ❌ |
| Change detection | ✅ | ❌ | ❌ | ✅ (enterprise) |
| PDF/CV support | ✅ | ❌ | ❌ | ❌ |
| Instant (not 48h) | ✅ | ❌ (48h manual) | ✅ | ✅ |
| Price | $99 + $19/mo | $149 + $79/mo | $5.99/mo | Enterprise |
