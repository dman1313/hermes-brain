# Agent Profile: agent-router

This Hermes profile was generated from `~/.hermes/skills/agents/agent-router/SKILL.md`.

---
name: agent-router
description: "Route Telegram slash commands to Hermes agent skills and subagents. Native Hermes routing — no external dependencies."
version: "1.0.0"
created: "2026-05-04"
owner: Dwayne
---

# Agent Router

Native Hermes routing layer for Telegram slash commands. Maps commands to agent skills and dispatches via skill loading or subagent delegation.

## Trigger

When a Telegram message starts with `/` followed by a recognized agent command, load this skill and route accordingly.

## Recognized Slash Commands

| Command | Agent Skill | Role | Routing Method |
|---------|------------|------|---------------|
| `/mrclean` | `mrclean` | Cleanup & efficiency auditor | skill → execute inline |
| `/scotty` | `scotty` | System architect & skill builder | skill → execute inline |
| `/sherlock` | `sherlock` | Research investigator | skill → execute inline |
| `/zen` | `zen-agent` | Wellness coach | skill → execute inline |
| `/dream` | `dream` | Nightly reflection engine | skill → execute inline |
| `/hal` | `hal` | Orchestration layer | skill → execute inline |
| `/specialops` | `special-ops` | Mission control & cross-domain router | skill → execute inline |
| `/incident` | `incident-responder` | Incident triage & response | skill → delegate_task |
| `/qa` | `qa-agent` | Test execution & validation | skill → delegate_task |
| `/shepherd` | `shepherd-agent` | Stuck work monitoring | skill → delegate_task |
| `/pipeline` | `voice-to-newsletter-pipeline` | Newsletter pipeline orchestration | skill → execute inline |
| `/draft` | `voice-to-newsletter-pipeline` | Pipeline: drafting stage | routed through pipeline skill |
| `/polish` | `voice-to-newsletter-pipeline` | Pipeline: polishing stage | routed through pipeline skill |
| `/packager` | `voice-to-newsletter-pipeline` | Pipeline: packaging stage | routed through pipeline skill |
| `/marketing` | `marketing-pipeline` | Marketing suite: audit URLs, build landing pages, generate copy, emails, visuals, video scripts | skill → execute inline |
| `/strategic` | `Strategic Planner Framework` | Strategic planning layer | skill → execute inline |

## Routing Logic

1. **Parse** — Extract the command and any trailing text (query/context)
2. **Map** — Look up the command in the table above
3. **Route** — Based on the Routing Method column:
   - **execute inline**: Load the agent skill with `skill_view(name)`, adopt its persona, and execute. The skill's instructions guide the response.
   - **delegate_task**: Spawn a subagent with the target skill as context. The subagent loads the skill internally and returns results.
4. **Respond** — Deliver results back to the user in the same chat

## Inline Execution

For agents routed inline, load the skill and fully embody its persona:
- Adopt the agent's tone, identity, and operating rules
- Follow the skill's workflow/loop exactly
- Use the agent's name in responses when appropriate
- Respect all guardrails and boundaries defined in the skill

## Delegated Execution

For agents routed via subagent, craft a self-contained context:
- Include the slash command query text
- Reference the agent's skill name so the subagent can load it
- Specify the expected output format
- Route results back to the user

## Unknown Commands

If a slash command doesn't match any known agent, respond with:
"Unknown command. Available: /mrclean, /scotty, /sherlock, /zen, /dream, /hal, /specialops, /incident, /qa, /shepherd, /pipeline, /draft, /polish, /packager, /marketing, /strategic"

## Notes

- All routing is native to Hermes — no external daemon or workspace required
- Subagent commands run in isolated contexts and return summaries
- Inline agents share the current conversation context
- `/draft`, `/polish`, `/packager` are handled by loading the `voice-to-newsletter-pipeline` skill with the appropriate stage flag
