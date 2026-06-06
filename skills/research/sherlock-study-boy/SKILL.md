---
name: sherlock-study-boy
description: "Sherlock Study Boy Agent — 12-step NotebookLM study package generator. Takes any NotebookLM notebook with uploaded course materials (tests, quizzes, syllabi, notes) and produces a complete study package using NotebookLM's native studio generators (reports, videos, slides, flashcards, quizzes) supplemented with text queries for answer keys and concept analysis. Triggers on 'sherlock study boy', 'study boy agent', 'generate study package'."
---

# Sherlock Study Boy Agent

12-step agent workflow that orchestrates NotebookLM to produce a complete study package from uploaded course materials.

## Prerequisites

- `nlm` CLI installed and authenticated (`nlm login --check`)
- NotebookLM notebook with uploaded sources (tests, quizzes, syllabi, answer keys, teacher notes, review sheets)
- **Direct VPS terminal session** — the workflow requires real shell access. Cron jobs and sandbox sessions may lack the terminal tool. If `nlm` commands fail, switch to a VPS SSH session.

## Execution Notes

This skill needs a session with working terminal access to run `nlm` commands.
- **Preferred:** SSH into the VPS and trigger the skill from there
- **Fallback:** Run the first two commands manually (`nlm login --check`, `nlm notebook get <id>`) and paste the output — the rest of the flow can be orchestrated once the notebook context is confirmed

## Usage

```
Load sherlock-study-boy
Target notebook: <notebook-id>  (e.g., 90d50a5a-a276-409a-9574-936bba1c038e)
```

Output saves to `~/study-packages/<notebook-id>/`.

## Core Rule

**Use NotebookLM's native studio generators** — not text queries that describe study materials. The native generators produce real artifacts (flashcard decks, quizzes, slideshows, videos, audio overviews, reports, infographics, mind maps, data tables). The agent's job is orchestration: kick off native generation, poll for completion, download, organize.

**What is native vs text-query:**
| Artifact | Native command | Do NOT query for |
|----------|---------------|-----------------|
| Flashcards | `nlm flashcards create <id>` | "create flashcards for concept X" |
| Quiz | `nlm quiz create <id>` | "create a quiz for concept X" |
| Slides | `nlm slides create <id>` | "create slideshow content for concept X" |
| Video | `nlm video create <id>` | "create a video script for concept X" |
| Audio/Podcast | `nlm audio create <id>` | N/A |
| Report | `nlm report create <id>` | "write a study guide for concept X" |
| Infographic | `nlm infographic create <id>` | N/A |
| Mind map | `nlm mindmap create <id>` | N/A |
| Data table | `nlm data-table create <id>` | N/A |

**Text queries are only for:** initial concept analysis (Step 2), answer keys (no native generator), and quality checks.

## The 12 Steps

### Step 1 — Read the Notebook Title

```bash
nlm notebook get <notebook-id>
```

Extract the title. It tells you: subject, course, exam type, student level.

Example: `Biology IGCSE Year 1 Test Review` → Biology, IGCSE, Year 1.

**Do not proceed to resource creation yet.** Title first, then move to Step 2.

### Step 2 — Analyze Sources for Top 10 Concepts

Query NotebookLM:

```
Please analyze all uploaded sources in this notebook, including tests, quizzes, answer keys, review sheets, syllabi, teacher notes, and study materials.

Based on the uploaded assessment materials, identify the top 10 concepts that appear most often across the tests.

For each concept, include:
1. The concept name
2. A short student-friendly explanation
3. The percentage of tests or assessment materials where this concept appears
4. Why this concept is important
5. Common question types connected to this concept
6. Any diagrams, vocabulary, or skills students need to know

Rank the concepts from most frequently tested to least frequently tested.
```

Command:
```bash
nlm notebook query <notebook-id> "<prompt>"
```

Save the response as `step2-top10-concepts.md`.

### Step 3 — Store the Top 10 Concepts Table

Parse the NotebookLM response into a structured table:

| Rank | Concept | Percentage | Why it matters |
|------|---------|------------|----------------|
| 1 | Cell structure | 80% | Foundational biology concept |
| 2 | Enzymes | 70% | Common in process and graph questions |

Save as `step3-concepts-table.md`. This is the master plan — every subsequent step references it.

