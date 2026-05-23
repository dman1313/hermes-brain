# FreeLLMAPI VPS Install Notes

Repo: https://github.com/tashfeenahmed/freellmapi
Type: Node.js 20+ / TypeScript (not Docker)
Installed: /home/ubuntu/freellmapi (May 2026)

## Quick Install

```bash
git clone https://github.com/tashfeenahmed/freellmapi.git
cd freellmapi
npm install
cp .env.example .env
echo "ENCRYPTION_KEY=$(node -e \"console.log(require('crypto').randomBytes(32).toString('hex'))\")" >> .env
```

## Port Conflicts

Default port is 3001. On this VPS, Hermes Office uses :3001 so FreeLLMAPI was shifted to :3002. Change `PORT=3002` in `.env`.

## Production Build + Systemd

Don't run `npm run dev` long-term — it spawns Vite dev server separately. Build for production:

```bash
npm run build
# Serves API + dashboard from single port via server/dist/index.js
```

Systemd unit (`/etc/systemd/system/freellmapi.service`):

```ini
[Unit]
Description=FreeLLMAPI - OpenAI-compatible proxy for free LLM providers
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/freellmapi
Environment=NODE_ENV=production
Environment=PORT=3002
Environment=PATH=/home/ubuntu/.local/bin:/home/ubuntu/.hermes/node/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=/home/ubuntu/.hermes/node/bin/node /home/ubuntu/freellmapi/server/dist/index.js
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

After install: `sudo systemctl daemon-reload && sudo systemctl enable freellmapi && sudo systemctl start freellmapi`

## Caddy Reverse Proxy

IP-based entry (not domain — avoids port 443 conflicts):

```
# /etc/caddy/Caddyfile
http://<public-ip>:7458 {
    reverse_proxy localhost:3002
}
```

Then `sudo systemctl reload caddy`.

## Adding API Keys Programmatically

The Keys page has a REST API at `POST /api/keys`:

```bash
curl -s -X POST http://localhost:3002/api/keys \
  -H "Content-Type: application/json" \
  -d '{"platform":"google","key":"<key>","label":"Dwayne"}'
```

Valid platforms: google, groq, cerebras, sambanova, nvidia, mistral, openrouter, github, cohere, cloudflare, zhipu, ollama, kilo, pollinations, llm7

## Retrieving the Unified API Key

SQLite query (sqlite3 CLI not available — use Python):

```python
import sqlite3
db = sqlite3.connect("/home/ubuntu/freellmapi/server/data/freeapi.db")
row = db.execute("SELECT value FROM settings WHERE key='unified_api_key'").fetchone()
print(row[0])
```

Format: `freellmapi-<48 hex chars>`. Use as Bearer token.

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
| Zhipu (bigmodel) | https://open.bigmodel.cn |
| NVIDIA NIM | https://build.nvidia.com |
| Ollama Cloud | https://ollama.com |

## Smoke Test

```bash
curl -s http://localhost:3002/v1/chat/completions \
  -H "Authorization: Bearer freellmapi-<key>" \
  -H "Content-Type: application/json" \
  -d '{"model":"auto","messages":[{"role":"user","content":"hi"}],"max_tokens":20}'
```

Check `_routed_via` in response to see which provider served the request.
