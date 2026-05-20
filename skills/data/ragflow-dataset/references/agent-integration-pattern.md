# Agent RAGFlow Integration Pattern

Standard pattern for connecting any Hermes agent to RAGFlow for context
retrieval, signal enrichment, or Q&A over its knowledge base.

## Overview

```
┌──────────────┐     ┌────────────────────┐     ┌───────────────┐
│ Hermes Agent │────▶│ RAGFlowClient      │────▶│ cloud.ragflow │
│ (Wolf,       │     │ ragflow_client.py  │     │ .io API       │
│  Sherlock,   │     │                    │     │               │
│  Agent Ready)│     │ .search()          │◀────│ search        │
│              │     │ .format_prompt()   │     │ endpoint      │
│              │     │ .format_qa()       │     │               │
└──────────────┘     └────────────────────┘     └───────────────┘
```

## Quick Start (any agent)

```python
from path.to.ragflow_client import RAGFlowClient

client = RAGFlowClient()
chunks = client.search("your query", dataset_ids=["dataset-id-1"])
context = client.format_prompt(chunks)  # Markdown for LLM prompts
qa_context = client.format_qa(chunks)   # Plain for inline responses
```

## Step-by-step

### 1. Import

```python
import sys, os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(SCRIPT_DIR, "..", "ragflow", "scripts"))
from ragflow_client import RAGFlowClient
```

The `ragflow_client.py` lives at `~/.hermes/skills/ragflow/scripts/` and
the data/ragflow-dataset skill manages it. Import relative to your own
script's location.

### 2. Choose dataset(s)

Available dataset IDs (exported as module constants):

| Constant | Dataset | Use Case |
|----------|---------|----------|
| `WIKI_ID` | wiki | General knowledge, procedures, concepts |
| `WOLF_TRADING_DOCS_ID` | wolf-trading-docs | Trading refs, playbooks, API notes |
| `AGENT_READY_ID` | agent-ready | Agent Ready code + templates |
| `HERMES_IDENTITY_ID` | hermes-identity | Agent identities, SOUL.md |
| `WOLF_TRADING_DATA_ID` | wolf-trading | Trading data (legacy) |

Convenience methods:
```python
client.search_wiki(query)          # Wiki only
client.search_trading_docs(query)  # Trading docs only
client.search_agent_ready(query)   # Agent Ready codebase only
client.search_all(query)           # All datasets
```

### 3. Search

```python
chunks = client.search(
    query="vertical spread small account",
    dataset_ids=[WOLF_TRADING_DOCS_ID, WIKI_ID],
    top_k=5,           # Max results
    threshold=0.2,     # Similarity floor (0-1)
    timeout=30,        # Seconds
)
```

Returns list of dicts with keys:
- `document_name` — source file name
- `dataset_name` — human-readable dataset label
- `similarity` — relevance score (0-1)
- `content` — the chunk text
- `chunk_id` — RAGFlow chunk ID
- `document_id` — RAGFlow document ID
- `dataset_id` — dataset UUID

Empty query returns `[]` immediately.

### 4. Format for LLM consumption

**For prompts** (markdown with headings and relevance annotations):
```python
context = client.format_prompt(chunks, max_chars=4000)
```

Output shape:
```
## 📚 RAGFlow Context

**1:** `notes.md` (wiki) sim:85%
content...

**2:** `playbook.md` (wolf-trading-docs) sim:72%
more content...

---
```

**For inline Q&A** (lighter format):
```python
qa = client.format_qa(chunks)
```

Output shape:
```
[notes.md (wiki)]
content...

[playbook.md (wolf-trading-docs)]
more content...
```

### 5. Timeouts and error handling

`search()` never raises — returns `[]` on any failure (timeout, bad JSON,
network error). Check stderr for `[RAGFlow]` prefixed diagnostics:

```python
chunks = client.search(...)
if not chunks:
    print(f"⚠️ RAGFlow search returned nothing for '{query}'")
```

The client handles:
- Timeout → `[RAGFlow] Search timed out` on stderr
- Bad JSON → `[RAGFlow] Search failed` on stderr
- Empty query → immediate `[]` return, no API call
- Non-200 response → `[RAGFlow] Search error` on stderr

## Pattern: Signal Enhancer

Enrich existing agent output with RAGFlow context:

```
Agent output ──▶ extract key entities ──▶ search RAGFlow ──▶ attach context
```

Example (from Wolf):
```python
def build_ragflow_context(client, signal):
    ticker = signal["ticker"]
    queries = [f"{ticker} trading strategy", f"{ticker} options"]
    all_chunks = []
    for q in queries:
        chunks = client.search(q, dataset_ids=[DOCS_ID, WIKI_ID], top_k=2)
        all_chunks.extend(chunks)
    # Deduplicate
    seen = set()
    unique = [c for c in all_chunks if (c.get("content") or "")[:100] not in seen and not seen.add((c.get("content") or "")[:100])]
    return client.format_prompt(unique[:5], max_chars=3000)
```

## Pattern: Pre-search Prime

Research heavily from RAGFlow before doing external research:

```python
# Before: don't re-research what's already documented
existing = client.search_wiki(topic, top_k=8)
if existing:
    print(f"Found {len(existing)} existing chunks — skipping external research")
    return client.format_prompt(existing)
# Do external research and document findings back to wiki
```

## Pattern: Codebase Q&A

Answer questions by searching the codebase dataset:

```python
def answer_question(question):
    client = RAGFlowClient()
    chunks = client.search_agent_ready(question)
    return client.format_qa(chunks)
```

The `agent_ready_ragflow.py` module wraps this with topic presets
for common areas (scanner, pricing, deployment).

## Pitfalls

- **Chunks may be empty while parsing is queued** — RAGFlow cloud processes
  documents asynchronously. After upload, check `parse_status.py` and wait
  until `DONE > 0` and `RUNNING == 0`. Initial upload to a busy cloud
  instance can queue >200 tasks.
- **threshold is strict** — the default 0.2 similarity floor can miss
  relevant results on a small dataset. Lower to 0.1 for broad retrieval,
  raise to 0.3+ for precision. Tune per use case.
- **dataset_ids must be keyword** — `client.search(query, [id])` silently
  passes a list as the second positional arg which maps to `dataset_id`.
  Always use keyword: `client.search(query, dataset_ids=[id])`.
- **format_prompt has a max_chars cap** — setting too low truncates
  silently. The truncation message shows how many were cut.
- **format_qa returns a fallback string, not ""** — when no chunks found,
  it returns "I don't have enough context..." instead of empty string.
  Check `len(chunks) > 0` before calling format_qa if you need to
  distinguish "no results" from "here's the fallback."
