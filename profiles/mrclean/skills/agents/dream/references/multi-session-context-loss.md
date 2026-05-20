# Multi-Session Context Loss — Detection & Case Studies

## What It Is

When a project spans multiple sessions (context compaction, session restart, or model switch), the agent loses critical deployment/configuration details. It then re-infers them from the project name, often getting them wrong.

## Detection Pattern

1. **Cluster sessions by project topic** — Look for sessions starting with the same project name or description
2. **Check for user corrections about domains/URLs** — Search user messages for: "not my", "wrong domain", "that's not", "I said"
3. **Compare deployment targets across sessions** — If the agent deployed to domain A in session 1 but domain B in session 2 (without user instruction to change), context was lost
4. **Count corrections** — If the user corrected the same detail 2+ times across different sessions, it's a systemic pattern

## Case Study: Agent Ready Project (May 3, 2026)

**Project:** "Agent Ready" — middleware service for certifying websites as agent-optimized
**Sessions:** 4 total (session_20260503_045857, 053539, 055651, 184137)
**Total size:** ~1.5MB across all sessions

**What happened:**
- Session 1 (045857): Agent built the service. Deployed to `agentready.humangood.ai` (correct). User said "This not my webpage" — agent had shown the wrong URL in verification but was actually deploying correctly. Final message showed correct domain.
- Session 2 (053539): Continued development with Claude Code. No domain issues.
- Session 3 (055651): Further iteration. No domain issues.
- Session 4 (184137): Agent re-deployed and verified `agentready.ai` (WRONG domain). User corrected again: "This not my webpage". Agent then fixed to `agentready.humangood.ai`.

**Root cause:** Context compaction between sessions 1→4 lost the domain mapping. The agent inferred `agentready.ai` from the project name "Agent Ready" instead of recalling the user's actual domain.

**Impact:** 2 identical corrections, wasted deployment cycles, eroded trust.

## Prevention Recommendations

For agents handling multi-session projects:
1. After a user correction about a domain/URL/deployment target, immediately persist it as a memory entry
2. Before deploying, verify the target matches what the user specified — don't infer from project name
3. When resuming a project from a compacted context, explicitly ask or check existing deployment configs for the correct target
4. Context compaction summaries should preserve URLs and domains as structured key-value pairs, not bury them in prose
