---
name: obsidian
description: Read, search, create, and edit notes in the Obsidian vault.
platforms: [linux, macos, windows]
---

# Obsidian Vault

Use this skill for filesystem-first Obsidian vault work: reading notes, listing notes, searching note files, creating notes, appending content, and adding wikilinks.

## Vault path

Use a known or resolved vault path before calling file tools.

The documented vault-path convention is the `OBSIDIAN_VAULT_PATH` environment variable, for example from `~/.hermes/.env`. If it is unset, use `~/Documents/Obsidian Vault`.

File tools do not expand shell variables. Do not pass paths containing `$OBSIDIAN_VAULT_PATH` to `read_file`, `write_file`, `patch`, or `search_files`; resolve the vault path first and pass a concrete absolute path. Vault paths may contain spaces, which is another reason to prefer file tools over shell commands.

If the vault path is unknown, `terminal` is acceptable for resolving `OBSIDIAN_VAULT_PATH` or checking whether the fallback path exists. Once the path is known, switch back to file tools.

## Read a note

Use `read_file` with the resolved absolute path to the note. Prefer this over `cat` because it provides line numbers and pagination.

## List notes

Use `search_files` with `target: "files"` and the resolved vault path. Prefer this over `find` or `ls`.

- To list all markdown notes, use `pattern: "*.md"` under the vault path.
- To list a subfolder, search under that subfolder's absolute path.

## Search

Use `search_files` for both filename and content searches. Prefer this over `grep`, `find`, or `ls`.

- For filenames, use `search_files` with `target: "files"` and a filename `pattern`.
- For note contents, use `search_files` with `target: "content"`, the content regex as `pattern`, and `file_glob: "*.md"` when you want to restrict matches to markdown notes.

## Create a note

Use `write_file` with the resolved absolute path and the full markdown content. Prefer this over shell heredocs or `echo` because it avoids shell quoting issues and returns structured results.

## Append to a note

Prefer a native file-tool workflow when it is not awkward:

- Read the target note with `read_file`.
- Use `patch` for an anchored append when there is stable context, such as adding a section after an existing heading or appending before a known trailing block.
- Use `write_file` when rewriting the whole note is clearer than constructing a fragile patch.

For an anchored append with `patch`, replace the anchor with the anchor plus the new content.

For a simple append with no stable context, `terminal` is acceptable if it is the clearest safe option.

## Targeted edits

Use `patch` for focused note changes when the current content gives you stable context. Prefer this over shell text rewriting.

## Second Brain Vault

See `references/second-brain-vault.md` for Dwayne's knowledge base vault (dman1313/second-brain) — wiki, journal, CRM, and raw ingestion queue. Separate from the agent-memory vault used for fleet coordination.

### Automated Ingestion Pipeline

The second brain has a live automated pipeline. See `references/second-brain-pipeline.md` for full architecture.

**How it works:**
1. **Feed Watcher** (`~/.hermes/scripts/feed-watcher.py`) — no_agent cron, runs every 6h (00,06,12,18). Checks RSS feeds from `~/.hermes/scripts/second-brain-feeds.json`, saves new articles to `raw/`.
2. **Ingestion Processor** — agent cron (job `7ee02d19d4a2`), runs every 6h staggered (01:30,07:30,13:30,19:30). Loads the obsidian skill, reads `raw/` items, creates wiki pages, updates CRM/indexes, moves to `raw/processed/`, commits+pushes.
3. **Quick-add** (`~/.hermes/scripts/quick-add.py`) — manual URL → `raw/` for YouTube, Twitter, or one-off articles.

**Cron stagger pattern:** Feed watcher runs 1.5h before ingestion so new items are ready. If adding new data sources, add to the feed watcher config, not directly to raw/.

## Wikilinks

Obsidian links notes with `[[Note Name]]` syntax. When creating notes, use these to link related content.
