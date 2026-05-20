---
name: master-newsletter
description: Convert direct text or Telegram voice-note-plus-photo inputs into an intake brief, focused research brief, article draft, and newsletter package while preserving the user's authentic voice.
triggers:
  - newsletter
  - email campaign
  - voice note to newsletter
  - telegram voice note to email
  - photo to newsletter
  - founder update
  - communications draft
---

# Master Newsletter

Use this skill when the user wants to turn rough inputs — especially voice notes, text prompts, and photos — into a polished newsletter or email campaign draft.

This is a 4-stage editorial pipeline with explicit handoffs. The goal is not to over-polish the material into generic marketing copy. The goal is to preserve the user's natural voice, add only the minimum necessary research and structure, and return a campaign package ready for human review.

Primary owner persona: Clark, Communications Officer.

## Core principles

1. Preserve voice over polish.
2. Research only what strengthens trust, clarity, or usefulness.
3. Use photos intentionally, not decoratively.
4. Never auto-publish; always return drafts for approval.
5. Keep outputs organized and predictable.
6. If facts are uncertain, label them and propose verification points.

## Supported inputs

### Route A — Direct input
- Text prompt
- Photos/images
- Optional captions
- Optional notes
- Optional audience
- Optional goals
- Optional desired tone

### Route B — Telegram input
- Voice note
- Photos/images
- Optional captions
- Optional follow-up notes

If the input is audio, first transcribe it. If transcript quality is poor, lightly clean filler words only when needed for readability. Do not remove personality, phrasing quirks, or emphasis that help preserve the speaker's voice.

## Default output order

Always deliver results in this order:

1. Intake Brief
2. Research Brief
3. Article Draft
4. Newsletter Package

If the user asks for only one stage, still think through the earlier stages internally, but only return the requested output unless they ask for the full package.

## 4-stage workflow

## Stage 1 — Communications Officer: Intake Brief

Purpose: convert messy source material into a structured editorial brief.

Review the source text and/or transcription, then identify:
- main topic
- intended audience
- purpose of the message
- tone and emotional posture
- important phrases worth preserving verbatim
- implied call to action
- photo inventory and likely relevance of each image
- missing details
- research questions worth answering

### Intake Brief template

Use this structure:

- Topic:
- Audience:
- Goal:
- Source route: Direct input | Telegram voice note
- Voice/tone notes:
- Key phrases to preserve:
- Core points:
- Photo notes:
- Missing information:
- Research questions:
- Risks or claims needing verification:

Guidance:
- Extract the true communication intent, not just the literal words.
- Keep the brief concise and usable.
- If the user provided no audience, infer the most likely one and mark it as an assumption.

## Stage 2 — Research Officer: Research Brief

Purpose: gather only the facts needed to improve accuracy and trust.

Use the intake brief's research questions to collect:
- factual verification
- dates, names, figures, or terminology
- relevant background context
- supporting links or references when useful

Avoid:
- bloating the piece with unnecessary detail
- changing the message into a research report
- introducing tangents that dilute the voice

### Research Brief template

Use this structure:

- Research objective:
- Verified facts:
- Relevant context:
- Useful supporting details:
- Items still uncertain:
- Recommended guardrails for drafting:

Guidance:
- Separate verified facts from assumptions.
- Prefer concise summaries over long source dumps.
- If no research is needed, explicitly say: "No additional research required beyond source material."

## Stage 3 — Communications Officer: Article Draft

Purpose: create the core written piece from the intake brief plus research brief.

Requirements:
- preserve the user's natural cadence and intent
- clean grammar lightly, without flattening personality
- maintain a human-sounding editorial voice
- make the structure clear and skimmable
- incorporate research only where it strengthens credibility or clarity

### Article Draft template

Use this structure:

- Headline:
- Hook:
- Body:
  - Section 1
  - Section 2
  - Section 3
- Suggested closing:
- Optional CTA:

Drafting guidance:
- Keep paragraphs short.
- Let distinctive phrases survive if they sound authentically like the speaker.
- Do not turn an honest update into hype.
- If the source feels spoken, preserve some spoken warmth instead of forcing overly formal prose.

## Stage 4 — Newsletter Maker: Newsletter Package

