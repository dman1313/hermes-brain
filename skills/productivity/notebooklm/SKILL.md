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
5. **Use NotebookLM's native generation for artifacts, not local files.** When the user asks to create study resources, guides, flashcards, quizzes, slides, videos, audio reviews, or any learning artifact FROM a notebook, use `nlm audio create`, `nlm report create`, `nlm flashcards create`, `nlm quiz create`, `nlm slides create`, `nlm mindmap create`, `nlm video create`, `nlm infographic create`, `nlm data-table create`. Do NOT write local markdown files as a substitute — the notebook IS the production environment. Use queries (`nlm notebook query`) to analyze the sources first, then trigger generation inside NotebookLM. Local files are supplementary (for custom content the notebook can't generate), not the primary deliverable. This is a recurring pattern — always default to NotebookLM studio generation.

6. **Batch generation**: All 9 artifact types can be triggered in sequence (each takes ~5-30s to start). They generate in parallel on NotebookLM's side. Poll with `nlm studio status <id>` after starting all of them. Typical completion: mindmap and flashcards are fastest (<30s), audio/video/slides take 1-5 minutes.

7. **Paid tier supports ~200 queries/day** with faster generation.

## Key Notebooks (alias → ID)

- `sdd` → Spec-Driven Development notebook
- `agent` → Agent notebook (40 sources)
- `bio` → IGCSE Bio (96 sources, 84 past papers) — ID: `e621431b-2a33-4f44-b23b-4a86e2349cad`
- H1 AI Brain: `e0da9697-4ba3-466f-9a59-1756dd3e5877`
- `igcse-physics` → IGCSE Physics (105 sources, past papers 2019-2025) — ID: `6b22f008-aec4-447b-8070-e28beb91efde`

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
| Data table | `nlm data-table create <id> "desc" --confirm` |

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

## Related Skills

- `sherlock-study-boy` — NotebookLM study package generation (video, slides, reports)

## References

- `references/exam-paper-analysis.md` — Workflow for cross-referencing exam papers against notebook sources to build concept frequency rankings.

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

## Pitfalls

1. **Stale aliases**: Aliases can point to deleted notebooks (API returns NOT_FOUND). Always verify with `nlm notebook get <alias>` before trusting. If it fails, run `nlm notebook list` to find the correct notebook by title, then `nlm alias set <name> <new-id>` to fix it.

2. **Query timeouts (~60s limit)**: Multi-part queries with "and"/"or" across different topics tend to timeout. Keep each query focused on ONE topic. For cross-referencing multiple concepts, run separate queries per concept and synthesize results yourself. Example: instead of "which papers test X and Y and Z", run three separate queries.

3. **Scanned PDFs**: When adding scanned PDFs (no text layer), pymupdf `get_text()` returns empty. Use `get_pixmap(dpi=200)` to convert pages to images, then OCR/vision to extract text. Alternatively, NotebookLM handles scanned PDFs natively when added as sources — the OCR issue only matters for local extraction.

4. **Large source lists**: Notebooks with 50+ sources produce long JSON from `nlm source list`. Pipe through grep/jq to filter rather than reading the full dump.

5. **`nlm data-table create` syntax**: The `description` is a POSITIONAL argument, not a flag. Correct: `nlm data-table create <id> "my description" --confirm`. Wrong: `nlm data-table create <id> --description "my description" --confirm` (fails with "No such option").

6. **Mindmap type reporting**: `nlm mindmap create` artifacts may show as type `flashcards` in `nlm studio status` output. This is a NotebookLM UI quirk — the mind map is still created correctly and accessible in the notebook's Studio tab.

## Content Extraction Patterns

**For building documents from notebook content:**
- Use `nlm notebook query <id> "detailed question"` for structured, synthesized answers. This is far cleaner than raw source content — NotebookLM extracts, organizes, and cites the relevant material.
- Use `nlm source content <source-id>` only when you need the raw, unsynthesized text from a specific source (e.g., extracting exact quotes, checking OCR output, or verifying what a source actually says).
- **Pipeline pattern**: Query multiple notebooks for complementary information, then combine the answers into a single document. Example: query notebook A for template structure, notebook B for domain content, then merge into a Google Doc via the Docs API (see `google-workspace` skill, `references/google-docs-api.md`).
- When a notebook has both a domain-specific notebook (e.g., "Farm to Table Resources") and a framework notebook (e.g., "IB PYP"), query both — the domain notebook provides content, the framework notebook provides structure.

## Notes

- Free tier: ~50 queries/day. Paid tier: ~200 queries/day
- Audio/video generation: 1-5 minutes
- Auth: `nlm login` needs Chrome. VPS uses Mac-scp'd cookies (~/.notebooklm-mcp-cli/)
- Package: `notebooklm-mcp-cli` v0.6.10, installed via uv
- Binary: `/home/ubuntu/.local/bin/nlm`
- Auth refresh via SCP from Mac every 2-4 weeks
