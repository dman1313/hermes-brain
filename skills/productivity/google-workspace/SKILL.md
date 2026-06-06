---
name: google-workspace
description: Gmail, Calendar, Drive, Contacts, Sheets, Docs, and Slides integration via Python. Uses OAuth2 with automatic token refresh. No external binaries needed — runs entirely with Google's Python client libraries in the Hermes venv.
version: 1.0.0
author: Nous Research
license: MIT
required_credential_files:
  - path: google_token.json
    description: Google OAuth2 token (created by setup script)
  - path: google_client_secret.json
    description: Google OAuth2 client credentials (downloaded from Google Cloud Console)
metadata:
  hermes:
    tags: [Google, Gmail, Calendar, Drive, Sheets, Docs, Slides, Contacts, Email, OAuth]
    homepage: https://github.com/NousResearch/hermes-agent
    related_skills: [himalaya]
---

# Google Workspace

Gmail, Calendar, Drive, Contacts, Sheets, Docs, and Slides — all through Python scripts in this skill. No external binaries to install.

## References

- `references/gmail-search-syntax.md` — Gmail search operators (is:unread, from:, newer_than:, etc.)
- `references/hermes-drive-backup.md` — Hermes state backup workflow to Google Drive (script, cron, retention)
- `references/google-slides-api.md` — Slides API patterns, pitfalls, helper functions, and the `fields` footgun
- `references/drive-folder-operations.md` — Create folders, move files, delete via standalone Drive API scripts (not in google_api.py)
- `references/drive-management-operations.md` — Drive operations not in google_api.py: create folders, move files, bulk reorganize (standalone script pattern)

## Scripts

- `scripts/setup.py` — OAuth2 setup (run once to authorize)
- `scripts/google_api.py` — API wrapper CLI (agent uses this for all operations)
- `scripts/slides-template.py` — Starter template for creating Google Slides presentations

## First-Time Setup

The setup is fully non-interactive — you drive it step by step so it works
on CLI, Telegram, Discord, or any platform.

Define a shorthand first:

```bash
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
GWORKSPACE_SKILL_DIR="$HERMES_HOME/skills/productivity/google-workspace"
PYTHON_BIN="${HERMES_PYTHON:-python3}"
if [ -x "$HERMES_HOME/hermes-agent/venv/bin/python" ]; then
  PYTHON_BIN="$HERMES_HOME/hermes-agent/venv/bin/python"
fi
GSETUP="$PYTHON_BIN $GWORKSPACE_SKILL_DIR/scripts/setup.py"
```

### Step 0: Check if already set up

```bash
$GSETUP --check
```

If it prints `AUTHENTICATED`, skip to Usage — setup is already done.

### Step 1: Triage — ask the user what they need

Before starting OAuth setup, ask the user TWO questions:

**Question 1: "What Google services do you need? Just email, or also
Calendar/Drive/Sheets/Docs?"**

- **Email only** → They don't need this skill at all. Use the `himalaya` skill
  instead — it works with a Gmail App Password (Settings → Security → App
  Passwords) and takes 2 minutes to set up. No Google Cloud project needed.
  Load the himalaya skill and follow its setup instructions.

- **Calendar, Drive, Sheets, Docs (or email + these)** → Continue with this
  skill's OAuth setup below.

**Question 2: "Does your Google account use Advanced Protection (hardware
security keys required to sign in)? If you're not sure, you probably don't
— it's something you would have explicitly enrolled in."**

- **No / Not sure** → Normal setup. Continue below.
- **Yes** → Their Workspace admin must add the OAuth client ID to the org's
  allowed apps list before Step 4 will work. Let them know upfront.

### Step 2: Create OAuth credentials (one-time, ~5 minutes)

Tell the user:

> You need a Google Cloud OAuth client. This is a one-time setup:
>
> 1. Go to https://console.cloud.google.com/apis/credentials
> 2. Create a project (or use an existing one)
> 3. Click "Enable APIs" and enable: Gmail API, Google Calendar API,
>    Google Drive API, Google Sheets API, Google Docs API, People API
> 4. Go to Credentials → Create Credentials → OAuth 2.0 Client ID
> 5. Application type: "Desktop app" → Create
> 6. Click "Download JSON" and tell me the file path

Once they provide the path:

```bash
$GSETUP --client-secret /path/to/client_secret.json
```

### Step 3: Get authorization URL

```bash
$GSETUP --auth-url
```

This prints a URL. **Send the URL to the user** and tell them:

> Open this link in your browser, sign in with your Google account, and
> authorize access. After authorizing, you'll be redirected to a page that
> may show an error — that's expected. Copy the ENTIRE URL from your
> browser's address bar and paste it back to me.

