# Dropbox Watcher Daemon Design

## Architecture

Single Python daemon managed by systemd user service.
Uses `inotifywait` subprocesses (one per watched directory) to detect filesystem events.
All sync actions go through the existing bash sync scripts — the watcher only triggers them.

## Components

```
dropbox-watcher.py (daemon)
├── Thread 1: inotifywait on ~/wiki/ → triggers ~/.local/bin/dropbox-sync.sh
└── Thread 2: inotifywait on ~/photo.news/ → triggers ~/.local/bin/photo-news-sync.sh
```

## Key Design Decisions

### Debounce (60s)
Each directory has an independent debounce timer. When a file changes, the timer resets.
This batches rapid edits (Obsidian auto-saves every few seconds, git operations, etc.)
into a single sync. 60s is long enough to catch most edit bursts without introducing
noticeable delay.

### Independent triggers
Wiki and photo.news are watched independently. Editing wiki does not trigger a photo.news sync.
Each has its own debounce timer and sync script.

### File filtering
- Excluded by inotifywait: `.git/` internals, Obsidian workspace/cache/graph files
- Excluded by Python: temp files (`*~`, `*.swp`, `*.tmp`), hidden dotfiles (except `.gitignore`)

### Restart safety
systemd `Restart=always` with 15s backoff. If inotifywait or the Python process dies,
it comes back automatically. The daemon also has an internal thread health monitor —
if a watcher thread dies, it restarts it within 30 seconds.

## Log Format

```
[2026-05-14 21:42:45] === Dropbox Watcher started ===
[2026-05-14 21:42:45] Watching 2 paths, debounce=60s
[2026-05-14 21:42:45] Watching wiki: /home/ubuntu/wiki
[2026-05-14 21:42:45] Watching photo.news: /home/ubuntu/photo.news
[2026-05-14 21:42:57]   Δ wiki: index.md
[2026-05-14 21:43:57] → Syncing wiki (/home/ubuntu/wiki)...
[2026-05-14 21:44:17] ✓ wiki sync OK: Sync complete! Uploaded 37 file(s).
```

## Installation

```bash
# Prerequisite
sudo apt-get install -y inotify-tools

# Daemon script
cp dropbox-watcher.py /home/ubuntu/.local/bin/
chmod +x /home/ubuntu/.local/bin/dropbox-watcher.py

# Systemd service
cp dropbox-watcher.service /home/ubuntu/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now dropbox-watcher

# Survive logout
loginctl enable-linger
```

## Token Dependency

Both syncs share the same Dropbox token at `/home/ubuntu/.dropbox-wiki-token`.
If the token expires, the watcher will log sync failures but keep running.
Re-auth via the `dropbox-auth.py` / `dropbox-finish.py` flow — the watcher
will pick up the new token on the next triggered sync without restart.
