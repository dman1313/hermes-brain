---
name: de-bono-six-hats
description: Structured multi-perspective decision analysis using De Bono's Six Thinking Hats framework with parallel sub-agents
---

# De Bono's Six Thinking Hats — Decision Agent

Use this skill when a user wants a structured multi-perspective decision analysis using De Bono's Six Thinking Hats framework.

## Trigger
User asks for a decision to be analyzed through "six hats," "six thinking hats," "De Bono," or explicitly asks for multiple perspectives on a decision.

## Workflow

**Step 1: Confirm the decision**
Ask the user to state the decision they want analyzed. Confirm you understood it before proceeding.

**Step 2: Run hats in parallel waves**
The `delegate_task` tool has `max_concurrent_children: 3` by default. Run in two waves:
- Wave 1 (parallel): White Hat, Red Hat, Black Hat
- Wave 2 (parallel): Yellow Hat, Green Hat, Blue Hat

**Step 3: Spawn each wave with these exact task goals:**

Wave 1 — each task gets this goal template:
```
You are the [HAT NAME] HAT. Analyze: "[DECISION]"

Respond ONLY with your hat's analysis — [hat-specific instruction below].
1-3 paragraphs max. Stay in character. No hat-switching.

White Hat: concise, factual, objective. What information/data exists?
Red Hat: gut feelings, emotions, intuition. What does your gut say?
Black Hat: risks, downsides, critical concerns. What could go wrong?
```

Wave 2 — Yellow, Green get their own, Blue waits to synthesize:
```
Yellow Hat: benefits, upsides, best-case. Why could this work out?
Green Hat: creative alternatives, wild ideas. What else could be tried?
```

**Blue Hat goal (Wave 2, waits for all 5):**
```
You are the BLUE HAT. Do NOT give your own perspective on the decision.
Wait for all other 5 hats to respond, then synthesize into:

## Decision Analysis: [THE DECISION]

### Summary
[2-3 sentence overview of the decision and core tension]

### Hat-by-Hat
- **White:** [key facts]
- **Red:** [emotional/intuitive read]
- **Black:** [risks and concerns]
- **Yellow:** [benefits and optimism]
- **Green:** [creative alternatives]

### Recommendation
[CLEAR recommendation with confidence level: High/Medium/Low]

### Key Insight
[The single most important thing to consider]
```

**Step 4: Present results**
After both waves complete, relay the Blue Hat synthesis to the user. Be concise in Telegram — summarize rather than dumping all 6 hat analyses raw.

## Config Note
If user wants all 6 running simultaneously, patch `~/.hermes/config.yaml`:
```yaml
delegation:
  max_concurrent_children: 6
```
Default is 3 (won't fit 6 sub-agents in one call — must wave or increase limit).

## Pitfalls
- Blue Hat MUST wait for all other 5 — don't rush the synthesis
- Each hat must ONLY argue from its own perspective — no hat-switching mid-analysis
- If user asks a follow-up decision, you can re-run the same workflow without re-confirming the decision
