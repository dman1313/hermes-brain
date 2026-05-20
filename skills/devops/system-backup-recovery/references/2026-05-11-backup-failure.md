# May 11, 2026 — Backup Failure Incident

## Incident Summary

The `hermes-gdrive-backup` cron job (ID: `2bac775e7d28`) ran at 2026-05-11 03:00 SGT and failed.

**Error:**
```
RuntimeError: checking third-party user token: bad request:
Personal Access Tokens are not supported for this endpoint
```

## Diagnosis

### Step 1 — Check cron output
```bash
cat /home/ubuntu/.hermes/cron/output/2bac775e7d28/2026-05-11_03-00-22.md
```

### Step 2 — Check token expiry
```bash
cat /home/ubuntu/.hermes/google_token.json | python3 -c \
  "import json,sys; d=json.load(sys.stdin); print('Expiry:', d.get('expiry','unknown'))"
```

### Step 3 — Test Drive API directly
```bash
python /home/ubuntu/.hermes/skills/productivity/google-workspace/scripts/google_api.py \
  drive search "hermes-backup-"
```

## Results

- **Token expiry:** `2026-05-11T01:04:56Z` (UTC). At backup run time (May 10 19:00 UTC), the token was still valid.
- **Drive API search succeeded** when tested at 14:20 SGT (May 11, 06:20 UTC — ~5 hours after expiry).
- **Drive had 8 backup files** from May 4–11, including one from today (03:57 SGT, possibly from a failed retry by the double-call bug).
- **Previous 7 days (May 4–10) all succeeded** with exit code 0 and correct uploads.

## Likely Root Cause

The Google OAuth `refresh_token` was rejected when the backup script's `get_credentials()` attempted to auto-refresh the expired token. The `google.oauth2.credentials.Credentials.refresh()` call raised:

```
RuntimeError: checking third-party user token: bad request:
Personal Access Tokens are not supported for this endpoint
```

This happens when:
1. The token was originally obtained via a Google OAuth consent flow
2. The refresh token was issued to a different client ID/scopes than currently used
3. Google's token endpoint rejects the refresh attempt (common when the OAuth app is in "testing" mode or the token predates a client secret reset)

## Resolution

Re-authentication fixed it:
```bash
cd /home/ubuntu/.hermes/skills/productivity/google-workspace/scripts
python setup.py
```

After re-auth, Drive API calls work again.

## Script Bug Found

The `upload()` function in `/home/ubuntu/scripts/hermes-backup.py` has a latent bug:

```python
def upload(path: Path) -> dict:
    run(*GAPI, "drive", "upload", str(path), "--name", path.name, check=False)  # BUG: discarded output
    result = run(*GAPI, "drive", "upload", str(path), "--name", path.name, check=False)
```

The first `run()` call:
- Uploads the file
- Prints output (JSON) to stdout
- Uses `check=False` so errors are silently swallowed
- The return value is never stored or parsed

This means:
1. The upload runs TWICE, doubling execution time and API quota
2. The first call's error output (if any) may confuse cron monitoring
3. The script relies on the second call succeeding, but if the first call succeeded and created/updated the file, the second call is redundant

**Fix:** Remove the first `run()` call entirely.
