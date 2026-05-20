---
name: dropbox-obsidian-wiki-sync
description: Run and repair the Dropbox sync for /home/ubuntu/wiki -> /Obsidian-Wiki when the stored token has expired.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Dropbox Obsidian Wiki Sync

Use this when the Dropbox wiki push job needs to run or when `/home/ubuntu/.local/bin/dropbox-sync.sh` fails with Dropbox auth errors.

## Paths
- Sync script: `/home/ubuntu/.local/bin/dropbox-sync.sh`
- Auth start script: `/home/ubuntu/.local/bin/dropbox-auth.py`
- Auth finish script: `/home/ubuntu/.local/bin/dropbox-finish.py`
- Token file: `/home/ubuntu/.dropbox-wiki-token`
- Local wiki dir: `/home/ubuntu/wiki`
- Dropbox target: `/Obsidian-Wiki`

## Normal run
```bash
/home/ubuntu/.local/bin/dropbox-sync.sh
```

Success ends with:
```text
Sync complete! Uploaded N file(s).
```

## Common failure: expired access token
Symptoms:
- `invalid_access_token` in refresh-token mode
- `expired_access_token` in access-token mode
- Message like `Unable to refresh access token without refresh token and app key`

Most commonly this means the token file contains only a short-lived access token instead of a refresh token, but it can also mean the stored refresh token was revoked or is otherwise unusable. Check token length/prefix before assuming the file only contains an access token.

In this environment, `.dropbox-wiki-token` values beginning with `sl.` or `sl.u.` indicate stored access tokens, not refresh tokens; once they expire, both `/home/ubuntu/.local/bin/dropbox-sync.sh` and `/home/ubuntu/.local/bin/photo-news-sync.sh` will fail until Dropbox is reauthorized.

## Reauthorize
1. Start auth flow:
```bash
python3 /home/ubuntu/.local/bin/dropbox-auth.py
```
2. Open the printed Dropbox authorization URL in a browser.
3. Log in to the intended Dropbox account and click **Allow**.
4. Copy the auth code.
5. Finish auth and save the new token:
```bash
python3 /home/ubuntu/.local/bin/dropbox-finish.py '<AUTH_CODE>'
```
6. Re-run sync:
```bash
/home/ubuntu/.local/bin/dropbox-sync.sh
```

## Notes
- `dropbox-finish.py` stores `refresh_token` if Dropbox returns one, otherwise it falls back to storing `access_token`.
- If Dropbox does not return a refresh token, future syncs will expire again and need reauthorization.
- `/home/ubuntu/.local/bin/photo-news-sync.sh` uses the same Dropbox token file and should follow the same refresh-token pattern as `dropbox-sync.sh`; if it fails with `expired_access_token`, inspect whether it still assumes access-token-only auth.
- Browser automation can reach the auth page, but if Dropbox requires login and there are no stored credentials, the flow must be completed by a human.
- **This Dropbox token now also powers full Hermes state backups.** The script `/home/ubuntu/scripts/hermes-dropbox-backup.py` (created 2026-05-11) reuses the same `/home/ubuntu/.dropbox-wiki-token` to upload a tarball of Hermes skills, config, cron, and gateway state to Dropbox `/hermes-backups/`. If the token expires, both wiki sync AND Hermes state backup will break — re-auth fixes both.

## Cron job configuration

The wiki Dropbox sync runs as a Hermes cron job (`wiki-dropbox-sync`, ID `233d2e3c4fbe`) on a `*/15` schedule. A separate job (`photo-news-dropbox-sync`, ID `bcca6a98591b`) handles photo.news sync to `/PhotoNews` using the same token file.

**Critical pitfall — silently broken cron jobs:** If a cron job has `model: null` AND no `script` attached, every run produces `(No response generated)` — the sync never runs, and there is no error message. The `last_status` shows `error` but the output file says nothing useful. Even with a script attached, a null-model job may still show `last_status: error` because no LLM agent processes the script output. The fix: attach a wrapper script AND assign a model (even a cheap one like `mimo-v2-pro`).

The scripts live at:
- `scripts/dropbox_wiki_sync.py` — wraps `dropbox-sync.sh` and reports exit code + output
- `scripts/dropbox_photo_sync.py` — wraps `photo-news-sync.sh` and reports exit code + output

**Pitfall — delivery field misleading:** Cron job delivery `local` means output is saved but never sent anywhere. The `last_status: ok` / `error` field only means the Hermes cron run completed, not that files were synced. Always read the output file under `~/.hermes/cron/output/<job_id>/` to verify actual sync results.

## Monitoring / status checks
- Cron jobs: `wiki-dropbox-sync` (ID `233d2e3c4fbe`), `photo-news-dropbox-sync` (ID `bcca6a98591b`).
- Verify real sync status by inspecting the latest cron output files under `~/.hermes/cron/output/233d2e3c4fbe/` and `~/.hermes/cron/output/bcca6a98591b/`.
- Current local wiki path remains `/home/ubuntu/wiki`, and Hermes config also points `skills.config.wiki.path` to `~/wiki`.
