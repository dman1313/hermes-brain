---
name: image-generation
description: "Generate images via AI providers and use Together AI as a custom LLM provider. Covers Together AI (FLUX), FAL, OpenAI DALL-E, xAI Grok, and Together AI chat inference (DeepSeek, GLM, Kimi, Qwen, Llama). Use when the user asks to create an image or configure Together AI as an LLM provider."
version: 1.0.0
author: Hermes
tags: [creative, image, generation, ai-art, together, flux, dall-e, llm-provider, custom-provider]
---

# Image Generation

Generate images from text prompts using AI providers.

## Provider Matrix

| Provider | Native `image_generate`? | Plugin name | Notes |
|----------|--------------------------|-------------|-------|
| FAL | ✅ | `image_gen/fal` | Nous Subscription gateway may block models (HTTP 403). Set `FAL_KEY` for direct access. |
| OpenAI | ✅ | `image_gen/openai` | Requires `OPENAI_API_KEY`. Hardcoded to `gpt-image-2`. |
| OpenAI (Codex) | ✅ | `image_gen/openai-codex` | Uses ChatGPT/Codex OAuth — no API key needed. |
| xAI | ✅ | `image_gen/xai` | Grok image generation. |
| **Together AI** | ❌ | *none* | Use the wrapper script (see below). Default model: `FLUX.1-schnell`. |

## Together AI (Primary — use this)

No native plugin exists. Use the wrapper script:

```bash
python3 ~/.hermes/scripts/together-img.py "prompt" [output_path] [model] [width] [height]
```

**Defaults:** model=`black-forest-labs/FLUX.1-schnell`, 1024×1024, output=`~/generated_image.jpg` (always JPEG for smaller files)
| Model ID | Notes |
|----------|-------|
| `black-forest-labs/FLUX.1-schnell` | Fast, default |
| `black-forest-labs/FLUX.1-krea-dev` | Artistic style |
| `black-forest-labs/FLUX.1-kontext-pro` | Context-aware |
| `black-forest-labs/FLUX.1-kontext-max` | Context-aware, highest quality |
| `black-forest-labs/FLUX.2-dev` | Higher quality |
| `black-forest-labs/FLUX.2-flex` | Flexible quality |
| `black-forest-labs/FLUX.2-pro` | Higher quality |
| `black-forest-labs/FLUX.2-max` | Highest quality |
| `ByteDance-Seed/Seedream-3.0` | ByteDance model |
| `ByteDance-Seed/Seedream-4.0` | ByteDance model (newer) |
| `google/imagen-4.0-fast` | Google's model |
| `google/flash-image-2.5` | Fast Google model |
| `ideogram/ideogram-3.0` | Good for text-in-image |
| `HiDream-ai/HiDream-I1-Fast` | Fast generation |
| `stabilityai/stable-diffusion-xl-base-1.0` | Stable Diffusion XL |
| `Wan-AI/Wan2.6-image` | Wan AI model |

### Pitfalls

1. **Cloudflare blocks Python `urllib.request`** — Together API returns HTTP 403 (error code 1010) when called from `urllib` due to missing User-Agent. The script uses `subprocess`+`curl` to work around this. Do NOT rewrite to use `urllib` or `requests` without setting a browser-like User-Agent header.

2. **`image_generate` native tool fails with `provider: together`** — there's no registered plugin with that name. The tool will return `"no plugin registered that name"`. Always use the script instead.

3. **FAL via Nous gateway may reject models** — the Nous Subscription proxy returns HTTP 403 for FAL models that aren't enabled. Either set `FAL_KEY` env var for direct FAL access, or use Together AI instead.

4. **Steps parameter** — FLUX.1-schnell only needs 4 steps. Higher-quality models (FLUX.2-pro, FLUX.2-max) may benefit from more steps (20-50). The script defaults to 4.

## Workflow

When the user asks for an image:

1. Call the script via `terminal`: `python3 ~/.hermes/scripts/together-img.py "prompt" ~/output.jpg`
2. Send the resulting file with `MEDIA:/path/to/file`
3. If the user wants a different style/quality, try a different model (e.g., `FLUX.2-pro` for higher quality)
4. For aspect ratios: use `width` and `height` params (e.g., 1024×768 for landscape, 768×1024 for portrait)

## Config Reference

Current Hermes config (may be stale):
```yaml
image_gen:
  provider: fal          # native tool — doesn't work with Together
  model: fal-ai/flux/schnell
```

The native tool config is separate from the script. The script reads `TOGETHER_API_KEY` from env or falls back to the hardcoded key.

## Together AI as LLM Chat Provider

Together AI can also serve as a custom LLM provider for chat inference (DeepSeek, GLM, Kimi, Qwen, Llama, etc.) via the `custom_providers` config.

### Config (config.yaml)

```yaml
custom_providers:
  - name: together
    base_url: https://api.together.xyz/v1
    api_key: <TOGETHER_API_KEY>
    models:
      - deepseek-ai/DeepSeek-V4-Pro
      - zai-org/GLM-5.1
      - moonshotai/Kimi-K2.6
      - Qwen/Qwen3.6-Plus
      - Qwen/Qwen3.7-Max
      - meta-llama/Llama-4-Maverick
```

Usage: set `provider = custom:together` and `model = <model-id>` in agent config or delegation overrides.

### Model ID Pitfalls

Model IDs on Together don't always match what you'd guess:

| You might guess | Actual ID on Together |
|----------------|----------------------|
| `zhipu/GLM-5.1` | `zai-org/GLM-5.1` |
| `moonshot/Kimi-K2.6` | `moonshotai/Kimi-K2.6` |
| `deepseek-ai/DeepSeek-V4-Flash` | Not available (as of May 2026) |

**Verify with:**
```bash
curl -s "https://api.together.xyz/v1/models" \
  -H "Authorization: Bearer $TOGETHER_API_KEY" | python3 -c "
import sys, json
data = json.load(sys.stdin)
models = data if isinstance(data, list) else data.get('data', [])
for m in models:
    if 'keyword' in m['id'].lower():
        print(m['id'], '-', m.get('type', '?'))
"
```

## Pitfalls: native image_gen tool

The native `image_generate` tool will fail regardless of what `image_gen.provider` is set to (since Together has no registered plugin). Recommended: set `image_gen.provider = fal` and accept that the native tool will return an error. When you need images, use the script above instead. Alternatively, disable the `image_gen` toolset entirely via `hermes tools disable image_gen` to suppress errors.
