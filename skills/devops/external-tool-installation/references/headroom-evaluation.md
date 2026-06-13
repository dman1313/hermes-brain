# Headroom Evaluation (2026-06-14)

**Repo:** https://github.com/chopratejas/headroom
**Package:** `headroom-ai` (PyPI + npm)
**What it does:** Context compression layer for AI agents — compresses tool outputs, logs, RAG chunks, files, and conversation history before they hit the LLM. Claims 60-95% token reduction with preserved accuracy.

## Install Notes

- Python package with Rust extensions (maturin build backend)
- System Rust 1.75 was too old — needed rustup upgrade to 1.96
- Required: `uv venv .venv`, `uv pip install maturin`, then `uv pip install -e ".[dev]" --no-build-isolation`
- Installed to `/home/ubuntu/headroom` with venv at `.venv`

## Key Features

- **Modes:** library (`compress(messages)`), proxy (`headroom proxy`), agent wrapper (`headroom wrap claude`), MCP server
- **Algorithms:** SmartCrusher (JSON), CodeCompressor (AST), Kompress-base (text, HuggingFace model)
- **CacheAligner:** stabilizes prefixes so provider KV caches hit
- **CCR (reversible):** originals cached locally, LLM can retrieve on demand
- **Cross-agent memory:** shared store across Claude, Codex, Gemini
- **`headroom learn`:** mines failed sessions, writes corrections to CLAUDE.md/AGENTS.md
- **Explicit OpenClaw support** in compatibility matrix

## Assessment for Our Setup

**Verdict: Marginal. Keep installed, don't wire in globally.**

Reasons:
1. Our biggest cost driver is model routing (cheap models for light tasks), not context size
2. Hermes already has context management — skills, memory compression, caveman mode
3. The proxy adds latency (extra hop per call)
4. Short messages don't compress (test: 352 tokens → 352 tokens, 0% savings)
5. Designed more for Claude Code/Codex coding workflows than Telegram bot orchestration

**Where it would help:**
- Long coding sessions with huge context (10K+ tokens per turn)
- As MCP server for specific heavy-payload workflows
- When hitting context window limits on specific models

**Recommendation:** Use `headroom wrap` for specific heavy agents if needed, not as global pipeline layer.
