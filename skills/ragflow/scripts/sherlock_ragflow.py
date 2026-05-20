#!/usr/bin/env python3
"""
Sherlock RAGFlow Integrator — prime investigations with known context.

Two entry points:
1. PRE-search (recommended from within investigations):
   - Queries wiki + hermes-identity for existing knowledge on a topic
   - Returns formatted markdown for injection into the investigation prompt
   - Prevents re-researching what's already documented

2. POST-search (report archival):
   - Uploads completed investigation reports to the wiki dataset
   - Makes past investigations searchable for future Sherlocks

Usage:
    python3 sherlock_ragflow.py pre "vertical spread small account"
    python3 sherlock_ragflow.py pre "Agent Ready deployment" --json

    python3 sherlock_ragflow.py upload /tmp/sherlock_report.md "Deep Dive: Finnhub API"
    python3 sherlock_ragflow.py search "past investigation finnhub"
"""

import argparse
import json
import sys
import os
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from ragflow_client import RAGFlowClient, WIKI_ID, HERMES_IDENTITY_ID


def pre_search_context(query: str, top_k: int = 5, json_output: bool = False) -> str:
    """Search wiki + hermes-identity for relevant existing knowledge.

    Returns formatted context for injection into an investigation prompt.
    """
    client = RAGFlowClient()

    wiki_chunks = client.search(query, dataset_ids=[WIKI_ID],
                                 top_k=top_k, threshold=0.15, timeout=20)
    identity_chunks = client.search(query, dataset_ids=[HERMES_IDENTITY_ID],
                                     top_k=2, threshold=0.1, timeout=20)

    all_chunks = wiki_chunks + identity_chunks

    if json_output:
        print(json.dumps(all_chunks, indent=2, default=str))
        return ""

    # Deduplicate
    seen = set()
    unique = []
    for c in all_chunks:
        fp = (c.get("content") or "").strip()[:80]
        if fp and fp not in seen:
            seen.add(fp)
            unique.append(c)

    context = RAGFlowClient.format_prompt(unique, max_chars=4000)

    if not context:
        print("🔍 No existing RAGFlow context found for this topic.")
        print("   This is a green-field investigation — document findings when done.")
        return ""

    print(f"🔍 Found {len(unique)} relevant chunks from {len(wiki_chunks)} wiki + "
          f"{len(identity_chunks)} identity results\n")
    print(context)
    return context


def upload_report(report_path: str, title: str | None = None) -> bool:
    """Upload a report file to the wiki dataset for future retrieval."""
    if not os.path.exists(report_path):
        print(f"❌ Report not found: {report_path}", file=sys.stderr)
        return False

    fsize = os.path.getsize(report_path)
    if fsize == 0:
        print(f"❌ Report is empty: {report_path}", file=sys.stderr)
        return False

    try:
        import subprocess
        env = os.environ.copy()
        env["RAGFLOW_API_URL"] = os.environ.get("RAGFLOW_API_URL",
            "https://cloud.ragflow.io")
        env["RAGFLOW_API_KEY"] = os.environ.get("RAGFLOW_API_KEY",
            "ragflow-F7uKNRboa_N6t5DH3P13JFO-VMOUJJ7sSrfrle7LImk")

        result = subprocess.run(
            [sys.executable, os.path.join(SCRIPT_DIR, "upload.py"),
             WIKI_ID, report_path, "--json"],
            capture_output=True, text=True, timeout=30,
            env=env, cwd=SCRIPT_DIR,
        )

        if result.returncode == 0:
            print(f"✅ Report uploaded to wiki dataset: {report_path}")
            if title:
                print(f"   Title: {title}")
            print(f"   Size: {fsize:,} bytes")
            print(f"   It will be searchable after RAGFlow parses it.")
            return True
        else:
            stderr = result.stderr.strip()
            print(f"❌ Upload failed (exit {result.returncode})", file=sys.stderr)
            if stderr:
                print(f"   Error: {stderr}", file=sys.stderr)
            return False

    except Exception as e:
        print(f"❌ Upload error: {e}", file=sys.stderr)
        return False


def search_investigations(query: str, top_k: int = 5, json_output: bool = False) -> None:
    """CLI-friendly search across datasets."""
    client = RAGFlowClient()
    chunks = client.search_all(query, top_k=top_k, timeout=20)

    if not chunks:
        print("📭 No results found. The dataset may still be parsing.")
        return

    if json_output:
        print(json.dumps(chunks, indent=2, default=str))
        return

    print(f"📚 Found {len(chunks)} result(s):\n")
    for i, c in enumerate(chunks, 1):
        doc = c.get("document_name", "?")
        ds = c.get("dataset_name", "")
        sim = c.get("similarity", 0)
        content = (c.get("content") or "").strip()[:300]
        source = f" ({ds})" if ds else ""
        print(f"[{i}] {doc}{source} sim: {sim:.0%}")
        print(f"    {content}...\n")


def main():
    parser = argparse.ArgumentParser(
        description="Sherlock RAGFlow — prime investigations with known context"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # Pre-search
    p_pre = sub.add_parser("pre", help="Search for existing knowledge before investigating")
    p_pre.add_argument("query", help="What to research")
    p_pre.add_argument("--top-k", type=int, default=5)
    p_pre.add_argument("--json", action="store_true")

    # Upload
    p_up = sub.add_parser("upload", help="Upload a completed report to the wiki")
    p_up.add_argument("report", help="Path to the report file (.md)")
    p_up.add_argument("title", nargs="?", help="Optional display title")

    # Search
    p_srch = sub.add_parser("search", help="Search past investigations and wiki entries")
    p_srch.add_argument("query", help="Search query")
    p_srch.add_argument("--top-k", type=int, default=5)
    p_srch.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if args.command == "pre":
        pre_search_context(args.query, top_k=args.top_k, json_output=args.json)

    elif args.command == "upload":
        upload_report(args.report, title=args.title)

    elif args.command == "search":
        search_investigations(args.query, top_k=args.top_k, json_output=args.json)


if __name__ == "__main__":
    main()
