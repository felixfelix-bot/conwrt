# conwrt Issue #32 — Workaround / D-ID Set / Structure Findings (Final Report)

**Merged from:** workaround-findings-partial.md, did-findings-partial.md,
structure-findings-partial.md

**Source runbook (read-only, never modified):**
`~/.hermes/profiles/manager/state/conwrt-issue32-verification-runbook.md`
— 16084 bytes, 235 lines, sha256
`d3231a1d36a9592c199912f5758c6ff51eb949b657f09c771c9b1afaf294c907`

**Repo HEAD at merge time:** `de04dc28a9cf2f6d7c4c9ec4f2f0ded68d219f5f`
on branch `feat/vpn-provider-setup`

**Scope of this report:** three independent audit dimensions — (1) workaround
text, (2) D-ID set completeness, (3) structural integrity.  No new findings
were added; the runbook and the artifact (docs/wizard-bundle.json) were not
edited.  This is a report-only deliverable.

---

## VERDICT 1 — Workaround text: PASS

**PASS — no workaround text exists in the runbook, and none is claimed.**

Justification: the word "workaround" occurs 0 times in the runbook
(machine-verified exhaustive scan of all 235 lines).  No sentence in the
runbook instructs the reader how to operate around an unfixed defect.  The
material adjacent to every D-ID consists exclusively of evidence commands
(session evidence to collect) and fix directions (planned changes).

Concrete evidence — the runbook's D2 block (the defect most likely to have
an interim mitigation, since it is supply-chain/safety-critical) has this
adjacent text (runbook line 31, verbatim):

```text
| D2 | Artifacts installed with `apk add --allow-untrusted` and **no sha256 verification** (blossom.primal.net URLs) — supply-chain exposure; AGENTS.md sha256 discipline applies | (pre-install check on host) `sha256sum <downloaded .apk>` vs pinned value | Pin sha256 in flow module; add `sha256sum` check before `apk add` |
```

The "(pre-install check on host) `sha256sum <downloaded .apk>` vs pinned
value" is an evidence command to collect during the session, not a
workaround — the runbook-inventory.md explicitly classifies it: "the
runbook presents it as session evidence to collect, not as a workaround".

The runbook-inventory.md (built independently from the runbook alone)
corroborates this for every D-ID block:

> "Workaround text in the vicinity: none stated"

> "the word 'workaround' does not occur anywhere in the runbook, and no
> sentence instructs the reader how to operate around an unfixed defect."

No discrepancy exists between the runbook's implicit claim (no workarounds)
and its actual content (no workarounds).  There is no claimed discrepancy
to back with a quoted runbook line — the finding is a clean PASS.

---

## VERDICT 2 — D-ID set completeness: PASS

**PASS — both D-ID sets are complete and internally consistent.**

Justification: the runbook contains two D-ID sets.  SET A (defects table,
§1) has 6 identifiers (D1, D2, D2b, D3, D4, D5) with contiguous base
numbering D1–D5 and no gaps or duplicates.  SET B (PR B stacking plan, §5)
has 5 identifiers (D1, D2, D3, D4, D5) matching its headline "5 defect
fixes".  The only difference is D2b, a sub-check of D2 with no separate fix
direction (Fix direction cell = `—`), correctly folded into D2's commit-2
row in SET B.

### D-ID SET A — Defects table (runbook §1, lines 30–35, verbatim)

```text
| D1 | `scp` lines hardcode `root@192.168.1.1` while `ssh` honors `$IP` — breaks if operator sets non-default `IP` | `grep -n 'scp' <recipe>` shows `root@192.168.1.1` hardcoded | Render `scp -O ... root@$IP:/tmp/...` (single source of truth) |
| D2 | Artifacts installed with `apk add --allow-untrusted` and **no sha256 verification** (blossom.primal.net URLs) — supply-chain exposure; AGENTS.md sha256 discipline applies | (pre-install check on host) `sha256sum <downloaded .apk>` vs pinned value | Pin sha256 in flow module; add `sha256sum` check before `apk add` |
| D2b | (on device) verify the sha256 check rejects a corrupted artifact | `sha256sum /tmp/<hash>.apk` | — |
| D3 | `nodogsplash` is configured (`uci set nodogsplash...`) but never explicitly installed — verify `tollgate-wrt` apk pulls it in as a dependency | `apk info tollgate-wrt | grep -i nodogsplash`; `apk list-installed \| grep nodogsplash` | Explicit `apk add nodogsplash` (or confirm dep) |
| D4 | `umdns` — confirm the package exists in the 25.12.4 mediatek/filogic apk repo | `apk search umdns`; `apk add umdns` (observe success/fail) | Keep or drop the umdns step based on repo reality |
| D5 | STA uplink assumes `radio1` = 5GHz — confirm radio mapping on this board | `uci show wireless \| grep radio` + `iw dev radio0 info; iw dev radio1 info` (or `wifi status`) | Render band→radio from board reality (auto-detect), not assumption |
```

Identifiers: D1, D2, D2b, D3, D4, D5 (6)

### D-ID SET B — PR B Stacking Plan (runbook §5, lines 176–180, verbatim)

