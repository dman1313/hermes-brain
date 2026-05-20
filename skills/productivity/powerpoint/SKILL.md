---
name: powerpoint
description: "Create, read, edit .pptx decks, slides, notes, templates."
license: Proprietary. LICENSE.txt has complete terms
---

# Powerpoint Skill

## When to use

Use this skill any time a .pptx file is involved in any way — as input, output, or both. This includes: creating slide decks, pitch decks, or presentations; reading, parsing, or extracting text from any .pptx file (even if the extracted content will be used elsewhere, like in an email or summary); editing, modifying, or updating existing presentations; combining or splitting slide files; working with templates, layouts, speaker notes, or comments. Trigger whenever the user mentions "deck," "slides," "presentation," or references a .pptx filename, regardless of what they plan to do with the content afterward. If a .pptx file needs to be opened, created, or touched, use this skill.

## Quick Reference

| Task | Guide |
|------|-------|
| Read/analyze content | `python -m markitdown presentation.pptx` |
| Edit or create from template | Read [editing.md](editing.md) |
| Create from scratch | Read [pptxgenjs.md](pptxgenjs.md) |

---

## Reading Content

```bash
# Text extraction
python -m markitdown presentation.pptx

# Visual overview
python scripts/thumbnail.py presentation.pptx

# Raw XML
python scripts/office/unpack.py presentation.pptx unpacked/
```

---

## Editing Workflow

**Read [editing.md](editing.md) for full details.**

1. Analyze template with `thumbnail.py`
2. Unpack → manipulate slides → edit content → clean → pack

---

## Creating from Scratch

**Read [pptxgenjs.md](pptxgenjs.md) for full details.**

Use when no template or reference presentation is available.

**Zen presentation template:** `templates/zen-deck.js` — reusable starter with Sage Calm palette, dark/light slide alternation, icon rendering (react-icons → sharp → base64), timeline cards, comparison tables, and principle cards. Copy and fill in your slide content.

**Icon caching pattern:** for decks with many icons × colors, split icon rasterization into a separate `render-icons.js` script that writes a JSON cache consumed by `gen-slides.js`. See [references/icon-caching-pattern.md](references/icon-caching-pattern.md). Keeps the slide builder synchronous and amortizes icon render cost across iterations.

## Templates

| Template | Use for |
|----------|---------|
| `templates/zen-deck.js` | Icon-driven decks with zen/minimal aesthetic. Timeline cards, comparison tables, principle summaries. |
| `references/matplotlib-charts-in-slides.md` | Embedding dark-themed matplotlib charts as slide images. |

---

## Design Ideas

**Don't create boring slides.** Plain bullets on a white background won't impress anyone. Consider ideas from this list for each slide.

### Content Density — The #1 Mistake

**When content feels cramped, use MORE slides — never compress.** Dense slides with 0.2" gaps and narrow text boxes are the hallmark of AI-generated decks. Good design means one idea per slide with generous whitespace.

- 10 slides too tight → go to 14–16. Nobody has ever complained a deck had too much breathing room.
- Each slide should communicate one idea. If you're fitting two concepts, split it.
- A slide with 3 spacious cards beats 6 cramped ones.

### Before Starting

- **Pick a bold, content-informed color palette**: The palette should feel designed for THIS topic. If swapping your colors into a completely different presentation would still "work," you haven't made specific enough choices.
- **Dominance over equality**: One color should dominate (60-70% visual weight), with 1-2 supporting tones and one sharp accent. Never give all colors equal weight.
- **Dark/light contrast**: Dark backgrounds for title + conclusion slides, light for content ("sandwich" structure). Or commit to dark throughout for a premium feel.
- **Commit to a visual motif**: Pick ONE distinctive element and repeat it — rounded image frames, icons in colored circles, thick single-side borders. Carry it across every slide.

### Spacing (Hard Rules)

- **0.7" minimum margins** from slide edges on all sides
- **0.3" minimum gaps** between cards, sections, and content blocks
- **0.35"+ preferred** for card gutters in grids
- Leave breathing room — don't fill every inch
- **Text box margin: 0** when aligning with shapes or icons at the same x-position

### Typography

**Choose an interesting font pairing** — don't default to Arial. Pick a header font with personality and pair it with a clean body font.

| Header Font | Body Font |
|-------------|-----------|
| Georgia | Calibri |
| Arial Black | Arial |
| Cambria | Calibri |
| Palatino | Garamond |

| Element | Size |
|---------|------|
| Slide title | 36-44pt bold |
| Section header | 20-24pt bold |
| Body text | 14-16pt |
| Captions | 10-12pt muted |

### Contrast Rules

