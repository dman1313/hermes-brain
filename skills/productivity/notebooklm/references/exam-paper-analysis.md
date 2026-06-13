# Exam Paper Cross-Reference Analysis

Workflow for extracting concepts from an exam paper and cross-referencing them against a NotebookLM notebook containing past papers.

## When to Use

- Student takes a practice paper and wants to know which concepts are highest-yield
- Comparing a new paper against historical frequency to prioritize revision
- Building a concept-frequency ranking across all past papers in a notebook

## Steps

### 1. Extract Concepts from the Paper

For scanned PDFs (no text layer):
```bash
uv pip install pymupdf
```
```python
import fitz, os
doc = fitz.open("paper.pdf")
os.makedirs("/tmp/paper_pages", exist_ok=True)
for i in range(len(doc)):
    pix = doc[i].get_pixmap(dpi=200)
    pix.save(f"/tmp/paper_pages/page_{i+1:02d}.png")
```

Then use `vision_analyze` on each page to extract:
- Question number and marks
- All biological concepts/topics tested
- Diagram descriptions

Skip non-question pages (command word references, cover pages).

### 2. Identify Core Concepts

Group extracted content into ~5-8 major concepts. For IGCSE Biology, typical groupings:
- Characteristics of Life (MRS GREN)
- Biological Molecules (carbs, lipids, proteins, enzymes)
- Cell Structure (prokaryotic vs eukaryotic, organelles)
- Movement In/Out of Cells (diffusion, osmosis, active transport)
- Microscopy & Magnification calculations
- Surface Area to Volume Ratio

### 3. Query NotebookLM Per Concept

Run ONE focused query per concept. Keep queries specific and single-topic.

**Good:** "Which past papers test osmosis and tonicity (hypertonic/hypotonic)?"
**Bad:** "Which past papers test osmosis and diffusion and SA:V ratio and cell structure?"

Multi-part queries timeout at ~60s. Run separate queries and synthesize.

### 4. Build Frequency Table

For each concept, count how many distinct past papers test it. Format:

| Concept | Papers | Priority |
|---------|--------|----------|
| Biological Molecules | ~18 papers | ⭐⭐⭐ |
| Osmosis | ~12 papers | ⭐⭐⭐ |
| Prokaryotic vs Eukaryotic | ~10 papers | ⭐⭐⭐ |

### 5. Deliver Analysis

Present:
1. All concepts from the paper with question mapping
2. Frequency ranking from most to least tested
3. Which specific papers test each concept (year/session)
4. Priority ranking for revision focus

## Output Format Notes

- Use Telegram-compatible formatting (no markdown tables — use bullet lists)
- Group by concept, not by question
- Include specific paper years/sessions for reference
- Star ratings for priority (⭐⭐⭐ = very high, ⭐⭐ = high, ⭐ = medium)
