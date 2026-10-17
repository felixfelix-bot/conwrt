#!/usr/bin/env python3
"""Independent re-verification of the stale-LAN-move claims for t_f644c1b9.

Read-only. Reads docs/wizard-bundle.json from the conwrt checkout and reports
counts by JSON key path. No writes anywhere in the repo.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

REPO = Path.home() / "repos" / "conwrt"
BUNDLE = REPO / "docs" / "wizard-bundle.json"

raw = BUNDLE.read_bytes()
sha = hashlib.sha256(raw).hexdigest()
b = json.loads(raw)

print("=== A. bundle identity ===")
print("path              :", BUNDLE)
print("sha256            :", sha)
print("bytes             :", len(raw))
print("top-level keys    :", sorted(b.keys()))
print("generated_at      :", b.get("generated_at"))
print("bundle['versions']:", b.get("versions"))
print("len(bundle['models'])  :", len(b["models"]))
print("len(bundle['flows'])   :", len(b["flows"]))
print("flow names             :", [f["name"] for f in b["flows"]])

# model version values
mver = {}
for m in b["models"]:
    mver.setdefault(m.get("version"), []).append(m["id"])
print("model 'version' values :")
for v, ids in sorted(mver.items(), key=lambda kv: str(kv[0])):
    print(f"   version={v!r}  n={len(ids)}  e.g. {ids[:3]}")

print()
print("=== B. rendered recipe inventory ===")
rendered = b["rendered"]
total = 0
rows = []
for mid, flows in rendered.items():
    for fname, vers in flows.items():
        for ver, content in vers.items():
            total += 1
            shell = content.get("shell", "")
            md = content.get("markdown", "")
            rows.append(
                {
                    "model": mid,
                    "flow": fname,
                    "version": ver,
                    "shell_has_LAN_IP_var": "LAN_IP=" in shell,
                    "shell_has_case_guard": 'case "$LAN_IP"' in shell,
                    "shell_has_readback": "uci get network.lan.ipaddr" in shell,
                    "shell_has_literal_set": bool(
                        re.search(r"uci set network\.lan\.ipaddr='[^']*'", shell)
                    ),
                    "md_has_LAN_IP_var": "LAN_IP=" in md,
                }
            )
print("models in rendered:", len(rendered))
print("total recipes    :", total)

guarded = [r for r in rows if r["shell_has_LAN_IP_var"] and r["shell_has_case_guard"]]
readback = [r for r in rows if r["shell_has_readback"]]
literal_noreadback = [
    r for r in rows if r["shell_has_literal_set"] and not r["shell_has_readback"]
]
print("recipes with LAN_IP='{{lan_ip}}' var   :", len(guarded))
print("recipes with case ... exit 1 guard     :", len([r for r in rows if r["shell_has_case_guard"]]))
print("recipes with uci get read-back         :", len(readback))
print("recipes with LITERAL set + NO read-back :", len(literal_noreadback))

print()
print("=== C. the guarded 2 ===")
for r in sorted(guarded, key=lambda r: (r["model"], r["flow"])):
    print("  guarded:", r["model"], r["flow"], r["version"])

print()
print("=== D. extract the literal per recipe (model,flow,version) -> literal ===")
lit_re = re.compile(r"uci set network\.lan\.ipaddr='([^']*)'")
model_lan_subnet = {}
for m in b["models"]:
    # bundle model entries do not carry lan_subnet; record for cross-check later
    model_lan_subnet[m["id"]] = None

lit_rows = []
for r in rows:
    pass

lit_out = []
for mid, flows in rendered.items():
    for fname, vers in flows.items():
        for ver, content in vers.items():
            m = lit_re.search(content.get("shell", ""))
            if m:
                lit_out.append({"model": mid, "flow": fname, "version": ver, "literal": m.group(1)})

print("literal set found in", len(lit_out), "recipes")
import collections

by_lit = collections.Counter(x["literal"] for x in lit_out)
print("distinct literals:", len(by_lit))
for lit, n in sorted(by_lit.items()):
    print(f"   {lit:20s} x{n}")

print()
print("=== E. literal-bearing recipes that ALSO have read-back ===")
both = [x for x in lit_out if "uci get network.lan.ipaddr" in rendered[x["model"]][x["flow"]][x["version"]]["shell"]]
print(len(both))
for x in both:
    print("  ", x)

lit_norb = [x for x in lit_out if "uci get network.lan.ipaddr" not in rendered[x["model"]][x["flow"]][x["version"]]["shell"]]
print("literal + NO read-back:", len(lit_norb))

print()
print("=== F. write machine-readable summary ===")
summary = {
    "sha256": sha,
    "bytes": len(raw),
    "generated_at": b.get("generated_at"),
    "versions": b.get("versions"),
    "n_models": len(b["models"]),
    "n_flows": len(b["flows"]),
    "n_recipes": total,
    "n_guarded": len(guarded),
    "n_readback": len(readback),
    "n_literal_noreadback": len(literal_noreadback),
    "guarded": [{"model": r["model"], "flow": r["flow"], "version": r["version"]} for r in guarded],
    "distinct_literals": dict(by_lit),
    "literal_rows": lit_norb,
}
out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("verify-summary.json")
out.write_text(json.dumps(summary, indent=2))
print("wrote", out)
