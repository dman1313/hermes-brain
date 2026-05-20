# Embedding Matplotlib Charts in pptxgenjs Slides

Workflow for data-dense presentations with embedded charts.

## Generate the Chart

```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Match presentation palette
BG = '#080E18'      # dark slide background
TEAL = '#00C6E0'    # accent
GREEN = '#14B87A'   # success
GOLD = '#E69B40'    # warm
GRAY = '#7C8294'    # muted

fig, ax = plt.subplots(figsize=(10, 5.5))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

# Style: no top/right spines, colored bottom left
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color('#1A3350')
ax.spines['bottom'].set_color('#1A3350')
ax.tick_params(colors=GRAY)
ax.grid(axis='x', color='#1A3350', lw=0.5, alpha=0.5)

# Target range zone
ax.axvspan(52, 57, alpha=0.08, color=GREEN)

fig.savefig('/tmp/chart.png', dpi=200, facecolor=fig.get_facecolor(), bbox_inches='tight')
```

## Embed in Slide

```javascript
s.addImage({ path: "/tmp/chart.png", x: 0.1, y: 1.5, w: 9.8, h: 3.6 });
```

## Key Settings

- `dpi=200` — crisp at slide scale on 10" canvas
- `bbox_inches='tight'` — prevents edge clipping
- Dark BG matching presentation palette — seamless integration
- Position at x=0.1, w=9.8 for full-width (minimal edge margin)
