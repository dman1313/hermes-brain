# gbrain Install on Hermes (2026-05-23)

Installed gbrain v0.39.0.0 (Garry Tan's agent brain) on Hermes VPS.

## Prerequisites

- Bun (was already installed at `~/.bun/bin/bun`, v1.3.12)
- Hermes workspace at `~/.hermes/`

## Install/Upgrade

Old version was v0.10.1. Upgraded via:
```bash
bun install -g github:garrytan/gbrain
```

Postinstall was blocked by Bun's security policy (noted but not blocking).

## Init with Embedding Provider

Critical: in non-TTY contexts (agent sessions), `gbrain init` can't show the interactive provider picker. Must pass explicit flags:

```bash
# OpenAI (when OPENAI_API_KEY is available)
gbrain init --pglite --embedding-model openai:text-embedding-3-large --embedding-dimensions 1536

# ZeroEntropy (when ZEROENTROPY_API_KEY is available)
gbrain init --pglite --embedding-model zeroentropyai:zembed-1 --embedding-dimensions 1280

# Skip embeddings entirely
gbrain init --pglite --no-embedding
```

## API Key Configuration

gbrain doesn't reliably read env vars during init. The `gbrain config set` command only accepts a limited set of keys. For reliable key injection, write directly to `~/.gbrain/config.json`:

```json
{
  "engine": "pglite",
  "database_path": "/home/ubuntu/.gbrain/brain.pglite",
  "embedding_model": "openai:text-embedding-3-large",
  "embedding_dimensions": 1536,
  "openai_api_key": "sk-...",
  "anthropic_api_key": "sk-ant-..."
}
```

If you switch embedding providers, delete `~/.gbrain/` and re-init (fresh brain only — don't do this on a populated brain; use `gbrain reinit-pglite` instead).

## Skillpack Scaffold

The `gbrain skillpack scaffold` command needs to find the gbrain repo root. When installed globally via bun, the source lives at `~/.bun/install/global/node_modules/gbrain/`. Run from there:

```bash
cd ~/.bun/install/global/node_modules/gbrain
gbrain skillpack scaffold --all --workspace /home/ubuntu/.hermes --trust
```

Flags:
- `--workspace PATH` — target agent workspace (Hermes: `~/.hermes`)
- `--trust` — skip confirm prompts (needed in non-TTY)
- `--all` — scaffold all 43+ bundled skills

64 files written to `~/.hermes/skills/` (skills + conventions + config files).

## Manual Fix: RESOLVER.md

`RESOLVER.md` (the skill dispatcher) was present in the gbrain source but not scaffolded. Copy manually:

```bash
cp ~/.bun/install/global/node_modules/gbrain/skills/RESOLVER.md ~/.hermes/skills/RESOLVER.md
```

## Key Files After Install

| File | Purpose |
|------|---------|
| `~/.gbrain/brain.pglite` | PGLite database (embedded Postgres) |
| `~/.gbrain/config.json` | API keys and config |
| `~/.hermes/skills/RESOLVER.md` | Skill dispatcher (must exist) |
| `~/.hermes/skills/signal-detector/SKILL.md` | Fire on every inbound message |
| `~/.hermes/skills/brain-ops/SKILL.md` | Brain-first lookup before external APIs |
| `~/.hermes/skills/_AGENT_README.md` | Agent contract |

## Search Mode

Default: `conservative` (no OpenAI key detected at init time).
To switch: `gbrain config set search.mode balanced` (sweet spot for Sonnet/DeepSeek tier).
Cost matrix: conservative $40-200/mo, balanced $100-500/mo, tokenmax $200-1,000/mo (at 10K queries/mo).

## Health Verification

```bash
gbrain doctor                          # full health check
gbrain doctor --json                   # machine-readable
gbrain search modes                    # confirm search mode
gbrain models doctor                   # 1-token probe per configured model
```

Fresh brain: expect ~75/100 score (rises as pages are imported and embedded).

## Next Steps (post-install)

```bash
gbrain import ~/wiki/ --no-embed       # import markdown files
gbrain embed --stale                   # generate vector embeddings
gbrain extract links --source db       # backfill knowledge graph
gbrain extract timeline --source db    # backfill timeline
gbrain autopilot --install             # background daemon for nightly enrichment
gbrain soul-audit                      # customize agent identity
```
