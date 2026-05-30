#!/usr/bin/env python3
"""Generate images via Together AI's FLUX API.

Usage: python together-img.py "prompt" [output_path] [model] [width] [height]

Defaults:
  model  = black-forest-labs/FLUX.1-schnell
  width  = 1024
  height = 1024
  output = ~/generated_image.jpg

Available models (image):
  black-forest-labs/FLUX.1-schnell     (fast, free-tier)
  black-forest-labs/FLUX.1-krea-dev
  black-forest-labs/FLUX.1-kontext-pro
  black-forest-labs/FLUX.1-kontext-max
  black-forest-labs/FLUX.2-dev
  black-forest-labs/FLUX.2-flex
  black-forest-labs/FLUX.2-pro
  black-forest-labs/FLUX.2-max
  ByteDance-Seed/Seedream-3.0
  ByteDance-Seed/Seedream-4.0
  google/imagen-4.0-fast
  google/flash-image-2.5
  ideogram/ideogram-3.0
  HiDream-ai/HiDream-I1-Fast
  stabilityai/stable-diffusion-xl-base-1.0
  Wan-AI/Wan2.6-image
"""

import json
import os
import subprocess
import sys

API_KEY = os.environ.get("TOGETHER_API_KEY", "tgp_v1_Pd6jzUWEqQEXEGZUyf1INX7jd00nyySJ9FuO1Db-yFg")
API_URL = "https://api.together.xyz/v1/images/generations"
DEFAULT_MODEL = "black-forest-labs/FLUX.1-schnell"


def generate(prompt: str, output_path: str = "", model: str = "",
             width: int = 1024, height: int = 1024) -> str:
    model = model or DEFAULT_MODEL
    output_path = output_path or os.path.expanduser("~/generated_image.jpg")

    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "width": width,
        "height": height,
        "steps": 4,
        "n": 1,
        "response_format": "b64_json",
    })

    result = subprocess.run(
        [
            "curl", "-s", "-X", "POST", API_URL,
            "-H", f"Authorization: Bearer {API_KEY}",
            "-H", "Content-Type: application/json",
            "-d", payload,
        ],
        capture_output=True, text=True, timeout=120,
    )

    if result.returncode != 0:
        raise RuntimeError(f"curl failed: {result.stderr}")

    data = json.loads(result.stdout)
    if "error" in data:
        raise RuntimeError(json.dumps(data["error"]))

    import base64
    from PIL import Image
    import io

    b64 = data["data"][0]["b64_json"]
    raw = base64.b64decode(b64)

    # Always convert to JPEG for smaller files and universal compatibility
    img = Image.open(io.BytesIO(raw)).convert("RGB")
    if not output_path.lower().endswith((".jpg", ".jpeg")):
        output_path = os.path.splitext(output_path)[0] + ".jpg"
    img.save(output_path, "JPEG", quality=92)

    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: together-img.py 'prompt' [output_path] [model] [width] [height]")
        sys.exit(1)

    prompt = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else ""
    model = sys.argv[3] if len(sys.argv) > 3 else ""
    w = int(sys.argv[4]) if len(sys.argv) > 4 else 1024
    h = int(sys.argv[5]) if len(sys.argv) > 5 else 1024

    path = generate(prompt, output, model, w, h)
    print(path)
