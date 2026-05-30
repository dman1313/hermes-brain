---
name: parallel-codebase-audit
description: Audit multiple codebases in parallel for security, quality, and domain-specific issues, then immediately patch all findings. Uses batch delegate_task for speed.
triggers:
  - audit code
  - review codebases
  - security audit
  - check trading code
  - code quality review
  - multiple repos
---

# Parallel Codebase Audit

Audit multiple codebases simultaneously using parallel subagents, then immediately fix all findings.

## When to Use

- User says "audit", "review", "check" across multiple codebases/directories
- Security review needed across a portfolio of related code
- Code quality sweep before a deployment or milestone
- Any "check all of X" request where X has 3+ distinct codebases

## Architecture

```
User request
  │
  ├─→ Subagent 1: Audit codebase A (security + quality + domain)
  ├─→ Subagent 2: Audit codebase B (security + quality + domain)
  ├─→ Subagent 3: Audit codebase C (security + quality + domain)
  │
  └─→ Consolidate findings → Report → Parallel fix subagents
```

## Step 1: Scope the Audit

Before spawning subagents, identify:
- Which directories/codebases to audit
- What categories to check (see rubric below)
- Any domain-specific checks (trading, finance, healthcare, etc.)

## Step 2: Parallel Audit (Batch delegate_task)

Spawn 1 subagent per codebase (or logical group). Each subagent gets:

**Standard rubric (always include):**
1. **Security vulnerabilities** — hardcoded secrets, path traversal, injection, unsafe deserialization
2. **API key/secret handling** — plaintext storage, logging exposure, permission issues
3. **Code quality** — error handling, type safety, dead code, race conditions
4. **Input validation** — external data sources, subprocess output, user input

**Domain-specific rubric (add as needed):**
- **Trading/finance:** position size limits, risk management, look-ahead bias, data leakage, market hours, idempotency
- **Web apps:** CSRF, XSS, auth flow, session management, rate limiting
- **Data pipelines:** schema validation, null handling, data leakage in train/test splits
- **CLI tools:** argument injection, path traversal in file args, permission handling

**Subagent prompt template:**
```
Audit [DIRECTORY] for: 1) security vulnerabilities, 2) API key/secret handling, 
3) code quality bugs, 4) [domain-specific checks]. 
Read all code files, produce a structured report with severity levels: 
🔴 CRITICAL, 🟠 HIGH, 🟡 MEDIUM, 🟢 LOW.
```

**Toolsets:** `["terminal", "file"]` — subagents need to read code and run commands.

## Step 3: Consolidate Report

After all subagents return:
1. Merge findings into a single report
2. Group by severity (critical first)
3. Identify cross-cutting issues (same bug pattern in multiple codebases)
4. Save to a report file (e.g., `~/trading-audit-report.md`)

## Step 4: Parallel Fix (Batch delegate_task)

Spawn 1 subagent per codebase to apply fixes. Each gets:
- The specific findings for that codebase
- Instructions to read files first, then patch
- Verification step (py_compile, syntax check, etc.)

**Fix subagent prompt template:**
```
Fix all issues in [CODEBASE]. Read each file first, then apply fixes.
Issues to fix: [specific list from audit]
Read each file, apply patches, verify. Be thorough.
```

## Proven Results

- Trading portfolio audit (6 codebases): audit in 58s, fixes in 166s, total cost ~$0.45
- Same task via Ruflo hive-mind: $1.08, zero output (context window exhausted)
- Direct subagents beat orchestration frameworks for bounded tasks

## Pitfalls to Avoid

- Don't use orchestration frameworks (Ruflo, hive-mind) for bounded audit tasks — the coordination overhead consumes the entire token budget
- Don't try to audit everything in one subagent — parallel is faster and each codebase gets full attention
- Don't skip the consolidation step — individual reports need cross-referencing for patterns
- Don't fix without auditing first — the audit report is the fix spec
- Always verify fixes compile/pass syntax check after patching
