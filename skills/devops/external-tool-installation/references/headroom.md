# Headroom — Context Compression Layer

**Repo**: https://github.com/chopratejas/headroom
**Version tested**: 0.26.0 (2026-06-14)
**License**: Apache 2.0

## What it does

Compresses context (tool outputs, logs, RAG, files, conversation history) before it hits the LLM. 60-95% fewer tokens, same answers. Local-first, reversible (originals stored, LLM retrieves on demand).

## Install

```bash
# PEP 668 systems (Ubuntu 24.04+): use uv
uv pip install headroom-ai

# Or with extras
uv pip install "headroom-ai[all]"   # everything (slow — many deps)
uv pip install "headroom-ai[proxy,mcp]"  # just proxy + MCP

# Or in a venv
python3 -m venv .venv && source .venv/bin/activate
pip install headroom-ai
```

## 4 Modes

1. **Library**: `from headroom import compress` — inline in Python/TS
2. **Proxy**: `headroom proxy --port 8787` — zero code changes, any language
3. **Agent wrap**: `headroom wrap claude|codex|cursor|aider|copilot` — one command
4. **MCP server**: `headroom_compress`, `headroom_retrieve`, `headroom_stats`

## Compression Algorithms

- **SmartCrusher** — JSON/array compression (70-90%)
- **CodeCompressor** — AST-aware (Python, JS, Go, Rust, Java, C++)
- **Kompress-base** — HuggingFace model trained on agentic traces
- **Log compressor** — build logs, diffs, search results
- **CacheAligner** — stabilizes prefixes for KV cache hits
- **CCR** — reversible; originals stored locally, retrievable on demand

## API Usage

```python
from headroom import compress

messages = [
    {"role": "user", "content": "..."},
    {"role": "tool", "content": "<large JSON or log output>"},
]

result = compress(messages)
# result.tokens_before, result.tokens_after, result.tokens_saved
# result.compression_ratio (0-1), result.transforms_applied
# result.messages — the compressed messages
```

Returns a `CompressResult` object (dataclass), not a list. Access `.messages` for the compressed messages.

## Test Results (2026-06-14)

- Small JSON (20 items): 702 → 643 tokens (8.4% — minimal)
- Realistic workload (100 log lines + 50-item JSON): 5,842 → 1,666 tokens (**71.5%**)
- Compression improves significantly with larger, more repetitive inputs

## Hermes Integration Potential

- `headroom wrap claude` or MCP server mode could compress Hermes tool outputs
- `headroom learn` mines failed sessions, writes corrections to CLAUDE.md/AGENTS.md
- Cross-agent memory: shared store across Claude, Codex, Gemini
- Not yet integrated — installed at ~/headroom/ with venv

## Pitfalls

1. **`CompressResult` is not iterable** — it's a dataclass, not a list. Use `result.messages` for the compressed messages.
2. **`headroom perf` needs proxy data** — shows "No performance data" until you run `headroom proxy` and generate traffic.
3. **`[all]` extras are heavy** — install specific extras (`[proxy,mcp,ml]`) if you don't need everything.
4. **PEP 668** — `pip install` fails on Ubuntu 24.04+. Use `uv pip install` or a venv.
