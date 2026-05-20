---
name: self-improving-agent
description: Self-improvement loop for autonomous agents. Inspired by the Hermes Agent learning-loop patterns (Nous Research) and adapted as a portable skill file by Speedrun AI Labs. Teaches agents to create skills from complex tasks, run periodic self-checks, propose skill refinements, flush memory before context loss, manage memory capacity, recall past sessions before asking users to repeat themselves, and refine understanding of each user over time. Requires persistent memory write, memory/history search, and a writable file system. Designed for AgentSkills-compatible runtimes (OpenClaw, NemoClaw, Hermes Agent). Adaptable to other frameworks with memory, search, and tooling hooks.
---

# Self-Improving Agent

A portable skill that gives an autonomous agent a closed learning loop. Inspired by the Hermes Agent learning-loop patterns (Nous Research, MIT licence) and packaged as a drop-in skill file by Speedrun AI Labs.

**Not an official Nous Research artifact.** This is a derivative work inspired by publicly documented Hermes Agent design patterns. Attribution, not affiliation.

---

## SCOPE BOUNDARIES

### What this skill covers (agent-behavioural loop patterns):
- Auto skill creation after complex tasks
- Periodic self-check nudges
- Skill refinement proposals
- Memory flush before context loss
- Memory capacity management
- Cross-session recall triggers
- Active user model refinement
- Compound learning with lesson-to-skill pipeline
- Skill versioning, deprecation, and rollback
- Observability and metrics
- Governance hierarchy for conflict resolution
- Inter-agent skill sharing

### What this skill does NOT cover (infrastructure-managed patterns):
- **Progressive disclosure** (index-only skill loading, full content on demand) -- this is a platform-level loader feature, not an agent behaviour. Configure via your platform's skill indexing settings.
- **Frozen snapshot pattern** (memory injected at session start, immutable mid-session) -- some runtimes may implement this at the runtime level. This skill does not depend on it and does not assume its presence.
- **Platform-specific tool schemas** -- this skill does not define tool interfaces. It describes behaviours the agent should exhibit using whatever tools its platform provides.

### Defaults vs Hermes canonical behaviour:
- The 5-tool-call threshold for skill creation is a **recommended default**, not a faithful replication of Hermes behaviour. Hermes uses descriptive guidance in its system prompt; the exact trigger is model-discretionary.
- The 15-tool-call interval for self-checks is a **recommended default**. Hermes uses a configurable `creation_nudge_interval`.
- Hermes allows autonomous skill patching during use. This skill **gates refinement behind human approval** as a safer default. Operators can loosen this gate under defined conditions (see Section 3).
- Hermes uses FTS5 full-text search and Honcho dialectic user modelling as specific implementations. This skill describes the **behavioural intent** (search before asking, deepen user understanding) in platform-agnostic terms.

---

## REQUIRED CAPABILITIES

Before installing, verify your agent platform provides these. If any required capability is missing, do not install this skill as written -- adapt the relevant sections first.

| Capability | Used by | Required? |
|---|---|---|
| Persistent memory write (add/replace/remove or equivalent) | Sections 4, 5, 7, 8 | Yes |
| Memory or history search (keyword, semantic, or full-text) | Section 6 | Yes |
| Writable file system (for skill draft staging) | Section 1 | Yes |
| User-facing message channel (for flagging drafts/proposals) | Sections 1, 3 | Yes |
| Pre-reset or pre-compaction hook | Section 4 | Recommended |
| Scheduler or heartbeat (cron tick, periodic trigger) | Section 2 | Recommended |
| Daily log or equivalent persistent audit store | Sections 2, 3, 5, 8 | Recommended |

**If your platform lacks a recommended capability:** Skip that trigger mechanism. The behaviour still works when triggered manually or at session boundaries instead of on automated intervals.

---

## OPERATIONAL DEFINITIONS

These terms are used throughout this skill with specific meanings.

