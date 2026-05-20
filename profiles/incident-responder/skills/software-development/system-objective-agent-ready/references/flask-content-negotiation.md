# Flask Content Negotiation — Accept: text/markdown

For WSGI/Flask apps that can't use ASGI middleware, use `@app.after_request`:

```python
from flask import Flask, request

@app.after_request
def content_negotiation(response):
    """Convert HTML to Markdown when client requests text/markdown."""
    # Always add Vary: Accept for CDN cache independence
    response.headers['Vary'] = 'Accept'

    accept = request.headers.get('Accept', '')
    if 'text/markdown' not in accept:
        return response

    # Only convert HTML responses
    ct = response.content_type or ''
    if 'text/html' not in ct:
        return response

    try:
        md = html_to_markdown(response.get_data(as_text=True))
        response.set_data(md)
        response.content_type = 'text/markdown; charset=utf-8'
    except Exception:
        pass  # conversion failed, return original HTML

    return response
```

## Key differences from ASGI middleware

| Aspect | ASGI Middleware | Flask after_request |
|--------|----------------|---------------------|
| Framework | FastAPI / Starlette | Flask |
| Body access | `response.body` (bytes) | `response.get_data(as_text=True)` |
| Content-Type | `raw_headers` tuple list | `response.content_type` |
| Vary header | Intercept `http.response.start` | `response.headers['Vary']` |
| Streaming | Skip multi-chunk bodies | Flask auto-buffers in most cases |

## Pitfalls

- `response.content_type` may be `None` — check before `.startswith()`
- `get_data()` returns bytes; use `as_text=True` for Markdown conversion
- The `@app.after_request` runs on EVERY request — filter early for performance
- When combined with `render_template`, the template is already rendered to HTML string by the time after_request fires
