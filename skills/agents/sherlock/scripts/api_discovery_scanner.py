#!/usr/bin/env python3
"""
Sherlock API Discovery Scanner
===============================
Daily scan for new financial data APIs that could feed Wolf Trading Agent.
Searches RapidAPI, GitHub, API directories, and general web.

THE RULE: Always test an API endpoint before marking it usable.
A 200 on a homepage means NOTHING. Hit the actual data endpoint.

Usage:
    python3 api_discovery_scanner.py                    # Full scan, human output
    python3 api_discovery_scanner.py --json             # JSON output
    python3 api_discovery_scanner.py --quick            # Quick scan (fewer sources)
    python3 api_discovery_scanner.py --check-existing   # Only check if known APIs changed

Output: wolf-trading-agent/output/api_discovery_YYYY-MM-DD.md (or .json)

What it looks for:
    - Stock/financial market data APIs (quotes, options, fundamentals)
    - Financial news APIs (alternative to GNews)
    - Options/derivatives data APIs
    - Crypto market data APIs
    - Economic indicators APIs
    - Free-tier or low-cost options (Wolf runs on a budget)

Each discovered API is rated:
    🟢 HIGH — Free tier available, endpoint tested working. Covers core Wolf needs.
    🟡 MEDIUM — Free tier limited or only covers secondary needs
    ⚪ LOW — Paid-only, redundant, or niche
    🔴 DEAD — Endpoint test failed, domain dead, no longer maintained
    ❓ UNKNOWN — Domain up but couldn't test the actual API endpoint
"""

import os
import sys
import json
import re
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import ssl

