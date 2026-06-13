---
name: kanban
description: "Hermes Kanban multi-agent system — orchestrator decomposition playbook and worker pitfalls. Covers task routing, dependency management, worker lifecycle, handoff patterns, and stuck-worker recovery."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
environments: [kanban]
metadata:
  hermes:
    tags: [kanban, multi-agent, orchestration, routing, workflow, collaboration]
    related_skills: [hermes-agent]
---

# Hermes Kanban — Multi-Agent Task System

The Kanban system routes work through specialist profiles. Two roles exist: **orchestrators** (decompose and route) and **workers** (execute and hand off). The core worker lifecycle (6 steps: orient → work → heartbeat → block/complete) is auto-injected into every worker's system prompt as `KANBAN_GUIDANCE` from `agent/prompt_builder.py`. This skill is the deeper playbook for both roles.

---

## Orchestrator — Decomposition Playbook

> The orchestrator skill is what you load when you're specifically playing the orchestrator role — routing work, not executing it.

### Profiles are user-configured — not a fixed roster

Hermes setups vary widely. Some users run a single profile that does everything; some run a small fleet; some run a curated specialist team. There is **no default specialist roster**.

Before fanning out, you must ground the decomposition in the profiles that actually exist. The dispatcher silently fails to spawn unknown assignee names.

**Step 0: discover available profiles before planning.**

Use one of these:
- `hermes profile list` — prints the table of profiles configured on this machine
- `kanban_list(assignee="<some-name>")` — sanity-check a single name
- **Just ask the user.** "What profiles do you have set up?" is a fine first turn

### When to use the board (vs. just doing the work)

Create Kanban tasks when any of these are true:

1. **Multiple specialists are needed.** Research + analysis + writing is three profiles.
2. **The work should survive a crash or restart.** Long-running, recurring, or important.
3. **The user might want to interject.** Human-in-the-loop at any step.
4. **Multiple subtasks can run in parallel.** Fan-out for speed.
5. **Review / iteration is expected.** A reviewer profile loops on drafter output.
6. **The audit trail matters.** Board rows persist in SQLite forever.

If *none* of those apply — it's a small one-shot reasoning task — use `delegate_task` instead or answer the user directly.

### The anti-temptation rules

Your job description says "route, don't execute." The rules that enforce that:

- **Do not execute the work yourself.** If you find yourself "just fixing this quickly" — stop and create a task for the right specialist.
- **For any concrete task, create a Kanban task and assign it.** Every single time.
- **Split multi-lane requests before creating cards.** A user prompt can contain several independent workstreams. Extract those lanes first, then create one card per lane.
- **Run independent lanes in parallel.** If two cards do not need each other's output, leave them unlinked.
- **Never create dependent work as independent ready cards.** If a card must wait for another card, pass `parents=[...]` in the original `kanban_create` call.
- **If no specialist fits the available profiles, ask the user.** Do not invent profile names; the dispatcher will silently drop unknown assignees.
- **Decompose, route, and summarize — that's the whole job.**

### Decomposition Steps

**Step 1 — Understand the goal.** Ask clarifying questions if ambiguous.

**Step 2 — Sketch the task graph.** Before creating anything, draft the graph out loud:

1. Extract the lanes from the request.
2. Map each lane to one of the profiles you discovered in Step 0.
3. Decide whether each lane is independent or gated by another lane.
4. Create independent lanes as parallel cards with no parent links.
5. Create synthesis/review/integration cards with parent links.

**Step 3 — Create tasks and link.** Use the profile names from Step 0:

```python
t1 = kanban_create(
    title="research: Postgres cost vs current",
    assignee="<profile-A>",
    body="Compare estimated infrastructure costs...",
    tenant=os.environ.get("HERMES_TENANT"),
)["task_id"]

t2 = kanban_create(
    title="research: Postgres performance vs current",
    assignee="<profile-A>",
    body="Compare query latency, throughput...",
)["task_id"]

t3 = kanban_create(
    title="synthesize migration recommendation",
    assignee="<profile-B>",
    body="Read the findings from T1 (cost) and T2 (performance)...",
    parents=[t1, t2],
)["task_id"]
```

