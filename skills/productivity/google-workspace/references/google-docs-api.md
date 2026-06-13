# Google Docs API — Patterns & Pitfalls

The Google Docs API is NOT covered by `scripts/google_api.py`. For document creation with formatting, write a standalone Python script that uses the same OAuth token at `~/.hermes/google_token.json`.

## Scopes Required

```python
SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive.file",
]
```

## Auth Pattern

```python
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

HERMES_HOME = Path.home() / ".hermes"
TOKEN_PATH = HERMES_HOME / "google_token.json"
SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive.file",
]

creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
    TOKEN_PATH.write_text(creds.to_json())

docs = build("docs", "v1", credentials=creds)
drive = build("drive", "v3", credentials=creds)
```

## Two-Pass Document Creation Pattern

The Docs API is index-based (character positions), which makes interleaving text insertion and formatting fragile. **Use a two-pass approach:**

### Pass 1: Build the full text string, recording segment boundaries

```python
full_text = ""
segments = []  # list of (start, end, style)

def add(text, style="normal"):
    global full_text
    start = len(full_text)
    full_text += text
    end = len(full_text)
    segments.append((start, end, style))

add("Title Here\n", "title")
add("Section 1\n", "heading1")
add("Body text here.\n")
add("Bold label: ", "bold")
add("normal text continues.\n")
add("Bullet item\n", "bullet")
```

### Pass 2: Insert all text at once, then apply formatting in batches

```python
requests = []

# Insert all text at index 1
requests.append({
    "insertText": {
        "location": {"index": 1},
        "text": full_text
    }
})

# Apply formatting — indices are offset by +1 (text inserted at index 1)
for start, end, style in segments:
    si, ei = start + 1, end + 1  # offset by insertion point

    if style == "title":
        requests.append({
            "updateTextStyle": {
                "range": {"startIndex": si, "endIndex": ei},
                "textStyle": {
                    "bold": True,
                    "fontSize": {"magnitude": 24, "unit": "PT"},
                    "foregroundColor": {"color": {"rgbColor": {"red": 0.1, "green": 0.3, "blue": 0.6}}}
                },
                "fields": "bold,fontSize,foregroundColor"
            }
        })
    elif style == "bold":
        requests.append({
            "updateTextStyle": {
                "range": {"startIndex": si, "endIndex": ei},
                "textStyle": {"bold": True},
                "fields": "bold"
            }
        })

    # Paragraph styles (headings)
    HEADING_MAP = {"heading1": "HEADING_1", "heading2": "HEADING_2", "title": "HEADING_1"}
    if style in HEADING_MAP:
        requests.append({
            "updateParagraphStyle": {
                "range": {"startIndex": si, "endIndex": ei},
                "paragraphStyle": {"namedStyleType": HEADING_MAP[style]},
                "fields": "namedStyleType"
            }
        })

    # Bullet points (manual indent, not native bullet API)
    elif style == "bullet":
        requests.append({
            "updateParagraphStyle": {
                "range": {"startIndex": si, "endIndex": ei},
                "paragraphStyle": {
                    "indentStart": {"magnitude": 36, "unit": "PT"},
                    "indentFirstLine": {"magnitude": -18, "unit": "PT"},
                    "spaceBelow": {"magnitude": 4, "unit": "PT"}
                },
                "fields": "indentStart,indentFirstLine,spaceBelow"
            }
        })
```

## Sending in Batches

Request size limits apply. Send in chunks of ~100:

```python
CHUNK = 100
for i in range(0, len(requests), CHUNK):
    chunk = requests[i:i+CHUNK]
    docs.documents().batchUpdate(
        documentId=doc_id,
        body={"requests": chunk}
    ).execute()
```

## Making Public

```python
drive.permissions().create(
    fileId=doc_id,
    body={"type": "anyone", "role": "reader"},
).execute()
```

## Pitfalls

1. **Index offset**: When you `insertText` at index 1, ALL subsequent formatting indices must account for the +1 offset. Text that starts at position 0 in your `full_text` string is at position 1 in the document.

2. **Don't interleave insert and format**: The Docs API processes requests sequentially within a batchUpdate. If you insert text at index 5, then try to format range 5-10 in the same batch, the second request's indices are stale. Solution: insert ALL text first, then format.

3. **No native bullet API**: The Docs API has no simple "make this a bullet" call. The `bullet` field in `updateParagraphStyle` requires a `listId` that must be created first via `createParagraphBullets`. The manual indent approach (indentStart + negative indentFirstLine) is simpler and works reliably for most cases.

4. **Empty lines count**: A `\n` at the end of text is a character that affects paragraph boundaries. Be consistent — always end segments with `\n` to ensure formatting applies to the right paragraph.

5. **No tables via simple API**: The `insertTable` request creates a table structure, but filling cells requires knowing the table's internal object IDs (auto-generated). For complex tables, consider: (a) creating a template doc manually and copying it, or (b) using Sheets API instead and embedding the sheet.

6. **Title auto-creation**: When you `documents().create()` with a title, the first paragraph in the body is empty (index 1 is a newline). Your first `insertText` at index 1 replaces this empty paragraph. This is correct behavior — don't try to delete the empty paragraph first.

## Quick Reference: Text Style Fields

| Effect | `fields` string | `textStyle` keys |
|--------|----------------|-----------------|
| Bold | `"bold"` | `"bold": True` |
| Font size | `"fontSize"` | `"fontSize": {"magnitude": N, "unit": "PT"}` |
| Color | `"foregroundColor"` | `"foregroundColor": {"color": {"rgbColor": {...}}}` |
| All combined | `"bold,fontSize,foregroundColor"` | all above |

## Quick Reference: Paragraph Style Fields

| Effect | `fields` string | `paragraphStyle` keys |
|--------|----------------|----------------------|
| Heading | `"namedStyleType"` | `"namedStyleType": "HEADING_1"` |
| Indent (bullet-like) | `"indentStart,indentFirstLine,spaceBelow"` | indent values in PT |
| Spacing | `"spaceAbove"` or `"spaceBelow"` | `{"magnitude": N, "unit": "PT"}` |
