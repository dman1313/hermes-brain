# Google Drive Folder Operations

`google_api.py` does NOT have commands for creating folders, moving files between parents, or batch deleting. Use the Drive API directly via standalone Python scripts.

## Standalone Script Pattern

The `google_api.py` module imports `hermes_constants` which fails outside the venv. Always use the venv python and load credentials directly:

```python
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

TOKEN_PATH = Path.home() / ".hermes" / "google_token.json"
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/contacts.readonly",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/presentations",
]

creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
    TOKEN_PATH.write_text(creds.to_json())
service = build("drive", "v3", credentials=creds)
```

Run with: `~/.hermes/hermes-agent/venv/bin/python /path/to/script.py`

## Create Folder

```python
body = {"name": "Folder Name", "mimeType": "application/vnd.google-apps.folder"}
folder = service.files().create(body=body, fields="id,name").execute()
folder_id = folder["id"]
```

## Move File to Folder

Uses `addParents` / `removeParents` (must know the current parent):

```python
file = service.files().get(fileId=file_id, fields="parents").execute()
prev_parents = ",".join(file.get("parents", []))
service.files().update(
    fileId=file_id,
    addParents=new_folder_id,
    removeParents=prev_parents,
    fields="id,parents"
).execute()
```

## Delete File

```python
service.files().delete(fileId=file_id).execute()
```

## List Files (with pagination)

```python
results = service.files().list(
    q="'root' in parents and trashed=false",
    pageSize=100,
    fields="nextPageToken, files(id, name, mimeType, modifiedTime)"
).execute()
files = results.get("files", [])
```

## Pitfalls

1. **`drive.file` scope** — The `drive.file` scope only allows access to files the app created or was explicitly granted. For full Drive access, you'd need `drive` scope (broader). Current token has `drive.file` which works for files created by the Hermes OAuth app.
2. **Rate limits** — Drive API has a default quota of 12,000 requests/100 seconds. Batch operations on 50+ files are fine but add a small sleep for 100+.
3. **Trash vs delete** — `files().delete()` permanently deletes. To trash instead: `service.files().update(fileId=fid, body={"trashed": True}).execute()`. Prefer trash for safety.
4. **Moving to root** — To move a file to root, use `removeParents=<current_parent>` without `addParents`. Or `addParents="root"`.
