# Installing External Skills from awesome-agent-skills

The [awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) repo is a curated collection of 1100+ official agent skills from teams like Anthropic, Google, Stripe, Vercel, Cloudflare, Sentry, DuckDB, and more. These skills are published in Claude Code / Codex SKILL.md format, which is YAML frontmatter + markdown — close enough to Hermes format to work directly.

## Finding the Source Repo

Each skill in the README links to `officialskills.sh/<owner>/skills/<skill-name>`. That page is a React SPA with the source GitHub repo embedded.

### Step 1: Find the GitHub repo from an officialskills.sh page

```python
import re
import subprocess

owner = "getsentry"
skill = "sentry-python-sdk"

html = subprocess.run(
    ["curl", "-sL", f"https://officialskills.sh/{owner}/skills/{skill}"],
    capture_output=True, text=True
).stdout

# Extract GitHub repo names (not images)
repos = [u for u in re.findall(
    r'github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)', html
) if not u.endswith('.png') and 'VoltAgent' not in u]

print(repos[0])  # e.g., getsentry/sentry-for-ai
```

### Step 2: Find the SKILL.md path

The SKILL.md is usually at `https://raw.githubusercontent.com/<repo>/main/skills/<skill-name>/SKILL.md`. But paths vary:

| Pattern | Example |
|---------|---------|
| `skills/<name>/SKILL.md` | `duckdb/duckdb-skills/main/skills/query/SKILL.md` |
| `skills/<name>/SKILL.md` (nested) | `getsentry/sentry-for-ai/main/skills/sentry-python-sdk/SKILL.md` |
| `<name>/SKILL.md` (flat) | `garrytan/gstack/main/office-hours/SKILL.md` |
| Root `SKILL.md` | `meodai/skill.color-expert/main/SKILL.md` |
| Claude plugin `plugins/<name>/SKILL.md` | `trailofbits/skills/main/plugins/...` |

### Step 3: Probe paths

```bash
# Quick probe for common patterns
for path in \
  "skills/$SKILL/SKILL.md" \
  "$SKILL/SKILL.md" \
  "SKILL.md"; do
  status=$(curl -sI -o /dev/null -w "%{http_code}" \
    "https://raw.githubusercontent.com/$REPO/main/$path")
  [ "$status" = "200" ] && echo "FOUND: main/$path"
done
```

### Step 4: Download and save

```bash
mkdir -p ~/.hermes/skills/<category>/<name>
curl -sL "$RAW_URL" -o ~/.hermes/skills/<category>/<name>/SKILL.md
```

### Step 5: Verify

```bash
head -10 ~/.hermes/skills/<category>/<name>/SKILL.md
wc -l ~/.hermes/skills/<category>/<name>/SKILL.md
```

## Known Repos

| Skill Owner | GitHub Repo | Path Pattern |
|-------------|-------------|--------------|
| Sentry | `getsentry/sentry-for-ai` | `skills/<name>/SKILL.md` |
| DuckDB | `duckdb/duckdb-skills` | `skills/<name>/SKILL.md` |
| Stripe | `stripe/ai` | `skills/<name>/SKILL.md` |
| Garry Tan | `garrytan/gstack` | `<name>/SKILL.md` |
| Meodai | `meodai/skill.color-expert` | `SKILL.md` |
| hqhq1025 | `hqhq1025/skill-optimizer` | `skills/<name>/SKILL.md` |
| Trail of Bits | `trailofbits/skills` | `plugins/<name>/SKILL.md` (Claude plugin format) |

## Pitfalls

- **officialskills.sh pages are minified React SPAs** — `grep` won't work; use Python `re.findall` on the raw HTML
- **GitHub API rate limits** — the API times out under heavy use; prefer raw.githubusercontent.com direct downloads
- **Branch names** — most use `main`, but some use `master`. Probe both.
- **Community skills** — many community-contributed skills have repos that don't exist or moved. Check the officialskills.sh page first.
- **Web search blocked** — If `web_search` returns subscription errors, fall back to direct GitHub probing with curl.
