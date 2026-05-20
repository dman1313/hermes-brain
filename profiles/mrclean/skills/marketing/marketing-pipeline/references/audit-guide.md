# Marketing Audit Guide — Hermes Reference

Hermes-side reference for the 5-agent parallel marketing audit pattern.
When the user runs `/marketing audit <url>`, dispatch 5 subagents in
parallel, then assemble the composite report.

---

## 1. 5-Agent Parallel Audit Pattern (Flagship)

`/marketing audit <url>` launches 5 parallel subagents:

| Subagent | Evaluates | Pages to Fetch |
|----------|-----------|----------------|
| market-content | Content quality, messaging, copy | Homepage, About, Pricing, 1 feature page, 1 blog post |
| market-conversion | CRO, funnels, signup flows | Homepage, landing pages, Pricing, Signup/Contact, forms |
| market-competitive | Competitive positioning | Target homepage + top 3 competitor homepages |
| market-technical | Technical SEO, site architecture | Target URL HTML, /robots.txt, /sitemap.xml, key pages |
| market-strategy | Brand trust, pricing, growth | Homepage, About, Pricing, blog |

Subagents run simultaneously — no ordering dependencies. Each writes its
analysis into the composite report under its own section header.

---

## 2. Marketing Score Methodology (0-100 Composite)

| Category | Weight | Source |
|----------|--------|--------|
| Content & Messaging | 25% | market-content |
| Conversion Optimization | 20% | market-conversion |
| SEO & Discoverability | 20% | market-technical |
| Competitive Positioning | 15% | market-competitive |
| Brand & Trust | 10% | market-strategy |
| Growth & Strategy | 10% | market-strategy |

Each subagent scores its dimension 0-10. Multiply by 10 to get 0-100.

**Composite** = Content*.25 + Conversion*.20 + SEO*.20 + Competitive*.15
+ Brand*.10 + Growth*.10

Display as "Marketing Score: XX/100" in the executive summary.

---

## 3. Business Context Detection

Before dispatching, classify the business type from homepage content:

| Type | Focus Areas |
|------|-------------|
| SaaS/Software | Trial-to-paid, onboarding, feature pages, pricing tiers |
| E-commerce | Product pages, cart abandonment, upsells, reviews |
| Agency/Services | Case studies, portfolio, contact forms, trust signals |
| Local Business | Google Business Profile, local SEO, reviews, directions |
| Creator/Course | Lead magnets, email capture, testimonials, community |
| Marketplace | Two-sided messaging, supply/demand, trust, fees |

Detection: scan homepage for telltale phrases like "sign up free" (SaaS),
"shop now" (e-commerce), "book a consultation" (agency), "enroll" (creator).
If ambiguous, classify by value proposition language and CTA verbs.

---

## 4. Per-Agent Instructions

### 4a. market-content — Content & Messaging

**Scoring dimensions (0-10 each):**
- Headline Clarity: Communicates value in <5 seconds, specific not generic
- Value Proposition: Differentiated, backed by numbers/outcomes, answers "why you?"
- Copy Persuasion: Benefits > features, customer language, emotion + logic
- Content Depth: Comprehensive features, educational content (blog, guides)
- CTA Effectiveness: Value-driven text, well-placed, clear primary vs secondary

**Output section template:**
```
## Content & Messaging Analysis
### Overall Score: X/10
### Dimension Scores [table: Dimension | Score | Key Finding]
### Top Wins [3 items with quoted examples]
### Critical Fixes [3 items: Issue -> Specific recommendation]
### Before/After Rewrites [3 rewrites with Before/After/Why]
### Missing Elements [bullet list]
```

**Rules**: Quote specific copy. Every fix includes concrete rewrite.
Score honestly. Prioritize by revenue impact.

### 4b. market-conversion — Conversion Optimization

**Scoring dimensions (0-10 each):**
- CTA Strategy: Value-driven text, visual hierarchy, placement, mobile
- Social Proof: Testimonials (named/photos/companies), logos, case studies, numbers, badges
- Friction (higher = less friction): Steps to convert, form fields, payment friction
- Trust Signals: Security badges, privacy/terms, money-back guarantee, contact access
- Urgency & Scarcity: Limited-time offers, social proof urgency — must be authentic

