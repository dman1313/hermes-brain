#!/usr/bin/env python3
"""
🐺 WOLF DAILY BRIEF — Google Docs Newsletter Generator

Creates a beautifully formatted daily trading brief as a Google Doc.
Reads Wolf scan output (JSON) + spread suggestions and renders a polished document.

Requirements:
  - Google OAuth token with documents + drive.file scopes
  - google-api-python-client, google-auth packages

Usage:
  python3 wolf_newsletter.py --scan /tmp/wolf_scan.json --spreads /tmp/wolf_spreads.json
"""

import argparse
import ast
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ── Constants ──────────────────────────────────────────────────────────

HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
TOKEN_PATH = HERMES_HOME / "google_token.json"
CLIENT_SECRET_PATH = HERMES_HOME / "google_client_secret.json"

REQUIRED_SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive.file",
]

# Brand colors
COLOR_WOLF_DARK = {"red": 0.13, "green": 0.13, "blue": 0.15}    # #222226
COLOR_GREEN = {"red": 0.13, "green": 0.63, "blue": 0.39}          # #22A163
COLOR_RED = {"red": 0.85, "green": 0.20, "blue": 0.20}            # #D93333
COLOR_YELLOW = {"red": 0.93, "green": 0.75, "blue": 0.18}         # #EEBF2E
COLOR_NEUTRAL = {"red": 0.55, "green": 0.55, "blue": 0.58}        # #8C8C94
COLOR_HEADER_BG = {"red": 0.09, "green": 0.09, "blue": 0.11}     # #17171C
COLOR_ACCENT = {"red": 0.26, "green": 0.52, "blue": 0.96}         # #4285F4


def get_credentials():
    """Load credentials, refreshing if needed. Exits with guidance if scopes are missing."""
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request

    if not TOKEN_PATH.exists():
        print("❌ No Google token found. Run Google Workspace setup first.", file=sys.stderr)
        sys.exit(1)

    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), REQUIRED_SCOPES)

    # Check for missing scopes
    granted = set()
    try:
        raw = json.loads(TOKEN_PATH.read_text())
        scopes_raw = raw.get("scopes") or raw.get("scope") or ""
        if isinstance(scopes_raw, str):
            granted = set(scopes_raw.split())
        else:
            granted = set(scopes_raw)
    except Exception:
        pass

    missing = [s for s in REQUIRED_SCOPES if s not in granted]
    if missing:
        print("⚠️  Google token is missing required scopes for Docs creation:", file=sys.stderr)
        for s in missing:
            print(f"   - {s}", file=sys.stderr)
        print("", file=sys.stderr)
        print("Fix: re-authenticate with the full scope set.", file=sys.stderr)
        print(f"   python3 {HERMES_HOME}/skills/productivity/google-workspace/scripts/setup.py --revoke", file=sys.stderr)
        print(f"   python3 {HERMES_HOME}/skills/productivity/google-workspace/scripts/setup.py --auth-url", file=sys.stderr)
        print("   (then complete the OAuth flow)", file=sys.stderr)
        sys.exit(1)

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN_PATH.write_text(creds.to_json())

    if not creds.valid:
        print("❌ Google token is invalid. Re-authenticate.", file=sys.stderr)
        sys.exit(1)

    return creds


def create_doc(title: str) -> str:
    """Create a new Google Doc and return its document ID."""
    from googleapiclient.discovery import build

    creds = get_credentials()
    docs_service = build("docs", "v1", credentials=creds)

    doc = docs_service.documents().create(body={"title": title}).execute()
    doc_id = doc["documentId"]
    print(f"📄 Created Google Doc: {title} (ID: {doc_id})")
    return doc_id


