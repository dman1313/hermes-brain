---
name: marketing-pipeline
description: |
  End-to-end marketing asset pipeline. Takes product/brand input and produces:
  landing pages, hero images, social media graphics, product demo videos, and
  brand design systems. Uses Garden Skills design philosophy (anti-slop,
  placeholder-before-fake, stunning-not-functional).
  Trigger when user asks to "build marketing assets," "create landing page,"
  "generate product visuals," "make a pitch deck," or "build complete brand package."
version: 1.1.0
author: Hermes Agent (adapted from ConardLi/garden-skills design patterns)
license: MIT
metadata:
  hermes:
    category: marketing
    tags: [marketing, landing-page, design, branding, image-generation, video]
---

# Marketing Pipeline — End-to-End Asset Orchestrator

Trigger this skill when a user asks to build marketing assets, create a landing page, generate product visuals, produce a brand package, or craft a video demo. The pipeline produces a complete output package under `./marketing-output/<project-slug>/` with a landing page (single-file HTML), a design system (CSS tokens + brand board), image prompts (for external AI image tools), and an optional video script.

---

## 1. Overview

**What this skill does:**  
Orchestrates 7 sequential phases (-1 through 5) that transform a product/brand description — or audit an existing website — into production-ready marketing assets, copy, email sequences, and audited reports. Each phase delegates to a focused subagent loaded with the appropriate reference guide.

**When to use it:**  
- User says "build marketing assets for my product"  
- User says "create a landing page and visuals"  
- User says "generate a complete brand package"  
- User says "audit this website" (`/marketing audit <url>`)  
- User says "generate email sequences" or "write copy for my landing page"  

**What it produces:**  
```
marketing-output/<project-slug>/
  MARKETING-AUDIT.md          # Phase -1: scored audit (website mode)
  brand-brief.md              # Phase 0: structured brief
  design-system.md            # Phase 1: design tokens & decisions
  brand-board.html            # Phase 1: single-file brand board
  landing-page.html           # Phase 2: single-file landing page
  prompts/                    # Phase 3: image prompts
    hero.md
    social.md
    mockup.md
    feature.md
  video/                      # Phase 4: (optional) video assets
    script.md
    outline.md
  EMAIL-SEQUENCES.md          # Phase 5: email sequences (optional)
  COPY-SUGGESTIONS.md         # Phase 5: copy suggestions (website mode)
```

**Core principles (from Garden Skills):**
- **Placeholders before fakery** — use `[icon]`, `[image: description]`, `[data: ask user]` instead of fabricated content
- **Stunning, not functional** — visual quality target is Dribbble/Behance showcase level
- **Anti-AI-slop** — no purple-pink gradients, no emoji abuse, no Inter/Roboto, no fake testimonials
- **Every subagent gets the FULL reference guide** — never summarize, always pass the complete `.md`

---

## 2. Quick Start

Minimal invocation:

```
User: "Build marketing assets for a project management app called 'FlowSync'"

You (Hermes):
1. Phase 0: Intake → produce brand-brief.md
2. Phase 1: Design System → produce design-system.md + brand-board.html
3. Phase 2: Landing Page → produce landing-page.html
4. Phase 3: Visual Assets → produce prompts/hero.md, social.md, mockup.md, feature.md
5. Phase 4: Video Script (ask user if needed) → produce video/script.md + video/outline.md
```

---

## 3. Pipeline Phases

### Phase -1: Website Audit (Parallel Subagents)

**Goal:** Run a comprehensive marketing audit of an existing website using 5 parallel subagents.

**Trigger:** `/marketing audit <url>` or user says "audit this website."

**Procedure:**

1. Detect business type from the URL content (SaaS, E-commerce, Agency, Local Business, Creator/Course, Marketplace)
2. Launch 5 parallel subagents, each loaded with `references/audit-guide.md`:
   - **market-content**: Content quality, messaging, copy effectiveness
   - **market-conversion**: CRO, funnels, landing pages, signup flows  
   - **market-competitive**: Competitive positioning, market landscape
   - **market-technical**: Technical SEO, site architecture, page speed
   - **market-strategy**: Brand trust, pricing, growth opportunities
3. Compose a weighted Marketing Score (0-100) from all 5 subagent outputs
4. Save composite report to `marketing-output/<project-slug>/MARKETING-AUDIT.md`