**Funnel leak map**: Awareness -> Interest -> Consideration -> Intent -> Conversion.
Per leak: severity (Critical/High/Medium/Low), revenue impact, fix.

**A/B tests**: 3-5 "If we [change], then [metric] improves because [reason]".

**Output section template:**
```
## Conversion Optimization Analysis
### Overall Score: X/10
### Dimension Scores [table]
### Conversion Path Map [step-by-step]
### Funnel Leaks [table: Leak Point | Severity | Issue | Fix]
### Quick CRO Wins [3 items]
### A/B Test Hypotheses [3-5 items]
### Missing CRO Elements [bullet list]
```

**Rules**: Trace actual path. Every recommendation ties to a measurable
metric. Include % impact estimates. No dark patterns.

### 4c. market-competitive — Competitive Positioning

**Competitor discovery**: Search for "[category] alternatives", "[brand] vs",
"best [category]". Identify 3-5 competitors (direct + aspirational).

**Scoring dimensions (0-10 each):**
- Positioning Clarity: Distinguishable in 10 seconds?
- Pricing Competitiveness: Transparent, aligned with buyers
- Feature Messaging: Differentiators highlighted prominently
- Market Awareness: Comparison pages, "why us" section
- Content Authority: Blog, case studies, thought leadership depth

**Opportunity areas**: Positioning gaps, content gaps, feature messaging
gaps, alternative page opportunities, switching narratives.

**Output section template:**
```
## Competitive Positioning Analysis
### Overall Score: X/10
### Competitors [table: Competitor | Category | Strength | Weakness]
### Positioning Comparison [table: Dimension x Target vs Competitors]
### Dimension Scores [table]
### Opportunities [3 items with specific actions]
### Recommended Actions [checkbox list]
```

**Rules**: Fetch competitor homepages. Be objective. Every competitor
weakness = marketing angle. Look for messaging gaps in the market.

### 4d. market-technical — Technical SEO & Discoverability

**Scoring dimensions (with sub-weights):**
- Page Structure (25%): Title 50-60 chars, meta 150-160 chars + CTA, H1 unique, H2-H6 hierarchy, alt text, URL, canonical
- Crawlability (20%): robots.txt, sitemap.xml, noindex, internal links, orphan pages
- Performance (15%): Page size, render-blocking, lazy loading, CDN, compression
- Content Architecture (20%): Navigation, clicks to key pages, blog organization, freshness, internal linking
- Schema & Tracking (20%): GA4/GTM, Meta Pixel, LinkedIn, cookie consent, JSON-LD (Organization, Website, Product, FAQ, Review, Breadcrumb, Article)

**Output section template:**
```
## Technical Marketing Analysis
### Overall Score: X/10
### Dimension Scores [table]
### SEO Quick Wins [3 items with example meta/titles]
### Technical Issues [table: Issue | Severity | Impact | Fix]
### Tracking Setup [table: Tool | Status | Notes]
### Schema Markup [table: Schema Type | Present | Recommendation]
### Content Architecture [bullet list]
```

**Rules**: Check actual HTML source. Inspect robots.txt + sitemap.xml.
Prioritize by revenue impact, not technical correctness.

### 4e. market-strategy — Brand, Pricing & Growth

**Brand & Trust (0-10 each):**
- Brand Consistency: Visual + messaging consistency, design polish
- Trust Architecture: About page quality, contact info, social proof, privacy
- Authority Signals: Thought leadership, press, awards, community

**Growth & Strategy (0-10 each):**
- Pricing Strategy: Transparency, free/trial, Good-Better-Best, upsell paths
- Acquisition Channels: Diversification, content, SEO, social, paid, referral
- Retention & Expansion: Onboarding, community, upgrades, newsletter, help center

**Revenue tiers**:
- Quick Wins (1-2 wks): Pricing tweaks, CTA changes, social proof additions
- Medium-Term (1-3 mo): Content expansion, email sequences, competitive pages
- Strategic (3-6 mo): New channels, PLG, partnerships, community

