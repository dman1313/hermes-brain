#!/usr/bin/env bash
# hermes-brain restore — rebuild Hermes from backup (requires manual secret restoration)
set -euo pipefail

HERMES_HOME="$HOME/.hermes"
BRAIN="$HOME/hermes-brain"

echo "=== Hermes Brain Restore ==="
echo "WARNING: This overwrites skills, profiles, and config in $HERMES_HOME"
echo "Secrets (.env, tokens, keys) must be restored manually afterward."
echo ""
read -p "Continue? [y/N] " confirm
[[ "$confirm" =~ ^[Yy]$ ]] || exit 0

# 1. Skills
echo "[1/5] Restoring skills..."
rm -rf "$HERMES_HOME/skills"
cp -r "$BRAIN/skills" "$HERMES_HOME/skills"

# 2. Profiles
echo "[2/5] Restoring profiles..."
rm -rf "$HERMES_HOME/profiles"
cp -r "$BRAIN/profiles" "$HERMES_HOME/profiles"

# 3. Config (merge — don't overwrite if secrets exist)
echo "[3/5] Restoring config..."
if [ -f "$HERMES_HOME/config.yaml" ]; then
    echo "  config.yaml exists — not overwriting. Review $BRAIN/config/config.yaml.redacted manually."
else
    cp "$BRAIN/config/config.yaml.redacted" "$HERMES_HOME/config.yaml"
    echo "  config.yaml restored (REDACTED — add your secrets)"
fi

# 4. Identity
echo "[4/5] Restoring identity..."
for f in SOUL.md AGENTS.md MEMORY.md; do
    if [ -f "$BRAIN/$f" ]; then
        cp "$BRAIN/$f" "$HERMES_HOME/$f"
        echo "  $f"
    fi
done

# 5. Webhook subscriptions
echo "[5/5] Restoring webhooks..."
if [ -f "$BRAIN/config/webhook_subscriptions.json" ]; then
    cp "$BRAIN/config/webhook_subscriptions.json" "$HERMES_HOME/webhook_subscriptions.json"
    echo "  webhook_subscriptions.json"
fi

echo ""
echo "=== Restore complete ==="
echo "NEXT STEPS:"
echo "  1. Restore ~/.hermes/.env with your API keys"
echo "  2. Restore ~/.hermes/ai-trader-token.txt"
echo "  3. Run: hermes gateway restart"
echo "  4. Run: hermes webhook list   (verify webhooks)"
