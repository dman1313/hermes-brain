# Kanban Agent Roster

17 agents defined in `plugins/kanban/dashboard/plugin_api.py` `_AGENT_META`.
Endpoint: `GET /api/plugins/kanban/agents` — returns live task counts, status,
progress, and active runs per agent.

## Adding a new agent

Add an entry to `_AGENT_META` in `plugin_api.py`:

```python
"agent-name": {
    "display": "Agent Display",
    "emoji": "🤖",
    "role": "Role Title",
    "gradient": ["#light", "#dark"],
    "color": "#hex",
    "description": "What this agent does",
}
```

Keys must match either a kanban assignee name OR the skill filename stem.
New agents automatically appear in the API response even with zero tasks.

## Current roster

| Agent | Emoji | Role | Color | Status |
|-------|-------|------|-------|--------|
| default (Hermes) | ⚡ | Default Worker | #7a9eb5 | Kanban worker |
| coder | 💻 | Implementation | #4a7c59 | Kanban worker |
| researcher-a | 🔬 | Research & Analysis | #9b7eb5 | Kanban worker |
| reviewer | 👁️ | Code Review | #d4a843 | Kanban worker |
| hal | 🛰️ | Orchestrator | #5c6bc0 | Skill persona |
| special-ops | 🎯 | Mission Control | #e91e63 | Skill persona |
| scotty | 🔧 | System Architect | #00897b | Skill persona |
| sherlock | 🔍 | Research Investigator | #ff8f00 | Skill persona |
| zen-agent | 🧘 | Wellness Coach | #66bb6a | Skill persona |
| dream | 🌙 | Nightly Reflection | #7e57c2 | Skill persona |
| mrclean | 🧹 | Cleanup Auditor | #00acc1 | Skill persona |
| qa-agent | ✅ | Quality Assurance | #7cb342 | Skill persona |
| incident-responder | 🚨 | Production Triage | #e64a19 | Skill persona |
| shepherd-agent | 🐑 | Workflow Monitor | #8e24aa | Skill persona |
| agent-router | 🔀 | Telegram Router | #607d8b | Skill persona |
| strategic-planner-framework | 📐 | Strategic Planner | #ef6c00 | Skill persona |
| voice-to-newsletter-pipeline | 📰 | Content Pipeline | #3949ab | Skill persona |

## API response shape

```json
{
  "agents": [{
    "name": "coder",
    "display": "Coder",
    "emoji": "💻",
    "role": "Implementation",
    "gradient": ["#e8f5e9", "#c8e6c9"],
    "color": "#4a7c59",
    "description": "Builds and ships code",
    "totalTasks": 1,
    "byStatus": {"todo": 1},
    "status": "online",
    "activeRuns": [{
      "taskId": "t_xxx",
      "title": "Task title",
      "startedAt": 1700000000,
      "maxRuntime": 3600,
      "elapsed": 120,
      "progress": 3
    }],
    "progress": 3
  }]
}
```

Status values: `busy` (has running tasks), `online` (has tasks, none running), `idle` (zero tasks).
Sort: busy first, then by task count desc, then display name asc.
