# NLM CLI Quirks & Error Reference

Collected from real sessions. Add to this file as new quirks surface.

## Generation Commands

| Artifact | Command | Notes |
|----------|---------|-------|
| Report | `nlm report create <id> --format "Study Guide" --confirm` | Default output is `.md` |
| Video | `nlm video create <id> --confirm` | Frequently rate-limited |
| Slides | `nlm slides create <id> --confirm` | Frequently rate-limited |
| Flashcards | `nlm flashcards create <id> --confirm --difficulty 3` | `--difficulty` takes INTEGER (3=medium) |
| Quiz | `nlm quiz create <id> --confirm --count 15 --difficulty 3` | `--difficulty` takes INTEGER |
| Audio | `nlm audio create <id> --format deep_dive --length long` | May timeout on 1st attempt |
| Mind map | `nlm mindmap create <id> --confirm` | |
| Infographic | `nlm infographic create <id> --confirm` | |
| Data table | `nlm data-table create <id> --confirm` | |

## Download Syntax (important)

Artifact IDs are ALWAYS passed via `--id` flag, NOT positional:

```bash
# CORRECT
nlm download report <notebook-id> --id <artifact-id> --output report.md

# WRONG (will error)
nlm download report <notebook-id> <artifact-id> --output report.pdf
```

Subcommands for download:
- Report → `nlm download report`
- Video → `nlm download video`
- Slides → `nlm download slide-deck`
- Flashcards → `nlm download flashcards`
- Quiz → `nlm download quiz`
- Audio → `nlm download audio`
- Mind map → `nlm download mind-map` (hyphenated!)
- Infographic → `nlm download infographic`

## Studio Status Quirks

Studio status may list a mind map's `type` as `"flashcards"` instead of `"mind_map"` due to a CLI quirk. If `nlm download mind-map` fails, try:
```bash
nlm download flashcards <notebook-id> --id <mind-map-artifact-id>
```

## Audio Download — .m4a Required

NotebookLM delivers AAC audio in an MP4 container. The CLI rejects `.mp3`:
```
Error: NotebookLM delivers AAC audio in an MP4 container; cannot honor '.mp3' suffix.
```
**Fix:** Use `.m4a` suffix:
```bash
nlm download audio <notebook-id> --id <artifact-id> --output audio-overview.m4a
```
**To get `.mp3`:** Download as `.m4a` then transcode with ffmpeg:
```bash
ffmpeg -i audio-overview.m4a -acodec libmp3lame -q:a 2 audio-overview.mp3
```

### Paid-Tier Behaviour

Paid NotebookLM tier can generate multiple audio overviews (two `type: "audio"` entries in studio status). Both are distinct — download each one. Video and slide creation still subject to per-minute burst rate limits even on paid tier.

## Known Errors

### Rate Limited — Video/Slides

```
Error: Rate limited — API error (code 8):
type.googleapis.com/google.internal.labs.tailwind.orchestration.v1.UserDisplayableError
Wait a few minutes before retrying video creation.
```

**Strategy:** Don't retry more than 2-3 times within a few minutes. Move on to other artifacts, wait some time, then retry. On paid tier, rate limits ease after ~10-15 minutes.

### Slides Silent Failure

Slides can show `"status": "failed"` in studio status without any visible error message in the CLI output. The generation just silently fails server-side.

**Strategy:** If slides show "failed", just retry immediately with a new `nlm slides create` command. The retry almost always works. Do not treat the failure as a blocker — it's a transient server-side issue.

### Video Unknown Status

Video can briefly show `"status": "unknown"` in studio status during generation. This is not a failure — the video is still being processed. **Do not attempt to download while status is unknown** (it will fail). Poll until it transitions to "completed". If it stays "unknown" for 5+ minutes, retry with a new video create command.

### Audio ReadTimeout

```
httpx.ReadTimeout: The read operation timed out
```

The audio/dialogue generation endpoint can be slow. Just retry — it usually works on the second attempt.

### Quiz Invalid Difficulty

```
Error: Invalid value for '--difficulty' / '-d': 'medium' is not a valid integer.
```

Use `--difficulty 3` for medium, not the string `"medium"`.

## Auth

Auth sessions last ~20 minutes. Run `nlm login --check` before every batch of operations. If expired, supply a new Google auth URL.
