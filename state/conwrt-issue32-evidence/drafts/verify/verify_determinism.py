#!/usr/bin/env python3
import json, subprocess
from pathlib import Path
tmpd = Path(open("/dev/shm/regen-path.txt").read().split("=", 1)[1].strip())
p1, p2 = tmpd / "regen-bundle.json", tmpd / "regen2.json"
if not p2.exists():
    print("regen2.json not present; run generator twice first")
else:
    a = json.loads(p1.read_text()); b = json.loads(p2.read_text())
    a.pop("generated_at", None); b.pop("generated_at", None)
    print("two regen runs identical (modulo generated_at):",
          json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True))
