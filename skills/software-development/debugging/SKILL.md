---
name: debugging
description: "Systematic debugging methodology plus language-specific debugger guides. Covers the 4-phase root cause process, Python debugging (pdb/debugpy), and Node.js debugging (--inspect/CDP)."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [debugging, troubleshooting, root-cause, python, pdb, debugpy, nodejs, node-inspect, cdp, breakpoints]
    related_skills: [test-driven-development, plan]
---

# Debugging — Methodology + Language-Specific Tools

This skill covers both the **process** of debugging (how to think about bugs) and the **tools** (how to inspect running code). Start with the methodology; reach for the language-specific section when you need breakpoints, stepping, or remote attach.

---

## Part 1: Systematic Debugging Methodology

**Core principle:** ALWAYS find root cause before attempting fixes. Symptom fixes are failure.

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

### When to Use

Use for ANY technical issue: test failures, bugs in production, unexpected behavior, performance problems, build failures, integration issues.

**Use this ESPECIALLY when:**
- Under time pressure (emergencies make guessing tempting)
- "Just one quick fix" seems obvious
- You've already tried multiple fixes
- Previous fix didn't work
- You don't fully understand the issue

### The Four Phases

#### Phase 1: Root Cause Investigation

**BEFORE attempting ANY fix:**

1. **Read Error Messages Carefully** — Don't skip past errors or warnings. They often contain the exact solution. Read stack traces completely.

2. **Reproduce Consistently** — Can you trigger it reliably? What are the exact steps? If not reproducible → gather more data, don't guess.

3. **Check Recent Changes** — What changed that could cause this? Git diff, recent commits, new dependencies, config changes.

4. **Gather Evidence in Multi-Component Systems** — For EACH component boundary: log what data enters, log what data exits, verify environment/config propagation, check state at each layer.

5. **Trace Data Flow** — Where does the bad value originate? Keep tracing upstream until you find the source. Fix at the source, not at the symptom.

**Phase 1 Completion Checklist:**
- [ ] Error messages fully read and understood
- [ ] Issue reproduced consistently
- [ ] Recent changes identified and reviewed
- [ ] Evidence gathered (logs, state, data flow)
- [ ] Problem isolated to specific component/code
- [ ] Root cause hypothesis formed

**STOP:** Do not proceed to Phase 2 until you understand WHY it's happening.

#### Phase 2: Pattern Analysis

1. **Find Working Examples** — Locate similar working code in the same codebase
2. **Compare Against References** — Read the reference implementation COMPLETELY
3. **Identify Differences** — List every difference, however small
4. **Understand Dependencies** — What other components does this need?

#### Phase 3: Hypothesis and Testing

1. **Form a Single Hypothesis** — "I think X is the root cause because Y"
2. **Test Minimally** — Make the SMALLEST possible change. One variable at a time.
3. **Verify Before Continuing** — Did it work? → Phase 4. Didn't work? → Form NEW hypothesis.
4. **When You Don't Know** — Say "I don't understand X". Don't pretend to know.

#### Phase 4: Implementation

1. **Create Failing Test Case** — Simplest possible reproduction. MUST have before fixing.
2. **Implement Single Fix** — Address the root cause. ONE change at a time. No "while I'm here" improvements.
3. **Verify Fix** — Run the specific regression test, then full suite.
4. **The Rule of Three** — If ≥ 3 fixes failed: STOP and question the architecture.

### Red Flags — STOP and Follow Process

If you catch yourself thinking:
- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "Add multiple changes, run tests"
- "It's probably X, let me fix that"
- "I don't fully understand but this might work"
- **"One more fix attempt" (when already tried 2+)**

**ALL of these mean: STOP. Return to Phase 1.**

### Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Issue is simple, don't need process" | Simple issues have root causes too. Process is fast for simple bugs. |
| "Emergency, no time for process" | Systematic debugging is FASTER than guess-and-check thrashing. |
| "Just try this first, then investigate" | First fix sets the pattern. Do it right from the start. |
| "Multiple fixes at once saves time" | Can't isolate what worked. Causes new bugs. |
| "I see the problem, let me fix it" | Seeing symptoms ≠ understanding root cause. |

### Quick Reference

| Phase | Key Activities | Success Criteria |
|-------|---------------|------------------|
| **1. Root Cause** | Read errors, reproduce, check changes, gather evidence, trace data flow | Understand WHAT and WHY |
| **2. Pattern** | Find working examples, compare, identify differences | Know what's different |
| **3. Hypothesis** | Form theory, test minimally, one variable at a time | Confirmed or new hypothesis |
| **4. Implementation** | Create regression test, fix root cause, verify | Bug resolved, all tests pass |

### With delegate_task

For complex multi-component debugging:
```python
delegate_task(
    goal="Investigate why [specific test/behavior] fails",
    context="""
    Follow systematic-debugging methodology:
    1. Read the error message carefully
    2. Reproduce the issue
    3. Trace the data flow to find root cause
    4. Report findings — do NOT fix yet

    Error: [paste full error]
    File: [path to failing code]
    Test command: [exact command]
    """,
    toolsets=['terminal', 'file']
)
```

