# NotebookLM Auth SCP Transfer

How to authenticate nlm on a headless VPS by transferring cookies from a machine with Chrome.

## Prerequisites

- nlm installed on both machines: `uv tool install notebooklm-mcp-cli`
- SSH/SCP access from GUI machine to VPS
- Google Chrome on the GUI machine

## Procedure

### 1. Authenticate on GUI machine (Mac)

```bash
nlm login
```

This launches Chrome, navigates to NotebookLM, and extracts cookies. Verify:

```bash
nlm login --check
nlm notebook list
```

### 2. Transfer auth data to VPS

IMPORTANT: Use the correct SCP syntax to avoid nesting.

```bash
# CORRECT — copies contents INTO the target directory
scp -r ~/.notebooklm-mcp-cli/* ubuntu@<vps-ip>:/home/ubuntu/.notebooklm-mcp-cli/

# CORRECT — -r with source dir, target dir exists
scp -r ~/.notebooklm-mcp-cli ubuntu@<vps-ip>:/home/ubuntu/
```

```bash
# WRONG — trailing slash on source WITH trailing slash on target
# Creates nested ~/.notebooklm-mcp-cli/.notebooklm-mcp-cli/
scp -r ~/.notebooklm-mcp-cli/ ubuntu@<vps-ip>:/home/ubuntu/.notebooklm-mcp-cli/
```

### 3. Verify on VPS

```bash
nlm login --check
nlm notebook list
```

### 4. Fix nested directory (if SCP went wrong)

If you accidentally created a nested directory, fix with:

```bash
rm -rf ~/.notebooklm-mcp-cli/profiles
mv ~/.notebooklm-mcp-cli/.notebooklm-mcp-cli/* ~/.notebooklm-mcp-cli/
mv ~/.notebooklm-mcp-cli/.notebooklm-mcp-cli/.* ~/.notebooklm-mcp-cli/ 2>/dev/null || true
rmdir ~/.notebooklm-mcp-cli/.notebooklm-mcp-cli/
```

### 5. Set output format (config carries over from Mac)

Auth data carries the Mac's config. If JSON output appears unexpectedly:

```bash
nlm config set output.format table
```

## Cookie Lifetime

- Google cookies: ~2-4 weeks
- CSRF token: auto-refreshed by nlm
- When auth fails, repeat steps 1-2

## Our Setup

- Account: dwayneprimeau@gmail.com
- VPS: ubuntu@43.167.176.156
- Package: notebooklm-mcp-cli v0.6.10 (installed via uv)
- Binary on VPS: /home/ubuntu/.local/bin/nlm
- Auth data path: ~/.notebooklm-mcp-cli/

## CLI Pitfalls

- `nlm notebook create` does NOT support `--json` — capture the ID from stdout (`ID: <uuid>`)
- `nlm notebook list --json` works; `nlm notebook list --title` for readable output
- `nlm source list --json` works; use `--url` for readable output
