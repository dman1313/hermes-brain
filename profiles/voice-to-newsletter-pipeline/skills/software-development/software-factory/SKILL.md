---
name: software-factory
description: Reference architecture for building a governed, multi-agent software delivery system. Maps factory roles to the agent ecosystem, identifies gaps, and provides a phased rollout plan. Use when designing agent workflows, planning SDLC automation, or evaluating agent coverage.
---

# Software Factory with Agents

Reference architecture for a governed, multi-agent software delivery system. Design the factory as a production system with specialized agents, explicit workflow stages, external state management, and hard validation gates.

## Operating Model

Five layers: **intake → orchestration → execution → validation → feedback**

Incoming requests → structured work items → routed to specialized agents → isolated implementation → automated + policy review → post-merge verification → production monitoring.

## Agent Roles (Mapped)

| Factory Role | Our Agent / Tool | Status |
|---|---|---|
| Intake / PM | Special Ops, framing-doc skill | Active |
| Planner / Orchestrator | HAL, Opus Strategic Planner | Active |
| Engineer agents | Kimi CLI, Codex, opencode | Active |
| Review / Architecture | Scotty, Sherlock | Active |
| QA / Cleanup | MrClean, DREAM audits | Active |
| Shepherd / Merge | Ralph (fixer, merger, reviewer) | Installed |
| Incident responder | Incident Responder (Red) | Active |
| QA / Verification | QA Agent (Checker) | Active |
| Shepherd / Monitor | Shepherd Agent (Shep) | Active |

## Reference Architecture

Event-driven, stateful loop:
1. Intake from GitHub, Linear, Slack, transcripts → normalized spec
2. Task decomposition → small testable units with dependency edges
3. Parallel execution in sandboxed branches/worktrees
4. Mandatory gates: build, lint, typecheck, tests, policy, architecture review
5. Merge → deploy → smoke checks → post-merge verification → feed incidents back

**Key principle:** Workflow state lives outside the model — in a control plane (Linear, GitHub Projects, Ralph routing), not buried in prompts or chat history.

## Guardrails

- Small tasks, tightly scoped context windows
- Separate sessions per task (no endlessly extended conversations)
- Role-based permissions / minimal tool access per agent
- Structured definitions of done with acceptance criteria
- Human escalation for risk, judgment, and architecture tradeoffs
- Fail loudly — don't improvise around uncertainty

## Gaps to Fill

~~1. **Incident Responder**~~ ✅ Created — Incident Responder (Red)
~~2. **QA Agent**~~ ✅ Created — QA Agent (Checker)  
~~3. **Shepherd Agent**~~ ✅ Created — Shepherd Agent (Shep)
4. **Ralph Configuration** — `.ralphrc` not yet set up with a provider
5. **Post-merge Verification** — smoke tests after deploy, automated rollback on failure
6. **Self-auditing Loop** — extend DREAM nightly reflection to factory metrics

## Rollout Plan

| Phase | Scope | Status |
|---|---|---|
| 1 | Intake + engineer + CI gates for one repo/one work type | Basic |
| 2 | Review + QA + merge queue automation | Partial (Ralph installed, not configured) |
| 3 | Post-merge verification + incident response | Not started |
| 4 | Measurement + factory self-auditing | Not started |

## Wiki

Full architecture doc: [[software-factory-agents]]