### Step 4 — Generate All Native Artifacts (Notebook-Level)

Native generators produce **one artifact per notebook**, not per concept. Generate all artifacts sequentially (shell `&` backgrounding breaks in foreground terminal mode). Send each create command in order — the CLI returns immediately after submitting the job.

**Kick off all generations sequentially:**

```bash
# Report — study guide format
nlm report create <notebook-id> --format "Study Guide" --confirm

# Video
nlm video create <notebook-id> --confirm

# Slides
nlm slides create <notebook-id> --confirm

# Flashcards (difficulty is a STRING — pass medium)
nlm flashcards create <notebook-id> --confirm --difficulty medium

# Quiz (difficulty is an INTEGER, not a word — pass 3 for medium)
nlm quiz create <notebook-id> --confirm --count 15 --difficulty 3

# Audio overview (podcast-style) — may timeout on first attempt; retry if so
nlm audio create <notebook-id> --confirm --format deep_dive --length long

# Mind map
nlm mindmap create <notebook-id> --confirm

# Infographic
nlm infographic create <notebook-id> --confirm
```

**NOTE on video and slides:** These are frequently rate-limited by NotebookLM's API (`Rate limited — API error (code 8)`). If they fail, continue with other artifacts and retry after 2-3 minutes. If they fail 3+ times, skip them — they can be generated manually later. Do not loop indefinitely.

**Poll until complete:**
```bash
nlm studio status <notebook-id>
```

Poll every 15-30 seconds. Generation takes 1-5 minutes per artifact. Some may complete before others.

### Step 5 — Download All Artifacts

Once `nlm studio status` shows all artifacts complete, download each one using the `--id` flag (NOT positional — the artifact ID is passed via `--id`):

```bash
# artifact-id is passed via --id flag, NOT as a positional argument
nlm download report <notebook-id> --id <artifact-id> --output report-study-guide.md
nlm download video <notebook-id> --id <artifact-id> --output video.mp4
nlm download slide-deck <notebook-id> --id <artifact-id> --output slides.pdf
nlm download flashcards <notebook-id> --id <artifact-id> --output flashcards.pdf
nlm download quiz <notebook-id> --id <artifact-id> --output quiz.pdf
nlm download audio <notebook-id> --id <artifact-id> --output audio-overview.m4a
nlm download mind-map <notebook-id> --id <artifact-id> --output mindmap.pdf
nlm download infographic <notebook-id> --id <artifact-id> --output infographic.pdf
```

**NOTE:** Reports download as `.md` by default (not `.pdf`). Mind map download uses `mind-map` (hyphenated) as the subcommand. If `nlm studio status` lists a mind map's `type` as `"flashcards"` (a known CLI quirk), try downloading it via the flashcards downloader with `--id <mind-map-artifact-id>`.

**If download fails** with an error, first re-check studio status — the artifact may still be generating. Poll again and retry.

**NOTE on audio:** NotebookLM delivers AAC in an MP4 container — the CLI rejects `.mp3` suffix. Use `.m4a` extension, then transcode with `ffmpeg -i audio.m4a -acodec libmp3lame -q:a 2 audio.mp3` if you need MP3 format. Paid tier may generate two audio overviews — download both.

### Step 6 — Generate Concept-Specific Answer Keys

No native generator exists for answer keys. Query NotebookLM for each concept:

```bash
nlm notebook query <notebook-id> "Create an answer key for the top 10 concepts. For each concept, include: 1. 5 key questions with correct answers 2. Short explanations 3. Common wrong answers 4. What the student should review if they got it wrong. Concepts: [list from step 3]"
```

Save as `answer-keys.md`. One query covers all 10 concepts — don't waste queries doing them individually.

### Step 7 — Quality Check

Verify all downloaded artifacts exist and are non-empty:

```bash
ls -la ~/study-packages/<notebook-id>/
```

Expected artifacts:
1. report-study-guide.pdf (report)
2. video.mp4 (video)
3. slides.pdf (slides)
4. flashcards.pdf (flashcards)
5. quiz.pdf (quiz)
6. audio-overview.m4a (audio)
7. mindmap.pdf (mind map)
8. infographic.pdf (infographic)
9. answer-keys.md (text query)

Re-run any missing generation commands.

