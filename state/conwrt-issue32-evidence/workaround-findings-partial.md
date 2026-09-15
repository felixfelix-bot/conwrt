# Workaround Findings (partial) — conwrt issue #32

**Scope:** Does the verification runbook contain any workaround text for the
open defects D1–D5 (and D2b)?  A workaround is defined as a sentence that
instructs the reader how to operate around an unfixed defect — interim
mitigation distinct from the stated fix direction.

**Source examined:**
`~/.hermes/profiles/manager/state/conwrt-issue32-verification-runbook.md`
(16084 bytes, 235 lines, sha256
`d3231a1d36a9592c199912f5758c6ff51eb949b657f09c771c9b1afaf294c907`).

**Method:** the runbook was read in full (all 235 lines).  An exhaustive
machine scan for the word "workaround" returned 0 hits.  Every D-ID block
was examined for surrounding text that resembles interim mitigation.

## Verbatim runbook quotes (what IS present around each D-ID)

For each defect the runbook provides exactly two kinds of adjacent text:
an evidence command (session evidence to collect on device) and a fix
direction (a planned change).  Neither is a workaround.

D1 table row (runbook line 30):

```text
| D1 | `scp` lines hardcode `root@192.168.1.1` while `ssh` honors `$IP` — breaks if operator sets non-default `IP` | `grep -n 'scp' <recipe>` shows `root@192.168.1.1` hardcoded | Render `scp -O ... root@$IP:/tmp/...` (single source of truth) |
```

D2 table row (runbook line 31):

```text
| D2 | Artifacts installed with `apk add --allow-untrusted` and **no sha256 verification** (blossom.primal.net URLs) — supply-chain exposure; AGENTS.md sha256 discipline applies | (pre-install check on host) `sha256sum <downloaded .apk>` vs pinned value | Pin sha256 in flow module; add `sha256sum` check before `apk add` |
```

D2b table row (runbook line 32):

```text
| D2b | (on device) verify the sha256 check rejects a corrupted artifact | `sha256sum /tmp/<hash>.apk` | — |
```

D3 table row (runbook line 33):

```text
| D3 | `nodogsplash` is configured (`uci set nodogsplash...`) but never explicitly installed — verify `tollgate-wrt` apk pulls it in as a dependency | `apk info tollgate-wrt | grep -i nodogsplash`; `apk list-installed \| grep nodogsplash` | Explicit `apk add nodogsplash` (or confirm dep) |
```

D4 table row (runbook line 34):

```text
| D4 | `umdns` — confirm the package exists in the 25.12.4 mediatek/filogic apk repo | `apk search umdns`; `apk add umdns` (observe success/fail) | Keep or drop the umdns step based on repo reality |
```

D5 table row (runbook line 35):

```text
| D5 | STA uplink assumes `radio1` = 5GHz — confirm radio mapping on this board | `uci show wireless \| grep radio` + `iw dev radio0 info; iw dev radio1 info` (or `wifi status`) | Render band→radio from board reality (auto-detect), not assumption |
```

## Verdict

**PASS — no workaround text exists in the runbook, and none is claimed.**

Justification: the word "workaround" occurs 0 times in the runbook
(machine-verified exhaustive scan).  No sentence in the runbook instructs
the reader how to operate around an unfixed defect.  The material adjacent
to every D-ID consists exclusively of (a) evidence commands to collect
during the hardware session and (b) fix directions describing planned
changes.  There is no discrepancy between the runbook's implicit claim
(no workarounds) and its actual content (no workarounds).

## Supporting evidence from the inventory

The runbook-inventory.md (built independently from the runbook alone)
corroborates this finding for every D-ID block:

> "Workaround text in the vicinity: none stated"

> "the word 'workaround' does not occur anywhere in the runbook, and no
> sentence instructs the reader how to operate around an unfixed defect."

(quoted from runbook-inventory.md, D1 block and verification section)