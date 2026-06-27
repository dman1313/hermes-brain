---
name: cronjob-model-management
description: Practical procedures for updating and managing cronjob model assignments in Hermes Agent systems.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [cronjob, model-management, hermes, configuration, system-admin]
    category: devops
---

# Cronjob Model Management

Practical procedures for updating and managing cronjob model assignments in Hermes Agent systems. This skill covers the hands-on implementation of model routing strategies for scheduled tasks.

## Prerequisites

- Hermes Agent with configured models
- Access to cronjob management (cronjob tool)
- Understanding of model routing concepts (see hermes-model-routing skill)

## Systematic Cronjob Model Update Procedure

### Step 1: Audit Current Model Assignments

First, identify all cronjobs and their current model assignments:

```bash
# List all cronjobs with detailed model information
cronjob(action='list')
```

**What to look for:**
- Cronjobs using outdated models (glm-4.5, older versions)
- Cronjobs with no model assigned (null)
- Provider names that may be incorrect
- Model names that don't match available models

### Step 2: Verify Available Models

Check which models are actually available through your providers:

```bash
# Check Kimi provider models
jq '.kimi-for-coding.models | keys' ~/.hermes/models_dev_cache.json

# Check ZAI provider models  
jq '.zai.models | keys[] | select(test("glm-5.1"))' ~/.hermes/models_dev_cache.json
```

**Common available models:**
- **Kimi-for-coding provider:** `k2p5`, `kimi-k2-thinking`
- **ZAI provider:** `glm-4.5`, `glm-5.1`

### Step 3: Update System Configuration

Ensure your Hermes configuration reflects the correct utility model:

```yaml
# In your Hermes configuration file
cheap_model: glm-5.1  # Utility worker for simple tasks
```

### Step 4: Update Cronjobs with Exact Names

**Critical:** Provider and model names must be exactly as they appear in the model cache.

**Correct Format:**
```bash
cronjob(action='update', job_id='ACTUAL_JOB_ID', model={'model': 'k2p5', 'provider': 'kimi-for-coding'})
```

**Common Mistakes:**
- ❌ `provider: 'kimi-coding'` (incorrect)
- ✅ `provider: 'kimi-for-coding'` (correct)
- ❌ `model: 'kimi-k2-5'` (incorrect) 
- ✅ `model: 'k2p5'` (correct)

### Step 5: Verify and Test Changes

After updating all cronjobs:

```bash
# Verify all changes
cronjob(action='list')

# Test one updated cronjob if possible
cronjob(action='run', job_id='TEST_JOB_ID')
```

## Model Assignment Guidelines

### When to Use Kimi Models (k2p5)

**Appropriate for:**
- Agent health monitoring tasks
- System resource monitoring
- Memory sync operations  
- Daily/nightly agent routines (DREAM, Zen, etc.)
- Technical execution requiring coding ability
- Complex decision-making tasks

**Example cronjobs:**
- Agent Health Monitor
- System Resources Monitor  
- DREAM Nightly Reflection
- Zen Morning/Evening routines

### When to Use GLM Models (glm-5.1 via ZAI)

**Appropriate for:**
- Simple reminder cleanup
- Basic system scripts
- Non-critical utility tasks
- Cost-optimized background processing
- When explicitly requested by user

### When to Use Xiaomi Models

**Dwayne's preferred cron provider (replaces GLM 5.1 / ZAI for all scheduled jobs).**

**Default model:** `mimo-v2-pro` — faster non-reasoning model, ideal for straightforward cron tasks.
**Reasoning model:** `mimo-v2.5-pro` — reserved for DREAM nightly analysis only.

**Provider:** `xiaomi`
**Base URL:** `https://token-plan-ams.xiaomimimo.com/v1`
**Key env var:** `XIAOMI_API_KEY`

**Note:** `mimo-v2.5-pro` has reasoning mode — needs higher `max_tokens` to accommodate both reasoning and response. `mimo-v2-pro` has no reasoning overhead, faster and cheaper for routine tasks.

**Pitfall — wrong host:** `https://mimo.xiaomi.com` is the marketing website, not the API. Always use `https://token-plan-ams.xiaomimimo.com/v1`. See `references/mimo-provider-notes.md`.

