---
name: framing-doc
description: Create a framing document from conversation transcripts. Use when the user has transcripts (VTT, call notes, etc.) and wants to produce a frame that captures the problem worth solving and why it was chosen over alternatives.
---

# Framing from Conversation Transcripts

Produce a frame document from one or more conversation transcripts. The frame captures the "why" — what problem to solve and why this one, not the others.

---

## Before You Start

Ask the user:

1. **Which transcripts?** Get specific file paths. Read them in the order the user specifies — conversation order often matters because ideas build across calls.
2. **What's the topic area?** A rough sense of what these conversations were about (e.g., "AI features," "onboarding redesign") so you know what lens to read through.

If the user doesn't know or this is exploration, just read them all and offer to organize.

---

## What You're Producing

A frame document that answers:

1. **What problem are we solving?** — One sentence. Concrete, not abstract.
2. **Why this one?** — What other problems came up and why this one won. Quote specific moments from the transcripts.
3. **What's at stake?** — Who benefits? What changes if we solve it?
4. **What constraints shape the solution?** — Technical, business, timing, political constraints from the conversation.

The frame is NOT a summary of everything discussed. It's a **decision document** — it captures the choice and the evidence behind it.

---

## Process

### 1. Read Everything First

Read all transcripts before writing anything. Look for:

- Problems that get repeated or returned to
- Moments where someone says "this is the real issue" or "what we actually need"
- Alternatives that were raised and discarded (and why)
- Constraints mentioned in passing ("we can't touch the API," "has to work offline")
- Emotional signals — frustration, excitement, hesitation — these often point to what matters

### 2. Identify the Shortlist of Problems

From the conversations, extract the concrete problems discussed. Each should be:

- Specific (not "improve UX" but "users can't find the export button")
- Traceable to a moment in the transcripts
- Something people actually spent time on

### 3. Make the Case for One

Pick the one that best fits:

- Recurrence — it came up multiple times, in different ways
- Clarity — people could describe it concretely
- Leverage — solving it unlocks other things
- Constraints — it fits within what's possible

Explain why the others were set aside. Quote the transcripts.

### 4. Write the Frame

Structure:

```markdown
# [Topic Area] — Frame

## The Problem

[One sentence. Concrete.]

## Why This One

[Evidence from transcripts. Quote specific moments. Explain what alternatives were considered and why they lost.]

## What's At Stake

[Who benefits. What changes. What happens if we don't solve it.]

## Constraints

[What shapes the solution space. Technical, business, timing, political.]
```

### 5. Offer the Output

Present the frame and ask:

- Does this capture what you heard in those conversations?
- Did I miss a problem that felt important?
- Should we adjust the emphasis?

---

## Principles

- **Quote the transcripts** — your evidence is what people actually said
- **Be specific** — "users can't export filtered results" not "export functionality needs improvement"
- **Frame is a decision, not a summary** — it argues for one problem over others
- **Constraints are part of the frame** — they define the shape of possible solutions

---

## Boundaries

- Read transcripts only — don't interview people or gather new data
- One frame at a time — if the transcripts cover multiple unrelated topics, offer to frame each separately
- Frame does NOT propose solutions — it defines the problem worth solving
- Offer to adjust — the user may have context you don't
