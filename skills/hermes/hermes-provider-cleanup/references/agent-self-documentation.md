# Agent Self-Documentation Workflow

When asked to "self-document" or update the agent profile in the shared memory vault:

## Procedure

```bash
# 1. Pull latest
cd /home/ubuntu/agent-memory && git pull --rebase

# 2. Read current profile
#    Located at Agents/<agent-name>.md

# 3. Gather current state (run these to get live data)
hermes status              # model, providers, API keys, gateway, platforms
hermes skills list         # count enabled skills
hermes mcp list            # MCP servers and status
hermes cron list           # scheduled jobs
systemctl --user list-units --type=service --state=running  # user services
systemctl list-units --type=service --state=running | grep -E "hermes|agent|caddy|freellm|9router"  # system services

# 4. Update the agent profile with current state
#    Key sections: Model Routing, API Keys, Skills, MCP Servers,
#    Running Services, Scheduled Jobs, Agent Fleet, Components

# 5. Commit and push
cd /home/ubuntu/agent-memory && git add -A && git commit -m "agents: <agent> self-documents" && git push
```

## Profile Sections (Agents/hermes.md template)

- **Model routing table** — tier, model, provider for each routing level
- **API keys configured** — provider name, key fingerprint (redacted)
- **Messaging platforms** — which are configured, home channel IDs
- **Skills** — count + key skill names by category
- **MCP servers** — name, transport, status
- **Running services** — service name, port, description
- **Scheduled jobs** — count + key job names
- **Agent fleet** — agent name, role description
- **Components** — dashboards, databases, shared vaults, wikis
- **Strengths** — what this agent uniquely does

## Pitfalls

- **Stale docs are worse than no docs.** Always pull live status, don't trust the existing profile text.
- **Also fix related docs.** While in the vault, check for other stale files (like Project/ docs) and fix them in the same commit.
- **Redact secrets.** Show key fingerprints (sk-...abcd) not full keys.
- **Include ports.** Services without ports are hard to debug later.