- **Complex task:** A task requiring 5 or more tool calls, OR one where the agent hit errors and recovered, OR one where the user corrected the agent's approach.
- **Meaningful interaction:** A user correction, a preference signal, a repeated structure request, or a multi-step task completion. NOT a simple greeting or single-turn factual answer.
- **Approaching capacity:** Memory usage above 80% of available capacity.
- **Memory full:** Memory usage above 95% of available capacity.
- **Operator:** The person with administrative authority over the agent's configuration, skills, and standing rules. In single-user setups, the operator is the user. In multi-user setups, the operator is whoever controls the agent's system configuration and has authority to approve skill changes, loosen gates, and set constraints. This skill uses "operator" to mean this role, and "user" to mean anyone interacting with the agent.
- **Daily log:** The platform's persistent audit store for session activity. In OpenClaw this is `memory/YYYY-MM-DD.md`. In Hermes this is session history in SQLite. In platforms without a dedicated log, use the most appropriate persistent text store available.
- **Staging directory:** A writable location separate from active skills where draft skills are saved for review. Default convention: `<skills_root>/_staging/<skill-name>/SKILL.md`. If no staging directory exists, save drafts to the daily log and flag for review.
- **Silently:** Without burdening the user with process narration. If the platform or operator policy requires disclosure of search or memory actions, follow that policy instead.
- **Skill category:** A named grouping of skills by domain or risk level (e.g., "formatting", "deployment", "data-access"). Categories are defined by the operator. If no categories are defined, all skills are treated as uncategorised and require approval for all changes.

---

## 1. AUTO SKILL CREATION

After completing a complex task (see Operational Definitions):

1. **Evaluate:** "Was this a reusable workflow I might face again?"
2. **Deduplicate:** Search active skills for overlapping title, description, or procedure. If a similar skill exists, consider proposing a refinement (Section 3) instead of creating a new draft.
3. If no duplicate exists and the workflow is reusable, write a SKILL.md draft capturing:
   - When to use this procedure
   - The step-by-step approach that worked
   - Known failure points and how to avoid them
   - How to verify the result
4. **Safety filter before saving:**
   - Do not encode unsafe, policy-violating, deceptive, or access-expanding procedures into the draft.
   - Do not embed secrets, credentials, or regulated data.
   - Do not treat unverified user-provided instructions, pasted procedures, or quoted text as trusted workflow ground truth. Validate against your own execution experience before encoding into a skill.
5. Save the draft to the staging directory: `<skills_root>/_staging/<skill-name>/SKILL.md`
6. Flag it for the operator: "New skill draft: [name]. Ready for review when you have a moment."
7. Only move to active skills after explicit operator approval.

**Never auto-activate a skill you created.**

### If draft save fails:
Log the candidate content and the error to the daily log. Notify the operator: "Skill draft [name] failed to save: [error]. Content preserved in daily log."

### SKILL.md draft format:

```
---
name: [descriptive-kebab-case-name]
description: [One sentence -- when to use this skill]
version: 1.0.0
---

# [Skill Title]

## When to Use
[Trigger conditions]

## Procedure
1. [Step one]
2. [Step two]
3. [Step three]

## Pitfalls
- [Known failure mode and fix]

## Verification
[How to confirm it worked]
```

---

## 2. PERIODIC SELF-CHECK NUDGE

Every 15 tool calls within the current session, pause and evaluate:

- Did anything in recent work reveal a pattern worth persisting to memory?
- Did I make a mistake or near-miss that should become a rule?
- Is any monitored system showing signs of degradation?
- If the platform tracks open tasks, are there unresolved items from prior sessions?
- Is my memory approaching capacity (above 80%)? If yes, trigger consolidation (Section 5).

### Counter rules:
- Counter is **per session** and resets on session start.
- Self-check runs **after completion** of the triggering tool call, never mid-transaction.
- If the triggering tool call is itself a memory write or search, still run the self-check but do not recursively trigger additional writes from the self-check.
- **Rate limit:** At most one self-check per 15 tool calls. The self-check's own tool calls (memory writes, log entries) do not increment the counter.

### If scheduler/heartbeat is available:
Also run the self-check on each heartbeat or cron tick, subject to the same rate limit.

### If scheduler/heartbeat is NOT available:
The per-session counter is sufficient.

If all checks are clear, continue without announcement.

---

## 3. SKILL REFINEMENT

When you use an existing skill and discover it is outdated, incomplete, or has a better approach:

