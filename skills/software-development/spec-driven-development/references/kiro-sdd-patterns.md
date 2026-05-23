# Kiro-Inspired Spec Patterns

Patterns observed from Kiro (Amazon's agentic IDE) that enhance spec-driven development.
Source: https://github.com/kirodotdev/Kiro, https://kiro.dev/docs/specs

## Three-File Spec Layout

Kiro generates three files per spec under `.kiro/specs/<name>/`:

```
requirements.md   →  User stories + acceptance criteria (WHEN...SHALL format)
design.md         →  Architecture, interfaces, data models, correctness properties
tasks.md          →  Ordered checkbox tasks with dependency tracking
```

### requirements.md Structure
- Glossary of terms/abbreviations
- User stories in WHEN...SHALL acceptance criterion format
- Each requirement references its acceptance criteria by number (1.1, 1.2, etc.)

### design.md Structure
- Architecture overview with Mermaid diagrams
- Component interfaces in TypeScript (even for non-TS projects — serves as a precise contract)
- Data models with interfaces
- **Correctness Properties** section (see below)
- Error handling strategy

### tasks.md Structure
- Ordered numbered tasks with subtasks
- Each task references the requirements it satisfies
- Checkpoints at major milestones ("ensure all tests pass, ask the user if questions arise")
- Optional tasks marked with `*` for MVP acceleration
- Task execution via dependency graph with parallel waves

## Correctness Properties — The Key Innovation

After the design, define formal properties the system must satisfy. Each property is a `For any X, when Y, Z should hold` statement that is testable.

### Format
```
### Property N: [Name]

*For any* [condition],
when [trigger/action],
[expected behavior].

**Validates: Requirements X.Y, X.Z**
```

### Example (from Kiro's GitHub issue automation spec)
```
### Property 6: High Confidence Duplicate Commenting

*For any* duplicate detection result with similarity score > 0.80,
a comment should be added to the issue listing all potential duplicates
with their scores and links.

**Validates: Requirements 2.2, 2.5**
```

### Why This Matters
- Bridges human-readable specs and machine-verifiable correctness
- Each property maps directly to a test case — no ambiguity about what to test
- Properties cover both positive cases (must happen) and negative cases (must NOT happen)
- Fault isolation properties ensure the system degrades gracefully:
  ```
  *For any* workflow run processing multiple issues,
  if individual issue processing fails,
  the workflow should continue processing remaining issues
  rather than failing entirely.
  ```

### Property Categories
| Category | Example |
|----------|---------|
| Invocation | API was called with correct params |
| Output validation | Labels assigned are from taxonomy |
| Timing/ordering | Closure happens after N days |
| Negative/absence | When X doesn't happen, Y is NOT done |
| Error handling | On failure, log + continue |
| Fault isolation | Individual failure doesn't kill batch |

## Dependency Wave Execution

Tasks in `tasks.md` can declare dependencies. Kiro builds a dependency graph and groups tasks into waves:

- **Wave 1**: All tasks with no dependencies → run concurrently
- **Wave 2**: All tasks whose dependencies were satisfied by Wave 1 → run concurrently
- **Wave N**: Continues until all tasks complete

Waves execute sequentially; tasks within a wave execute concurrently. This is more structured than manually ordering tasks — the dependency relationships define the order, and parallelism is automatic for independent work.

### Applying This to Hermes

In Hermes' SDD workflow:
1. Add a "Correctness Properties" section to the design phase — after architecture, before tasks
2. Use the property format: `*For any* [input/state], when [action], [expected result].`
3. In tasks, add dependency annotations so subagents can identify parallelizable work
4. Keep the number of properties manageable (15-25 for a medium feature) — they're the spec's contract, not exhaustive documentation
