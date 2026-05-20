// Zen Presentation Template — pptxgenjs
// Palette: Sage Calm (dark+light slides, Georgia+Calibri, icon-driven cards)
// CUSTOMIZE: palette colors, slide content arrays, icon choices
//
// Usage: NODE_PATH=$(npm root -g) node this-file.js
// Dependencies: pptxgenjs react-icons react react-dom sharp (all global)

const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");

// ═══════════════════════════════════════════════════════════
// CONFIGURE ICONS — pick from react-icons/fa, /md, /hi, /bi
// ═══════════════════════════════════════════════════════════
const ICON_IMPORTS = {
  // Edit this list to match your slide content
  leaf:    ["fa", "FaLeaf"],
  rocket:  ["fa", "FaRocket"],
  brain:   ["fa", "FaBrain"],
  star:    ["fa", "FaStar"],
  chart:   ["fa", "FaChartLine"],
  shield:  ["fa", "FaShieldAlt"],
  check:   ["fa", "FaCheckCircle"],
  bulb:    ["fa", "FaLightbulb"],
  arrow:   ["fa", "FaArrowRight"],
  update:  ["md", "MdUpdate"],
  magic:   ["md", "MdAutoAwesome"],
};

// Dynamic import helper
function buildIconMap() {
  const map = {};
  for (const [name, [lib, icon]] of Object.entries(ICON_IMPORTS)) {
    const mod = lib === "fa" ? require("react-icons/fa") : require("react-icons/md");
    map[name] = mod[icon];
  }
  return map;
}

// ═══════════════════════════════════════════════════════════
// COLOR PALETTE — customize for your topic
// ═══════════════════════════════════════════════════════════
const C = {
  dark:    "1C2625",    // Dark slide backgrounds
  dark2:   "2D3A39",    // Card background on dark slides
  cream:   "F7F5F0",    // Light slide backgrounds
  sage:    "84B59F",    // Primary accent
  sageDk:  "5C8D7A",    // Darker variant
  euc:     "69A297",    // Secondary
  slate:   "50808E",    // Tertiary
  gold:    "D4A574",    // Warm accent for highlights
  white:   "FFFFFF",
  textDk:  "2D2D2D",    // Text on light backgrounds
  textMd:  "5C5C5C",    // Secondary text
  textLt:  "999999",    // Muted text
  cardBg:  "FFFFFF",    // Card fill on light slides
  gridBg:  "EDEAE4",    // Alternating row / subtle bg
};

// ═══════════════════════════════════════════════════════════
// ICON HELPERS — render to base64 PNG for universal compat
// ═══════════════════════════════════════════════════════════
function renderIconSvg(IconComponent, color = "#000000", size = 256) {
  return ReactDOMServer.renderToStaticMarkup(
    React.createElement(IconComponent, { color, size: String(size) })
  );
}

async function iconToBase64Png(IconComponent, color, size = 256) {
  const svg = renderIconSvg(IconComponent, color, size);
  const pngBuffer = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + pngBuffer.toString("base64");
}

// ═══════════════════════════════════════════════════════════
// OPTION FACTORIES — never reuse option objects (pptxgenjs mutates them)
// ═══════════════════════════════════════════════════════════
const mkShadow = () => ({ type: "outer", blur: 8, offset: 3, color: "000000", opacity: 0.10, angle: 135 });

// ═══════════════════════════════════════════════════════════
// SLIDE TEMPLATES — copy/paste and customize per slide
// ═══════════════════════════════════════════════════════════

// ── TITLE SLIDE (dark bg) ──────────────────────────────────
function addTitleSlide(pres, icons, title, subtitle, tagline) {
  const s = pres.addSlide();
  s.background = { color: C.dark };

  // Decorative zen circles
  s.addShape(pres.shapes.OVAL, {
    x: 7.2, y: -1.5, w: 5, h: 5,
    fill: { color: C.sage, transparency: 92 }
  });
  s.addShape(pres.shapes.OVAL, {
    x: -1.5, y: 3.5, w: 4, h: 4,
    fill: { color: C.euc, transparency: 93 }
  });

  // Center icon
  if (icons.leaf) {
    s.addImage({ data: icons.leaf, x: 4.65, y: 0.5, w: 0.7, h: 0.7 });
  }

  s.addText(title, {
    x: 0.8, y: 1.3, w: 8.4, h: 1.0,
    fontSize: 48, fontFace: "Georgia", color: C.white, bold: true,
    align: "center", margin: 0
  });
  s.addText(subtitle, {
    x: 0.8, y: 2.3, w: 8.4, h: 0.7,
    fontSize: 24, fontFace: "Calibri", color: C.sage, italic: true,
    align: "center", margin: 0
  });

  // Divider
  s.addShape(pres.shapes.LINE, {
    x: 3.5, y: 3.2, w: 3, h: 0,
    line: { color: C.sageDk, width: 1.5 }
  });
  s.addText(tagline, {
    x: 0.8, y: 3.5, w: 8.4, h: 0.5,
    fontSize: 13, fontFace: "Calibri", color: C.textLt,
    align: "center", margin: 0
  });

  // Bottom bar
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 5.2, w: 10, h: 0.425,
    fill: { color: C.sage, transparency: 70 }
  });
}

