#!/usr/bin/env python3
"""Compare the three bundle shas: committed(pr-55), origin/master, upstream master."""
import json, re, hashlib
from pathlib import Path

files = {
    "committed(pr-55 HEAD)": Path.home() / "repos" / "conwrt" / "docs" / "wizard-bundle.json",
    "origin/master": Path("/dev/shm/origin-master-bundle.json"),
    "upstream amperstrand/master": Path("/dev/shm/upstream-master-bundle.json"),
}
lit_re = re.compile(r"uci set network\.lan\.ipaddr='([^']*)'")

for label, p in files.items():
    raw = p.read_bytes()
    try:
        b = json.loads(raw)
    except Exception as e:
        print(f"{label:28s} sha={hashlib.sha256(raw).hexdigest()[:16]} PARSE FAIL {e}")
        continue
    n = g = lit = rb = 0
    ver_vals = set()
    for m in b["models"]:
        ver_vals.add(m.get("version"))
    for mid, flows in b["rendered"].items():
        for fn, vers in flows.items():
            for v, c in vers.items():
                n += 1
                sh = c.get("shell", "")
                if "LAN_IP=" in sh and 'case "$LAN_IP"' in sh:
                    g += 1
                if "uci get network.lan.ipaddr" in sh:
                    rb += 1
                if lit_re.search(sh) and "uci get network.lan.ipaddr" not in sh:
                    lit += 1
    print(f"{label:28s} sha={hashlib.sha256(raw).hexdigest()[:16]} models={len(b['models'])} "
          f"versions={b.get('versions')} recipes={n} guarded={g} readback={rb} literal={lit}")
    print(f"{'':28s} model version values={sorted(map(str,ver_vals))}")