- **Dark slides**: Body text = white or near-white. Accent text = vibrant color on dark bg (teal, gold). Icons = white inside colored translucent circles. Never use light gray icons on dark backgrounds — invisible on projectors.
- **Light slides**: Body text = near-black (#141A28 or #3D4250). Secondary text = medium gray (#4B5060 minimum). Never use light gray (#999999) for body text — unreadable in meeting rooms.
- **Icons on dark slides**: Always place inside a colored circle (0.85" diameter, 85–90% transparency). White icon centered within.
- **Icons on light slides**: Can use colored icons directly on light backgrounds — sufficient contrast exists.

### Avoid (Common Mistakes)

- **Don't repeat the same layout** — vary columns, cards, and callouts across slides
- **Don't skimp on size contrast** — titles need 36pt+ to stand out from 14-16pt body
- **Don't use low-contrast elements** — icons AND text need strong contrast; no light gray text on dark backgrounds
- **NEVER use accent lines under titles** — hallmark of AI-generated slides; use whitespace instead
- **Don't cram 10 slides when 16 fit better** — if QA reports text cutoff or cramped gaps, expand the deck. More slides with less per slide always beats dense compression. Nobody has ever complained a deck had too much breathing room.
- **Don't use 0.2" gaps for text-heavy cards** — 2×2, 2×3, and 3×2 grids with descriptive text need 0.35" minimum between cards. If gaps need to be 0.2" to fit, you have too much content — reduce text or add a slide.

### Icon Pipeline (react-icons → base64)

Pre-render all icon variants before writing the slide script. This keeps the generation script clean and avoids the shell-quote escaping issues that break inline `kimi -p` / `claude -p` prompts.

Render step:
```bash
NODE_PATH=$(npm root -g) node -e "
const React = require('react');
const ReactDOMServer = require('react-dom/server');
const sharp = require('sharp');
const fa = require('react-icons/fa');
const fs = require('fs');
const icons = {FaShieldAlt: fa.FaShieldAlt, FaServer: fa.FaServer, FaDownload: fa.FaDownload, FaCheckCircle: fa.FaCheckCircle, FaLock: fa.FaLock};
async function ic(IconComponent, color, size) {
  const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(IconComponent, { color, size: String(size) }));
  const pngBuffer = await sharp(Buffer.from(svg)).png().toBuffer();
  return 'image/png;base64,' + pngBuffer.toString('base64');
}
(async () => {
  const results = {};
  for (const [name, comp] of Object.entries(icons)) {
    results[name + '_mint'] = await ic(comp, '#00C853', 256);
    results[name + '_charcoal'] = await ic(comp, '#36454F', 256);
    results[name + '_white'] = await ic(comp, '#FFFFFF', 256);
  }
  fs.writeFileSync('/tmp/icons.json', JSON.stringify(results));
  console.log('Icons rendered: ' + Object.keys(results).length);
})();
"
```

Use in script:
```js
const icons = JSON.parse(fs.readFileSync('/tmp/icons.json', 'utf8'));
function iconData(name) { return icons[name]; }
slide.addImage({ data: iconData('FaShieldAlt_mint'), x: 1, y: 1, w: 0.5, h: 0.5 });
```

---

## QA (Required)

**Assume there are problems. Your job is to find them.**

Your first render is almost never correct. Approach QA as a bug hunt, not a confirmation step. If you found zero issues on first inspection, you weren't looking hard enough.

### Content QA

```bash
python -m markitdown output.pptx
```

Check for missing content, typos, wrong order.

**When using templates, check for leftover placeholder text:**

```bash
python -m markitdown output.pptx | grep -iE "xxxx|lorem|ipsum|this.*(page|slide).*layout"
```

If grep returns results, fix them before declaring success.

### Visual QA

**⚠️ USE SUBAGENTS** — even for 2-3 slides. You've been staring at the code and will see what you expect, not what's there. Subagents have fresh eyes.

Convert slides to images (see [Converting to Images](#converting-to-images)), then use this prompt:

```
Visually inspect these slides. Assume there are issues — find them.

Look for:
- Overlapping elements (text through shapes, lines through words, stacked elements)
- Text overflow or cut off at edges/box boundaries
- Decorative lines positioned for single-line text but title wrapped to two lines
- Source citations or footers colliding with content above
- Elements too close (< 0.3" gaps) or cards/sections nearly touching
- Uneven gaps (large empty area in one place, cramped in another)
- Insufficient margin from slide edges (< 0.5")
- Columns or similar elements not aligned consistently
- Low-contrast text (e.g., light gray text on cream-colored background)
- Low-contrast icons (e.g., dark icons on dark backgrounds without a contrasting circle)
- Text boxes too narrow causing excessive wrapping
- Leftover placeholder content

For each slide, list issues or areas of concern, even if minor.

Read and analyze these images:
1. /path/to/slide-1.jpg (Expected: [brief description])
2. /path/to/slide-2.jpg (Expected: [brief description])

Report ALL issues found, including minor ones.
```

**Note on filenames in the prompt:** verify the actual output of `pdftoppm` before pasting paths into the QA prompt. Default behavior is no zero-padding for <10 slides (`slide-1.jpg`, not `slide-01.jpg`). Hard-coding the wrong pattern wastes a vision call.

### Verification Loop

1. Generate slides → Convert to images → Inspect
2. **List issues found** (if none found, look again more critically)
3. Fix issues
4. **Re-verify affected slides** — one fix often creates another problem
5. Repeat until a full pass reveals no new issues

**Do not declare success until you've completed at least one fix-and-verify cycle.**

---

## Converting to Images

Convert presentations to individual slide images for visual inspection:

```bash
# Use soffice directly — the scripts/office/soffice.py wrapper may not exist
soffice --headless --convert-to pdf output.pptx
pdftoppm -jpeg -r 150 output.pdf slide
```

This creates `slide-1.jpg`, `slide-2.jpg`, etc. **No zero-padding by default** when the deck has fewer than 10 slides. For decks with 10+ slides pdftoppm pads to 2 digits. Don't hard-code `slide-01.jpg` in QA prompts — verify with `ls slide-*.jpg` first and use the actual filenames you see.

To force consistent zero-padding regardless of slide count, add a wrapper rename or use a glob in downstream scripts (`slide-*.jpg`).

To re-render specific slides after fixes:

```bash
pdftoppm -jpeg -r 150 -f N -l N output.pdf slide-fixed
```

---

## Delegation Recipe — When You Build from Scratch

**Do NOT delegate slide generation to CLI coding agents (Kimi, Claude Code, Goose).** The prompt is too long and complex for their tool-call loop — Claude Code stalls silently with zero output for 300s+, Kimi may auth-expire mid-run. Build directly with `execute_code` + `write_file` instead.

1. Render icons to base64 PNGs first (see [Icon Pipeline](#icon-pipeline below)) and save to `/tmp/icons.json`
2. Write the slide generation script with icons loaded via `const icons = JSON.parse(fs.readFileSync('/tmp/icons.json', 'utf8'))`
3. Run with `NODE_PATH=$(npm root -g)` — the shell variable MUST be passed through (claude -p escapes `$` differently than kimi -p)
4. Verify content with `markitdown <output>.pptx`
5. If vision_analyze auth fails, fall back to content-only QA — don't block on visual QA

### Icon Pipeline (react-icons → base64)

Pre-render all icon variants before writing the slide script. This keeps the generation script clean and avoids the shell-quote escaping issues that break inline `kimi -p` / `claude -p` prompts.

Render step:
```bash
NODE_PATH=$(npm root -g) node -e "
const React = require('react');
const ReactDOMServer = require('react-dom/server');
const sharp = require('sharp');
const fa = require('react-icons/fa');
const fs = require('fs');
const icons = {FaShieldAlt: fa.FaShieldAlt, FaServer: fa.FaServer, FaDownload: fa.FaDownload, FaCheckCircle: fa.FaCheckCircle, FaLock: fa.FaLock};
async function ic(IconComponent, color, size) {
  const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(IconComponent, { color, size: String(size) }));
  const pngBuffer = await sharp(Buffer.from(svg)).png().toBuffer();
  return 'image/png;base64,' + pngBuffer.toString('base64');
}
(async () => {
  const results = {};
  for (const [name, comp] of Object.entries(icons)) {
    results[name + '_mint'] = await ic(comp, '#00C853', 256);
    results[name + '_charcoal'] = await ic(comp, '#36454F', 256);
    results[name + '_white'] = await ic(comp, '#FFFFFF', 256);
  }
  fs.writeFileSync('/tmp/icons.json', JSON.stringify(results));
  console.log('Icons rendered: ' + Object.keys(results).length);
})();
"
```

Use in script:
```js
const icons = JSON.parse(fs.readFileSync('/tmp/icons.json', 'utf8'));
function iconData(name) { return icons[name]; }
slide.addImage({ data: iconData('FaShieldAlt_mint'), x: 1, y: 1, w: 0.5, h: 0.5 });
```

---

## Dependencies

- `pip install "markitdown[pptx]"` - text extraction (may need install in active venv)
- `pip install Pillow` - thumbnail grids
- `npm install -g pptxgenjs` - creating from scratch
- `npm install -g react-icons react react-dom sharp` - icons for slides
- LibreOffice Impress (`sudo apt-get install libreoffice-impress`) - PDF conversion via `soffice --headless`
- Poppler (`pdftoppm`) - PDF to images (`sudo apt-get install poppler-utils`)

### Environment Pitfalls

- **pptxgenjs installed globally but not found**: Set `NODE_PATH=$(npm root -g)` when running slide scripts, or use the full global node_modules path. Verify with `NODE_PATH=$(npm root -g) node -e "require('pptxgenjs')"`.
- **`soffice.py` wrapper may not exist**: The `scripts/office/soffice.py` helper is present in some installs but missing in others. Use `soffice --headless --convert-to pdf` directly as the reliable fallback.
- **vision_analyze auth may fail**: If the vision API returns 401, visual QA via subagent will not work. Fall back to content-only QA with `markitdown` + careful heuristic review of spacing math (card x/y positions, gap calculations) in the generation script. Check for: gaps <0.2\" between cards, text boxes narrower than 1.5\" with multiline content, and title-bottom to content-top spacing <0.15\".