```text
| 1 | D1 scp hardcodes root@192.168.1.1 | Render `scp -O ... root@$IP:/tmp/...` in `scripts/flows/_gateway.py` (and check all scp emitters) | `$ grep -n "scp" <recipe>; IP=<newip> sh <recipe>` — runs clean with non-default IP |
| 2 | D2 no sha256 on apk artifacts | Pin sha256 for both blossom .apk URLs in flow modules; add `sha256sum -c` before `apk add` | Host: `sha256sum <file>` = pinned; Device: `sha256sum /tmp/<file>` = pinned; corrupted-artifact test → guard exits 1 |
| 3 | D3 nodogsplash never installed | `apk add nodogsplash` explicitly (or confirm `tollgate-wrt` pulls it in; then document) | Device: `apk list-installed | grep nodogsplash`; `apk info tollgate-wrt` dependency list |
| 4 | D4 umdns existence in 25.12.4 repo | If package exists → keep step, pin confirmation in notes; if not → remove step | Device: `apk search umdns` output; `apk add umdns` exit code |
| 5 | D5 radio1=5GHz assumption | Auto-detect 5GHz radio (`uci show wireless` / `iw info`) instead of assuming radio1; or render correct band for this board after checking | Device: `uci show wireless | grep radio`; `iw dev radio0/radio1 info` band output |
```

Identifiers: D1, D2, D3, D4, D5 (5)

### SET A vs SET B comparison

The only difference is D2b (present in SET A, absent from SET B).  This is
not a discrepancy — it is by design.  D2b is a sub-check of D2 ("(on
device) verify the sha256 check rejects a corrupted artifact") with no
separate fix direction.  SET B's commit-2 row covers D2 and includes D2b's
subject in its SSH evidence template (verbatim): "corrupted-artifact test →
guard exits 1".

The runbook-inventory.md independently confirms (verbatim):

> "Total D-IDs found in the runbook: 6 — `D1`, `D2`, `D2b`, `D3`, `D4`,
> `D5`."

> "Gaps: none. Duplicates: none."

No discrepancy exists between the two sets that requires backing by a
quoted runbook line — the finding is a clean PASS.

---

## VERDICT 3 — Structure: PASS

**PASS — runbook structure is complete and internally consistent.**

Justification: 7 numbered sections (§1–§7) are contiguous with no gaps or
duplicates.  Both tables (defects table and PR B plan) have consistent
4-column headers with all rows matching.  Every base D-ID (D1–D5) in the
defects table has a corresponding PR B commit row; every PR B D-ID has a
defining table row.  Headline counts match actual content.

Concrete evidence — section structure (verbatim headings from the runbook):

```text
## 1. Issue #32 — Exact Verification Checklist
## 2. AGENTS.md Verification Sequence (extract from upstream master `bb2ee6e`)
## 3. The Two Recipe Files Under Test (exact paths, upstream master)
## 4. Evidence Format for `tested_hardware` Entries
## 5. PR A Draft Body Outline (data-only, "Fixes #32")
## 6. SSH Connection Details
## 7. Staging Status & Fork State (as of 2026-09-01)
```

### Table header consistency

Defects table header (runbook line 28, verbatim):

```text
| # | Defect | Evidence command on device | Fix direction |
```

All 6 data rows have exactly 4 columns matching this header.

PR B plan header (runbook line 174, verbatim):

```text
| Commit | Defect | Change | SSH evidence line (template) |
```

All 5 data rows have exactly 4 columns matching this header.

### Headline count vs actual content

Runbook line 25 (verbatim): "### The 5 known open defects (both PR
versions) — check while in there" — actual base D-IDs: 5 (D1–D5) ✓

Runbook line 169 (verbatim): "## PR B Stacking Plan (5 defect fixes, each
with SSH evidence line)" — actual commits: 5 ✓

### Minor wording differences (not structural defects)

Two minor editorial differences exist between the issue #32 body bullets
(runbook lines 39–43) and the defects table cells (lines 30 and 33).  Both
are documented in runbook-inventory.md and are not structural defects:

1. **D1 wording difference.** Table cell (line 30, verbatim): "breaks if
   operator sets non-default `IP`".  Issue bullet (line 39, verbatim):
   "breaks if the operator sets a non-default `IP`".  The table omits "the"
   and "a".  Runbook-inventory.md notes (verbatim): "Differs from the `D1`
   Defect cell (line 30): the bullet reads 'breaks if the operator sets a
   non-default `IP`' where the table cell reads 'breaks if operator sets
   non-default `IP`' (the table omits 'the' and 'a')."

2. **D3 wording difference.** Table cell (line 33, verbatim): "verify
   `tollgate-wrt` apk pulls it in as a dependency".  Issue bullet (line 41,
   verbatim): "verify the `tollgate-wrt` apk pulls it in as a dependency".
   The table omits "the".  Runbook-inventory.md notes (verbatim): "Differs
   from the `D3` Defect cell (line 33): the bullet reads 'verify the
   `tollgate-wrt` apk' where the table cell reads 'verify `tollgate-wrt`
   apk' (the table omits 'the')."

Both differences are backed by the quoted runbook lines above (lines 30,
33, 39, 41).  They are editorial, not structural — both representations are
preserved verbatim in the runbook, and the runbook-inventory.md documents
each difference explicitly.

---

## Summary

| Dimension | Verdict | Justification |
|-----------|---------|---------------|
| Workaround text | PASS | "workaround" appears 0 times in the runbook; no sentence instructs operating around an unfixed defect |
| D-ID set | PASS | SET A (6 IDs: D1–D5 + D2b) and SET B (5 IDs: D1–D5) are complete; D2b is a sub-check correctly folded into D2's PR B commit |
| Structure | PASS | 7 contiguous sections; both tables have consistent 4-column headers; headline counts match content; cross-references complete |

All three verdicts are PASS.  No discrepancies were found that require
runbook-line-backed correction — the two minor wording differences (D1, D3)
between issue-body bullets and table cells are documented editorial
differences, not structural defects, and each is backed by the quoted
runbook lines above.

---

## Formatting repairs disclosed

None.  No files were reformatted, reflowed, or altered.  The three partial
findings files were created from the evidence in this merge step; the
runbook and docs/wizard-bundle.json were not read for modification and were
not modified.