### Step 9 — Per-Concept Deep Dive (Optional)

After the notebook-level package is done, you can generate **focused artifacts per concept** using the `--focus` parameter. This filters the notebook's sources (often 95+) to a single topic.

**Only generate per-concept content when the user explicitly asks.** Do not assume they want this.

**Supported per-concept generators:**

| Artifact | Command with focus | Notes |
|----------|-------------------|-------|
| Video | `nlm video create <id> --confirm --focus "Short Topic"` | Keep focus SHORT (2-5 words max). Long focus strings cause silent failure. |
| Slides | `nlm slides create <id> --confirm --focus "Short Topic"` | Same focus length advice. Slides can fail on first attempt — retry immediately works. |
| Study Guide | `nlm notebook query <id> --json "Focus on [topic] for IGCSE..."` | Use query, NOT report create. Save response `.value.answer` as markdown. |
| Flashcards | `nlm flashcards create <id> --confirm --difficulty medium --focus "Short"` | `--difficulty` takes STRING (easy/medium/hard), NOT integer. Keep focus short. |

**Per-concept workflow:**

1. Create `concepts/` dir + `concept-progress.json` with all 10 concepts and their status
2. Start report (seconds), then slides, then video (3-7 min) — slowest last
3. Poll every 60s (videos/slides filter all sources and take longer than notebook-level)
4. **"Unknown" status fix:** Focused videos may show `status: "unknown"` after processing. **Wait 3-5 minutes and poll again** — the original usually completes in the background. Do NOT immediately retry generation; a new retry often fails while the original succeeds. Only generate a new video if the original shows `failed` after 10+ minutes.
5. Space concept generations 1 hour apart to avoid rate limits and let each batch fully render.
6. **CRITICAL: Use SHORT focus strings (2-5 words max).** Store a separate `focus` field in concept-progress.json. Full concept names like "Human Organ Systems (Coordination & Excretion)" cause silent failures (empty flashcards, unknown videos). Use "Organ Systems" instead.
7. **Use `nlm notebook query` for study guides, NOT `nlm report create --prompt`.** The `--prompt` flag is treated as a style suggestion and produces generic content. Query returns focused, citation-rich content.

**Automation via cron:** For 10-concept pipelines, write a no-agent cron script that reads concept-progress.json, generates the next pending concept, polls for completion, downloads, and updates progress. Deliver output to `concepts/` dir. The script keeps going until all concepts are marked `"done"`. **Tip:** The pipeline script uses a fire-and-forget pattern (Phase 1 submits, Phase 2 checks next run), but you can run Phase 1 and then immediately poll `nlm studio status` + download in the same session — no need to wait for the next cron cycle. Just run the script, wait 3-5 minutes, then manually check status and download completed artifacts.

**Progress tracker format:**
```json
{
  "notebook": "<id>",
  "title": "Subject",
  "current_concept": 1,
  "total_concepts": 10,
  "concepts": [
    {"rank": 1, "name": "Topic", "percentage": "100%", "status": "done"},
    {"rank": 2, "name": "Topic", "percentage": "90%", "status": "pending"}
  ]
}
```

Status values: `"pending"`, `"generating"`, `"done"`, `"failed"`.

### Step 8 — Final Study Package Index

Query NotebookLM for a summary:

```bash
nlm notebook query <notebook-id> "Create a final study package index. List the top 10 concepts by test frequency. For each, include the concept name, percentage of appearance, and a student-friendly summary. At the end, create a suggested 10-day study plan where the student reviews one concept per day."
```

Save as `study-package-index.md`.

## Output Structure

### Notebook-Level Package

```
~/study-packages/<notebook-id>/
├── step1-notebook-title.md
├── step2-top10-concepts.md
├── step3-concepts-table.md
├── report-study-guide.md        # native report (.md, not .pdf)
├── video.mp4                    # native video
├── slides.pdf                   # native slides
├── flashcards.pdf               # native flashcards
├── quiz.pdf                     # native quiz
├── audio-overview.m4a           # native audio/podcast (.m4a, not .mp3)
├── audio-overview-2.m4a         # 2nd audio (paid tier only)
├── mindmap.pdf                  # native mind map
├── infographic.pdf              # native infographic
├── answer-keys.md               # text query (no native equivalent)
├── study-package-index.md
├── progress.json                # notebook-level step tracker
└── concepts/                    # per-concept focused artifacts
    ├── concept-1-<name>-video.mp4
    ├── concept-1-<name>-slides.pdf
    ├── concept-1-<name>.md          # focused study guide
    └── ...concept-10
    
    # Top-level tracker for concept pipeline
    concept-progress.json
```

