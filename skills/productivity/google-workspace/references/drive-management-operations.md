# Drive Management Operations (Move, Folder, Reorganize)

`google_api.py` has `drive search`, `drive upload`, and `drive delete` but NO `drive move`, `drive create-folder`, or `drive reorganize`. For these operations, write a standalone Python script using the same OAuth token.

## Prerequisites

Use the Hermes venv python (not system python3) to avoid `hermes_constants` import errors:

```bash
~/.hermes/hermes-agent/venv/bin/python /tmp/drive_ops.py
```

## Credential Loading (standalone script)

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

## Create Folder

```python
body = {"name": "Folder Name", "mimeType": "application/vnd.google-apps.folder"}
folder = service.files().create(body=body, fields="id,name").execute()
folder_id = folder["id"]
```

## Move File (add to new parent, remove from old)

```python
file = service.files().get(fileId=file_id, fields="parents").execute()
prev_parents = ",".join(file.get("parents", []))
service.files().update(
    fileId=file_id,
    addParents=new_parent_id,
    removeParents=prev_parents,
    fields="id,parents"
).execute()
```

## Delete File

```python
service.files().delete(fileId=file_id).execute()
```

## Pitfalls

1. **`google_api.py` cannot be imported standalone** — it uses `argparse` at module level which triggers on import. Always write a standalone script instead of trying to `from google_api import get_drive_service`.
2. **Must use Hermes venv python** — system python3 won't have `hermes_constants` module. Always use `~/.hermes/hermes-agent/venv/bin/python`.
3. **`drive.file` scope** — the granted scope only covers files the app created or was explicitly granted. For reorganizing files the user owns (which is the typical case), this works fine. For shared drives or files owned by others, you'd need broader scopes.
4. **Rate limits** — Drive API has a default quota of 12,000 requests/100 seconds. For bulk operations (50+ files), add a small sleep between calls to avoid 429s.
5. **Moving between My Drive and Shared Drives** requires `supportsAllDrives=true` parameter.
6. **Duplicate file listing** — `drive search ""` returns files sorted by modifiedTime desc. When identifying duplicates by name, keep the first occurrence (newest).