def build_requests(doc_id: str, data: dict) -> list:
    """Build all Google Docs API batchUpdate requests for the newsletter."""
    requests = []
    current_index = 1  # Track insertion position

    signals = data.get("signals", [])
    spreads = data.get("spreads", [])
    metadata = data.get("metadata", {})

    # ── Helper: insert text with style ──
    def add_text(text, style="NORMAL_TEXT", bold=False, fontSize=None, color=None, alignment=None):
        nonlocal current_index
        req = {
            "insertText": {
                "location": {"index": current_index},
                "text": text + "\n",
            }
        }
        requests.append(req)
        text_len = len(text) + 1

        # Style the inserted text
        style_req = {
            "updateTextStyle": {
                "range": {"startIndex": current_index, "endIndex": current_index + text_len},
                "textStyle": {"bold": bold},
                "fields": "bold",
            }
        }
        if fontSize:
            style_req["updateTextStyle"]["textStyle"]["fontSize"] = {"magnitude": fontSize, "unit": "PT"}
            style_req["updateTextStyle"]["fields"] += ",fontSize"
        if color:
            style_req["updateTextStyle"]["textStyle"]["foregroundColor"] = {"color": {"rgbColor": color}}
            style_req["updateTextStyle"]["fields"] += ",foregroundColor"
        requests.append(style_req)

        if alignment:
            requests.append({
                "updateParagraphStyle": {
                    "range": {"startIndex": current_index, "endIndex": current_index + text_len},
                    "paragraphStyle": {"alignment": alignment},
                    "fields": "alignment",
                }
            })

        current_index += text_len
        return current_index

    def add_horizontal_rule():
        nonlocal current_index
        requests.append({
            "insertText": {
                "location": {"index": current_index},
                "text": "\n",
            }
        })
        requests.append({
            "updateParagraphStyle": {
                "range": {"startIndex": current_index, "endIndex": current_index + 1},
                "paragraphStyle": {
                    "borderBetween": {
                        "color": {"color": {"rgbColor": COLOR_NEUTRAL}},
                        "width": {"magnitude": 1, "unit": "PT"},
                        "dashStyle": "SOLID",
                        "padding": {"magnitude": 4, "unit": "PT"},
                    },
                    "spaceBelow": {"magnitude": 10, "unit": "PT"},
                },
                "fields": "borderBetween,spaceBelow",
            }
        })
        current_index += 1

    # ═══════════════════════════════════════
    # DOCUMENT CONTENT
    # ═══════════════════════════════════════

    # ── Title ──
    add_text("🐺 WOLF DAILY TRADING BRIEF", fontSize=24, bold=True, color=COLOR_HEADER_BG, alignment="CENTER")
    now = datetime.now()
    date_str = now.strftime("%A, %B %d, %Y")
    add_text(date_str, fontSize=13, color=COLOR_NEUTRAL, alignment="CENTER")
    add_text("")

    # ── Market Overview ──
    add_text("MARKET OVERVIEW", fontSize=14, bold=True, color=COLOR_ACCENT)
    add_horizontal_rule()

    reddit_count = metadata.get("reddit_posts", 0)
    twitter_count = metadata.get("twitter_tweets", 0)
    news_count = metadata.get("news_articles", 0)
    signals_found = metadata.get("signals_found", len(signals))

    overview_lines = [
        f"📡 Scanned: {reddit_count} Reddit posts · {twitter_count} Twitter posts · {news_count} news queries",
        f"🎯 Signals detected: {signals_found} tickers",
        f"📊 Spread trades suggested: {len(spreads)}",
    ]
    for line in overview_lines:
        add_text(line, fontSize=11, color=COLOR_NEUTRAL)
    add_text("")

    # ── Top Signals ──
    strong = [s for s in signals if s.get("tier") == "🟢 STRONG BUY"]
    watch = [s for s in signals if s.get("tier") == "🟡 WATCH"]
    neutral = [s for s in signals if s.get("tier") == "⚪ NEUTRAL"]

    if strong:
        add_text("🟢 STRONG BUY SIGNALS", fontSize=13, bold=True, color=COLOR_GREEN)
        add_horizontal_rule()
        for s in strong[:5]:
            name = s.get("company_name", s["ticker"])
            sentiment = s.get("avg_sentiment", 0)
            sent_str = "📈" if sentiment > 0.1 else ("📉" if sentiment < -0.1 else "➡️")
            line = f"• ${s['ticker']} — {name}  {sent_str}  (score: {s['score']:.2f})"
            add_text(line, fontSize=11, bold=True)
            detail = f"  {s['mentions']} mentions · {s.get('velocity', 0)} sources · sentiment {sentiment:+.2f}"
            add_text(detail, fontSize=10, color=COLOR_NEUTRAL)
        add_text("")

    if watch:
        add_text("🟡 WATCHLIST", fontSize=13, bold=True, color=COLOR_YELLOW)
        add_horizontal_rule()
        for s in watch[:8]:
            name = s.get("company_name", s["ticker"])
            line = f"• ${s['ticker']} — {name}  (score: {s['score']:.2f})"
            add_text(line, fontSize=11)
            detail = f"  {s['mentions']} mentions · {s.get('velocity', 0)} sources"
            add_text(detail, fontSize=10, color=COLOR_NEUTRAL)
        add_text("")

    if neutral and not strong and not watch:
        add_text("⚪ MENTIONED", fontSize=13, bold=True, color=COLOR_NEUTRAL)
        add_horizontal_rule()
        tickers_str = ", ".join([f"${s['ticker']}" for s in neutral[:10]])
        add_text(tickers_str, fontSize=11, color=COLOR_NEUTRAL)
        add_text("")

    # ── Spread Trade Suggestions ──
    if spreads:
        add_text("🎯 SPREAD TRADE SUGGESTIONS", fontSize=13, bold=True, color=COLOR_GREEN)
        add_text("Vertical spreads · small-account playbook", fontSize=10, color=COLOR_NEUTRAL)
        add_horizontal_rule()

        for s in spreads[:5]:
            direction_emoji = "📈" if "bullish" in s.get("direction", "") else "📉"
            title = f"{direction_emoji} ${s['ticker']} — {s['type']}"
            add_text(title, fontSize=12, bold=True)

            details = [
                f"  Strategy: {s.get('bias', '').replace('_', ' ')}",
                f"  IV regime: {s.get('iv_regime', 'unknown').upper()}",
                f"  Why: {s.get('reason', '')}",
                f"  Profit target: {s.get('profit_target', '')}",
            ]
            for d in details:
                add_text(d, fontSize=10, color=COLOR_NEUTRAL)

            if "strikes" in s:
                st = s["strikes"]
                add_text(f"  ✏️ {st.get('strike_note', '')}", fontSize=10, bold=True)
                if "max_loss_per_contract" in st:
                    add_text(f"  Max loss: ${st['max_loss_per_contract']}", fontSize=10, color=COLOR_RED)

            if s.get("notes"):
                for note in s["notes"]:
                    add_text(f"  {note}", fontSize=10, color=COLOR_RED)

            add_text("")

    # ── Source Breakdown ──
    add_text("📡 SOURCE BREAKDOWN", fontSize=13, bold=True, color=COLOR_ACCENT)
    add_horizontal_rule()

    source_map = {}
    for s in signals:
        for src in s.get("sources", []):
            source_map[src] = source_map.get(src, 0) + 1

    for src, count in sorted(source_map.items()):
        add_text(f"• {src.title()}: {count} ticker mentions", fontSize=10, color=COLOR_NEUTRAL)
    add_text("")

    # ── Footer ──
    add_horizontal_rule()
    add_text("", fontSize=6)
    add_text(
        f"🐺 Wolf Trading Agent · Generated {now.strftime('%Y-%m-%d %H:%M UTC')}",
        fontSize=8, color=COLOR_NEUTRAL, alignment="CENTER"
    )
    add_text(
        "This is not financial advice. For informational purposes only. Do your own research.",
        fontSize=8, color=COLOR_NEUTRAL, alignment="CENTER"
    )

    return requests


