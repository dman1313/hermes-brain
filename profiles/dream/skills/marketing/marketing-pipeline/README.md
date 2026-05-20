# Marketing Pipeline

End-to-end marketing asset pipeline for Hermes Agent. Takes product/brand input and produces landing pages, hero images, social graphics, product demo videos, and brand design systems.

## What It Does

The Marketing Pipeline transforms a plain brand brief into a complete set of marketing assets:

1. **Brand Brief** — structured product/market input (you fill this in)
2. **Audit & Validation** — checks that the brief is complete and actionable
3. **Asset Generation** — produces landing pages, hero images, social media graphics, product demo video scripts, and brand design systems

## How to Trigger

In Hermes Agent, say:

```
Build marketing assets for [product name]
Create a landing page for [product name]
Generate product visuals for [product name]
Build a complete brand package for [product name]
```

Or use the CLI directly:

```bash
python scripts/pipeline.py init my-product
# fill in brand-brief.md
python scripts/pipeline.py validate brief brand-brief.md
python scripts/pipeline.py summary my-product
```

## Output Structure

Each project creates a directory tree:

```
my-product/
├── brand-brief.md            # Your filled-in brief
├── audits/
│   ├── audit-report.json     # Structured data / LLM-readiness scores
│   └── remediation-plan.md   # Prioritized fixes
└── outputs/
    ├── landing-page.html      # Hero landing page
    ├── hero-image-prompt.md   # Image generation prompt (for DALL-E / Midjourney)
    ├── social-graphics/       # Social media sized variants
    ├── video-script.md        # Product demo video script
    ├── video-outline.md       # Video production outline
    └── brand-design-system/   # Colors, typography, tokens
```

## Phases

| Phase | What Happens | Gate |
|-------|-------------|------|
| **0. Init** | Create project, copy brand-brief template | User fills brief |
| **1. Validate** | Check brief completeness (no unfilled prompts, required sections present) | All checks pass |
| **2. Audit** | Run product context audit (market positioning, competitor signals, tone alignment) | Audit report written |
| **3. Generate** | Subagents produce assets in parallel: landing page (Design Engineer), hero image prompts, video script + outline, brand design system | All assets written to outputs/ |
| **4. Package** | Compile and present results; optional upload to cloud | User confirms |

## Requirements

- **Hermes Agent** — the orchestrator that manages phase transitions and subagent dispatch
- **GLM 5.1** (or equivalent capable model) — recommended for design and content generation subagents
- **Kimi CLI** — used for parallel subagent coordination during Phase 3 (Generate)
- **Python 3.10+** — for the pipeline CLI script
- **No image generation API** — the pipeline outputs *prompts* for DALL-E, Midjourney, or GPT Image 2; the user executes them

## Design Philosophy

Built on the **Garden Skills methodology**:

- **Anti-Slop** — every element must earn its place. No purple-pink gradients, no emoji substitutes for icons, no fabricated testimonials, no generic SaaS boilerplate.
- **Placeholder Before Fake** — a `[hero image]` placeholder signals "real material needed here" more professionally than a poorly generated fake.
- **Stunning, Not Functional** — visual output targets Dribbble/Behance showcase quality, not "it works."
- **One-Pass Content** — script and outline produced in a single pass; no iterative rewrites.
- **Checkpoint Alignment** — stories/videos present a checkpoint plan before proceeding to production, preventing wasted effort.
- **Mode C Image Workflow** — we write high-quality prompts for the user to execute in their image tool of choice; we never pretend to generate images.

## Example: Triggering with Agent Ready

Given a product called **Agent Ready** (a micro-SaaS certification for LLM-optimized websites):

1. Create and fill the brand brief:

```bash
python scripts/pipeline.py init agent-ready
```

2. Fill `agent-ready/brand-brief.md` with product details (see `templates/sample-agent-ready-brief.md` for a filled example).

3. Validate:

```bash
python scripts/pipeline.py validate brief agent-ready/brand-brief.md
```

4. Check status:

```bash
python scripts/pipeline.py summary agent-ready
```

5. The pipeline then dispatches subagents to produce:
   - A landing page HTML that explains the certification and pricing tiers
   - Hero image prompts showing a certification badge + website scan visualization
   - A product demo video script and outline
   - A brand design system (colors, typography, tokens)

## Limitations

- **No image generation** — the pipeline produces prompts only; the user must execute them in DALL-E, Midjourney, or GPT Image 2
- **Video stops at Phase 1 checkpoint** — video production outputs script.md + outline.md + a checkpoint plan, then waits for user alignment. Phase 2-4 (scaffolding, audio, recording) are not yet implemented.
- **No A/B testing** — the pipeline produces a single direction per asset; variant exploration is manual via the Tweaks panel pattern
- **English-first** — copy conventions, prompt templates, and script rules assume English-language output
- **No analytics integration** — generated assets are static; tracking/analytics integration is the user's responsibility

## License

MIT — see SKILL.md for details.
