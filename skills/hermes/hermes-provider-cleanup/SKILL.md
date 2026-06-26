---
name: hermes-provider-cleanup
category: hermes
description: Manage Hermes providers — cleanup dead ones, configure image gen and auxiliary services, and maintain agent profiles in the shared memory vault. Coordinates four-way consistency across models cache, auth.json, config.yaml, and .env.
tags: [hermes, cleanup, providers, configuration, maintenance, image-generation, agent-memory, self-documentation]
triggers:
  - "clean up providers"
  - "remove dead models"
  - "clean up config"
  - "remove failed providers"
  - "prune model list"
  - "configure working providers"
  - "set up image generation"
  - "configure image gen provider"
  - "together ai images"
  - "self-document"
  - "update agent profile"
  - "agent memory vault"
---

# Hermes Provider Cleanup

Companion to `provider-api-health-check`. After finding which providers work and which don't, this skill handles the actual cleanup — removing dead entries from the models cache, credential pool, and config in a coordinated, consistent way.

## Reference Files

- `references/image-gen-provider-setup.md` — configure image gen plugins (FAL, OpenAI, xAI) and fallback to direct Together API
- `references/agent-self-documentation.md` — structured workflow for updating agent profiles in the shared memory vault

## Why This Matters

Hermes has **four** separate data stores that must stay in sync:
- **models_dev_cache.json** — lists all available models per provider (used for model discovery)
- **auth.json** — credential pool with API keys and status flags
- **config.yaml** — provider definitions, default model, fallback chain
- **.env** — API key environment variables (the actual secrets that feed credential pools)

If you only remove providers from one store, the others will still reference them, causing confusing errors (models listed but unusable, credential pools that always fail, fallback chains that never activate). Additionally, config.yaml references removed providers in many places beyond the `providers:` section — see the "Config cross-references" pitfall below.

The models cache ships with 40+ providers by default, most of which have no API keys — leaving the model roster cluttered with non-functional entries. This skill reduces it to only the working set.

## Prerequisites

- Completed `provider-api-health-check` (know which providers work/fail)
- `~/.hermes/models_dev_cache.json` readable
- `~/.hermes/auth.json` readable/writable
- `~/.hermes/config.yaml` readable/writable
- Python with `json` standard library

## Procedure

### Step 1: Backup Everything First

```bash
cp ~/.hermes/models_dev_cache.json ~/.hermes/models_dev_cache.json.bak
cp ~/.hermes/config.yaml ~/.hermes/config.yaml.bak
cp ~/.hermes/auth.json ~/.hermes/auth.json.bak
```

### Step 2: Identify What to Remove

Create a target list based on API health check results:

| Category | What to Remove | Example |
|----------|---------------|---------|
| **Failed providers** | Full provider entry from all 3 stores | anthropic (401), kimi (404) |
| **OpenRouter failures** | Specific model entries in cache only | openai/gpt-5*, deepseek/deepseek-v4-* on OR |
| **Stale status flags** | Reset misleading status in auth.json | zai marked "exhausted" but working |
| **No-key providers** | Full entries with no credentials | mistral, ollama-cloud, togetherai, wafer.ai |

**MiniMax note (2026-06-18):** MiniMax works with Coding Plan keys (`sk-cp-` prefix, ~125 chars). These keys authenticate on `api.minimax.io/v1/chat/completions`. The regular `sk-api-` keys may return 402 (no balance) while `sk-cp-` keys work via the Coding Plan billing. Both key types go in the same `minimax` credential pool. Test: `curl -X POST https://api.minimax.io/v1/chat/completions -H "Authorization: Bearer KEY" -d '{"model":"MiniMax-M3","max_tokens":5,"messages":[{"role":"user","content":"hi"}]}'`

**MiniMax note:** MiniMax works with Z.AI coding plan keys (`sk-cp-` prefix). These keys return 401 on Z.AI endpoints but 200 on `api.minimax.io`. Direct MiniMax keys (`sk-api-` prefix) need account balance (402 if empty).

### Step 3: Clean Models Cache

The models cache is a flat dict keyed by provider name. Filter it:

```python
import json

with open('/home/ubuntu/.hermes/models_dev_cache.json') as f:
    data = json.load(f)

failed_providers = ['anthropic', 'kimi-for-coding', 'minimax', ...]
no_key_providers = ['mistral', 'ollama-cloud', 'togetherai', ...]

for provider in failed_providers + no_key_providers:
    if provider in data:
        del data[provider]

with open('/home/ubuntu/.hermes/models_dev_cache.json', 'w') as f:
    json.dump(data, f, indent=2)
```

For **OpenRouter model filtering**, remove specific model IDs from the openrouter model list:

