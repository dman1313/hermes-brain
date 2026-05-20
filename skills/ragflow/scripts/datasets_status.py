#!/usr/bin/env python3
"""
RAGFlow dataset status monitor — check parse progress across all 5 datasets.

Shows a quick table of which datasets are done, still parsing, or failed.

Usage:
    python3 datasets_status.py               # Table view
    python3 datasets_status.py --json        # Raw JSON
"""

import argparse
import json
import subprocess
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARSE_STATUS = os.path.join(SCRIPT_DIR, "parse_status.py")

DATASETS = [
    ("wiki", "36beca164f6011f19e18a1f44b6b7545", "General wiki (30 .md files)"),
    ("wolf-trading-docs", "3dcfae744f6011f1807f8fd47dde3e8d", "Trading refs (3 docs)"),
    ("agent-ready", "39909b484f6011f19e18a1f44b6b7545", "Agent Ready codebase (10 files)"),
    ("hermes-identity", "387a32a04f6011f19e18a1f44b6b7545", "Agent identities (4 files)"),
    ("wolf-trading", "53f318c24f5f11f1afb7375ddf940ad2", "Trading data (1 file, legacy)"),
]

ENV = os.environ.copy()
ENV.setdefault("RAGFLOW_API_URL", "https://cloud.ragflow.io")
ENV.setdefault("RAGFLOW_API_KEY",
    "ragflow-F7uKNRboa_N6t5DH3P13JFO-VMOUJJ7sSrfrle7LImk")


def check_dataset(name: str, ds_id: str, desc: str,
                  timeout: int = 15) -> dict:
    """Check parse status for one dataset."""
    try:
        result = subprocess.run(
            [sys.executable, PARSE_STATUS, ds_id, "--json"],
            capture_output=True, text=True, timeout=timeout,
            env=ENV, cwd=SCRIPT_DIR,
        )
        if result.returncode != 0:
            return {"name": name, "id": ds_id, "status": "error",
                    "error": result.stderr.strip() or "unknown"}

        data = json.loads(result.stdout)
        summary = data.get("summary", {})
        total = summary.get("total", 0)
        done = summary.get("DONE", 0)
        running = summary.get("RUNNING", 0)
        fail = summary.get("FAIL", 0)
        unstart = summary.get("UNSTART", 0)

        if total == 0:
            status = "no-docs"
        elif done == total:
            status = "done"
        elif fail > 0:
            status = "partial-fail"
        elif running > 0 or unstart > 0:
            status = "parsing"
        else:
            status = "unknown"

        return {
            "name": name,
            "id": ds_id,
            "description": desc,
            "status": status,
            "total": total,
            "done": done,
            "running": running,
            "fail": fail,
            "unstart": unstart,
            "progress_pct": round(done / total * 100, 1) if total > 0 else 0,
        }

    except subprocess.TimeoutExpired:
        return {"name": name, "id": ds_id, "status": "timeout"}
    except (json.JSONDecodeError, subprocess.SubprocessError) as e:
        return {"name": name, "id": ds_id, "status": "error", "error": str(e)}


def format_table(results: list[dict]) -> str:
    """Format results as a compact table."""
    lines = ["📊 RAGFlow Dataset Parse Status", "=" * 50, ""]

    status_icons = {
        "done": "✅",
        "parsing": "⏳",
        "no-docs": "📭",
        "error": "❌",
        "timeout": "⏰",
        "partial-fail": "⚠️",
        "unknown": "❓",
    }

    header = f"{'Dataset':<20} {'Status':<12} {'Progress':>8}  {'Files':<20}"
    sep = "-" * len(header)
    lines.append(header)
    lines.append(sep)

    all_done = True
    for r in results:
        icon = status_icons.get(r["status"], "❓")
        progress = f"{r['progress_pct']}%" if r["total"] > 0 else "-"
        files = f"{r['done']}/{r['total']}" if r["total"] > 0 else "0"
        if r["status"] == "error":
            files = f"ERR: {r.get('error', '?')[:25]}"
        elif r["status"] == "timeout":
            files = "timeout"

        lines.append(
            f"{r['name']:<20} {icon + ' ' + r['status']:<12} {progress:>8}  {files:<20}"
        )
        if r["status"] != "done":
            all_done = False

    lines.append("")
    if all_done:
        lines.append("✅ All datasets fully parsed and searchable.")
    else:
        lines.append("⏳ Some datasets still parsing. Search results may be incomplete.")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Check RAGFlow dataset parse progress")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--timeout", type=int, default=15, help="Per-dataset timeout")
    args = parser.parse_args()

    results = []
    for name, ds_id, desc in DATASETS:
        print(f"  Checking {name}...", end=" ", flush=True)
        r = check_dataset(name, ds_id, desc, timeout=args.timeout)
        results.append(r)
        print(r["status"])

    if args.json:
        print(json.dumps(results, indent=2, default=str))
    else:
        print()
        print(format_table(results))


if __name__ == "__main__":
    main()
