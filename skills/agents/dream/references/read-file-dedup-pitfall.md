# read_file Deduplication in execute_code — Error Reference

## Error Signature
```
KeyError: 'content'
```
When accessing `result['content']` from a `read_file()` call inside `execute_code`.

## Root Cause
The `hermes_tools.read_file()` function returns a dict with these keys:
- `status` — "unchanged" or similar
- `message` — "File unchanged since last read..."  
- `path` — the file path
- `dedup` — `True` when deduplicated
- `content_returned` — **boolean**, NOT the file content

When the file has already been read earlier in the conversation, the function returns `content_returned: False` and the actual content is omitted. The previous `read_file` call's content is available in the conversation context (tool output), but not accessible programmatically from within `execute_code`.

## Observed Failures

### May 29 DREAM Cron (3 errors)
```
[2026-05-29 03:04:36] execute_code returned error:
  File "/tmp/hermes_sandbox_ioii5wj9/script.py", line 7, in <module>
    data = json.loads(result['content'].split...)
KeyError: 'content'
```

### May 29 DREAM Manual Run (2 errors)
Same pattern — called `read_file` on `jobs.json` which had been read earlier in the conversation. Got `KeyError: 'content'` twice before switching to `terminal` with heredoc.

## Working Pattern
```python
# CORRECT: Use terminal with heredoc for file reading in execute_code
import json
from hermes_tools import terminal
r = terminal("python3 << 'PYEOF'\nimport json\nwith open('/path/to/file.json') as f:\n    data = json.load(f)\nprint(json.dumps(data, indent=2))\nPYEOF")
data = json.loads(r['output'])
```

```python
# WRONG: Using read_file and accessing result['content']
from hermes_tools import read_file
r = read_file('/path/to/file.json')
data = json.loads(r['content'])  # KeyError: 'content'
```

## Why Terminal + Heredoc Works
`terminal()` executes in a fresh shell each time — no deduplication, no caching. The heredoc (`<< 'PYEOF'`) avoids pipe-to-interpreter security blocks. This is the most reliable pattern for reading files from `execute_code`.
