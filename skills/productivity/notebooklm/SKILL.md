---
name: notebooklm
description: "Interact with Google NotebookLM via the nlm CLI. Use when the user wants to query sources, add URLs/PDFs/YouTube/files to a notebook, generate podcasts/video/slides/infographics/reports/mind maps/quizzes/flashcards/data tables, download artifacts, run web research, or manage notebooks. Triggers on mentions of 'notebooklm', 'nlm', 'notebook lm', 'podcast generation', 'audio overview', or generating any NotebookLM artifact."
---

# NotebookLM CLI (via nlm)

The binary is `nlm` from the `notebooklm-mcp-cli` package. Installed at `/home/ubuntu/.local/bin/nlm`.

## Critical Rules

1. **Auth required**: Run `nlm login --check` before any operation. If expired, tell the user to run `nlm login` on a machine with Chrome (session lasts ~20 min for queries, ~2-4 weeks for cookies).
2. **ALWAYS confirm before delete, generate, download, or query with --save-as-note.** Read-only commands (list, status, auth check, source add, history) are autonomous.
3. **Use `nlm studio status <id>` to poll generation progress** — audio/video takes 1-5 minutes.
4. **Sessions expire in ~20 min** — re-auth when commands fail.
5. **Rate limits**: ~50 queries/day on free tier.
6. **TTY workaround**: `nlm` outputs JSON when no TTY is detected. For rich table output, wrap commands in `script -qc "nlm ..." /dev/null`. For simple lists, use `--title` (notebook list) or `--url` (source list). For programmatic work, use `--json`.
7. **Output format per command**:
   - `notebook list`: use `--title` for readable list, `--json` for parsing
   - `source list`: use `--url` for readable list, `--json` for parsing. No `--title` flag.
   - `studio status`: always JSON
   - `notebook query`: always JSON
   - `notebook describe`: always text/JSON

## Command Mapping

The user may use these shorthand command shapes. Map them to the real `nlm` commands:

### Auth & Status
| User command | Real command |
|---|---|
| `notebooklm auth check` | `nlm login --check` |
| `notebooklm login` | `nlm login` (requires Chrome) |

### Notebooks
| User command | Real command |
|---|---|
| `notebooklm list` | `nlm notebook list` |
| `notebooklm notebooks` | `nlm notebook list` |
| `notebooklm status` | `nlm notebook list && nlm login --check` |
| `notebooklm use <id>` | Set context: run `nlm notebook get <id>` to verify, then treat `<id>` as the active notebook for subsequent commands |
| `notebooklm create "Title"` | `nlm notebook create "Title"` |
| `notebooklm delete <id>` | `nlm notebook delete <id> --confirm` |
| `notebooklm describe <id>` | `nlm notebook describe <id>` |
| `notebooklm query <id> "question"` | `nlm notebook query <id> "question"` |
| `notebooklm ask <id> "question"` | `nlm notebook query <id> "question"` |

### Sources
| User command | Real command |
|---|---|
| `notebooklm source add <id> --url "..."` | `nlm source add <id> --url "..."` |
| `notebooklm source add <id> --file <path>` | `nlm source add <id> --file <path> --wait` |
| `notebooklm source add <id> --text "..." --title "..."` | `nlm source add <id> --text "..." --title "..."` |
| `notebooklm source add <id> --youtube "..."` | `nlm source add <id> --youtube "..."` |
| `notebooklm source add <id> --drive <doc-id>` | `nlm source add <id> --drive <doc-id>` |
| `notebooklm source list <id>` | `nlm source list <id>` |
| `notebooklm source describe <source-id>` | `nlm source describe <source-id>` |
| `notebooklm source content <source-id>` | `nlm source content <source-id>` |

### Generation (all require --confirm)
| User command | Real command |
|---|---|
| `notebooklm generate audio <id>` | `nlm audio create <id> --confirm` |
| `notebooklm generate podcast <id>` | `nlm audio create <id> --confirm` |
| `notebooklm generate report <id>` | `nlm report create <id> --confirm` |
| `notebooklm generate video <id>` | `nlm video create <id> --confirm` |
| `notebooklm generate slides <id>` | `nlm slides create <id> --confirm` |
| `notebooklm generate infographic <id>` | `nlm infographic create <id> --confirm` |
| `notebooklm generate mindmap <id>` | `nlm mindmap create <id> --confirm` |
| `notebooklm generate quiz <id>` | `nlm quiz create <id> --confirm` |
| `notebooklm generate flashcards <id>` | `nlm flashcards create <id> --confirm` |
| `notebooklm generate data-table <id> "desc"` | `nlm data-table create <id> --description "desc" --confirm` |

