# Agent Ready — Standalone Flask App

Location: `/home/ubuntu/agent-ready/`

## Architecture

```
agent-ready/
├── app.py              # Flask app — all routes + content negotiation middleware
├── checker.py          # Synchronous certifier (httpx.Client, not AsyncClient)
├── requirements.txt    # flask, gunicorn, httpx, beautifulsoup4, markdownify, lxml
├── Procfile            # web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 2
├── templates/
│   └── index.html      # Landing page with embedded scanner form
└── static/
    └── styles.css      # Dark theme, green accent, agent/terminal vibe
```

## Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Landing page (hero + scanner form + pricing) |
| `/certify?url=X` | GET | Scanner UI with results rendered |
| `/api/certify?url=X` | GET | JSON API (used by badge.js + programmatic consumers) |
| `/badge.js` | GET | Embeddable JS badge (auto-certifies hostname on page load) |
| `/llms.txt` | GET | Agent site map — H1 title, blockquote summary, categorized MD links |
| `/ai.txt` | GET | Agent permissions — Allow-RAG, No-Training, Crawl-Delay directives |
| `/index.md` | GET | Markdown mirror via content negotiation |

## Content Negotiation

Uses Flask `@app.after_request` (not ASGI middleware — WSGI-compatible):
- Intercepts `Accept: text/markdown` → converts HTML → Markdown via `markdownify`
- Always adds `Vary: Accept` header
- Markdown response gets `Content-Type: text/markdown; charset=utf-8`

## JSON-LD Injection

Static `<script type="application/ld+json">` in `templates/index.html` with:
- `@context: https://schema.org`
- `@type: Organization`
- `name`, `url`, `description`

## Key Differences from System Objective (FastAPI lib)

| Aspect | System Objective lib | Agent Ready standalone |
|--------|---------------------|----------------------|
| Framework | FastAPI + ASGI | Flask + WSGI |
| Checker | `async certify_url()` | sync `certify_url()` |
| Deployment | Library (pip install) | Standalone app (gunicorn) |
| Tests | 155 pytest tests | None (manual verification) |
| Content negotiation | Pure ASGI middleware | `@app.after_request` |
| Schema injection | Dynamic module | Static `<script>` in template |

## Live Preview (without domain)

When the user wants to see it without using their production domain:
```bash
cd /home/ubuntu/agent-ready
PORT=8766 python app.py &
sudo ufw allow 8766/tcp
curl -s ifconfig.me  # get IP → http://<ip>:8766
```