## Notebook-Level vs Per-Concept Generation

### Notebook-Level (Step 4)

Native generators produce **one artifact per notebook** without focus. Generate one complete set covering all content:

```bash
nlm video create <id> --confirm
nlm slides create <id> --confirm
nlm report create <id> --format "Study Guide" --confirm
nlm flashcards create <id> --confirm --difficulty medium
nlm quiz create <id> --confirm --count 15 --difficulty 3
```

### Per-Concept Generation (Step 9 — optional deep-dive)

After the notebook-level package is complete, you can generate **focused artifacts per concept** using the `--focus` parameter. This produces concept-specific video, slides, and report that narrow the notebook's 95+ sources to a single topic.

**Supported per-concept generators:**

| Artifact | Command with focus | Notes |
|----------|-------------------|-------|
| Video | `nlm video create <id> --confirm --focus "Short Topic"` | Keep focus SHORT (2-5 words max). Long focus strings cause silent failure. |
| Slides | `nlm slides create <id> --confirm --focus "Short Topic"` | Same focus length advice. Slides can fail on first attempt — retry immediately works. |
| Study Guide | `nlm notebook query <id> --json "Focus on [topic] for IGCSE..."` | Use query, NOT report create. Save response `.value.answer` as markdown. |
| Flashcards | `nlm flashcards create <id> --confirm --difficulty medium --focus "Short"` | `--difficulty` takes STRING (easy/medium/hard), NOT integer. Keep focus SHORT (2-5 words). |

**Do NOT use `nlm report create` for per-concept study guides.** The `--prompt` parameter is treated as a style suggestion, not a content filter — reports always cover ALL notebook sources generically. Use `nlm notebook query` instead:

```bash
nlm notebook query <notebook-id> --json \
    "Focus on <topic> for IGCSE Biology exam preparation. Give me: 1. Key definitions 2. Core processes 3. Common exam questions 4. Diagrams to memorize 5. Common mistakes."
```

Then extract the answer from the JSON response:
```python
import json
data = json.loads(response)
answer = data.get('response', {}).get('answer', '') or data.get('value', {}).get('answer', '')
```

**Per-concept workflow:**

1. Create `concepts/` directory under the notebook's study-packages folder
2. Generate study guide via `nlm notebook query` (fastest, most reliable)
3. Generate flashcards via `nlm flashcards create --difficulty medium --focus "Short"`
4. Generate slides via `nlm slides create --focus "Short"` (may need retry)
5. Generate video via `nlm video create --focus "Short"` (slowest, 3-7 min)
6. Use a progress tracker (`concept-progress.json`) with status per concept
7. **Validate artifacts on download** — check min file sizes (video >10MB, slides >100KB, study guide >500 chars, flashcards non-empty cards array). Don't trust "file exists" alone.
8. **Known issue:** Focused videos may show `status: "unknown"` after 3-5 minutes of processing. If download fails at this point, retry with a shorter `--focus` string (2-3 words max). The original may complete in the background — check `nlm studio status` periodically.
9. Space concept generation sessions 1 hour apart to avoid rate limits and let each set fully render.

**Automated pipeline:** See `~/.hermes/scripts/concept-pipeline.sh` for a working cron-compatible script that implements this full workflow with validation, retry logic, and timeout handling.

### When to use which

- **Notebook-level:** Student wants a general study package on the full subject.
- **Per-concept:** Student wants deep-dive materials on specific weak topics identified from the top-10 analysis.

## Progress Tracking

### Notebook-Level Progress

Use `progress.json` to survive session restarts for the 12-step notebook-level pipeline:
```json
{
  "notebook_id": "90d50a5a-...",
  "title": "Biology IGCSE Year 1 Test Review",
  "current_step": 5,
  "current_concept": 3,
  "completed_concepts": [1, 2],
  "concepts": [
    {"rank": 1, "name": "Cell structure", "percentage": "80%"},
    ...
  ]
}
```

