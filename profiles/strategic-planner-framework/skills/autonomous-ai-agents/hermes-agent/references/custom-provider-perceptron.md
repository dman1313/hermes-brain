# Perceptron Custom Provider

**Endpoint:** `https://api.perceptron.inc/v1` (OpenAI-compatible chat completions)
**Auth:** Bearer token (format: `ak.xxx...`)

## Free Models

| Model | Vision | Reasoning | Notes |
|-------|--------|-----------|-------|
| `isaac-0.2-1b` | ✅ | ❌ | Fastest, lowest latency |
| `isaac-0.2-2b-preview` | ✅ | ✅ | Better quality, has reasoning |
| `perceptron-mk1` | ✅ | ✅ | Requires paid quota (returns 429 on free tier) |

## Config Entry

```yaml
custom_providers:
  - name: perceptron
    base_url: https://api.perceptron.inc/v1
    api_key: ak.QXDT_VtDSNeOaOwu5-hp6Q.R0BLgRqBMbVmrBiI6xpcWePZXRIHypXA5SQ1Yan-wtE
    models:
      - isaac-0.2-2b-preview
      - isaac-0.2-1b
      - perceptron-mk1
```

## Vision Auxiliary Config

```yaml
auxiliary:
  vision:
    provider: custom:perceptron
    model: isaac-0.2-2b-preview
```

## Tested Working

- Text-only requests with both Isaac models ✅
- Base64-encoded image requests with `isaac-0.2-1b` ✅
- `isaac-0.2-2b-preview` returns reasoning_content in response

## Tips

- Perceptron's server fetches images from URLs — use publicly accessible URLs or base64 data URIs
- For image analysis in Hermes, the vision tool will send the image URL or base64 data automatically
- `perceptron-mk1` supports additional features like object detection bounding boxes, video clipping, and CLIP-style temporal localization
