# FreeLLMAPI — VPS Install Notes

## What It Is
OpenAI-compatible proxy aggregating free-tier API keys from 11+ providers (Google, Groq, Cerebras, SambaNova, Mistral, OpenRouter, GitHub Models, Cloudflare, Cohere, Zhipu, NVIDIA, Ollama Cloud). Single `/v1/chat/completions` endpoint with automatic fallover, per-key rate tracking, and encrypted key storage.

Repo: `https://github.com/tashfeenahmed/freellmapi` (~4K stars)
Language: TypeScript (Node.js 20+, React + Vite dashboard)

## Install Commands

```bash
git clone https://github.com/tashfeenahmed/freellmapi.git /home/ubuntu/freellmapi
cd /home/ubuntu/freellmapi
npm install

# Generate encryption key and configure
cp .env.example .env
echo "ENCRYPTION_KEY=$(node -e "console.log(require('crypto').randomBytes(32).toString('hex'))")" >> .env
```

## Port Selection
Default port is 3001. On a VPS with Hermes Office (Claw3D), 3001 is taken. Edit `.env`:
```
PORT=3002
```

## Running
```bash
npm run dev   # server on :3002, dashboard on :5173 (Vite HMR)
```

## Adding API Keys
Keys can be added via the dashboard at `http://localhost:5173` → Keys page, OR programmatically via REST:

```bash
curl -s -X POST http://localhost:3002/api/keys \
  -H "Content-Type: application/json" \
  -d '{"platform":"google","key":"AIza...","label":"My Key"}'
```

Valid platforms: `google`, `groq`, `cerebras`, `sambanova`, `nvidia`, `mistral`, `openrouter`, `github`, `cohere`, `cloudflare`, `zhipu`, `ollama`, `kilo`, `pollinations`, `llm7`

## Getting the Unified API Key
Stored in SQLite at `server/data/freeapi.db` in the `settings` table:
```python
import sqlite3
db = sqlite3.connect("server/data/freeapi.db")
key = db.execute("SELECT value FROM settings WHERE key='unified_api_key'").fetchone()[0]
# Format: freellmapi-<48 hex chars>
```

## Provider Signup URLs
| Provider | Signup URL |
|----------|-----------|
| Google Gemini | https://aistudio.google.com/apikey |
| Groq | https://console.groq.com/keys |
| Cerebras | https://cloud.cerebras.ai |
| SambaNova | https://cloud.sambanova.ai |
| Mistral | https://console.mistral.ai |
| OpenRouter | https://openrouter.ai/keys |
| GitHub Models | https://github.com/marketplace/models |
| Cloudflare AI | https://dash.cloudflare.com/ai/workers-ai |
| Cohere | https://dashboard.cohere.com/api-keys |
| Zhipu | https://open.bigmodel.cn |
| NVIDIA NIM | https://build.nvidia.com |
| Ollama Cloud | https://ollama.com |

## Usage
```python
from openai import OpenAI
client = OpenAI(
    base_url="http://localhost:3002/v1",
    api_key="freellmapi-<unified-key>",
)
resp = client.chat.completions.create(
    model="auto",  # let router pick; or specify e.g. "gemini-2.5-flash"
    messages=[{"role": "user", "content": "Hello"}],
)
print(resp.choices[0].message.content)
print("Routed via:", resp.headers.get("x-routed-via"))
```

## Noted During Install (May 23, 2026)
- Port 3001 was occupied by Hermes Office (Claw3D Next.js server) — used 3002 instead
- The `/anthropic` and `/` root paths on the Xiaomi token plan portal return 404 on curl — unrelated to FreeLLMAPI, just tested during the same session
- 12 npm audit vulnerabilities (10 moderate, 2 high) — typical for a project of this size, none blocking