### Step 4: Exchange the code

The user will paste back either a URL like `http://localhost:1/?code=4/0A...&scope=...`
or just the code string. Either works. The `--auth-url` step stores a temporary
pending OAuth session locally so `--auth-code` can complete the PKCE exchange
later, even on headless systems:

```bash
$GSETUP --auth-code "THE_URL_OR_CODE_THE_USER_PASTED"
```

### Step 5: Verify

```bash
$GSETUP --check
```

Should print `AUTHENTICATED`. Setup is complete — token refreshes automatically from now on.

### Notes

- Token is stored at `google_token.json` under the active profile's `HERMES_HOME` and auto-refreshes.
- Pending OAuth session state/verifier are stored temporarily at `google_oauth_pending.json` under the active profile's `HERMES_HOME` until exchange completes.
- Hermes now refuses to overwrite a full Google Workspace token with a narrower re-auth token missing Gmail scopes, so one profile's partial consent cannot silently break email actions later.
- To revoke: `$GSETUP --revoke`

## Usage

All commands go through the API script. Set `GAPI` as a shorthand:

```bash
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
GWORKSPACE_SKILL_DIR="$HERMES_HOME/skills/productivity/google-workspace"
PYTHON_BIN="${HERMES_PYTHON:-python3}"
if [ -x "$HERMES_HOME/hermes-agent/venv/bin/python" ]; then
  PYTHON_BIN="$HERMES_HOME/hermes-agent/venv/bin/python"
fi
GAPI="$PYTHON_BIN $GWORKSPACE_SKILL_DIR/scripts/google_api.py"
```

### Gmail

```bash
# Search (returns JSON array with id, from, subject, date, snippet)
$GAPI gmail search "is:unread" --max 10
$GAPI gmail search "from:boss@company.com newer_than:1d"
$GAPI gmail search "has:attachment filename:pdf newer_than:7d"

# Read full message (returns JSON with body text)
$GAPI gmail get MESSAGE_ID

# Send
$GAPI gmail send --to user@example.com --subject "Hello" --body "Message text"
$GAPI gmail send --to user@example.com --subject "Report" --body "<h1>Q4</h1><p>Details...</p>" --html

# Reply (automatically threads and sets In-Reply-To)
$GAPI gmail reply MESSAGE_ID --body "Thanks, that works for me."

# Labels
$GAPI gmail labels
$GAPI gmail modify MESSAGE_ID --add-labels LABEL_ID
$GAPI gmail modify MESSAGE_ID --remove-labels UNREAD
```

### Calendar

```bash
# List events (defaults to next 7 days)
$GAPI calendar list
$GAPI calendar list --start 2026-03-01T00:00:00Z --end 2026-03-07T23:59:59Z

# Create event (ISO 8601 with timezone required)
$GAPI calendar create --summary "Team Standup" --start 2026-03-01T10:00:00-06:00 --end 2026-03-01T10:30:00-06:00
$GAPI calendar create --summary "Lunch" --start 2026-03-01T12:00:00Z --end 2026-03-01T13:00:00Z --location "Cafe"
$GAPI calendar create --summary "Review" --start 2026-03-01T14:00:00Z --end 2026-03-01T15:00:00Z --attendees "alice@co.com,bob@co.com"

# Delete event
$GAPI calendar delete EVENT_ID
```

### Drive

```bash
$GAPI drive search "quarterly report" --max 10
$GAPI drive search "mimeType='application/pdf'" --raw-query --max 5

# Upload (replaces existing file with same name)
$GAPI drive upload /path/to/file.tar.gz --name "backup.tar.gz"
$GAPI drive upload report.pdf --name "Q4-Report.pdf" --mimetype "application/pdf"

# Delete / prune (keep N most recent)
$GAPI drive delete "hermes-backup-" --keep 7
```

### Contacts

```bash
$GAPI contacts list --max 20
```

### Sheets

```bash
# Read
$GAPI sheets get SHEET_ID "Sheet1!A1:D10"

# Write
$GAPI sheets update SHEET_ID "Sheet1!A1:B2" --values '[["Name","Score"],["Alice","95"]]'

# Append rows
$GAPI sheets append SHEET_ID "Sheet1!A:C" --values '[["new","row","data"]]'
```

### Docs

```bash
$GAPI docs get DOC_ID
```

**Creating new documents** is supported at the API level (scopes: `documents` + `drive.file`). The CLI wrapper doesn't yet expose a `docs create` command, but scripts can use the Google Docs API directly via the same token — see `wolf-newsletter.py` in `wolf-trading-agent` for a worked example of creating + formatting a Google Doc with batchUpdate.