// ── TIMELINE CARDS (light bg) ──────────────────────────────
// items: [{ name, date, tag, specs, color }]
function addTimelineSlide(pres, icons, title, subtitle, items) {
  const s = pres.addSlide();
  s.background = { color: C.cream };

  s.addImage({ data: icons.rocket, x: 0.6, y: 0.35, w: 0.45, h: 0.45 });
  s.addText(title, {
    x: 1.2, y: 0.3, w: 8, h: 0.6,
    fontSize: 32, fontFace: "Georgia", color: C.textDk, bold: true, margin: 0
  });
  s.addText(subtitle, {
    x: 1.2, y: 0.85, w: 8, h: 0.4,
    fontSize: 14, fontFace: "Calibri", color: C.textMd, margin: 0
  });

  const cardW = 2.1;
  const totalW = items.length * cardW;
  const gap = (9.0 - totalW) / (items.length - 1);
  const startX = 0.5;

  items.forEach((item, i) => {
    const cx = startX + i * (cardW + gap);

    s.addShape(pres.shapes.RECTANGLE, {
      x: cx, y: 1.5, w: cardW, h: 2.9,
      fill: { color: C.cardBg }, shadow: mkShadow()
    });
    // Accent bar
    s.addShape(pres.shapes.RECTANGLE, {
      x: cx, y: 1.5, w: cardW, h: 0.06,
      fill: { color: item.color || C.sage }
    });
    s.addText(item.name, {
      x: cx + 0.15, y: 1.7, w: cardW - 0.3, h: 0.5,
      fontSize: 24, fontFace: "Georgia", color: C.textDk, bold: true, margin: 0
    });
    // Tag badge
    s.addShape(pres.shapes.RECTANGLE, {
      x: cx + 0.15, y: 2.18, w: 0.95, h: 0.22,
      fill: { color: item.color || C.sage }
    });
    s.addText(item.tag || "", {
      x: cx + 0.15, y: 2.15, w: 1.8, h: 0.3,
      fontSize: 8, fontFace: "Calibri", color: C.white, bold: true, margin: 0
    });
    s.addText(item.date, {
      x: cx + 0.15, y: 2.55, w: cardW - 0.3, h: 0.3,
      fontSize: 11, fontFace: "Calibri", color: item.color || C.sage, bold: true, margin: 0
    });
    s.addText(item.specs, {
      x: cx + 0.15, y: 2.9, w: cardW - 0.3, h: 1.3,
      fontSize: 11, fontFace: "Calibri", color: C.textMd, margin: 0,
      lineSpacingMultiple: 1.4
    });
  });

  // Arrows between cards
  for (let i = 0; i < items.length - 1; i++) {
    const ax = startX + (i + 0.5) * (cardW + gap) + cardW / 2 - 0.12;
    s.addImage({ data: icons.arrow, x: ax, y: 2.8, w: 0.25, h: 0.25 });
  }
}

// ── COMPARISON TABLE SLIDE (light bg) ──────────────────────
// headers: ["Col1", "Col2", ...]
// rows: [["val", "val", ...], ...]
// colWidths: [2.0, 2.4, 2.0, 3.2] — must sum to ~9.4
function addTableSlide(pres, icons, title, subtitle, headers, rows, colWidths) {
  const s = pres.addSlide();
  s.background = { color: C.cream };

  s.addImage({ data: icons.chart, x: 0.6, y: 0.35, w: 0.45, h: 0.45 });
  s.addText(title, {
    x: 1.2, y: 0.3, w: 8, h: 0.6,
    fontSize: 32, fontFace: "Georgia", color: C.textDk, bold: true, margin: 0
  });
  s.addText(subtitle, {
    x: 1.2, y: 0.85, w: 8, h: 0.4,
    fontSize: 14, fontFace: "Calibri", color: C.textMd, italic: true, margin: 0
  });

  const allRows = [headers, ...rows];
  const data = allRows.map((row, ri) =>
    row.map((cell, ci) => ({
      text: cell,
      options: {
        fill: { color: ri === 0 ? C.sage : (ri % 2 === 0 ? C.gridBg : C.white) },
        color: ri === 0 ? C.white : (ci === 1 ? C.sageDk : C.textDk),
        bold: ri === 0 || ci === 1,
        fontSize: ri === 0 ? 11 : 10,
        fontFace: "Calibri",
        align: "center",
        valign: "middle",
      }
    }))
  );

  const rowH = [0.38, ...rows.map(() => 0.42)];
  s.addTable(data, {
    x: 0.3, y: 1.5, w: 9.4, colW: colWidths,
    border: { pt: 0.5, color: C.gridBg },
    rowH,
  });
}