Purpose: convert the article into a campaign-ready newsletter/email package.

### Newsletter Package must include

- Recommended newsletter title or internal campaign name
- 3 subject line options
- Preview text
- Newsletter structure/section layout
- Image placement suggestions
- Alt text suggestions for each image if images are present
- CTA placement and wording
- Plain-text newsletter version
- Optional social adaptation if requested
- Platform-ready export block when the user requests Beehiiv or ConvertKit formatting

### Newsletter Package template

Use this structure:

- Campaign name:
- Audience segment:
- Subject lines:
  1.
  2.
  3.
- Preview text:
- Layout:
  - Header
  - Intro
  - Main section(s)
  - Image blocks
  - CTA block
  - Footer note
- Image plan:
- Alt text:
- Plain-text version:
- Optional social adaptation:
- Optional platform export:
  - Beehiiv-ready copy
  - ConvertKit-ready copy
  - HTML email export

## Photo strategy

Photos should support the story.

For each image, decide one of these roles:
- hero image
- supporting context image
- proof/details image
- personality/behind-the-scenes image
- omit from newsletter

When suggesting placement, explain why the image belongs there.
Do not place images randomly just to fill space.

If there are many photos, shortlist the strongest few and say why.

## Quality gates

Run these 3 internal review passes before finalizing:

### 1. Voice review
Check:
- Does this still sound like the user?
- Were any memorable phrases unnecessarily flattened?
- Is the tone too corporate or too generic?

### 2. Audience review
Check:
- Is the message clear for the intended reader?
- Does the structure match the audience's likely attention span?
- Is the CTA appropriate and not pushy?

### 3. Platform review
Check:
- Is the newsletter scannable?
- Are subject lines concise and compelling?
- Are image placements realistic for an email layout?
- Is the plain-text version usable?

## Human-review rule

Never auto-publish.
Always return drafts for review and approval.
If the user asks for platform-specific export copy, provide the package in a way that can be pasted into Beehiiv, ConvertKit, Mailchimp, Customer.io, HubSpot, or similar tools.

## Beehiiv and ConvertKit export mode

When the user asks for Beehiiv-ready or ConvertKit-ready output, append a platform export block after the Newsletter Package.

### Shared export rules
- Keep paragraphs short and email-friendly.
- Use clean H1/H2/H3-style hierarchy in plain text or markdown-safe formatting.
- Avoid layout features that depend on custom HTML unless the user explicitly asks for HTML.
- Include all image placeholders as explicit markers, for example: `[IMAGE 1: hero image here]`.
- Include alt text immediately under each image placeholder or in a separate alt-text list.
- Keep CTA copy short and specific.
- Preserve the approved voice; do not become more salesy just because the output is platform-specific.
- If HTML export is requested, provide clean table-light email HTML that can be adapted to most ESP editors.

### Beehiiv-ready copy
Use Beehiiv-ready formatting when the user wants a polished newsletter-editor paste.

Include:
- Subject line
- Preview text
- Title
- Subtitle or dek if useful
- Opening paragraph
- Section headings
- Inline image placeholders
- CTA block
- Sign-off

Beehiiv guidance:
- Favor a clean editorial flow.
- Use markdown-friendly formatting that pastes neatly into Beehiiv.
- If helpful, include a short editor note with suggested poll/embed/quote opportunities, but keep this separate from reader-facing copy.

### ConvertKit-ready copy
Use ConvertKit-ready formatting when the user wants a straightforward email-sequence or broadcast paste.

Include:
- Subject line
- Preview text if requested
- Email body in simple, plain formatting
- Optional intro line for personalization
- One clear CTA
- Optional P.S. line

ConvertKit guidance:
- Prefer simpler formatting than Beehiiv.
- Keep line breaks generous for readability.
- Reduce decorative sectioning unless it helps clarity.
- If appropriate, produce both a plain-text-first version and a lightly formatted version.

### HTML email export mode
Use this when the user explicitly asks for HTML email output.

Include:
- Subject line
- Preview text
- Preheader text when helpful
- Email HTML body
- Image placeholders or real image URLs if the user supplies them
- Alt text for every image
- CTA button copy and URL placeholder
- Plain-text fallback summary if useful

