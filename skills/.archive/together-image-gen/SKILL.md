---
name: together-image-gen
description: "Generate and edit images via Together AI's FLUX, Imagen, Seedream, and other models."
version: 1.0.0
tags: [image, generation, together, flux, creative]
---

# Together AI Image Generation

Generate images via Together AI using FLUX, Google Imagen, ByteDance Seedream, and 30+ models.

## Script

`~/.hermes/scripts/together-img.py` — handles API calls, JPEG conversion, all parameters.

## Quick Usage

```bash
# Simple generation
python3 ~/.hermes/scripts/together-img.py "a golden retriever puppy" -o ~/output.jpg

# High quality with FLUX.2 Pro
python3 ~/.hermes/scripts/together-img.py "a zen garden" -m black-forest-labs/FLUX.2-pro -s 28 -o ~/zen.jpg

# Landscape
python3 ~/.hermes/scripts/together-img.py "mountain panorama" -W 1344 -H 768 -o ~/landscape.jpg

# Portrait
python3 ~/.hermes/scripts/together-img.py "fashion portrait" -W 768 -H 1344 -o ~/portrait.jpg

# Edit existing image (Kontext models)
python3 ~/.hermes/scripts/together-img.py "make it a watercolor painting" --image-url "https://example.com/photo.jpg" -m black-forest-labs/FLUX.1-kontext-pro -o ~/edited.jpg

# With reference images (FLUX.2/Google)
python3 ~/.hermes/scripts/together-img.py "change car color to blue" --reference "https://example.com/car.jpg" -m black-forest-labs/FLUX.2-pro -o ~/edited.jpg

# Multiple variations
python3 ~/.hermes/scripts/together-img.py "abstract art" --n 4 -o ~/variations.jpg

# Reproducible with seed
python3 ~/.hermes/scripts/together-img.py "a cat" --seed 42 -o ~/cat.jpg

# Negative prompt
python3 ~/.hermes/scripts/together-img.py "a portrait" --negative "blurry, distorted, extra fingers" -o ~/portrait.jpg

# List available models
python3 ~/.hermes/scripts/together-img.py --list-models
```

## Models (32 available)

**Text-to-image (fast):**
- `black-forest-labs/FLUX.1-schnell` — 4 steps, fast, default

**Text-to-image (quality):**
- `black-forest-labs/FLUX.2-pro` — production quality
- `black-forest-labs/FLUX.2-max` — highest quality
- `black-forest-labs/FLUX.2-dev` — dev quality, guidance_scale support
- `black-forest-labs/FLUX.2-flex` — flexible, guidance_scale support
- `black-forest-labs/FLUX.1.1-pro` — legacy pro

**Image editing:**
- `black-forest-labs/FLUX.1-kontext-pro` — edit with --image-url
- `black-forest-labs/FLUX.1-kontext-max` — best editing, --image-url

**Other providers:**
- `ByteDance-Seed/Seedream-5.0-lite` / `4.0` / `3.0`
- `google/imagen-4.0-ultra` / `4.0-fast` / `4.0-preview`
- `google/flash-image-3.1` / `flash-image-2.5` / `gemini-3-pro-image`
- `openai/gpt-image-1.5`
- `xai/grok-imagine-image-pro`
- `ideogram/ideogram-3.0`
- `Qwen/Qwen-Image-2.0-Pro` / `Qwen-Image-2.0`
- `stabilityai/stable-diffusion-3-medium` / `sdxl-base-1.0`
- `HiDream-ai/HiDream-I1-Full` / `Dev` / `Fast`

## Parameters

| Param | Default | Notes |
|-------|---------|-------|
| `-o` | `~/generated_image.jpg` | Output path |
| `-m` | `FLUX.1-schnell` | Model |
| `-W` | 1024 | Width (multiples of 8) |
| `-H` | 1024 | Height (multiples of 8) |
| `-s` | auto (4 for schnell, 28 for others) | Diffusion steps |
| `--seed` | random | Fixed seed for reproducibility |
| `--guidance` | 3.5 | How closely to follow prompt (1-10) |
| `--negative` | none | What to avoid |
| `--n` | 1 | Number of images (1-4) |
| `--format` | jpeg | Output format |
| `--image-url` | none | Source image for Kontext editing |
| `--reference` | none | Reference images for FLUX.2/Google |
| `--safety-off` | off | Disable NSFW checker |

## Prompt Tips

- Be specific: subject, setting, lighting, composition, style
- Add style refs: "National Geographic style", "studio photograph", "8k"
- Quality modifiers: "highly detailed", "professional", "cinematic"
- Negative prompt for quality: "blurry, low quality, distorted, pixelated"
- guidance_scale 8-10 when model ignores parts of prompt
- guidance_scale 1-5 when output looks oversaturated
- **Full body shots**: user often wants the entire subject visible (head to tail). Add "full body shot, entire subject visible, wide angle" to the prompt. Without this, image models default to close-up portraits.

## Delivering Images to Telegram

The `MEDIA:/path` tag in response text does NOT reliably deliver images on Telegram. Use the Telegram Bot API directly:

```bash
source ~/.hermes/.env
curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendPhoto" \
  -F chat_id="${TELEGRAM_HOME_CHANNEL}" \
  -F photo="@/path/to/image.jpg" \
  -F caption="Description text"
```

Always verify the response shows `"ok": true`. If it returns 401, the bot token may be expired or the env vars weren't loaded.

## Pricing (cheapest usable → expensive)

| Model | $/MP | 1024×1024 cost | Speed | Notes |
|-------|------|----------------|-------|-------|
| FLUX.1-schnell | $0.0027 | ~$0.003 | 0.4s | **Default — best value** |
| HiDream-I1-Fast | $0.0032 | ~$0.003 | cold start | |
| HiDream-I1-Dev | $0.0045 | ~$0.005 | cold start | |
| Qwen-Image | $0.0058 | ~$0.006 | cold start | |
| FLUX.2-dev | $0.0154 | ~$0.016 | varies | guidance_scale support |
| FLUX.2-pro | $0.03 | ~$0.03 | varies | production quality |
| FLUX.2-max | $0.07 | ~$0.07 | varies | highest quality |

**Rule: FLUX.1-schnell is the sweet spot.** Niche models cold-start 35+ min on serverless.

## Pitfalls

- Cloudflare blocks `urllib` — script uses `curl` subprocess (don't switch to requests/urllib)
- Kontext models use `aspect_ratio` not `width/height` (script handles this automatically)
- Safety checker runs on all models except FLUX Schnell
- Each image costs money — use `--n 4` for variations, not 4 separate calls
- Dimensions must be multiples of 8
- `response_format: "base64"` is used to avoid URL fetch round-trips
- **Cold starts kill cheap models** — DreamShaper ($0.0006/MP), Juggernaut-Lightning ($0.0017/MP), HiDream-Fast ($0.0032/MP) all cold-start 35-125+ min on serverless. FLUX.1-schnell ($0.0027/MP, 0.4s) is the cheapest *usable* model. Don't default to niche models.
