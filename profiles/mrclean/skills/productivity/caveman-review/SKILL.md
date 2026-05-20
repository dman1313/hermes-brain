---
name: caveman-review
description: >
  Ultra-compressed code review comments. Cuts noise from PR feedback while preserving
  the actionable signal. Each comment is one line: location, problem, fix. Use when user
  says "review this PR", "code review", "/review", or /caveman-review.
---

Write code review comments terse and actionable. One line per finding. Location, problem, fix. No throat-clearing.

## Rules

**Format:** `L<line>: <problem>. <fix>.` — or `<file>:L<line>: ...` when reviewing multi-file diffs.

**Severity prefix (optional):**
- 🔴 `bug:` — broken behavior, will cause incident
- 🟡 `risk:` — works but fragile (race, missing null check, swallowed error)
- 🔵 `nit:` — style, naming, micro-optim. Author can ignore
- ❓ `q:` — genuine question, not a suggestion

**Drop:**
- "I noticed that...", "It seems like...", "You might want to consider..."
- "This is just a suggestion but..." — use `nit:` instead
- "Great work!", "Looks good overall but..." — say it once at top, not per comment
- Hedging ("perhaps", "maybe", "I think") — if unsure use `q:`

**Keep:**
- Exact line numbers
- Exact symbol/function/variable names in `backticks`
- Concrete fix, not "consider refactoring this"
- The *why* if the fix isn't obvious from the problem

## Examples

✅ `L42: 🔴 bug: user can be null after .find(). Add guard before .email.`
✅ `L88-140: 🔵 nit: 50-line fn does 4 things. Extract validate/normalize/persist.`
✅ `L23: 🟡 risk: no retry on 429. Wrap in withBackoff(3).`

## Auto-Clarity

Drop terse mode for: security findings (CVE-class bugs need full explanation + reference), architectural disagreements (need rationale, not just one-liner), onboarding contexts where author is new and needs the "why".

## Boundaries

Reviews only — does not write the fix, does not approve/request-changes, does not run linters. Output comment(s) ready to paste into PR.
