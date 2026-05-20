#!/usr/bin/env python3
"""
Complete Dropbox OAuth and save refresh token.
Usage: python3 dropbox-finish.py <AUTH_CODE>
"""
import sys
import dropbox
from dropbox import DropboxOAuth2FlowNoRedirect

APP_KEY = "<DROPBOX_APP_KEY>"
APP_SECRET = "<DROPBOX_APP_SECRET>"
TOKEN_FILE = "/home/ubuntu/.dropbox-wiki-token"

if len(sys.argv) < 2:
    print("Usage: python3 dropbox-finish.py <AUTH_CODE>")
    sys.exit(1)

auth_code = sys.argv[1].strip()
auth_flow = DropboxOAuth2FlowNoRedirect(APP_KEY, APP_SECRET)

try:
    oauth_result = auth_flow.finish(auth_code)
    print("=" * 60)
    print("Access token:", oauth_result.access_token)
    print("Refresh token:", oauth_result.refresh_token)
    print("=" * 60)
    with open(TOKEN_FILE, "w") as f:
        f.write(oauth_result.refresh_token)
    print(f"Refresh token saved to {TOKEN_FILE}")
    print("\nNow run: python3 dropbox-sync.py")
except Exception as e:
    print("Error:", e)
