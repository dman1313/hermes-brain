---
name: wiki-git-sync
description: "Sync a markdown wiki across devices using GitHub and the obsidian-git plugin. Covers git init, .gitignore, repo creation, PAT auth, obsidian-git config, and server-side auto-commit."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [wiki, git, github, obsidian, sync, markdown, knowledge-base]
    category: devops
    related_skills: [llm-wiki, obsidian]
---

# Wiki Git Sync

Sync a markdown wiki directory across multiple devices using GitHub as the
backend and the obsidian-git plugin for automatic two-way sync.

Works with Karpathy-style LLM wikis, Obsidian vaults, or any markdown-based
knowledge base.

## When This Skill Activates

Use when the user:
- Asks to sync their wiki with GitHub / git / obsidian-git
- Wants cross-device access to a markdown knowledge base
- Needs to set up version control for their wiki
- Mentions Vinzent03/obsidian-git or similar sync tooling

## Prerequisites

- A local wiki directory (e.g., `~/wiki`)
- A GitHub personal access token (classic) with `repo` scope
- Obsidian desktop or mobile (for the plugin)

## Setup Steps

### 1. Initialize Git in the Wiki Directory

```bash
cd ~/wiki
git init
git config user.email "your@email.com"
git config user.name "Your Name"
```

### 2. Create .gitignore

Exclude large binaries, ephemeral Obsidian files, and generated assets:

```gitignore
# Wiki-specific exclusions
_archive/
_meta/
raw/assets/
*.pdf
*.mp4
*.png
*.jpg
*.jpeg
*.gif

# Obsidian ephemeral files
.obsidian/workspace*
.obsidian/cache*
.obsidian/graph.json
```

Write this to `~/wiki/.gitignore`.

### 3. First Commit

```bash
cd ~/wiki
git add .
git commit -m "Initial wiki setup"
```

### 4. Create Remote GitHub Repository

Option A — Via GitHub API (programmatic):
```bash
curl -X POST \
  -H "Authorization: token <GITHUB_PAT>" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/user/repos \
  -d '{"name":"wiki","description":"Personal markdown wiki","private":true}'
```

Option B — Manually via github.com (empty repo, no README).

### 5. Link Remote and Push

Embed the PAT in the remote URL for non-interactive auth:
```bash
git branch -m main
git remote add origin https://<GITHUB_PAT>@github.com/<USER>/wiki.git
git push -u origin main
```

Alternatively, use git credential helper:
```bash
git config credential.helper store
echo -e "url=https://github.com\nusername=<USER>\npassword=<GITHUB_PAT>" | git credential approve
```

### 6. Obsidian-Git Plugin Configuration

On each device where you want to use Obsidian:

**Install the plugin:**
1. Open Obsidian → Settings → Community Plugins
2. Turn off Safe Mode → Browse → Search `Git` (by Vinzent03)
3. Install → Enable

**Configure auto-sync:**
- Auto commit-and-sync: **ON**
- Pull on startup: **ON** (prevents conflicts)
- Push on backup: **ON**
- Commit message template: `{{hostname}} - {{date}}`
- Backup interval: 1 minute (or as preferred)

**Open the vault:** Point Obsidian to the `~/wiki` directory.

### 7. Clone on Additional Devices

```bash
git clone https://<GITHUB_PAT>@github.com/<USER>/wiki.git ~/wiki
```

Then open `~/wiki` as an Obsidian vault and enable obsidian-git.

## Server-Side Auto-Commit

If an agent or script writes to `~/wiki` on a headless server, set up a cron job
to automatically commit and push changes:

```bash
# Edit crontab
crontab -e

# Add this line to commit every hour:
0 * * * * cd ~/wiki && git add -A && git diff --cached --quiet || (git commit -m "auto: $(date +%Y-%m-%d-%H:%M)" && git pull --rebase && git push)
```

This ensures server-side edits reach GitHub even when Obsidian is closed.

## Verification

After setup, verify sync is working:
1. Edit a file in Obsidian → wait 1-2 minutes → check GitHub web UI for the commit
2. Edit a file on GitHub web → restart Obsidian → confirm the change appears locally
3. If using server auto-commit, create a file on the server → wait for the top of the hour → confirm on GitHub

## Troubleshooting

**Merge conflicts:** If Obsidian and the server both modify the same file, git will
conflict. Resolve manually or delete and recreate the file.

**Token expiry:** GitHub PATs can expire. If push fails with 401, regenerate the
token and update the remote URL:
```bash
git remote set-url origin https://<NEW_PAT>@github.com/<USER>/wiki.git
```

**Large files:** If `raw/assets/` contains large files, consider using Git LFS or
excluding them from git entirely and syncing via another method (e.g., cloud storage).

## Pitfalls

- Don't commit `.obsidian/workspace*` files — they differ per device and cause noise
- Don't commit large binary assets to git — use `.gitignore` or Git LFS
- The auto-commit cron job can create many small commits; squash history periodically
if commit noise bothers you
- Keep the PAT secure — it grants repo access. Rotate it regularly
