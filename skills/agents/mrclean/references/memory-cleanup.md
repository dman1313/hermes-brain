# Memory Store Cleanup

When the persistent memory store (`memory` tool) approaches capacity (≥90%), write operations start failing. This is visible in errors.log as "Memory at N/4,000 chars. Adding this entry would exceed the limit."

## Audit Checklist

1. **Cross-reference with user profile** — Any memory entry that's also in the user profile is a duplicate. Remove from memory (profile takes priority for user facts).
2. **Tool/API specs** — Entries like "ScrapingBee vX at URL Y" or "CloakBrowser v0.3.28: 49 patches" are re-discoverable via skills or tool invocation. Remove.
3. **Model specs** — Model version numbers, parameter counts, context window sizes belong in the model roster, not memory. Remove.
4. **Condense verbose entries** — Two entries about the same project can merge into one shorter entry.
5. **Stale dates** — Check whether meeting dates and deadlines have passed.

## Safe to Remove

- GitHub CLI tool facts (re-discoverable)
- API endpoint versions and patch counts (in skills)
- Model architecture details (in roster/API)
- Wiki workflow descriptions that duplicate user profile rules

## Keep

- Credentials and access tokens (though ideally these should be in secrets, not memory)
- Thread/channel mappings
- Active project paths and key config locations
- Human Good AI legal/financial deadlines
- Current service ports and systemd names

## Method

Use `memory(action='remove', old_text='unique substring', target='memory')` — one entry at a time. Verify after each removal with the usage% in the response.