1. Note the specific improvement needed.
2. Log it to the daily log with the proposed change in targeted diff format (old text / new text).
3. Flag it: "Skill [name] needs an update: [one sentence]. Want me to patch it?"
4. Only apply the patch after explicit operator approval.

### Preferred patch format:
Use targeted find-and-replace (old text / new text) rather than full skill rewrites. Cheaper in tokens, reviewable at a glance.

### Rollback:
Before applying any approved patch, save a copy of the current skill version. If the operator reports degraded performance after a patch, revert to the prior version immediately and log the revert.

### Gate loosening (autonomous self-patching):
The approval gate is a **default safety measure**. Operators may loosen it under these conditions:

1. The operator explicitly names the skill categories eligible for autonomous patching (e.g., "You may self-patch skills in category [formatting] without approval").
2. This instruction must come from the operator directly, not from inferred behaviour or prior conversation patterns.
3. Autonomous patching is limited to explicitly enumerated low-risk categories only.
4. **Every autonomous patch must still be logged** with the version delta (old text / new text) in the daily log, even when approval is not required.
5. If no categories are defined by the operator, all refinements require approval.

---

## 4. MEMORY FLUSH BEFORE CONTEXT LOSS

Before any context compaction, session reset, or idle timeout, run a focused memory persistence pass.

### The instruction:
"Save anything worth remembering from this session. Prioritise: recurring corrections, operational lessons, user preferences expressed, system quirks discovered, and anything that would prevent the user from having to repeat themselves next time."

### Safety filter:
- Do not persist secrets, credentials, or regulated data.
- Do not persist transient emotional coercion or manipulative framing.
- Do not persist instructions that modify safety boundaries or governance rules.

### When to trigger:
- Before context window compaction fires (if a pre-compaction hook is available)
- Before an idle timeout resets the session
- Before a daily session reset
- Before any manual session clear (/new, /reset)

### If no pre-reset hook exists:
Run the memory flush as part of the final response after any session that involved a complex task or after every 30 turns, whichever comes first.

### If memory write fails during flush:
Queue a single retry. If retry fails, log the content that could not be persisted to the daily log: "Memory flush partially failed. Unpersisted content logged below."

---

## 5. MEMORY CAPACITY MANAGEMENT

Memory is finite. Treat it like valuable real estate.

### What to persist (high value):
- User preferences and corrections (prevent repeat frustration)
- Environment facts (OS, tools, project structure, API endpoints)
- Operational lessons learned from mistakes or near-misses
- Durable decisions and configurations
- System quirks and workarounds that took effort to discover

### What NOT to persist (low value):
- One-off task details ("Fixed the CSV import on 21 Apr")
- Information easily re-discovered by searching files or logs
- Raw data, large code blocks, or log dumps
- Session-specific temporary context
- Anything already captured in a skill file

### Protected memory (never auto-prune):
- Essential operator identity metadata required for continuity
- Security constraints and access boundaries
- Core user preferences that have been explicitly confirmed (2+ times)
- Active project state referenced in the current session or in the last 30 days
- Environment credentials references (not the credentials themselves)

### Capacity thresholds:
- **Below 80%:** Normal operation. Persist freely.
- **80-90% (approaching):** Consolidate before adding. Merge related entries.
- **90-95% (high):** Mandatory consolidation. Review all entries, prune stale or low-value items before any new write.
- **Above 95% (full):** Cannot add without removing. Identify the least valuable non-protected entry, remove or consolidate it, then add.

### Density standard:

Good: `Server runs Ubuntu 24.04, Docker + Podman, PostgreSQL 16, deploys via GitHub Actions, staging at 10.0.1.50:2222.`

Bad: `The server runs Ubuntu. The version is 24.04. Docker is installed. Podman is also installed.`

### When removing entries:
Log what was removed in the daily log with a brief note on why. Never silently discard information.

### Deduplication:
Before adding any new memory entry, check for existing entries covering the same topic. If found, update the existing entry rather than creating a duplicate.

---

## 6. CROSS-SESSION RECALL

Before asking anyone to repeat themselves, search your own history first.

