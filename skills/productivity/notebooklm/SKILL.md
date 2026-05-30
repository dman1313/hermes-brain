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

### Research as Web Fallback

When external search APIs are unavailable (Firecrawl subscription expired, MCP rate limits hit, GLM reader exhausted), NotebookLM's built-in research engine is an independent fallback. It has its own web search capability that doesn't depend on Nous subscription or MCP quotas.

**Workflow (parallel strategy — preferred):**
1. `nlm notebook create "Topic — Date"` — create a fresh notebook
2. `nlm research start "detailed query" --notebook-id <id> --mode deep` — NotebookLM searches the web itself
3. **In parallel**, add key URLs directly: `nlm source add <id> --url "..."` for each known authoritative source
4. Wait for research completion (see blocking behavior pitfall below)
5. `nlm research import <notebook-id> <task-id>` — import discovered sources into the notebook
6. `nlm notebook query <id> "synthesis question"` — query all sources

**This produced 61 sources from a single deep research call when all other web tools were down.**

**Pitfall: Research import can fail even when manual sources exist.** `research import` only imports sources *the research engine found* — it does not include manually added URLs. If import returns "No sources were found in the research results", the manually added sources are still queryable. This is why the parallel strategy matters: add URLs directly so you always have content even if research finds nothing.

**Pitfall: Cloudflare-blocked sources are useless.** Many education sites (IBO, OECD, UNESCO) block automated fetching via Cloudflare. These get added as sources but contain only "Just a moment..." — zero usable content. After adding URLs, run `nlm source list <id> --url` and check titles. Sources titled "Just a moment..." or "403 Forbidden" will not contribute to queries. Don't waste query budget on them.

**Post-research enrichment: Save synthesis back to notebook.** After completing a multi-query research session, add the final synthesis document as a text source: `nlm source add <id> --file /path/to/synthesis.md --title "Research Synthesis"`. This makes the synthesis queryable alongside the original sources for follow-up questions.

### Pitfall: `nlm research status` Blocks Until Completion

`nlm research status <notebook-id>` does NOT return partial progress — it blocks (hangs) until the research job finishes. For `--mode deep`, this can take 3-5+ minutes, guaranteeing terminal timeouts (default 180s).

**Workaround:** Run in background, then wait:
```bash
# Start research
nlm research start "query" --notebook-id <id> --mode deep

# Check status in background (won't timeout)
terminal(background=True, command='nlm research status <id>')
# Returns session_id, e.g. proc_abc123

# Wait for completion (up to 5 min)
process(action='wait', session_id='proc_abc123', timeout=300)
# Output shows: "Research Status: Status: completed, Sources found: N"

# Then import
nlm research import <notebook-id> <task-id>
```

**Alternative:** If you don't need to poll, just wait ~5 minutes and run `nlm research import` directly — it will error if research isn't done yet, at which point you wait more.

**Pitfall — `--json` not supported on `research status`:** Unlike other nlm commands, `nlm research status` does not accept `--json`. It always outputs formatted text.

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

## Research Notebook Index

Notable research notebooks are tracked in [references/research-notebooks.md](references/research-notebooks.md). Use this to find existing notebooks by topic before creating new ones.

## Alignment Verification Workflow

When the user asks "does this align with X guidelines?" or "is this consistent with Y's official position?", use this workflow instead of brute-force web scraping:

1. **Query the notebook first.** If the research was done in a prior session, the notebook likely already has the answer. Run `nlm notebook query <id> "What does [body] say about [topic]?"` — this is fast and free.
2. **Try the primary source once.** One attempt at the official URL. If Cloudflare-blocked, don't retry with 10 different approaches.
3. **Acknowledge the gap honestly.** "The IB's site is Cloudflare-protected and I couldn't access their official guidance directly" is better than 5 minutes of failed attempts.
4. **Provide the best available answer.** Synthesize from what the notebook contains (secondary sources, TeachAI, ISTE, etc.) and clearly mark what's from primary vs. secondary sources.
5. **Offer a concrete next step.** Ask the user to download the PDF on their local machine and send it, or suggest they paste the relevant section. This is the fastest path to closing the gap.

**Do NOT:** Spend 10+ tool calls trying Wayback Machine, Google cache, DuckDuckGo, Bing, CachedView, curl with different user-agents, etc. If the first browser attempt shows Cloudflare, move to step 3.

**Pitfall: Institutional sites are Cloudflare-locked.** IBO (ibo.org), OECD, UNESCO, and many .org education sites block automated fetching. This is persistent across sessions — don't expect it to change. The NotebookLM research engine can sometimes access these during its own web search (it uses different infrastructure), so sources added during `nlm research` may have more content than sources added via direct URL.

