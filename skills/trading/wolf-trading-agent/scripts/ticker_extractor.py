#!/usr/bin/env python3
"""Ticker symbol extractor — pulls stock symbols from text using regex and a known-company whitelist."""

import re
import json
import os

# Path to known tickers CSV (NYSE, NASDAQ top ~2000)
TICKERS_CACHE = os.path.join(os.path.dirname(__file__), "..", "data", "tickers_cache.json")

# Common false positives — words that look like tickers but aren't
FALSE_POSITIVES = {
    "A", "I", "E", "O", "Y", "GO", "TO", "BE", "SO", "WE", "ME", "HE", "NO",
    "OR", "AN", "IT", "AT", "IN", "ON", "IS", "AM", "UP", "DO", "IF", "HI", "OK",
    "DD", "CEO", "CFO", "IPO", "ETF", "API", "AI", "ML", "VR", "AR", "ROI",
    "USD", "GDP", "CPI", "EPS", "PE", "PM", "AM", "YOLO", "LOL", "FOMO",
    "USA", "UK", "EU", "IMO", "TLDR", "EDIT", "PS", "OP",
    "ALL", "CAN", "FOR", "HAS", "NOW", "NEW", "ONE", "OUT", "THE", "TOP",
    "RH", "TD", "WSB", "IRL", "BTFD", "ATH",
}

# Known large-cap companies (ticker -> [aliases])
KNOWN_TICKERS = {
    "AAPL": ["apple"],
    "MSFT": ["microsoft"],
    "GOOGL": ["google", "alphabet"],
    "AMZN": ["amazon"],
    "NVDA": ["nvidia"],
    "META": ["meta", "facebook"],
    "TSLA": ["tesla"],
    "BRK.B": ["berkshire", "buffett"],
    "JPM": ["jpmorgan", "jpm"],
    "V": ["visa"],
    "JNJ": ["johnson"],
    "WMT": ["walmart"],
    "MA": ["mastercard"],
    "PG": ["procter", "pg"],
    "UNH": ["unitedhealth"],
    "HD": ["home depot"],
    "BAC": ["bank of america"],
    "DIS": ["disney"],
    "ADBE": ["adobe"],
    "NFLX": ["netflix"],
    "CRM": ["salesforce"],
    "AMD": ["amd"],
    "INTC": ["intel"],
    "PYPL": ["paypal"],
    "UBER": ["uber"],
    "SQ": ["block", "square"],
    "SNAP": ["snapchat"],
    "PLTR": ["palantir"],
    "RBLX": ["roblox"],
    "COIN": ["coinbase"],
    "GME": ["gamestop"],
    "AMC": ["amc"],
    "BB": ["blackberry"],
    "RIVN": ["rivian"],
    "LCID": ["lucid"],
    "NIO": ["nio"],
    "SOFI": ["sofi"],
    "HOOD": ["robinhood"],
    "RDDT": ["reddit"],
    "SPY": ["spy", "spdr"],
    "QQQ": ["qqq", "nasdaq etf"],
    "IWM": ["russell"],
    "DIA": ["dow etf"],
    "TLT": ["bond etf", "treasury etf"],
    "GLD": ["gold etf"],
    "SLV": ["silver etf"],
    "USO": ["oil etf"],
    "UNG": ["nat gas etf"],
    "VIX": ["vix", "volatility"],
    "SHEL": ["shell"],
    "BP": ["bp"],
    "XOM": ["exxon"],
    "CVX": ["chevron"],
    "OXY": ["occidental"],
    "MRNA": ["moderna"],
    "PFE": ["pfizer"],
    "BA": ["boeing"],
    "LMT": ["lockheed"],
    "RTX": ["raytheon"],
    "NOC": ["northrop"],
    "CAT": ["caterpillar"],
    "DE": ["deere"],
    "F": ["ford"],
    "GM": ["general motors"],
    "TM": ["toyota"],
    "TMUS": ["t-mobile", "tmobile"],
    "T": ["at&t"],
    "VZ": ["verizon"],
    "KO": ["coca-cola"],
    "PEP": ["pepsi"],
    "MCD": ["mcdonalds"],
    "SBUX": ["starbucks"],
    "NKE": ["nike"],
    "COST": ["costco"],
    "TGT": ["target"],
    "LOW": ["lowes"],
    "SHOP": ["shopify"],
    "SPOT": ["spotify"],
    "ABNB": ["airbnb"],
    "DKNG": ["draftkings"],
    "CRWD": ["crowdstrike"],
    "ZS": ["zscaler"],
    "NET": ["cloudflare"],
    "SNOW": ["snowflake"],
    "DDOG": ["datadog"],
    "MDB": ["mongodb"],
    "U": ["unity"],
    "TTD": ["trade desk"],
    "AFRM": ["affirm"],
    "UPST": ["upstart"],
    "MSTR": ["microstrategy"],
    "RIOT": ["riot"],
    "MARA": ["marathon"],
    "CLSK": ["cleanspark"],
    "SMCI": ["supermicro", "smci"],
    "ARM": ["arm"],
    "ASTS": ["ast spacemobile", "ast"],
    "RKLB": ["rocket lab"],
    "LUNR": ["intuitive machines"],
    "IONQ": ["ionq"],
    "QBTS": ["d-wave"],
    "RGTI": ["rigetti"],
}

