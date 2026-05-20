---
name: kickoff-doc
description: Turn a shaped project kickoff transcript into a reference document for the builder. Use when the user has a transcript (VTT, etc.) from a kickoff call and wants to produce a document that captures what was shaped and agreed.
---

# Kickoff Document from Transcript

Turn a kickoff call transcript into a builder-facing reference document for a shaped project.

---

## Before You Start

Ask the user:

1. **Who is the primary audience?** (Usually the builder who will implement the work.)
2. **What other inputs are there?** (Visuals, screenshots, mockups, breadboards from the session.)

The transcript is your source material. The document is NOT a summary of the call — it's a **map of the territory** that was shaped.

---

## Organizing Principle: Territory, Not Chronology

A kickoff call moves through topics as people talk. The document reorganizes that into a stable structure:

1. **What we're building** — the shaped solution, concisely
2. **The parts** — what pieces exist and how they relate
3. **How to build it** — sequence, dependencies, gotchas
4. **Reference** — decisions made, open questions, links to other docs

Do NOT organize the document in the order things were discussed. Reorganize for the builder who needs to know what to build and in what order.

---

## Document Structure

```markdown
# [Project Name] — Kickoff Reference

## Overview
[One paragraph. What we're building and why. The shaped solution in a nutshell.]

## Parts
[The pieces of the system. For each part:]
- What it does
- What it depends on
- Key decisions or constraints

## Build Sequence
[Order to build the parts. What depends on what. What can be parallelized.]

## Decisions
[Key decisions made during the kickoff. Who decided. Why.]

## Open Questions
[Things that weren't resolved. Who owns finding the answer.]

## Related Documents
[Links to breadboards, shaping docs, designs, etc.]
```

---

## Process

### 1. Extract the Shape

Read the full transcript. Identify:

- What problem is being solved? (Should be clear from the shaping doc, but verify.)
- What shape was chosen? (The solution approach, from alternatives discussed.)
- What are the concrete parts? (Screens, affordances, data flows, integration points.)

### 2. Identify Decisions

Every time someone says "let's do X" or "we'll go with Y" — that's a decision. Capture:

- What was decided
- Who made the call
- Why (if discussed)
- What was the alternative (if discussed)

### 3. Map Dependencies

From the discussion, work out what needs to be built first. Look for:

- "We need X before we can do Y"
- "Y depends on the API being ready"
- "We can start on Z while waiting for X"

### 4. Write the Document

Reorganize into the structure above. Be concise. The builder needs to find things quickly.

### 5. Review and Refine

Present the document and ask:

- Does this match what you remember deciding?
- Did I miss any parts or decisions?
- Is the build order right?
- Do you want to add anything before handing this to the builder?

---

## Principles

- **Builder-first** — organize for the person who will do the work
- **Decisions over discussion** — capture conclusions, not the journey to them
- **Be specific** — "use the existing /api/users endpoint" not "integrate with user service"
- **Flag uncertainties** — if something was vague in the discussion, mark it as an open question

---

## Boundaries

- One kickoff per document
- Requires a transcript — don't work from memory
- Document is a reference, not a spec — it captures agreements, not implementation details
- If the transcript doesn't contain enough to fill a section, mark it as TBD