**Scoring weights:**
| Category | Weight | Source Agent |
|----------|--------|-------------|
| Content & Messaging | 25% | market-content |
| Conversion Optimization | 20% | market-conversion |
| SEO & Discoverability | 20% | market-technical |
| Competitive Positioning | 15% | market-competitive |
| Brand & Trust | 10% | market-strategy |
| Growth & Strategy | 10% | market-strategy |

**Quick Snapshot:** `/marketing quick <url>` — 60-second assessment, no subagents, terminal output only (under 30 lines). Fetch homepage, evaluate headline/CTA/value prop/trust/mobile, output scorecard with top 3 wins and fixes.

**Quality gate:**
- [ ] All 5 subagent outputs collected
- [ ] Composite score calculated with weighted formula
- [ ] Executive summary present (2-3 paragraphs)
- [ ] Top 5 prioritized action items listed
- [ ] Report saved to MARKETING-AUDIT.md

**Post-audit flow:** After audit completes, the scores and findings feed into Phase 0 (brand-brief.md enriched with audit data) and Phase 5 (copy suggestions informed by audit scores).

---

### Phase 0: Intake — Brand Brief

**Goal:** Gather minimum viable product info and produce `brand-brief.md` from `templates/brand-brief-template.md`.

**Procedure:**

1. Ask the user for:
   - **Product name** (required)
   - **Product category / industry** (required — e.g., SaaS, CPG, fintech)
   - **1-2 sentence pitch** (required — what does it do, for whom)
   - **Target audience** (optional — default to "early adopter professionals in [industry]")
   - **Brand personality** (optional — default to "modern, trustworthy, approachable")
   - **Primary color preference** (optional — default to a derived palette using the brand hue)
   - **Competitors** (optional — skip unless user volunteers)

2. Merge answers into the template. Template fields use `{field name="..." default="..."}` notation. Fill all fields. Leave no `TODO` markers.

3. Save to `marketing-output/<project-slug>/brand-brief.md`.

**Smart defaults policy:** If only product name is given, set:
- industry → "SaaS / Technology"
- pitch → "A [product name] tool that helps [default audience] achieve [default outcome]"
- audience → "professionals in technology and business"
- personality → "modern, trustworthy, approachable"
- color → use `oklch()` with a derived hue from the product name's first letter (A=0, B=30, C=60, D=90, E=120, F=150, G=180, H=210, I=240, J=270, K=300, L=330, M=0, N=30, O=60, P=90, Q=120, R=150, S=180, T=210, U=240, V=270, W=300, X=330, Y=0, Z=30)

**Quality gate:** Verify all template fields are filled. No raw `{...}` syntax remains in output.

---

### Phase 1: Design System — Tokens + Brand Board

**Goal:** Produce `design-system.md` (design tokens & decisions) and `brand-board.html` (single-file brand board HTML).

**Subagent dispatch:**

```
DISPATCH subagent with:
  task: "Build a design system and brand board for the product in brand-brief.md"
  context_files:
    - marketing-output/<project-slug>/brand-brief.md
  reference_guides:
    - references/design-engineer-guide.md  (FULL content)
  outputs:
    - marketing-output/<project-slug>/design-system.md
    - marketing-output/<project-slug>/brand-board.html
```

**design-system.md** must contain:
- Color palette: primary, secondary, neutral, accent — expressed in `oklch()`
- Typography: heading font, body font (avoid Inter/Roboto/system-ui)
- Spacing system: base unit and multiples
- Border-radius strategy
- Shadow hierarchy (elevation 1-5)
- Motion style: easing curves, duration, trigger types
- Rationale for each decision

**brand-board.html** must:
- Be a single, self-contained HTML file (inline CSS, no external dependencies)
- Include: logo zone (brand name in text + geometric shape per placeholder philosophy), color swatches with hex/oklch values, typography specimens, spacing scale visualization, application mockup area (`[image: brand application mockup]`)
- Follow the Design Engineer Guide's anti-AI-slop checklist: no purple-pink gradients, no Inter/Roboto, no emoji as icons, no SVG-drawn graphics as substitute for real assets
- Include a Tweaks panel (bottom-right) with at least 2 toggles (e.g., light/dark mode variant, accent color shift)

**Quality gate:**
- [ ] oklch() colors derived from brand-brief hue — no invented hues
- [ ] No Inter, Roboto, Arial, Fraunces, system-ui in font stack
- [ ] No purple-pink-blue gradient backgrounds
- [ ] No emoji as icon substitutes
- [ ] All placeholders marked `[icon]`, `[image: description]`
- [ ] brand-board.html renders standalone (open in browser, no errors)
- [ ] Tweaks panel present with ≥ 2 options

