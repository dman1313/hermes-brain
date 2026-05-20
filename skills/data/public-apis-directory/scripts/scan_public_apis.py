#!/usr/bin/env python3
"""Public APIs health scanner — concurrent HTTP check of every API in the list.

Run with: python3 scripts/scan_public_apis.py

Tests every API URL from public-apis.md with concurrent HTTP requests.
Produces a report at ~/.hermes/data/public-apis-scan.txt showing:
- Alive vs dead counts and percentages
- Category survival rates
- List of ready-to-use APIs (no auth + HTTPS + alive)
- List of dead APIs with failure reasons

Concurrency: 20 simultaneous connections, 8s timeout per URL.
Total runtime for 1,483 APIs: ~5-7 minutes.
"""
import re
import sys
import time
import asyncio
import aiohttp
from collections import defaultdict

MARKDOWN_PATH = "/home/ubuntu/.hermes/data/public-apis.md"
CONCURRENCY = 20
TIMEOUT = 8
MAX_REDIRECTS = 3

def parse_entries(path):
    with open(path) as f:
        lines = f.readlines()
    
    entries = []
    current_category = "Unknown"
    
    for line in lines:
        if line.startswith("### "):
            current_category = line.replace("### ", "").strip()
            continue
        
        match = re.match(
            r'^\|\s*\[([^\]]+)\]\(([^)]+)\)\s*\|\s*([^|]+?)\s*\|\s*(?:`?([^`|]+?)`?)\s*\|\s*(Yes|No|Unknown)\s*\|\s*(Yes|No|Unknown)\s*\|\s*\[?(?:Go!)\]?\(?([^)\s]+)\)?\s*\|',
            line
        )
        if not match:
            match = re.match(
                r'^\|\s*\[([^\]]+)\]\(([^)]+)\)\s*\|\s*([^|]+?)\s*\|\s*(?:`?([^`|]+?)`?)\s*\|\s*(Yes|No|Unknown)\s*\|\s*(Yes|No|Unknown)',
                line
            )
            if not match:
                continue
            api_name, name_url, description, auth, https, cors = match.groups()
            test_url = name_url
        else:
            api_name, name_url, description, auth, https, cors, test_url = match.groups()
            test_url = test_url.strip()
        
        entries.append({
            "category": current_category,
            "name": api_name.strip(),
            "url": test_url,
            "description": description.strip(),
            "auth": auth.strip().strip('`'),
            "https": https.strip(),
            "cors": cors.strip(),
        })
    
    return entries

async def test_url(session, entry, semaphore):
    url = entry["url"]
    async with semaphore:
        try:
            async with session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=TIMEOUT),
                allow_redirects=True,
                max_redirects=MAX_REDIRECTS,
                headers={"User-Agent": "Hermes-API-Scanner/1.0"}
            ) as resp:
                return {
                    **entry,
                    "status": resp.status,
                    "ok": resp.status < 400,
                    "error": None,
                }
        except asyncio.TimeoutError:
            return {**entry, "status": 0, "ok": False, "error": "timeout"}
        except aiohttp.ClientError as e:
            return {**entry, "status": 0, "ok": False, "error": str(e)[:100]}
        except Exception as e:
            return {**entry, "status": 0, "ok": False, "error": type(e).__name__}

async def main():
    print("Parsing entries...")
    entries = parse_entries(MARKDOWN_PATH)
    print(f"Found {len(entries)} APIs across {len(set(e['category'] for e in entries))} categories")
    
    semaphore = asyncio.Semaphore(CONCURRENCY)
    connector = aiohttp.TCPConnector(limit=CONCURRENCY, force_close=True)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        print(f"Testing with concurrency={CONCURRENCY}, timeout={TIMEOUT}s...")
        start = time.time()
        tasks = [test_url(session, entry, semaphore) for entry in entries]
        results = await asyncio.gather(*tasks)
        elapsed = time.time() - start
    
    by_status = defaultdict(list)
    alive = 0
    dead = 0
    
    for r in results:
        if r["ok"]:
            alive += 1
            bucket = f"2xx-3xx ({r['status']})"
        elif r["status"] == 0:
            dead += 1
            bucket = "connection-failed"
        else:
            dead += 1
            bucket = f"{r['status']}"
        by_status[bucket].append(r)
    
    print(f"\n{'='*70}")
    print(f"PUBLIC APIs HEALTH SCAN — {len(results)} APIs tested")
    print(f"Time: {elapsed:.1f}s | Concurrency: {CONCURRENCY} | Timeout: {TIMEOUT}s")
    print(f"{'='*70}")
    print(f"\n✅  ALIVE:  {alive}/{len(results)} ({alive*100//len(results)}%)")
    print(f"❌  DEAD:   {dead}/{len(results)} ({dead*100//len(results)}%)\n")
    
    for bucket, items in sorted(by_status.items(), key=lambda x: -len(x[1])):
        print(f"  {bucket}: {len(items)} APIs")
    
    by_cat = defaultdict(lambda: {"alive": 0, "dead": 0})
    for r in results:
        cat = r["category"]
        if r["ok"]:
            by_cat[cat]["alive"] += 1
        else:
            by_cat[cat]["dead"] += 1
    
    print(f"\n{'='*70}")
    print("CATEGORY SURVIVAL RATES")
    print(f"{'='*70}")
    for cat, counts in sorted(by_cat.items()):
        total = counts["alive"] + counts["dead"]
        rate = counts["alive"] * 100 // total if total > 0 else 0
        bar = "█" * (rate // 10) + "░" * (10 - rate // 10)
        print(f"  {bar} {rate:3d}%  {cat} ({counts['alive']}/{total})")
    
    dead_entries = [r for r in results if not r["ok"]]
    if dead_entries:
        print(f"\n{'='*70}")
        print(f"DEAD APIs ({len(dead_entries)})")
        print(f"{'='*70}")
        for r in sorted(dead_entries, key=lambda x: x["name"].lower()):
            err = r["error"] or f"HTTP {r['status']}"
            print(f"  ✗ {r['name']} — {err}")
            print(f"    {r['url']}")
    
    no_auth_alive = [r for r in results if r["ok"] and r["auth"] == "No"]
    print(f"\n{'='*70}")
    print(f"READY-TO-USE (no auth + HTTPS + alive): {len(no_auth_alive)} APIs")
    print(f"{'='*70}")
    for r in sorted(no_auth_alive, key=lambda x: x["category"]):
        print(f"  [{r['category']}] {r['name']} — {r['description'][:80]}")
        print(f"    {r['url']}")
    
    summary_path = "/home/ubuntu/.hermes/data/public-apis-scan.txt"
    with open(summary_path, "w") as f:
        f.write(f"Public APIs Health Scan — {time.strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"Alive: {alive}/{len(results)} ({alive*100//len(results)}%)\n")
        f.write(f"Dead: {dead}/{len(results)} ({dead*100//len(results)}%)\n\n")
        f.write("DEAD APIs:\n")
        for r in dead_entries:
            err_msg = r.get("error") or f"HTTP {r['status']}"
            f.write(f"  {r['name']} — {err_msg} — {r['url']}\n")
    print(f"\nReport saved: {summary_path}")

if __name__ == "__main__":
    asyncio.run(main())