```python
if 'openrouter' in data:
    or_models = data['openrouter'].get('models', [])
    patterns_to_remove = ['openai/gpt-5', 'deepseek/deepseek-v4-']
    data['openrouter']['models'] = [
        m for m in or_models 
        if not any(p in m['id'] for p in patterns_to_remove)
    ]
```

**Important:** Do NOT remove all OpenRouter entries just because some models fail — OpenRouter serves 150+ models that work (Claude, Grok, Gemini, Llama, Qwen, etc.).

### Step 4: Refresh Stale Model Lists

Refreshing cached model lists prevents stale entries and missing new models:

```python
import subprocess, json

def refresh_models(base_url, api_key, provider_name):
    """Fetch fresh model list from provider API and update cache."""
    headers = ["-H", f"Authorization: Bearer {api_key}"]
    r = subprocess.run(
        ["curl", "-s"] + headers + [f"{base_url}/models"],
        capture_output=True, text=True, timeout=10
    )
    if r.returncode == 0:
        try:
            api_models = json.loads(r.stdout).get('data', [])
            cached_ids = {m['id'] for m in data[provider_name].get('models', [])}
            fresh_ids = [m['id'] for m in api_models]
            new_models = [m for m in fresh_ids if m not in cached_ids]
            # Update cache with combined model list
            return {"existing": len(cached_ids), "new": new_models}
        except json.JSONDecodeError:
            return {"error": "failed to parse API response"}
```

### Step 5: Clean Auth.json Credential Pools

Remove dead credential pools and reset stale status flags:

```python
with open('/home/ubuntu/.hermes/auth.json') as f:
    auth = json.load(f)

# Remove dead pools
for pool_name in ['kimi-coding', 'anthropic', 'minimax', 'copilot']:
    if pool_name in auth.get('credential_pool', {}):
        del auth['credential_pool'][pool_name]

# Reset stale exhausted status (ZAI often shows exhausted but actually works)
for pool_name, creds in auth.get('credential_pool', {}).items():
    for c in creds:
        if c.get('last_status') == 'exhausted':
            c['last_status'] = None

with open('/home/ubuntu/.hermes/auth.json', 'w') as f:
    json.dump(auth, f, indent=2)
```

### Step 6: Update Config.yaml

Three things to update in config:

**a) Default model/provider** — set to a provider that demonstrably works:
```yaml
model:
  default: deepseek-reasoner
  provider: deepseek
```

**b) Add provider definitions** for new working providers:
```yaml
providers:
  # Existing providers stay
  deepseek:
    base_url: https://api.deepseek.com/v1
    models:
      deepseek-reasoner:
        context_window: 65536
        max_tokens: 8192
        reasoning: true
      deepseek-chat:
        context_window: 131072
        max_tokens: 8192
        reasoning: false
  zai:
    base_url: https://api.z.ai/api/coding/paas/v4
    models:
      glm-5.1:
        context_window: 128000
        max_tokens: 4096
        reasoning: true
```

**c) Set fallback chain** to working providers:
```yaml
fallback_providers:
  - zai
```

**d) Remove dead credential pool strategies:**
```yaml
credential_pool_strategies:
  # Remove: minimax: fill_first
  openrouter: round_robin
```

### Step 7: Clean .env API Keys

The `.env` file contains the actual API key secrets. When removing providers, their keys must be removed or commented out — otherwise `hermes config check` still lists them, and credential pools can still pick them up on restart.

Two approaches:

**A) Keep-based cleanup** (when you know exactly what to keep):
```python
import os
env_path = os.path.expanduser('~/.hermes/.env')
with open(env_path) as f:
    lines = f.readlines()

# Only these provider families stay
KEEP_PROVIDERS = {'DEEPSEEK', 'XIAOMI', 'KIMI', 'GLM', 'ZAI'}
# Plus platform keys: TELEGRAM_, DISCORD_, API_SERVER_, TERMINAL_, BROWSER_

new_lines = []
for line in lines:
    s = line.strip()
    if not s or s.startswith('#'):
        new_lines.append(line)
        continue
    if '=' in s:
        key = s.split('=')[0].strip()
        # Keep platform + infrastructure keys
        if any(key.startswith(p) for p in ['TELEGRAM_', 'DISCORD_', 'API_SERVER_', 
                'TERMINAL_', 'BROWSER', 'WEB_TOOLS_', 'VISION_TOOLS_', 'MOA_TOOLS_',
                'IMAGE_TOOLS_', 'VOICE_TOOLS_']):
            new_lines.append(line)
            continue
        # Check if key belongs to a kept provider
        if any(key.startswith(p) for p in KEEP_PROVIDERS):
            new_lines.append(line)
            continue
        # Has an actual value and is a provider-like key → comment out
        val = s.split('=', 1)[1].strip()
        if val and not val.startswith('your_'):
            if any(tag in key for tag in ['API_KEY', 'TOKEN', 'BASE_URL']):
                new_lines.append(f'# {key}=   # REMOVED - provider purged\n')
                continue
    new_lines.append(line)

with open(env_path, 'w') as f:
    f.writelines(new_lines)
```

