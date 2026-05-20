#!/usr/bin/env bash
# hermes-brain backup — snapshot durable Hermes state (no secrets)
set -euo pipefail

HERMES_HOME="$HOME/.hermes"
BRAIN="$HOME/hermes-brain"
TIMESTAMP=$(date +%Y-%m-%d-%H%M)

echo "=== Hermes Brain Backup — $TIMESTAMP ==="

# 1. Skills
echo "[1/6] Copying skills..."
rm -rf "$BRAIN/skills"
cp -r "$HERMES_HOME/skills" "$BRAIN/skills"
find "$BRAIN/skills" -type f \( -name '.env' -o -name '*token*' -o -name '*secret*' -o -name '*credential*' \) -delete
echo "  $(find "$BRAIN/skills" -name 'SKILL.md' | wc -l) skills"

# 2. Profiles (no .env)
echo "[2/6] Copying profiles..."
rm -rf "$BRAIN/profiles"
cp -r "$HERMES_HOME/profiles" "$BRAIN/profiles"
find "$BRAIN/profiles" -name '.env' -delete
echo "  $(ls "$BRAIN/profiles" | wc -l) profiles"

# 3. Config (redacted)
echo "[3/6] Redacting config..."
mkdir -p "$BRAIN/config"
sed -E 's/(key|secret|token|password|api_key)[:=].+/\\1: [REDACTED]/gi' \
    "$HERMES_HOME/config.yaml" > "$BRAIN/config/config.yaml.redacted"
echo "  config.yaml redacted"

# 4. Identity files
echo "[4/6] Copying identity..."
for f in SOUL.md AGENTS.md MEMORY.md; do
    if [ -f "$HERMES_HOME/$f" ]; then
        cp "$HERMES_HOME/$f" "$BRAIN/$f"
        echo "  $f"
    fi
done

# 5. Webhook subscriptions
echo "[5/6] Copying webhook subscriptions..."
if [ -f "$HERMES_HOME/webhook_subscriptions.json" ]; then
    cp "$HERMES_HOME/webhook_subscriptions.json" "$BRAIN/config/webhook_subscriptions.json"
    echo "  webhook_subscriptions.json"
fi

# 6. Memory export
echo "[6/6] Exporting memory..."
cp "$HERMES_HOME/MEMORY.md" "$BRAIN/MEMORY.md" 2>/dev/null || true
# Also snapshot the daily memory files
if [ -d "$HERMES_HOME/memory" ]; then
    rm -rf "$BRAIN/memory"
    cp -r "$HERMES_HOME/memory" "$BRAIN/memory"
    echo "  $(ls "$BRAIN/memory" | wc -l) daily memory files"
fi

echo ""
echo "=== Backup complete ==="
echo "Run: cd $BRAIN && git add -A && git commit -m 'backup: $TIMESTAMP' && git push"