### Generation options
| Flag | Maps to |
|---|---|
| `--format deep_dive\|brief\|critique\|debate` | `--format` (audio) |
| `--length short\|default\|long` | `--length` (audio) |
| `--format "Briefing Doc"\|"Study Guide"\|"Blog Post"` | `--format` (report) |
| `--count N` | `--count N` (quiz) |
| `--difficulty easy\|medium\|hard` | `--difficulty` (quiz/flashcards) |
| `--style classic\|whiteboard\|kawaii\|anime\|...` | `--style` (video) |
| `--orientation landscape\|portrait\|square` | `--orientation` (infographic) |

### Artifact Management
| User command | Real command |
|---|---|
| `notebooklm artifact status <id>` | `nlm studio status <id>` |
| `notebooklm artifact list <id>` | `nlm studio status <id>` |
| `notebooklm artifact wait <id>` | Loop `nlm studio status <id>` until all in_progress artifacts complete. Poll every 10s. |
| `notebooklm artifact delete <id> <artifact-id>` | `nlm studio delete <id> <artifact-id> --confirm` |

### Downloads
| User command | Real command |
|---|---|
| `notebooklm download audio <id> <artifact-id>` | `nlm download audio <id> <artifact-id> --output <file>` |
| `notebooklm download report <id> <artifact-id>` | `nlm download report <id> <artifact-id> --output <file>` |
| `notebooklm download video <id> <artifact-id>` | `nlm download video <id> <artifact-id> --output <file>` |
| `notebooklm download slides <id> <artifact-id>` | `nlm download slide-deck <id> <artifact-id> --output <file>` |
| `notebooklm download infographic <id> <artifact-id>` | `nlm download infographic <id> <artifact-id> --output <file>` |
| `notebooklm download mindmap <id> <artifact-id>` | `nlm download mind-map <id> <artifact-id> --output <file>` |
| `notebooklm download data-table <id> <artifact-id>` | `nlm download data-table <id> <artifact-id> --output <file>` |

### Research
| User command | Real command |
|---|---|
| `notebooklm research start "query" --notebook-id <id>` | `nlm research start "query" --notebook-id <id>` |
| `notebooklm research start "query" --notebook-id <id> --mode deep` | `nlm research start "query" --notebook-id <id> --mode deep` |
| `notebooklm research status <id>` | `nlm research status <id>` |
| `notebooklm research import <id> <task-id>` | `nlm research import <id> <task-id>` |

### Aliases
| `notebooklm alias set <name> <uuid>` | `nlm alias set <name> <uuid>` |
| `notebooklm alias list` | `nlm alias list` |

### Sharing
| User command | Real command |
|---|---|
| `notebooklm share public <id>` | `nlm share public <id>` |
| `notebooklm share status <id>` | `nlm share status <id>` |

## Autonomy Rules

Read-only (autonomous — run without asking):
- `nlm login --check`, `nlm notebook list`, `nlm notebook get`, `nlm notebook describe`
- `nlm source list`, `nlm source describe`, `nlm source content`
- `nlm studio status`, `nlm research status`
- `nlm alias list`
- `nlm share status`

Requires confirmation (always ask):
- Any `--confirm` or delete command
- Any `download` command
- `nlm research import` (modifies notebook)
- `nlm notebook query --save-as-note`
- `nlm share public/private/invite`
- `nlm chat configure`

## Task Shape

Every task follows this flow:
1. If no notebook is active, run `nlm notebook list` to show options.
2. Use `nlm notebook get <id>` to verify context before operations.
3. Add sources or query as needed.
4. For generation: kick off with `nlm <type> create`, then `nlm studio status` polling.
5. Cite source IDs in your answer when relevant.

## Headless Server Auth

When the host has no Chrome (headless VPS), authenticate on a machine with a GUI (Dwayne's Mac) then SCP the auth data over. Full procedure: [references/auth-scp-transfer.md](references/auth-scp-transfer.md)

## Style Notes

- Dwayne prefers **step-by-step walkthroughs** with one verified step at a time. Don't dump 5 steps at once — guide sequentially.
- When instructing file transfers, be **concrete about what's being copied and why**. Don't assume the user knows what a directory contains or why it matters.

## Error Recovery

| Error | Cause | Solution |
|---|---|---|
| "Profile not found" | Not authenticated | Run `nlm login` on a machine with Chrome, then SCP the auth data (see auth transfer reference) |
| "Cookies have expired" | Session timeout | Re-authenticate via Mac + SCP |
| "Notebook not found" | Invalid ID | `nlm notebook list` |
| "Rate limit exceeded" | Too many calls | Wait 30s, retry |
| Chrome doesn't launch | Port conflict or headless | Use auth transfer approach for headless servers |
| Auth fails after SCP transfer | Nested directory from trailing slash | See references/auth-scp-transfer.md §4 — mv files up one level |

## Notes

- Free tier: ~50 queries/day
- Audio/video generation: 1-5 minutes
- Device requirement: `nlm login` needs Chrome on a graphical machine. Headless VPS uses pre-authenticated cookies transferred via SCP.
- Package: `notebooklm-mcp-cli` v0.6.10, installed via uv
- Binary path: `/home/ubuntu/.local/bin/nlm`
