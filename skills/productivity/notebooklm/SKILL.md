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
4. **Sessions expire in ~20 min** — re-auth when commands fail. On paid tier, higher limits.
5. **Paid tier supports ~200 queries/day** with faster generation.

## Key Notebooks (alias → ID)

- `sdd` → Spec-Driven Development notebook
- `agent` → Agent notebook (40 sources)
- `bio` → IGCSE Bio (45 sources)
- H1 AI Brain: `e0da9697-4ba3-466f-9a59-1756dd3e5877`

## Command Mapping

### Auth & Status
| What you need | Run |
|---|---|
| Check auth | `nlm login --check` |
| Login (needs Chrome) | `nlm login` |
| Config | `nlm config show` |

### Notebooks
| What you need | Run |
|---|---|
| List notebooks | `nlm notebook list` |
| Get notebook info | `nlm notebook get <id>` |
| Describe notebook | `nlm notebook describe <id>` |
| Query notebook | `nlm notebook query <id> "your question"` |
| Create notebook | `nlm notebook create "Title"` |
| Delete notebook | `nlm notebook delete <id> --confirm` |
| Set alias | `nlm alias set <name> <uuid>` |
| List aliases | `nlm alias list` |

### Sources
| What you need | Run |
|---|---|
| Add URL | `nlm source add <id> --url "..."` |
| Add file | `nlm source add <id> --file <path> --wait` |
| Add text | `nlm source add <id> --text "..." --title "..."` |
| Add YouTube | `nlm source add <id> --youtube "..."` |
| Add Drive doc | `nlm source add <id> --drive <doc-id>` |
| List sources | `nlm source list <id>` |
| Describe source | `nlm source describe <source-id>` |
| Get source content | `nlm source content <source-id>` |

### Generation (all require --confirm)
| What you need | Run |
|---|---|
| Audio/podcast | `nlm audio create <id> --confirm` |
| Report | `nlm report create <id> --confirm` |
| Video | `nlm video create <id> --confirm` |
| Slides | `nlm slides create <id> --confirm` |
| Infographic | `nlm infographic create <id> --confirm` |
| Mind map | `nlm mindmap create <id> --confirm` |
| Quiz | `nlm quiz create <id> --confirm` |
| Flashcards | `nlm flashcards create <id> --confirm` |
| Data table | `nlm data-table create <id> --description "desc" --confirm` |

### Artifact Management
| What you need | Run |
|---|---|
| Check generation status | `nlm studio status <id>` |
| Wait for all to complete | Loop `nlm studio status <id>` until all done |
| Delete artifact | `nlm studio delete <id> <artifact-id> --confirm` |

### Downloads (all require confirm)
| What you need | Run |
|---|---|
| Download audio | `nlm download audio <id> <artifact-id> --output <file>` |
| Download report | `nlm download report <id> <artifact-id> --output <file>` |
| Download video | `nlm download video <id> <artifact-id> --output <file>` |
| Download slides | `nlm download slide-deck <id> <artifact-id> --output <file>` |
| Download infographic | `nlm download infographic <id> <artifact-id> --output <file>` |
| Download mind map | `nlm download mind-map <id> <artifact-id> --output <file>` |

### Research
| What you need | Run |
|---|---|
| Start research | `nlm research start "query" --notebook-id <id>` |
| Deep research | `nlm research start "query" --notebook-id <id> --mode deep` |
| Research status | `nlm research status <id>` |
| Import results | `nlm research import <id> <task-id>` |

### Sharing
| What you need | Run |
|---|---|
| Make public | `nlm share public <id>` |
| Check share status | `nlm share status <id>` |

## H1 AI Brain Notebook

- **ID:** `e0da9697-4ba3-466f-9a59-1756dd3e5877`
- Used for session summary storage and cross-session context querying
- Push session logs here at end of each session via wrapup skill

## Autonomy Rules

**Read-only (run without asking):**
- `nlm login --check`, `nlm notebook list`, `nlm notebook get`, `nlm notebook describe`
- `nlm source list`, `nlm source describe`, `nlm source content`
- `nlm studio status`, `nlm research status`
- `nlm alias list`
- `nlm share status`

**Requires confirmation (always ask):**
- Any `--confirm` or delete command
- Any `download` command
- `nlm research import` (modifies notebook)
- `nlm notebook query --save-as-note`
- `nlm share public/private/invite`

## Error Recovery

| Error | Cause | Solution |
|---|---|---|
| "Profile not found" | Not authenticated | `nlm login` on Mac then SCP auth folder |
| "Cookies have expired" | Session timeout | Re-auth via Mac → SCP |
| "Notebook not found" | Invalid ID | `nlm notebook list` to find correct ID |
| "Rate limit exceeded" | Too many calls | Wait 30s, retry. Paid tier is more generous |
| Video/slides fail 2x | Burst rate limit | Skip, retry later. Known NotebookLM paid tier quirk |

## Notes

- Free tier: ~50 queries/day. Paid tier: ~200 queries/day
- Audio/video generation: 1-5 minutes
- Auth: `nlm login` needs Chrome. VPS uses Mac-scp'd cookies (~/.notebooklm-mcp-cli/)
- Package: `notebooklm-mcp-cli` v0.6.10, installed via uv
- Binary: `/home/ubuntu/.local/bin/nlm`
- Auth refresh via SCP from Mac every 2-4 weeks