## Multi-Query Research Pattern

For comprehensive research sessions (e.g., building a specialist brief), use sequential queries against the same notebook rather than trying to get everything in one question:

1. **Create notebook + add sources** (parallel strategy above)
2. **Query 1:** Core topic / driving question #1 — get foundational findings
3. **Query 2:** Risks, limitations, counter-arguments
4. **Query 3:** Practical recommendations / implementation guidance
5. **Query 4:** Domain-specific angle (e.g., "What does X framework say about Y?")
6. **Compile** the answers into a single synthesis document
7. **Save synthesis back** as a text source for follow-up queries

Each query benefits from the growing source base. NotebookLM's retrieval improves when it has multiple query rounds to surface different relevant passages from the same sources.

**Tip:** Include "Cite specific sources" in each query prompt to get attribution. NotebookLM returns source IDs and cited text, which can be used for proper citations in the synthesis.

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
| "No sources were found in the research results" | Research engine found nothing (rate limits, query too narrow, or sites blocked) | Manually added sources still work — query the notebook directly. Add more URLs and retry research with a broader query. |

## Fire-and-Forget Pattern for Cron Pipelines

When generating NotebookLM artifacts from cron scripts, **never poll** — the cron timeout (default 120s) is shorter than artifact generation (1-5 min). Use a two-run fire-and-forget pattern instead:

**Run 1 (submit):**
1. Submit artifacts via `nlm video create`, `nlm slides create`, `nlm report create`
2. Save state to a JSON file (rank, name, timestamp)
3. Exit immediately (<30s)

**Run 2+ (check/download):**
1. Read state file — if submitted, check `nlm studio status`
2. If artifacts ready → download, mark concept done, delete state file
3. If not ready → exit silently, try again next run

**State file example** (`pipeline-state.json`):
```json
{"rank": 2, "name": "Genetics, Inheritance & GM", "submitted": true}
```

**Key benefits:**
- Each run completes in <60s, well within cron timeout
- Rate-limited submissions (common with slides) get retried naturally on next run
- No lost work — state persists across runs

**Pitfall: `nlm slides create` is rate-limit-prone.** It fails more often than video or report. In the submit phase, catch the error (`|| true`) and let the download phase handle partial artifacts. The pipeline state tracks concept completion, not individual artifact types.

## Cron-Based Generation: Fire-and-Forget Pattern

When generating NotebookLM artifacts from a cron job, **never poll inside the script**. NotebookLM artifact generation (video, slides, report, flashcards) takes 1-10 minutes. A polling loop (sleep 60 × 10 iterations = 600s) will exceed the cron timeout (120s default) and the job always fails.

**Correct pattern — submit on run N, download on run N+1:**

1. **Run 1 (submit):** Call `nlm video create`, `nlm slides create`, `nlm report create`, `nlm flashcards create` with `--confirm`. Save a state file (e.g. `pipeline-state.json`) with the concept rank and name. Exit immediately.

2. **Run 2+ (check/download):** Read the state file. Call `nlm studio status <notebook> --json`. If artifacts are completed, download them. If not, exit silently — the next hourly run will check again.

3. **Rate limits:** NotebookLM rate-limits slide deck creation. The `|| true` after each create command prevents the script from aborting on rate-limit errors. Slides that fail on submit will succeed on a later run.

**Key implementation details:**
- Each run completes in <30s (no polling)
- State file tracks which concept is "in flight"
- Download filter: `a.get('type') in ('video','slide_deck','report','flashcards')`
- Use `completed[-4:]` (last 4 artifacts) since each concept submits 4 types
- Mark concept done only after at least one artifact downloads

## Study Material Generation: Always Include All 4 Types

When generating study materials for a notebook (IGCSE, courses, etc.), **always produce all 4 artifact types**:

1. **Video** — `nlm video create`
2. **Slides** — `nlm slides create`
3. **Study Guide** — `nlm report create --format "Study Guide"`
4. **Flashcards** — `nlm flashcards create`

Do not skip flashcards. They are a standard part of the study material set.

## Notes

- Free tier: ~50 queries/day
- Audio/video generation: 1-5 minutes
- Device requirement: `nlm login` needs Chrome on a graphical machine. Headless VPS uses pre-authenticated cookies transferred via SCP.
- Package: `notebooklm-mcp-cli` v0.6.10, installed via uv
- Binary path: `/home/ubuntu/.local/bin/nlm`
