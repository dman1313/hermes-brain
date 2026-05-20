#!/usr/bin/env python3
"""
Dropbox sync script for LLM Wiki.
Usage: python3 dropbox-sync.py
Requires: pip install dropbox
Requires: ~/.dropbox-wiki-token containing refresh token
"""
import os
import sys
import requests
import dropbox

APP_KEY = "<DROPBOX_APP_KEY>"
APP_SECRET = "<DROPBOX_APP_SECRET>"
TOKEN_FILE = os.path.expanduser("~/.dropbox-wiki-token")
WIKI_DIR = os.path.expanduser("~/wiki")
DROPBOX_PREFIX = "/wiki"

def get_access_token():
    if not os.path.exists(TOKEN_FILE):
        print(f"Error: No token found at {TOKEN_FILE}")
        print("Run dropbox-auth.py first to authorize.")
        sys.exit(1)
    refresh_token = open(TOKEN_FILE).read().strip()
    resp = requests.post("https://api.dropboxapi.com/oauth2/token", data={
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": APP_KEY,
        "client_secret": APP_SECRET,
    })
    data = resp.json()
    if "access_token" not in data:
        print("Error refreshing token:", data)
        sys.exit(1)
    return data["access_token"]

def sync():
    access_token = get_access_token()
    dbx = dropbox.Dropbox(access_token)

    for root, dirs, files in os.walk(WIKI_DIR):
        dirs[:] = [d for d in dirs if d not in [".git", "__pycache__", "node_modules"]]
        for file in files:
            local_path = os.path.join(root, file)
            rel_path = os.path.relpath(local_path, WIKI_DIR)
            dropbox_path = (DROPBOX_PREFIX + "/" + rel_path).replace("\\", "/")
            with open(local_path, "rb") as f:
                content = f.read()
            try:
                dbx.files_upload(content, dropbox_path, mode=dropbox.files.WriteMode("overwrite"))
                print(f"Uploaded: {rel_path}")
            except Exception as e:
                print(f"Error uploading {rel_path}: {e}")
    print("Sync complete!")

if __name__ == "__main__":
    sync()
