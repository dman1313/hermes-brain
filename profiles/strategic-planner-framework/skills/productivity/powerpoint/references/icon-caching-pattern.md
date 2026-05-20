# Icon Caching Pattern for Iterative Deck Development

## Problem

When generating decks with `react-icons` + `sharp`, every run re-renders every icon to PNG. For a deck with 5 icons × 4 colors that's 20 icon renders per run. During iterative development (script error, fix, re-run, repeat) this becomes noticeable wall-clock cost and adds noise to the script.

It also forces `gen-slides.js` to be `async` from the top because icon rendering is async. If you want a clean synchronous slide-builder loop, the async I/O should live elsewhere.

## Pattern

Split icon rasterization from slide generation. Two scripts, one shared JSON cache.

### Step 1: render-icons.js (run once, or whenever icon set changes)

```javascript
const React = require('react');
const ReactDOMServer = require('react-dom/server');
const sharp = require('sharp');
const fa = require('react-icons/fa');
const fs = require('fs');

const icons = {
  FaShieldAlt: fa.FaShieldAlt,
  FaServer: fa.FaServer,
  FaCheckCircle: fa.FaCheckCircle,
  FaLock: fa.FaLock,
  FaDownload: fa.FaDownload,
};

const colors = {
  mint:     '#00C853',
  charcoal: '#36454F',
  white:    '#FFFFFF',
  offwhite: '#F2F2F2',
};

async function iconToBase64Png(IconComponent, color, size = 256) {
  const svg = ReactDOMServer.renderToStaticMarkup(
    React.createElement(IconComponent, { color, size: String(size) })
  );
  const png = await sharp(Buffer.from(svg)).png().toBuffer();
  return 'image/png;base64,' + png.toString('base64');
}

(async () => {
  const out = {};
  for (const [iname, comp] of Object.entries(icons)) {
    for (const [cname, hex] of Object.entries(colors)) {
      out[`${iname}_${cname}`] = await iconToBase64Png(comp, hex);
    }
  }
  fs.writeFileSync('/tmp/icons.json', JSON.stringify(out));
  console.log(`Rendered ${Object.keys(out).length} icon variants`);
})();
```

Run with `NODE_PATH=$(npm root -g) node render-icons.js`. Takes <1 second.

### Step 2: gen-slides.js (consume the cache)

```javascript
const pptxgen = require('pptxgenjs');
const icons = JSON.parse(require('fs').readFileSync('/tmp/icons.json', 'utf8'));

const iconData = name => icons[name];  // simple lookup

// Now slide-building can be entirely sync until the final writeFile
let pres = new pptxgen();
let slide = pres.addSlide();
slide.addImage({ data: iconData('FaShieldAlt_mint'), x: 4.4, y: 0.8, w: 1.2, h: 1.2 });
// ...
await pres.writeFile({ fileName: 'output.pptx' });
```

## When to Use

- Iterating on layout/copy with stable icon set → big win, the icon render is amortized
- Decks with many icon × color variants → cache prevents combinatorial re-render
- When you want the slide builder to read like a static layout, not async I/O

## When Not to Use

- One-shot deck, single run → just inline it, the cache adds a step for no payoff
- Icon set changes every iteration → cache invalidation cost > savings

## Cache Invalidation

Cache key is `<IconName>_<colorName>`. Any time you add a new icon or color, re-run `render-icons.js`. There's no automatic invalidation — keep the script next to `gen-slides.js` and re-run when in doubt. The render is fast enough that this is fine.

## Naming Convention

Use `<IconName>_<colorName>` not `<IconName>_<hex>`. Hex strings in keys make the slide-builder code unreadable. Define a small named-color palette in `render-icons.js` and stick to those names everywhere downstream.