### Cron Job Model Tiering (Dwayne's Preference)

Default all cron jobs to `mimo-v2-pro` unless the task genuinely benefits from reasoning:

| Tier | Model | Use For |
|---|---|---|
| **Reasoning** | `mimo-v2.5-pro` | DREAM nightly analysis (complex pattern analysis) |
| **Standard** | `mimo-v2-pro` | Everything else — health monitors, syncs, reflections, reminders, system checks |

**Rationale:** Most cron jobs are straightforward (read script output and report, send a short message, check system status). `mimo-v2-pro` is faster, cheaper, and produces identical results for these tasks. Only DREAM's multi-session pattern analysis warrants `mimo-v2.5-pro`'s reasoning overhead.

**Common pitfall — `mimo.xiaomi.com` vs API host:** The website `https://mimo.xiaomi.com` is the marketing site, not the API. The API lives at `https://token-plan-ams.xiaomimimo.com/v1`. Calling the marketing site returns HTML 404 pages. Always use the `token-plan-ams` host for API calls. See `references/mimo-provider-notes.md` for full provider details and testing patterns.

### When to Use No Model (null) — AVOID ENTIRELY

**Never use `model: null` for any cron job.** Even with an attached `script`, null-model jobs behave unpredictably in the Hermes cron engine:

- Without a script: produces `(No response generated)` and `last_status: error` — the job never executes
- With a script: the script output IS captured and injected into the prompt, but with no LLM agent to read it, the output may still show `(No response generated)` and `last_status: error` depending on the cron engine version

The safe pattern: ALWAYS assign a model. For script-driven jobs, use the cheapest available model (`mimo-v2-pro`) and limit toolsets to `["terminal"]`.

## Troubleshooting Common Issues

### Issue: "Job with ID 'xxxxx' not found"

**Cause:** Using incorrect job ID from memory instead of actual list

**Solution:**
1. Run `cronjob(action='list')` to get current job IDs
2. Copy the exact job_id from the output
3. Use that exact ID in your update command

### Issue: "Provider not found" or API errors

**Cause:** Incorrect provider name in model specification

**Solution:**
1. Check models_dev_cache.json for exact provider names
2. Use `jq '.kimi-for-coding' ~/.hermes/models_dev_cache.json` to verify
3. Common correct names: `kimi-for-coding`, `zai`, `openai`
4. Remember the Hermes provider quirk: the user-facing/config slug `kimi-for-coding` may normalize internally to the runtime/auth provider key `kimi-coding`

### Issue: Kimi direct API works inconsistently or Hermes Kimi calls return 404

**Cause:** Two recurring Kimi integration quirks were observed:
1. The raw REST endpoint may reject direct requests with HTTP 403 (`access_terminated_error`) even when Hermes-native agent calls succeed
2. Hermes Kimi calls fail with HTTP 404 if the base URL is missing the `/v1` suffix

**Solution:**
1. Prefer validating Kimi through a Hermes-native agent call, not just a raw `requests.post()` test
2. Ensure the effective base URL is `https://api.kimi.com/coding/v1`
3. If direct REST returns 403 but Hermes-native calls succeed, treat Kimi as usable through coding-agent paths only
4. If Hermes-native calls hit `https://api.kimi.com/coding/` and return 404, fix the base URL before concluding Kimi is down

### Issue: Model updates don't take effect

**Cause:** Cronjobs don't inherit from config file, need explicit updates

**Solution:**
1. Update each cronjob individually with explicit model/provider
2. Don't assume config file changes affect existing cronjobs
3. Verify updates with `cronjob(action='list')`

### Issue: Some cronjobs fail after model change

**Cause:** New model doesn't have required capabilities or API access

**Solution:**
1. Check if the task requires specific model capabilities
2. For simple tasks, fall back to GLM 5.1
3. For complex tasks, ensure using k2p5 or equivalent
4. Monitor error logs for specific failure reasons

### Issue: Cronjob fails with "no API key found" or falls through to wrong provider

**Cause:** Job has `model: null` (no model assigned). The cron engine falls through to the default provider (`model.default.provider` in config.yaml), which may not have a valid API key configured.

This is a **silent fail** — the job shows `last_status: error` with NO useful output in the cron log directory. The error only surfaces in `~/.hermes/logs/errors.log`:
```
RuntimeError: Provider 'minimax' is set in config.yaml but no API key was found.
```