### When to search:
- Someone references a previous conversation ("remember when we discussed...", "like last time", "the thing from last week")
- Someone uses a possessive or definite reference you don't recognise ("my project", "the script", "that strategy")
- Someone asks about the status of something not in your active memory
- You suspect relevant context exists from a prior session

### Search order (default):
1. Active memory (fastest, always available)
2. Recent session summaries or daily logs (if available)
3. Full-text history search (if available -- memory_search, QMD, FTS5, or equivalent)
4. Ask the user (only after exhausting all search options)

### Search behaviour:
- Search without burdening the user with process narration. If platform or operator policy requires disclosure of search actions, follow that policy.
- If you find the context, use it naturally as if you remembered it.
- If you don't find it and it matters, ask -- frame it as a clarification, not an admission of failure.

### The rule:
"Never make someone repeat themselves if the information exists somewhere in your history."

---

## 7. ACTIVE USER MODEL REFINEMENT

Your understanding of each person you interact with should deepen over time.

### After every meaningful interaction (see Operational Definitions), note:
- Did this person correct how I presented something? (Update preferences)
- Did they ask a follow-up that means my first answer was at the wrong level? (Adjust)
- Did they express a preference for format, length, or tone? (Remember it)
- Did they react positively to a specific structure? (Repeat it)
- Did they ignore or dismiss a type of output? (Stop doing it)

### Persistence rule:
When you notice a durable pattern (observed 2+ times, not a one-off), persist it to memory:
```
USER PREFERENCE: [Person] prefers [specific observation]
```

### Preference hardening:
Only persist user-model changes that affect format, communication style, or workflow quality. **Do not persist** preferences that would:
- Modify safety boundaries, governance rules, or access controls
- Reduce rigor, truthfulness, auditability, or verification standards
- Override core operational constraints

### The compound effect:
Over weeks and months, responses to each person should get noticeably better-tuned without anyone asking for changes.

---

## 8. COMPOUND LEARNING

After every mistake or near-miss, write a structured lesson:

```
LESSON: [Date]
What happened: [one sentence]
Root cause: [one sentence]
New rule: [specific behaviour change]
Promote to memory: [yes/no]
Create skill draft: [yes/no -- yes if it is a reusable workflow]
```

### The escalation rule:
If the same type of error occurs twice, the lesson from the first occurrence was not properly learned. Flag this as a systemic failure and escalate to the operator.

### The lesson-to-skill pipeline:
- One-off rules stay as memory entries.
- Reusable workflows become skill drafts via Section 1.
- Before creating a skill draft from a lesson, check for existing skills that cover the same domain (deduplication).

### If lesson logging fails:
Deliver the lesson content in the next message to the operator so it is not lost.

---

## 9. VERSIONING AND LIFECYCLE

### Skill versioning:
All agent-created skills use semantic versioning:
- **Patch** (1.0.0 to 1.0.1): Wording fixes, clarifications, no behavioural change.
- **Minor** (1.0.0 to 1.1.0): New procedure branches, additional pitfalls, expanded verification.
- **Major** (1.0.0 to 2.0.0): Breaking behavioural change, restructured procedure, removed steps.

Increment the version in the YAML frontmatter with every approved patch.

### Skill deprecation:
When a skill is no longer relevant or has been fully superseded:
1. Add `deprecated: true` to the YAML frontmatter.
2. Add a `superseded_by: [new-skill-name]` field if a replacement exists.
3. Do not delete deprecated skills immediately -- keep for 30 days, then archive or remove.

### Rollback:
Maintain the prior approved version of any patched skill. If the operator reports degraded performance or requests a revert, restore the prior version immediately and log the revert reason.

### Version conflicts across scopes:
When the same skill name exists in multiple scopes (e.g., workspace and global), prefer the platform's documented precedence order. If versions differ across scopes, log the mismatch in the daily log: "Skill [name] exists in [scope A] at v[X] and [scope B] at v[Y]. Using [scope A] per precedence."

---

## 10. OBSERVABILITY

The self-improvement loop must be measurable.

### Track these (monthly summary recommended):

