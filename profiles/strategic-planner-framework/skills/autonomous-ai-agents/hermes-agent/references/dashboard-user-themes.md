# Dashboard User Themes (YAML-based)

The native Hermes dashboard supports user-created themes as YAML files in
`~/.hermes/dashboard-themes/*.yaml`. These ship with their full definition
to the frontend — no web rebuild needed.

## Quick Start

```bash
mkdir -p ~/.hermes/dashboard-themes
# Create your-theme.yaml (see template below)
hermes config set dashboard.theme your-theme-name
hermes dashboard --stop && hermes dashboard --port 9119 --host 0.0.0.0 --insecure --no-open &
```

Refresh the dashboard — the new theme appears in the theme picker and is active.

## YAML Format

```yaml
name: my-theme              # unique id (used in config)
label: My Theme             # display name in picker
description: What it does   # shown in picker tooltip

palette:                    # 3-layer color system
  background:               # page background
    hex: "#f5f0e8"
    alpha: 1.0
  midground:                # text / primary accent color
    hex: "#2d2926"
    alpha: 1.0
  foreground:               # top highlight layer
    hex: "#ffffff"
    alpha: 1.0
  warmGlow: "rgba(74,124,89,0.12)"  # backdrop vignette
  noiseOpacity: 0.25        # grain texture intensity (0-1.2)

typography:
  fontSans: '"Inter", system-ui, sans-serif'
  fontMono: '"JetBrains Mono", ui-monospace, monospace'
  fontUrl: "https://fonts.googleapis.com/css2?family=..."
  baseSize: "15px"
  lineHeight: "1.55"
  letterSpacing: "0"

layout:
  radius: "1rem"            # corner radius token
  density: comfortable       # compact | comfortable | spacious

colorOverrides:             # pin shadcn tokens to exact hex
  card: "#ffffff"           # overrides derived color-mix values
  cardForeground: "#2d2926"
  primary: "#4a7c59"
  primaryForeground: "#ffffff"
  secondary: "#ede8dd"
  secondaryForeground: "#2d2926"
  muted: "#f5f0e8"
  mutedForeground: "#a39e96"
  accent: "#4a7c59"
  accentForeground: "#ffffff"
  destructive: "#c47d7d"
  success: "#4a7c59"
  warning: "#d4a843"
  border: "#d9d3c7"
  input: "#d9d3c7"
  ring: "#4a7c59"
  popover: "#ffffff"
  popoverForeground: "#2d2926"

componentStyles:            # per-component CSS var overrides
  header:
    background: "rgba(255,255,255,0.6)"
    backdropFilter: "blur(16px)"
    borderBottom: "1px solid #d9d3c7"
  sidebar:
    background: "rgba(255,255,255,0.7)"
    backdropFilter: "blur(16px)"
    borderRight: "1px solid #d9d3c7"
  card:
    background: "#ffffff"
    border: "1px solid #d9d3c7"
    borderRadius: "16px"
    boxShadow: "0 1px 4px rgba(0,0,0,0.04)"
  badge:
    borderRadius: "6px"
  progress:
    color: "#4a7c59"
    background: "#d9d3c7"

customCSS: |                # raw CSS injected as <style> tag
  /* Target any element — pseudo-elements, kanban classes, etc. */
  body::before { content:''; /* grain texture overlay */ }
  .hermes-kanban-card-content { /* card restyling */ }
  ::-webkit-scrollbar { width: 6px; }  /* custom scrollbar */
```

## What customCSS Can Do

- Restyle any element on the page (kanban cards, columns, inputs, scrollbars)
- Add pseudo-elements (`::before`, `::after`) for grain textures, blobs, decorative elements
- Override `.hermes-kanban-*` selectors (status dots, column headers, cards, progress pills)
- Inject CSS animations (`@keyframes`)
- Max 32 KB

## What customCSS CANNOT Do

- Create new DOM elements (no Agent Squad Bar, no extra divs)
- Run JavaScript
- Change the kanban card's internal HTML structure (ID, badges, assignee layout is fixed by the React component)

## How the Palette Works

The dashboard derives shadcn-compat tokens from the 3-layer palette using
`color-mix()`. For example, `--color-card` is computed as:
```css
color-mix(in srgb, var(--midground-base) 4%, var(--background-base))
```

This works well for dark themes but produces inverted results for light themes
(cards become darker than the background instead of lighter). **Use
`colorOverrides` to pin all shadcn tokens to exact hex values when building
a light theme.**

### Light-Theme Palette Strategy

There are two strategies for light themes:

**Strategy A: Green midground (accent-driven UI).** The midground color drives primary/accent
computation. Setting it to an accent color gives the UI green-toned chrome.
This looks polished but can make text hard to read because `--color-foreground`
(primary text) derives from midground.

```yaml
# Pretty but text may be hard to read
midground: {hex: "#4a7c59", alpha: 1.0}  # forest green accents everywhere
```

**Strategy B: Dark midground (readability-first).** Set midground to a near-black
warm tone. This makes ALL text dark and readable. Use `colorOverrides.primary`
to keep buttons green. **This is the preferred approach for this user.**

```yaml
# Clean, readable, dark text everywhere
midground: {hex: "#1a1816", alpha: 1.0}   # near-black warm text
colorOverrides:
  primary: "#4a7c59"                       # green buttons survive
  primaryForeground: "#ffffff"
  accent: "#4a7c59"                        # green accents
  mutedForeground: "#78716c"               # readable secondary text (not #a39e96)
```

**User preference (encoding session corrections):** This user prefers:
- White background (`background.hex: "#ffffff"`, NOT cream `#f5f0e8`)
- Thick, dark, readable fonts (Strategy B above)
- Font weight 400-800 (drop the 300 light weight from Google Fonts URL)
- Base font size 16px (not 15px)
- Letter-spacing 0 (not negative)
- Muted text at `#78716c` or darker (NOT light `#a39e96`)
- Green used ONLY for buttons/accent elements, never for body text

## Built-in Theme Names

`default`, `default-large`, `midnight`, `ember`, `mono`, `cyberpunk`, `rose`

User themes take precedence over built-ins when names collide.
