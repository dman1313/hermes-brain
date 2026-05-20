#!/usr/bin/env python3
"""
RAGFlow Client Library — shared helper for Wolf, Sherlock, Agent Ready.

Provides a clean Python API to search RAGFlow datasets and format results
for injection into agent prompts, digests, or Q&A flows.

Usage:
    from ragflow_client import RAGFlowClient

    client = RAGFlowClient()
    results = client.search("best vertical spreads for small accounts", 
                            dataset_ids=["wolf-trading-docs-ID", "wiki-ID"])
    print(client.format_prompt(results))
"""

import os
import json
import subprocess
import sys
from typing import Any

# Path to the RAGFlow scripts directory
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
SEARCH_SCRIPT = os.path.join(SCRIPTS_DIR, "search.py")

# Dataset IDs (from RAGFlow cloud)
WOLF_TRADING_DOCS_ID = "3dcfae744f6011f1807f8fd47dde3e8d"
WIKI_ID = "36beca164f6011f19e18a1f44b6b7545"
AGENT_READY_ID = "39909b484f6011f19e18a1f44b6b7545"
HERMES_IDENTITY_ID = "387a32a04f6011f19e18a1f44b6b7545"
WOLF_TRADING_DATA_ID = "53f318c24f5f11f1afb7375ddf940ad2"

DATASET_NAMES = {
    WIKI_ID: "wiki",
    WOLF_TRADING_DOCS_ID: "wolf-trading-docs",
    AGENT_READY_ID: "agent-ready",
    HERMES_IDENTITY_ID: "hermes-identity",
    WOLF_TRADING_DATA_ID: "wolf-trading-data",
}

# Default environment — loaded from .env or env vars
DEFAULT_URL = os.environ.get("RAGFLOW_API_URL", "https://cloud.ragflow.io")
DEFAULT_KEY = os.environ.get("RAGFLOW_API_KEY",
    "ragflow-F7uKNRboa_N6t5DH3P13JFO-VMOUJJ7sSrfrle7LImk")


def _env_lookup(api_key: str | None, base_url: str | None) -> tuple[str, str]:
    """Resolve API credentials, trying explicit args then env then defaults."""
    return base_url or os.environ.get("RAGFLOW_API_URL") or DEFAULT_URL, \
           api_key or os.environ.get("RAGFLOW_API_KEY") or DEFAULT_KEY


