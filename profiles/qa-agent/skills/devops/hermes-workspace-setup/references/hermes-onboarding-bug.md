# HermesOnboarding Missing Component Bug

**Date encountered:** 2026-05-03
**Workspace version:** cloned May 2 2026 from `outsourc-e/hermes-workspace`

## Error

```
Can't find variable: HermesOnboarding
```

This is a JavaScript runtime error in the browser — the page loads but React crashes when it hits the undefined component reference.

## Root Cause

In `src/routes/__root.tsx` at line 355:

```tsx
{mounted && rootSurfaceState.showOnboarding ? <HermesOnboarding /> : null}
```

The `<HermesOnboarding />` JSX tag references a component that is:
- **Not imported** anywhere in the file (checked all imports lines 1-30)
- **Not defined** anywhere in the codebase (`search_files` for `function HermesOnboarding`, `const HermesOnboarding`, or `export.*HermesOnboarding` returned zero results across all .ts/.tsx/.js/.jsx files)

## Fix

Comment out the broken line:

```tsx
{/* HermesOnboarding not yet defined — see hermes-workspace-setup pitfall 6 */}
{false && rootSurfaceState.showOnboarding ? null : null}
```

Or more simply:

```tsx
{/* {mounted && rootSurfaceState.showOnboarding ? <HermesOnboarding /> : null} */}
```

Vite dev server hot-reloads the fix — no restart needed. Verify with `curl -s -o /dev/null -w "%{http_code}" http://localhost:3000` → should return 200.

## Why This Happens

The `showOnboarding` state in `rootSurfaceState` is part of the workspace shell flow (handles login → onboarding → main shell transitions). The onboarding component was scaffolded into `__root.tsx` but the actual component file was never committed. This is likely an in-progress feature that shipped to main prematurely.

## Detection

If you encounter this in a new clone, search first:
```bash
grep -rn "HermesOnboarding" ~/hermes-workspace/src/
```

If only `__root.tsx` matches (one result), the component is missing and needs the fix above.