**Output section template:**
```
## Brand & Growth Strategy Analysis
### Brand & Trust Score: X/10 | Growth & Strategy Score: X/10
### Brand Assessment [table: Dimension | Score | Key Finding]
### Growth Assessment [table: Dimension | Score | Key Finding]
### Revenue Opportunities [3 tiers: Effort | Impact | Timeline]
### Pricing Analysis [structure, strengths, weaknesses, recommendation]
### Channel Strategy [active channels, underutilized, recommended next]
```

**Rules**: Frame through revenue lens. Identify the single biggest growth
lever. Adjust recommendations by business type.

---

## 5. Output Standards (All Agents)

1. **Actionable**: Every recommendation must be implementable from the
   instruction alone. Not "improve the headline" but "Change headline from
   'We help businesses grow' to 'Double your demo-to-close rate in 30 days'."

2. **Prioritized by impact**: Rank High/Medium/Low. High = directly affects
   conversion/revenue. Medium = improves experience. Low = nice to have.

3. **Revenue-focused**: Connect every suggestion to business outcomes.
   Phrase as "This could increase conversion by X%" or "Adds Y revenue/mo."

4. **Example-driven**: Top 3 critical fixes include before/after copy.
   Quote current copy, show improved version, explain why it's better.

5. **Client-ready**: Professional tone. No raw data dumps. Executive summary
   on top. Reports presentable without editing.

---

## 6. Composite Report Assembly

After all 5 subagents return, assemble `MARKETING-AUDIT.md`:

```
# Marketing Audit Report
**URL**: [url] | **Date**: [date] | **Type**: [business type]

## Executive Summary
- Marketing Score: [composite]/100
- Top 3 strengths (from wins across agents)
- Top 3 critical issues (from critical fixes)
- Single biggest growth recommendation

## Marketing Score Breakdown
| Category | Score | Weight | Weighted |
|----------|-------|--------|----------|
| Content & Messaging | X/100 | 25% | X |
| Conversion Optimization | X/100 | 20% | X |
| SEO & Discoverability | X/100 | 20% | X |
| Competitive Positioning | X/100 | 15% | X |
| Brand & Trust | X/100 | 10% | X |
| Growth & Strategy | X/100 | 10% | X |
| **Composite** | | **100%** | **X/100** |

## [market-content section — full content analysis]
## [market-conversion section — full conversion analysis]
## [market-competitive section — full competitive analysis]
## [market-technical section — full technical analysis]
## [market-strategy section — full brand & growth analysis]

## Consolidated Action Plan
### Critical (This Week) [3-5 highest impact items]
### High Priority (This Month) [5-8 items]
### Medium Priority (This Quarter) [remaining items]
```

---

## 7. Quick Snapshot (`/marketing quick`)

60-second assessment. NO subagents. Fetch homepage only. Output <30 lines
directly to terminal (no file).

**Evaluate**: Headline clarity (1-10), CTA strength (1-10), Value prop
clarity (1-10), Trust signals (1-10), Mobile readiness (1-10).

```
## Marketing Quick Snapshot
**URL**: [url] | **Type**: [business type]

| Element | Score | Status |
|---------|-------|--------|
| Headline | 7/10 | Clear but generic |
| CTA | 5/10 | "Get Started" too vague |
| Value Prop | 6/10 | Differentiated unproven |
| Trust | 4/10 | No testimonials visible |
| Mobile | 8/10 | Responsive design present |

**Top 3 Wins**: [...] (one line each)
**Top 3 Fixes**: [...] (one line each, specific)

**Score: [avg]/10 | Single biggest lever: [one line]**
```

---

## 8. Key Rules (All Modes)

- Always fetch actual page content — never hallucinate or assume
- Quote specific copy from the site in all analysis
- Business context detection runs before any analysis
- Scores are honest, not inflated
- Every recommendation must be implementable from the instruction
- Before/after examples required for top 3 critical fixes
- Revenue impact estimates encouraged ("could increase conversions 15-20%")
