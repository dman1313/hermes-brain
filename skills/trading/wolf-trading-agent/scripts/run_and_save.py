#!/usr/bin/env python3
import json, os, sys
from datetime import datetime

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)
from wolf_scan import run_full_scan

result = run_full_scan(verbose=False)
output = {"metadata": result["metadata"], "signals": result["signals"]}
date_str = datetime.now().strftime("%Y-%m-%d")
out_path = os.path.join(SCRIPTS_DIR, "..", "output", f"wolf_enhanced_{date_str}.json")
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, "w") as f:
    json.dump(output, f, indent=2, default=str)
print(f"Saved: {out_path}")
print(f"Signals: {len(result['signals'])}")
for s in result['signals']:
    print(f"  {s['ticker']}: score={s['score']}, tier={s['tier']}, mentions={s['mentions']}")
