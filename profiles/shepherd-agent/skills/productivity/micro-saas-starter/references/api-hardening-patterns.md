# API Hardening Patterns

Mandatory patterns for any public-facing API endpoint in Dwayne's micro-SaaS projects.

## 1. Rate Limiting

Use `ratelimit.py` — in-memory sliding window, zero dependencies:

```python
# ratelimit.py
class RateLimiter:
    def __init__(self, max_requests=10, window_seconds=60):
        self.max_requests = max_requests
        self.window = window_seconds
        self._buckets: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, key: str) -> bool:
        now = time.time()
        bucket = self._buckets[key]
        cutoff = now - self.window
        while bucket and bucket[0] < cutoff:
            bucket.pop(0)
        if len(bucket) >= self.max_requests:
            return False
        bucket.append(now)
        return True
```

Integrate in route:
```python
client_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
if not limiter.is_allowed(client_ip):
    return jsonify({"error": "Rate limit exceeded", "retry_after_seconds": 60}), 429
```

## 2. SSRF Protection

The scanner makes outbound HTTP requests to user-supplied URLs. Block internal addresses:

```python
def _is_private_url(url: str) -> bool:
    import socket
    from urllib.parse import urlparse
    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    lower = hostname.lower()
    # Block known private hostnames
    if lower in ("localhost", "127.0.0.1", "0.0.0.0", "[::1]"):
        return True
    if lower.endswith(".local") or lower.endswith(".internal"):
        return True
    # Resolve and check IP ranges
    try:
        addrs = socket.getaddrinfo(hostname, 80, family=socket.AF_INET)
        for _, _, _, _, sockaddr in addrs:
            ip = ipaddress.ip_address(sockaddr[0])
            if ip.is_private or ip.is_loopback or ip.is_link_local:
                return True
    except socket.gaierror:
        return False
    return False
```

## 3. CORS for Cross-Origin Embeds

Badge.js needs `Access-Control-Allow-Origin: *` and OPTIONS preflight:

```python
@app.route("/api/certify", methods=["GET", "OPTIONS"])
def api_certify():
    if request.method == "OPTIONS":
        return _cors(Response(""), 204)
    # ... normal logic ...

def _cors(response, status=200):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.status_code = status
    return response
```

## 4. Error Handling

Never let the scanner crash the route. Wrap in try/except:

```python
try:
    report = certify_url(target)
except ValueError as e:
    return jsonify({"error": str(e)}), 400
except Exception:
    return jsonify({"error": "Certification failed — please check the URL"}), 502
```

Don't leak `str(e)` for generic exceptions — attackers can probe internal state.

## 5. URL Validation

```python
target = target.strip()
if not (target.startswith("http://") or target.startswith("https://")):
    target = "https://" + target
if len(target) > 2000:
    return jsonify({"error": "URL too long"}), 400
```

## 6. Security Headers

Set on every response via `@app.after_request`:

```python
response.headers["X-Content-Type-Options"] = "nosniff"
response.headers["X-Frame-Options"] = "DENY"
response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
```
