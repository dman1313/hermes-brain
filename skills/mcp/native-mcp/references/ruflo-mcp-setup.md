# Ruflo (Claude Flow V3) MCP Server Integration

## What It Is
Ruflo (formerly Claude Flow) is a multi-agent AI harness — 293 MCP tools covering agent lifecycle, swarm orchestration, memory/embeddings, hooks/intelligence, tasks/workflows, hive-mind, WASM agents, browser sessions, GitHub integration, neural training, and more.

**Repo:** https://github.com/ruvnet/ruflo
**NPM:** `ruflo` (v3.10.36+)
**License:** MIT

## Install Steps

1. **Clone + install** (optional, for local development):
   ```bash
   cd ~ && git clone https://github.com/ruvnet/ruflo.git
   cd ruflo && npm install
   ```

2. **Global install** (recommended for MCP):
   ```bash
   npm install -g ruflo
   ```

3. **Initialize** (creates .claude/, .claude-flow/ in current dir):
   ```bash
   cd ~/ruflo && npx ruflo init --wizard
   ```

4. **Add to Hermes** — Python yaml approach (hermes mcp add chokes on `-y` flag):
   ```python
   python3 -c "
   import yaml
   with open('$HOME/.hermes/config.yaml', 'r') as f: config = yaml.safe_load(f)
   config['mcp_servers']['ruflo'] = {
       'command': 'ruflo',
       'args': ['mcp', 'start'],
       'env': {
           'CLAUDE_FLOW_MODE': 'v3',
           'CLAUDE_FLOW_HOOKS_ENABLED': 'true',
           'CLAUDE_FLOW_TOPOLOGY': 'hierarchical-mesh',
           'CLAUDE_FLOW_MAX_AGENTS': '15',
           'CLAUDE_FLOW_MEMORY_BACKEND': 'hybrid',
       },
       'timeout': 120,
       'connect_timeout': 120,
       'enabled': True,
   }
   with open('$HOME/.hermes/config.yaml', 'w') as f:
       yaml.dump(config, f, default_flow_style=False, sort_keys=True, allow_unicode=True)
   "
   ```

5. **Test** (first run will fail — ONNX model needs to download):
   ```bash
   hermes mcp test ruflo   # expect timeout on first run
   hermes mcp test ruflo   # second run: ~17s, 293 tools discovered
   ```

## Key Tool Categories (293 total)

| Category | Example Tools | Count |
|----------|--------------|-------|
| Agent Management | agent_spawn, agent_execute, agent_list, managed_agent_* | ~15 |
| Swarm | swarm_init, swarm_status, swarm_health | 4 |
| Memory & Embeddings | memory_store, memory_search, embeddings_* | ~25 |
| Hooks & Intelligence | hooks_pre-task, hooks_route, hooks_codemod, hooks_worker-* | ~35 |
| Tasks & Workflows | task_create, task_assign, workflow_run, workflow_execute | ~20 |
| Hive-Mind | hive-mind_init, hive-mind_consensus, hive-mind_broadcast | ~10 |
| WASM Agents | wasm_agent_create, wasm_agent_prompt, wasm_gallery_* | ~25 |
| AgentDB | agentdb_health, agentdb_pattern-store, agentdb_graph-query | ~15 |
| GitHub | github_repo_analyze, github_pr_manage, github_issue_track | 5 |
| Neural | neural_train, neural_predict, neural_patterns | 6 |
| Browser Sessions | browser_session_record, browser_session_end | 4 |
| AIDefence | aidefence_scan, aidefence_is_safe, aidefence_has_pii | 5 |
| Performance | performance_report, performance_benchmark | 6 |
| Guidance | guidance_recommend, guidance_discover, guidance_workflow | 5 |
| Autopilot | autopilot_enable, autopilot_config, autopilot_learn | 8 |
| Coordination | coordination_topology, coordination_consensus | 7 |
| ruvllm/WASM LLM | ruvllm_status, ruvllm_hnsw_create, ruvllm_sona_* | ~10 |
| Claims | claims_claim, claims_handoff, claims_steal | ~10 |
| Config | config_get, config_set, config_list | 6 |
| Terminal | terminal_create, terminal_execute | 5 |

## Pitfalls

- **ONNX model loading**: First start downloads all-MiniLM-L6-v2 (23MB) from HuggingFace. Takes 15-30s. After caching, connects in ~17s.
- **Startup noise**: Server prints ONNX loading messages to stderr. Stdio MCP responses go to stdout. This is normal — stderr lines are not errors.
- **Monorepo build**: Local clone v3/ uses pnpm workspaces (`workspace:*` protocol). npm can't build it. Use pnpm or just use the globally installed npm package.
- **env vars**: The CLAUDE_FLOW_* env vars configure behavior. Key ones:
  - `CLAUDE_FLOW_MODE=v3` — enables V3 features
  - `CLAUDE_FLOW_TOPOLOGY=hierarchical-mesh` — queen + peer communication
  - `CLAUDE_FLOW_MEMORY_BACKEND=hybrid` — combines in-memory + persistent storage
