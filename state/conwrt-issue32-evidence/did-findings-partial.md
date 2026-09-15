# D-ID Set Findings (partial) — conwrt issue #32

**Scope:** Enumerate the complete set of defect identifiers (D-IDs) in the
verification runbook and check for gaps, duplicates, or mismatches between
the two places D-IDs appear: the defects table (§1, lines 28–35) and the
PR B Stacking Plan (§5, lines 174–180).

**Source examined:**
`~/.hermes/profiles/manager/state/conwrt-issue32-verification-runbook.md`
(16084 bytes, 235 lines, sha256
`d3231a1d36a9592c199912f5758c6ff51eb949b657f09c771c9b1afaf294c907`).

## D-ID SET A — Defects table (runbook §1, lines 30–35)

Verbatim table rows:

```text
| D1 | `scp` lines hardcode `root@192.168.1.1` while `ssh` honors `$IP` — breaks if operator sets non-default `IP` | `grep -n 'scp' <recipe>` shows `root@192.168.1.1` hardcoded | Render `scp -O ... root@$IP:/tmp/...` (single source of truth) |
| D2 | Artifacts installed with `apk add --allow-untrusted` and **no sha256 verification** (blossom.primal.net URLs) — supply-chain exposure; AGENTS.md sha256 discipline applies | (pre-install check on host) `sha256sum <downloaded .apk>` vs pinned value | Pin sha256 in flow module; add `sha256sum` check before `apk add` |
| D2b | (on device) verify the sha256 check rejects a corrupted artifact | `sha256sum /tmp/<hash>.apk` | — |
| D3 | `nodogsplash` is configured (`uci set nodogsplash...`) but never explicitly installed — verify `tollgate-wrt` apk pulls it in as a dependency | `apk info tollgate-wrt | grep -i nodogsplash`; `apk list-installed \| grep nodogsplash` | Explicit `apk add nodogsplash` (or confirm dep) |
| D4 | `umdns` — confirm the package exists in the 25.12.4 mediatek/filogic apk repo | `apk search umdns`; `apk add umdns` (observe success/fail) | Keep or drop the umdns step based on repo reality |
| D5 | STA uplink assumes `radio1` = 5GHz — confirm radio mapping on this board | `uci show wireless \| grep radio` + `iw dev radio0 info; iw dev radio1 info` (or `wifi status`) | Render band→radio from board reality (auto-detect), not assumption |
```

Identifiers in SET A: **D1, D2, D2b, D3, D4, D5** (6 identifiers)

## D-ID SET B — PR B Stacking Plan (runbook §5, lines 176–180)

Verbatim table rows:

```text
| 1 | D1 scp hardcodes root@192.168.1.1 | Render `scp -O ... root@$IP:/tmp/...` in `scripts/flows/_gateway.py` (and check all scp emitters) | `$ grep -n "scp" <recipe>; IP=<newip> sh <recipe>` — runs clean with non-default IP |
| 2 | D2 no sha256 on apk artifacts | Pin sha256 for both blossom .apk URLs in flow modules; add `sha256sum -c` before `apk add` | Host: `sha256sum <file>` = pinned; Device: `sha256sum /tmp/<file>` = pinned; corrupted-artifact test → guard exits 1 |
| 3 | D3 nodogsplash never installed | `apk add nodogsplash` explicitly (or confirm `tollgate-wrt` pulls it in; then document) | Device: `apk list-installed | grep nodogsplash`; `apk info tollgate-wrt` dependency list |
| 4 | D4 umdns existence in 25.12.4 repo | If package exists → keep step, pin confirmation in notes; if not → remove step | Device: `apk search umdns` output; `apk add umdns` exit code |
| 5 | D5 radio1=5GHz assumption | Auto-detect 5GHz radio (`uci show wireless` / `iw info`) instead of assuming radio1; or render correct band for this board after checking | Device: `uci show wireless | grep radio`; `iw dev radio0/radio1 info` band output |
```

Identifiers in SET B: **D1, D2, D3, D4, D5** (5 identifiers)

## SET A vs SET B — comparison

- SET A has 6 identifiers: D1, D2, D2b, D3, D4, D5
- SET B has 5 identifiers: D1, D2, D3, D4, D5
- The difference: **D2b** appears in SET A (the defects table) but NOT in
  SET B (the PR B stacking plan).
- SET B's headline says "5 defect fixes" (runbook line 169: "PR B Stacking
  Plan (5 defect fixes, each with SSH evidence line)"); SET A's headline
  says "The 5 known open defects" (runbook line 25).
- D2b is a sub-check of D2 ("(on device) verify the sha256 check rejects a
  corrupted artifact") with no separate fix direction (its Fix direction
  cell is `—`).  It is folded into commit 2 of the PR B plan (which covers
  D2 and includes the corrupted-artifact test: "corrupted-artifact test →
  guard exits 1").

## Verdict

**PASS — both D-ID sets are complete and internally consistent.**

Justification: SET A (defects table) contains 6 identifiers (D1–D5 + D2b)
with no gaps or duplicates in the base numbering (D1–D5 contiguous).  SET B
(PR B plan) contains 5 identifiers (D1–D5) matching the headline "5 defect
fixes".  The only difference is D2b, which is a sub-check of D2 with no
separate fix direction — it is correctly folded into D2's commit-2 row in
SET B.  The runbook-inventory.md independently confirms: "Total D-IDs found
in the runbook: 6 — D1, D2, D2b, D3, D4, D5" and "Gaps: none. Duplicates:
none."