#!/usr/bin/env python3
"""
HAL Startup Context Enhancer — loads RAGFlow wiki context at session start.

Called during main session initialization. Searches the wiki dataset for
the most recent/relevant entries based on the current project or topic.

Two modes:
1. Auto: No args — searches for "recent updates" and "active projects" 
   to give HAL a pulse on what's been happening.
2. Topic: With --topic — searches wiki for a specific topic.

Usage:
    python3 hal_startup_ragflow.py
    python3 hal_startup_ragflow.py --topic "Agent Ready deployment"
    python3 hal_startup_ragflow.py --topic "vertical spread" --json
"""

import argparse
import json
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from ragflow_client import RAGFlowClient, WIKI_ID


DEFAULT_TOPICS = [
    "recent updates active projects",
    "current tasks priorities",
    "trading market context",
    "agent readiness certification",
    "wiki index schema structure",
]


def get_startup_context(top_k_per_topic: int = 3) -> list[dict]:
    """Gather RAGFlow context for session startup.

    Runs several broad queries to give HAL a pulse on what's current.
    """
    client = RAGFlowClient()
    all_chunks = []
    seen = set()

    for topic in DEFAULT_TOPICS:
        chunks = client.search(topic, dataset_ids=[WIKI_ID], top_k=top_k_per_topic, threshold=0.1)
        for c in chunks:
            content = (c.get("content") or "").strip()[:100]
            if content and content not in seen:
                seen.add(content)
                all_chunks.append(c)

    return all_chunks[:10]


def main():
    parser = argparse.ArgumentParser(description="HAL RAGFlow startup context")
    parser.add_argument("--topic", help="Specific topic to search")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    client = RAGFlowClient()

    if args.topic:
        chunks = client.search(
            args.topic, dataset_ids=[WIKI_ID], top_k=8, threshold=0.15
        )
    else:
        chunks = get_startup_context()

    if not chunks:
        msg = (
            "📚 **RAGFlow Context:** No wiki content available yet. "
            "The wiki dataset is still being parsed by RAGFlow. "
            "Check back later with `python3 hal_startup_ragflow.py`"
        )
        if args.json:
            print(json.dumps({"status": "unavailable", "message": msg}))
        else:
            print(msg)
        return

    ctx = RAGFlowClient.format_prompt(chunks, max_chars=4000)
    if args.json:
        print(json.dumps({"chunks": chunks, "context": ctx}, indent=2, default=str))
    else:
        print(ctx)


if __name__ == "__main__":
    main()
