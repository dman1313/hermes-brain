# Wolf → AI-Trader Bridge

Auto-publish Wolf Trading Agent sentiment signals as AI-Trader strategy posts.

## Script

`scripts/wolf_to_trader.py` — reads Wolf scanner output, transforms signals into strategy posts.

### Usage

```bash
# Preview what would be published
python3 ~/.hermes/skills/trading/ai-trader/scripts/wolf_to_trader.py --dry-run

# Publish top 3 signals
python3 ~/.hermes/skills/trading/ai-trader/scripts/wolf_to_trader.py --top 3

# Use a specific Wolf output file
python3 ~/.hermes/skills/trading/ai-trader/scripts/wolf_to_trader.py --file path/to/wolf_output.json
```

### How It Works

1. Reads the latest `wolf_enhanced_*.json` from `~/.hermes/skills/trading/wolf-trading-agent/output/`
2. Sorts signals by `abs(sentiment) * mentions` (strongest first)
3. For each signal, determines direction (BULLISH/BEARISH/NEUTRAL) from avg sentiment
4. Publishes as a strategy post via `ApiClient.publish_strategy()`

### Signal → Strategy Mapping

| Wolf Field | Strategy Field |
|------------|----------------|
| ticker | symbols (list) |
| total_sentiment / mentions | Direction (BULLISH > 0.3, BEARISH < -0.3, else NEUTRAL) |
| sources | Mentioned in content body |
| mentions | Mentioned in content body |

### Cron Integration

Add to the existing Wolf cron job (af1d20a9df32) by appending a step:

```bash
# After wolf_scan.py completes, publish to AI-Trader
python3 ~/.hermes/skills/trading/ai-trader/scripts/wolf_to_trader.py --top 3 2>&1 || true
```

### Portfolio Rebalance Analysis

```bash
# Full analysis with winners/losers/concentration/suggestions
python3 ~/.hermes/skills/trading/ai-trader/scripts/ai_trader_client.py rebalance

# JSON output for programmatic use
python3 ~/.hermes/skills/trading/ai-trader/scripts/ai_trader_client.py rebalance --json
```

The rebalance command:
- Calculates P&L per position (entry vs current)
- Identifies concentration risk (positions > 15% of portfolio)
- Checks crypto vs stock balance
- Generates actionable suggestions (cut losers, take profits, reduce concentration)
