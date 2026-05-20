# Hermes Agent Self-Evolution

**Repo:** `https://github.com/NousResearch/hermes-agent-self-evolution`
**Installed at:** `~/hermes-agent-self-evolution/`
**What it does:** Automatically evolves and optimizes Hermes Agent skills, tool descriptions, prompts, and code using DSPy + GEPA (Genetic-Pareto Prompt Evolution). No GPU — all API-based (~$1-2 per run).

## Architecture

```
Read skill → Generate eval dataset → GEPA Optimizer → Evaluate candidates → Best variant → PR
```

Guardrails: full test suite, size limits, semantic preservation, human PR review.

## Phases

| Phase | Target | Status |
|-------|--------|--------|
| 1 | Skill files (SKILL.md) | ✅ Implemented |
| 2 | Tool descriptions | 🔲 Planned |
| 3 | System prompt sections | 🔲 Planned |
| 4 | Tool implementation code | 🔲 Planned |
| 5 | Continuous improvement loop | 🔲 Planned |

## Configured Models

Defaults patched for DeepSeek (was OpenAI):

- Optimizer: `deepseek/deepseek-v4-pro`
- Evaluator: `deepseek/deepseek-v4-pro`
- Judge (dataset gen): `deepseek/deepseek-v4-pro`

Override with `--optimizer-model` and `--eval-model` flags.

## Critical: DeepSeek Endpoint

litellm routes `deepseek/deepseek-v4-pro` to `https://api.deepseek.com/beta` which returns 401. The evolve script has been patched to pass `api_base="https://api.deepseek.com"` explicitly. Also set `DEEPSEEK_API_BASE=https://api.deepseek.com` in `~/.hermes/.env`.

## Usage

```bash
cd ~/hermes-agent-self-evolution

# Dry run (no API calls)
python -m evolution.skills.evolve_skill --skill github-code-review --dry-run

# Real run (10 iterations)
DEEPSEEK_API_KEY=$(grep DEEPSEEK_API_KEY ~/.hermes/.env | cut -d= -f2) \
  python -m evolution.skills.evolve_skill --skill github-code-review --iterations 10

# Custom models
python -m evolution.skills.evolve_skill --skill github-code-review \
  --optimizer-model deepseek/deepseek-v4-pro \
  --eval-model deepseek/deepseek-v4-flash

# From session history instead of synthetic data
python -m evolution.skills.evolve_skill --skill github-code-review \
  --eval-source sessiondb
```

## Dependencies

- DSPy 3.2.1+ (pip)
- GEPA 0.0.27 (bundled with DSPy 3.2+)
- litellm 1.83+ (bundled with DSPy 3.2+)
- Click, Rich, PyYAML, OpenAI SDK

## Tests

139 tests pass (installed in Hermes venv at `~/.hermes/hermes-agent/venv/`).

```bash
cd ~/hermes-agent-self-evolution && python -m pytest tests/ -q
```

## Output

Results saved to `~/hermes-agent-self-evolution/output/<skill>/<timestamp>/`:
- `evolved_skill.md` — the optimized skill
- `baseline_skill.md` — original for comparison
- `metrics.json` — scores, sizes, timing

## Pitfalls

1. **Env var propagation**: `~/.hermes/.env` vars are NOT auto-loaded in subprocesses. Prefix commands with `DEEPSEEK_API_KEY=$(grep DEEPSEEK_API_KEY ~/.hermes/.env | cut -d= -f2)` or export manually.
2. **Dependency conflicts**: Installing dspy/litellm pulls in newer versions of `aiohttp`, `click`, `openai`, `jsonschema` that conflict with `browser-use` and `skill-seekers`. These are harmless for the evolution tool but worth noting.
3. **GEPA fallback**: If GEPA isn't available in the installed DSPy version, the evolve script falls back to MIPROv2 automatically.
