# Video Guide — Marketing Video Production (Phase 1 Reference)

> Phase 1 only reference for subagents producing marketing videos
> (product demos, pitch videos, explainers). Covers one-pass
> script.md + outline.md + Checkpoint Plan. Does NOT cover Phase 2-4
> (scaffolding, audio synthesis, recording).

---

## Scope: Marketing Videos Only

This is for MARKETING content — product demos, pitch videos, explainers.
Not educational or technical tutorials. Output is a 16:9 click-driven web
page that looks like a video when screen-recorded.

---

## Phase 1 Workflow: One-Pass Content Writing

### 1.1 Identify User Input

| User gives | What to do |
|---|---|
| Written article (blog, docs, whitepaper) | One-pass produce script.md + outline.md, then Checkpoint Plan |
| Direct script / talking points | Save as script.md, produce outline.md, then Checkpoint Plan |
| Nothing, just "make a video about X" | **Push back** — ask for source material. Skill does not invent content from scratch. |

### 1.2 One-Pass Produce script.md + outline.md

Both outputs in a single thinking pass. Do NOT stop between them.

1. **Write script.md** — Convert article to spoken marketing script.
   Keep article.md untouched — it is the detail source for outline info
   pools and chapter visuals (dual-source principle).

2. **Write outline.md** — Chapter splits + step counts + info pools.
   Outline is a development plan, NOT a visual spec.

**Output files**:
```
article.md    # User's original text — NEVER delete
script.md     # Spoken script (determines beats/steps)
outline.md    # Dev plan (chapter splits + steps + info pools)
```

### Outline Boundaries

| Outline MUST write | Outline MUST NOT write |
|---|---|
| Chapter splits / step counts / time estimates | Specific animation types (blur, wipe, spring) |
| Per-step screen content (hero, data, slogan, lists) | CSS implementation (filter, SVG, clip-path) |
| Chapter-level info pool (numbers, quotes, cases, tags) | Duration values (~2.5s, 80-120ms) |
| Step-level relationship hints (optional) | Micro-rhythm (stagger, sustained micro-motion) |

**Why no animation in outline**: Locking animation = chapter agent becomes
a translation machine. Leaving it open lets the agent design freely per-step
using CHAPTER-CRAFT.md's content-driven decision tree.

---

## 10 Principles (Condensed One-Liner Each)

| # | Principle | One-liner |
|---|---|---|
| 1 | 16:9 Fixed Stage | Content at 1920x1080 + transform scale — no responsive layout |
| 2 | Global Step Counter | Chapter is a pure function of step; no timers or intervals |
| 3 | Full-Screen Steps | if (step === N) return <FullScene /> — each step owns viewport |
| 4 | Narration Beat = Step | One beat of speech = one step = one focused idea |
| 5 | Hidden Controls | Progress bar / pager default opacity 0 — visible on hover only |
| 6 | No Chrome | No header, footer, page numbers, brand bars |
| 7 | Content-Driven Animation | Find intrinsic action first; entrance animation as fallback only |
| 8 | Progressive Reveal | 1 item = 1 step. Never reveal N items simultaneously with stagger |
| 9 | Single Theme | No theme-switching between chapters; colors/fonts via tokens |
| 10 | Dual Source | script.md sets beat/order, article.md sets visual density |

---

## script.md: Marketing Script Rules

- Cold open — hook in 3s. No "大家好今天我们来讲讲"
- Second person — use "你/你们", never "用户/读者/客户"
- Short sentences — ≤ 20 chars (Mandarin baseline)
- Numbers → feeling — translate stats to felt impact. Keep core numbers raw
- No structural words — no "首先/其次/最后", no "总结一下"
- Concrete examples — "on my 5-year-old laptop" not "performance is superior"
- Info retention ≥ 60% by char count; key facts/cases/arguments survive
- Anti-AI-slop: no fake empathy, fake depth, self-aggrandizement, universal
  templates ("说白了/本质上/底层逻辑"), triple parallelism
- Marketing tone: "I used it for a week" not corporate boilerplate.
  Problem→solution→result for pitching. No emoji. Use `---` as step boundaries

---

## outline.md: Marketing Outline Format

Format:
```
# Video Outline
> **Theme**: <theme-id> | **Duration**: ~Xm Ys | **Chapters**: N ch / M steps

## N. <chapter-id> — <Title> (S steps · ~Ts)

**Info Pool**:
  - <type>: <content> — source §X

**Development Plan**:
  - step 1 (~Ts) — <one-line screen content>
  - step 2 (~Ts) — <one-line screen content>

Narration excerpt: > <1-3 sentences>
```

**Rules**: 3-8 steps/chapter, 30-60s per chapter, one focused topic each.
Info pool ≥ 3 items with source annotation. No animation/means in step lines.
Asset list at end, per-chapter, ✓/⚠️ annotated.

---

## Checkpoint Plan

After script.md + outline.md are written and self-checked, STOP. Present
all 5 items to user. Do not proceed until aligned.

```
Content plan written. Files: article.md, script.md ({X} chars/~{Y}min),
outline.md ({N} ch/{M} steps + info pools + asset list).

Align 5 things:

1) Script (script.md) — edits needed? Edit file or describe changes.
2) Outline (outline.md) — edits? Check: 3-8 steps/ch, 30-60s/ch,
   clear step content, rich info pools, complete asset list.
3) Theme — pick one.
   ★ <rec 1> — best for <reason>
   ★ <rec 2> — best for <reason>
4) Assets — a) I pick from existing, b) you provide, c) all placeholders.
5) Dev mode — Chapter 1 always main-thread + forced review. After:
   A) Per-chapter review (default, safest)
   B) Sequential (all at once after last chapter)
   C) Parallel subagents (fastest, style variance expected)
```

**Theme must be confirmed** before Phase 2. If user says "you choose",
pick your top recommendation, tell them why, and give an opt-out.

---

## Hard Self-Check Protocol
After each output, run self-check before proceeding. Prefer Agent Teams
(reviewer agent + file + checklist), fallback to subAgent or self-check.
**Fix all fails before reporting to user**.

### Script Self-Check
- [ ] Info retention ≥ 60% by char count
- [ ] No emoji / book-title marks / unspokeable parentheticals
- [ ] Sentences ≤ 20 chars; second person; cold open in 3s
- [ ] Numbers translated to feeling; no structural words
- [ ] Concrete examples, not abstractions
- [ ] No fake empathy / fake depth / self-aggrandizement / universal templates / triple parallelism

### Outline Self-Check

- [ ] No "animation"/"means" lines — just screen content
- [ ] No micro-timing except (~Ts) narration estimate
- [ ] Every chapter has info pool ≥ 3 items with source annotation
- [ ] All step (~Ts) sum ≈ total (within 10%)
- [ ] 3-8 steps/chapter, one topic each
- [ ] Asset list at end, per-chapter, ✓/⚠️

---

## Don'ts

- Writing animation specs into outline — outline is for content/rhythm only
- Skipping Checkpoint Plan — never; it's the only alignment point before dev
- Deleting article.md — dual-source detail pool, never delete
- Corporate boilerplate instead of human voice
- Step counts not matching narration beats

- AI fingerprints: fake empathy, triple parallelism, universal templates
