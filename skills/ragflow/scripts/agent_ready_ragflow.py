#!/usr/bin/env python3
"""
Agent Ready RAGFlow Q&A — search the codebase for context.

Searches the 'agent-ready' RAGFlow dataset for relevant context to
answer user questions about the Agent Ready service.

Usage:
    python3 agent_ready_ragflow.py "how does the scanner work?"
    python3 agent_ready_ragflow.py "what payment methods are supported?" --json
    python3 agent_ready_ragflow.py --topic scanner
"""

import argparse
import json
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from ragflow_client import RAGFlowClient, AGENT_READY_ID, WIKI_ID


TOPIC_QUERIES = {
    "scanner": ["scanner certification checker", "scoring site analysis", "checker.py"],
    "payment": ["payment stripe coinbase", "checkout billing checkout"],
    "middleware": ["content negotiation middleware", "agent headers detection LLM"],
    "fix": ["fix guide remediation manual", "fix.html improvement steps"],
    "pricing": ["pricing certification plan pricing"],
    "deploy": ["deployment zeabur docker vps", "config setup configuration"],
}


def search_codebase(question: str, top_k: int = 5,
                     include_wiki: bool = False) -> list[dict]:
    """Search Agent Ready + optionally wiki for relevant context."""
    client = RAGFlowClient()
    dataset_ids = [AGENT_READY_ID]
    if include_wiki:
        dataset_ids.append(WIKI_ID)
    return client.search(question, dataset_ids=dataset_ids,
                          top_k=top_k, threshold=0.15, timeout=20)


def get_context(question: str, include_wiki: bool = False) -> str:
    """Get formatted Q&A context for a question about Agent Ready."""
    chunks = search_codebase(question, top_k=6, include_wiki=include_wiki)
    if not chunks:
        return (
            "I searched the Agent Ready codebase and couldn't find relevant context. "
            "The dataset may still be processing — check back later or rephrase your question."
        )
    return RAGFlowClient.format_qa(chunks)


def topic_mode(topic: str, top_k: int = 5, json_output: bool = False) -> None:
    """Run multiple queries for a predefined topic and merge results."""
    queries = TOPIC_QUERIES.get(topic)
    if not queries:
        available = ", ".join(sorted(TOPIC_QUERIES.keys()))
        print(f"❌ Unknown topic: '{topic}'. Available: {available}",
              file=sys.stderr)
        sys.exit(1)

    client = RAGFlowClient()
    all_chunks = []
    seen = set()

    for q in queries:
        chunks = client.search(q, dataset_ids=[AGENT_READY_ID],
                                top_k=3, threshold=0.15, timeout=15)
        for c in chunks:
            fp = (c.get("content") or "").strip()[:80]
            if fp and fp not in seen:
                seen.add(fp)
                all_chunks.append(c)

    if json_output:
        print(json.dumps(all_chunks[:top_k], indent=2, default=str))
    else:
        if not all_chunks:
            print(f"📭 No results found for topic '{topic}'. Dataset may still be parsing.")
            return
        print(f"📚 {len(all_chunks)} results for topic '{topic}':\n")
        print(RAGFlowClient.format_prompt(all_chunks[:top_k], max_chars=5000))


def main():
    parser = argparse.ArgumentParser(
        description="Agent Ready RAGFlow — search the codebase for context"
    )
    parser.add_argument("question", nargs="?",
                        help="Question about Agent Ready")
    parser.add_argument("--json", action="store_true",
                        help="Raw JSON output (chunks)")
    parser.add_argument("--include-wiki", action="store_true",
                        help="Also search the wiki for related context")
    parser.add_argument("--top-k", type=int, default=5,
                        help="Max results")
    parser.add_argument("--topic",
                        choices=sorted(TOPIC_QUERIES.keys()),
                        help="Predefined topic query")

    args = parser.parse_args()

    if args.topic:
        topic_mode(args.topic, top_k=args.top_k, json_output=args.json)
        return

    if args.question:
        if args.json:
            chunks = search_codebase(args.question, top_k=args.top_k,
                                      include_wiki=args.include_wiki)
            print(json.dumps(chunks, indent=2, default=str))
        else:
            ctx = get_context(args.question, include_wiki=args.include_wiki)
            print(ctx)
        return

    parser.print_help()
    print()
    print("Examples:")
    print("  python3 agent_ready_ragflow.py \"how does the scanner work?\"")
    print("  python3 agent_ready_ragflow.py --topic pricing")
    print("  python3 agent_ready_ragflow.py \"deploy to zeabur\" --include-wiki")
    print()
    print("Available topics: scanner, payment, middleware, fix, pricing, deploy")


if __name__ == "__main__":
    main()
