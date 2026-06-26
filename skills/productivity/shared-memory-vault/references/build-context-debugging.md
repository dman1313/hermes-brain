# build-context.sh Debugging & Recovery

## Failure Mode Summary

There are two independent failure modes in `~/agent-memory/build-context.sh`:

### 1. xargs Quoting Bug (THE MOST DESTRUCTIVE)

**Symptom:** `bash build-context.sh` produces no visible output (exit 0) or only "xargs: unmatched single quote" errors. NOW.md never regenerates. ACTIVITY.md entries accumulate but parsed.tsv stays empty.

**Root cause:** GNU xargs treats `'` as a quoting delimiter. When any parsed ACTIVITY.md entry's detail field contains a contraction (e.g., `Dwayne's`, `can't`, `doesn't`), xargs on lines 119-122 of build-context.sh exits 1 with "unmatched single quote" and returns empty string. The resulting empty `$agent` or `$event` variable triggers `return 1` on line 123, silently skipping that entry. Over hundreds of entries — virtually all of which contain contractions — zero entries ever make it to parsed.tsv.

**Detection:**
```bash
cd ~/agent-memory
# Run with debug output to see the parse failures
bash -x build-context.sh 2>&1 | head -40
# Check if parsed.tsv is empty
timeout 10 bash -c '
PARSEDFILE=/tmp/test_parsed.tsv
> "$PARSEDFILE"
in_entries=false
while IFS= read -r line || [ -n "$line" ]; do
    if [ "$line" = "<!-- ENTRIES BELOW THIS LINE -->" ]; then
        in_entries=true; continue
    fi
    if ! $in_entries; then continue; fi
    [[ -z "$line" ]] && continue
    ts=$(echo "$line" | grep -oP "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z")
    [ -z "$ts" ] && continue
    echo "$ts" >> "$PARSEDFILE"
done < ACTIVITY.md
echo "Parsed $(wc -l < "$PARSEDFILE") lines"
'
# If parsed.tsv is 0 lines, the xargs bug is active
```

**Fix:**
Replace `xargs` (which has quote-special behavior) with `sed` for whitespace trimming:

```bash
# In parse_activity_line() — change from:
agent=$(echo "${BASH_REMATCH[2]}" | xargs)
# To:
agent=$(echo "${BASH_REMATCH[2]}" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
```

Do this for all four fields (agent, event, project, detail). Also check `fm_get()` function (~line 418) which may have `2>/dev/null` masking the same xargs failure.

### 2. Overall Script Timeout

**Symptom:** xargs quoting is fixed but `timeout 120 bash build-context.sh` still exits 124. NOW.md not regenerated.

**Root cause:** The awk/sort/filter pipeline on 200+ parsed entries exceeds 120s. Pre-existing performance issue with no recent trigger — it has been timing out consistently since mid-June.

**Workaround:** Skip `bash build-context.sh` for routine 1-2 entry updates (the skill's threshold of "run after 5+ entries" already accounts for this). For full regeneration, either:
- Run without the outer `timeout` wrapper and let it complete naturally
- Break the script into stages (parse only → NOW.md write → CONTEXT.md write)
- Increase the timeout

## Vault Commit Failure Mode

**Symptom:** HAL daily brief crons produce full substantive output (health metrics, DREAM/Wolf review) but the final `git add -A && git commit && git push` never completes. ACTIVITY.md has no entries for that day. Other agents see a stale vault.

**Detected:** Jun 26 HAL brief identified 4 consecutive days (Jun 22-25) where this happened. The build-context.sh xargs quoting bug (above) is the most likely root cause — if NOW.md doesn't regenerate despite entries existing, the `bash build-context.sh` step in the session closeout waits 120s and times out, which prevents the git commit step from executing.

**Fix:** Fix the xargs quoting bug first. If the commit still fails after that, check git auth: `git pull --rebase --autostash` should work silently. If it prompts for credentials, the remote URL may need a PAT embedded.
