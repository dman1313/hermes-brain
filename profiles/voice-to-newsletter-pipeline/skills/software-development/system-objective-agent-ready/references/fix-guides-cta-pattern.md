# Fix Guides + CTA Upsell Pattern

## Architecture

When a site fails certification, the results page guides the user toward a paid fix:

```
Scanner → 7 checks → FAILs expand with fix guide → "Fix It For Me" CTA
                                              ↘ "I'll fix it myself" → /fix page
```

## FIX_GUIDES Dictionary (checker.py)

Each entry contains a self-contained markdown fix guide with copy-paste code snippets. The dictionary key matches the `CertCheck.name` field exactly.

### Guide format rules:
- Start with `# How to Add/Fix [Check Name]`
- Include 2-3 platform-specific code blocks (Python/Flask, Node.js/Express, Nginx, Apache, static HTML)
- End with `[📋 Copy template →]()` link
- Keep the scrollable height small (~320px) via CSS `.fix-guide { max-height: 320px; overflow-y: auto; }`

### Current guides (7 total):

| Check Name | Primary Audience | Code Languages |
|---|---|---|
| llms.txt accessible | Everyone | Markdown template |
| Markdown negotiation | Backend devs | Python, Node.js |
| Alternate link tag | Frontend devs | HTML |
| JSON-LD structured data | Frontend devs | HTML/JSON |
| Vary header | DevOps | Apache, Nginx, Python, Cloudflare |
| Link canonical header | Backend devs | Python, Nginx |
| ai.txt present | Everyone | Plain text |

## CTA Placement Rules

### Show when:
- `scan_result.certified == False` (any FAIL)
- Template: `{% if not scan_result.certified %}`

### Hide when:
- Site passes all required checks (no FAILs)
- Result page loads without a scan (form-only state)

### CTA copy:
```
🔧 Want us to fix all N issues?
One-time setup — your site gets fully agent-ready within 24 hours.
Includes all 7 standards, automated re-certification, and the badge.

[Fix It For Me — $99]   [I'll fix it myself →]
```

### CTA links:
- "Fix It For Me" → `mailto:hello@agentready.ai?subject=Fix%20[URL]`
- "I'll fix it myself" → `/fix` (dedicated guides page)

## Template Pattern (Jinja2)

```html
{% if scan_result %}
<div class="results {% if scan_result.certified %}certified{% else %}not-certified{% endif %}">
  <!-- header + stats -->

  <div class="checks">
    {% for c in scan_result.checks %}
    <details class="check-row {{ c.status.value|lower }}" {% if c.status.value == 'FAIL' %}open{% endif %}>
      <summary class="check-summary">
        <span class="check-icon">{{ c.emoji() }}</span>
        <span class="check-name">{{ c.name }}</span>
        <span class="check-status-badge {{ c.status.value|lower }}">{{ c.status.value }}</span>
      </summary>
      <div class="check-body">
        <p class="check-detail">{{ c.detail }}</p>
        {% if c.status.value in ('FAIL', 'WARN') and c.fix_guide %}
        <div class="fix-guide">{{ c.fix_guide | safe }}</div>
        {% endif %}
      </div>
    </details>
    {% endfor %}
  </div>

  <!-- CTA: only for non-certified -->
  {% if not scan_result.certified %}
  <div class="cta-fix">
    <div class="cta-fix-content">
      <h3>🔧 Want us to fix all {{ scan_result.failed + scan_result.warnings }} issues?</h3>
      <p>One-time setup — your site gets fully agent-ready within 24 hours...</p>
      <div class="cta-fix-buttons">
        <a href="mailto:hello@agentready.ai?subject=Fix%20{{ scan_result.url | urlencode }}" class="btn-primary">Fix It For Me — $99</a>
        <a href="/fix" class="btn-secondary">I'll fix it myself →</a>
      </div>
    </div>
  </div>
  {% endif %}
</div>
{% endif %}
```

## API Response Shape

The `/api/certify?url=` endpoint includes `fix_guide` for FAIL/WARN checks:

```json
{
  "certified": false,
  "checks": [
    {
      "name": "llms.txt accessible",
      "status": "FAIL",
      "detail": "HTTP 404",
      "fix_guide": "# How to Add llms.txt\n\nCreate a file..."
    }
  ]
}
```

Only FAIL and WARN checks get `fix_guide`. PASS checks get empty string.

## CSS Key Classes

| Class | Purpose |
|---|---|
| `.check-row` | `<details>` element, border on `[open]` |
| `.check-summary` | Flex row: icon + name + badge, cursor: pointer |
| `.check-status-badge` | Colored pill: PASS=green, FAIL=red, WARN=amber |
| `.check-body` | Padded indented content area |
| `.fix-guide` | Scrollable container for guide content, max-height 320px |
| `.cta-fix` | Green gradient border box, centered, margin-top 24px |
| `.cta-fix-buttons` | Flex row, gap 12px, center-aligned |
