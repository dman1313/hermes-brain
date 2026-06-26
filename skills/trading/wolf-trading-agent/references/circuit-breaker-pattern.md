# Circuit Breaker Pattern for Data Source Scanners

When scanning external data sources that can fail (rate limits, blocks, timeouts), use a simple consecutive-failure circuit breaker to prevent the entire scan from hanging.

## Pattern

```python
consecutive_failures = 0
MAX_FAILURES = 3  # abort after this many consecutive failures

for query in queries:
    try:
        result = fetch(query)
        consecutive_failures = 0  # reset on success
        process(result)
    except Exception as e:
        consecutive_failures += 1
        if consecutive_failures >= MAX_FAILURES:
            print(f"  [source] {MAX_FAILURES} consecutive failures — aborting")
            break
        time.sleep(REQUEST_DELAY)
```

## Why Not Signal Alarms

Python's `signal.alarm()` approach is fragile across function boundaries. If a signal timer is set in function A but function B runs before it fires, the SIGALRM will fire in B's context instead — crashing B instead of timing out A. **Use per-request `timeout=N` in urllib calls instead.**

## When to Apply

- **DuckDuckGo**: Known to time out or return empty results after rate limits
- **RSS feeds**: Subreddit feeds other than WSB return 429 quickly
- **Any third-party API**: Treat every external call as potentially blocking

## Per-Request Timeout

```python
with urllib.request.urlopen(req, timeout=8) as resp:
    data = resp.read()
```

8 seconds is generous enough for most APIs but tight enough to not hang the whole scan. Reduce to 5s for quicker failure detection in fast-paced scans.