---

### Phase 2: Landing Page — Single-File HTML

**Goal:** Produce `landing-page.html` — a single-file, production-ready landing page.

**Subagent dispatch:**

```
DISPATCH subagent with:
  task: "Build a single-file landing page HTML from the brand brief and design system"
  context_files:
    - marketing-output/<project-slug>/brand-brief.md
    - marketing-output/<project-slug>/design-system.md
  reference_guides:
    - references/design-engineer-guide.md  (FULL content)
  outputs:
    - marketing-output/<project-slug>/landing-page.html
```

**Requirements:**
- Single-file HTML with inline CSS — zero external dependencies
- CSS custom properties on `:root` for all design tokens (colors, fonts, spacing, radii, shadows)
- Fluid typography with `clamp()` — responsive across mobile/tablet/desktop
- CSS Grid + Flexbox layout; container queries for component-level responsiveness
- `text-wrap: pretty` on all text blocks
- Accessible: `@media (prefers-color-scheme)` and `@media (prefers-reduced-motion)` support
- Structure: Hero section (headline + subhead + CTA + `[image: hero visual]`), Features section (3-4 feature cards with `[icon]` placeholders), Social proof area (`[testimonial placeholder]`), CTA section, Footer with brand name
- No fabricated logos, testimonials, or stats — use placeholders
- No purple-pink gradient backgrounds, no rounded cards with colored left-border accent, no emoji as icons

**Quality gate:**
- [ ] Single file, no broken resource links
- [ ] All design tokens from design-system.md — no rogue hues
- [ ] `[icon]` and `[image: x]` placeholders used correctly — no emoji substitutes
- [ ] No console errors
- [ ] Responsive: renders correctly on mobile, tablet, desktop
- [ ] No Inter/Roboto/Arial in font stack
- [ ] Not empty-looking — composition, whitespace, and type-scale rhythm fill the page

---

### Phase 3: Visual Assets — Image Prompts

**Goal:** Produce 4 prompt files in `prompts/` directory for external AI image tools (ChatGPT, Midjourney, DALL-E, etc.).

**Subagent dispatch:**

```
DISPATCH subagent with:
  task: "Write 4 image prompts for the product in brand-brief.md"
  context_files:
    - marketing-output/<project-slug>/brand-brief.md
    - marketing-output/<project-slug>/design-system.md
  reference_guides:
    - references/image-gen-guide.md  (FULL content)
  outputs: (4 files)
    - marketing-output/<project-slug>/prompts/hero.md
    - marketing-output/<project-slug>/prompts/social.md
    - marketing-output/<project-slug>/prompts/mockup.md
    - marketing-output/<project-slug>/prompts/feature.md
```

**Required prompt files:**

| File | Template | Description |
|------|----------|-------------|
| `hero.md` | `banner-hero` | Web hero / landing page hero image. Left column headline + subhead + CTA, right column hero visual. |
| `social.md` | `social-interface-mockup` | Social media post mockup for the product. Realistic interface. |
| `mockup.md` | `product-card-overlay` | E-commerce detail / product card scene with marketing overlay. |
| `feature.md` | `premium-studio-product` or `exploded-view-poster` | High-end visual showcasing a specific product feature or component breakdown. |

**Each prompt file must:**
- Use the structured JSON skeleton from the image-gen-guide (type, goal, subject, scene, layout, style, details, constraints)
- Fill all template parameters — use sensible defaults for anything the brand brief doesn't specify
- Include a usage note at the top: "Take this prompt to ChatGPT, Midjourney, DALL-E, or any GPT Image 2 compatible tool."
- Be saved with a timestamp in the filename convention: `<template-type>-<project-slug>-<YYYYMMDD-HHMMSS>.md` — but since the pipeline saves to `prompts/hero.md` etc., include the full JSON inside with timestamp metadata

**Important:** We are Mode C (Advisor) — the subagent writes prompts, it does NOT generate images.

**Quality gate:**
- [ ] All 4 files present in prompts/
- [ ] Each file contains the JSON prompt skeleton fully filled
- [ ] Usage note included in each file
- [ ] No "generated image" claims — only "prompt saved, take to your image tool"

---

### Phase 4: Video Script (Optional)

**Goal:** Produce `video/script.md` and `video/outline.md` — only if user requests video.

**Ask the user:** "Would you like a product demo video script as well? This will produce a spoken script and a production outline."

If user declines, skip this phase entirely.

**Subagent dispatch:**