`parents=[...]` gates promotion — children stay in `todo` until every parent reaches `done`, then auto-promote to `ready`.

**Step 4 — Complete your own task.** Mark it done with a summary of what you created.

**Step 5 — Report back to the user.** Tell them what you created in plain prose.

### Common Patterns

**Fan-out + fan-in (research → synthesize):** N research-style cards with no parents, one synthesis card with all of them as parents.

**Parallel implementation + validation:** one implementer card makes the change while one explorer/researcher card verifies config, docs, or source mapping.

**Pipeline with gates:** `planner → implementer → reviewer`. Each stage's `parents=[previous_task]`.

**Same-profile queue:** N tasks, all assigned to the same profile, no dependencies between them. Dispatcher serializes.

**Human-in-the-loop:** Any task can `kanban_block()` to wait for input. Dispatcher respawns after `/unblock`.

### Goal-mode cards (persistent workers)

For open-ended cards where one turn rarely finishes the job, pass `goal_mode=True`:

```python
kanban_create(
    title="Translate the full docs site to French",
    body="Acceptance: every page translated, no English left, links intact.",
    assignee="<translator-profile>",
    goal_mode=True,
    goal_max_turns=15,
)["task_id"]
```

After each worker turn, an auxiliary judge evaluates the worker's response against the card's title + body. Not done + budget remains → the worker keeps going. Budget exhausted → the card is blocked for human review.

### Recovering stuck workers

When a worker profile keeps crashing, hallucinating, or getting blocked:

1. **Reclaim** (`hermes kanban reclaim <task_id>`) — abort the running worker immediately and reset the task to `ready`.
2. **Reassign** (`hermes kanban reassign <task_id> <new-profile> --reclaim`) — switch the task to a different profile.
3. **Change profile model** — edit profile config, then Reclaim to retry with the new model.

### Orchestrator Pitfalls

- **Inventing profile names that don't exist.** The dispatcher silently fails. Always assign to a profile from Step 0 discovery.
- **Bundling independent lanes into one card.** If the user asks for two independent outcomes, create two cards.
- **Over-linking because of wording.** "Finally check X" may still be parallel with implementation.
- **Forgetting dependency links.** Use parent links so implement/review cannot run before their inputs exist.
- **Reassignment vs. new task.** If a reviewer blocks with "needs changes," create a NEW task linked from the reviewer's task.
- **Don't pre-create the whole graph if the shape depends on intermediate findings.** Orchestrators can spawn orchestrators.

---

## Worker — Pitfalls and Examples

> The worker skill is what you load when you want deeper detail on specific scenarios. The lifecycle itself is auto-injected via KANBAN_GUIDANCE.

### Workspace handling

| Kind | What it is | How to work |
|---|---|---|
| `scratch` | Fresh tmp dir, yours alone | Read/write freely; it gets GC'd when the task is archived. |
| `dir:<path>` | Shared persistent directory | Other runs will read what you write. Treat it like long-lived state. |
| `worktree` | Git worktree at the resolved path | If `.git` doesn't exist, run `git worktree add <path> ${HERMES_KANBAN_BRANCH:-wt/$HERMES_KANBAN_TASK}` first. |

### Tenant isolation

If `$HERMES_TENANT` is set, prefix memory entries with the tenant so context doesn't leak:
- Good: `business-a: Acme is our biggest customer`
- Bad (leaks): `Acme is our biggest customer`

### Good summary + metadata shapes

The `kanban_complete(summary=..., metadata=...)` handoff is how downstream workers read what you did.

**Coding task:**
```python
kanban_complete(
    summary="shipped rate limiter — token bucket, keys on user_id with IP fallback, 14 tests pass",
    metadata={
        "changed_files": ["rate_limiter.py", "tests/test_rate_limiter.py"],
        "tests_run": 14,
        "tests_passed": 14,
        "decisions": ["user_id primary, IP fallback for unauthenticated requests"],
    },
)
```