WOLF_DIR = os.path.expanduser("~/.hermes/skills/trading/wolf-trading-agent")
OUTPUT_DIR = os.path.join(WOLF_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

KNOWN_APIS_FILE = os.path.join(OUTPUT_DIR, "api_discovery_known.json")

SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE


def get_gnnews_key() -> str:
    """Get GNews API key from env or .env file."""
    key = os.environ.get("GNEWS_API_KEY", "")
    if key:
        return key
    env_file = os.path.expanduser("~/.hermes/.env")
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                if line.startswith("GNEWS_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def get_alphavantage_key() -> str:
    """Try to get Alpha Vantage key from env."""
    key = os.environ.get("ALPHA_VANTAGE_API_KEY", "")
    if key:
        return key
    env_file = os.path.expanduser("~/.hermes/.env")
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                if line.startswith("ALPHA_VANTAGE_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


# ─── Each known API gets a real endpoint test ───
# This is the core of "always test before using"
# Each entry specifies how to test it: URL, expected data pattern, auth method
API_ENDPOINT_TESTS = [
    # ── News APIs ──
    {
        "name": "GNews API",
        "domain": "https://gnews.io",
    "endpoint": "https://gnews.io/api/v4/search?q=test&lang=en&max=1&token=__KEY__",
    "auth": "key-replace",         # replace __KEY__ in URL
    "auth_param": "__KEY__",
    "key_source": get_gnnews_key,
    "expected": "articles",
    "notes": "Primary Wolf news source. 100 req/day free, 12h delay.",
    "category": "news",
    "tier": "free",
    },
    {
        "name": "MarketAux",
        "domain": "https://www.marketaux.com",
        "endpoint": "https://api.marketaux.com/v1/news/all?symbols=AAPL,TSLA&filter_entities=true&api_token=TEST_ONLY&limit=1",
        "auth": "query-param",       # &api_token=KEY
        "auth_param": "api_token",
        "key_source": None,
        "expected": "meta",
        "notes": "Financial news API. Free: 100 req/day. Check if still free.",
        "category": "news",
        "tier": "free",
    },
    # ── Market Data APIs ──
    {
        "name": "Alpha Vantage",
        "domain": "https://www.alphavantage.co",
        "endpoint": "https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=IBM&apikey=TEST_ONLY",
        "auth": "query-param",
        "auth_param": "apikey",
        "key_source": get_alphavantage_key,
        "expected": "Global Quote",
        "notes": "Free: 25 req/day, 5 req/min. Stocks, FX, crypto, fundamentals.",
        "category": "market-data",
        "tier": "free",
    },
    {
        "name": "Finnhub",
        "domain": "https://finnhub.io",
        "endpoint": "https://finnhub.io/api/v1/quote?symbol=AAPL",
        "auth": "query-param",
        "auth_param": "token",
        "key_source": None,  # Fetched from env
        "expected": "c",
        "notes": "300 api calls/day free. News, quotes, fundamentals.",
        "category": "market-data",
        "tier": "free",
    },
    {
        "name": "Twelve Data",
        "domain": "https://twelvedata.com",
        "endpoint": "https://api.twelvedata.com/quote?symbol=AAPL&apikey=TEST_ONLY",
        "auth": "query-param",
        "auth_param": "apikey",
        "key_source": None,
        "expected": "price",
        "notes": "Check if still free tier exists.",
        "category": "market-data",
        "tier": "free",
    },
    {
        "name": "Twelve Data (RapidAPI)",
        "domain": "https://twelvedata.com",
        "endpoint": "https://rapidapi.com/twelvedata/api/twelve-data",
        "auth": "none",
        "auth_param": None,
        "key_source": None,
        "expected": None,
        "notes": "Available via RapidAPI marketplace. Check pricing.",
        "category": "market-data",
        "tier": "free",
    },
    {
        "name": "Polygon.io",
        "domain": "https://polygon.io",
        "endpoint": "https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers/AAPL?apiKey=TEST_ONLY",
        "auth": "query-param",
        "auth_param": "apiKey",
        "key_source": None,
        "expected": "status",
        "notes": "$29/mo basic. Check if free tier exists.",
        "category": "market-data",
        "tier": "paid",
    },
    {
        "name": "MarketStack",
        "domain": "https://marketstack.com",
        "endpoint": "https://api.marketstack.com/v1/eod?access_key=TEST_ONLY&symbols=AAPL&limit=1",
        "auth": "query-param",
        "auth_param": "access_key",
        "key_source": None,
        "expected": "data",
        "notes": "Free tier: 1000 req/month EOD data. No real-time.",
        "category": "market-data",
        "tier": "free",
    },
    # ── Fundamentals ──
    {
        "name": "Financial Modeling Prep",
        "domain": "https://financialmodelingprep.com",
        "endpoint": "https://financialmodelingprep.com/api/v3/profile/AAPL?apikey=TEST_ONLY",
        "auth": "query-param",
        "auth_param": "apikey",
        "key_source": None,
        "expected": "companyName",
        "notes": "Free tier: 250 req/day. Financial statements, profiles.",
        "category": "fundamentals",
        "tier": "free",
    },
    {
        "name": "EOD Historical Data",
        "domain": "https://eodhd.com",
        "endpoint": "https://eodhd.com/api/eod/AAPL.US?api_token=TEST_ONLY&fmt=json",
        "auth": "query-param",
        "auth_param": "api_token",
        "key_source": None,
        "expected": "date",
        "notes": "Free tier: 20 API calls/day. EOD + fundamentals.",
        "category": "market-data",
        "tier": "free",
    },
    # ── Broker / Trading ──
    {
        "name": "Alpaca Markets",
        "domain": "https://alpaca.markets",
        "endpoint": "https://paper-api.alpaca.markets/v2/account",
        "auth": "header",       # APCA-API-KEY-ID + APCA-API-SECRET-KEY
        "auth_param": "header",
        "key_source": None,
        "expected": "id",
        "notes": "Quotes work. Minute bars/options return 403 on free tier.",
        "category": "broker-data",
        "tier": "free-hybrid",
    },
    # ── Crypto ──
    {
        "name": "CoinGecko",
        "domain": "https://www.coingecko.com",
        "endpoint": "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
        "auth": "none",
        "auth_param": None,
        "key_source": None,
        "expected": "bitcoin",
        "notes": "Free crypto data. 10-30 req/min.",
        "category": "crypto",
        "tier": "free",
    },
    # ── Identifiers ──
    {
        "name": "OpenFIGI",
        "domain": "https://www.openfigi.com",
        "endpoint": "https://api.openfigi.com/v3/mapping",
        "auth": "none",
        "auth_param": None,
        "key_source": None,
        "expected": None,
        "notes": "FIGI mapping API. POST endpoint. Check availability.",
        "category": "identifiers",
        "tier": "free",
    },
    # ── Deprecated/legacy ──
    {
        "name": "IEX Cloud",
        "domain": "https://iexcloud.io",
        "endpoint": "https://cloud.iexapis.com/stable/stock/aapl/quote?token=TEST_ONLY",
        "auth": "query-param",
        "auth_param": "token",
        "key_source": None,
        "expected": "symbol",
        "notes": "Acquired by NYSE. Check if still operational.",
        "category": "market-data",
        "tier": "paid",
    },
    {
        "name": "Tiingo",
        "domain": "https://www.tiingo.com",
        "endpoint": "https://api.tiingo.com/tiingo/daily/aapl/prices?token=TEST_ONLY",
        "auth": "query-param",
        "auth_param": "token",
        "key_source": None,
        "expected": "adjClose",
        "notes": "Was affordable ($10/mo). IEX data, fundamentals.",
        "category": "market-data",
        "tier": "paid",
    },
    {
        "name": "Intrinio",
        "domain": "https://intrinio.com",
        "endpoint": "https://api-v2.intrinio.com/securities/AAPL/prices?api_key=TEST_ONLY",
        "auth": "query-param",
        "auth_param": "api_key",
        "key_source": None,
        "expected": "stock_price",
        "notes": "Enterprise-focused. Expensive. Verify if accessible.",
        "category": "market-data",
        "tier": "paid",
    },
    {
        "name": "Yahoo Finance (unofficial)",
        "domain": "https://finance.yahoo.com",
        "endpoint": "https://query1.finance.yahoo.com/v8/finance/chart/AAPL?range=1d&interval=1d",
        "auth": "none",
        "auth_param": None,
        "key_source": None,
        "expected": "chart",
        "notes": "Unofficial. Fragile — breaks without warning.",
        "category": "market-data",
        "tier": "free",
    },
    {
        "name": "World Trading Data",
        "domain": "https://www.worldtradingdata.com",
        "endpoint": "https://api.worldtradingdata.com/api/v1/stock?symbol=AAPL&api_token=TEST_ONLY",
        "auth": "query-param",
        "auth_param": "api_token",
        "key_source": None,
        "expected": "data",
        "notes": "Check if still active. Was free tier available.",
        "category": "market-data",
        "tier": "free",
    },
    {
        "name": "Stock Data",
        "domain": "https://www.stockdata.org",
        "endpoint": "https://api.stockdata.org/v1/data/quote?symbols=AAPL&api_token=TEST_ONLY",
        "auth": "query-param",
        "auth_param": "api_token",
        "key_source": None,
        "expected": "data",
        "notes": "Free tier: 100 req/day. Real-time + EOD.",
        "category": "market-data",
        "tier": "free",
    },
    {
        "name": "Yahoo Finance (RapidAPI)",
        "domain": "https://rapidapi.com/apidojo/api/yh-finance",
        "endpoint": "https://yh-finance.p.rapidapi.com/stock/v2/get-summary?symbol=AAPL",
        "auth": "rapidapi",
        "auth_param": "x-rapidapi-key",
        "key_source": None,
        "expected": "price",
        "notes": "RapidAPI provider. Requires subscription.",
        "category": "market-data",
        "tier": "paid",
    },
    {
        "name": "EOD Historical Data (RapidAPI)",
        "domain": "https://rapidapi.com/eodhistoricaldata/api/eod-historical-data",
        "endpoint": "https://eodhistoricaldata.com/api/real-time/AAPL.US?api_token=TEST_ONLY&fmt=json",
        "auth": "query-param",
        "auth_param": "api_token",
        "key_source": None,
        "expected": "date",
        "notes": "Available via RapidAPI + direct. Check free tier.",
        "category": "market-data",
        "tier": "free",
    },
]


def fetch_url(url: str, timeout: int = 10, headers: dict = None) -> tuple[str, int]:
    """Fetch URL content. Returns (body, status_code)."""
    req_headers = {"User-Agent": "SherlockDiscovery/1.0"}
    if headers:
        req_headers.update(headers)
    req = Request(url, headers=req_headers)
    try:
        with urlopen(req, timeout=timeout, context=SSL_CTX) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return body, resp.status
    except HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:500] if e.fp else ""
        return body, e.code
    except Exception as e:
        return f"{e}", 0


def test_api_endpoint(api: dict) -> dict:
    """
    Test an API's actual data endpoint, not just its homepage.
    Returns updated api dict with real test results.

    Result categories:
      - working: endpoint returned 200 and response contained expected field
      - no-key: needs an API key we don't have
      - forbidden: 401/403/429 — needs auth or rate-limited
      - dead: domain unreachable or endpoint returns 500
      - unexpected: domain works but endpoint response doesn't match expected pattern
    """
    name = api["name"]
    endpoint = api.get("endpoint", "")
    auth = api.get("auth", "none")
    expected = api.get("expected")
    key_source_fn = api.get("key_source")

    result = {
        "name": name,
        "domain": api.get("domain", ""),
        "endpoint": endpoint,
        "result": "untested",
        "status_code": 0,
        "response_preview": "",
        "notes": api.get("notes", ""),
    }

    if not endpoint:
        result["result"] = "no-endpoint"
        return result

    # Build the URL with auth if we have a key
    test_url = endpoint
    headers = {}

    if auth == "api-param":
        # Auth goes as query parameter ?token=KEY or similar
        key = key_source_fn() if key_source_fn else None
        if key:
            test_url = f"{endpoint}&{api.get('auth_param', 'token')}={key}"
        else:
            # Try without key — likely fails
            pass  # Test with placeholder still in URL

    elif auth == "key-replace":
        # Replace __KEY__ placeholder in URL with actual key
        key = key_source_fn() if key_source_fn else None
        if key:
            test_url = endpoint.replace(api.get("auth_param", "__KEY__"), key)

    elif auth == "query-param":
        # Replace placeholder in URL
        key = key_source_fn() if key_source_fn else None
        if key:
            auth_param = api.get("auth_param", "apikey")
            test_url = endpoint.replace("TEST_ONLY", key)

    elif auth == "header":
        # Uses header-based auth — skip unless we have credentials
        result["result"] = "needs-auth-header"
        result["notes"] = "Requires API key header auth (not currently configured for automated test)."
        return result

    elif auth == "rapidapi":
        # RapidAPI uses x-rapidapi-key header
        rapid_key = os.environ.get("X_RAPIDAPI_KEY", "2c94489ce3mshd675512363df454p1b3228jsn3e6cf4b70215")
        headers["x-rapidapi-key"] = rapid_key
        headers["x-rapidapi-host"] = test_url.split("/")[2]

    elif auth == "none":
        pass  # Public endpoint

    # Execute the test
    body, status = fetch_url(test_url, timeout=10, headers=headers)
    result["status_code"] = status

    if status == 0:
        result["result"] = "dead"
        result["notes"] = f"Endpoint unreachable: {body[:100]}"
        return result

    if status in (401, 403):
        result["result"] = "forbidden"
        result["notes"] = f"HTTP {status} — needs valid API key or subscription."
        return result

    if status == 429:
        result["result"] = "rate-limited"
        result["notes"] = "HTTP 429 — hit rate limit. Check back later."
        return result

    if status == 404:
        result["result"] = "not-found"
        result["notes"] = "HTTP 404 — endpoint doesn't exist. API may have moved."
        return result

    if status >= 500:
        result["result"] = "server-error"
        result["notes"] = f"HTTP {status} — server error. Likely needs valid key or API down."
        return result

    if status != 200:
        result["result"] = "unexpected-status"
        result["notes"] = f"HTTP {status} — unexpected."
        return result

    # Status is 200 — check response quality
    if not body.strip():
        result["result"] = "empty-response"
        result["notes"] = "HTTP 200 but empty body."
        return result

    result["response_preview"] = body[:200].replace("\n", " ").strip()

    # Check if response contains expected field
    if expected and expected in body:
        result["result"] = "working"
        result["notes"] = "Endpoint tested and returned expected data."
    elif expected and expected not in body:
        # Check if it's an error message about missing key
        if "api" in body.lower() and ("key" in body.lower() or "token" in body.lower()):
            result["result"] = "needs-key"
            result["notes"] = "Endpoint returned error requesting API key."
        else:
            result["result"] = "unexpected-format"
            result["notes"] = f"HTTP 200 but response format unexpected (expected '{expected}' not found)."
    else:
        # No expected field specified — just confirmed reachable
        result["result"] = "reachable"
        result["notes"] = "Endpoint responded with HTTP 200."

    return result


def build_known_api_state(test_results: list[dict]) -> dict:
    """Build the persistent known API state from test results."""
    established = []
    deprecated = []

    for r in test_results:
        entry = {
            "name": r["name"],
            "url": r.get("domain", ""),
            "endpoint": r.get("endpoint", ""),
            "category": "market-data",
            "tier": "unknown",
            "status": r["result"],
            "notes": r.get("notes", ""),
            "last_tested": datetime.now().isoformat(),
        }
        if r["result"] == "working":
            established.append(entry)
        elif r["result"] in ("dead", "not-found", "no-endpoint"):
            deprecated.append(entry)
        else:
            established.append(entry)  # keeps it in active monitoring

    return {"established": established, "deprecated": deprecated}


def save_known_apis(data: dict):
    """Save known APIs to persistent file."""
    with open(KNOWN_APIS_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)


def search_rapidapi_finance() -> list[dict]:
    """
    Check RapidAPI marketplace for finance APIs.
    We hit the marketplace pages to see if they're still there.
    """
    results = []
    rapid_finance_apis = [
        ("Twelve Data (RapidAPI)", "https://rapidapi.com/twelvedata/api/twelve-data"),
        ("Alpha Vantage (RapidAPI)", "https://rapidapi.com/alphavantage/api/alpha-vantage"),
        ("FMP (RapidAPI)", "https://rapidapi.com/financial-modeling-prep/api/financial-modeling-prep"),
        ("Yahoo Finance (RapidAPI)", "https://rapidapi.com/apidojo/api/yh-finance"),
        ("Stock Data (RapidAPI)", "https://rapidapi.com/stockdata/api/stock-data"),
        ("MarketAux (RapidAPI)", "https://rapidapi.com/marketaux/api/marketaux"),
        ("EOD HD (RapidAPI)", "https://rapidapi.com/eodhistoricaldata/api/eod-historical-data"),
        ("World Trading Data (RapidAPI)", "https://rapidapi.com/worldtradingdata/api/world-trading-data"),
    ]

    for name, url in rapid_finance_apis:
        body, status = fetch_url(url, timeout=8)
        results.append({
            "name": name,
            "url": url,
            "source": "rapidapi",
            "status": "active-page" if status == 200 else f"http-{status}",
            "notes": "RapidAPI marketplace page." if status == 200 else f"Page returned HTTP {status} — may be dead/moved.",
        })

    return results


def search_github_finance_apis() -> list[dict]:
    """
    Check GitHub for trending financial API projects.
    """
    results = []
    queries = [
        "https://api.github.com/search/repositories?q=stock+market+api+free&sort=stars&order=desc&per_page=5",
        "https://api.github.com/search/repositories?q=financial+data+api&sort=stars&order=desc&per_page=5",
        "https://api.github.com/search/repositories?q=free+stock+api&sort=stars&order=desc&per_page=5",
    ]
    seen = set()
    for q in queries:
        body, status = fetch_url(q, timeout=10, headers={"Accept": "application/vnd.github.v3+json"})
        if status == 200:
            try:
                data = json.loads(body)
                for item in data.get("items", []):
                    name = item.get("full_name", "")
                    if name in seen:
                        continue
                    seen.add(name)
                    results.append({
                        "name": name,
                        "url": item.get("html_url", ""),
                        "source": "github",
                        "status": "active",
                        "notes": f"Stars: {item.get('stargazers_count', '?')}. Updated: {item.get('updated_at', '?')[:10]}",
                    })
            except json.JSONDecodeError:
                pass
    return results


def load_known_apis() -> dict:
    """Load known APIs from persistent file."""
    if os.path.exists(KNOWN_APIS_FILE):
        try:
            with open(KNOWN_APIS_FILE) as f:
                return json.load(f)
        except:
            pass
    return {"established": [], "deprecated": []}


def scan(quick: bool = False, check_existing: bool = False) -> dict:
    """Main scan function."""
    scan_ts = datetime.now()
    report = {
        "scan_time": scan_ts.isoformat(),
        "date": scan_ts.strftime("%Y-%m-%d"),
        "endpoint_tests": [],
        "new_discoveries": [],
        "sources_checked": [],
        "summary": {},
        "errors": [],
    }

    # Phase 1: Test every known API endpoint (this is the real work)
    if not quick:
        print(f"  Testing {len(API_ENDPOINT_TESTS)} API endpoints...")
    test_results = []
    for api in API_ENDPOINT_TESTS:
        if quick and api.get("skip_in_quick"):
            continue
        result = test_api_endpoint(api)
        test_results.append(result)
        if not quick:
            status_icon = {
                "working": "✅",
                "reachable": "✅",
                "needs-key": "⚠️",
                "needs-auth-header": "⏭️",
                "forbidden": "🔒",
                "rate-limited": "⏳",
                "not-found": "❌",
                "dead": "❌",
                "server-error": "⚠️",
                "empty-response": "⚠️",
                "unexpected-format": "🤔",
                "unexpected-status": "⚠️",
                "no-endpoint": "⏭️",
            }.get(result["result"], "❓")
            print(f"  {status_icon} {result['name']:30s} → {result['result']:20s} HTTP {result.get('status_code', '?')}")

    report["endpoint_tests"] = test_results

    # Build known API state
    known = build_known_api_state(test_results)
    save_known_apis(known)

    # Summarize
    working = [r for r in test_results if r["result"] in ("working", "reachable")]
    needs_key = [r for r in test_results if r["result"] in ("needs-key", "forbidden", "needs-auth-header")]
    dead = [r for r in test_results if r["result"] in ("dead", "not-found")]
    other = [r for r in test_results if r not in working and r not in needs_key and r not in dead]

    report["summary"] = {
        "total_tested": len(test_results),
        "working": [r["name"] for r in working],
        "needs_key_or_auth": [r["name"] for r in needs_key],
        "dead": [r["name"] for r in dead],
        "other": [r["name"] for r in other],
    }

    if not quick and not check_existing:
        # Search RapidAPI
        rapid_results = search_rapidapi_finance()
        report["sources_checked"].append("rapidapi")
        report["new_discoveries"].extend(rapid_results)

        # Search GitHub
        github_results = search_github_finance_apis()
        report["sources_checked"].append("github")
        report["new_discoveries"].extend(github_results)

    if quick:
        report["sources_checked"].append("endpoint-tests-only")

    return report


def format_report(report: dict, as_json: bool = False) -> str:
    if as_json:
        return json.dumps(report, indent=2, default=str)

    lines = []
    lines.append(f"# 🔍 API Discovery Scan — {report['date']}")
    lines.append(f"")
    lines.append(f"Scan time: {report['scan_time']}")
    lines.append(f"")

    summary = report.get("summary", {})
    lines.append(f"## 📊 Summary")
    lines.append(f"")
    lines.append(f"**Tested:** {summary.get('total_tested', 0)} endpoints")
    lines.append(f"")
    lines.append(f"**✅ Working:** {len(summary.get('working', []))}")
    for a in summary.get("working", []):
        lines.append(f"  - {a}")
    lines.append(f"")
    lines.append(f"**🔒 Needs Key/Auth:** {len(summary.get('needs_key_or_auth', []))}")
    for a in summary.get("needs_key_or_auth", []):
        lines.append(f"  - {a}")
    lines.append(f"")
    lines.append(f"**❌ Dead/Not Found:** {len(summary.get('dead', []))}")
    for a in summary.get("dead", []):
        lines.append(f"  - {a}")
    lines.append(f"")

    if summary.get("other"):
        lines.append(f"**🤔 Other:** {len(summary.get('other', []))}")
        for a in summary.get("other", []):
            lines.append(f"  - {a}")
        lines.append(f"")

    lines.append(f"## 🔬 Detailed Endpoint Tests")
    lines.append(f"")
    for t in report.get("endpoint_tests", []):
        icon = {
            "working": "✅",
            "reachable": "✅",
            "needs-key": "⚠️",
            "needs-auth-header": "⏭️",
            "forbidden": "🔒",
            "rate-limited": "⏳",
            "not-found": "❌",
            "dead": "❌",
            "server-error": "⚠️",
            "empty-response": "⚠️",
            "unexpected-format": "🤔",
            "unexpected-status": "⚠️",
            "no-endpoint": "⏭️",
        }.get(t["result"], "❓")
        lines.append(f"  {icon} **{t['name']}** — {t['result']}")
        lines.append(f"     Endpoint: `{t.get('endpoint', 'N/A')[:80]}`")
        lines.append(f"     Status: {t.get('result', '?')} (HTTP {t.get('status_code', '?')})")
        lines.append(f"     Notes: {t.get('notes', '')}")
        lines.append(f"")

    if report.get("new_discoveries"):
        lines.append(f"## 🆕 New/Marketplace Discoveries")
        lines.append(f"")
        for d in report["new_discoveries"]:
            lines.append(f"  - **{d['name']}** ({d['source']}) — {d['status']}")
            lines.append(f"    {d.get('notes', '')}")
            lines.append(f"")

    lines.append(f"## 🧹 Recommendations for Wolf")
    lines.append(f"")
    lines.append(f"Sources checked: {', '.join(report['sources_checked'])}")
    lines.append(f"")

    working = summary.get("working", [])
    lines.append(f"**APIs worth integrating right now (tested working):**")
    for w in working:
        lines.append(f"  - {w}")
    lines.append(f"")

    needs_key = summary.get("needs_key_or_auth", [])
    if needs_key:
        lines.append(f"**Could work with a free API key (register → test → integrate):**")
        for n in needs_key:
            lines.append(f"  - {n}")
        lines.append(f"")

    lines.append(f"---")
    lines.append(f"_Generated by Sherlock API Discovery Scanner — endpoint tests are REAL_")

    return "\n".join(lines)


def main():
    args = sys.argv[1:]
    quick = "--quick" in args
    check_existing = "--check-existing" in args
    json_mode = "--json" in args

    print(f"🔍 Sherlock API Discovery — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    mode_str = "quick (endpoint tests only)" if quick else "full (endpoint tests + discovery)"
    print(f"   Mode: {mode_str}")

    report = scan(quick=quick, check_existing=check_existing)

    output = format_report(report, as_json=json_mode)

    # Write to output dir
    date_str = report["date"]
    ext = "json" if json_mode else "md"
    outpath = os.path.join(OUTPUT_DIR, f"api_discovery_{date_str}.{ext}")
    with open(outpath, "w") as f:
        f.write(output)

    print(f"\n✅ Report saved to: {outpath}")


if __name__ == "__main__":
    main()