```
DISPATCH subagent with:
  task: "Write a marketing video script and outline for the product in brand-brief.md"
  context_files:
    - marketing-output/<project-slug>/brand-brief.md
    - marketing-output/<project-slug>/design-system.md
  reference_guides:
    - references/video-guide.md  (FULL content)
  outputs:
    - marketing-output/<project-slug>/video/script.md
    - marketing-output/<project-slug>/video/outline.md
```

**Requirements:**
- **script.md**: Cold open in 3 seconds. Second person. Short sentences. No structural words (no "first/second/finally"). Numbers translated to feeling. Concrete examples. No emoji. Use `---` as step boundaries.
- **outline.md**: Chapter splits + step counts + info pools (≥ 3 items per chapter with source annotation). No animation specs. Asset list at end with ✓/⚠️ annotation.
- **Checkpoint Plan required**: After writing both files, present the 5-item alignment checkpoint (script, outline, theme, assets, dev mode). Do NOT proceed to any further phase without user alignment.

**Quality gate:**
- [ ] script.md: cold open ≤ 3s, second person, ≤ 20 char sentences, no structural words
- [ ] script.md: no emoji, no fake empathy, no triple parallelism
- [ ] outline.md: ≥ 3 info pool items per chapter, no animation/means lines
- [ ] outline.md: 3-8 steps per chapter
- [ ] Checkpoint plan presented
- [ ] No `article.md` deletion (if applicable)

---

### Phase 5: Copy Generation (Optional — Website Mode)

**Goal:** Generate optimized copy, email sequences, or ad creative from audit insights or a brand brief.

**Trigger:** User says "write copy for my landing page," "generate email sequences," "write ad copy."

**Subagent dispatch:**

```
DISPATCH subagent with:
  task: "Generate [copy type] for the product/brand"
  context_files:
    - marketing-output/<project-slug>/brand-brief.md
    - marketing-output/<project-slug>/MARKETING-AUDIT.md (if exists)
  reference_guides:
    - references/copy-guide.md  (FULL content)
  outputs:
    - marketing-output/<project-slug>/COPY-SUGGESTIONS.md  (website copy)
    - marketing-output/<project-slug>/EMAIL-SEQUENCES.md   (email sequences)
```

**Copy generation checklist:**
- [ ] Page type detected (homepage, landing, pricing, about)
- [ ] Voice & tone profile analyzed
- [ ] Headline scored across 5 dimensions (clarity, specificity, relevance, differentiation, emotion)
- [ ] ≥5 before/after rewrite examples
- [ ] CTA optimization recommendations
- [ ] Swipe file: 10 headline alternatives, 5 CTAs, 3 meta descriptions

**Email sequence checklist:**
- [ ] Sequence type selected (welcome, nurture, launch, re-engagement, cart abandonment)
- [ ] One Email, One Job rule enforced
- [ ] Subject lines follow formula patterns (number+benefit, curiosity gap, direct benefit)
- [ ] Send timing and cadence specified
- [ ] Industry benchmarks included (open rate, click rate, conversion rate)
- [ ] Compliance notes (CAN-SPAM, GDPR, CASL)
- [ ] Use templates from `templates/email-welcome.md`, `templates/email-nurture.md`, `templates/email-launch.md`

**Quality gate:**
- [ ] All before/after examples include specific quotes and concrete alternatives
- [ ] Headline scorecard complete with 5 dimensions
- [ ] Email sequences include subject lines, preview text, body frameworks, and CTAs
- [ ] Files saved to output directory

---

## 4. Output Package Structure

```
marketing-output/<project-slug>/
  MARKETING-AUDIT.md           # Phase -1 — scored audit (website mode)
  brand-brief.md               # Phase 0
  design-system.md             # Phase 1 — design tokens
  brand-board.html             # Phase 1 — visual brand board
  landing-page.html            # Phase 2 — landing page
  prompts/                     # Phase 3 — image prompts
    hero.md                    #   banner-hero prompt
    social.md                  #   social-interface-mockup prompt
    mockup.md                  #   product-card-overlay prompt
    feature.md                 #   premium-studio or exploded-view poster prompt
  video/                       # Phase 4 — (optional)
    script.md                  #   spoken marketing script
    outline.md                 #   production outline
  COPY-SUGGESTIONS.md          # Phase 5 — copy rewrite suggestions
  EMAIL-SEQUENCES.md           # Phase 5 — generated email sequences
```

The `<project-slug>` is derived from the product name: lowercase, spaces to hyphens, remove special characters. Example: "FlowSync Pro" → `flowsync-pro`.

