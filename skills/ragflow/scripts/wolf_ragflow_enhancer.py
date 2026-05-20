#!/usr/bin/env python3
"""
Wolf RAGFlow Enhancer — enriches Wolf signals with RAGFlow context.

Called after wolf_scan.py produces its ranked signals.
For each top signal, searches wolf-trading-docs + wiki for relevant
trading context (spread playbooks, strategy notes, market knowledge)
and attaches it to the digest output.

Usage:
    python3 wolf_ragflow_enhancer.py --scan path/to/wolf_scan.json
    python3 wolf_ragflow_enhancer.py --scan path/to/wolf_scan.json --json
    python3 wolf_ragflow_enhancer.py --scan path/to/wolf_scan.json --attach-digest
"""

import argparse
import json
import sys
import os
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from ragflow_client import RAGFlowClient, WOLF_TRADING_DOCS_ID, WIKI_ID

# Output dir: resolve to the actual wolf output dir if it exists, else local
_WOLF_OUTPUT_CANDIDATE = os.path.realpath(
    os.path.join(SCRIPT_DIR, "..", "..", "trading", "wolf-trading-agent", "output")
)
WOLF_OUTPUT_DIR = _WOLF_OUTPUT_CANDIDATE if os.path.isdir(
    os.path.join(SCRIPT_DIR, "..", "..", "trading", "wolf-trading-agent")
) else SCRIPT_DIR


def load_scan(path: str) -> dict | None:
    """Load a wolf_scan JSON file with friendly error."""
    if not os.path.exists(path):
        print(f"❌ Scan file not found: {path}", file=sys.stderr)
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in scan file: {e}", file=sys.stderr)
        return None


def build_ragflow_context(client: RAGFlowClient, signal: dict) -> str:
    """Build RAGFlow context for a single signal ticker."""
    ticker = signal["ticker"]
    company = signal.get("company_name", "")

    queries = []
    if company:
        queries.append(f"{ticker} {company} trading strategy")
    queries.append(f"{ticker} stock options")
    queries.append(f"{ticker} market analysis")
    queries.append(f"vertical spread {ticker}")

    all_chunks = []
    for q in queries:
        chunks = client.search(q, dataset_ids=[WOLF_TRADING_DOCS_ID, WIKI_ID],
                                top_k=2, threshold=0.15, timeout=15)
        all_chunks.extend(chunks)

    # Deduplicate by content fingerprint
    seen = set()
    unique = []
    for c in all_chunks:
        fp = (c.get("content") or "").strip()[:120]
        if fp and fp not in seen:
            seen.add(fp)
            unique.append(c)

    return RAGFlowClient.format_prompt(unique[:5], max_chars=3000)


def enhance_signals(scan_path: str, *, json_output: bool = False,
                    attach_digest: bool = False) -> dict | None:
    """Load Wolf scan results, enhance with RAGFlow context."""
    data = load_scan(scan_path)
    if data is None:
        return None

    signals = data.get("signals", [])
    metadata = data.get("metadata", {})

    if not signals:
        print("ℹ️ No signals to enhance (empty scan).")
        return data

    client = RAGFlowClient()
    scan_time_str = metadata.get("scan_time", "")[:10]
    date_str = scan_time_str if scan_time_str else datetime.now().strftime("%Y-%m-%d")

    enhanced_signals = []
    for sig in signals:
        context = build_ragflow_context(client, sig)
        enhanced = dict(sig)
        enhanced["ragflow_context"] = context
        enhanced_signals.append(enhanced)

        if not json_output:
            ticker = sig["ticker"]
            ctx_len = len(context)
            status = "✅" if ctx_len > 50 else "⚠️"
            print(f"  {status} ${ticker}: {ctx_len} chars of context")

    # General market pulse
    general_ctx = client.search("market conditions trading", dataset_ids=[WIKI_ID],
                                 top_k=3, threshold=0.1, timeout=15)

    result = {
        "metadata": {
            **metadata,
            "enhanced_at": datetime.now().isoformat(),
            "signals_enhanced": len(enhanced_signals),
        },
        "signals": enhanced_signals,
        "ragflow_market_context": RAGFlowClient.format_prompt(
            general_ctx[:3], max_chars=2000
        ),
    }

    if attach_digest and "digest" in data:
        # Build an enriched digest by injecting context after each signal
        lines = data["digest"].split("\n")
        result["enhanced_digest"] = _attach_context_to_digest(lines, enhanced_signals)

    # Save
    os.makedirs(WOLF_OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(WOLF_OUTPUT_DIR, f"wolf_enhanced_{date_str}.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2, default=str)

    if json_output:
        print(json.dumps(result, indent=2, default=str))
    else:
        print(f"\n✅ Enhanced {len(enhanced_signals)} signals — saved to {out_path}")

    return result


def _attach_context_to_digest(digest_lines: list[str],
                               signals: list[dict]) -> str:
    """Inject brief contextual footnotes after each ticker mention."""
    ticker_map = {s["ticker"]: s["ragflow_context"] for s in signals}
    out = []

    for line in digest_lines:
        out.append(line)
        # After a ticker block (lines starting with •), inject a slim footnote
        if line.startswith("  Score:") or line.startswith("  Sentiment:"):
            # Find which ticker this belongs to by scanning up
            for prev in reversed(out[:-1]):
                if prev.startswith("• **$") and "**" in prev:
                    ticker = prev.split("**$")[1].split("**")[0]
                    ctx = ticker_map.get(ticker, "")
                    if ctx:
                        # Extract a single-line relevance note
                        for cline in ctx.split("\n"):
                            if "sim:" in cline and cline.strip():
                                out.append(f"  📚 {cline.strip()}")
                                break
                    break

    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(
        description="Enhance Wolf signals with RAGFlow trading context"
    )
    parser.add_argument("--scan", required=True,
                        help="Path to wolf_scan JSON output")
    parser.add_argument("--json", action="store_true",
                        help="Output raw JSON")
    parser.add_argument("--attach-digest", action="store_true",
                        help="Inject context footnotes into the digest")
    args = parser.parse_args()

    success = enhance_signals(args.scan, json_output=args.json,
                               attach_digest=args.attach_digest)
    sys.exit(0 if success is not None else 1)


if __name__ == "__main__":
    main()
