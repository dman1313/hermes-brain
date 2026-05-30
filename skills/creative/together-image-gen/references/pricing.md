# Together AI Image Model Pricing (2026-05)

Source: https://docs.together.ai/docs/serverless/models

All prices per megapixel. 1024×1024 ≈ 1.05 MP.

## Text-to-Image Models

| Model | API string | $/MP | Default steps | Notes |
|-------|-----------|------|---------------|-------|
| DreamShaper | Lykon/DreamShaper | $0.0006 | — | Ultra cheap but 35+ min cold start |
| Juggernaut Lightning | Rundiffusion/Juggernaut-Lightning-Flux | $0.0017 | — | Slow cold start |
| SD3 Medium | stabilityai/stable-diffusion-3-medium | $0.0019 | — | |
| SDXL 1.0 | stabilityai/stable-diffusion-xl-base-1.0 | $0.0019 | — | |
| FLUX.1 Schnell | black-forest-labs/FLUX.1-schnell | $0.0027 | 4 | **Default — best value** |
| HiDream-I1-Fast | HiDream-ai/HiDream-I1-Fast | $0.0032 | — | |
| HiDream-I1-Dev | HiDream-ai/HiDream-I1-Dev | $0.0045 | — | |
| Juggernaut Pro | RunDiffusion/Juggernaut-pro-flux | $0.0049 | — | |
| Qwen-Image | Qwen/Qwen-Image | $0.0058 | — | |
| HiDream-I1-Full | HiDream-ai/HiDream-I1-Full | $0.009 | — | |
| FLUX.1 Krea Dev | black-forest-labs/FLUX.1-krea-dev | $0.025 | 28 | |
| Seedream 3.0 | ByteDance-Seed/Seedream-3.0 | $0.018 | — | |
| FLUX.2 Dev | black-forest-labs/FLUX.2-dev | $0.0154 | 28 | guidance_scale support |
| FLUX.2 Pro | black-forest-labs/FLUX.2-pro | $0.03 | — | production quality |
| Seedream 4.0 | ByteDance-Seed/Seedream-4.0 | $0.03 | — | |
| Flash Image 2.5 | google/flash-image-2.5 | $0.039 | — | |
| FLUX.1.1 Pro | black-forest-labs/FLUX.1.1-pro | $0.04 | — | |
| Kontext Pro | black-forest-labs/FLUX.1-kontext-pro | $0.04 | 28 | image editing via image_url |
| Flash Image 3.1 | google/flash-image-3.1 | $0.05 | — | |
| Imagen 4.0 Fast | google/imagen-4.0-fast | $0.02 | — | |
| Imagen 4.0 Ultra | google/imagen-4.0-ultra | $0.06 | — | |
| Ideogram 3.0 | ideogram/ideogram-3.0 | $0.06 | — | |
| FLUX.2 Max | black-forest-labs/FLUX.2-max | $0.07 | 50 | highest quality |
| Grok Imagine | xai/grok-imagine-image-pro | $0.07 | — | |
| Kontext Max | black-forest-labs/FLUX.1-kontext-max | $0.08 | 28 | best editing |
| Gemini 3 Pro | google/gemini-3-pro-image | $0.134 | — | |

## Cost Formula (FLUX models)

```
Cost = MP × Price_per_MP × (Steps ÷ Default_Steps)
```
- Only applies if steps > default steps
- Using fewer steps does NOT reduce cost
- MP = (Width × Height) / 1,000,000
