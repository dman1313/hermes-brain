#!/usr/bin/env python3
"""
Dropbox OAuth helper for LLM Wiki sync.
Usage: python3 dropbox-auth.py
Then open the URL, click Allow, copy the code.
Then: python3 dropbox-finish.py <CODE>
"""
import dropbox
from dropbox import DropboxOAuth2FlowNoRedirect

APP_KEY = "<DROPBOX_APP_KEY>"
APP_SECRET = "<DROPBOX_APP_SECRET>"

auth_flow = DropboxOAuth2FlowNoRedirect(APP_KEY, APP_SECRET)
authorize_url = auth_flow.start()

print("=" * 60)
print("1. Go to this URL in your browser:")
print(authorize_url)
print("=" * 60)
print("2. Click 'Allow'")
print("3. Copy the authorization code")
print("4. Run: python3 dropbox-finish.py <CODE>")