---

## Part 2: Python Debugging (pdb + debugpy)

Three tools, picked by situation:

| Tool | When |
|---|---|
| **`breakpoint()` + pdb** | Local, interactive, simplest. Add `breakpoint()` in the source, run normally, get a REPL at that line. |
| **`python -m pdb`** | Launch an existing script under pdb with no source edits. |
| **`debugpy`** | Remote / headless / "attach to already-running process." Talks DAP, scriptable from terminal. |

**Start with `breakpoint()`.** It's the cheapest thing that works.

### When to Use

- A test fails and the traceback doesn't reveal why a value is wrong
- You need to step through a function and watch a collection mutate
- A long-running process misbehaves and you can't restart it
- Post-mortem: an exception fired and you want to inspect locals at the crash site

**Don't use for:** things `print()` / `logging.debug` solve in under a minute.

### pdb Quick Reference

| Command | Action |
|---|---|
| `n` | next line (step over) |
| `s` | step into |
| `r` | return from current function |
| `c` | continue |
| `l` / `ll` | list source around current line / full function |
| `w` | where (stack trace) |
| `u` / `d` | move up / down in the stack |
| `a` | print args of the current function |
| `p expr` / `pp expr` | print / pretty-print expression |
| `b file:line` | set breakpoint |
| `b func` | break on function entry |
| `b file:line, cond` | conditional breakpoint |
| `cl N` | clear breakpoint N |
| `!stmt` | execute arbitrary Python |
| `interact` | drop into full Python REPL in current scope |
| `q` | quit |

### Recipe 1: Local breakpoint (easiest)

```python
def compute(x, y):
    result = some_helper(x)
    breakpoint()           # <-- drops into pdb here
    return result + y
```

**Don't forget to remove `breakpoint()` before committing:**
```bash
rg -n 'breakpoint\(\)' --type py
```

### Recipe 2: Launch a script under pdb

```bash
python -m pdb path/to/script.py arg1 arg2
(Pdb) b path/to/script.py:42
(Pdb) c
```

### Recipe 3: Debug a pytest test

```bash
# Drop to pdb on failure:
pytest tests/path/to/test_file.py --pdb -p no:xdist

# Show locals in tracebacks without pdb:
pytest tests/path/to/test_file.py --showlocals --tb=long
```

**pdb does NOT work under xdist.** Always add `-p no:xdist` or run a single test with `-n 0`.

### Recipe 4: Post-mortem on any exception

```python
import pdb, sys
try:
    run_the_thing()
except Exception:
    pdb.post_mortem(sys.exc_info()[2])
```

Or wrap a whole script:
```bash
python -m pdb -c continue script.py
# When it crashes, pdb catches it and you're in the frame of the exception
```

### Recipe 5: Remote debug with debugpy

For long-lived processes: Hermes gateway, tui_gateway, a daemon.

**Pattern A: Source-edit — process waits for debugger at launch**
```python
import debugpy
debugpy.listen(("127.0.0.1", 5678))
print("debugpy listening on 5678, waiting for client...", flush=True)
debugpy.wait_for_client()
```

**Pattern B: No source edit — launch with `-m debugpy`**
```bash
python -m debugpy --listen 127.0.0.1:5678 --wait-for-client your_script.py arg1
```

**Pattern C: Attach to an already-running process**
```bash
python -m debugpy --listen 127.0.0.1:5678 --pid <pid>
```

Some kernels block ptrace-based injection. Fix with:
```bash
echo 0 | sudo tee /proc/sys/kernel/yama/ptrace_scope
```

**Alternative: `remote-pdb`** — usually what you actually want from a terminal agent:
```bash
pip install remote-pdb
```
```python
from remote_pdb import set_trace
set_trace(host="127.0.0.1", port=4444)
```
Then: `nc 127.0.0.1 4444` — you get a `(Pdb)` prompt exactly as if debugging locally.

### Python Debugging Pitfalls

1. **pdb under pytest-xdist silently does nothing.** Always use `-p no:xdist` or `-n 0`.
2. **`breakpoint()` in CI / non-TTY contexts hangs the process.** Never commit it.
3. **`PYTHONBREAKPOINT=0`** disables all `breakpoint()` calls. Check the env if your breakpoint isn't hitting.
4. **Attach to PID fails on hardened kernels.** `ptrace_scope=1` (Ubuntu default). Workaround: `echo 0 > /proc/sys/kernel/yama/ptrace_scope`.
5. **Threads.** `pdb` only debugs the current thread. For multithreaded code, use `debugpy`.
6. **Forking / multiprocessing.** pdb does not follow forks. Each child needs its own `breakpoint()`.

---

## Part 3: Node.js Debugging (--inspect + CDP)

When `console.log` isn't enough, drive Node's built-in V8 inspector programmatically from the terminal.