// ── PRINCIPLE CARDS SLIDE (dark bg, 3 cards) ───────────────
// principles: [{ icon: icons.xxx, title: "Title", body: "Text" }]
function addPrinciplesSlide(pres, icons, title, subtitle, principles) {
  const s = pres.addSlide();
  s.background = { color: C.dark };

  // Decorative circle + icon
  s.addShape(pres.shapes.OVAL, {
    x: 0.6, y: 0.5, w: 1.6, h: 1.6,
    fill: { color: C.sage, transparency: 85 }
  });
  s.addImage({ data: icons.leaf, x: 1.1, y: 0.95, w: 0.6, h: 0.6 });

  s.addText(title, {
    x: 2.5, y: 0.7, w: 7, h: 0.7,
    fontSize: 36, fontFace: "Georgia", color: C.white, bold: true, margin: 0
  });
  s.addText(subtitle, {
    x: 2.5, y: 1.4, w: 7, h: 0.5,
    fontSize: 18, fontFace: "Calibri", color: C.sage, italic: true, margin: 0
  });

  const cardH = 0.9;
  const startY = 2.15;
  const gap = 0.20; // minimum 0.2" between cards

  principles.forEach((p, i) => {
    const py = startY + i * (cardH + gap);

    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.5, y: py, w: 9, h: cardH,
      fill: { color: C.dark2 }
    });
    s.addImage({ data: p.icon, x: 0.75, y: py + 0.2, w: 0.5, h: 0.5 });
    s.addText(p.title, {
      x: 1.45, y: py + 0.08, w: 3, h: 0.38,
      fontSize: 18, fontFace: "Georgia", color: C.gold, bold: true, margin: 0
    });
    s.addText(p.body, {
      x: 1.45, y: py + 0.45, w: 7.7, h: 0.4,
      fontSize: 12, fontFace: "Calibri", color: C.textMd, margin: 0
    });
  });

  // Footer bar
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 5.2, w: 10, h: 0.425,
    fill: { color: C.sage, transparency: 70 }
  });
}

// ═══════════════════════════════════════════════════════════
// MAIN — wire up your slides here
// ═══════════════════════════════════════════════════════════
async function main() {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_16x9";
  pres.author = "Your Name";
  pres.title = "Your Presentation Title";

  // Render all icons
  const IconComponents = buildIconMap();
  const icons = {};
  for (const [name, Comp] of Object.entries(IconComponents)) {
    icons[name] = await iconToBase64Png(Comp, `#${C.sage}`, 256);
  }

  // ══ ADD YOUR SLIDES HERE ═════════════════════════════════

  // Example: Title slide
  // addTitleSlide(pres, icons, "YOUR TITLE", "Your Subtitle", "Your Tagline");

  // Example: Timeline
  // addTimelineSlide(pres, icons, "Timeline Title", "Subtitle", [
  //   { name: "Item 1", date: "Jan 2025", tag: "TAG", specs: "Details\nMore details", color: C.sage },
  //   { name: "Item 2", date: "Apr 2025", tag: "TAG", specs: "Details\nMore details", color: C.gold },
  // ]);

  // Example: Comparison table
  // addTableSlide(pres, icons, "Table Title", "Subtitle",
  //   ["Col 1", "Col 2", "Col 3", "Col 4"],
  //   [["Val", "Val", "Val", "Val"], ["Val", "Val", "Val", "Val"]],
  //   [2.0, 2.4, 2.0, 3.2]
  // );

  // Example: Principles (dark bg summary)
  // addPrinciplesSlide(pres, icons, "Summary Title", "Tagline", [
  //   { icon: icons.bulb, title: "Principle 1", body: "Description text here." },
  //   { icon: icons.shield, title: "Principle 2", body: "Description text here." },
  //   { icon: icons.leaf, title: "Principle 3", body: "Description text here." },
  // ]);

  // ═════════════════════════════════════════════════════════

  await pres.writeFile({ fileName: "Presentation.pptx" });
  console.log("✅ Presentation saved: Presentation.pptx");
}

main().catch(e => { console.error(e); process.exit(1); });
