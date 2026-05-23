# Presentation Workflow — Quant NN Scanner Results → Slides

Pattern used to turn batch scan results into a polished pptxgenjs presentation.

## Step 1: Generate Charts with Matplotlib

```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Dark theme matching presentation palette
fig, ax = plt.subplots(figsize=(10, 5.5))
fig.patch.set_facecolor('#080E18')
ax.set_facecolor('#080E18')
# ... plot data ...
fig.savefig('/tmp/chart_name.png', dpi=200, facecolor=fig.get_facecolor(), bbox_inches='tight')
```

Key settings:
- `dpi=200` for crisp rendering at slide scale
- Dark background matching Midnight Quant palette (#080E18)
- `bbox_inches='tight'` to avoid margin clipping
- No plt.show() — use Agg backend

## Step 2: Embed in pptxgenjs Slides

```javascript
// In a slide function:
s.addImage({ path: "/tmp/chart_leaderboard.png", x: 0.1, y: 1.5, w: 9.8, h: 3.6 });
```

Position chart to fill slide width minus minimal margins (0.1" each side on 10" canvas). Adjust height to maintain aspect ratio.

## Step 3: QA Both

- Content QA: `python3 -m markitdown output.pptx`
- Visual QA: `soffice --headless --convert-to pdf` → `pdftoppm -jpeg -r 150` → subagent vision_analyze
- Check for placeholder text: `grep -ciE "xxxx|lorem|placeholder"`
- Verify slide count matches expected

## Common Pitfalls

- **addHeader requires `pres`**: The helper function `addHeader(pres, s, icons, ...)` needs the presentation object as first parameter because `s.addShape(pres.shapes.OVAL, ...)` requires it. If you get `Cannot read properties of undefined (reading 'shapes')`, you forgot to pass `pres`.
- **Chart clipping**: If chart edges are cut, increase `bbox_inches` margin or reduce w/h slightly
- **Slide count creep**: Start with 16-20 slides for a comprehensive deck. Foundation slides (1-10) are reusable across versions.
