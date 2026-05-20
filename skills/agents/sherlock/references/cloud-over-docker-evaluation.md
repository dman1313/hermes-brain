# Cloud vs Docker Evaluation Pattern

When evaluating a heavy FOSS project that requires Docker + multiple services
(DB, vector store, object storage, search engine, queue), use this decision tree:

## Step 1: Check cloud availability

The project may offer a free or paid cloud tier. This avoids:
- Docker install on the VPS (not always possible)
- 4GB+ RAM consumption per service stack
- Ongoing maintenance (upgrades, backups, restarts)

Check: README links, website, docs for cloud/saas/hosted option.

## Step 2: Check if the project has an API-first design

Many projects expose REST APIs or an MCP server that a cloud instance
provides. If the cloud API matches the self-hosted API surface, scripts
built for one work on the other with just env var changes (API_URL + API_KEY).

## Step 3: Check for existing integrations

- OpenClaw skills (clawhub.ai)
- Official MCP server
- Python/JS client libraries
- Community Docker Compose alternatives

## Step 4: When you MUST self-host

Minimum viable resources per service type:
- Full RAG + search (RAGFlow, Qdrant + API): 4 vCPU / 8GB RAM / 50GB disk
- Lightweight vector search (chromadb, sqlite-vss): 1 vCPU / 512MB RAM
- Document parsing (marker-pdf, pymupdf): 1 vCPU / 1GB RAM

If the VPS doesn't meet minimums, the cloud path is the right call.
