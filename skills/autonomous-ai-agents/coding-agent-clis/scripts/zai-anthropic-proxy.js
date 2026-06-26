#!/usr/bin/env node
// Anthropic-to-Z.AI proxy: translates Anthropic Messages API → Z.AI OpenAI-compatible API
// Claude Code → localhost:18765 → api.z.ai/api/coding/paas/v4/chat/completions
//
// Usage: ANTHROPIC_API_KEY=<inference_key> node zai-anthropic-proxy.js
// Then set ANTHROPIC_BASE_URL=http://127.0.0.1:18765 in ~/.claude/settings.json

const http = require('http');
const https = require('https');

const PORT = 18765;
const ZAI_HOST = 'api.z.ai';
const ZAI_CHAT_PATH = '/api/coding/paas/v4/chat/completions';
const ZAI_MODELS_PATH = '/api/v1/models';
const API_KEY = process.env.ANTHROPIC_API_KEY || '';

function translateAnthropicToOpenAI(body) {
  const messages = [];
  if (body.system) {
    if (typeof body.system === 'string') {
      messages.push({ role: 'system', content: body.system });
    } else if (Array.isArray(body.system)) {
      messages.push({ role: 'system', content: body.system.map(b => b.text || '').join('\n') });
    }
  }
  for (const msg of (body.messages || [])) {
    let content = '';
    if (typeof msg.content === 'string') {
      content = msg.content;
    } else if (Array.isArray(msg.content)) {
      content = msg.content
        .filter(b => b.type === 'text')
        .map(b => b.text)
        .join('\n');
    }
    messages.push({ role: msg.role, content });
  }
  return {
    model: body.model || 'glm-5.2',
    messages,
    max_tokens: body.max_tokens || 4096,
    temperature: body.temperature ?? 0.7,
    stream: false,
  };
}

function translateOpenAIToAnthropic(openaiResp, model) {
  const choice = openaiResp.choices?.[0];
  const msg = choice?.message;
  const text = msg?.content || '';
  const reasoning = msg?.reasoning_content || '';

  return {
    id: openaiResp.id || `msg_${Date.now()}`,
    type: 'message',
    role: 'assistant',
    content: [{ type: 'text', text: reasoning ? `${reasoning}\n\n${text}` : text }],
    model: model,
    stop_reason: choice?.finish_reason === 'length' ? 'max_tokens' : 'end_turn',
    stop_sequence: null,
    usage: {
      input_tokens: openaiResp.usage?.prompt_tokens || 0,
      output_tokens: openaiResp.usage?.completion_tokens || 0,
    },
  };
}

const server = http.createServer((req, res) => {
  let body = '';
  req.on('data', chunk => body += chunk);
  req.on('end', () => {
    // Models endpoint — forward directly to Z.AI Anthropic-compatible path
    if (req.url.startsWith('/v1/models')) {
      const opts = {
        hostname: ZAI_HOST, port: 443,
        path: ZAI_MODELS_PATH + (req.url.includes('?') ? req.url.slice(req.url.indexOf('?')) : ''),
        method: 'GET',
        headers: { 'x-api-key': API_KEY, 'anthropic-version': '2023-06-01' },
      };
      const proxyReq = https.request(opts, proxyRes => {
        let d = ''; proxyRes.on('data', c => d += c);
        proxyRes.on('end', () => {
          res.writeHead(proxyRes.statusCode, { 'content-type': 'application/json' });
          res.end(d);
        });
      });
      proxyReq.on('error', err => { res.writeHead(502); res.end(JSON.stringify({ error: err.message })); });
      proxyReq.end();
      return;
    }

    // Messages endpoint — translate Anthropic → OpenAI → Z.AI
    if (req.url.startsWith('/v1/messages') && req.method === 'POST') {
      let parsed;
      try { parsed = JSON.parse(body); } catch { res.writeHead(400); res.end('{"error":"bad json"}'); return; }

      const openaiBody = translateAnthropicToOpenAI(parsed);
      const payload = JSON.stringify(openaiBody);

      const opts = {
        hostname: ZAI_HOST, port: 443,
        path: ZAI_CHAT_PATH,
        method: 'POST',
        headers: {
          'content-type': 'application/json',
          'Authorization': `Bearer ${API_KEY}`,
          'content-length': Buffer.byteLength(payload),
        },
      };

      const proxyReq = https.request(opts, proxyRes => {
        let d = ''; proxyRes.on('data', c => d += c);
        proxyRes.on('end', () => {
          try {
            const openaiResp = JSON.parse(d);
            if (openaiResp.error) {
              res.writeHead(proxyRes.statusCode, { 'content-type': 'application/json' });
              res.end(JSON.stringify({ type: 'error', error: { type: 'api_error', message: openaiResp.error.message || openaiResp.error } }));
              return;
            }
            const anthropicResp = translateOpenAIToAnthropic(openaiResp, parsed.model || 'glm-5.2');
            res.writeHead(200, { 'content-type': 'application/json' });
            res.end(JSON.stringify(anthropicResp));
          } catch (e) {
            res.writeHead(502, { 'content-type': 'application/json' });
            res.end(JSON.stringify({ type: 'error', error: { type: 'proxy_error', message: e.message } }));
          }
        });
      });
      proxyReq.on('error', err => { res.writeHead(502); res.end(JSON.stringify({ error: err.message })); });
      proxyReq.write(payload);
      proxyReq.end();
      return;
    }

    res.writeHead(404); res.end('{"error":"not found"}');
  });
});

server.listen(PORT, '127.0.0.1', () => {
  console.log(`Anthropic→Z.AI proxy on http://127.0.0.1:${PORT}`);
  console.log(`Models → https://${ZAI_HOST}${ZAI_MODELS_PATH}`);
  console.log(`Messages → https://${ZAI_HOST}${ZAI_CHAT_PATH} (translated)`);
});
