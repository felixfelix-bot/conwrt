#!/usr/bin/env python3
import json, re, collections, ipaddress
from pathlib import Path

REPO = Path.home() / "repos" / "conwrt"
b = json.loads((REPO / "docs/wizard-bundle.json").read_text())
rendered = b["rendered"]

lit_re = re.compile(r"uci set network\.lan\.ipaddr='([^']*)'")
rows = []
for mid, flows in rendered.items():
    for fname, vers in flows.items():
        for ver, c in vers.items():
            m = lit_re.search(c.get("shell", ""))
            if m:
                rows.append((mid, fname, ver, m.group(1)))

by_model = collections.Counter(r[0] for r in rows)
print("distinct models with literal recipes:", len(by_model))
print("recipes per model:", sorted(set(by_model.values())))
for mid, n in sorted(by_model.items()):
    vers = sorted({r[2] for r in rows if r[0] == mid})
    flows = sorted({r[1] for r in rows if r[0] == mid})
    print(f"  {mid:32s} n={n} versions={vers} flows={flows}")

print()
print("=== literal == network+1 of that model's lan_subnet? ===")
bad = 0
missing = 0
for mid in sorted(by_model):
    p = REPO / "models" / f"{mid}.json"
    if not p.exists():
        print(f"  {mid:32s} MODEL FILE MISSING")
        missing += 1
        continue
    src = json.loads(p.read_text())
    sub = src.get("lan_subnet", "")
    gw = str(ipaddress.ip_network(sub, strict=False).network_address + 1) if sub else ""
    lits = sorted({r[3] for r in rows if r[0] == mid})
    ok = (lits == [gw]) if lits else False
    if not ok:
        bad += 1
    print(f"  {mid:32s} lan_subnet={sub:20s} expected_gw={gw:16s} bundle_literals={lits} {'OK' if ok else 'MISMATCH'}")
print("mismatches:", bad, "missing model files:", missing)

print()
print("=== comfast-cf-wr632ax model file ===")
cf = json.loads((REPO / "models" / "comfast-cf-wr632ax.json").read_text())
print("has lan_subnet key:", "lan_subnet" in cf, "| value:", cf.get("lan_subnet", "<absent>"))
print("openwrt.version  :", cf.get("openwrt", {}).get("version"))
