#!/usr/bin/env python3
"""
Wolf Spread Strategist — applies the Small-Account Vertical Spread Playbook
to Wolf's daily ticker signals, suggesting specific option spread trades.

Playbook reference: references/vertical-spread-playbook.md

Flow:
  1. Take top-scored tickers from Wolf
  2. Determine directional bias (bullish/bearish) from sentiment
  3. Classify IV regime (high/low → credit/debit) — flags for data verification
  4. Suggest specific strikes based on delta targets
  5. Apply sizing and skip rules
  6. Output trade-ready spread suggestions
"""

import sys
import os
from typing import Optional

# ── Playbook Constants ──────────────────────────────────────────────────

# Credit spread rules
CREDIT_SHORT_DELTA_DEFAULT = 0.30   # 30 delta = ~70% prob OTM
CREDIT_SHORT_DELTA_MIN = 0.15       # Conservative floor
CREDIT_SHORT_DELTA_MAX = 0.30       # Don't go above 30 delta
CREDIT_PROFIT_TARGET = 0.50         # Take profit at 50% of max
CREDIT_DTE_DEFAULT = 35             # 30-45 DTE sweet spot

# Debit spread rules
DEBIT_LONG_DELTA = 0.60             # Long leg ~60 delta
DEBIT_SHORT_DELTA = 0.40            # Short leg ~40 delta
DEBIT_DTE_DEFAULT = 35

# Sizing
MAX_LOSS_PER_TRADE_PCT = 0.02       # Max 2% of account per trade
MIN_PREMIUM_RATIO = 0.15            # Credit must be ≥ 15% of spread width

# Liquidity filters
MIN_OPEN_INTEREST = 100
MAX_BID_ASK_SPREAD = 0.10           # ≤ $0.10 wide for liquid underlyings

# ── Direction Classification ────────────────────────────────────────────

def classify_direction(sentiment: float, mentions: int, sources: int) -> str:
    """Classify directional bias: bullish, bearish, or neutral.

    Uses sentiment score + signal strength (multi-source confirmation).
    """
    if sentiment > 0.15 and sources >= 2:
        return "bullish"
    elif sentiment < -0.10 and sources >= 2:
        return "bearish"
    elif sentiment > 0.05:
        return "bullish_weak"
    elif sentiment < -0.05:
        return "bearish_weak"
    else:
        return "neutral"


# ── Spread Type Selector ────────────────────────────────────────────────

def select_spread_type(iv_regime: str, direction: str) -> Optional[dict]:
    """Select spread type based on IV regime and directional bias.

    Returns None if no suitable spread exists (e.g., neutral direction).
    """
    if direction in ("neutral",):
        return None

    is_bullish = "bullish" in direction

    if iv_regime == "high":
        # Credit spreads: sell premium
        if is_bullish:
            return {
                "type": "Bullish Put Credit Spread",
                "action": "sell_put_spread",
                "bias": "bullish_to_neutral",
                "reason": "High IV favors premium selling. Bullish bias → sell OTM put spread.",
                "profit_target": f"{CREDIT_PROFIT_TARGET*100:.0f}% of max profit",
                "theta_friendly": True,
            }
        else:
            return {
                "type": "Bearish Call Credit Spread",
                "action": "sell_call_spread",
                "bias": "bearish_to_neutral",
                "reason": "High IV favors premium selling. Bearish bias → sell OTM call spread.",
                "profit_target": f"{CREDIT_PROFIT_TARGET*100:.0f}% of max profit",
                "theta_friendly": True,
            }
    else:  # low IV
        # Debit spreads: buy directional exposure cheap
        if is_bullish:
            return {
                "type": "Bullish Call Debit Spread",
                "action": "buy_call_spread",
                "bias": "bullish",
                "reason": "Low IV means cheap directional exposure. Bullish → buy call spread.",
                "profit_target": "take profits when directional move occurs",
                "theta_friendly": False,
            }
        else:
            return {
                "type": "Bearish Put Debit Spread",
                "action": "buy_put_spread",
                "bias": "bearish",
                "reason": "Low IV means cheap directional exposure. Bearish → buy put spread.",
                "profit_target": "take profits when directional move occurs",
                "theta_friendly": False,
            }


