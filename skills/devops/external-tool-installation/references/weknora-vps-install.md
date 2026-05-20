# WeKnora VPS Install (2026-05-16)

Tencent's open-source RAG knowledge framework. Docker Compose stack.

## Install Path
- Repo: `/home/ubuntu/weknora/`
- Frontend: `http://localhost:8089` (nginx proxy inside container, mapped from :80)
- API: `http://localhost:8088` (Go app, mapped from :8080)
- Compose: `sudo docker compose up -d` from `/home/ubuntu/weknora/`

## Port Conflicts
Defaults (80, 8080) conflicted with Caddy. Changed in `.env`:
- `APP_PORT=8088` (was 8080)
- `FRONTEND_PORT=8089` (was 80)

## Caddy Reverse Proxy
Added to `/etc/caddy/Caddyfile`:
```
http://43.167.176.156:8090 {
    reverse_proxy localhost:8089
}
```
Did NOT use domain-based entry (`weknora.humangood.ai`) because:
- Domain-based entry triggers Caddy auto-HTTPS → tries to bind :443
- Port 443 is already taken by `/go/bin/main` (Cloudflare Tunnel or similar)
- Fallback: IP-based routing on dedicated port

## Containers (5)
- `WeKnora-app` — Go backend API (:8080 internally, :8088 host)
- `WeKnora-frontend` — Vue.js SPA (:80 internally, :8089 host)
- `WeKnora-postgres` — ParadeDB (pgvector extension)
- `WeKnora-redis` — Redis 7 alpine
- `WeKnora-docreader` — Python document parsing (uv, gRPC :50051)

## Optional Profiles
Added via `--profile`:
- `full` — all features
- `neo4j` — knowledge graph
- `minio` — object storage
- `langfuse` — tracing/observability

## First-Time Setup
Visiting `http://localhost:8089` shows setup wizard: LLM provider config, embedding model selection, etc.

## Restart Behavior
Compose uses `restart: unless-stopped` per service. Docker daemon auto-starts on boot via systemd, so containers survive reboots.
