---
name: hermes-model-roster
category: hermes
description: Display comprehensive LLM roster from Hermes system configuration and models cache
tags: [hermes, models, inventory, diagnostic]
triggers:
  - "show me your llm roster"
  - "what models do you have"
  - "list available models"
  - "hermes model inventory"
---

# Hermes Model Roster

This skill provides a comprehensive overview of all LLM models and providers available in your Hermes system.

## Prerequisites

- Hermes Agent installed and configured
- Access to Hermes configuration files
- JSON parsing capability (jq recommended)

## Procedure

1. **Check current configuration** (`hermes config`)
   - Default model and provider
   - Smart model routing settings
   - Delegation model configuration
   - Auxiliary model overrides (vision, web_extract, compression, etc.)

2. **Cross-reference API keys** (`.env` file)
   - Only providers with valid API keys are actually usable
   - grep for `API_KEY` lines with actual values (not commented, not `your_`)
   - This is the definitive "what can you actually call" list

3. **Parse models caches**
   - `models_dev_cache.json` — 100+ providers, the full catalog
   - `model_catalog.json` — structured catalog with metadata/providers/version
   - The cache shows what's *known*, not what's *usable* — always cross-reference with `.env`

4. **Distinguish usable from catalog-only**
   - A provider in the cache but with no API key in `.env` is not usable
   - A provider with an API key but not in `providers:` section of config.yaml may still work via auto-discovery
   - Present clearly: "X providers in cache, Y with API keys, Z explicitly configured"

## Key Findings Structure

Present the roster in this format:

```
## Primary Configuration
- Default Model: [model] → provider: [provider]
- Session Model: [current model in use]

## Actually Usable Providers (API key + configured)
Count: N
### [Provider Name] — [model list]
### ...

## Catalog-Only Providers (in cache, no API key)
Count: M
(not callable — add API key to .env to activate)

## Auxiliary Model Configuration
- Vision: [provider/model]
- Web Extract: [provider/model]
- Compression: [provider/model]
- Delegation: [provider/model]
- TTS: [provider]
```

## Notes

- The models cache typically contains 100+ models across 40+ providers
- Smart routing automatically selects appropriate models based on task complexity
- Provider availability depends on API keys and authentication
- Some providers require specific environment variables to be configured

## Troubleshooting

If encountering JSON parsing errors with hyphenated provider names:
- Use proper quoting around keys containing hyphens
- This is required because some parsers treat hyphens as subtraction operators

If models cache is missing or empty:
- Run `hermes model` command to refresh the cache
- Check internet connectivity for provider API access
- Verify API keys are properly configured in your environment

## Common Providers Found

- **OpenAI/OpenAI Codex**: GPT-5 series, GPT-4o, o1/o3/o4 series
- **Anthropic**: Claude Sonnet, Opus, Haiku series
- **ZAI**: GLM series (4.5, 4.6, 4.7, 5, 5.1)
- **Kimi For Coding**: Kimi K2 series, specialized for coding tasks
- **OpenRouter**: DeepSeek, LFM, Trinity, FLUX models and many others
- **Others**: 302.AI, Google/Vertex, MiniMax, Perplexity, etc.