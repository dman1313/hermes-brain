---
name: codebase-audit
description: Security and code quality audit of one or more codebases using parallel subagents. Produces a structured report with severity levels. Use when asked to review, audit, or check code for vulnerabilities, bugs, or quality issues.
---

# Codebase Audit

Audit one or more codebases for security, code quality, and domain-specific correctness using parallel subagents.

## When to Use

- "Audit this code" / "Review for security" / "Check for bugs"
- Multi-repo or multi-module reviews where parallelism saves time
- Trading/financial code where correctness matters especially

## Steps

### 1. Identify Audit Targets

Map the codebases to audit. Check these common locations:
- Skills: `~/.hermes/skills/<domain>/<name>/`
- Projects: `~/project-name/`
- Ask the user if ambiguous

### 2. Split Into Parallel Tasks

Group related codebases into 2-4 balanced subagent tasks. Rules:
- Each subagent gets 1-3 related codebases (not more — context limits)
- Separate by domain (e.g., trading skills vs ML pipeline)
- Each subagent reads ALL code files in its assigned targets

### 3. Define Audit Axes

Standard axes (include all, add domain-specific ones as needed):

1. **Security vulnerabilities** — injection, path traversal, auth gaps
2. **API key/secret handling** — plaintext keys, world-readable files, key logging
3. **Code quality** — error handling, type safety, dead code, serialization bugs
4. **Domain correctness** — financial logic, data leakage (ML), protocol compliance
5. **Risk management** — position limits, circuit breakers, rate limiting

### 4. Run Parallel Subagents

```
delegate_task(tasks=[
  {goal: "Audit <targets> for <axes>. Read all code files, produce structured report with severity levels.", toolsets: ["terminal", "file"]},
  {goal: "Audit <targets> for <axes>. Read all code files, produce structured report with severity levels.", toolsets: ["terminal", "file"]},
  ...
])
```

Each subagent prompt should include:
- Exact file paths to audit
- The 5 audit axes
- Output format: severity levels (🔴 Critical, 🟠 High, 🟡 Medium, 🟢 Low)

### 5. Consolidate Results

Merge subagent reports into a single report:
- Summary table (per-codebase severity counts)
- Top 5 most urgent fixes (regardless of source)
- Positive findings (what's done well)
- Save to `~/audit-report-<topic>.md`

### 6. Fix Critical Issues Immediately

If any 🔴 Critical findings are trivially fixable (e.g., `chmod 600` on a token file), fix them during the audit. Report what was fixed vs what needs user decision.

## Output Format

```markdown
# <Topic> Audit Report
**Date:** YYYY-MM-DD

## Summary
| Codebase | 🔴 Critical | 🟠 High | 🟡 Medium | 🟢 Low |
|---|---|---|---|---|

## 🔴 TOP CRITICAL FIXES
(Numbered list with file, issue, and fix)

## Full Findings by Codebase
(Structured per-codebase breakdown)

## Positive Findings
(What's done well)
```

## Pitfalls

- **Don't use orchestration-heavy frameworks for code review.** Ruflo's hive-mind burned $1.08 and 35 turns producing zero output — the system prompt alone consumed the entire context window. Direct `delegate_task` with parallel subagents does the same job for ~$0.15 in seconds.
- **Don't let subagents audit more than 3 codebases each.** Context limits kill them. Split narrowly.
- **Include `terminal` in toolsets.** Subagents need `ls`, `find`, and permission checks — not just file reads.
- **Fix trivial criticals immediately.** A `chmod 600` takes 1 second and eliminates a real risk. Don't just report it.
- **Save the report to a file.** Don't only display in chat — it's too long for Telegram and gets lost.
