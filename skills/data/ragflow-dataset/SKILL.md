---
name: ragflow-dataset
description: "RAGFlow dataset management — create/list/inspect/delete datasets, upload/list/parse documents, and search/retrieve chunks. Backed by cloud.ragflow.io."
version: "1.2"
created: "2026-05-14"
requires:
  env:
    - RAGFLOW_API_URL
    - RAGFLOW_API_KEY
---

# RAGFlow Dataset Management

Manages datasets on RAGFlow cloud (`https://cloud.ragflow.io`).  
Use the bundled Python scripts in `scripts/`.

## Active Datasets (5)

| Dataset | ID | Content |
|---------|-----|---------|
| **wiki** | `36beca164f6011f19e18a1f44b6b7545` | Wiki knowledge base (30 .md files) |
| **wolf-trading-docs** | `3dcfae744f6011f1807f8fd47dde3e8d` | Trading refs (spread playbook, API notes) |
| **agent-ready** | `39909b484f6011f19e18a1f44b6b7545` | Agent Ready code + templates + docs |
| **hermes-identity** | `387a32a04f6011f19e18a1f44b6b7545` | Agent SOUL.md, AGENTS.md, personality files |
| **wolf-trading** | `53f318c24f5f11f1afb7375ddf940ad2` | Wolf trading data (legacy) |

## Environment

These must be set (already in `/home/ubuntu/.hermes/.env`):
- `RAGFLOW_API_URL=https://cloud.ragflow.io`
- `RAGFLOW_API_KEY=ragflow-F7uKNRboa_N6t5DH3P13JFO-VMOUJJ7sSrfrle7LImk`

## Scripts Location

```
~/.hermes/skills/ragflow/scripts/
```

## Available Commands

### Base (official RAGFlow scripts)
```bash
# List all datasets
python3 datasets.py list --json

# Create a dataset
python3 create_dataset.py "Dataset Name" --description "Description" --json

# Upload a document to a dataset
python3 upload.py DATASET_ID /path/to/file.pdf --json

# List documents in a dataset
python3 list_documents.py DATASET_ID --json

# Start parsing documents
python3 parse.py DATASET_ID DOC_ID1 [DOC_ID2 ...] --json

# Check parse status
python3 parse_status.py DATASET_ID --json

# Search/retrieve chunks
python3 search.py "your query" --json
python3 search.py "your query" DATASET_ID --json

# List configured models
python3 list_models.py --json

# Delete a dataset
python3 datasets.py delete DATASET_ID
```

### Env Wrapper (run.py)

The official RAGFlow scripts need `RAGFLOW_API_URL` and `RAGFLOW_API_KEY` in the
environment. Instead of exporting manually, use `run.py` which loads them from
`~/.hermes/.env` automatically:

```bash
cd ~/.hermes/skills/ragflow/scripts
python3 run.py datasets.py list --json
python3 run.py search.py "your query" DATASET_ID --json
python3 run.py parse_status.py DATASET_ID --json
python3 run.py upload.py DATASET_ID /path/to/file
```

Run `python3 run.py` with no args to list available scripts.

### Dataset Status Monitor

One command checks all 5 datasets in a single table:

```bash
cd ~/.hermes/skills/ragflow/scripts
python3 datasets_status.py                    # table view
python3 datasets_status.py --json             # raw JSON
```

No env vars needed — auto-loads credentials from ~/.hermes/.env.

### RAGFlow Client Library (shared)

```python
from ragflow_client import RAGFlowClient, WIKI_ID, WOLF_TRADING_DOCS_ID, AGENT_READY_ID

client = RAGFlowClient()
chunks = client.search("vertical spread small account", dataset_ids=[WOLF_TRADING_DOCS_ID, WIKI_ID])
context = client.format_prompt(chunks)  # → markdown block for LLM prompt
qa_context = client.format_qa(chunks)   # → light format for inline Q&A
```

Convenience methods: `search_wiki()`, `search_trading_docs()`, `search_agent_ready()`, `search_all()`.
All return `[]` on error (timeout, bad JSON, network) — never raises.

### Agent Integrations

**Wolf Enhancer** — enriches scan results with trading context:
```bash
python3 wolf_ragflow_enhancer.py --scan /path/to/wolf_scan.json
python3 wolf_ragflow_enhancer.py --scan /path/to/wolf_scan.json --json
python3 wolf_ragflow_enhancer.py --scan /path/to/wolf_scan.json --attach-digest
```

**Sherlock Integrator** — pre-search context + investigation archival:
```bash
python3 sherlock_ragflow.py pre "vertical spread small account"
python3 sherlock_ragflow.py upload /tmp/report.md "Deep Dive Title"
python3 sherlock_ragflow.py search "past investigation finnhub"
```

**Agent Ready Q&A** — answers about the Agent Ready codebase:
```bash
python3 agent_ready_ragflow.py "how does the scanner work?"
python3 agent_ready_ragflow.py "what payment methods?" --json
python3 agent_ready_ragflow.py --topic scanner    # predefined topic queries
python3 agent_ready_ragflow.py --topic pricing
```

**HAL Startup** — session initialization context:
```bash
python3 hal_startup_ragflow.py                           # auto: recent topics
python3 hal_startup_ragflow.py --topic "vertical spread"  # specific topic
```

### Agent RAGFlow Integration Pattern

See `references/agent-integration-pattern.md` for the standard pattern
to connect any Hermes agent to RAGFlow for context retrieval, signal
enrichment, or Q&A over its knowledge base.

## Workflow

1. Create a dataset
2. Upload documents (PDF, txt, markdown, etc.)
3. Start parsing (RAGFlow chunks + embeds the documents)
4. Search for relevant chunks
5. Use results as context for Wolf, Sherlock, or any other agent

To enhance Wolf signals with RAGFlow context:
```bash
python3 wolf_ragflow_enhancer.py --scan ~/.hermes/skills/trading/wolf-trading-agent/output/wolf_scan_YYYY-MM-DD.json
```

For Agent Ready Q&A from the Flask app:
```python
from ragflow_client import RAGFlowClient
client = RAGFlowClient()
chunks = client.search("how to deploy", dataset_ids=["39909b48...", "36beca16..."])
context = client.format_qa(chunks)
```

## Dataset Status

All 5 datasets uploaded and queued for parsing. Quick check:

```bash
cd ~/.hermes/skills/ragflow/scripts && python3 datasets_status.py
```

Parsing via **BAAI/bge-small-en-v1.5** embeddings, **naive** chunk method with GraphRAG light.

## Notes

- All base scripts from official RAGFlow GitHub repo: `infiniflow/ragflow-skills`
- Pass `--help` on any script for full options
- Delete operations require explicit user confirmation
- Parsing async — use `datasets_status.py` or `parse_status.py` to check
- Client library auto-loads API credentials from env or hardcoded defaults
- `search()` never raises — returns `[]` on any failure
- `run.py` loads env from `~/.hermes/.env` so you don't need to export RAGFLOW_ vars
- See `references/agent-integration-pattern.md` for the standard integration pattern
