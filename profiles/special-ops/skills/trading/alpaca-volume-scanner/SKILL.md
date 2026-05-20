---
name: alpaca-volume-scanner
description: Build and run an Alpaca Markets paper trading bot with volume spike detection, modular strategy system, Telegram alerts, and cron-ready architecture.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [trading, alpaca, volume-scanning, paper-trading, stock-market, telegram-alerts]
    related_skills: [cronjob-model-management, telegram-group-management]
---

# Alpaca Volume Scanner

Build a modular Alpaca Markets trading bot. Paper-trade only (no real money) by default. Plugs into Hermes cronjobs and Telegram for alerts.

## Project Structure

```
~/alpaca-bot/
├── .env.example        # Template with all keys
├── .env                # Your actual keys (gitignored by default)
├── config.py           # API key loader, paper/live detection
├── data.py             # Market data fetcher (Alpaca StockBarsRequest)
├── trading.py          # Paper trade executor, position/order helpers, trade log
├── notify.py           # Telegram alert formatter + sender
├── commands.py         # Hermes/CLI commands: /status, /trades, /scan
├── run.py              # Main scan loop — cron-ready entry point
├── strategies/
│   ├── __init__.py     # Abstract base Strategy class
│   └── volume_spike.py # Volume spike strategy (concrete implementation)
├── trade_log.json      # Auto-generated trade history
└── last_scan.json      # Auto-generated last scan output
```

## Setup

```bash
# Install deps
pip install alpaca-py pandas python-dotenv

# Edit .env with your keys
cd ~/alpaca-bot
# PAPER API key from https://alpaca.markets/ -> Paper Trading -> API Keys
# ALPACA_API_KEY=pk_...
# ALPACA_SECRET_KEY=...
```

### Config Notes

- `config.py` defaults to paper mode automatically if no API key is set or URL contains `paper-api`
- Telegram is optional — bot runs silently without it
- `.env` is NOT committed; `.env.example` is the template

## Volume Spike Strategy

The default strategy (`strategies/volume_spike.py`):

- **Entry**: Current bar volume ≥ 2x rolling 20-bar average → BUY
- **Exit**: Hold for 5 bars then SELL (time-based take-profit)
- **Position sizing**: 5% of available cash per trade
- **No double-buy**: Skips symbols already held or with pending orders

## Usage

### One-off scan
```bash
cd ~/alpaca-bot && python3 run.py

# Dry run (analyze but don't trade):
cd ~/alpaca-bot && python3 run.py --dry-run
```

### Telegram commands (via commands.py)
```bash
python3 commands.py status    # Show account + positions
python3 commands.py trades    # Show last 20 trades
python3 commands.py scan      # Force a scan now
python3 commands.py help      # List all commands
```

### Hermes cron job (set up after keys are configured)
```
Cron prompt: Run the volume scanner. Run `cd ~/alpaca-bot && python3 run.py` and summarize any trades placed.
Schedule: Every 30 minutes during market hours (e.g., 30 9-16 * * 1-5)
```

## Adding a New Strategy

1. Create `strategies/your_strategy.py`
2. Subclass `Strategy` from `strategies/__init__.py`
3. Implement `generate_signal(symbol, bars) -> dict | None`

Signal dict format:
```python
{
    "action": "buy" | "sell" | "hold",
    "symbol": symbol,
    "qty": int or None,  # None lets the engine calculate
    "price": float,
    "reason": "readable explanation",
    "volume_ratio": float,  # optional, for logging
}
```

## Architecture Notes

### Modular source architecture
The bot is designed to layer in additional data sources (Reddit, Twitter/X, News):
- Each source is an independent scanner module
- A scoring engine blends signals: volume(40%) + sentiment(30%) + momentum(20%) + news(10%)
- Currently only the volume scanner is active

### Pitfalls

- **Free tier data limits**: The free paper account does NOT include minute-level bar data. StockBarsRequest with TimeFrame.Minute returns 403: subscription does not permit querying recent SIP data. Workaround: use StockLatestQuoteRequest for real-time prices and bid/ask. Daily bars may work; test before building strategy around intraday data.
### Pitfalls

- **Alpaca SDK relative imports**: `config.py`, `data.py`, `trading.py`, and `notify.py` use flat imports (`from config import ...`), NOT relative imports. If restructuring as a package, change to relative imports.
- **Market hours**: Alpaca data API returns empty bars outside market hours. `run.py` handles this gracefully but produces no signals.
- **Alpaca-py vs alpaca-trade-api**: This project uses `alpaca-py` (the newer v2 SDK), NOT the deprecated `alpaca-trade-api` package.
- **Day trade limits**: Paper accounts are not subject to PDT rules, but switching to live requires attention to pattern day trader rules for accounts under $25K.
- **Telegram alert failures**: If Telegram is unconfigured, `notify.py` silently returns `{"sent": false, "reason": "Telegram not configured"}` — no crash.
- **Free tier data limits**: `StockBarsRequest` with minute-level timeframe returns 403 `"subscription does not permit querying recent SIP data"`. The free tier only supports quotes (`StockLatestQuoteRequest`) and daily bars. For volume analysis, use `StockLatestTradeRequest` or daily bars.
- **Options trading**: Paper accounts get Options Level 3. Single-leg option orders work via `MarketOrderRequest` with option contract symbols (e.g., `AAPL260508P00275000`). Naked call selling is blocked (403 — "account not eligible to trade uncovered option contracts"). Multi-leg/spread orders NOT supported via API. Option contracts looked up with `GetOptionContractsRequest` filtering by underlying, expiration, type, and strike range.
- **get_account() params**: The `TradingClient.get_account()` in alpaca-py takes no arguments (unlike some examples showing `GetAccountRequest` — removed in current version).
- **Order lookup**: Use `GetOrdersRequest(limit=N, status='all')` not `client.get_orders(status='all')` — the method signature changed in current alpaca-py.

### Verification

```bash
cd ~/alpaca-bot && python3 -c "
from config import get_config
from data import fetch_bars
from strategies import Strategy
from strategies.volume_spike import VolumeSpikeStrategy
from trading import get_account_info, get_positions
from notify import send_alert
from run import run_scan
print('All imports OK')
"
```
