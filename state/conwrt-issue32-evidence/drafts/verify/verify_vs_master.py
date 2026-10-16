#!/usr/bin/env python3
"""Are the 84 committed literal recipes byte-identical to master's bundle?"""
import json, re, collections
from pathlib import Path

REPO = Path.home() / "repos" / "conwrt"
pr = json.loads((REPO / "docs" / "wizard-bundle.json").read_text())
ma = json.loads(Path("/dev/shm/master-bundle.json").read_text())

lit_re = re.compile(r"uci set network\.lan\.ipaddr='[^']*'")

def recipes(b):
    out = {}
    for mid, flows in b["rendered"].items():
        for fname, vers in flows.items():
            for ver, c in vers.items():
                out[(mid, fname, ver)] = c.get("shell", "")
    return out

p, m = recipes(pr), recipes(ma)
print("pr-55 recipes:", len(p), " master recipes:", len(m))
print("keys only in pr-55:", sorted(set(p) - set(m)))
print("keys only in master:", sorted(set(m) - set(p)))

same = diff = 0
diffkeys = []
for k in sorted(set(p) & set(m)):
    if p[k] == m[k]:
        same += 1
    else:
        diff += 1
        diffkeys.append(k)
print("byte-identical shell strings:", same)
print("differing shell strings     :", diff)
for k in diffkeys:
    print("   DIFFERS:", k)
print()
print("=== the 84 literal recipes: identical to master? ===")
litkeys = [k for k, sh in p.items() if lit_re.search(sh)]
print("literal recipes in pr-55:", len(litkeys))
ident = [k for k in litkeys if p.get(k) == m.get(k)]
print("of those, byte-identical to master:", len(ident))
mdkeys = [k for k, sh in p.items() if lit_re.search(sh) or "LAN_IP=" in sh]
print()
print("=== all LAN-move-bearing recipes (literal or guarded) ===")
print("count:", len(mdkeys))
for k in sorted(mdkeys):
    tag = "GUARDED" if "LAN_IP=" in p[k] else "literal"
    print(f"  {tag:8s} {k}")
