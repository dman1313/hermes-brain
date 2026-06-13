# Google Docs API — Formatting Pitfalls

## Invalid Fields (Python google-api-python-client v2.x)

The following fields are **NOT valid** in the Docs API `batchUpdate` despite appearing in tutorials and the Slides API:

| Attempted Field | Error | Fix |
|---|---|---|
| `fontFamily` in `updateTextStyle` | `Unknown name "fontFamily"` | No direct equivalent. Use `weightedFontFamily` with `fontFamily` + `weight` inside it, or skip font changes. |
| `spaceBefore` in `updateParagraphStyle` | `Unknown name "spaceBefore"` | Use `spaceAbove` |
| `spaceAfter` in `updateParagraphStyle` | `Unknown name "spaceAfter"` | Use `spaceBelow` |
| `foregroundColor: {color: {rgbColor: ...}}` | `Unknown name "color"` | See color section below |
| `foregroundColor: {opaqueColor: {rgbColor: ...}}` | `Unknown name "opaqueColor"` | See color section below |

## ForegroundColor Format

The Docs API `TextStyle.foregroundColor` is of type `OptionalColor`, but the Python client serializes nested objects differently than the Slides API. After multiple attempts, the following formats all failed via the Python client:

```python
# FAILS: "Unknown name 'color'"
"foregroundColor": {"color": {"rgbColor": {"red": 0.1, "green": 0.3, "blue": 0.6}}}

# FAILS: "Unknown name 'opaqueColor'"
"foregroundColor": {"opaqueColor": {"rgbColor": {"red": 0.1, "green": 0.3, "blue": 0.6}}}
```

**Workaround**: Skip foregroundColor in batchUpdate. Apply colors manually in the Google Doc, or use the Slides API (which handles colors correctly with `opaqueColor`).

## What DOES Work Reliably

```python
# Bold
{"updateTextStyle": {
    "range": {"startIndex": start, "endIndex": end},
    "textStyle": {"bold": True},
    "fields": "bold"
}}

# Font size
{"updateTextStyle": {
    "range": {"startIndex": start, "endIndex": end},
    "textStyle": {"fontSize": {"magnitude": 24, "unit": "PT"}},
    "fields": "fontSize"
}}

# Heading styles
{"updateParagraphStyle": {
    "range": {"startIndex": start, "endIndex": end},
    "paragraphStyle": {"namedStyleType": "HEADING_1"},
    "fields": "namedStyleType"
}}

# Alignment
{"updateParagraphStyle": {
    "range": {"startIndex": start, "endIndex": end},
    "paragraphStyle": {"alignment": "CENTER"},
    "fields": "alignment"
}}

# Paragraph spacing (use spaceAbove/spaceBelow, NOT spaceBefore/spaceAfter)
{"updateParagraphStyle": {
    "range": {"startIndex": start, "endIndex": end},
    "paragraphStyle": {
        "spaceAbove": {"magnitude": 12, "unit": "PT"},
        "spaceBelow": {"magnitude": 6, "unit": "PT"}
    },
    "fields": "spaceAbove,spaceBelow"
}}
```

## Text Insertion Pattern

The reliable pattern for building a Google Doc:

1. **Build full text string first** — concatenate all content
2. **Insert once** at index 1 with a single `insertText` request
3. **Apply formatting** in chunks of ~80 requests using recorded positions
4. **Skip color formatting** — it fails via Python client

```python
# Insert all text at once
requests = [{"insertText": {"location": {"index": 1}, "text": full_text}}]

# Then apply headings/bold using tracked positions
for start, end, style in segments:
    if style == "heading":
        requests.append({"updateParagraphStyle": {
            "range": {"startIndex": start + 1, "endIndex": end + 1},
            "paragraphStyle": {"namedStyleType": "HEADING_1"},
            "fields": "namedStyleType"
        }})

# Send in chunks
for i in range(0, len(requests), 80):
    docs.documents().batchUpdate(documentId=doc_id, body={"requests": requests[i:i+80]}).execute()
```

## Table of Contents / Bookmarks

Google Docs API supports `createNamedRange` for bookmarks and `createParagraphBookmarkLink` for TOC links. However, these are complex to implement correctly. A simpler approach: insert a numbered list at the top with section names (users can Ctrl+click in Google Docs to navigate headings).

## Making Documents Public

```python
drive.permissions().create(
    fileId=doc_id,
    body={"type": "anyone", "role": "reader"},
).execute()
```

## Batch Size Limits

- Keep batches to ~80 requests per API call
- For 200+ formatting requests, chunk into 3-4 calls
- The API returns 400 for entire batch if ANY request has invalid fields — filter invalid fields before sending