**B) Remove-specific approach** (when removing named providers):
```bash
# Comment out specific keys
sed -i 's/^OPENROUTER_API_KEY=/# OPENROUTER_API_KEY=  # REMOVED/' ~/.hermes/.env
sed -i 's/^ANTHROPIC_API_KEY=/# ANTHROPIC_API_KEY=  # REMOVED/' ~/.hermes/.env
sed -i 's/^COPILOT_GITHUB_TOKEN=/# COPILOT_GITHUB_TOKEN=  # REMOVED/' ~/.hermes/.env
# etc.
```

### Step 8: Verify Consistency and Restart

Check that all four files agree:

```bash
# 1. Full config check (catches missing keys, stale refs, auxiliary model issues)
hermes config check 2>&1

# 2. Models cache shows only working providers
python3 -c "import json; d=json.load(open('/home/ubuntu/.hermes/models_dev_cache.json')); print(list(d.keys()))"

# 3. Auth pools match working providers
python3 -c "import json; d=json.load(open('/home/ubuntu/.hermes/auth.json')); print(list(d.get('credential_pool',{}).keys()))"

# 4. Config has no references to removed providers
grep -n "copilot\|openrouter\|anthropic\|minimax\|github" ~/.hermes/config.yaml || echo "Clean - no dead refs"

# 5. .env has only intended provider keys
grep -E "^(?!#)" ~/.hermes/.env | grep -E "API_KEY|TOKEN" | cut -d= -f1

# 6. Default model is from a working provider
grep -A2 "^model:" ~/.hermes/config.yaml

# 7. Restart gateway so changes take effect for messaging platforms
hermes gateway restart
```

Gateway restart has a 60s `RestartSec` backoff — check status after:
```bash
hermes gateway status
```

## Common Pitfalls

### 1. Don't Delete What You Can't Recreate
Always backup before deleting. Models cache can be rebuilt with `hermes model`, but auth.json and config.yaml modifications are manual — no redo.

### 2. Xiaomi Has Two Endpoints
- `token-plan-ams.xiaomimimo.com/v1` — Token Plan AMS (works today)
- `api.xiaomimimo.com/v1` — Main Xiaomi API

Both work independently. Check both during provider health check.

### 3. OpenRouter Is Useful Despite Some Failures
OpenRouter can serve models that no direct provider has keys for (Claude, Grok, Gemini, Llama, Qwen). Don't remove OpenRouter entirely just because the OpenAI gpt-5.x models fail on it — those need a direct OpenAI API key.

### 4. Four-Way Consistency Is Mandatory
If models cache lists a provider but config.yaml doesn't, or vice versa, Hermes can get confused. After cleanup, all four stores (models cache, auth.json, config.yaml, .env) must agree. An extra credential pool with no model cache entry is harmless but wasteful; a model cache entry with no credential pool will show up in `hermes model` but always fail if you try to use it.

### 5. Stale "exhausted" Flags
The `last_status` field in auth.json credential pools is not actively maintained by the system. Keys marked `exhausted` may actually work. Always reset to `None` after confirming the key works via API test.

### 6. Context Window Matters
When adding provider models to config.yaml, use realistic context_window and max_tokens values from the provider's documentation. Setting them too high will cause Hermes to attempt large contexts that the model can't actually handle.

### 9. Z.AI Has Two Separate Endpoint Families

Z.AI (`api.z.ai`) runs TWO independent API surfaces with different key permissions:

| Family | Base Path | Auth Format | Key Type That Works |
|--------|-----------|-------------|---------------------|
| Anthropic-compatible | `/api/v1/*` | `x-api-key` header | MCP keys (models only, 403 on messages) |
| OpenAI-compatible | `/api/coding/paas/v4/*` | `Authorization: Bearer` | Inference keys |

**Hermes uses the OpenAI-compatible family** via `zai-coding-plan` provider (`/api/coding/paas/v4`).
**Claude Code needs the Anthropic family** for model validation but can't infer on it — requires a proxy.

The models cache has TWO Z.AI entries: `zai` (Anthropic endpoints) and `zai-coding-plan` (OpenAI endpoints). The Anthropic family uses slug names (`gpt-4o`, `gpt-4o-mini`) while the OpenAI family uses GLM names (`glm-5.2`, `glm-5.1`).