**Solution:** Always pin cron jobs to an explicit model/provider combo, never leave `model: null`. Use `cronjob(action='update', job_id='...', model={'model': 'DEEPSEEK_CHAT', 'provider': 'deepseek'})` for simple tasks that don't need a specific model's capabilities.

**Cause:** The selected provider or model rejected the request.

**Solution:**
1. Do not ask the user to manually pick a provider.
2. Automatically try the fallback chain: zai (glm-5.1) → kimi-for-coding (k2p5) → openai-codex (gpt-5.4).
3. Only escalate to the user if all fallbacks fail.
4. Document the chosen provider in the job notes for future reference.

## Verification Checklist

After completing cronjob model updates:

- [ ] All cron jobs have a model assigned (no null-model jobs, ever)
- [ ] Default model for all jobs is `mimo-v2-pro` via `xiaomi` unless the job specifically needs reasoning
- [ ] DREAM Nightly Reflection uses `mimo-v2.5-pro` (reasoning tier)
- [ ] Dropbox sync jobs have both a model AND a wrapper script attached
- [ ] Config file cheap_model matches the utility worker model
- [ ] No cronjobs use deprecated or incorrect model names
- [ ] Provider names exactly match models_dev_cache.json
- [ ] Model names exactly match models_dev_cache.json
- [ ] Test run of at least one updated cronjob succeeds

## Example: Complete Migration Workflow

### Scenario: Migrate from GLM to Kimi models

```bash
# 1. Audit current state
cronjob(action='list')

# 2. Identify cronjobs using GLM models (grep for glm-4.5, glm-5.1)
# 3. Verify Kimi models available
jq '.kimi-for-coding.models | keys' ~/.hermes/models_dev_cache.json

# 4. Update config file if needed
# Change cheap_model from glm-4.5 to glm-5.1

# 5. Update each GLM cronjob to use Kimi
cronjob(action='update', job_id='28bd7873af01', model={'model': 'k2p5', 'provider': 'kimi-for-coding'})
cronjob(action='update', job_id='d0778687dd26', model={'model': 'k2p5', 'provider': 'kimi-for-coding'})
# ... continue for all identified cronjobs

# 6. Verify changes
cronjob(action='list')

# 7. Test one or two critical cronjobs
cronjob(action='run', job_id='CRITICAL_JOB_ID')
```

### Scenario: Batch Migrate All Cron Jobs to a New Provider

When the user says "use xiaomi instead of glm 5.1" or similar, update ALL jobs in a single pass:

1. First test the new provider is working (do NOT skip this):
```bash
curl -s --max-time 20 https://<base-url>/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d '{"model":"<model>","messages":[{"role":"user","content":"say ok"}],"max_tokens":100}'
```

2. List all jobs: `cronjob(action='list')`

3. Update every job that uses the old provider using `cronjob(action='update', job_id=XXX, model={'model': 'NEW_MODEL', 'provider': 'NEW_PROVIDER'})`. Do them ALL — the user means every job, not a subset. Common targets:
   - DREAM Nightly Reflection
   - Agent Health Monitor
   - System Resources Monitor
   - Sync Shared Memory
   - wiki-dropbox-sync / photo-news-dropbox-sync
   - Agent Activity & Issue Monitor
   - Daily Night Ignore Reminders
   - Zen Morning/Evening/Night
   - Morning/Evening Reflections
   - Human Good AI Departure Countdown
   - Take a breath reminder

4. Verify with `cronjob(action='list')` — all jobs should now show the new provider/model.

**Pitfall — using wrong tool:** Do NOT use `hermes cron update` CLI commands for batch updates. Use `cronjob(action='update', ...)` one job at a time. The CLI syntax differs from the tool syntax and will fail silently.

## Best Practices

1. **Always list before updating** - Get current job IDs first
2. **Use exact names** - Provider and model names must be precise
3. **Update individually** - Each cronjob needs explicit model specification
4. **Test critical jobs** - Don't assume updates work without testing
5. **Document changes** - Log what was changed and why
6. **Monitor after changes** - Watch for failed runs or errors

## Default Cron Frequencies (Dwayne's Preferences)

