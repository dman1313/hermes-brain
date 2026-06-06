# Second Brain Automated Pipeline

## Architecture

```
RSS Feeds ──→ feed-watcher.py ──→ raw/ ──→ Ingestion Cron ──→ wiki/ + crm/ + log.md
                                      ↑                        ↓
                                   quick-add.py            git commit+push
```

## Feed Watcher

**Script:** `~/.hermes/scripts/feed-watcher.py`
**Config:** `~/.hermes/scripts/second-brain-feeds.json`
**State:** `~/.hermes/scripts/feed-state.json` (tracks seen items by hash)
**Cron:** no_agent, every 6h at 00,06,12,18

### Config format

```json
{
  "rss_feeds": [
    {"name": "GitHub Blog", "url": "https://github.blog/feed/", "type": "article", "enabled": true}
  ],
  "max_items_per_feed": 3
}
```

Add feeds to `rss_feeds` array. Set `enabled: false` to pause a feed without removing it.

### Limitations

- YouTube RSS returns 400 from this VPS — use quick-add for YouTube URLs
- OpenAI and Anthropic RSS feeds may not return entries (URLs may need updating)
- No Twitter feed automation — use quick-add or Obsidian Web Clipper

## Quick-add

**Script:** `~/.hermes/scripts/quick-add.py`

```bash
python3 ~/.hermes/scripts/quick-add.py "https://example.com/article"
python3 ~/.hermes/scripts/quick-add.py "https://youtube.com/watch?v=..." --title "Custom Title"
```

Auto-detects source type from URL domain (youtube, twitter, github, article). Fetches basic metadata (title, description) when possible. For YouTube, uses yt-dlp to get channel name.

## Ingestion Processor

**Cron job ID:** `7ee02d19d4a2`
**Schedule:** every 6h at 01:30, 07:30, 13:30, 19:30 (staggered 1.5h after feed watcher)
**Skills loaded:** obsidian
**Model:** default provider

### What it does

1. Runs `~/.hermes/scripts/list-raw-items.py` to check for unprocessed items
2. Reads vault AGENTS.md for rules
3. For each item in `raw/` (max 5 per run):
   - Reads source file, fetches full content if only URL+summary available
   - Creates wiki pages with proper frontmatter, tags, Sources section
   - Updates CRM if real people mentioned
   - Updates wiki/index.md and root index.md
   - Moves source to `raw/processed/{type}/`
   - Logs to log.md
4. Commits and pushes to GitHub

### Skip rules

- Merch/promo content (shop announcements, swag)
- Sources too short or low quality
- Items already in `raw/processed/`

## Helper: list-raw-items.py

**Script:** `~/.hermes/scripts/list-raw-items.py`

Lists unprocessed items in raw/ with type, filename, and URL. Used by the ingestion cron at the start of each run. Can also be called manually to check queue status.

## Adding new feed sources

1. Edit `~/.hermes/scripts/second-brain-feeds.json`
2. Add entry to `rss_feeds` array
3. Test: `python3 ~/.hermes/scripts/feed-watcher.py`
4. No cron restart needed — it reads config fresh each run