Full endpoint map: see `coding-agent-clis` skill → `references/zai-endpoint-discovery.md`.

### 10. Config Cross-References — Check ALL Sections

When removing a provider, it's not enough to delete its `providers:` entry. The provider may be referenced in many other config sections. After cleanup, grep for the removed provider name across the whole config:

```bash
grep -n "copilot\|openrouter\|anthropic" ~/.hermes/config.yaml
```

Sections that commonly reference providers by name:
| Section | Field | Example |
|---------|-------|---------|
| `model` | `provider` | `provider: copilot` |
| `providers` | provider block | `xiaomi:`, `deepseek:` |
| `fallback_providers` | provider list | `- deepseek` |
| `fallback_model` | `provider`, `model` | `provider: deepseek` |
| `delegation` | `provider`, `model` | `provider: deepseek` |
| `smart_model_routing.cheap_model` | `provider`, `model` | `provider: deepseek` |
| `auxiliary.vision` | `provider`, `model` | `provider: zai` |
| `auxiliary.web_extract` | `provider`, `model` | `provider: zai` |
| `auxiliary.compression` | `provider`, `model` | `provider: zai` |
| `tts` | `provider` | `provider: xiaomi` |
| `openrouter` | (entire section) | remove if OpenRouter is purged |
| `credential_pool_strategies` | provider name | `openrouter: round_robin` |

If a removed provider is still referenced in any of these sections, Hermes will fail silently or throw confusing errors at runtime.
The models cache (`models_dev_cache.json`) can be stale — the cached model list may be missing models that the API actually serves. After health-checking a provider's `/models` endpoint, update the cache with the fresh model list from the API response rather than keeping the old cached list. Example: Xiaomi's cached list showed 3 models but the API returned 9.

### 9. Credential Values Are Masked in Tool Output

Hermes masks secrets in tool output — any value that looks like an API key renders as `***`. This means you **cannot verify a credential by reading it back** from `grep`, `cat`, or `python3 -c "print(...)"`. The file stores the real value, but you'll only see `***`.

**Workaround — verify by length, not by content:**
```python
line = [l for l in open('/home/ubuntu/.hermes/.env') if l.startswith('GNEWS_API_KEY')][0]
val = line.strip().split('=', 1)[1]
print(f'Key length: {len(val)} chars, starts with: {val[:4]}...')
```

If the length matches the expected key format (e.g. 32 hex chars for GNews, 64 for most provider keys), the write succeeded. If it's 4 chars (`***`), the masking leaked into the file and you need to rewrite.

**Pitfall:** Inline `echo >> .env` and `sed -i` can accidentally write the masked placeholder instead of the real value if the shell variable was already masked. Safest approach: write a Python helper script that takes the key as `sys.argv[1]` and writes it directly, bypassing any shell-level masking.

## Adding a New Provider (Three-Store Wiring)

When adding a new provider (e.g. MiniMax), three stores must be updated together:

### 1. `.env` — API Key
```bash
# Uncomment or add the key line
MINIMAX_API_KEY=sk-api-xxxxx
MINIMAX_BASE_URL=https://api.minimax.io/v1
```

### 2. `config.yaml` — Provider Block
```yaml
providers:
  minimax:
    base_url: https://api.minimax.io/v1
    models:
      MiniMax-M3:
        id: MiniMax-M3
        name: MiniMax M3
        context_window: 1000000
        max_tokens: 16384
        reasoning: true
```

### 3. `auth.json` — Credential Pool
```python
import json, os
auth_path = os.path.expanduser('~/.hermes/auth.json')
with open(auth_path) as f:
    auth = json.load(f)
auth['credential_pool']['minimax'] = [{
    'api_key': api_key,
    'base_url': 'https://api.minimax.io/v1',
    'last_status': None,
    'last_used': None
}]
with open(auth_path, 'w') as f:
    json.dump(auth, f, indent=2)
```

### 4. Verify
```bash
hermes config check 2>&1 | grep -i minimax  # Should show ✓ for key + base_url
```

**Pitfall:** The `.env` file is credential-masked in tool output. Verify key length, not content:
```python
line = [l for l in open(os.path.expanduser('~/.hermes/.env')) if l.startswith('MINIMAX_API_KEY')][0]
val = line.strip().split('=', 1)[1]
print(f'Key length: {len(val)} chars')  # Should be >50, not 3 (which means masked)
```

## Verification

After cleanup:
1. `hermes config check` — should show ✓ for kept providers, no stale references
2. `hermes config` — review model section, auxiliary, delegation
3. Try the default model: send a simple message
4. Test delegation: `delegate_task` with a simple goal
5. Test fallback: disable the default provider temporarily, confirm fallback activates
6. `hermes gateway status` — confirm gateway running after restart
