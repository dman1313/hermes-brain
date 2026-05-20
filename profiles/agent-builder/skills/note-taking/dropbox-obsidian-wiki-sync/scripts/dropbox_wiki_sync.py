#!/usr/bin/env python3
"""Run wiki dropbox sync script and report exit code + output.

Use as a Hermes cron job script (model=null, script=dropbox_wiki_sync.py)
so the sync actually executes instead of producing "(No response generated)."
"""
import subprocess, sys

result = subprocess.run(
    ["/home/ubuntu/.local/bin/dropbox-sync.sh"],
    capture_output=True, text=True, timeout=120
)

print(f"exit_code: {result.returncode}")
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr[:500])