Two tools, pick one:
- **`node inspect`** — built-in, zero install, CLI REPL. Best for quick poking.
- **`ndb` / CDP via `chrome-remote-interface`** — scriptable from Node/Python; best when you want to automate many breakpoints.

**Prefer `node inspect` first.** It's always available and the REPL is fast.

### When to Use

- A Node test fails and you need to see intermediate state
- ui-tui crashes or behaves wrong and you want to inspect React/Ink state pre-render
- tui_gateway child processes misbehave
- You need to inspect a value in a closure that `console.log` can't reach

**Don't use for:** things `console.log` solves in under a minute.

### Quick Reference: `node inspect` REPL

```bash
node inspect path/to/script.js
# or with tsx
node --inspect-brk $(which tsx) path/to/script.ts
```

| Command | Action |
|---|---|
| `c` / `cont` | continue |
| `n` / `next` | step over |
| `s` / `step` | step into |
| `o` / `out` | step out |
| `pause` | pause running code |
| `sb('file.js', 42)` | set breakpoint at file.js line 42 |
| `sb('functionName')` | break when function is called |
| `cb('file.js', 42)` | clear breakpoint |
| `bt` | backtrace (call stack) |
| `list(5)` | show 5 lines of source around current position |
| `repl` | drop into REPL in current scope |
| `exec expr` | evaluate expression once |
| `restart` | restart script |

### Attaching to a Running Process

```bash
# 1. Send SIGUSR1 to enable the inspector
kill -SIGUSR1 <pid>

# 2. Attach the debugger CLI
node inspect -p <pid>
```

To start with the inspector from the beginning:
```bash
node --inspect script.js           # listen, keep running
node --inspect-brk script.js       # listen AND pause on first line
```

### Programmatic CDP (scripting from terminal)

When you want to automate — set many breakpoints, capture scope state:
```bash
npm i -g chrome-remote-interface
node --inspect-brk=9229 target.js &
```

Driver script:
```javascript
const CDP = require('chrome-remote-interface');
(async () => {
  const client = await CDP({ port: 9229 });
  const { Debugger, Runtime } = client;

  Debugger.paused(async ({ callFrames }) => {
    const top = callFrames[0];
    console.log(`PAUSED @ ${top.url}:${top.location.lineNumber + 1}`);

    // Walk scopes for locals
    for (const scope of top.scopeChain) {
      if (scope.type === 'local' || scope.type === 'closure') {
        const { result } = await Runtime.getProperties({
          objectId: scope.object.objectId,
          ownProperties: true,
        });
        for (const p of result) {
          console.log(`  ${scope.type}.${p.name} =`, p.value?.value);
        }
      }
    }
    await Debugger.resume();
  });

  await Debugger.enable();
  await Runtime.enable();
  await Debugger.setBreakpointByUrl({
    urlRegex: '.*app\\.tsx$',
    lineNumber: 119,
  });
  await Runtime.runIfWaitingForDebugger();
})();
```

### Node.js Debugging Pitfalls

1. **Wrong line numbers in TS source.** Breakpoints hit the emitted JS, not the `.ts`. Use `node --enable-source-maps` or break in `dist/*.js`.
2. **`--inspect` vs `--inspect-brk`.** `--inspect` starts the inspector but doesn't pause. Use `--inspect-brk` when you need to set breakpoints before any code runs.
3. **Port collisions.** Default is `9229`. Use `--inspect=0` for random port and read from `/json/list`.
4. **Child processes.** `--inspect` on a parent does NOT inspect its children. Use `NODE_OPTIONS='--inspect-brk'` to propagate.
5. **Background kills.** If you `Ctrl+C` out of `node inspect` while the target is paused, the target stays paused. `cont` first, or `kill` explicitly.
6. **Security.** `--inspect=0.0.0.0:9229` exposes arbitrary code execution. Always bind to `127.0.0.1`.

### Debugging Hermes ui-tui

The TUI is built Ink + tsx:

```bash
cd ~/hermes-agent/ui-tui
npm run build
node --inspect-brk dist/entry.js
# In another terminal:
node inspect -p <node pid>
```

Then inside `debug>`: `sb('dist/app.js', 220)`, `cont`. When it pauses, `repl` → inspect `props`, state refs, etc.

For a running `hermes --tui`:
```bash
TUI_PID=$(pgrep -f 'ui-tui/dist/entry' | head -1)
kill -SIGUSR1 "$TUI_PID"
curl -s http://127.0.0.1:9229/json/list | jq -r '.[0].webSocketDebuggerUrl'
node inspect ws://127.0.0.1:9229/<uuid>
```

---

## Verification Checklist (All Languages)

After setting up a debug session, verify:

- [ ] The debug port is actually listening
- [ ] First breakpoint actually hits
- [ ] Source listing at pause shows the right file
- [ ] Post-debug cleanup: no stray `breakpoint()` / `set_trace()` in committed code
  ```bash
  rg -n 'breakpoint\(\)|set_trace\(|debugpy\.listen' --type py
  ```
