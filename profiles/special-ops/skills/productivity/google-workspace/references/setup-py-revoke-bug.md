# setup.py Revoke URL Bug — Fixed 2026-05-11

## Bug
The `revoke()` function in `/home/ubuntu/.hermes/skills/productivity/google-workspace/scripts/setup.py` had a literal `***` placeholder instead of the actual token in the revoke URL:

```python
# Before (broken):
urllib.request.Request(
    f"https://oauth2.googleapis.com/revoke?token=***"  # ← literal asterisks
)
```

This meant:
- The revoke HTTP request always sent `token=***` as the literal value
- Google's revoke endpoint would either reject or silently accept it
- The actual token was never revoked remotely
- The `except` clause caught the failure, logged "Remote revocation failed (token may already be invalid): ..."
- The local token file was still deleted as a fallback

## Fix Applied

```python
# After (fixed):
urllib.request.Request(
    f"https://oauth2.googleapis.com/revoke?token={creds.token}",
)
```

Also fixed indentation — the original had the f-string at the wrong indent level (missing one level), causing a SyntaxError if someone tried to add the `{creds.token}` interpolation correctly.
