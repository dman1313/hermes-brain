# CLI Tools Batch Install — June 2026

User presented a categorized list of ~30 repos/tools. Assessment and install results. Two sessions: initial install (2026-06-18) and credential wiring (2026-06-18 later).

## Assessment Buckets

### Already Have / Redundant
- `cli/cli` (gh) — installed and auth'd
- `BurntSushi/ripgrep` — built into Hermes `search_files`
- `sharkdp/fd` — available, rarely needed separately
- `jqlang/jq` — available in terminal
- `github/github-mcp-server` — user confirmed already installed
- `obra/superpowers` — Hermes skills cover TDD/debug/planning
- `anthropics/skills` — Hermes skill system replaces this
- `cursor/cursor` — not using Cursor
- `modelcontextprotocol/servers` — Hermes has native equivalents
- `sourcegraph/sourcegraph` — overkill for current codebase sizes
- `tree-sitter/tree-sitter` — ast-grep covers most use cases

### Installed (useful for actual work)
- **ruff** 0.15.17 — `uv tool install ruff` (Python lint/format)
- **pre-commit** 4.6.0 — `uv tool install pre-commit` (git hooks)
- **ast-grep** 0.43.0 — `npm install -g @ast-grep/cli` (structural code search; cargo install timed out)
- **zeabur** 0.19.0 — `npm install -g zeabur` (deploy CLI; NOT an MCP server)
- **context7** MCP — configured in Hermes `mcp_servers` (live library docs)
- **firecrawl** MCP — configured in Hermes `mcp_servers` with API key (web scrape/crawl)

### Waiting on Credentials
- **zeabur** — ZEABUR_TOKEN set but `zeabur auth login` requires browser (headless VPS limitation)

### Not Relevant Now
- `supabase/supabase-mcp`, `firebase/firebase-tools` — not using these platforms
- `puppeteer/puppeteer` — Hermes has browser tools
- `ast-grep/ast-grep` (full), `pulldown-cmark`, `maud`, `calibreapp`, `mozilla/pdf.js` — AgentReady project shelved
- `release-it/release-it` — no public packages to release
- `actions/starter-workflows` — reference-only, not installable as a tool

## Install Commands

```bash
# Python CLI tools (PEP 668 safe)
uv tool install ruff          # 0.15.17
uv tool install pre-commit    # 4.6.0

# Node.js fallback (when cargo times out)
npm install -g @ast-grep/cli  # 0.43.0
npm install -g zeabur         # 0.19.0
```

## MCP Server Configuration

### context7 (live library docs)
```bash
hermes config set mcp_servers.context7.command npx
hermes config set mcp_servers.context7.args '["-y", "@upstash/context7-mcp"]'
hermes config set mcp_servers.context7.enabled true
```

### firecrawl (web scrape/crawl)
Requires API key in env. `hermes config set` can't handle nested env vars — use Python YAML:
```python
import yaml
with open('/home/ubuntu/.hermes/config.yaml', 'r') as f:
    config = yaml.safe_load(f)
config['mcp_servers']['firecrawl'] = {
    'command': 'npx',
    'args': '["-y", "firecrawl-mcp"]',
    'enabled': True,
    'env': {'FIRECRAWL_API_KEY': '<key>'}
}
with open('/home/ubuntu/.hermes/config.yaml', 'w') as f:
    yaml.dump(config, f, default_flow_style=False, sort_keys=False)
```

Both require Hermes restart to activate.

## Key Lessons

### cargo install timeout
`cargo install ast-grep --locked` timed out after 60s. The npm package `@ast-grep/cli` installed in 5s. For Rust tools that ship npm wrappers, always try npm first if cargo isn't already cached.

### zeabur is NOT an MCP server
Initially added zeabur as an MCP server (`command: zeabur, args: ['mcp']`). `zeabur --help` showed no `mcp` subcommand. Removed from MCP config — it's a CLI-only deploy tool. Always verify MCP support before adding to `mcp_servers`.

### hermes config set can't do nested env vars
`hermes config set mcp_servers.firecrawl.env.FIRECRAWL_API_KEY <key>` fails with `Invalid environment variable name`. The CLI only supports flat keys. For MCP servers needing env vars, use Python YAML manipulation directly.

### API key display truncation
The agent model truncates API keys in output. When verifying keys were written correctly, use Python `repr()` and `len()` — not the displayed value. The file usually stores the full key even when display shows truncated.

### Headless VPS + browser auth
`zeabur auth login` opens a browser for OAuth. On headless VPS, fails with `xdg-open: no method available`. Must set `ZEABUR_TOKEN` env var or have user run auth from a machine with a browser.
