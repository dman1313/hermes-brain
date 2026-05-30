# Image Generation Plugin Architecture

## How `image_generate` resolves a provider

1. Reads `image_gen.provider` from `config.yaml`
2. Looks up a registered plugin by that name in `plugins/image_gen/`
3. Calls `provider.is_available()` to check env vars + dependencies
4. Calls `provider.generate(prompt, aspect_ratio, **kwargs)`

## Registered plugins (source: `plugins/image_gen/`)

| Plugin dir | Provider name | Auth | Model | Notes |
|-----------|---------------|------|-------|-------|
| `fal/` | `fal` | `FAL_KEY` env or Nous gateway | Configurable via `image_gen.model` | Nous gateway may 403 models not enabled on subscription |
| `openai/` | `openai` | `OPENAI_API_KEY` env | Hardcoded `gpt-image-2` (low/medium/high quality tiers) | Does NOT read `image_gen.api_key` or `image_gen.base_url` from config |
| `openai-codex/` | `openai-codex` | Codex OAuth token | `gpt-image-2` via ChatGPT backend | No API key needed, uses Responses API |
| `xai/` | `xai` | `XAI_API_KEY` env | Grok image model | |

## Common failures

- `"no plugin registered that name"` — `image_gen.provider` set to a value that has no plugin (e.g., `together`, `stability`, `midjourney`)
- `"HTTP 403"` from FAL — Nous Subscription gateway rejected the model. Fix: set `FAL_KEY` for direct access
- `"OPENAI_API_KEY not set"` — openai plugin reads from env ONLY, not from `image_gen.api_key` config

## Key source files

- Provider base class: `agent/image_gen_provider.py`
- Plugin registry: each plugin's `register(ctx)` calls `ctx.register_image_gen_provider()`
- Config reader: each plugin reads `image_gen` section independently via `hermes_cli.config.load_config()`

## Adding a new image gen plugin

1. Create `plugins/image_gen/<name>/__init__.py`
2. Implement `ImageGenProvider` subclass with `name`, `is_available()`, `generate()`
3. Add `register(ctx)` entry point
4. Enable: `hermes plugins enable image_gen/<name>`
