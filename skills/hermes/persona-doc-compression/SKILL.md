---
name: persona-doc-compression
description: Condense verbose persona/identity docs from prose novels into compact reference-grade form — everything preserved, nothing lost, 2-5x size reduction.
version: 1.0.0
author: HAL
tags: [persona, soul, compression, token-optimization, context-efficiency]
related_skills: []
---

# Persona Doc Compression

Persona docs (`SOUL.md`, identity files, agent character sheets) accumulate verbose prose over time — single-sentence-per-line formatting, repeated embellishments, redundant concept restatements. This skill provides a repeatable compression method.

## When to Use

- A persona doc exceeds 500 lines or 10KB
- A DREAM audit or session transcript flags "SOUL.md is too large" or "memory is critically full"
- A new agent's soul doc was created with verbose prose rather than compact reference form
- You notice the persona takes noticeable time to load (sessions feel slow to start)

## Compression Method

### Step 1: Read the full doc

Read the entire file. Don't skip sections — every section may contain a signal you need to preserve.

### Step 2: Identify bloat patterns

Common bloat sources:
- **Single-sentence-per-line:** Each statement on its own line with a blank line after. This inflates line count 5-10x.
- **Repetition:** The same concept stated positively then negatively (e.g., "HAL should be kind. HAL should not be unkind.")
- **Explanatory scaffolding:** Phrases like "This means that...", "In other words...", "For example..."
- **List expansion:** Bullet points that say the same thing in 5 different ways (e.g., "Don't be corporate. Don't be a hype machine. Don't be a generic chatbot.")
- **Redundant section headers:** Sections that restate the section name as the first sentence.
- **Trailing qualifiers:** "Unless the task is unusually important" after every rule.

### Step 3: Compress each section

| Before | After |
|--------|-------|
| Single sentence per line, blank lines between | Compact paragraphs, 1-3 sentences per concept |
| "HAL should do X. HAL should not do Y." | "Do X, not Y." |
| "For model routing, use lightweight models for: ... (bullet list)" | "**Lightweight:** ... (comma list)" |
| 10-line section about "be direct" | "Be direct." |
| 15-line agent routing table with explanation per line | Bullet: agent name + comma-separated use cases |

### Step 4: Verify nothing lost

After compression, spot-check:
- Every section header from the original exists in the compressed version
- Every agent/role/tool mentioned is accounted for
- No decision rules were dropped
- The compressed doc is human-readable, not a machine-code dump

### Step 5: Check character savings

Quick sanity check — compressed should be at least 2x smaller than original.

## Measurement

```
# Before and after
wc -l -c SOUL.md
```

Target: 500-2,000 chars per major section (identity, routing, rules sections).  
Red flag: any single section over 3KB.

## Pitfalls

- **Over-compression into unreadable bullet points.** The goal is compact reference, not machine output. A human (or another LLM) should be able to read it naturally.
- **Losing nuance.** If a section had careful conditional logic ("Use X _unless_ Y"), preserve the condition. Compress the framing, not the logic.
- **Assuming the old format was wrong.** Some persona docs have verbose prose by design (artistic tone, character voice). Only compress when the verbosity is wasteful formatting, not intentional voice.
- **Not telling the user.** If you changed SOUL.md (or any major identity doc), inform the user — it's their agent's identity.

## Related

- `~/.hermes/skills/hermes/persona-doc-compression/SKILL.md`
- See also: memory-compression (for MEMORY.md overflow)
