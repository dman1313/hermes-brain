#!/usr/bin/env python3
"""
RAGFlow env wrapper — loads credentials from .env, then runs the target script.

Usage:
    python3 run.py search.py "your query" DATASET_ID
    python3 run.py upload.py DATASET_ID /path/to/file.pdf
    python3 run.py datasets.py list --json

This handles the chore of setting RAGFLOW_API_URL and RAGFLOW_API_KEY
in the environment before calling the official RAGFlow scripts.
"""

import os
import sys
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def load_dotenv(path: str) -> dict[str, str]:
    """Minimal .env loader — no dependencies."""
    env = os.environ.copy()
    if not os.path.exists(path):
        return env
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip("\"'")
            # Set RAGFLOW_ vars unconditionally — override any old values
            if key.startswith("RAGFLOW_"):
                env[key] = value
    return env


def main():
    if len(sys.argv) < 2:
        print(__doc__.strip())
        print("\nAvailable RAGFlow scripts:")
        for f in sorted(os.listdir(SCRIPT_DIR)):
            if f.endswith(".py") and f not in ("run.py", "common.py"):
                print(f"  {f}")
        sys.exit(1)

    target = sys.argv[1]
    target_path = os.path.join(SCRIPT_DIR, target)

    if not os.path.exists(target_path):
        print(f"❌ Script not found: {target}", file=sys.stderr)
        print(f"   Looked in: {target_path}", file=sys.stderr)
        sys.exit(1)

    # Load .env from the Hermes config dir, then merge ragflow/.env on top
    env = load_dotenv(os.path.expanduser("~/.hermes/.env"))
    env2 = load_dotenv(os.path.join(SCRIPT_DIR, ".env"))
    env.update(env2)  # ragflow/.env overrides if present

    cmd = [sys.executable, target_path] + sys.argv[2:]

    try:
        proc = subprocess.run(cmd, env=env, cwd=SCRIPT_DIR)
        sys.exit(proc.returncode)
    except FileNotFoundError:
        print(f"❌ Python interpreter not found: {sys.executable}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == "__main__":
    main()