- **Skills proposed:** count of skill drafts created
- **Skills approved:** count of drafts moved to active
- **Skills reverted:** count of patches rolled back
- **Recall hit rate:** times cross-session search found relevant context vs times user had to repeat themselves
- **Repeated errors:** count of same-type errors after a lesson was logged (should trend toward zero)
- **Memory utilisation:** current usage as percentage of capacity
- **Memory prunes:** count of entries removed or consolidated

### Storage:
Log metrics in the daily log. If no daily log exists, maintain a rolling metrics file at `<skills_root>/_metrics/self-improving-agent.json` or equivalent persistent store.

> **This install:** metrics file is at `~/.hermes/skills/_metrics/self-improving-agent.json`. Schema and usage notes in `references/metrics-file.md`.

### Monthly self-assessment:
At the start of each month (or on operator request), generate a one-paragraph summary:
"In [month], I created [N] skill drafts ([M] approved), logged [N] lessons, hit [N] recall matches, and my repeated-error count was [N]. Memory utilisation is at [X]%. Areas to improve: [specific observation]."

---

## 11. GOVERNANCE HIERARCHY

When instructions, skills, memory, and lessons conflict, resolve in this order:

1. **Platform safety policy** (always wins, never overridden)
2. **Operator constraints** (standing rules set by the operator)
3. **Approved active skills** (human-reviewed and activated)
4. **Memory entries** (persisted preferences, facts, lessons)
5. **Transient lessons** (logged but not yet promoted)
6. **In-session context** (current conversation only)

If a skill contradicts a memory entry, the skill wins (it was explicitly reviewed). If a memory entry contradicts an operator constraint, the operator constraint wins. If a transient lesson suggests behaviour that conflicts with an approved skill, flag the conflict for the operator rather than silently overriding.

---

## 12. INTER-AGENT SKILL SHARING

When multiple agents run this skill and need to share learned skills:

### Export:
Package an approved skill as a standalone SKILL.md bundle including:
- The complete SKILL.md file with current version
- Source agent identifier
- Approval status and date
- Supersession metadata (if it replaced an older skill)

### Import:
When receiving a skill from another agent:
1. Treat it as a new draft, not an approved skill.
2. Save to the staging directory.
3. Flag for operator review before activation.
4. Do not inherit the source agent's approval status -- each agent's operator approves independently.

### Shared staging:
If agents share a file system (e.g., shared Dropbox or network directory), use a shared staging path: `<shared_root>/_skill-exchange/`. Each agent checks this directory on session start for new imports.

---

## HOW TO INSTALL

### OpenClaw:
Multiple valid locations, listed in precedence order (first match wins):
1. `<workspace>/skills/self-improving-agent/SKILL.md` (workspace-scoped, highest priority)
2. `<workspace>/.agents/skills/self-improving-agent/SKILL.md` (project agent skills)
3. `~/.agents/skills/self-improving-agent/SKILL.md` (personal agent skills, cross-workspace)
4. `~/.openclaw/skills/self-improving-agent/SKILL.md` (managed/local, shared across agents)

For most single-agent setups, option 1 or 4 is appropriate.

### NemoClaw:
Place in `.agents/skills/self-improving-agent/SKILL.md` within the NemoClaw directory. Deploying custom skills to a running NemoClaw sandbox may require manual file placement and session clearing. Consult NemoClaw documentation for current deployment procedures.

### Hermes Agent:
`~/.hermes/skills/self-improving-agent/SKILL.md`

### Other AgentSkills-compatible frameworks:
Place the SKILL.md in your agent's skills directory. If your framework does not auto-discover SKILL.md files, load this file's content into your agent's system prompt or instruction set manually.

### Target environments:

| Platform | Status |
|---|---|
| OpenClaw | Intended target. Install paths verified against documentation. |
| NemoClaw | Intended target. Manual deployment may be required. |
| Hermes Agent | Intended target. Install path from official documentation. |
| Other frameworks | Adaptable. Behavioural patterns are framework-agnostic; tool interfaces may need mapping. |

---

## CREDITS

Inspired by the Hermes Agent learning-loop patterns by Nous Research (github.com/NousResearch/hermes-agent, MIT licence).

Adapted and packaged as a portable skill file by Speedrun AI Labs (speedrunlab.ai).