# ── Strike Suggester ────────────────────────────────────────────────────

def suggest_spread_strikes(
    ticker: str,
    current_price: float,
    spread_type: str,
    direction: str,
    dte: int = CREDIT_DTE_DEFAULT,
    width_points: float = None,
) -> dict:
    """Suggest specific strike prices based on delta targets and current price.

    These are approximate — real strikes must be verified against the option chain.
    """
    is_bullish = "bullish" in direction
    is_credit = "credit" in spread_type.lower()

    if is_credit:
        # Credit spread: short at ~30 delta OTM
        if is_bullish:
            # Put credit spread: sell put below market
            otm_distance = current_price * 0.04  # ~4% OTM for 30 delta
            short_strike = round(current_price - otm_distance, 2)
            width = width_points or max(1.0, round(current_price * 0.01, 1))  # ~1% width
            long_strike = short_strike - width
            return {
                "strategy": "Put Credit Spread",
                "short_strike": round(short_strike, 2),
                "long_strike": round(long_strike, 2),
                "spread_width": round(width, 2),
                "max_loss_per_contract": round(width * 100, 2),
                "short_delta_approx": f"~{CREDIT_SHORT_DELTA_DEFAULT*100:.0f} delta",
                "probability_otm": f"~{(1-CREDIT_SHORT_DELTA_DEFAULT)*100:.0f}%",
                "strike_note": f"Sell {short_strike} put, buy {long_strike} put",
            }
        else:
            # Call credit spread: sell call above market
            otm_distance = current_price * 0.04
            short_strike = round(current_price + otm_distance, 2)
            width = width_points or max(1.0, round(current_price * 0.01, 1))
            long_strike = short_strike + width
            return {
                "strategy": "Call Credit Spread",
                "short_strike": round(short_strike, 2),
                "long_strike": round(long_strike, 2),
                "spread_width": round(width, 2),
                "max_loss_per_contract": round(width * 100, 2),
                "short_delta_approx": f"~{CREDIT_SHORT_DELTA_DEFAULT*100:.0f} delta",
                "probability_otm": f"~{(1-CREDIT_SHORT_DELTA_DEFAULT)*100:.0f}%",
                "strike_note": f"Sell {short_strike} call, buy {long_strike} call",
            }
    else:
        # Debit spread: long ~60 delta, short ~40 delta
        if is_bullish:
            # Call debit: buy ITM call, sell OTM call
            long_strike = round(current_price * 0.97, 2)   # ~3% ITM → 60 delta
            short_strike = round(current_price * 1.02, 2)  # ~2% OTM → 40 delta
            width = short_strike - long_strike
            return {
                "strategy": "Call Debit Spread",
                "long_strike": round(long_strike, 2),
                "short_strike": round(short_strike, 2),
                "spread_width": round(width, 2),
                "max_loss_per_contract": "debit paid × 100",
                "long_delta_approx": f"~{DEBIT_LONG_DELTA*100:.0f} delta",
                "short_delta_approx": f"~{DEBIT_SHORT_DELTA*100:.0f} delta",
                "strike_note": f"Buy {long_strike} call, sell {short_strike} call",
            }
        else:
            # Put debit: buy ITM put, sell OTM put
            long_strike = round(current_price * 1.03, 2)   # ~3% OTM → 60 delta put
            short_strike = round(current_price * 0.98, 2)  # ~2% ITM → 40 delta put
            width = long_strike - short_strike
            return {
                "strategy": "Put Debit Spread",
                "long_strike": round(long_strike, 2),
                "short_strike": round(short_strike, 2),
                "spread_width": round(width, 2),
                "max_loss_per_contract": "debit paid × 100",
                "long_delta_approx": f"~{DEBIT_LONG_DELTA*100:.0f} delta",
                "short_delta_approx": f"~{DEBIT_SHORT_DELTA*100:.0f} delta",
                "strike_note": f"Buy {long_strike} put, sell {short_strike} put",
            }