# Build reverse index: lowercase name -> ticker
def _build_name_index():
    idx = {}
    for ticker, names in KNOWN_TICKERS.items():
        for name in names:
            idx[name.lower()] = ticker
    return idx

NAME_TO_TICKER = _build_name_index()


def extract_tickers(text: str) -> list[dict]:
    """Extract ticker symbols from text. Returns [{"ticker": "AAPL", "mentions": 3, "source": "reddit"}, ...]"""
    tickers = {}
    text_lower = text.lower()

    # Pass 1: $TICKER format (cashtags)
    cashtags = re.findall(r'\$([A-Z]{1,5})\b', text)
    for t in cashtags:
        if t.upper() not in FALSE_POSITIVES:
            tickers[t.upper()] = tickers.get(t.upper(), 0) + 1

    # Pass 2: TICKER format (ALL CAPS 1-5 chars, word boundary)
    raw_tickers = re.findall(r'\b([A-Z]{1,5})\b', text)
    for t in raw_tickers:
        if t not in FALSE_POSITIVES and t in KNOWN_TICKERS:
            tickers[t] = tickers.get(t, 0) + 1

    # Pass 3: Company name matching
    for name_lower, ticker in NAME_TO_TICKER.items():
        count = len(re.findall(r'\b' + re.escape(name_lower) + r'\b', text_lower))
        if count > 0:
            tickers[ticker] = tickers.get(ticker, 0) + count

    return [{"ticker": k, "mentions": v} for k, v in sorted(tickers.items(), key=lambda x: -x[1])]


def get_company_name(ticker: str) -> str:
    """Get company name for a ticker, or return ticker if unknown."""
    names = KNOWN_TICKERS.get(ticker.upper(), [])
    if names:
        return names[0].title()
    return ticker.upper()


def sentiment_score(text: str) -> float:
    """Simple lexicon-based sentiment. Returns -1.0 to 1.0."""
    bullish = [
        "bullish", "moon", "rocket", "pump", "long", "buy", "calls", "green",
        "beat", "upgrade", "buyout", "breakout", "squeeze", "gamma", "yolo",
        "strong buy", "outperform", "overweight", "undervalued", "dip buy",
        "loading up", "accumulating", "doubling down", "to the moon",
        "diamond hands", "tendies", "gains", "winning", "crushing",
        "exploding", "surging", "ripping", "flying", "booming",
    ]
    bearish = [
        "bearish", "crash", "dump", "short", "sell", "puts", "red",
        "miss", "downgrade", "bankruptcy", "dilution", "rug pull",
        "weak", "underperform", "underweight", "overvalued", "bag holder",
        "paper hands", "loss porn", "bleeding", "tanking", "plummeting",
        "collapsing", "freefall", "dead cat", "bagholder", "rekt",
    ]
    text_lower = text.lower()
    score = 0.0
    for word in bullish:
        score += text_lower.count(word) * 0.1
    for word in bearish:
        score -= text_lower.count(word) * 0.1
    return max(-1.0, min(1.0, score))
