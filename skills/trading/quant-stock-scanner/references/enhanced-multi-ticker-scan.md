# Enhanced Multi-Ticker Quant Scan

Full scan combining options flow, quant scores, sentiment, and diverse spread setups.

## Workflow

### Step 1 — Options Volume Scan (alpaca_options_scan.py)

```bash
cd ~/.hermes/skills/trading/wolf-trading-agent/scripts
python3 alpaca_options_scan.py
```

Output: P/C ratio, call/put contract counts, call/put volume, call/put IV, directional bias per ticker.

### Step 2 — Categorize Tickers

Split the scan output into these groups:

**By P/C Ratio (directional bias):**
- Call-Skewed: P/C < 0.70 → bullish flow (e.g. NFLX 0.11, MU 0.27)
- Neutral: 0.70–1.30
- Put-Skewed: P/C > 1.30 → bearish/hedging flow

**By Volume (conviction):**
- High Volume: total call+put volume > 200K → where big money is (NVDA, TSLA, SPY)
- Low Volume: total < 20K → under the radar, thinner spreads

### Step 3 — Quant Scores on Top Candidates

Run quant_scan.py on the most interesting tickers from each category.
**yfinance rate-limits after 2-3 calls.** Pick the best 2-3 from:
- Highest call skew (P/C lowest)
- Highest put skew (P/C highest)
- Highest total volume

```bash
python3 ~/.hermes/skills/trading/quant-stock-scanner/scripts/quant_scan.py TICKER --score-only
```

### Step 4 — Alpaca Real-Time Prices

```bash
/usr/bin/python3 -c "
import os, time
for line in open(os.path.expanduser('~/alpaca-bot/.env')):
    line = line.strip()
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        os.environ[k.strip()] = v.strip().strip('\"')
from alpaca.data import StockHistoricalDataClient
from alpaca.data.requests import StockLatestTradeRequest
client = StockHistoricalDataClient(os.environ['ALPACA_API_KEY'], os.environ['ALPACA_SECRET_KEY'])
for t in ['NFLX','MU','MSTR']:
    snap = client.get_stock_latest_trade(StockLatestTradeRequest(symbol_or_symbols=[t]))
    print(f'{t}: \${round(snap[t].price,2)}')
    time.sleep(0.5)
"
```

### Step 5 — Sentiment via last30days

```bash
python3.12 ~/.hermes/skills/last30days/scripts/last30days.py "TICKER stock sentiment options" --json
```

Run on top 2-3 candidates. Look for: social media buzz, analyst upgrades/downgrades, catalyst events.

### Step 6 — Build Diverse Spread Setups

**Diversity rule:** Always present BOTH call spreads AND put spreads. Mix debit (directional) and credit (premium selling).

**Call Spreads (Debit — Bullish):**
- Best when: P/C < 0.70 (bullish flow), low IV, momentum positive
- Buy ATM call, sell OTM call
- NFLX example: $81/$86 call spread

**Put Spreads (Credit — Premium Selling):**
- Best when: high IV (>25%), neutral-to-bullish thesis
- Sell OTM put, buy lower protective put
- SMCI example: sell $30 put, buy $27 put

**Bear Put Spreads (Debit — Bearish):**
- Best when: P/C > 0.88 (put-heavy flow), negative momentum
- Buy ATM put, sell OTM put
- UBER example: buy $62 put, sell $58 put

**IV Decision Matrix:**
| IV Regime | Strategy | Example |
|-----------|----------|---------|
| Low (<15%) | Debit spreads | NFLX call spread |
| Medium (15-25%) | Either | TSLA, HOOD |
| High (>25%) | Credit spreads | SMCI, MARA, IONQ |

### Step 7 — Present as Matrix

```
SETUP          TYPE     DIRECTION  IV REGIME  CONVICTION
NFLX call spr  DEBIT    BULLISH    LOW        HIGH (0.11 P/C + quant 72)
MU call spread DEBIT    BULLISH    LOW        HIGH (0.27 P/C + quant 77)
SMCI put cred  CREDIT   NEUTRAL    HIGH       MEDIUM (IV seller)
MARA put cred  CREDIT   NEUTRAL    HIGH       MEDIUM (crypto IV)
```

## Pitfalls

- **yfinance rate limits after 2-3 calls**: Don't try to score all 60+ tickers. Pick the 2-3 best from options flow, score those only.
- **alpaca-py not in hermes venv**: Must use `/usr/bin/python3` (Python 3.12), not the hermes venv python.
- **last30days requires python3.12**: Script exits on 3.11 with version check error.
- **Alpaca credentials**: Load from `~/alpaca-bot/.env`, NOT `~/.hermes/.env`.
- **Don't forget diversity**: Dwayne explicitly wants call spreads AND put spreads, debit AND credit. Never present only one type.
