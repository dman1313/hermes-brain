# Google Docs API borderBottom Bug (v2.188.0)

**Symptom:** `updateParagraphStyle` with `borderBottom` returns:
```
Invalid requests[N].updateParagraphStyle: Unsupported dimension unit: UNIT_UNSPECIFIED
```

**Root cause:** The `borderBottom` property in `ParagraphStyle` is broken in the google-api-python-client v2.188.0. Every variation fails (with or without color, with or without width, with or without dashStyle) — even a bare `borderBottom: { dashStyle: "SOLID" }`.

**Tested:** `spaceBelow` alone works. `borderBetween` works. `borderBottom` alone fails.

**Workaround:** Use `borderBetween` with `padding` instead:
```python
{
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
}
```

**Discovered:** 2026-05-01 during Wolf newsletter generation.
**Affected file:** `scripts/wolf_newsletter.py` (patched).