**Coding task that needs human review:**
```python
kanban_comment(
    body="review-required handoff:\n" + json.dumps({
        "changed_files": ["rate_limiter.py", "tests/test_rate_limiter.py"],
        "tests_run": 14,
        "tests_passed": 14,
    }, indent=2),
)
kanban_block(
    reason="review-required: rate limiter shipped, 14/14 tests pass — needs eyes on the user_id/IP fallback choice before merging",
)
```

Use `kanban_complete` only when the task is genuinely terminal — one-line typo fix, docs change, or research task where the artifact IS the writeup.

### Claiming cards you actually created

If your run produced new kanban tasks, pass the ids in `created_cards` on `kanban_complete`. The kernel verifies each id exists and was created by your profile.

```python
c1 = kanban_create(title="remediate SQL injection", assignee="security-worker")
c2 = kanban_create(title="fix CSRF middleware", assignee="web-worker")

kanban_complete(
    summary="Review done; spawned remediations for both findings.",
    metadata={"pr_number": 123, "approved": False},
    created_cards=[c1["task_id"], c2["task_id"]],
)
```

**NEVER claim ids you don't have captured return values for.** Phantom ids block the completion.

### Block reasons that get answered fast

Bad: `"stuck"` — the human has no context.

Good: one sentence naming the specific decision you need. Leave longer context as a comment instead.

```python
kanban_comment(
    task_id=os.environ["HERMES_KANBAN_TASK"],
    body="Full context: I have user IPs from Cloudflare headers but some users are behind NATs...",
)
kanban_block(reason="Rate limit key choice: IP (simple, NAT-unsafe) or user_id (requires auth, skips anonymous endpoints)?")
```

### Heartbeats worth sending

Good heartbeats name progress: `"epoch 12/50, loss 0.31"`, `"scanned 1.2M/2.4M rows"`.

Bad heartbeats: `"still working"`, empty notes, sub-second intervals.

### Retry scenarios

If `kanban_show` returns `runs: [...]` with one or more closed runs, you're a retry:

- `outcome: "timed_out"` — hit `max_runtime_seconds`. Chunk the work or shorten it.
- `outcome: "crashed"` — OOM or segfault. Reduce memory footprint.
- `outcome: "spawn_failed"` — usually a profile config issue. Ask the human via `kanban_block`.
- `outcome: "blocked"` — a previous attempt blocked; the unblock comment should be in the thread.

### Worker Do NOTs

- **Do NOT call `delegate_task` as a substitute for `kanban_create`.** `delegate_task` is for short reasoning subtasks inside YOUR run; `kanban_create` is for cross-agent handoffs that outlive one API loop.
- **Do NOT call `clarify` to ask the human a question.** You are running headless — there is no live user to answer. Use `kanban_comment` + `kanban_block(reason=...)` instead.
- **Do NOT modify files outside `$HERMES_KANBAN_WORKSPACE`** unless the task body says to.
- **Do NOT create follow-up tasks assigned to yourself** — assign to the right specialist.
- **Do NOT complete a task you didn't actually finish.** Block it instead.

### Worker Pitfalls

- **Task state can change between dispatch and your startup.** Always `kanban_show` first. If it reports `blocked` or `archived`, stop.
- **Workspace may have stale artifacts.** Read the comment thread — it usually explains why you're running again.
- **Don't rely on the CLI when the guidance is available.** The `kanban_*` tools work across all terminal backends. `hermes kanban <verb>` from your terminal tool will fail in containerized backends.

### CLI fallback (for scripting)

Every tool has a CLI equivalent:
- `kanban_show` ↔ `hermes kanban show <id> --json`
- `kanban_complete` ↔ `hermes kanban complete <id> --summary "..." --metadata '{...}'`
- `kanban_block` ↔ `hermes kanban block <id> "reason"`
- `kanban_create` ↔ `hermes kanban create "title" --assignee <profile> [--parent <id>]`

Use the tools from inside an agent; the CLI exists for the human at the terminal.

### Notification routing

Configure the gateway to receive cross-profile Kanban task notifications by adding `notification_sources` to `~/.hermes/config.yaml`.
- `notification_sources: ['*']` accepts subscriptions from all profiles.
- `notification_sources: ['default', 'zilor-ppt']` restricts to specified profiles.
