#!/bin/bash
# Smoke test: Claude Code routed through Kimi coding API.
# Usage: bash kimi-claude-smoke-test.sh
# Reads KIMI_API_KEY from ~/.hermes/.env, sets ANTHROPIC env vars, runs claude -p.
set -e
KIMI_KEY=$(grep '^KIMI_API_KEY=' ~/.hermes/.env | sed 's/KIMI_API_KEY=//')
if [ -z "$KIMI_KEY" ]; then
  echo "ERROR: KIMI_API_KEY not found in ~/.hermes/.env"
  exit 1
fi
export ANTHROPIC_API_KEY="${KIMI_KEY}"
export ANTHROPIC_BASE_URL="https://api.kimi.com/coding"
echo "Testing Kimi through Claude Code..."
cd /tmp && claude -p "Say hello in exactly 3 words." --max-turns 1 --output-format json 2>/dev/null | python3 -c "
import sys, json
data = json.load(sys.stdin)
if data.get('subtype') == 'success':
    print(f'OK — {data[\"result\"]} (${data[\"total_cost_usd\"]:.2f}, {data[\"duration_ms\"]}ms)')
else:
    print(f'FAIL — subtype={data.get(\"subtype\")}: {data.get(\"result\",\"\")[:100]}')
"
