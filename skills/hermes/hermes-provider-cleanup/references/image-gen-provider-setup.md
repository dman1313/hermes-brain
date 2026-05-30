# Image Generation Provider Setup

Hermes supports multiple image generation backends. The default is the Nous-managed gateway (FAL). To use a direct API provider instead:

## Configuration Keys

```bash
hermes config set image_gen.provider <provider_name>
hermes config set image_gen.api_key <api_key>
hermes config set image_gen.use_gateway false   # bypass Nous gateway, call provider directly
```

Then restart: `hermes gateway restart`

## Registered Image Gen Plugins

Only these image gen plugins actually exist (verify with `hermes plugins list | grep image_gen`):

| Plugin name              | `image_gen.provider` value | Auth requirement                          | Notes                                        |
|--------------------------|---------------------------|-------------------------------------------|----------------------------------------------|
| `image_gen/fal`          | `fal`                     | Nous Subscription gateway OR `FAL_KEY`    | Default. Gateway may 403 on some FAL models  |
| `image_gen/openai`       | `openai`                  | `OPENAI_API_KEY` env var (hardcoded name) | Ignores `image_gen.api_key`; needs env var   |
| `image_gen/openai-compat`| (check plugin list)       | Varies                                    | May support custom base_url + API key        |
| `image_gen/xai`          | `xai`                     | xAI API key                               | Grok Imagine Image models                    |

**⚠️ There is NO `together` image gen plugin.** Setting `image_gen.provider: together` will fail with "no plugin registered that name." Together AI is a model-provider plugin, not an image gen plugin.

## Pitfalls

- **Gateway bypass required for direct providers.** If `use_gateway` stays `true`, Hermes routes through the Nous tool gateway regardless of the provider setting. Set it to `false` when using your own API key.
- **Config file is protected.** `~/.hermes/config.yaml` cannot be edited with `patch` or `write_file`. Always use `hermes config set`.
- **API key goes in config, not .env.** The `image_gen.api_key` config key is the intended location. Don't rely on environment variables for image gen.
- **Restart required.** Image gen config changes don't hot-reload. Run `hermes gateway restart`.
- **OpenAI plugin ignores image_gen.api_key.** The `openai` image gen plugin reads `OPENAI_API_KEY` from the environment, not from `image_gen.api_key`. Setting the config key alone won't authenticate.
- **FAL models may be 403'd by Nous gateway.** Even with `image_gen/fal` enabled, specific FAL model IDs (e.g. `fal-ai/flux-2/klein/9b`) may be blocked by the Nous Subscription gateway. The error message suggests setting `FAL_KEY` directly or picking a different model.
- **image_generate tool ignores image_gen.model config.** The `image_generate` tool appears to use a hardcoded default model, not the `image_gen.model` config key. Changing the model via config doesn't take effect.
- **Plugins must be enabled.** Image gen plugins are `not enabled` by default. Run `hermes plugins enable image_gen/<name>` before configuring.

## Fallback: Direct Together API via curl

When no image gen plugin works, Together AI's OpenAI-compatible API can generate images directly:

```bash
# 1. List available image models
curl -s "https://api.together.xyz/v1/models" \
  -H "Authorization: Bearer $TOGETHER_API_KEY" | \
  python3 -c "import sys,json; data=json.load(sys.stdin); models=data if isinstance(data,list) else data.get('data',[]); [print(m.get('id')) for m in models if m.get('type')=='image' or 'flux' in str(m.get('id','')).lower() or 'stable' in str(m.get('id','')).lower()]"

# 2. Generate image (b64_json response)
curl -s -X POST "https://api.together.xyz/v1/images/generations" \
  -H "Authorization: Bearer $TOGETHER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "black-forest-labs/FLUX.1-schnell",
    "prompt": "your prompt here",
    "width": 1024, "height": 1024,
    "steps": 4, "n": 1,
    "response_format": "b64_json"
  }' | python3 -c "
import sys, json, base64, os
data = json.load(sys.stdin)
if 'error' in data: print('ERROR:', data['error'])
elif 'data' in data:
    path = os.path.expanduser('~/generated.png')
    with open(path, 'wb') as f: f.write(base64.b64decode(data['data'][0]['b64_json']))
    print('SAVED:', path)
"
```

**Available Together image models (as of 2026-05):**
- `black-forest-labs/FLUX.1-schnell` — fast, good quality
- `black-forest-labs/FLUX.1.1-pro` — higher quality
- `black-forest-labs/FLUX.2-dev` / `FLUX.2-pro` / `FLUX.2-max` — latest gen
- `stabilityai/stable-diffusion-xl-base-1.0` — classic SDXL
- `google/imagen-4.0-fast`, `google/flash-image-2.5` — Google models
- `ideogram/ideogram-3.0` — good for text-in-image

**⚠️ Avoid `*-Free` models** — they require dedicated endpoints, not serverless.

## Verification

```bash
# Check current image_gen config
grep -A 5 "^image_gen:" ~/.hermes/config.yaml

# Check which image gen plugins are available and enabled
hermes plugins list | grep image_gen

# Test with a simple image generation request
# (use the image_generate tool in a Hermes session)
```
