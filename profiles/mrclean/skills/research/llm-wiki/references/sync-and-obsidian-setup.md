# Wiki Sync and Obsidian Setup Guide

Supplementary guide for GitHub sync, Obsidian vault configuration, and Dropbox alternative sync.

## Git Sync Setup

When the user asks to sync the wiki with GitHub or set up git tracking:

1. Initialize the repo (if not already done):
```bash
cd ~/wiki
git init
git config user.email "<user-email>"
git config user.name "<user-name>"
```

2. Create `.gitignore`:
```
_archive/
_meta/
raw/assets/
*.pdf
*.mp4
*.png
*.jpg
*.jpeg
*.gif
.obsidian/workspace*
.obsidian/cache*
.obsidian/sync.json
.obsidian/app.json.bak
node_modules/
```

3. Commit the initial wiki structure:
```bash
git add .
git commit -m "Initial wiki setup"
```

4. Create GitHub repo (via API or ask user to create one), then link and push:
```bash
git branch -m main
git remote add origin https://<TOKEN>@github.com/<USER>/wiki.git
git push -u origin main
```

5. Auto-sync script (optional, for server-side):
Create `~/.local/bin/wiki-sync` that stages, commits with timestamp, and pushes if there are changes.

## Obsidian Vault Config

When the user wants a proper Obsidian vault setup, create the `.obsidian/` directory with these files:

**`app.json`** - Core settings:
- `alwaysUpdateLinks: true`
- `attachmentFolderPath: "raw/assets"`
- `newFileLocation: "folder"`
- `newFileFolderPath: "concepts"`
- `useMarkdownLinks: false` (enables wikilinks)
- `newLinkFormat: "shortest"`
- `userIgnoreFilters: ["raw/assets/", "_archive/", "_meta/", ".git/"]`
- `showFrontmatter: true`
- `livePreview: true`

**`graph.json`** - Graph view color coding by folder:
- `path:entities` = red
- `path:concepts` = orange
- `path:comparisons` = blue
- `path:queries` = green
- `path:raw` = gray
- Set `showOrphans: true` and `showArrow: true`

**`community-plugins.json`** - Enable dataview:
```json
["dataview"]
```

**`plugins/dataview/dataview.json`** - Dataview plugin settings with refresh enabled.

After creating config files, commit and push them. The `.obsidian/` directory should be tracked in git (except workspace/cache files which are gitignored).

## Dropbox Alternative Sync

If the user provides Dropbox app credentials instead of GitHub or Obsidian Sync:

**Prerequisites:** `pip install dropbox requests`

**Why not rclone?** rclone's `authorize` command spawns a localhost callback server that cannot complete in a headless/server environment. The Python SDK's no-redirect flow is the reliable path.

**Auth flow** (no-redirect OAuth2):
1. Use `DropboxOAuth2FlowNoRedirect` to generate an auth URL
2. User opens URL in browser, clicks Allow, copies the authorization code
3. Exchange code using `auth_flow.finish(code)`
4. **Pitfall:** The refresh token may be empty depending on Dropbox app settings. If `oauth_result.refresh_token` is empty, save `oauth_result.access_token` directly to `~/.dropbox-wiki-token` instead.
5. Sync script reads the token from `~/.dropbox-wiki-token` and uploads via `Dropbox.files_upload()`

**Sync script structure:** Use a Python heredoc in bash (`python3 << PYEOF`), NOT an inline Python string in a bash variable. Inline Python breaks on backslash escaping (e.g., `replace('\', '/')` becomes a syntax error). Walk the wiki dir, upload each file to the target Dropbox folder with overwrite mode. Skip `.git/`, `__pycache__/`, and `node_modules/`.

**Auto-sync:** Schedule with `cronjob` every 15 minutes to run the sync script.

**Pitfall:** Dropbox OAuth requires an interactive browser step exactly once. After that, the stored token enables fully automated headless sync.

## Companion Workspaces

Users often want parallel organizational folders alongside the wiki with the same sync setup. Pattern: create a sibling directory with parallel structure.

Example: `photo.news/` for a Communications Officer persona:
```
photo.news/
├── README.md
├── photos/{raw,edited,thumbnails}/
├── newsletters/{templates,drafts,sent,archive}/
└── assets/{logos,icons,headers}/
```

Use the same Dropbox sync script with a different source directory and target Dropbox folder.