class RAGFlowClient:
    """Simple Python wrapper around RAGFlow search scripts."""

    def __init__(self, base_url: str | None = None, api_key: str | None = None):
        self.base_url, self.api_key = _env_lookup(api_key, base_url)
        self._env = os.environ.copy()
        self._env["RAGFLOW_API_URL"] = self.base_url
        self._env["RAGFLOW_API_KEY"] = self.api_key

    def search(
        self,
        query: str,
        *,
        dataset_ids: list[str] | None = None,
        top_k: int = 5,
        threshold: float = 0.2,
        timeout: int = 30,
    ) -> list[dict[str, Any]]:
        """
        Search RAGFlow datasets.

        Args:
            query: The search query (required)
            dataset_ids: List of dataset IDs to search. If None, searches all datasets.
            top_k: Max results per dataset
            threshold: Similarity threshold 0-1
            timeout: Request timeout in seconds

        Returns:
            List of chunk dicts with keys: document_name, dataset_id,
            similarity, content
        """
        if not query or not query.strip():
            return []

        query = query.strip()

        # Build argv for the search.py script
        argv = [query]

        if not dataset_ids:
            # No dataset_id args — search.py needs one positional or --dataset-ids
            # Pass an empty string as placeholder; the script handles it gracefully
            argv.append("")

        argv.extend([
            "--json",
            "--top-k", str(top_k),
            "--threshold", str(threshold),
        ])

        if dataset_ids:
            argv.extend(["--dataset-ids", ",".join(dataset_ids)])

        try:
            result = subprocess.run(
                [sys.executable, SEARCH_SCRIPT] + argv,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=self._env,
                cwd=SCRIPTS_DIR,
            )
            if result.returncode != 0:
                stderr = result.stderr.strip()
                if stderr:
                    print(f"[RAGFlow] Search error: {stderr}", file=sys.stderr)
                return []

            data = json.loads(result.stdout)
            chunks = data.get("chunks", [])

            # Annotate with dataset display names
            for c in chunks:
                ds_id = c.get("dataset_id") or c.get("kb_id", "")
                c["dataset_name"] = DATASET_NAMES.get(ds_id, ds_id[:16])

            return chunks

        except subprocess.TimeoutExpired:
            print(f"[RAGFlow] Search timed out ({timeout}s) for: {query[:60]}...",
                  file=sys.stderr)
            return []
        except (json.JSONDecodeError, subprocess.SubprocessError) as e:
            print(f"[RAGFlow] Search failed: {e}", file=sys.stderr)
            return []

    def search_wiki(self, query: str, *, top_k: int = 5, timeout: int = 30) -> list[dict[str, Any]]:
        """Search the wiki dataset only."""
        return self.search(query, dataset_ids=[WIKI_ID], top_k=top_k, timeout=timeout)

    def search_trading_docs(self, query: str, *, top_k: int = 5, timeout: int = 30) -> list[dict[str, Any]]:
        """Search the Wolf trading docs dataset."""
        return self.search(query, dataset_ids=[WOLF_TRADING_DOCS_ID], top_k=top_k, timeout=timeout)

    def search_agent_ready(self, query: str, *, top_k: int = 5, timeout: int = 30) -> list[dict[str, Any]]:
        """Search the Agent Ready codebase dataset."""
        return self.search(query, dataset_ids=[AGENT_READY_ID], top_k=top_k, timeout=timeout)

    def search_all(self, query: str, *, top_k: int = 3, timeout: int = 30) -> list[dict[str, Any]]:
        """Search all knowledge datasets."""
        return self.search(
            query,
            dataset_ids=[WIKI_ID, WOLF_TRADING_DOCS_ID, AGENT_READY_ID, HERMES_IDENTITY_ID],
            top_k=top_k,
            timeout=timeout,
        )

    @staticmethod
    def format_prompt(chunks: list[dict[str, Any]], *, max_chars: int = 4000) -> str:
        """Format RAGFlow chunks for injection into an LLM prompt context.

        Produces a compact markdown block prefixed with a heading so the
        consuming agent knows these are RAGFlow-retrieved facts.
        """
        if not chunks:
            return ""

        lines = ["## 📚 RAGFlow Context", ""]
        char_count = 0
        total = len(chunks)

        for i, chunk in enumerate(chunks, 1):
            doc = chunk.get("document_name") or "unknown"
            ds_name = chunk.get("dataset_name", "")
            sim = chunk.get("similarity")
            sim_str = f" sim:{sim:.0%}" if isinstance(sim, (int, float)) else ""
            content = (chunk.get("content") or "").strip()

            if not content:
                continue

            source_tag = f"`{doc}`"
            if ds_name:
                source_tag += f" ({ds_name})"

            entry = (
                f"**{i}:** {source_tag}{sim_str}\n"
                + content[:600]
                + ("..." if len(content) > 600 else "")
                + "\n"
            )

            if char_count + len(entry) > max_chars:
                remaining = total - i + 1
                if remaining > 0:
                    lines.append(f"*(+{remaining} more result{'s' if remaining > 1 else ''} truncated)*")
                break

            lines.append(entry)
            char_count += len(entry)

        lines.append("---")
        return "\n".join(lines)

    @staticmethod
    def format_qa(chunks: list[dict[str, Any]]) -> str:
        """Format chunks for Q&A — just the content with source labels.

        Lighter version for Agent Ready's inline Q&A responses.
        """
        if not chunks:
            return "I don't have enough context to answer that confidently."

        parts = []
        for i, chunk in enumerate(chunks, 1):
            doc = chunk.get("document_name") or f"source {i}"
            ds_name = chunk.get("dataset_name", "")
            content = (chunk.get("content") or "").strip()
            if content:
                label = f"{doc} ({ds_name})" if ds_name else doc
                parts.append(f"[{label}]\n{content[:800]}")

        return "\n\n".join(parts)


def quick_test():
    """Run a quick search to verify the client works."""
    client = RAGFlowClient()
    results = client.search("vertical spread small account",
                            dataset_ids=[WOLF_TRADING_DOCS_ID], top_k=3, timeout=10)
    print(f"Found {len(results)} results")
    for r in results:
        sim = r.get("similarity", 0)
        con = (r.get("content") or "")[:80]
        print(f"  - [{r.get('document_name','?')}] sim={sim:.2f}: {con}...")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] in ("--help", "-h"):
        print(__doc__)
    else:
        print("ℹ️ RAGFlow Client Library — import this module, don't run it directly.\n")
        print("Quick test:\n")
        quick_test()
