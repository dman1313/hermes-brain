#!/usr/bin/env python3
"""Approve a pending OpenClaw Gateway device pairing request.

Usage:
  python3 approve-device.py [--request-id ID] [--list]

If --request-id is given, approve that specific request.
If --list is given, just list pending devices.
If neither, approve the most recent pending device.

Requires: websockets (pip install websockets)
"""
import json, asyncio, argparse, os, sys
import websockets

TOKEN = os.environ.get("OPENCLAW_GATEWAY_TOKEN") or ""
URI = os.environ.get("OPENCLAW_GATEWAY_URL", "ws://127.0.0.1:18789")


async def connect(ws):
    """Perform the connect handshake. Returns True on success."""
    await ws.send(json.dumps({
        "type": "req", "id": "c1", "method": "connect",
        "params": {
            "role": "operator", "auth": {"token": TOKEN},
            "client": {"id": "gateway-client", "platform": "linux", "mode": "backend", "version": "1.0.0"},
            "minProtocol": 3, "maxProtocol": 3,
            "scopes": ["operator", "operator.admin"]
        }
    }))
    for _ in range(5):
        resp = await asyncio.wait_for(ws.recv(), timeout=5)
        r = json.loads(resp)
        if r.get("ok"):
            # Drain health event
            try: await asyncio.wait_for(ws.recv(), timeout=2)
            except: pass
            return True
        if r.get("ok") is False:
            print(f"Connect failed: {r.get('error', {}).get('message', resp[:200])}")
            return False
    return False


async def list_pending(ws):
    """List pending device pairings."""
    await ws.send(json.dumps({"type": "req", "id": "l1", "method": "device.pair.list", "params": {}}))
    resp = await asyncio.wait_for(ws.recv(), timeout=5)
    r = json.loads(resp)
    if r.get("ok"):
        pending = r.get("payload", {}).get("pending", [])
        if not pending:
            print("No pending devices.")
            return None
        for dev in pending:
            print(f"  Device: {dev.get('displayName')} ({dev.get('platform')})")
            print(f"  RequestID: {dev.get('requestId')}")
            print(f"  IP: {dev.get('remoteIp')}")
            print(f"  Client: {dev.get('clientId')} v{dev.get('clientMode')}")
            print()
        return pending
    else:
        print(f"List failed: {r}")
        return None


async def approve(ws, request_id):
    """Approve a device pairing request."""
    await ws.send(json.dumps({
        "type": "req", "id": "a1", "method": "device.pair.approve",
        "params": {"requestId": request_id}
    }))
    resp = await asyncio.wait_for(ws.recv(), timeout=5)
    r = json.loads(resp)
    if r.get("ok") or (r.get("event") == "device.pair.resolved" and r.get("payload", {}).get("decision") == "approved"):
        print(f"✅ Approved: {request_id}")
        return True
    else:
        print(f"Approve failed: {resp[:300]}")
        return False


async def main():
    parser = argparse.ArgumentParser(description="Approve OpenClaw Gateway device pairings")
    parser.add_argument("--list", action="store_true", help="List pending devices only")
    parser.add_argument("--request-id", help="Approve a specific request ID")
    parser.add_argument("--token", help="Gateway auth token (or set OPENCLAW_GATEWAY_TOKEN)")
    parser.add_argument("--url", default=URI, help="Gateway WebSocket URL")
    args = parser.parse_args()

    global TOKEN
    if args.token:
        TOKEN = args.token
    if not TOKEN:
        # Try reading from config
        config_path = os.path.expanduser("~/.openclaw/openclaw.json")
        if os.path.exists(config_path):
            with open(config_path) as f:
                d = json.load(f)
                TOKEN = d.get("gateway", {}).get("auth", {}).get("token", "")
    if not TOKEN:
        print("Error: No token. Set OPENCLAW_GATEWAY_TOKEN or use --token")
        sys.exit(1)

    async with websockets.connect(args.url, additional_headers={"Authorization": f"Bearer {TOKEN}"}) as ws:
        if not await connect(ws):
            sys.exit(1)

        pending = await list_pending(ws)
        if args.list:
            return

        if not pending:
            print("No devices to approve.")
            return

        if args.request_id:
            await approve(ws, args.request_id)
        elif pending:
            # Approve the most recent
            rid = pending[0]["requestId"]
            print(f"Approving most recent: {rid}")
            await approve(ws, rid)


if __name__ == "__main__":
    asyncio.run(main())
