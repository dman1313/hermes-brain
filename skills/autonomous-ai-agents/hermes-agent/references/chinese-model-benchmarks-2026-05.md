# Chinese AI Model Benchmark Comparison (May 2026)

Data collected from official HuggingFace model cards, LiveBench, and pricing pages.

## Benchmark Scores

### Coding & Agentic

| Benchmark | DeepSeek V4 Pro | Kimi K2.6 | GLM-5.1 | MiMo V2.5 Pro |
|-----------|:-:|:-:|:-:|:-:|
| SWE-bench Verified | 80.6 | 80.2 | — | 78.9 |
| SWE-bench Pro | 55.4 | **58.6** | 58.4 | 57.2 |
| Terminal-Bench 2.0 | 67.9 | 66.7 | 63.5 | **68.4** |
| LiveCodeBench v6 | **93.5** | 89.6 | — | — |
| τ³-bench (multi-turn agentic) | — | — | 70.6 | **72.9** |
| HLE w/ tools | 48.2 | **54.0** | 52.3 | 48.0 |
| BrowseComp | **83.4** | 83.2 | 68.0 | — |
| MCP-Atlas | 62.2 | 63.8 | **71.8** | — |
| Tool-Decathlon | **51.8** | 50.0 | 40.7 | — |

### DeepSWE (Contamination-Free, May 2026)

| Model | Score |
|-------|------:|
| GPT-5.5 | 70% ±4% |
| GPT-5.4 | 56% ±5% |
| Claude Opus 4.7 | 54% ±5% |
| Claude Sonnet 4.6 | 32% ±4% |
| Gemini 3.5 Flash | 28% ±4% |
| GPT-5.4 Mini | 24% ±4% |
| **Kimi K2.6** | **24% ±4%** |
| **MiMo V2.5 Pro** | **19% ±4%** |
| **GLM-5.1** | **18% ±4%** |
| Gemini 3.1 Pro | 10% ±3% |
| **DeepSeek V4 Pro** | **8% ±2%** |

**Key insight:** DeepSeek V4 Pro drops from 80.6% (SWE-bench Verified) to 8% (DeepSWE). Strong evidence of SWE-bench contamination. GLM-5.1's "strongest for coding" reputation from community sources does not hold on contamination-free benchmarks.

### Reasoning & Knowledge

| Benchmark | DeepSeek V4 Pro | Kimi K2.6 | GLM-5.1 | MiMo V2.5 Pro |
|-----------|:-:|:-:|:-:|:-:|
| GPQA-Diamond | 90.1 | **90.5** | 86.2 | — |
| AIME 2026 | 95.2 | **96.4** | 95.3 | — |
| MMLU (base) | **90.1** | ~87.1 | — | 89.4 |
| GSM8K (base) | 92.6 | 92.1 | — | **99.6** |
| MATH (base) | 64.5 | 70.2 | — | **86.2** |
| LiveBench Global | **73.58** | 72.17 | 70.18 | 58.14* |

*LiveBench has MiMo V2 Pro, not V2.5 Pro

## Pricing ($/1M tokens, OpenRouter, May 2026)

| Model | Input | Output | Blended (1:1) |
|-------|------:|-------:|--------:|
| MiMo V2.5 Pro | $0.44 | $0.87 | **$1.31** |
| DeepSeek V4 Pro | $0.44 | $0.87 | **$1.31** |
| Kimi K2.6 | $0.73 | $3.49 | **$4.22** |
| GLM-5.1 | $0.98 | $3.08 | **$4.06** |

**Notes:**
- DeepSeek V4 Pro "promo" pricing (97.5% off) IS the permanent new price. No rush to buy credits.
- MiMo V2.5 Pro had a 99% price cut on May 27, 2026.
- GLM-5.1 has a coding-only subscription plan (¥49-469/mo) — cannot use for non-coding tasks on the plan.

## Subscription Plans

### MiMo (Xiaomi) — Credit-based
| Tier | Credits/mo | ~Cost |
|------|-----------|-------|
| Lite | 49.2B tokens | ~$6/mo |
| Standard | 132B tokens | ~$16/mo |
| Pro | 456B tokens | ~$50/mo |
| Max | 984B tokens | ~$100/mo |

All tiers access all 8 MiMo models. 20% off during off-peak hours.

### Kimi (Moonshot) — Pure PAYG
No subscription plans. Cumulative recharge tiers for rate limits.
K2.6: ¥6.50/M input, ¥27/M output (~$0.90/$3.75)

### GLM (Z.ai) — Coding-only subscription
| Tier | ~Cost | Notes |
|------|-------|-------|
| Lite | ~$7/mo | "3x Claude Pro quota" |
| Pro | ~$21/mo | 5x Lite |
| Max | ~$65/mo | 20x Lite |

Coding tools only (Claude Code, OpenClaw, etc.). Non-coding requires PAYG.

## Model Routing Recommendations

| Use Case | Best Model | Why |
|----------|-----------|-----|
| Orchestrator (daily driver) | MiMo V2.5 Pro | Best τ³-bench, cheapest, 1M context, strong agentic |
| Coding agent | Kimi K2.6 | Best SWE-bench Pro, best HLE w/ tools |
| Deep reasoning | DeepSeek V4 Pro | Best LiveCodeBench, best MMLU |
| Tool-heavy / MCP tasks | GLM-5.1 | Best MCP-Atlas (71.8) |
| Delegation children | MiMo V2.5 Pro or DeepSeek V4 Flash | Cheapest capable |

**Key rule:** If you have subscription plans, burn through those before touching PAYG models.
