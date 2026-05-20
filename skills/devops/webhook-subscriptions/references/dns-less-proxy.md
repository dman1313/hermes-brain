# DNS-Less Webhook Exposure via App Proxy

When you can't add a DNS record for the webhook subdomain (stale `cloudflared` cert, no API token, manual DNS unavailable), proxy webhook traffic through an existing web app on a working subdomain.

## Pattern

Add a catch-all route to an existing Flask/Express/nginx app that forwards matching requests to the webhook server:

```python
# Flask example — add to existing app
import requests

@app.route("/webhooks/<path:subpath>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def webhook_proxy(subpath):
    WEBHOOK_BACKEND = "http://127.0.0.1:8644"
    target_url = f"{WEBHOOK_BACKEND}/webhooks/{subpath}"
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
```

## When to use

- `cloudflared tunnel route dns` fails with "missing token in the certificate"
- No Cloudflare API token available
- DNS changes require manual dashboard access
- Need webhooks working immediately without waiting for DNS propagation

## Example from this session

Linear webhook at `https://hermesdash.humangood.ai/webhooks/linear` proxies through the hermesdash Flask dashboard (:9999) → Hermes webhook server (:8644). No separate `webhook.humangood.ai` DNS record needed.
