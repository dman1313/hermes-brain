#!/usr/bin/env python3
"""Create a Google Slides presentation from a structured outline.

Template — copy and customize for your own presentation.
Uses the same OAuth token as the rest of google-workspace.

Usage:
  python scripts/slides-template.py
"""

import sys
from pathlib import Path

HERMES_HOME = Path.home() / ".hermes"
TOKEN_PATH = HERMES_HOME / "google_token.json"

SCOPES = [
    "https://www.googleapis.com/auth/presentations",
    "https://www.googleapis.com/auth/drive.file",
]

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
    TOKEN_PATH.write_text(creds.to_json())

from googleapiclient.discovery import build

slides = build("slides", "v1", credentials=creds)
drive = build("drive", "v3", credentials=creds)

# ── Color palette ──
DARK = {"rgbColor": {"red": 0.07, "green": 0.07, "blue": 0.12}}
ACCENT = {"rgbColor": {"red": 0.4, "green": 0.55, "blue": 0.95}}
WHITE = {"rgbColor": {"red": 1, "green": 1, "blue": 1}}
GRAY = {"rgbColor": {"red": 0.7, "green": 0.7, "blue": 0.8}}
GREEN = {"rgbColor": {"red": 0.2, "green": 0.8, "blue": 0.4}}


def tbox(page_id, text, x, y, w, h, size=12, bold=False, color=None):
    """Create a text box with styling. Returns list of batchUpdate requests."""
    obj_id = f"{page_id}_txt_{abs(hash(text)) % 100000}"
    return [
        {"createShape": {
            "objectId": obj_id, "shapeType": "TEXT_BOX",
            "elementProperties": {
                "pageObjectId": page_id,
                "size": {
                    "width": {"magnitude": w, "unit": "PT"},
                    "height": {"magnitude": h, "unit": "PT"}},
                "transform": {
                    "scaleX": 1, "scaleY": 1,
                    "translateX": x, "translateY": y, "unit": "PT"},
            },
        }},
        {"insertText": {"objectId": obj_id, "text": text}},
        {"updateTextStyle": {
            "objectId": obj_id,
            "style": {
                "bold": bold,
                "fontSize": {"magnitude": size, "unit": "PT"},
                "foregroundColor": {"opaqueColor": color or WHITE},
            },
            "textRange": {"type": "ALL"},
            "fields": "bold,fontSize,foregroundColor",
        }},
    ]


def bul(page_id, items, x, y, w, h, size=11, color=None):
    """Create a bullet-point text box."""
    text = "\n".join(f"• {item}" for item in items)
    return tbox(page_id, text, x, y, w, h, size=size, color=color or GRAY)


def bg(page_id):
    """Dark background for a slide."""
    return {
        "updatePageProperties": {
            "objectId": page_id,
            "pageProperties": {
                "pageBackgroundFill": {"solidFill": {"color": DARK}}
            },
            "fields": "pageBackgroundFill",
        }
    }


def new_slide(obj_id, index):
    """Create a new blank slide at the given index."""
    return {
        "createSlide": {
            "objectId": obj_id,
            "insertionIndex": index,
            "slideLayoutReference": {"predefinedLayout": "BLANK"},
        }
    }


def send(reqs):
    """Send batchUpdate requests."""
    slides.presentations().batchUpdate(
        presentationId=pres_id, body={"requests": reqs}
    ).execute()


# ── Create presentation ──
TITLE = "CHANGE_ME — Your Title Here"
pres = slides.presentations().create(body={"title": TITLE}).execute()
pres_id = pres["presentationId"]
slide1_id = pres["slides"][0]["objectId"]


# ── SLIDE 1: Title ──
send([
    bg(slide1_id),
    *tbox(slide1_id, "YOUR TITLE", 50, 100, 620, 60, size=48, bold=True, color=ACCENT),
    *tbox(slide1_id, "Subtitle or description", 50, 170, 620, 40, size=28, color=WHITE),
    *tbox(slide1_id, "Your Name / Date / Context", 50, 240, 620, 30, size=16, color=GRAY),
    *tbox(slide1_id, "Footer text or URL", 50, 340, 620, 24, size=13, color=GRAY),
])

# ── SLIDE 2: Content ──
send([new_slide("slide2", 1)])
send([
    bg("slide2"),
    *tbox("slide2", "Slide Title", 50, 35, 620, 45, size=32, bold=True, color=ACCENT),
    *bul("slide2", [
        "First bullet point",
        "Second bullet point",
        "Third bullet point",
    ], 50, 100, 620, 280, size=14, color=WHITE),
])

# ── SLIDE 3: More Content ──
send([new_slide("slide3", 2)])
send([
    bg("slide3"),
    *tbox("slide3", "Another Slide", 50, 35, 620, 45, size=32, bold=True, color=ACCENT),
    *bul("slide3", [
        "Point A",
        "Point B",
        "Point C",
    ], 50, 100, 620, 280, size=14, color=WHITE),
])

# ── Make public ──
drive.permissions().create(
    fileId=pres_id,
    body={"type": "anyone", "role": "reader"},
).execute()

print(f"Done — {pres_id}")
print(f"Edit: https://docs.google.com/presentation/d/{pres_id}/edit")
print(f"View: https://docs.google.com/presentation/d/{pres_id}/present")
