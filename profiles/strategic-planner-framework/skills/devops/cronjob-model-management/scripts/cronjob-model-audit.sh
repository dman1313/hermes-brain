#!/bin/bash

# Cronjob Model Management Helper Script
# Usage: ./cronjob-model-audit.sh [list|update|verify]

set -e

ACTION=${1:-list}
MODELS_CACHE="$HOME/.hermes/models_dev_cache.json"

echo "=== Hermes Cronjob Model Management ==="
echo "Action: $ACTION"
echo ""

case "$ACTION" in
    "list")
        echo "1. Current Cronjob Model Assignments:"
        echo "======================================"
        cronjob(action='list') 2>/dev/null || echo "Error: Unable to list cronjobs. Check Hermes connection."
        echo ""
        
        echo "2. Available Models by Provider:"
        echo "================================"
        if [[ -f "$MODELS_CACHE" ]]; then
            echo "Kimi-for-coding models:"
            jq -r '.kimi-for-coding.models | keys[]' "$MODELS_CACHE" 2>/dev/null || echo "  Unable to read Kimi models"
            
            echo ""
            echo "ZAI GLM models:"
            jq -r '.zai.models | keys[] | select(test("glm"))' "$MODELS_CACHE" 2>/dev/null || echo "  Unable to read ZAI GLM models"
        else
            echo "Error: Models cache file not found at $MODELS_CACHE"
        fi
        ;;
        
    "verify")
        echo "Verifying cronjob model assignments..."
        echo "===================================="
        
        # Get cronjob list and check for issues
        cronjob(action='list') 2>/dev/null > /tmp/cronjobs.txt
        
        echo "Checking for potential issues:"
        echo ""
        
        # Check for GLM models that should be Kimi
        echo "Cronjobs using GLM models (consider updating to Kimi):"
        grep -E "glm-[0-9]" /tmp/cronjobs.txt | grep -v "null" || echo "  None found"
        echo ""
        
        # Check for null models (should be scripts only)
        echo "Cronjobs with no model (should be system scripts only):"
        grep "null.*null" /tmp/cronjobs.txt || echo "  None found"
        echo ""
        
        # Check for potential issues
        echo "Potential issues to review:"
        echo "- Verify agent health tasks use k2p5"
        echo "- Verify system sync tasks have null model"
        echo "- Verify utility tasks use glm-5.1"
        
        rm -f /tmp/cronjobs.txt
        ;;
        
    "help"|*)
        echo "Usage: $0 [list|update|verify|help]"
        echo ""
        echo "Commands:"
        echo "  list    - Show current cronjob assignments and available models"
        echo "  verify  - Check for potential model assignment issues"  
        echo "  help    - Show this help message"
        echo ""
        echo "This script helps manage cronjob model assignments in Hermes Agent."
        echo "For actual updates, use the cronjob tool with exact model names."
        ;;
esac

echo ""
echo "Done."