# Webhook Proxy via Existing Subdomain

When you can't add a new DNS record (stale cloudflared cert, no API token), piggyback on an existing working subdomain with a Flask reverse-proxy route.

## When to Use

- Cloudflared cert.pem is stale and `cloudflared tunnel route dns` fails with "missing token"
- No Cloudflare API token available
- Need webhooks live NOW without manual DNS configuration

## Pattern

Add a catch-all proxy route to an existing Flask app that's already served through Cloudflare:

```python
@app.route("/webhooks/<path:subpath>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def webhook_proxy(subpath):
    """Proxy webhook requests to the local webhook server."""
    WEBHOOK_BACKEND = "http://127.0.0.1:8644"
    target_url = f"{WEBHOOK_BACKEND}/webhooks/{subpath}"
    try:
        r = requests.request(
            method=request.method,
            url=target_url,
            headers={k: v for k, v in request.headers if k.lower() != "host"},
            data=request.get_data(),
            timeout=30,
            allow_redirects=False,
        )
        return Response(r.content, status=r.status_code,
                        content_type=r.headers.get("Content-Type", "application/json"))
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "webhook server not reachable"}), 502
```

Then the webhook URL becomes `https://<existing-subdomain>/webhooks/<name>` instead of `https://<new-subdomain>/webhooks/<name>`.

## Gotchas

- Flask app may be root-owned — use `sudo tee -a` for writes
- Restart the service after adding the route
- Test with a POST without HMAC signature — expect "Invalid signature", not 502
