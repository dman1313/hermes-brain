---
name: policy-procedure-ai-service
description: Use when converting human-written policies, procedures, SOPs, manuals, or operational docs into AI-friendly artifacts for Hermes agents and the wiki. Runs the local pp-ai-service CLI to generate wiki-ready markdown, Hermes SKILL.md, validation reports, and manifest JSON.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [policies, procedures, sop, ai-ready, documentation, skills]
    related_skills: [obsidian, hermes-agent-skill-authoring, test-driven-development]
---

# Policy & Procedure AI Service

## Overview

Use this skill to convert human-oriented policies, procedures, SOPs, and manuals into AI-executable documentation. The local service parses markdown/text documents and outputs:

1. A wiki-ready markdown page with AI execution notes.
2. A Hermes `SKILL.md` that agents can load and follow.
3. An AI-readiness validation report.
4. A manifest JSON with source, output paths, score, and issues.

The tool lives at:

```bash
/home/ubuntu/tools/pp-ai-service
```

The durable wiki page for the service is:

```bash
/home/ubuntu/wiki/concepts/policy-procedure-ai-service.md
```

## When to Use

Use this skill when the user asks to:

- Make policies/procedures/SOPs “AI friendly.”
- Turn a human procedure into a Hermes skill.
- Validate whether a procedure is ready for AI agents to follow.
- Convert operational docs into wiki + skill + report artifacts.
- Batch-improve internal documentation so agents can execute it reliably.

Do not use this skill for:

- Generic note creation with no procedural/execution component — use `obsidian` or the wiki workflow.
- Writing a complex new software feature from scratch — use `writing-plans` and `test-driven-development` first.
- Authoring a hand-crafted in-repo Hermes Agent skill — use `hermes-agent-skill-authoring`.

## AI-Ready Procedure Schema

A document is considered AI-ready when it includes:

- **Purpose** — the intended outcome.
- **Trigger Conditions** — when the procedure should be activated.
- **Preconditions** — what must be true before execution starts.
- **Procedure / Workflow Steps** — ordered steps an agent can follow.
- **Verification / Success Criteria** — objective checks before reporting success.
- **Pitfalls / Failure Modes** — risks, exceptions, and escalation points.

If any of these are missing, the validation report will flag them.

## Basic Workflow

### 1. Put the source document somewhere stable

For ad-hoc testing, use the service examples directory:

```bash
mkdir -p /home/ubuntu/tools/pp-ai-service/examples
cat > /home/ubuntu/tools/pp-ai-service/examples/example-procedure.md <<'EOF'
# Example Procedure

## Purpose
Describe the intended outcome.

## Trigger Conditions
- Describe when to use this.

## Preconditions
- Describe what must already be true.

## Procedure
1. Step one.
2. Step two.

## Verification
- Describe how to prove success.

## Pitfalls
- Describe a known risk or stop condition.
EOF
```

For user-provided files, preserve the original path and use that directly.

### 2. Run the converter

```bash
cd /home/ubuntu/tools/pp-ai-service
PYTHONPATH=src python -m pp_ai_service.cli path/to/source.md --out generated
```

Expected output shape:

```text
Generated AI-friendly artifacts for <Title> at /home/ubuntu/tools/pp-ai-service/generated
AI-readiness score: <N>/100
```

Generated files:

```text
generated/
├── manifest.json
├── reports/<slug>-validation.md
├── skills/<slug>/SKILL.md
└── wiki/<slug>.md
```

### 3. Inspect the validation report

```bash
cat /home/ubuntu/tools/pp-ai-service/generated/reports/<slug>-validation.md
```

If score is below 100, fix the source document or manually improve the generated artifacts before installation.

### 4. Review generated skill before installing

```bash
cat /home/ubuntu/tools/pp-ai-service/generated/skills/<slug>/SKILL.md
```

Check:

- Trigger conditions are not too broad.
- Preconditions are clear and enforceable.
- Steps are safe and ordered.
- Verification checks are objective.
- Pitfalls include escalation/stop conditions.

### 5. Copy wiki artifact into the wiki if approved

Choose the correct wiki location. For durable concepts/procedures, usually:

```bash
cp /home/ubuntu/tools/pp-ai-service/generated/wiki/<slug>.md /home/ubuntu/wiki/concepts/<slug>.md
```

Then update:

- `/home/ubuntu/wiki/index.md`
- `/home/ubuntu/wiki/log.md`

Follow the wiki-system-first rules: keep frontmatter, wikilinks, and log entries current.

### 6. Install generated skill only after review

For a user-local skill:

```bash
mkdir -p /home/ubuntu/.hermes/skills/productivity/<slug>
cp /home/ubuntu/tools/pp-ai-service/generated/skills/<slug>/SKILL.md /home/ubuntu/.hermes/skills/productivity/<slug>/SKILL.md
```

Important: the current Hermes session may not see newly installed skills until a fresh session.

## Verification Commands

Run the service test suite before relying on it after edits:

```bash
cd /home/ubuntu/tools/pp-ai-service
python -m pytest -q
```

Known-good result from initial MVP:

```text
6 passed
```

Run an end-to-end smoke test:

```bash
cd /home/ubuntu/tools/pp-ai-service
PYTHONPATH=src python -m pp_ai_service.cli examples/vendor-onboarding.md --out generated
python -m pytest -q
```

Expected:

```text
Generated AI-friendly artifacts for Vendor Onboarding Procedure at /home/ubuntu/tools/pp-ai-service/generated
AI-readiness score: 100/100
6 passed
```

## Common Pitfalls

1. **Forgetting `PYTHONPATH=src`.**
   The service is local/dev-mode. Use `PYTHONPATH=src python -m pp_ai_service.cli ...` unless it has been installed as a package.

2. **Installing generated skills without review.**
   Generated `SKILL.md` files are scaffolds. Review safety, scope, and trigger conditions before copying into `~/.hermes/skills/`.

3. **Treating a low score as failure instead of feedback.**
   A low score identifies missing AI-execution structure. Use it to improve the source policy/procedure.

4. **Skipping wiki updates.**
   If a generated wiki page becomes durable knowledge, update `index.md` and append a `log.md` entry.

5. **Assuming generated docs are legally/policy authoritative.**
   The service restructures documents for AI execution; it does not replace human approval for compliance-sensitive policies.

## Output Review Checklist

Before reporting completion:

- [ ] CLI ran successfully.
- [ ] `manifest.json` exists.
- [ ] Wiki markdown exists and has frontmatter.
- [ ] Generated `SKILL.md` exists.
- [ ] Validation report exists and was inspected.
- [ ] AI-readiness score is reported to the user.
- [ ] Any missing sections are summarized.
- [ ] Durable wiki updates were made if requested or clearly appropriate.
- [ ] Generated skill was not installed without review/approval.
