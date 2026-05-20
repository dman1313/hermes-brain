# Google Slides API — Patterns & Pitfalls

The Google Slides API is NOT covered by `scripts/google_api.py`. For slide creation, write a standalone Python script that uses the same OAuth token at `~/.hermes/google_token.json`.

## Scopes Required

Add to the SCOPES list:
```python
"https://www.googleapis.com/auth/presentations",
```

The existing `drive.file` scope is also needed for permissions (making public).

## Auth Pattern

```python
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

HERMES_HOME = Path.home() / ".hermes"
TOKEN_PATH = HERMES_HOME / "google_token.json"
SCOPES = [
    "https://www.googleapis.com/auth/presentations",
    "https://www.googleapis.com/auth/drive.file",
]

creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
    TOKEN_PATH.write_text(creds.to_json())

from googleapiclient.discovery import build
slides = build("slides", "v1", credentials=creds)
drive = build("drive", "v3", credentials=creds)
```

## CRITICAL PITFALL: `fields` in batchUpdate Requests

**The `fields` parameter MUST be nested inside the request object, NOT at the top level of the request dict.**

Wrong (produces HTTP 400 `Unknown name "fields"`):
```python
{
    "updatePageProperties": {
        "objectId": slide_id,
        "pageProperties": {"pageBackgroundFill": {"solidFill": {"color": DARK}}},
    },
    "fields": "pageBackgroundFill",  # ← WRONG — sibling of updatePageProperties
}
```

Correct:
```python
{
    "updatePageProperties": {
        "objectId": slide_id,
        "pageProperties": {"pageBackgroundFill": {"solidFill": {"color": DARK}}},
        "fields": "pageBackgroundFill",  # ← CORRECT — inside updatePageProperties
    },
}
```

This applies to ALL batchUpdate request types that accept a field mask:
- `updatePageProperties` → `fields` inside it
- `updateTextStyle` → `fields` inside it
- `updateShapeProperties` → `fields` inside it

## Creating a Presentation

```python
pres = slides.presentations().create(
    body={"title": "My Presentation"}
).execute()
pres_id = pres["presentationId"]
# The first slide is auto-created — its ID is pres["slides"][0]["objectId"]
```

## Adding Slides

```python
slides.presentations().batchUpdate(
    presentationId=pres_id,
    body={"requests": [{
        "createSlide": {
            "objectId": "slide2",
            "insertionIndex": 1,
            "slideLayoutReference": {"predefinedLayout": "BLANK"},
        }
    }]}
).execute()
```

Use `predefinedLayout: "BLANK"` for full control. Other options: TITLE, TITLE_AND_BODY, etc.

## Helper Functions (from working example)

### Dark Background
```python
def bg(page_id):
    return {
        "updatePageProperties": {
            "objectId": page_id,
            "pageProperties": {
                "pageBackgroundFill": {"solidFill": {"color": DARK}}
            },
            "fields": "pageBackgroundFill",
        }
    }
```

### Text Box
```python
def tbox(page_id, text, x, y, w, h, size=12, bold=False, color=None):
    obj_id = f"{page_id}_txt_{abs(hash(text)) % 100000}"
    return [
        {"createShape": {
            "objectId": obj_id, "shapeType": "TEXT_BOX",
            "elementProperties": {
                "pageObjectId": page_id,
                "size": {"width": {"magnitude": w, "unit": "PT"},
                         "height": {"magnitude": h, "unit": "PT"}},
                "transform": {"scaleX": 1, "scaleY": 1,
                              "translateX": x, "translateY": y, "unit": "PT"},
            },
        }},
        {"insertText": {"objectId": obj_id, "text": text}},
        {"updateTextStyle": {
            "objectId": obj_id,
            "style": {"bold": bold,
                      "fontSize": {"magnitude": size, "unit": "PT"},
                      "foregroundColor": {"opaqueColor": color or WHITE}},
            "textRange": {"type": "ALL"},
            "fields": "bold,fontSize,foregroundColor",
        }},
    ]
```

### Bullet List
```python
def bul(page_id, items, x, y, w, h, size=11, color=None):
    text = "\n".join(f"• {item}" for item in items)
    return tbox(page_id, text, x, y, w, h, size=size, color=color)
```

## Making Public

```python
drive.permissions().create(
    fileId=pres_id,
    body={"type": "anyone", "role": "reader"},
).execute()
```

## Coordinate System

- Slide canvas: 720pt wide × 405pt high (standard 16:9)
- Origin (0,0) is top-left
- All positions in points (PT)

## Common Colors

```python
DARK = {"rgbColor": {"red": 0.07, "green": 0.07, "blue": 0.12}}
ACCENT = {"rgbColor": {"red": 0.4, "green": 0.55, "blue": 0.95}}
WHITE = {"rgbColor": {"red": 1, "green": 1, "blue": 1}}
GRAY = {"rgbColor": {"red": 0.7, "green": 0.7, "blue": 0.8}}
GREEN = {"rgbColor": {"red": 0.2, "green": 0.8, "blue": 0.4}}
```

## Batch Updates

Send updates in groups per slide to keep request size manageable:
```python
def send(reqs):
    slides.presentations().batchUpdate(
        presentationId=pres_id, body={"requests": reqs}
    ).execute()
```

Unpack helper lists with the spread operator:
```python
send([
    bg("slide1"),
    *tbox("slide1", "Title", 50, 100, 620, 60, size=48, bold=True),
    *bul("slide1", ["Item 1", "Item 2"], 50, 200, 620, 200),
])
```