Read this file before each run to resume where you left off.

### Per-Concept Pipeline Progress

When running the 10-concept deep-dive (Step 9), use a separate `concept-progress.json` in the notebook root:

```json
{
  "notebook": "e621431b-...",
  "title": "IGCSE Biology",
  "current_concept": 1,
  "total_concepts": 10,
  "concepts": [
    {"rank": 1, "name": "Experimental Design (CORMS)", "percentage": "100%", "status": "done"},
    {"rank": 2, "name": "Genetics", "percentage": "90%", "status": "generating"},
    {"rank": 3, "name": "Respiration", "percentage": "85%", "status": "pending"}
  ]
}
```

Status values: `"pending"`, `"generating"`, `"done"`, `"failed"`.

## Pitfalls

- **Per-concept generation:** See `references/pipeline-v2-patterns.md` for the recommended approach. Key: use `nlm notebook query` for study guides (not `nlm report create`), keep focus strings to 2-5 words, and validate artifact content not just file existence.

- **Focused video "unknown" status:** Videos generated with `--focus` may show `status: "unknown"` in studio status after 3-5 minutes. **Do NOT immediately retry with a new generation.** In practice, the original video almost always completes in the background — a retry with shorter focus will often **fail** while the original succeeds. Instead: wait 3-5 minutes and poll `nlm studio status` again. Only retry generation if the original shows `status: "failed"` after 10+ minutes. If the original shows `completed`, download it — even if a retry also exists and failed.
- **Slides can fail on first attempt (non-rate-limit):** Slides sometimes fail with `status: "failed"` for no clear reason. Unlike rate-limited errors, just retry immediately — it usually works on the second attempt.
- **Generation takes 3-7 minutes per artifact for focused videos/slides** (longer than notebook-level because they filter 95+ sources). Report is fastest (~seconds). Poll every 60 seconds for video/slides, not 15-30.
- **Generation takes 1-5 minutes per artifact.** Always poll with `nlm studio status <id>` before trying to download. Don't assume instant availability.
- **Run generation commands SEQUENTIALLY, not with shell `&` backgrounding.** The Hermes terminal foreground mode does not support `&` (background jobs). Each `nlm create` command returns immediately after submitting the job — just run them one after another.
- **Rate limits — paid vs free:** Video and slides are frequently rate-limited by NotebookLM's API (`Rate limited — API error (code 8)`). On free tier, wait 5+ minutes between retries or skip for the session. On paid tier, rate limits ease after ~10-15 minutes. Slides can also fail silently (`status: \"failed\"` in studio status) — just retry immediately, it usually works on the second attempt.
- **Quiz `--difficulty` takes an INTEGER**, not a string like `"medium"`. Use `--difficulty 3` for medium difficulty. Using `"medium"` causes an "invalid value for integer" error.
- **Download artifact IDs are passed via `--id` flag**, NOT as positional arguments. The correct syntax is `nlm download report <notebook-id> --id <artifact-id>` (not `nlm download report <notebook-id> <artifact-id>`).
- **Mind map download uses `mind-map`** (hyphenated subcommand), not `mindmap`. And in `nlm studio status`, mind maps may appear with `type: "flashcards"` (a CLI quirk). If the regular mind-map download fails, try downloading via the flashcards downloader with `nlm download flashcards <notebook-id> --id <mind-map-id>`.
- **Audio creation can timeout with `ReadTimeout` on the first attempt.** Simply retry — it usually works on the second try.
- **Reports download as `.md`** by default, not `.pdf`. This is correct — they're markdown text files.
- **Free tier ~50 queries/day.** Each native generation counts as a query. 8 artifacts + 2-3 text queries = ~11 queries per package. Don't waste queries generating duplicates.
- **Auth expiry:** Sessions last ~20 min. Run `nlm login --check` before every batch. Re-auth via Mac + SCP if expired.
- **Free vs paid tier:** Free tier ~50 queries/day. Paid tier generates faster and allows 2 audio overviews per notebook. Video/slides may still hit per-minute burst limits even on paid tier — wait 10-15 min between retries.

## Reference Files

- `references/nlm-cli-quirks.md` — Exact error messages, download syntax quirks, rate-limit strategies, and known CLI bugs collected from real sessions. Read this when you hit an unexpected nlm error.