# ── Trade Evaluator ─────────────────────────────────────────────────────

def evaluate_signal_for_spread(
    signal: dict,
    current_price: float = None,
    iv_regime: str = "unknown",
    account_size: float = None,
) -> Optional[dict]:
    """Evaluate a Wolf signal against the vertical spread playbook.

    Returns a trade suggestion dict, or None if the signal doesn't qualify.
    """
    ticker = signal.get("ticker", "")
    sentiment = signal.get("avg_sentiment", 0)
    mentions = signal.get("mentions", 0)
    sources = signal.get("velocity", 1)
    score = signal.get("score", 0)

    # ── Gate 1: Signal strength ──
    # Only evaluate 🟢 STRONG BUY or high 🟡 WATCH signals
    if score < 0.35:
        return None

    # ── Gate 2: Direction ──
    direction = classify_direction(sentiment, mentions, sources)
    if direction == "neutral":
        return None

    # ── Gate 3: Spread type ──
    spread = select_spread_type(iv_regime, direction)
    if spread is None:
        return None

    # ── Gate 4: Strikes (if we have a price) ──
    strikes = None
    if current_price:
        strikes = suggest_spread_strikes(
            ticker, current_price,
            spread_type=spread["type"],
            direction=direction,
        )

    # ── Gate 5: Risk check ──
    risk_warning = None
    if account_size and strikes and "max_loss_per_contract" in strikes:
        max_loss = strikes["max_loss_per_contract"]
        if isinstance(max_loss, (int, float)):
            max_loss_pct = max_loss / account_size
            if max_loss_pct > MAX_LOSS_PER_TRADE_PCT:
                risk_warning = f"⚠️ Max loss (${max_loss:.0f}) exceeds {MAX_LOSS_PER_TRADE_PCT*100:.0f}% of account"
                # Suggest tightening: recalculate with 1-2% width
                if current_price:
                    tight_width = round(current_price * 0.015, 1)
                    tight_strikes = suggest_spread_strikes(
                        ticker, current_price,
                        spread_type=spread["type"],
                        direction=direction,
                        width_points=tight_width,
                    )
                    strikes = tight_strikes
                    risk_warning += f" → tightened to ${tight_width} width (${tight_strikes.get('max_loss_per_contract', 0):.0f} max loss)"

    # ── Gate 6: IV uncertainty flag ──
    iv_note = None
    if iv_regime == "unknown":
        iv_note = "⚠️ IV regime unknown — verify before entry"

    # ── Gate 7: Directional strength flag ──
    conviction_note = None
    if "weak" in direction:
        conviction_note = "⚠️ Weak directional signal — consider reducing size or skipping"

    # ── Build suggestion ──
    suggestion = {
        "ticker": ticker,
        "company": signal.get("company_name", ticker),
        "wolf_score": score,
        "sentiment": sentiment,
        "direction": direction,
        "iv_regime": iv_regime,
        **spread,
    }

    if strikes:
        suggestion["strikes"] = strikes

    notes = []
    if risk_warning:
        notes.append(risk_warning)
    if iv_note:
        notes.append(iv_note)
    if conviction_note:
        notes.append(conviction_note)
    if notes:
        suggestion["notes"] = notes

    # Sources context
    sources_list = sorted(signal.get("sources", []))
    if sources_list:
        suggestion["signal_sources"] = sources_list

    return suggestion


# ── Batch Evaluator ──────────────────────────────────────────────────────