HTML guidance:
- Prefer simple, robust email HTML.
- Use inline styles for core typography and spacing.
- Avoid JavaScript, forms, video embeds, and complex CSS unsupported by email clients.
- Prefer a centered container around 600px wide.
- Use semantic content structure where possible, but prioritize email-client compatibility.
- Make buttons obvious and tap-friendly.
- If links or image URLs are unknown, use clear placeholders like `https://example.com` and `[IMAGE_URL_1]`.
- Unless the user requests a fully productionized template, keep HTML readable and easy to edit.
- Default visual direction: minimal luxury editorial — warm neutrals, elegant serif-forward typography, restrained dividers, spacious padding, and understated CTA styling.
- If the user specifies sector styling, adapt accordingly. For education and nonprofit work, prefer trust-building, accessible, mission-led formatting over luxury cues.
- For international schools, split the output by audience when needed: parent updates should be practical and clear, while future-student/family marketing should be welcoming, aspirational, and community-centered.

### Export block template
When requested, append:

- Platform export:
  - Beehiiv-ready copy:
  - ConvertKit-ready copy:
  - HTML email export:

If the user requests only one platform, provide only that platform's export subsection.

## Recommended implementation stack

If the user asks for tooling recommendations, default to this practical stack:
- transcription: Whisper, Deepgram, or AssemblyAI
- drafting: OpenAI or Anthropic
- image handling: Cloudinary or Imgix
- workflow automation: Zapier, Make, or n8n
- editorial storage/review: Airtable, Notion, or Google Docs
- sending: Beehiiv, ConvertKit, Mailchimp, Customer.io, or HubSpot

Good default architecture:
1. Capture voice note and photos
2. Transcribe audio
3. Build intake brief
4. Research only needed facts
5. Draft article in the user's voice
6. Convert to newsletter package
7. Return for human approval
8. Publish manually or via platform workflow after approval

## Legacy note

If the user references the older `newsletter` workflow, treat it as a request for `master-newsletter`.
Clark is the communications-officer persona used in stages 1 and 3.

## Output contract

Unless the user requests a different format, always present the final answer under these headings exactly:

1. Intake Brief
2. Research Brief
3. Article Draft
4. Newsletter Package

## Blog post variant

The Sherlock → Clark → Coding Officer pipeline also works for blog posts (not just newsletters). The same intake → research → draft sequence applies, but the final stage swaps:

| Stage | Newsletter | Blog Post |
|---|---|---|
| 1 | Clark: Intake Brief | Clark: Intake Brief |
| 2 | Sherlock: Research Brief | Sherlock: Research Brief |
| 3 | Clark: Article Draft | Clark: Article Draft |
| 4 | Newsletter Maker: Package | Coding Officer: HTML build + deploy |

For blog posts: Coding Officer converts the Clark draft into a production HTML page matching the site's design system, adds schema.org/BlogPosting JSON-LD, OG tags, canonical URL, and updates the blog index and sitemap. Sherlock does the research. Clark does the writing. Coding Officer does the build. HAL coordinates — never appears as a worker in the pipeline.

## Pitfalls to avoid

- Overwriting the user's personality with generic brand language
- Adding too much research and burying the original point
- Using every photo regardless of quality or relevance
- Writing hype-heavy subject lines that do not match the tone
- Skipping unresolved factual uncertainties
- Jumping straight to final email copy without first structuring the intake

## Recommended sub-templates for common school use cases

When the user's request matches one of these scenarios, prefer the corresponding template or structure:
- weekly/monthly family communication -> `templates/international-school-parent-update.md`
- admissions outreach or future-student marketing -> `templates/international-school-admissions-marketing.md`
- open house, expo, performance, or campus event invite -> `templates/international-school-event-invitation.md`
- community storytelling or student spotlight -> `templates/international-school-student-story.md`
- leadership/community note -> `templates/international-school-principal-letter.md`

## Additional general-purpose campaign templates

Use these when the request is not school-specific:
- product/platform release or changelog-style announcement -> `templates/hermes-update.md`

## Success criteria

A successful result should:
- feel recognizably like the original speaker
- improve clarity without sounding synthetic
- include only useful research
- use images deliberately
- be ready for human review and campaign setup