When creating or updating cron jobs without explicit user instruction, use these defaults:

| Job Type | Default Frequency | Examples |
|----------|-------------------|----------|
| **Agent Health Monitor** | Every 4 hours | `0 */4 * * *` |
| **System Monitoring** (Agent Activity, System Resources, Sync Shared Memory) | Every 6 hours | `0 */6 * * *` |
| **DREAM Nightly Reflection** | Daily at 3:00 AM | `0 3 * * *` |
| **Wellness Reminders** (Zen Morning Goals, Morning Wellness, Evening Reflection, Zen Night Reflection) | Daily at scheduled times | `0 8 * * *`, `0 9 * * *`, `0 20 * * *`, `0 21 * * *` |
| **File Sync Jobs** (Dropbox, etc.) | Every 4 hours | `0 */4 * * *` |

**Important:** If the user says "stop texting me" about wellness reminders, switch delivery to `local` (not Telegram) but keep the jobs running.

## Batch Update Safety Checklist

When updating multiple cron jobs at once:

1. **List all jobs first** — `cronjob(action='list')`
2. **Identify only the target jobs** — verify job IDs match the intended jobs
3. **Update one job at a time** — avoid batch updates that might affect unrelated jobs
4. **Verify each change** — check the schedule, model, and delivery method after each update
5. **Never change DREAM's schedule** unless explicitly asked — it must stay at `0 3 * * *`

## Emergency Provider Failover

When a provider goes down (token plan expired, API key revoked, service outage), all cron jobs pinned to it fail silently with `last_status: error`. This is the reactive recovery workflow:

### Step 1: Identify Failed Jobs

```bash
cronjob(action='list')
```

Scan for `last_status: "error"` across all jobs. Group by provider — if all failures share the same provider, that's your root cause.

### Step 2: Batch Switch to Working Provider

Update each failed job to an available provider. Do them all in parallel (no dependencies between updates):

```bash
cronjob(action='update', job_id='JOB_1', model={'model': 'TARGET_MODEL', 'provider': 'TARGET_PROVIDER'})
cronjob(action='update', job_id='JOB_2', model={'model': 'TARGET_MODEL', 'provider': 'TARGET_PROVIDER'})
# ... all failed jobs
```

**Provider fallback chain** (Dwayne's preference order):
1. `deepseek` / `deepseek-v4-pro` — heavy work, reliable
2. `kimi-for-coding` / `k2p5` — coding-capable
3. `zai` / `glm-5.1` — cheap utility tasks

### Step 3: Re-run All Failed Jobs

Trigger each job to catch up on missed runs:

```bash
cronjob(action='run', job_id='JOB_1')
cronjob(action='run', job_id='JOB_2')
# ... all failed jobs
```

Jobs run sequentially in the scheduler — they'll execute one after another and deliver to their configured targets.

### Step 4: Decide on Permanent vs Temporary

- **Temporary** ("run all with DeepSeek this one time"): Leave the jobs on the new provider. Switch back when the original provider recovers.
- **Permanent**: Update memory/config to reflect the new default provider for cron jobs.

**Pitfall — don't forget paused jobs:** Paused jobs won't show `last_status: error` since they don't run. But if they were paused *because* of a provider issue, they need updating too before resuming.

## Key Lessons Learned

### From Experience (2026-05-23)

1. **Provider outages cause silent cascading failures**: When a provider's token plan expires or API key becomes invalid, ALL cron jobs pinned to that provider fail with `last_status: error` and no fallback. The fix is batch-switch + re-run, not individual troubleshooting.
2. **`cronjob(action='run')` does not support model override**: You must update the job's model first, then run. There's no way to override the model at run time.

### From Experience (2026-04-18)

1. **Provider names must be exact**: The difference between `kimi-coding` and `kimi-for-coding` causes failures
2. **Model names must be exact**: `kimi-k2-5` vs `k2p5` - use exactly what's in the model cache
3. **Cronjobs don't inherit**: Each cronjob needs explicit model/provider assignment
4. **Always verify job IDs**: Never use job IDs from memory, always list first
5. **Test after changes**: Don't assume updates work without verification

This skill ensures systematic, reliable migration of cronjob models while avoiding common pitfalls and ensuring all scheduled tasks continue to function correctly.