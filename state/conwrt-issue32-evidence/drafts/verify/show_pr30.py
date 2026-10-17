#!/usr/bin/env python3
import json
from pathlib import Path

for f in ("pr30.json",):
    p = Path("/dev/shm") / f
    if not p.exists():
        print("missing", p)
        continue
    d = json.loads(p.read_text())
    print("=== PR #30 ===")
    print("number      :", d["number"])
    print("state       :", d["state"])
    print("mergedAt    :", d["mergedAt"])
    print("mergeCommit :", d["mergeCommit"])
    for c in d.get("statusCheckRollup") or []:
        print("  check:", c.get("name"), "->", c.get("conclusion") or c.get("state"))

c = Path("/dev/shm/pr30-checks.json")
if c.exists():
    d = json.loads(c.read_text())
    print()
    print("=== check-runs for merge commit 3b5fb44 ===")
    print("total_count:", d.get("total_count"))
    for r in d.get("check_runs", []):
        print("  ", r["name"], "->", r["conclusion"], "|", r.get("html_url"))
