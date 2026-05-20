# Dashboard User Themes (YAML)

User themes are YAML files in `~/.hermes/dashboard-themes/<name>.yaml`.
The dashboard reads them live on every call — no restart needed.

## Minimal Theme

```yaml
name: my-theme
label: My Theme
description: A custom theme
palette:
  background:
    hex: "#ffffff"
    alpha: 1.0
  midground:
    hex: "#1a1816"
    alpha: 1.0
  foreground:
    hex: "#ffffff"
    alpha: 0.0
  warmGlow: "rgba(74, 124, 89, 0.15)"
  noiseOpacity: 0.25
```

## Full Schema

```yaml
name: natural                    # unique, kebab-case
label: Natural                   # display name in picker
description: "..."
palette:
  background: { hex: "#fff", alpha: 1.0 }    # page background
  midground:  { hex: "#1a1816", alpha: 1.0 } # text/accent color (drives shadcn tokens)
  foreground: { hex: "#fff", alpha: 0.0 }    # top-layer highlight
  warmGlow: "rgba(...)"                      # ambient vignette color
  noiseOpacity: 0.25                          # grain texture intensity (0-1.2)
typography:
  fontSans: "Inter, system-ui, sans-serif"
  fontMono: "JetBrains Mono, ui-monospace, monospace"
  fontDisplay: "Inter, system-ui, sans-serif"   # optional
  fontUrl: "https://fonts.googleapis.com/..."    # optional, auto-injected <link>
  baseSize: "16px"
  lineHeight: "1.6"
  letterSpacing: "0"
layout:
  radius: "0.875rem"                            # corner radius
  density: comfortable                          # compact | comfortable | spacious
colorOverrides:                                 # direct shadcn token overrides
  primary: "#4a7c59"
  primaryForeground: "#ffffff"
  secondary: "#f7f4ee"
  secondaryForeground: "#1a1816"
  muted: "#f0ece6"
  mutedForeground: "#78716c"
  accent: "#4a7c59"
  accentForeground: "#ffffff"
  destructive: "#c47d7d"
  destructiveForeground: "#ffffff"
  border: "#d9d3c7"
  input: "#d9d3c7"
  ring: "#4a7c59"
  card: "#ffffff"
  cardForeground: "#1a1816"
  popover: "#ffffff"
  popoverForeground: "#1a1816"
componentStyles:                     # per-component CSS var overrides
  card:
    boxShadow: "0 1px 4px rgba(0,0,0,0.04)"
  header:
    background: "rgba(255,255,255,0.85)"
    backdropFilter: "blur(16px)"
  sidebar:
    background: "rgba(255,255,255,0.7)"
    backdropFilter: "blur(16px)"
customCSS: |                         # raw CSS injected as <style> tag (max 32KB)
  .some-class { ... }
```

## Key Mechanics

- **midground drives text color**: `--color-foreground` maps to midground. For light themes, use dark hex like `#1a1816`.
- **colorOverrides pin shadcn tokens**: Without overrides, tokens are derived from palette via `color-mix()`.
- **customCSS is scoped**: Injected into `<style id="hermes-theme-custom-css">`, cleaned up on theme switch.
- **Read live**: Dashboard reads YAML on every `/api/dashboard/themes` call. No restart needed.

## Activation

```bash
hermes config set dashboard.theme natural
```

## Built-in vs User Themes

Built-in themes defined in `web/src/themes/presets.ts`. User themes from `~/.hermes/dashboard-themes/*.yaml` override built-ins with same name. Backend normalizer: `hermes_cli/web_server.py` → `_normalise_theme_definition()`.
