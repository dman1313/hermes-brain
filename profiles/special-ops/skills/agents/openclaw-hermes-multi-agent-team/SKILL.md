---
name: openclaw-hermes-multi-agent-team
description: Complete multi-agent team setup with OpenClaw and Hermes Agent following Alex Finn's YouTube guide
version: 2.1.0
author: Hermes Assistant
metadata:
  hermes:
    tags: [multi-agent, openclaw, hermes, backup, supervisor, monitoring, memory]
    homepage: https://github.com/NousResearch/hermes-agent
    video_source: https://youtu.be/mduLV-mWrNM?si=lArWr3cvFxwF9uPc
---

# OpenClaw + Hermes Multi-Agent Team Setup

Based on Alex Finn's YouTube video "You NEED to set up a multi agent team with OpenClaw and Hermes", this skill implements the four core workflows for a resilient, cost-effective AI team.

## Core Concept

Using **OpenClaw** (our Telegram/Discord bot) and **Hermes Agent** together creates a highly reliable system with complementary strengths:

- **OpenClaw (Primary Worker):** More stable, gets updates faster, reliable for large tasks
- **Hermes Agent (Assistant/Monitor):** Lighter weight, faster, uses fewer tokens

## Current Setup Status

✅ **Already Implemented:**
- Multi-agent system (11 agents: Scotty, DREAM, HAL, Special Ops, Zen, Sherlock, Hermes, MrClean, DRAFT, POLISH, PACKAGER)
- Telegram gateway (@betaclawv1_bot)
- Agent routing via slash commands (/sherlock, /scotty, /zen, /mrclean, etc.)
- All routing native via `agent-router` skill (Multica removed 2026-05-04)

## Four Key Workflows Implemented

### 1. Mutual Backup & Repair System ✅

**Problem:** Individual agents can break during updates
**Solution:** When one agent fails, the other diagnoses and fixes it

**Implementation:**
- `~/.hermes/scripts/agent_health_diagnostic.py` - Comprehensive health checks (provider-aware)
- `~/.hermes/scripts/api_key_diagnostic.py` - API key detection and repair
- **Cron Job:** Agent Health Monitor runs every 30 minutes

**Key Improvements in v2.1:**
- **Provider-aware API key checking:** Script now checks for API keys matching the configured model provider (e.g., DEEPSEEK_API_KEY when using deepseek provider)
- **Fixed false positives:** No longer warns about missing OPENAI/ANTHROPIC keys when using alternative providers
- **Accurate process detection:** Updated to match actual gateway command patterns (`gateway run` instead of `hermes-gateway`)

**Example Fix Flow:**
- OpenClaw errors with "missing API key for OpenAI"
- Hermes runs `api_key_diagnostic.py` to identify issue
- Script provides specific fixes or creates template
- Downtime reduced from ~1 hour to seconds

### 2. Supervisor/Builder Workflow (Planner-Worker-Reviewer) ✅

Cost-efficient workflow for building projects:

1. **Plan:** OpenClaw (powered by Claude Opus) creates detailed plans
2. **Execute:** Hermes (cheaper model) implements the plan
3. **Review:** OpenClaw audits the built code for quality

**Templates Created:**
- `~/.hermes/templates/planner_prompt.txt` - For OpenClaw planning
- `~/.hermes/templates/executor_prompt.txt` - For Hermes execution
- `~/.hermes/templates/reviewer_prompt.txt` - For OpenClaw review

### 3. Monitor System ✅

Use Hermes (lighter/cheaper) to run scheduled cron jobs as a "hallway monitor":

**Cron Jobs Configured:**
1. **Agent Health Monitor** (`*/30 * * * *`)
   - Runs diagnostic scripts
   - Reports issues to Telegram
   - Logs to shared memory

2. **System Resources Monitor** (`0 */2 * * *`)
   - Checks CPU, memory, disk
   - Monitors agent performance
   - Verifies external services

### 4. Shared Memory Workspace (Obsidian) ✅

Centralize knowledge to improve both agents' memory and enable recursive self-improvement.

**Folder Structure:**
```
~/.hermes/obsidian_workspace/
├── agent_openclaw/          # Individual memory/logs
├── agent_hermes/           # Individual memory/logs  
├── agent_shared/           # Central shared workspace
│   ├── lessons_learned/template.md
│   ├── common_errors/      # Auto-populated from diagnostics
│   ├── best_practices/
│   ├── project_contexts/
│   └── workflow_templates/
└── system_logs/            # Health check logs
```

**Integration:**
- Agents save lessons to shared folder after solving problems
- Diagnostic scripts auto-log issues to `common_errors/`
- Health checks save logs to `system_logs/`

## Pro Tips from Video

1. **Physical Setup:** Keep both agent chats (Telegram) open on a second monitor for constant visibility
2. **Easy Implementation:** Give the video link to either agent - it will generate transcript and set up system
3. **Model Strategy:**
   - OpenClaw: Claude Opus (best for agents) or ChatGPT
   - Hermes: ChatGPT or cheaper models (GLM, etc.) as assistant
4. **Community:** Join Vibe Coding Academy for weekly bootcamps

## Quick Verification

```bash
# Test health diagnostic
python3 ~/.hermes/scripts/agent_health_diagnostic.py

# Test API key diagnostic  
python3 ~/.hermes/scripts/api_key_diagnostic.py

# List cron jobs
hermes cron list

# View shared memory structure
ls -la ~/.hermes/obsidian_workspace/
```

## Usage Examples

### 1. Mutual Backup:
When an agent fails, run diagnostics:
```bash
python3 ~/.hermes/scripts/api_key_diagnostic.py
```

### 2. Planner-Worker-Reviewer:
- OpenClaw: Use `~/.hermes/templates/planner_prompt.txt`
- Hermes: Use `~/.hermes/templates/executor_prompt.txt`  
- OpenClaw: Use `~/.hermes/templates/reviewer_prompt.txt`

### 3. Monitoring:
- Health checks run automatically every 30 minutes
- System checks every 2 hours
- Issues auto-logged to shared memory

### 4. Shared Memory:
- Lessons automatically saved to `agent_shared/lessons_learned/`
- Errors logged to `agent_shared/common_errors/`
- System logs in `agent_shared/system_logs/`

## Test Results

✅ **Health diagnostic** working - detects missing API keys, gateway status  
✅ **API key diagnostic** working - identifies and logs missing keys  
✅ **Cron jobs** scheduled - health monitor (30min), system monitor (2hr)  
✅ **File structure** complete - all templates and scripts in place  
✅ **Shared memory** operational - auto-logging implemented

## Resources

- **Video:** https://youtu.be/mduLV-mWrNM?si=lArWr3cvFxwF9uPc
- **Obsidian Memory Guide:** https://youtu.be/6V-b073qhPA
- **Vibe Coding Academy:** https://vibecodingacademy.dev
- **Creator's Newsletter:** https://www.alexfinn.ai/subscribe