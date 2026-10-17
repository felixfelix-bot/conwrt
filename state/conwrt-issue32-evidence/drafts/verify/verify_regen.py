#!/usr/bin/env python3
"""Compare regenerated vs committed bundle. Read-only."""
import json, re
from pathlib import Path

REPO = Path.home() / "repos" / "conwrt"
tmpd = Path(open("/dev/shm/regen-path.txt").read().split("=", 1)[1].strip())
regen = json.loads((tmpd / "regen-bundle.json").read_text())
committed = json.loads((REPO / "docs" / "wizard-bundle.json").read_text())

print("=== G. regenerated bundle ===")
print("versions        :", regen["versions"])
print("n_models        :", len(regen["models"]))
print("n_flows         :", len(regen["flows"]))
print("n_recipes       :", sum(len(v) for m in regen["rendered"].values() for v in m.values()))
model_ver = {m["id"]: m.get("version") for m in regen["models"]}
print("comfast version :", model_ver.get("comfast-cf-wr632ax"))
print("model ids (regen):", sorted(model_ver))
print()
print("model ids (committed):", sorted(m["id"] for m in committed["models"]))
extra = sorted(set(model_ver) - set(m["id"] for m in committed["models"]))
print("models in regen NOT in committed:", extra)

lit_old = re.compile(r"uci set network\.lan\.ipaddr='([^']*)'")
def classify(bundle):
    g = r = lit = 0
    lits = {}
    for mid, flows in bundle["rendered"].items():
        for fname, vers in flows.items():
            for ver, c in vers.items():
                sh = c.get("shell", "")
                if "LAN_IP=" in sh and 'case "$LAN_IP"' in sh:
                    g += 1
                if "uci get network.lan.ipaddr" in sh:
                    r += 1
                m = lit_old.search(sh)
                if m and "uci get network.lan.ipaddr" not in sh:
                    lit += 1
                    lits.setdefault(mid, set()).add(m.group(1))
    return g, r, lit, lits

for label, bundle in (("COMMITTED", committed), ("REGEN", regen)):
    g, r, lit, lits = classify(bundle)
    print(f"{label:10s} guarded={g:3d} readback={r:3d} literal_no_readback={lit:3d}")
