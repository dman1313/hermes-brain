# Pipeline v2 Patterns — Per-Concept Generation

Lessons from the IGCSE Biology pipeline rebuild (2026-05-31).

## What Broke in v1

| Artifact | v1 Approach | Failure Mode |
|----------|-------------|--------------|
| Study guide | `nlm report create --prompt "Focus on X"` | All 10 guides were identical (same md5). `--prompt` is a style hint, not a content filter. |
| Flashcards | `nlm flashcards create --focus "Full Concept Name (Parenthetical)"` | All 79 bytes, empty `cards: []`. Long focus strings cause silent failure. |
| Slides | `nlm slides create --focus "Full Concept Name"` | Only 3/10 generated. Slides fail silently on first attempt. |
| Videos | `nlm video create --focus "Full Concept Name"` | Mostly worked but some got `status: unknown`. |

## v2 Fixes

### Study Guides — Use `nlm notebook query` Instead

```bash
# WRONG — report generator ignores --prompt for content filtering
nlm report create <id> --format "Study Guide" --confirm --prompt "Focus on X"

# RIGHT — query gives focused, citation-rich content
nlm notebook query <id> --json "Focus on X for IGCSE Biology. Give me: 1. Key definitions 2. Core processes 3. Common exam questions 4. Diagrams to memorize 5. Common mistakes."
```

The query response JSON has the answer nested at `.response.answer` or `.value.answer`. Extract and save as markdown. Timeout: set to 120s (queries can take 30-90s).

### Focus Strings — Keep SHORT (2-5 words)

```bash
# WRONG — causes silent failure
nlm video create <id> --focus "Human Organ Systems (Coordination & Excretion)"

# RIGHT — 2-5 words max
nlm video create <id> --focus "Organ Systems"
```

Map each concept to a short focus string in the progress tracker:

```json
{"rank": 9, "name": "Human Organ Systems", "focus": "Organ Systems", "status": "pending"}
```

### Flashcards — String Difficulty, Not Integer

```bash
# WRONG — quiz uses integer, flashcards use string
nlm flashcards create <id> --confirm --difficulty 3

# RIGHT
nlm flashcards create <id> --confirm --difficulty medium --focus "Short Focus"
```

### Slides — Retry Once on Failure

Slides fail silently (`status: "failed"` in studio status). Just retry immediately — it usually works on the second attempt.

### Validation — Check Content, Not Just Existence

```python
import os, json, hashlib

# Minimum file sizes
MIN_VIDEO = 10_000_000   # 10MB
MIN_SLIDES = 100_000     # 100KB
MIN_REPORT = 500         # 500 chars
MIN_FLASHCARDS = 200     # 200 bytes (46 bytes = empty `[]`, 79 bytes = empty from long focus)

# Flashcards: check cards array is non-empty AND file size
fpath = "concept-X-flashcards.json"
fsize = os.path.getsize(fpath)
assert fsize >= MIN_FLASHCARDS, f"Flashcards too small ({fsize} bytes) — likely empty stub"
cards = json.load(open(fpath)).get('cards', [])
assert len(cards) > 0, "Flashcards empty (cards array is [])"

# Study guides: check unique hash (not identical to others)
hash = hashlib.md5(open(fpath, 'rb').read()).hexdigest()
```

**Known empty flashcard sizes:**
- 46 bytes → `[]` (no content at all)
- 79 bytes → `{"cards":[]}` (empty from long `--focus` strings)

### Timeout Handling

After 12 failed attempts (12 hours for hourly pipeline), mark concept as `failed` and move on. Don't loop forever.

## Recommended Generation Order

1. **Study guide** (via query) — fastest, generates locally
2. **Flashcards** — fast, small output
3. **Slides** — medium speed, may need retry
4. **Video** — slowest (3-7 min), most likely to fail

Submit all 4 in one script run. Check for downloads on next run (1 hour later).
