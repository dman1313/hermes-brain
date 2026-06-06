# Cron Script Path Resolution — Pitfall Reference

## The Problem

Hermes prepends `~/.hermes/scripts/` to whatever is in the `--script` field of a cron job. This means:

- `--script "pipeline.sh"` → resolves to `~/.hermes/scripts/pipeline.sh` ✅
- `--script "bash ~/study-packages/pipeline.sh"` → resolves to `~/.hermes/scripts/bash ~/study-packages/pipeline.sh` ❌
- `--script "/home/ubuntu/study-packages/pipeline.sh"` → resolves to `~/.hermes/scripts//home/ubuntu/study-packages/pipeline.sh` ❌

The error message is: `Script not found: /home/ubuntu/.hermes/scripts/bash ~/path/to/script.sh`

## The Fix

1. **Copy** the script into `~/.hermes/scripts/`:
   ```bash
   cp ~/path/to/original/script.sh ~/.hermes/scripts/my-script.sh
   ```

2. **Symlinks don't work** — Hermes rejects them with: `"Script path escapes the scripts directory via traversal: 'my-script.sh'"`. The traversal check follows symlinks and rejects anything pointing outside `~/.hermes/scripts/`.

3. Reference by filename only:
   ```bash
   hermes cron edit JOB_ID --script "my-script.sh"
   ```

## Audit Signal

When scanning cron job output for cleanup opportunities, grep for `Script not found:` in the last_run error messages. These are always broken path references that need the copy-and-fix pattern above.

## Example Real-World Fix

**Broken cron config:**
```
Script: bash ~/study-packages/e1717d74-04f8-4d1d-b626-c1e18df2cc4a/concept-pipeline.sh
Last run: error: Script not found: /home/ubuntu/.hermes/scripts/bash ~/study-packages/...
```

**Fixed:**
```bash
cp ~/study-packages/e1717d74-04f8-4d1d-b626-c1e18df2cc4a/concept-pipeline.sh ~/.hermes/scripts/chemistry-pipeline.sh
hermes cron edit JOB_ID --script "chemistry-pipeline.sh"
```

**Result:** Script now resolves to `~/.hermes/scripts/chemistry-pipeline.sh` and runs successfully.

## Also Check

- Delivery target validity — if the chat ID is wrong (e.g. "Chat not found"), the script runs but output goes nowhere. Fix `--deliver` to a valid target.
- Scripts that reference relative paths internally may need `--workdir` set to their original directory.
