#!/bin/bash
# Wolf Trading Agent wrapper — requires GNEWS_API_KEY in environment, then runs the scan
# Set it: export GNEWS_API_KEY="your_key_here"
export GNEWS_API_KEY="${GNEWS_API_KEY:?Set GNEWS_API_KEY environment variable}"
cd "$HOME/.hermes/skills/trading/wolf-trading-agent/scripts"
exec python3 wolf_scan.py "$@"
