---
name: competitor-teardown-methodology
description: Systematic approach to identifying competitors, extracting their best features, and building superior versions into your product. Used for web-to-llm service vs ContextKit, AI-Signed, Markdown.co, llmstxt.org.
version: 1.0.0
author: Dwayne Primeau
license: MIT
metadata:
  hermes:
    tags: [sales, competitor-intelligence, product-development, strategy]
---

# Competitor Teardown & Feature Steal Methodology

A repeatable process for finding competitors in any space, extracting their best ideas, and building them into your product faster/cheaper/better.

## Step 1: Landscape Discovery

Search across multiple angles:

```python
# Pattern:
web_search("keyword related to YOUR service")
web_search("competitor alternative to YOUR service")
web_search("'keyword' badge website service")
web_search("keyword API markdown LLM")
```

**For web-to-llm we searched:**
- "LLM friendly badge website service"
- "convert website to markdown for LLM service"
- "llms.txt standard"
- "AI readiness checker website"

## Step 2: Deep Dive Each Competitor

For each competitor found:
1. `web_extract(url)` — get full page content
2. Note their:
   - Pricing model (one-time? monthly? per-page?)
   - Feature list (what do they highlight?)
   - Differentiators (what do they claim is unique?)
   - Badges/badges/trust signals
   - Pain points they solve

## Step 3: Extract What Works

From each competitor, identify:

| Competitor | What to steal | How to improve |
|---|---|---|
| llmstxt.org | `/llms.txt` spec standard | Auto-generate with every conversion |
| AI-Signed | Trust score 0-100 + grade badge | Score across LLM-specific signals, not generic trust |
| ContextKit | One-time setup + monthly pricing model | Cheaper ($99+$19 vs $149+$79) + instant delivery |
| Markdown.co | Change detection / "Digital Twin" | Simple word-count diff log vs their complex system |

## Step 4: Build Faster & Cheaper

Key principle: **Your version doesn't need to be better — it needs to be good enough and cheaper.**

- ContextKit takes 48 hours manual → yours is instant automated
- AI-Signed charges $5.99/mo for scoring → yours is included
- Markdown.co change detection is enterprise-only → yours is in every plan

## Step 5: Update Pricing

Use ContextKit's model as the reference:
1. Their one-time setup fee → your setup fee (slightly lower)
2. Their monthly → your monthly (significantly lower)
3. Their enterprise → your enterprise (comparable)

## Step 6: Competitive Comparison Table

Build a table for your sales page:

| Feature | You | Competitor A | Competitor B |
|---|---|---|---|
| Core feature | ✅ | ✅ | ❌ |
| Your unique feature | ✅ | ❌ | ❌ |
| Price | $$ | $$$ | $$ |

## Trigger Conditions

Use this skill when:
- User asks "Is anyone else doing this?"
- User says "Rip off their ideas" or "Steal from competitors"
- Building a new service and need to know the market
- Need to set pricing for a new offering
- Want to differentiate in a competitive space