def evaluate_signals(
    signals: list[dict],
    current_prices: dict = None,
    iv_regimes: dict = None,
    account_size: float = None,
) -> list[dict]:
    """Evaluate all Wolf signals for spread trade opportunities.

    Args:
        signals: Wolf's scored ticker signals
        current_prices: {ticker: price} dict (optional, for strike suggestions)
        iv_regimes: {ticker: 'high'|'low'|'unknown'} dict (optional)
        account_size: account value for risk checks
    """
    current_prices = current_prices or {}
    iv_regimes = iv_regimes or {}

    suggestions = []
    for signal in signals:
        ticker = signal.get("ticker", "")
        price = current_prices.get(ticker)
        iv = iv_regimes.get(ticker, "unknown")

        suggestion = evaluate_signal_for_spread(
            signal,
            current_price=price,
            iv_regime=iv,
            account_size=account_size,
        )
        if suggestion:
            suggestions.append(suggestion)

    # Sort by wolf_score descending
    suggestions.sort(key=lambda s: s["wolf_score"], reverse=True)
    return suggestions


# ── Output Formatting ────────────────────────────────────────────────────

def format_spread_suggestions(suggestions: list[dict]) -> str:
    """Format spread suggestions for Telegram."""
    if not suggestions:
        return "🐺 _No spread trades meet the playbook criteria today._"

    lines = [
        "## 🎯 SPREAD TRADE SUGGESTIONS",
        "_Vertical spreads following the small-account playbook_",
        "",
    ]

    for s in suggestions[:5]:  # Top 5 only
        ticker = s["ticker"]
        company = s.get("company", ticker)
        spread_type = s["type"]
        direction = s["direction"]
        iv_regime = s.get("iv_regime", "unknown")

        # Emoji for direction
        dir_emoji = "📈" if "bullish" in direction else "📉"
        iv_emoji = "🔴" if iv_regime == "high" else ("🟢" if iv_regime == "low" else "❓")

        lines.append(f"### {dir_emoji} ${ticker} — {spread_type}")
        lines.append(f"• **Company:** {company}")
        lines.append(f"• **Signal:** score {s['wolf_score']:.2f} · sentiment {s['sentiment']:+.2f}")
        lines.append(f"• **IV regime:** {iv_emoji} {iv_regime.upper()}")
        lines.append(f"• **Bias:** {s['bias'].replace('_', ' ')}")
        lines.append(f"• **Why:** {s['reason']}")

        if "strikes" in s:
            st = s["strikes"]
            lines.append(f"• **Strikes:** {st.get('strike_note', 'N/A')}")
            lines.append(f"• **Max loss:** ${st.get('max_loss_per_contract', 'N/A')}")
            if "probability_otm" in st:
                lines.append(f"• **Prob OTM:** {st['probability_otm']}")

        lines.append(f"• **Profit target:** {s['profit_target']}")

        if s.get("notes"):
            for note in s["notes"]:
                lines.append(f"• {note}")

        if s.get("signal_sources"):
            lines.append(f"• **Sources:** {', '.join(s['signal_sources'])}")

        lines.append("")

    lines.append("━" * 30)
    lines.append("🐺 _Hypothetical suggestions — verify IV, delta, and liquidity before trading._")
    lines.append("_Not financial advice. Paper trade first._")

    return "\n".join(lines)


if __name__ == "__main__":
    # Demo: test with a mock signal
    mock_signals = [
        {
            "ticker": "AAPL",
            "company_name": "Apple",
            "score": 0.72,
            "avg_sentiment": 0.25,
            "mentions": 15,
            "velocity": 2,
            "sources": ["reddit", "news"],
        },
        {
            "ticker": "NVDA",
            "company_name": "Nvidia",
            "score": 0.55,
            "avg_sentiment": -0.18,
            "mentions": 10,
            "velocity": 2,
            "sources": ["twitter", "reddit"],
        },
    ]

    mock_prices = {"AAPL": 195.50, "NVDA": 880.00}
    mock_iv = {"AAPL": "high", "NVDA": "low"}

    results = evaluate_signals(mock_signals, mock_prices, mock_iv, account_size=5000)
    print(format_spread_suggestions(results))
