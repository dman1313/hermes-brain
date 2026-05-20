---
name: voice-to-newsletter-pipeline
description: Orchestrate the full Voice-to-Newsletter pipeline using Hermes subagents (DRAFT, POLISH, PACKAGER) with Sherlock research and Hermes built-in STT/Vision. Accepts voice notes + photos and returns a complete newsletter package.
triggers:
  - newsletter pipeline
  - voice to newsletter
  - run pipeline
  - /pipeline
  - /newsletter
version: 1.1.0
author: Hermes Agent
metadata:
  hermes:
    tags: [newsletter, pipeline, agents, voice, dropbox, wiki]
    category: agents
---

# Voice-to-Newsletter Pipeline

Orchestrate the full pipeline from voice notes + photos to a complete newsletter package using Hermes subagents.

## When This Skill Activates

Use when the user:
- Sends a voice note + photos and wants a newsletter/article
- Uses `/pipeline` or `/newsletter` command
- Asks to run the voice-to-newsletter pipeline
- Wants to convert voice input into a published-ready newsletter

## Pipeline Architecture

```
Input (voice + images)
  │
  ├─→ Hermes STT ──→ transcript
  │
  ├─→ Sherlock ──→ research_brief
  │         (parallel)
  ├─→ Hermes Vision ──→ visual_analysis
  │
  ├─→ DRAFT ──→ article_draft
  │
  ├─→ POLISH ──→ humanized_draft
  │
  ├─→ PACKAGER ──→ newsletter_package
  │
  └─→ Output for human review
```

## Agent Roles

| Role | Method | Description |
|------|--------|-------------|
| DRAFT | Hermes subagent (delegate_task) | Topic extraction + drafting |
| POLISH | Hermes subagent (delegate_task) | Humanization |
| PACKAGER | Hermes subagent (delegate_task) | Formatting + Dropbox + wiki |
| Sherlock | Hermes subagent (delegate_task) | Research |

## Step-by-Step Execution

### Step 1: Intake (Hermes built-in)
- Receive voice note file(s) and image file(s)
- Generate a job_id (UUID)
- Store raw inputs temporarily

### Step 2: Transcription + Research (parallel)
Use `delegate_task` with batch mode for parallel execution:

**Task A — Transcription:**
- Use Hermes STT capabilities to transcribe audio
- Clean transcript lightly (remove fillers only when needed)
- Preserve personality, phrasing quirks, emphasis

**Task B — Research:**
- Delegate to Sherlock agent via `delegate_task`
- Pass the transcript (or topic hints from it)
- Sherlock returns: verified facts, context, sources, items uncertain

**Task C — Visual Analysis (if images):**
- Use `vision_analyze` tool for each image
- Generate descriptions, suggested captions, editorial roles
- Determine image-article section matching

### Step 3: Drafting (DRAFT agent)
- Delegate to DRAFT agent via `delegate_task`
- Pass: transcript + research_brief + visual_analysis
- DRAFT returns: structured JSON with headline, sections, image placements

### Step 4: Humanization (POLISH agent)
- Delegate to POLISH agent via `delegate_task`
- Pass: DRAFT output + original transcript excerpts
- POLISH returns: humanized JSON with voice review

### Step 5: Packaging (PACKAGER agent)
- Delegate to PACKAGER agent via `delegate_task`
- Pass: POLISH output + images + research + transcript + job metadata
- PACKAGER returns: complete newsletter package + Dropbox URLs + wiki path

### Step 6: Delivery
- Return the newsletter package to the user for review
- NEVER auto-publish
- Include: subject lines, preview text, markdown, image plan, Dropbox links

## Parallelization Strategy

Steps 2A, 2B, 2C run in parallel using `delegate_task` batch mode.
Steps 3→4→5 are sequential (each depends on previous output).

## Error Handling

1. If any agent fails, retry once with the same input
2. If retry fails, return partial output with error details
3. Never discard original transcript or images
4. Log all failures in the job metadata

## Slash Commands

### `/pipeline <optional notes>`
Run the full pipeline on the current voice note + photos.

### `/newsletter <optional notes>`
Alias for `/pipeline`.

## Output Contract

Always return results in this format:

1. **Newsletter** — headline, body, image placements, captions
2. **Research Pack** — facts, sources, notes
3. **Asset List** — Dropbox links, tags
4. **Wiki Entry** — structured data object path

## Quality Gates

Before final delivery, verify:
- [ ] Voice review: sounds like the speaker
- [ ] Audience review: clear for intended reader
- [ ] Platform review: newsletter is scannable and well-formatted

## Pitfalls

- Don't skip the POLISH stage — raw DRAFT output sounds robotic
- Don't auto-publish without human review
- Don't lose the original transcript at any stage
- Don't overload with research — it supports the story, not the other way around
- Don't place images decoratively — every image needs an editorial purpose