---

## 5. Quality Gates — Per-Phase Review

Run these checks before reporting completion to the user. If any gate fails, re-execute the failing phase.

| # | Phase | Gate | What to verify |
|---|-------|------|----------------|
| -1 | Audit | 5-agent completeness | All 5 subagent outputs collected, composite score calculated, executive summary present |
| 0 | Intake | Brief completeness | All template fields filled, no raw `{...}` syntax, smart defaults applied |
| 1 | Design System | Token fidelity | oklch() colors derived from brief hue, no font clichés, board renders standalone |
| 2 | Landing Page | Single-file integrity | No broken resource links, tokens match design-system.md, responsive across 3 breakpoints |
| 3 | Visual Assets | 4/4 prompts | All four files present, each with filled JSON skeleton and usage note |
| 4 | Video Script | Content quality | Cold open, second person, ≤20 char sentences, ≥3 info pool items per chapter, checkpoint plan presented |
| 5 | Copy Generation | Actionable rewrites | ≥5 before/after examples, headline scorecard complete, email sequences include subject/preview/body/CTA |

**Global anti-slop checklist (all phases):**
- [ ] No purple-pink-blue gradient backgrounds
- [ ] No rounded cards with colored left-border accent
- [ ] No Inter, Roboto, Arial, Fraunces, system-ui in font stacks
- [ ] No emoji as icon substitutes
- [ ] No fabricated data (fake testimonials, fake logo walls, fake stats)
- [ ] No SVG-drawn graphics as asset substitutes
- [ ] All placeholders use `[icon]`, `[image: description]`, `[data: ask user]` format

---

## 6. Model Routing

Different phases benefit from different model strengths. Route accordingly:

| Phase | Recommended Model | Rationale |
|-------|------------------|-----------|
| Phase -1: Audit | GLM 5.1 (orchestrator), Kimi (subagents) | GLM handles composite scoring; Kimi subagents run deep page-by-page analysis |
| Phase 0: Intake | GLM 5.1 | Fast structured output generation, good at filling templates with defaults |
| Phase 1: Design System | GLM 5.1 | Strong visual/design reasoning, produces coherent token systems |
| Phase 2: Landing Page | GLM 5.1 | Complex HTML/CSS composition — GLM 5.1 builds single-file pages reliably |
| Phase 3: Visual Prompts | Kimi | Better at nuanced prompt engineering, handles JSON skeleton templates cleanly |
| Phase 4: Video Script | Kimi | Creative writing strengths match video script needs — maintains character voice |
| Phase 5: Copy Generation | Kimi | Copywriting and email sequence generation — creative with structural precision |

**Fallback:** If the recommended model is unavailable, use any available model. The reference guides are comprehensive enough to compensate.

---

## 7. Pitfalls

| Pitfall | Mitigation |
|---------|------------|
| **Subagent summarizing the reference guide instead of passing it** | Always say "Here is the COMPLETE reference guide" and include the full file content. Never write "Based on the guide, here's what to do..." |
| **Using AI-cliché fonts (Inter, Roboto, Arial, Fraunces, system-ui)** | The Design Engineer Guide provides alternatives; enforce in quality gate |
| **Subagent invents colors outside the brief's declared hue** | Enforce oklch() derivation from brand-brief hue value at Phase 1 and Phase 2 quality gates |
| **Prompt subagent claims to have generated images** | Mode C rule: no image APIs available. Subagent produces prompts only. Enforce "Prompt saved — take to your image tool" language |
| **Landing page looks empty — designer over-minimalism** | Verify page has visible content at all breakpoints. Empty-looking page = layout problem, not feature |
| **Video phase proceeds without Checkpoint Plan** | Enforce: Checkpoint Plan is mandatory before any video production continues |
| **Multiple subagents write to same path** | Each phase dispatches sequentially. Never parallelize subagents writing to the same output directory. Phase 3 generates 4 files in one subagent call — single agent owns the batch. When dispatching Phase -1's 5 parallel audit subagents, each writes to a separate output file (their section of the audit) — the orchestrator composites them afterward, not the subagents. **Never dispatch two subagents that both target the same output file** — they silently clobber each other. |
| **User provides insufficient info in Phase 0** | Use smart defaults — only ask when the product name itself is missing. A v0 with assumptions beats a perfect v1 nobody asked for |
| **HTML files reference external resources at dead URLs** | All HTML must be single-file. No external images, fonts, or scripts. Pin CDN versions: React 18.3.1, Babel 7.29.0 if used |
