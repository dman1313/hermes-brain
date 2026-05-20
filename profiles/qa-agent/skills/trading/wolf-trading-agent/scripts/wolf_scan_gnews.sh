#!/bin/bash
# Wolf Trading Agent wrapper — sets GNews API key then runs the scan
export GNEWS_API_KEY="ef9382a7b540143cbc64e9a0148b674f"
cd /home/ubuntu/.hermes/skills/trading/wolf-trading-agent/scripts
exec python3 wolf_scan.py "$@"
