#!/usr/bin/env python3
"""
AI-Trader Client — Secure trading client for ai4trade.ai.

Features:
- Token from env var AI_TRADER_TOKEN or ~/.hermes/ai-trader-token.txt (chmod 600 check)
- Position size limits (10% of portfolio, max 1000 shares)
- Rate limiting (5s between trades)
- Duplicate trade detection (recent signal hashes)
- Circuit breaker (max 20 trades/hour)
- Idempotency keys (uuid4) on every trade
- Market hours check (US: 9:30-16:00 ET, M-F)
- Position check before trade execution
- WebSocket reconnect with exponential backoff
- Trade audit log to data/audit.jsonl
- CLI interface: status|positions|trade|heartbeat
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import re
import stat
import sys
import time
import uuid
from collections import deque
from datetime import datetime, time as dt_time, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pytz
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BASE_URL = "https://ai4trade.ai"
API_BASE = f"{BASE_URL}/api"
WS_BASE = "wss://ai4trade.ai/ws/notify"

# Position limits
MAX_POSITION_PCT = 0.10  # 10% of portfolio per position
MAX_QUANTITY = 1000  # absolute max shares/contracts

# Rate limiting
MIN_TRADE_INTERVAL_SECONDS = 5

# Circuit breaker
MAX_TRADES_PER_HOUR = 20

# Duplicate detection
DUPLICATE_WINDOW_SECONDS = 300  # 5 min

# WebSocket reconnect
WS_MAX_RETRIES = 5
WS_BASE_DELAY = 1.0
WS_MAX_DELAY = 60.0

# Paths
TOKEN_FILE = Path.home() / ".hermes" / "ai-trader-token.txt"
SKILL_DIR = Path.home() / ".hermes" / "skills" / "trading" / "ai-trader"
DATA_DIR = SKILL_DIR / "data"
STATE_FILE = DATA_DIR / "state.json"
AUDIT_LOG = DATA_DIR / "audit.jsonl"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# US Market hours (Eastern Time)
EASTERN_TZ = pytz.timezone("US/Eastern")
MARKET_OPEN = dt_time(9, 30)
MARKET_CLOSE = dt_time(16, 0)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("ai_trader_client")


# ---------------------------------------------------------------------------
# Custom Exceptions
# ---------------------------------------------------------------------------

class AiTraderError(Exception):
    """Base exception for AI-Trader client errors."""

class AuthError(AiTraderError):
    """Raised on authentication / token issues."""

class RateLimitError(AiTraderError):
    """Raised when rate limit is exceeded."""

class DuplicateTradeError(AiTraderError):
    """Raised when a duplicate trade signal is detected."""

class CircuitBreakerError(AiTraderError):
    """Raised when hourly trade limit is exceeded."""

class MarketClosedError(AiTraderError):
    """Raised when US markets are closed for stock trades."""

class PositionLimitError(AiTraderError):
    """Raised when position limits are exceeded."""

class ApiError(AiTraderError):
    """Raised on unexpected API errors."""

class WebSocketError(AiTraderError):
    """Raised on WebSocket connection issues."""


# ---------------------------------------------------------------------------
# Token loader
# ---------------------------------------------------------------------------

def load_token() -> str:
    """Load the API token from environment variable or file.

    Priority:
    1. AI_TRADER_TOKEN environment variable
    2. ~/.hermes/ai-trader-token.txt file (must be chmod 600)

    Returns:
        The bearer token string.

    Raises:
        AuthError: If no token source is found or permissions are unsafe.
    """
    token = os.environ.get("AI_TRADER_TOKEN")
    if token:
        logger.debug("Loaded token from AI_TRADER_TOKEN env var")
        return token.strip()

    token_path = TOKEN_FILE
    if not token_path.exists():
        raise AuthError(
            f"Token file not found at {token_path}. "
            "Set AI_TRADER_TOKEN env var or create the token file."
        )

    # Check file permissions — must be 600 (owner read/write only)
    file_stat = token_path.stat()
    perms = stat.S_IMODE(file_stat.st_mode)
    if perms != 0o600:
        raise AuthError(
            f"Token file {token_path} has unsafe permissions {oct(perms)}. "
            "Run: chmod 600 {token_path}"
        )

    token = token_path.read_text().strip()
    if not token:
        raise AuthError(f"Token file {token_path} is empty.")

    logger.debug("Loaded token from file")
    return token


# ---------------------------------------------------------------------------
# HTTP session
# ---------------------------------------------------------------------------

def _make_session() -> requests.Session:
    """Create a requests session with retry and connection pooling."""
    session = requests.Session()

    retry_strategy = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods={"GET", "POST"},
    )
    adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=20)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    return session


# ---------------------------------------------------------------------------
# Market hours
# ---------------------------------------------------------------------------

def is_market_open() -> Tuple[bool, Optional[str]]:
    """Check if US stock markets are currently open.

    Returns:
        Tuple of (is_open: bool, reason: str or None if open).
    """
    now_et = datetime.now(EASTERN_TZ)
    current_time = now_et.time()

    # Check weekday
    if now_et.weekday() >= 5:  # Saturday=5, Sunday=6
        return False, f"Market closed — it's {now_et.strftime('%A')} (weekend)"

    # Check hours
    if current_time < MARKET_OPEN:
        return False, f"Market not open yet — opens at 9:30 ET (now {now_et.strftime('%H:%M')} ET)"
    if current_time >= MARKET_CLOSE:
        return False, f"Market closed at 16:00 ET (now {now_et.strftime('%H:%M')} ET)"

    return True, None


# ---------------------------------------------------------------------------
# Signal hashing for duplicate detection
# ---------------------------------------------------------------------------

def _signal_hash(market: str, action: str, symbol: str, price: float, quantity: float) -> str:
    """Generate a deterministic hash for a trade signal."""
    raw = f"{market}:{action}:{symbol}:{price}:{quantity}"
    return hashlib.sha256(raw.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Audit log
# ---------------------------------------------------------------------------

def _write_audit(entry: Dict[str, Any]) -> None:
    """Append an audit entry to the JSONL audit log."""
    try:
        AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
        with AUDIT_LOG.open("a") as f:
            f.write(json.dumps(entry, default=str) + "\n")
    except OSError as exc:
        logger.warning("Failed to write audit log: %s", exc)


# ---------------------------------------------------------------------------
# ApiClient
# ---------------------------------------------------------------------------

class ApiClient:
    """Secure HTTP client for the AI-Trader API."""

    def __init__(self) -> None:
        self.token: str = load_token()
        self.session: requests.Session = _make_session()
        self._headers: Dict[str, str] = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

        # Rate limiting state (persisted)
        self._last_trade_time: float = 0.0

        # Duplicate detection (persisted)
        self._recent_hashes: deque[str] = deque(maxlen=100)
        self._hash_timestamps: Dict[str, float] = {}

        # Circuit breaker (persisted)
        self._trade_timestamps: deque[float] = deque()

        # Load persisted state
        self._load_state()

    def _load_state(self) -> None:
        """Load persistent state from state file for cross-invocation tracking."""
        try:
            if not STATE_FILE.exists():
                return
            data = json.loads(STATE_FILE.read_text())
            self._last_trade_time = float(data.get("last_trade_time", 0))
            for h, ts in data.get("hash_timestamps", {}).items():
                if time.time() - ts < DUPLICATE_WINDOW_SECONDS:
                    self._recent_hashes.append(h)
                    self._hash_timestamps[h] = ts
            for ts in data.get("trade_timestamps", []):
                if time.time() - float(ts) < 3600:
                    self._trade_timestamps.append(float(ts))
        except (OSError, json.JSONDecodeError, ValueError, TypeError) as exc:
            logger.debug("Could not load state (fresh start): %s", exc)

    def _save_state(self) -> None:
        """Persist current state to file for cross-invocation tracking."""
        try:
            state = {
                "last_trade_time": self._last_trade_time,
                "hash_timestamps": dict(self._hash_timestamps),
                "trade_timestamps": list(self._trade_timestamps),
            }
            STATE_FILE.write_text(json.dumps(state, default=str))
        except OSError as exc:
            logger.warning("Could not save state: %s", exc)

    def _request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> requests.Response:
        """Make an authenticated HTTP request.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: API path (e.g., /api/positions)
            **kwargs: Extra arguments for requests.

        Returns:
            Response object.

        Raises:
            ApiError: On non-success HTTP status.
        """
        url = f"{API_BASE}{path}" if not path.startswith("http") else path
        headers = {**self._headers, **kwargs.pop("headers", {})}

        try:
            resp = self.session.request(method, url, headers=headers, timeout=30, **kwargs)
        except requests.exceptions.Timeout as exc:
            raise ApiError(f"Request timed out: {method} {path}") from exc
        except requests.exceptions.ConnectionError as exc:
            raise ApiError(f"Connection error: {method} {path}") from exc
        except requests.exceptions.RequestException as exc:
            raise ApiError(f"Request failed: {method} {path}: {exc}") from exc

        if resp.status_code == 401:
            raise AuthError(f"Authentication failed (401) for {method} {path}")
        if resp.status_code == 429:
            raise RateLimitError(f"Rate limited (429) for {method} {path}")
        if not resp.ok:
            body = resp.text[:500]
            raise ApiError(
                f"API error {resp.status_code} for {method} {path}: {body}"
            )

        return resp

    # ------------------------------------------------------------------
    # Heartbeat
    # ------------------------------------------------------------------

    def heartbeat(self) -> Dict[str, Any]:
        """Send heartbeat to check for messages, tasks, and notifications.

        Returns:
            Heartbeat response dict with messages, tasks, poll interval, etc.
        """
        resp = self._request("POST", "/claw/agents/heartbeat")
        data: Dict[str, Any] = resp.json()
        logger.info(
            "Heartbeat: %d messages, %d tasks",
            len(data.get("messages", [])),
            len(data.get("tasks", [])),
        )
        return data

    # ------------------------------------------------------------------
    # Positions
    # ------------------------------------------------------------------

    def get_positions(self) -> List[Dict[str, Any]]:
        """Fetch current positions from the API.

        Returns:
            List of position dicts.
        """
        resp = self._request("GET", "/positions")
        raw = resp.json()
        if isinstance(raw, dict):
            data: List[Dict[str, Any]] = raw.get("positions", [])
        elif isinstance(raw, list):
            data = raw
        else:
            data = []
        logger.info("Retrieved %d positions", len(data))
        return data

    def get_portfolio_value(self) -> float:
        """Calculate total portfolio value from positions and agent info.

        Returns:
            Total portfolio value in dollars.
        """
        try:
            resp = self._request("GET", "/claw/agents/me")
            agent = resp.json()
            cash = float(agent.get("cash", 0))
            # Positions value = sum of position values
            positions_value = 0.0
            for pos in self.get_positions():
                positions_value += float(pos.get("value", 0))
            return cash + positions_value
        except (AiTraderError, ValueError, TypeError) as exc:
            logger.warning("Could not calculate portfolio value: %s", exc)
            return 0.0

    # ------------------------------------------------------------------
    # Trade Signal
    # ------------------------------------------------------------------

    def submit_trade(
        self,
        market: str,
        action: str,
        symbol: str,
        price: float,
        quantity: float,
        content: Optional[str] = None,
        executed_at: str = "now",
        bypass_checks: bool = False,
    ) -> Dict[str, Any]:
        """Submit a trade signal with full safety checks.

        Args:
            market: Market (us-stock, crypto, polymarket).
            action: Action (buy, sell, short, cover).
            symbol: Trading symbol.
            price: Execution price (0 for auto-quote).
            quantity: Position size.
            content: Optional notes.
            executed_at: ISO 8601 timestamp or "now".
            bypass_checks: If True, skip safety checks (use with caution).

        Returns:
            API response dict.

        Raises:
            MarketClosedError: If markets are closed (stock trades only).
            RateLimitError: If trading too fast.
            DuplicateTradeError: If identical signal sent recently.
            CircuitBreakerError: If hourly trade limit exceeded.
            PositionLimitError: If quantity exceeds limits.
            AuthError: On auth issues.
            ApiError: On other API errors.
        """
        if not bypass_checks:
            # Market hours check (US stocks only — skip for simulated trades)
            if market == "us-stock" and price > 0:
                open_flag, reason = is_market_open()
                if not open_flag:
                    raise MarketClosedError(reason or "US markets are closed")

            # Rate limiting
            elapsed = time.time() - self._last_trade_time
            if elapsed < MIN_TRADE_INTERVAL_SECONDS:
                wait = MIN_TRADE_INTERVAL_SECONDS - elapsed
                raise RateLimitError(
                    f"Rate limited — wait {wait:.1f}s between trades "
                    f"(last trade was {elapsed:.1f}s ago, minimum {MIN_TRADE_INTERVAL_SECONDS}s)"
                )

            # Duplicate detection
            sig_hash = _signal_hash(market, action, symbol, price, quantity)
            now = time.time()
            # Prune old hashes
            stale = [
                h for h, ts in self._hash_timestamps.items()
                if now - ts > DUPLICATE_WINDOW_SECONDS
            ]
            for h in stale:
                self._hash_timestamps.pop(h, None)
                if h in self._recent_hashes:
                    self._recent_hashes.remove(h)

            if sig_hash in self._recent_hashes:
                raise DuplicateTradeError(
                    f"Duplicate trade detected: {market} {action} {symbol} "
                    f"qty={quantity} price={price} — identical signal submitted "
                    f"within {DUPLICATE_WINDOW_SECONDS}s window"
                )

            # Circuit breaker
            cutoff = now - 3600
            while self._trade_timestamps and self._trade_timestamps[0] < cutoff:
                self._trade_timestamps.popleft()
            if len(self._trade_timestamps) >= MAX_TRADES_PER_HOUR:
                raise CircuitBreakerError(
                    f"Circuit breaker active — {MAX_TRADES_PER_HOUR} trades already "
                    f"submitted in the last hour"
                )

            # Position size limits
            if quantity > MAX_QUANTITY:
                raise PositionLimitError(
                    f"Quantity {quantity} exceeds MAX_QUANTITY={MAX_QUANTITY}"
                )

            if market in ("us-stock", "crypto"):
                portfolio_value = self.get_portfolio_value()
                max_pct_qty = int(portfolio_value * MAX_POSITION_PCT / (price if price > 0 else 1))
                if quantity > max_pct_qty > 0:
                    raise PositionLimitError(
                        f"Quantity {quantity} exceeds {MAX_POSITION_PCT*100}% "
                        f"of portfolio (${portfolio_value:.2f}) = {max_pct_qty} units"
                    )

            # Position check
            positions = self.get_positions()
            existing_position = None
            for pos in positions:
                if pos.get("symbol", "").upper() == symbol.upper() and pos.get("market") == market:
                    existing_position = pos
                    break
            if existing_position:
                logger.info(
                    "Existing position for %s: %s units at $%s",
                    symbol, existing_position.get("quantity", "?"), existing_position.get("entry_price", "?")
                )

        # Build payload
        idempotency_key = str(uuid.uuid4())
        payload: Dict[str, Any] = {
            "market": market,
            "action": action,
            "symbol": symbol,
            "price": price,
            "quantity": quantity,
            "executed_at": executed_at,
            "idempotency_key": idempotency_key,
        }
        if content:
            payload["content"] = content

        # Submit
        resp = self._request("POST", "/signals/realtime", json=payload)

        # Update state on success
        self._last_trade_time = time.time()
        sig_hash = _signal_hash(market, action, symbol, price, quantity)
        self._recent_hashes.append(sig_hash)
        self._hash_timestamps[sig_hash] = time.time()
        self._trade_timestamps.append(time.time())
        self._save_state()

        data: Dict[str, Any] = resp.json()

        # Audit log
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "idempotency_key": idempotency_key,
            "market": market,
            "action": action,
            "symbol": symbol,
            "price": price,
            "quantity": quantity,
            "status": "submitted",
            "response": data,
        }
        _write_audit(audit_entry)

        logger.info(
            "Trade submitted: %s %s %s x%s (idempotency=%s)",
            action.upper(), symbol, market, quantity, idempotency_key[:8],
        )
        return data

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def status(self) -> Dict[str, Any]:
        """Get overall account status (agent info + positions summary).

        Returns:
            Dict with agent info, positions count, portfolio value.
        """
        agent_resp = self._request("GET", "/claw/agents/me")
        agent: Dict[str, Any] = agent_resp.json()

        positions = self.get_positions()
        portfolio_value = 0.0
        try:
            cash = float(agent.get("cash", 0))
            pos_value = 0.0
            for p in positions:
                # Try value field first, fall back to quantity * current_price
                val = p.get("value")
                if val and float(val) > 0:
                    pos_value += float(val)
                else:
                    qty = float(p.get("quantity", 0) or 0)
                    price = float(p.get("current_price", 0) or 0)
                    if qty > 0 and price > 0:
                        pos_value += qty * price
                    else:
                        price = float(p.get("entry_price", 0) or 0)
                        if qty > 0 and price > 0:
                            pos_value += qty * price
            portfolio_value = cash + pos_value
        except (ValueError, TypeError):
            pass

        return {
            "agent": agent,
            "agent_id": agent.get("id"),
            "agent_name": agent.get("name"),
            "cash": agent.get("cash", "N/A"),
            "points": agent.get("points", "N/A"),
            "reputation": agent.get("reputation", "N/A"),
            "positions_count": len(positions),
            "portfolio_value": portfolio_value,
        }

    # ------------------------------------------------------------------
    # Strategy & Discussion signals
    # ------------------------------------------------------------------

    def publish_strategy(
        self,
        market: str,
        title: str,
        content: str,
        symbols: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Publish a strategy signal.

        Args:
            market: Market (us-stock, crypto, polymarket).
            title: Strategy title.
            content: Strategy content/thesis.
            symbols: List of symbols this strategy covers.
            tags: List of tags.

        Returns:
            API response dict.
        """
        payload: Dict[str, Any] = {
            "market": market,
            "title": title,
            "content": content,
        }
        if symbols:
            payload["symbols"] = ",".join(symbols) if isinstance(symbols, list) else symbols
        if tags:
            payload["tags"] = ",".join(tags) if isinstance(tags, list) else tags

        resp = self._request("POST", "/signals/strategy", json=payload)
        data: Dict[str, Any] = resp.json()
        logger.info("Strategy published: %s", title)
        _write_audit({
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "type": "strategy",
            "title": title,
            "market": market,
            "symbols": symbols,
        })
        return data

    def publish_discussion(
        self,
        title: str,
        content: str,
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Publish a discussion signal.

        Args:
            title: Discussion title.
            content: Discussion content.
            tags: List of tags.

        Returns:
            API response dict.
        """
        payload: Dict[str, Any] = {
            "title": title,
            "content": content,
        }
        if tags:
            payload["tags"] = tags

        resp = self._request("POST", "/signals/discussion", json=payload)
        data: Dict[str, Any] = resp.json()
        logger.info("Discussion published: %s", title)
        _write_audit({
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "type": "discussion",
            "title": title,
        })
        return data

    def reply_to_signal(
        self,
        signal_id: int,
        content: str,
        user_name: str = "Hermes_Dwayne_Primeau",
    ) -> Dict[str, Any]:
        """Reply to a signal.

        Args:
            signal_id: The signal to reply to.
            content: Reply content.
            user_name: Display name.

        Returns:
            API response dict.
        """
        resp = self._request("POST", "/signals/reply", json={
            "signal_id": signal_id,
            "user_name": user_name,
            "content": content,
        })
        data: Dict[str, Any] = resp.json()
        logger.info("Replied to signal %d", signal_id)
        return data

    # ------------------------------------------------------------------
    # Feed browsing
    # ------------------------------------------------------------------

    def get_feed(
        self,
        limit: int = 10,
        message_type: Optional[str] = None,
        symbol: Optional[str] = None,
        keyword: Optional[str] = None,
        sort: str = "new",
    ) -> List[Dict[str, Any]]:
        """Browse the signal feed.

        Args:
            limit: Max signals to return.
            message_type: Filter by type (realtime, strategy, discussion).
            symbol: Filter by symbol.
            keyword: Search keyword.
            sort: Sort order (new, active, following).

        Returns:
            List of signal dicts.
        """
        params: Dict[str, Any] = {"limit": limit, "sort": sort}
        if message_type:
            params["message_type"] = message_type
        if symbol:
            params["symbol"] = symbol
        if keyword:
            params["keyword"] = keyword

        resp = self._request("GET", "/signals/feed", params=params)
        data = resp.json()
        if isinstance(data, dict):
            data = data.get("signals", data.get("data", []))
        logger.info("Feed returned %d signals", len(data) if isinstance(data, list) else 0)
        return data if isinstance(data, list) else []

    # ------------------------------------------------------------------
    # Rebalance analysis
    # ------------------------------------------------------------------

    def analyze_positions(self) -> Dict[str, Any]:
        """Analyze current positions for rebalancing opportunities.

        Returns:
            Dict with winners, losers, concentration risk, and suggestions.
        """
        positions = self.get_positions()
        if not positions:
            return {"error": "No positions to analyze"}

        total_value = 0.0
        position_details = []

        for pos in positions:
            symbol = pos.get("symbol", "?")
            qty = float(pos.get("quantity", 0) or 0)
            entry = float(pos.get("entry_price", 0) or 0)
            current = float(pos.get("current_price", 0) or 0)
            value = float(pos.get("value", 0) or 0)

            if value == 0 and qty > 0 and current > 0:
                value = qty * current
            if value == 0 and qty > 0 and entry > 0:
                value = qty * entry

            pnl_pct = ((current - entry) / entry * 100) if entry > 0 else 0
            total_value += value

            position_details.append({
                "symbol": symbol,
                "quantity": qty,
                "entry": entry,
                "current": current,
                "value": value,
                "pnl_pct": round(pnl_pct, 2),
                "market": pos.get("market", "unknown"),
            })

        # Sort by P&L
        winners = sorted([p for p in position_details if p["pnl_pct"] > 0],
                        key=lambda x: x["pnl_pct"], reverse=True)
        losers = sorted([p for p in position_details if p["pnl_pct"] < 0],
                       key=lambda x: x["pnl_pct"])

        # Concentration analysis
        concentration = []
        for p in position_details:
            pct = (p["value"] / total_value * 100) if total_value > 0 else 0
            p["weight_pct"] = round(pct, 1)
            if pct > 15:
                concentration.append(f"⚠️ {p['symbol']}: {pct:.1f}% (over-concentrated)")

        return {
            "total_positions": len(positions),
            "total_value": round(total_value, 2),
            "winners": winners,
            "losers": losers,
            "concentration_warnings": concentration,
            "suggestions": self._generate_suggestions(position_details, total_value),
        }

    def _generate_suggestions(
        self, positions: List[Dict[str, Any]], total_value: float
    ) -> List[str]:
        """Generate rebalance suggestions based on position analysis."""
        suggestions = []

        losers = [p for p in positions if p["pnl_pct"] < -5]
        if losers:
            syms = ", ".join(f"{p['symbol']} ({p['pnl_pct']}%)" for p in losers[:3])
            suggestions.append(f"Consider cutting losers: {syms}")

        winners = [p for p in positions if p["pnl_pct"] > 3]
        if winners:
            syms = ", ".join(f"{p['symbol']} (+{p['pnl_pct']}%)" for p in winners[:3])
            suggestions.append(f"Consider taking profits on: {syms}")

        over_weight = [p for p in positions if p.get("weight_pct", 0) > 15]
        if over_weight:
            syms = ", ".join(f"{p['symbol']} ({p['weight_pct']}%)" for p in over_weight)
            suggestions.append(f"Reduce concentration: {syms}")

        # Check sector/market balance
        crypto = [p for p in positions if p["market"] == "crypto"]
        stocks = [p for p in positions if p["market"] == "us-stock"]
        if len(crypto) > 0 and len(stocks) > 0:
            crypto_val = sum(p["value"] for p in crypto)
            stock_val = sum(p["value"] for p in stocks)
            if total_value > 0:
                crypto_pct = crypto_val / total_value * 100
                if crypto_pct > 30:
                    suggestions.append(f"Crypto exposure high at {crypto_pct:.0f}% — consider trimming")

        return suggestions

    # ------------------------------------------------------------------
    # Follow trader
    # ------------------------------------------------------------------

    def follow_trader(self, leader_id: int) -> Dict[str, Any]:
        """Follow a trader.

        Args:
            leader_id: The agent ID of the trader to follow.

        Returns:
            API response.
        """
        resp = self._request("POST", "/signals/follow", json={"leader_id": leader_id})
        data: Dict[str, Any] = resp.json()
        logger.info("Now following trader %s", leader_id)
        return data

    def unfollow_trader(self, leader_id: int) -> Dict[str, Any]:
        """Unfollow a trader.

        Args:
            leader_id: The agent ID of the trader to unfollow.

        Returns:
            API response.
        """
        resp = self._request("POST", "/signals/unfollow", json={"leader_id": leader_id})
        data: Dict[str, Any] = resp.json()
        logger.info("Unfollowed trader %s", leader_id)
        return data

    def get_following(self) -> List[Dict[str, Any]]:
        """List all traders being followed.

        Returns:
            List of followed trader dicts.
        """
        resp = self._request("GET", "/signals/following")
        data: List[Dict[str, Any]] = resp.json()
        logger.info("Following %d traders", len(data))
        return data

    # ------------------------------------------------------------------
    # Exchange points
    # ------------------------------------------------------------------

    def exchange_points(self, amount: int) -> Dict[str, Any]:
        """Exchange points for cash (1 point = $1,000).

        Args:
            amount: Number of points to exchange.

        Returns:
            API response.
        """
        resp = self._request(
            "POST", "/agents/points/exchange", json={"amount": amount}
        )
        data: Dict[str, Any] = resp.json()
        logger.info("Exchanged %d points for cash", amount)
        return data

    # ------------------------------------------------------------------
    # WebSocket notifications
    # ------------------------------------------------------------------

    def connect_websocket(self, agent_id: int) -> None:
        """Connect to the WebSocket notification stream with reconnection.

        Args:
            agent_id: The agent ID for the WebSocket URL.

        Raises:
            WebSocketError: If connection ultimately fails after retries.
        """
        import websocket  # type: ignore[import-untyped]

        ws_url = f"{WS_BASE}/{agent_id}"
        retries = 0
        delay = WS_BASE_DELAY

        def on_message(ws: Any, message: str) -> None:
            logger.info("WS message: %s", message)
            _write_audit({
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "type": "ws_message",
                "payload": message,
            })

        def on_error(ws: Any, error: Exception) -> None:
            logger.error("WS error: %s", error)

        def on_close(ws: Any, close_status_code: int, close_msg: str) -> None:
            logger.info("WS closed: code=%s msg=%s", close_status_code, close_msg)

        def on_open(ws: Any) -> None:
            logger.info("WS connected to %s", ws_url)
            # Reset retry on successful connect
            nonlocal retries, delay
            retries = 0
            delay = WS_BASE_DELAY
            # Send auth
            ws.send(json.dumps({"type": "auth", "token": self.token}))

        while retries < WS_MAX_RETRIES:
            try:
                ws = websocket.WebSocketApp(
                    ws_url,
                    on_message=on_message,
                    on_error=on_error,
                    on_close=on_close,
                    on_open=on_open,
                    header={"Authorization": f"Bearer {self.token}"},
                )
                ws.run_forever(ping_interval=30, ping_timeout=10)
            except Exception as exc:
                logger.warning(
                    "WS connection failed (attempt %d/%d): %s",
                    retries + 1, WS_MAX_RETRIES, exc,
                )

            retries += 1
            if retries < WS_MAX_RETRIES:
                logger.info("Reconnecting in %.1fs...", delay)
                time.sleep(delay)
                delay = min(delay * 2, WS_MAX_DELAY)
            else:
                raise WebSocketError(
                    f"WebSocket connection failed after {WS_MAX_RETRIES} retries"
                )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _cmd_status(args: argparse.Namespace) -> None:
    """Handle the 'status' CLI command."""
    client = ApiClient()
    info = client.status()
    print(json.dumps(info, indent=2, default=str))


def _cmd_positions(args: argparse.Namespace) -> None:
    """Handle the 'positions' CLI command."""
    client = ApiClient()
    positions = client.get_positions()
    if not positions:
        print("No open positions.")
        return
    for pos in positions:
        symbol = pos.get("symbol", "?") or "?"
        qty = pos.get("quantity", 0) or 0
        entry = pos.get("entry_price", "?") or "?"
        current = pos.get("current_price", "?") or "?"
        value = pos.get("value", "?") or "?"
        print(f"  {str(symbol):8s}  x{str(qty):<6}  entry=${str(entry):<8}  current=${str(current):<8}  value=${str(value)}")


def _cmd_trade(args: argparse.Namespace) -> None:
    """Handle the 'trade' CLI command."""
    client = ApiClient()
    try:
        result = client.submit_trade(
            market=args.market,
            action=args.action,
            symbol=args.symbol,
            price=args.price,
            quantity=args.quantity,
            content=args.content,
            executed_at=args.executed_at,
        )
        print(json.dumps(result, indent=2, default=str))
    except AiTraderError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def _cmd_heartbeat(args: argparse.Namespace) -> None:
    """Handle the 'heartbeat' CLI command."""
    client = ApiClient()
    result = client.heartbeat()
    print(json.dumps(result, indent=2, default=str))


def _cmd_strategy(args: argparse.Namespace) -> None:
    """Handle the 'strategy' CLI command."""
    client = ApiClient()
    symbols = args.symbols.split(",") if args.symbols else None
    tags = args.tags.split(",") if args.tags else None
    try:
        result = client.publish_strategy(
            market=args.market,
            title=args.title,
            content=args.content,
            symbols=symbols,
            tags=tags,
        )
        print(json.dumps(result, indent=2, default=str))
    except AiTraderError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def _cmd_discussion(args: argparse.Namespace) -> None:
    """Handle the 'discussion' CLI command."""
    client = ApiClient()
    tags = args.tags.split(",") if args.tags else None
    try:
        result = client.publish_discussion(
            title=args.title,
            content=args.content,
            tags=tags,
        )
        print(json.dumps(result, indent=2, default=str))
    except AiTraderError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def _cmd_feed(args: argparse.Namespace) -> None:
    """Handle the 'feed' CLI command."""
    client = ApiClient()
    try:
        signals = client.get_feed(
            limit=args.limit,
            message_type=args.type,
            symbol=args.symbol,
            keyword=args.keyword,
            sort=args.sort,
        )
        if not signals:
            print("No signals found.")
            return
        for s in signals:
            stype = str(s.get("message_type", s.get("type", "?")) or "?")
            title = str(s.get("title", s.get("content", "")[:60]) or "")
            agent = str(s.get("agent_name", s.get("user_name", "?")) or "?")
            sym = str(s.get("symbol", "") or "")
            ts = str(s.get("created_at", "") or "")[:16]
            print(f"  [{stype:12s}] {agent:20s} | {sym:8s} | {title[:50]:50s} | {ts}")
    except AiTraderError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def _cmd_rebalance(args: argparse.Namespace) -> None:
    """Handle the 'rebalance' CLI command."""
    client = ApiClient()
    try:
        analysis = client.analyze_positions()
        if "error" in analysis:
            print(analysis["error"])
            return

        print(f"\n📊 Portfolio Analysis — {analysis['total_positions']} positions")
        print(f"   Total value: ${analysis['total_value']:,.2f}\n")

        if analysis["winners"]:
            print("🟢 Winners:")
            for w in analysis["winners"]:
                print(f"   {w['symbol']:8s} +{w['pnl_pct']}%  ${w['value']:,.0f}  ({w.get('weight_pct', '?')}%)")

        if analysis["losers"]:
            print("\n🔴 Losers:")
            for l in analysis["losers"]:
                print(f"   {l['symbol']:8s} {l['pnl_pct']}%  ${l['value']:,.0f}  ({l.get('weight_pct', '?')}%)")

        if analysis["concentration_warnings"]:
            print("\n⚠️  Concentration:")
            for w in analysis["concentration_warnings"]:
                print(f"   {w}")

        if analysis["suggestions"]:
            print("\n💡 Suggestions:")
            for s in analysis["suggestions"]:
                print(f"   • {s}")

        if args.json:
            print("\n" + json.dumps(analysis, indent=2, default=str))
    except AiTraderError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog="ai_trader_client",
        description="AI-Trader trading client for ai4trade.ai",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # status
    sub.add_parser("status", help="Show account status")

    # positions
    sub.add_parser("positions", help="List open positions")

    # trade
    trade_parser = sub.add_parser("trade", help="Submit a trade signal")
    trade_parser.add_argument("--market", required=True,
                              choices=["us-stock", "crypto", "polymarket"],
                              help="Trading market")
    trade_parser.add_argument("--action", required=True,
                              choices=["buy", "sell", "short", "cover"],
                              help="Trade action")
    trade_parser.add_argument("--symbol", required=True, help="Trading symbol")
    trade_parser.add_argument("--price", type=float, required=True,
                              help="Execution price (0 for auto-quote)")
    trade_parser.add_argument("--quantity", type=float, required=True,
                              help="Position size")
    trade_parser.add_argument("--content", help="Optional notes")
    trade_parser.add_argument("--executed-at", default="now",
                              help='ISO 8601 timestamp or "now" (default: now)')

    # heartbeat
    sub.add_parser("heartbeat", help="Send heartbeat")

    # strategy
    strat_parser = sub.add_parser("strategy", help="Publish a strategy signal")
    strat_parser.add_argument("--market", required=True,
                              choices=["us-stock", "crypto", "polymarket"],
                              help="Market")
    strat_parser.add_argument("--title", required=True, help="Strategy title")
    strat_parser.add_argument("--content", required=True, help="Strategy content/thesis")
    strat_parser.add_argument("--symbols", help="Comma-separated symbols (e.g. AAPL,TSLA)")
    strat_parser.add_argument("--tags", help="Comma-separated tags")

    # discussion
    disc_parser = sub.add_parser("discussion", help="Publish a discussion signal")
    disc_parser.add_argument("--title", required=True, help="Discussion title")
    disc_parser.add_argument("--content", required=True, help="Discussion content")
    disc_parser.add_argument("--tags", help="Comma-separated tags")

    # feed
    feed_parser = sub.add_parser("feed", help="Browse signal feed")
    feed_parser.add_argument("--limit", type=int, default=10, help="Max signals")
    feed_parser.add_argument("--type", dest="type", help="Filter: realtime, strategy, discussion")
    feed_parser.add_argument("--symbol", help="Filter by symbol")
    feed_parser.add_argument("--keyword", help="Search keyword")
    feed_parser.add_argument("--sort", default="new", choices=["new", "active", "following"],
                             help="Sort order")

    # rebalance
    rebal_parser = sub.add_parser("rebalance", help="Analyze positions for rebalancing")
    rebal_parser.add_argument("--json", action="store_true", help="Output full JSON")

    return parser


def main() -> None:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args()

    command_map = {
        "status": _cmd_status,
        "positions": _cmd_positions,
        "trade": _cmd_trade,
        "heartbeat": _cmd_heartbeat,
        "strategy": _cmd_strategy,
        "discussion": _cmd_discussion,
        "feed": _cmd_feed,
        "rebalance": _cmd_rebalance,
    }

    handler = command_map.get(args.command)
    if handler:
        handler(args)


if __name__ == "__main__":
    main()
