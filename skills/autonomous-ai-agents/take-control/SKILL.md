---
name: take-control
description: "Make any software agent-native using CLI-Anything. Install existing CLI harnesses from CLI-Hub or build new ones for any software with a codebase. Replaces fragile GUI automation with structured CLI interfaces."
trigger:
  - "take control of"
  - "make agent-native"
  - "cli-anything"
  - "cli harness"
  - "agent control software"
  - "automate <software>"
  - "build cli for"
---

# Take Control — CLI-Anything Agent Harness

> Make ANY software agent-native. No GUI automation, no screenshots, no fragile pixel-clicking — pure structured CLI.

## What This Does

CLI-Anything transforms desktop/web applications into agent-controllable CLI tools. Two paths:

1. **Use existing harness** — 30+ production CLIs already built (Blender, GIMP, LibreOffice, OBS, etc.)
2. **Build new harness** — 7-phase automated pipeline generates a full CLI for any software with a codebase

## Quick Decision

```
Is there a CLI-Hub harness for the software?
├── YES → Install and use it (Phase 1)
└── NO → Build one (Phase 2)
```

---

## Phase 1: Install & Use Existing Harness

### Install CLI-Hub

```bash
pip install cli-anything-hub
```

### Browse & Search

```bash
cli-hub list                          # See all available CLIs
cli-hub search <keyword>              # Search by domain
cli-hub info <name>                   # Inspect a specific CLI
```

### Install a CLI

```bash
cli-hub install <name>                # Install from registry
cli-hub launch <name> [args...]       # Run it
```

### Use the Generated CLI

```bash
# Get help
cli-anything-<software> --help

# Enter interactive REPL
cli-anything-<software>

# JSON output for agent consumption
cli-anything-<software> --json <command>

# Example: Blender
cli-anything-blender scene new --name ProductShot
cli-anything-blender object add-mesh --type cube --location 0 0 1
cli-anything-blender render execute --output render.png --engine CYCLES
```

### Agent Integration Pattern

```bash
# Discover capabilities
which cli-anything-<software>
cli-anything-<software> --help

# All commands support --json flag
cli-anything-<software> --json <subcommand>

# Project files are JSON — easy to parse
cli-anything-<software> --project myproject.json <command>
```

---

## Phase 2: Build a New CLI Harness

### Prerequisites

- Python 3.10+
- Target software or source repo available
- Strong model required (Claude Opus, GPT-5.x, DeepSeek Pro)

### Methodology: 7-Phase Pipeline

| Phase | What Happens |
|-------|-------------|
| 1. **Analyze** | Scan source code, map GUI actions to APIs |
| 2. **Design** | Architect command groups, state model, output formats |
| 3. **Implement** | Build Click CLI with REPL, JSON output, undo/redo |
| 4. **Plan Tests** | Create TEST.md with unit + E2E test plans |
| 5. **Write Tests** | Implement comprehensive test suite |
| 6. **Document** | Update TEST.md with results |
| 7. **Publish** | Create setup.py, install to PATH |

### Build Command

```bash
# From local source
/cli-anything /path/to/software

# From GitHub repo
/cli-anything https://github.com/org/repo
```

### Refine an Existing Harness

```bash
# Broad gap analysis
/cli-anything:refine /path/to/software

# Focused refinement
/cli-anything:refine /path/to/software "batch processing and filters"
```

---

## Critical Design Rules

### DO
- **Use the real software** — CLI MUST call the actual application for rendering
- **Generate valid project files** — ODF, MLT XML, SVG, then invoke real backend
- **Support `--json` flag** on every command for agent consumption
- **Include REPL mode** — bare command enters interactive session
- **Verify output** — magic bytes, ZIP structure, pixel analysis, audio RMS
- **Write SKILL.md** for agent skill discovery

### DON'T
- Don't use Pillow as a GIMP replacement
- Don't use custom renderers for Blender
- Don't trust exit code 0 — always verify output
- Don't skip E2E tests with real software

### The Rendering Gap

GUI apps apply effects at render time. If your CLI manipulates project files but uses a naive export tool, effects get silently dropped. Solution: native renderer → filter translation → render script.

---

## Supported Software Categories

| Category | Examples |
|----------|----------|
| **Creative** | Blender, GIMP, Inkscape, Krita, Audacity, Kdenlive, Shotcut |
| **Office** | LibreOffice, Zotero, Calibre, Obsidian |
| **Dev Tools** | Jenkins, Gitea, Portainer, pgAdmin |
| **AI/ML** | ComfyUI, Ollama, Stable Diffusion, InvokeAI |
| **Game Dev** | Godot, s&box |
| **Diagramming** | Draw.io, Mermaid, PlantUML, Excalidraw |
| **Communication** | Zoom, Jitsi, Mattermost |
| **Network** | AdGuard Home |
| **Scientific** | FreeCAD, QGIS, ImageJ, ParaView |

---

## Architecture

```
cli-anything-<software>/
├── cli_anything/<software>/
│   ├── cli.py              # Click CLI entry point
│   ├── core/               # Business logic
│   ├── utils/              # repl_skin.py, backend wrappers
│   └── tests/
│       ├── unit/           # Synthetic data tests
│       └── e2e/            # Real software tests
├── setup.py                # pip install -e .
├── SKILL.md                # Agent discovery
└── TEST.md                 # Test plan & results
```

### REPL Interface

Every CLI shares unified REPL (repl_skin.py):
- Branded banner
- Styled prompts with project context
- Command history
- Progress indicators
- `--json` flag on all commands

---

## Integration with Hermes

### Install a CLI for Agent Use

```bash
pip install cli-anything-hub
cli-hub install <software>
```

### Verify Installation

```bash
which cli-anything-<software>
cli-anything-<software> --help
```

### Use in Agent Workflows

```bash
# Always use --json for structured output
cli-anything-<software> --json <command>

# Chain commands in scripts
cli-anything-<software> --json project new -o proj.json
cli-anything-<software> --project proj.json <add-content>
cli-anything-<software> --project proj.json export render output.pdf
```

### For Advanced Users: Build Custom Harnesses

```bash
# Clone CLI-Anything
git clone https://github.com/HKUDS/CLI-Anything.git

# Use the methodology (HARNESS.md) as reference
cat CLI-Anything/cli-anything-plugin/HARNESS.md
```

---

## Pitfalls

1. **Model strength matters** — Weak models produce incomplete CLIs. Use frontier models.
2. **Source code required** — Compiled-only binaries degrade harness quality.
3. **Iterative refinement** — Single pass may not cover everything. Run `/refine` multiple times.
4. **Real software needed** — Some CLIs need the actual app installed (GIMP, Blender, LibreOffice).
5. **Windows users** — Claude Code needs bash. Install Git for Windows or use WSL.

---

## References

- **Repo:** https://github.com/HKUDS/CLI-Anything
- **CLI-Hub:** https://clianything.cc/
- **HARNESS.md:** `cli-anything-plugin/HARNESS.md` (methodology SOP)
- **License:** Apache 2.0
