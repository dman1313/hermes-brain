---
name: npm-dependency-troubleshooting
description: Fix npm warnings, engine mismatches, deprecated transitive deps, and dependency conflicts. Covers version pinning, overrides, resolutions, and lockfile surgery.
triggers:
  - npm warn EBADENGINE
  - npm warn deprecated
  - npm ERR! peer dep
  - npm ERR! ERESOLVE
  - engine compatibility
  - deprecated package
  - transitive dependency warning
  - npm overrides
---

# npm Dependency Troubleshooting

Fix common npm dependency warnings and errors without blindly ignoring them.

## Quick Diagnosis

```bash
# See full dependency tree for a package
npm ls <package-name>

# Check what engines a specific version requires
npm view <pkg>@<version> engines --json

# Check what depends on a deprecated package
npm ls <deprecated-package>

# See all available versions
npm view <pkg> versions --json
```

## Fix 1: EBADENGINE — Package Requires Newer Node

**Signal:** `npm warn EBADENGINE Unsupported engine { package: 'X@version', required: { node: '>=24' }, current: { node: 'v22...' } }`

**Root cause:** A dependency bumped its `engines.node` requirement beyond your installed Node version.

**Fix:** Find the last version that supports your Node, then pin it (remove `^` prefix):

```bash
# Check which version introduced the engine requirement
for v in 13.11.1 13.11.2 13.12.0; do
  echo -n "$v: "
  npm view <pkg>@$v engines --json 2>/dev/null || echo "none"
done
```

Then in `package.json`:
```jsonc
// Before (resolves to latest, which requires Node 24)
"@icons-pack/react-simple-icons": "^13.13.0"

// After (pinned to last compatible version)
"@icons-pack/react-simple-icons": "13.11.1"
```

**Pitfall:** Don't use `^` with the pinned version — that allows npm to upgrade past it again. Use an exact version or a range that excludes the breaking version.

## Fix 2: Deprecated Transitive Dependencies

**Signal:** `npm warn deprecated <package>@<version>: This proposal has been merged...`

**Root cause:** A transitive dependency (not yours directly) uses a deprecated package. The parent hasn't updated yet.

**Fix:** Add an `overrides` section in the **root** `package.json` (the one with `node_modules`):

```json
{
  "overrides": {
    "@babel/plugin-proposal-private-methods": "npm:@babel/plugin-transform-private-methods@^7.27.1"
  }
}
```

The `npm:` protocol redirects the deprecated package name to its replacement. This works because Babel proposal plugins that were merged into the ECMAScript standard get renamed from `proposal-*` to `transform-*` with identical APIs.

**Common babel proposal → transform redirects:**
- `@babel/plugin-proposal-private-methods` → `@babel/plugin-transform-private-methods`
- `@babel/plugin-proposal-class-properties` → `@babel/plugin-transform-class-properties`
- `@babel/plugin-proposal-optional-chaining` → `@babel/plugin-transform-optional-chaining`

**Pitfall:** The `overrides` field only works in the root package.json (the one you run `npm install` from). In a monorepo, it must be in the workspace root.

## Fix 3: Peer Dependency Conflicts (ERESOLVE)

```bash
# Nuclear option — install ignoring peer deps
npm install --legacy-peer-deps

# Better — check what's conflicting first
npm ls <package> --all
```

Use `--legacy-peer-deps` sparingly. It suppresses the conflict rather than resolving it.

## Workflow

1. Identify which package is causing the warning
2. `npm ls <package>` to find the dependency chain
3. `npm view <pkg>@<version> engines` to find the last compatible version
4. Apply the appropriate fix (pin version, add override, or update parent)
5. `npm install` and verify warnings are gone
6. Check `git diff` to confirm only the expected changes in lockfile
