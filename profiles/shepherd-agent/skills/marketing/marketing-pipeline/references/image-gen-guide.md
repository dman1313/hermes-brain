# Image Generation Reference Guide (Mode C · Advisor)

## Mode Detection — We Are Always Mode C

Dwayne has NO image APIs (no DALL-E, no Midjourney, no Stable Diffusion). We operate exclusively in **Mode C (Advisor/Consultant)** — we write high-quality prompts for the user to execute elsewhere.

**Do NOT pretend to generate images.** We produce prompt files that the user can take to ChatGPT, Midjourney, DALL-E, Sora, or any GPT Image 2 compatible gateway.

## Prompt Writing Methodology

1. Select the closest category and template (see below).
2. Fill template fields: map user input to `{argument name="..." default="..."}` parameters.
3. Structured templates use JSON prompt format; simpler requests use natural language.
4. Missing information that significantly affects output? Ask precise questions (not vague "what style?").
5. Otherwise use sensible defaults and proceed.

Recommended JSON skeleton:

```json
{
  "type": "template type",
  "goal": "image purpose",
  "subject": { ... },
  "scene": { ... },
  "layout": { ... },
  "style": { ... },
  "details": { ... },
  "constraints": { ... }
}
```

## Template Selection Strategy for Marketing

Match the user's ask to one of four categories:

- **UI mockups** — the user wants interface/mockup visuals
- **Product visuals** — the user wants product-centric commercial imagery
- **Posters & campaigns** — the user wants brand/campaign hero visuals
- **Branding & packaging** — the user wants brand identity systems

## Category: ui-mockups

### product-card-overlay
Person/background scene with a product card + marketing UI overlay. Left column text, center product, right model/scene. Best for: e-commerce detail page hero, landing page hero section, ad creatives with "person + product card + selling points." Ask for: product name/category, model source, pricing/features, style (Japanese minimal / tech / lifestyle / studio / street), color palette, language.

### landing-page-case-study
Full-page SaaS/marketing case study mockup — 5-7 vertical sections (hero, strategy, performance, social proof, CTA) stitched into one tall screenshot. Best for: SaaS landing pages, growth reports, client proposals. Ask for: business type, brand+positioning, dark/light/glass aesthetic, core metrics, whether client logos + testimonials needed, aspect ratio (3:4 / 9:16 / desktop).

### social-interface-mockup
Highly realistic social media app post detail page (Twitter/X, Xiaohongshu, Weibo, Threads, Instagram). Header + author info + post body + media cards + interaction row + reply area. Best for: concept demos, celebrity/historical figure fake accounts, marketing demos. Ask for: platform, dark/light mode, account identity, post content, whether you can auto-fill engagement data.

## Category: product-visuals

### white-background-product
Clean e-commerce white-background product shot. Single product centered, soft reflection/drop shadow, optional brand name + one selling point overlay. Best for: Taobao/Amazon/JD main image, SKU cards. Ask for: product name + visual description, single or multi-angle, text overlay needed, badges needed.

### premium-studio-product
Magazine-ad-grade commercial product photography. Dramatic lighting, unified color tone, minimal props, product as sole narrative hero. Best for: perfume/watches/liquor/luxury 3C, high-end brand site hero. Ask for: product + category, brand positioning, color tone, lighting mood, props, logo/tagline.

### exploded-view-poster
Product vertically stacked into internal components + callout labels + top headline + bottom brand area. Best for: product launch hero, technical highlight image, engineering aesthetic showcase. Ask for: product model, component count (6-9 typical), brand name + slogan, color tone, bilingual callouts needed.

## Category: poster-and-campaigns

### brand-poster
Single brand hero poster — one strong slogan, clear visual center, strict brand colors, logo in corner. Best for: new product launch, seasonal campaign, brand upgrade, anniversary. Ask for: brand name + industry, theme/slogan, visual tone (futuristic/vintage/minimal/street), subject type, aspect ratio.

### campaign-kv
Campaign Key Visual system — one anchor visual + derivative layout system (1:1, 9:16, 16:9 previews) with strict color palette. Best for: seasonal campaign, double-11, cross-platform unified visuals. Ask for: campaign name + claim, time window, brand + campaign colors, visual center, whether to show derivatives.

### banner-hero
Horizontal-format web hero / app banner. Left column headline + subhead + CTA, right column hero visual. Best for: landing page hero, app activity banner, email marketing. Ask for: use case (web/app/email), theme/claim, main visual, CTA text + color, brand colors, aspect ratio.

## Category: branding-and-packaging

### brand-identity-board
Single-page brand identity system — logo zone + color palette swatches + typography + application mockups. Grid-based, professional, understated. Best for: VI summary, brand proposal board, designer case study, brand guideline cover. Ask for: brand name + tagline, industry, logo type (wordmark/icon/combination), primary colors, font preference, whether packaging/business card mockups needed.

## Prompt Save Rules

Every prompt file we produce MUST be saved. No exceptions.

- Output directory: `garden-gpt-image-2/prompt/`
- Naming convention: `<task-slug>-<timestamp>.md`
- Example: `garden-gpt-image-2/prompt/live-commerce-ui-20260424-153045.md`

Create the directory if it doesn't exist. The slug should be a short descriptive name derived from the task. Use the current timestamp in `YYYYMMDD-HHMMSS` format.

## When to Ask Questions vs. Use Defaults

Ask the user only when missing information would significantly hurt the result:

- No prompt goal at all
- Subject identity determines the entire visual direction
- Product/price/copy/UI text is a core visual element
- User expresses conflicting goals

Otherwise, use the template's default values and proceed. Merge related questions into one message when possible.

## Summary Workflow

1. Identify the marketing category + specific template
2. Ask targeted questions if critical info is missing (otherwise use defaults)
3. Fill template parameters with user input
4. Render the final prompt (JSON or natural language)
5. Save to `garden-gpt-image-2/prompt/<task-slug>-<timestamp>.md`
6. Print the prompt and a brief usage note: "Prompt saved — take it to ChatGPT, Midjourney, DALL-E, or any GPT Image 2 compatible tool."