def apply_formatting(doc_id: str, requests: list):
    """Apply batch update requests to the Google Doc."""
    from googleapiclient.discovery import build

    creds = get_credentials()
    docs_service = build("docs", "v1", credentials=creds)

    # Apply in batches (API accepts max ~100 requests per call)
    for i in range(0, len(requests), 50):
        batch = requests[i:i+50]
        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={"requests": batch},
        ).execute()

    print(f"✅ Applied {len(requests)} formatting requests")


def generate_newsletter(scan_data: dict, spreads_data: dict = None) -> str:
    """Main entry point. Creates Google Doc and returns the URL."""
    now = datetime.now()
    title = f"🐺 Wolf Daily Brief — {now.strftime('%B %d, %Y')}"

    doc_id = create_doc(title)

    # Merge data
    data = {
        "signals": scan_data.get("signals", []),
        "metadata": scan_data.get("metadata", {}),
        "spreads": spreads_data or [],
    }

    requests = build_requests(doc_id, data)
    apply_formatting(doc_id, requests)

    doc_url = f"https://docs.google.com/document/d/{doc_id}"
    print(f"🔗 {doc_url}")
    return doc_url


# ── CLI ─────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="🐺 Wolf Daily Brief — Google Docs Newsletter")
    parser.add_argument("--scan", help="Path to Wolf scan JSON", default="/tmp/wolf_scan.json")
    parser.add_argument("--spreads", help="Path to spread suggestions JSON", default=None)
    parser.add_argument("--output-url", help="Save doc URL to file", default="/tmp/wolf_newsletter_url.txt")
    args = parser.parse_args()

    # Load scan data
    if not os.path.exists(args.scan):
        print(f"❌ Scan file not found: {args.scan}", file=sys.stderr)
        print("Run wolf_scan.py first: python3 wolf_scan.py --json > /tmp/wolf_scan.json", file=sys.stderr)
        sys.exit(1)

    with open(args.scan) as f:
        scan_data = json.load(f)

    # Normalize `sources` fields: wolf_scan.py outputs Python string repr
    # (e.g., "{'reddit'}") instead of a list. Parse it.
    for signal in scan_data.get("signals", []):
        sources = signal.get("sources")
        if isinstance(sources, str):
            try:
                parsed = ast.literal_eval(sources)
                if isinstance(parsed, (set, dict)):
                    signal["sources"] = list(parsed)
            except (ValueError, SyntaxError):
                signal["sources"] = []

    # Load spreads if available
    spreads_data = None
    if args.spreads and os.path.exists(args.spreads):
        with open(args.spreads) as f:
            spreads_data = json.load(f)

    # Generate
    doc_url = generate_newsletter(scan_data, spreads_data)

    # Save URL
    with open(args.output_url, "w") as f:
        f.write(doc_url)
    print(f"📎 Doc URL saved to {args.output_url}")


if __name__ == "__main__":
    main()
