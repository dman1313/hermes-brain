# Workflow Registry Method

> Adapted from The Agency's Workflow Architect (msitarzewski/agency-agents).
> A structured approach to discovering, documenting, and maintaining workflows as a cross-referenced registry.

## When to Use This

When you're entering a new codebase, designing a new system, or debugging a workflow failure that nobody fully understands. Use it before writing code, not after.

## The Core Insight

Most workflows are never announced — they are implied by the code, the data model, the infrastructure, or the business rules. Your job is discovery before design.

## Discovery Method

Read these in order to find every workflow in a system:

1. **Every route file** — each endpoint is a workflow entry point
2. **Every worker/job file** — each background job type is a workflow
3. **Every database migration** — each schema change implies a lifecycle
4. **Every service orchestration config** (docker-compose, K8s manifests, Helm) — every dependency implies an ordering workflow
5. **Every IaC module** (Terraform, CloudFormation) — each resource has creation/destruction workflow
6. **Every config and env file** — each value is an assumption about runtime state
7. **Architectural decision records and design docs** — stated principles imply workflow constraints
8. **Ask**: "What triggers this? What happens next? What happens if it fails? Who cleans it up?"

**Anything that exists in code but not in a spec is a liability.** It will be modified without understanding its full shape, and it will break.

## The Four-View Registry

Document every discovered workflow in four cross-referenced views:

### View 1: By Workflow (master list)

```
## Workflows

### [Workflow Name]
- **Triggers**: [What starts this?]
- **Actors**: [Who/the what participates?]
- **States**: [All observable states this passes through]
- **Decision Nodes**: [Every branching point and what controls it]
- **Failure Modes**: [Every way this can fail + recovery action]
- **Success State**: [What "done" looks like]
- **Contracts**: [Handoff boundaries between components]
- **Spec Location**: [Path to the spec file]
```

### View 2: By Component (inverse index)

Map every file/endpoint/service back to the workflows it participates in:

```
### [Component Name]
- **Participates in**: [Workflow A], [Workflow B]
- **Role**: [What it does in each workflow]
- **Handoff boundaries**: [What it expects and what it produces]
```

### View 3: By User Journey (user-facing flows)

```
### [User Action]
- **Steps**: [Detailed path through the system]
- **Branch conditions**: [What changes the path]
- **Failure states**: [What user sees on failure]
- **Recovery paths**: [How user gets back to happy path]
```

### View 4: By Failure Mode (inverse of View 1)

```
### [Failure: "X crashes when Y is empty"]
- **Affects workflows**: [Wf A] step 3, [Wf B] step 7
- **Affects components**: [Component X] line 42, [Component Y] line 15
- **Affects users**: [Journey A] step 2 shows 500 error
- **Recovery**: [Explicit recovery action or known workaround]
```

## Key Principle

**A workflow that exists in code but not in a spec is a liability.** If you discover an undocumented workflow during exploration, document it — even if nobody asked for it. The registry is how you prevent the next engineer (or agent) from breaking it.