### Slides

The `google_api.py` CLI does NOT have a `slides` subcommand. For Google Slides, write a standalone Python script that uses the same OAuth token. Load the reference doc for patterns:

```
skill_view("google-workspace", file_path="references/google-slides-api.md")
```

Or copy the template and customize:

```bash
cp $GWORKSPACE_SKILL_DIR/scripts/slides-template.py ./my-slides.py
# Edit the content, then:
$PYTHON_BIN ./my-slides.py
```

The template includes helper functions (`tbox`, `bul`, `bg`, `new_slide`, `send`) for building presentations programmatically. Outputs a publicly-viewable Google Slides URL.

## Output Format

All commands return JSON. Parse with `jq` or read directly. Key fields:

- **Gmail search**: `[{id, threadId, from, to, subject, date, snippet, labels}]`
- **Gmail get**: `{id, threadId, from, to, subject, date, labels, body}`
- **Gmail send/reply**: `{status: "sent", id, threadId}`
- **Calendar list**: `[{id, summary, start, end, location, description, htmlLink}]`
- **Calendar create**: `{status: "created", id, summary, htmlLink}`
- **Drive search**: `[{id, name, mimeType, modifiedTime, webViewLink}]`
- **Contacts list**: `[{name, emails: [...], phones: [...]}]`
- **Sheets get**: `[[cell, cell, ...], ...]`

## Rules

1. **Never send email or create/delete events without confirming with the user first.** Show the draft content and ask for approval.
2. **Check auth before first use** — run `setup.py --check`. If it fails, guide the user through setup.
3. **Use the Gmail search syntax reference** for complex queries — load it with `skill_view("google-workspace", file_path="references/gmail-search-syntax.md")`.
4. **Calendar times must include timezone** — always use ISO 8601 with offset (e.g., `2026-03-01T10:00:00-06:00`) or UTC (`Z`).
5. **Respect rate limits** — avoid rapid-fire sequential API calls. Batch reads when possible.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `NOT_AUTHENTICATED` | Run setup Steps 2-5 above |
| `REFRESH_FAILED` | Token revoked or expired — redo Steps 3-5 |
| `HttpError 403: Insufficient Permission` | Missing API scope — `$GSETUP --revoke` then redo Steps 3-5 |
| `HttpError 403: Request had insufficient authentication scopes` | Token was issued with old read-only scopes (pre-2026-04-30). Scopes upgraded to `drive.file` + `documents` (write). Revoke and re-auth: `$GSETUP --revoke` then `$GSETUP --auth-url`. |
| `RuntimeError: checking third-party user token: bad request: Personal Access Tokens are not supported for this endpoint` | **Transient token refresh glitch** — not a permanent failure. Retry the operation; the token auto-refreshes. If it persists, run `$GSETUP --revoke` then re-auth with `$GSETUP --auth-url` + `--auth-code`. |
| `HttpError 403: Access Not Configured` | API not enabled — user needs to enable it in Google Cloud Console |
| `ModuleNotFoundError` | Run `$GSETUP --install-deps` |
| Drive upload hangs / times out (60s+) | Large files (200MB+) may exceed the terminal tool's default timeout. The upload often succeeds on the Drive side even if the local command times out. After a timeout, verify with `$GAPI drive search \"filename\"` — if the file appears, the upload completed. For files >500MB, consider splitting or uploading from a non-Hermes context. |
| Drive upload times out for large files (200MB+) | The `execute_code` / `terminal` timeout default (60s) may be too short. The upload continues server-side and often succeeds despite the client timeout. Search Drive afterward to confirm: `$GAPI drive search "filename"`. To avoid the timeout, split into smaller archives or increase the tool timeout for the upload command. |
| `No module named pip` during dependency install | Bootstrap pip in the Hermes venv with `$HERMES_HOME/hermes-agent/venv/bin/python -m ensurepip --default-pip`, then retry |
| Advanced Protection blocks auth | Workspace admin must allowlist the OAuth client ID |
| `updateParagraphStyle: Unsupported dimension unit: UNIT_UNSPECIFIED` with `borderBottom` | Bug in google-api-python-client v2.188.0 — `borderBottom` is broken in all variations. Workaround: use `borderBetween` with a `padding` property instead. See wolf-trading-agent `references/google-docs-borderbottom-bug.md`. |
| `--revoke` shows success but token file still exists / revoke URL has `***` placeholder | Bug in setup.py v1.0 — the revoke URL literally had `***` instead of `{creds.token}`. Fixed 2026-05-11. See `references/setup-py-revoke-bug.md`. |

## Revoking Access

```bash
$GSETUP --revoke
```
