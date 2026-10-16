#!/usr/bin/env python3
"""Confirm: does the LOCAL pr-55 checkout have a freshness gate?

The upstream freshness test lives in tests/test_wizard_recipes.py and compares
build_bundle() against docs/wizard-bundle.json. Check whether that file exists
on the local branch, and whether the local tests/test_generate_site.py asserts
anything about the COMMITTED bundle.
"""
from pathlib import Path

REPO = Path.home() / "repos" / "conwrt"

cands = [
    "tests/test_wizard_recipes.py",
    "tests/integration/test_wizard_recipes.py",
    "tests/test_generate_site.py",
]
for c in cands:
    p = REPO / c
    print(f"{c:48s} exists={p.exists()}")
    if p.exists():
        txt = p.read_text()
        print(f"{'':48s} mentions committed bundle: "
              f"{'docs/wizard-bundle.json' in txt or 'wizard-bundle' in txt}")
        print(f"{'':48s} mentions build_bundle  : {'build_bundle' in txt}")
        for line in txt.splitlines():
            if "stale" in line.lower() or "regenerat" in line.lower():
                print(f"{'':48s}   > {line.strip()}")
