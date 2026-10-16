# conwrt issue #32 — workaround / D-ID set / structure audit of defects-d1-d5.md (findings)

Date: 2026-10-01, checks 13:51–13:52 local (+0200), host dq05
Worker: fleet offload worker (profile worker-heavy), dispatched workspace
/home/c03rad0r/repos/conwrt (branch pr-55, HEAD ef30e7f at check time).
Task: independently verify (1) the stated_workaround column, (2) the
'## Discrepancies' D-ID set, and (3) the overall structure of
`~/.hermes/profiles/manager/state/conwrt-issue32-evidence/defects-d1-d5.md`
against `~/.hermes/profiles/manager/state/conwrt-issue32-verification-runbook.md`.

Locations: this report lives at the dispatch OUTPUT path (manager evidence
dir) and as a byte-identical repo-side copy at
`state/conwrt-issue32-evidence/workaround-did-structure-findings.md` in the
conwrt repo (locally committed on pr-55, not pushed) — the commit vehicle
used by the two prior issue32 evidence commits (cc5f134, ef30e7f).

## Verdicts

Workaround check: FAIL — the artifact `defects-d1-d5.md` does not exist on
disk (direct `test -e`, 2026-10-01T13:51:32+02:00), so there are ZERO table
rows whose stated_workaround value could be read; and the runbook against
which each value would be verified is itself absent, so no workaround —
stated, paraphrased, softened, or any 'none stated' contradicted by an
adjacent sentence — can be confirmed or falsified. No workaround-level
defect is asserted or invented.

D-ID set reconciliation: FAIL — the artifact's '## Discrepancies' section
cannot be read (file absent), and the reference D-ID list cannot be built
from the raw runbook because the runbook file is absent; the METHOD's named
cross-check file `runbook-inventory.md` is absent as well. Both D-ID sets
are therefore EMPTY-because-absent (listed verbatim below). Per the task's
hard constraint, no D-IDs were invented from the GitHub issue or from the
sibling fragments to force the two lists to agree.

Structure check: FAIL — with zero artifact bytes on disk, the required shape
(exactly a '## Discrepancies' section, the table, and optionally
long-description bullets) cannot be confirmed, and no extra content (runbook
overview, step list, conclusions, executive summary, or other) could be
observed either. No structural defect beyond the absence itself is reported.

All three FAILs mean UNVERIFIABLE — primary inputs absent — not "checked and
found wrong". Nothing passes by default.

## D-ID sets, verbatim (for the downstream assembler)

- Artifact set (IDs in the '## Discrepancies' section of defects-d1-d5.md):
  (empty — file absent; no section exists to read)
- Runbook set (D-IDs in conwrt-issue32-verification-runbook.md):
  (empty — file absent)
- Cross-check list (runbook-inventory.md): (empty — file absent)

Assembler assertion: both sets are empty-for-absent. Equality over absent
inputs is VACUOUS and must NOT be recorded as a verified match. Re-run this
audit only after the manager re-supplies BOTH files.

## Primary evidence (all first-hand, this session, one command batch)

1. Direct existence check, 2026-10-01T13:51:32+02:00 (`test -e` on each
   dispatch-named path), verbatim output:
   ```
   ABSENT : /home/c03rad0r/.hermes/profiles/manager/state/conwrt-issue32-evidence/defects-d1-d5.md
   ABSENT : /home/c03rad0r/.hermes/profiles/manager/state/conwrt-issue32-verification-runbook.md
   ABSENT : /home/c03rad0r/.hermes/profiles/manager/state/conwrt-issue32-evidence/runbook-inventory.md
   ```
2. Evidence-dir listing at the same moment (concurrent-activity facts):
   `fragment-d3.md` (13:18), `fragment-d5.md` (13:04),
   `quote-location-findings.md` (13:26), `structure-findings-partial.md`
   (13:07), `triage-d3-d5-context.md` (13:45), plus `preflight/`
   (`reachability.txt` 12:47, `reachability-attempt2-20261001.txt` 13:12,
   `clock-sync.txt` 13:20, `run-log.md` 13:47). No `defects-d1-d5.md`.
3. Scoped negative searches, both completed rc=0 with no hits:
   - `find ~/.hermes/profiles/manager -maxdepth 5` for
     `defects-d1-d5*` / `*verification-runbook*` / `runbook-inventory*`
   - `find ~/repos/conwrt` (whole tree) for the same three patterns
4. conwrt repo state at check time: root /home/c03rad0r/repos/conwrt,
   branch pr-55, HEAD ef30e7f566bc02d087d65716454daf83c863a894,
   `git status --porcelain` empty (clean).
5. Never committed on ANY ref:
   `git log --all --oneline --diff-filter=A -- '*defects-d1-d5*' '*conwrt-issue32-verification-runbook*'`
   → empty output, rc=0. A sweep of every filename ever touched on any ref
   for defects-d1-d5|verification-runbook|runbook-inventory matched nothing
   (rc=1).
6. The only issue32-named paths at HEAD are
   `state/conwrt-issue32-evidence/drafts/net4sats-verification.md` and
   `state/conwrt-issue32-evidence/preflight-validation.md` — neither is the
   artifact or the runbook.

## Corroborating quotes (sibling lanes / preflight, all read this session)

- `preflight/reachability.txt:19-20`: "Referenced runbook
  ~/.hermes/profiles/manager/state/conwrt-issue32-verification-runbook.md
  no longer exists on disk."
- `structure-findings-partial.md:11`: "VERDICT: FAIL — the artifact
  `defects-d1-d5.md` does not exist on disk, so the required
  `## Discrepancies` section, table, and long-description bullets cannot be
  confirmed."
- `quote-location-findings.md` (Verdicts): "Verbatim-quote check: FAIL —
  the artifact `defects-d1-d5.md` does not exist on disk at audit time" and
  "Location check: FAIL — the source runbook
  `conwrt-issue32-verification-runbook.md` is itself absent".

Acceptance-criterion note: ZERO discrepancies are claimed by this audit, so
"every claimed discrepancy is backed by a quoted runbook line" is vacuously
satisfied; the only quoted lines above are absence evidence, each with
file:line.

## Non-runbook D material on disk (facts only — explicitly NOT canonical)

- `fragment-d3.md` and `fragment-d5.md` each contain one raw markdown table
  row (D3, D5) + one loose prose line. Their own provenance cells say,
  verbatim: "ctx file triage-d3-d5-context.md ABSENT — D3 reconstructed from
  Amperstrand/conwrt#32 \"Known open defects\" item 3" (D3) and "… — D5
  reconstructed from Amperstrand/conwrt#32 \"Known open defects\" item 5"
  (D5). Their upstream is the GitHub issue, NOT the runbook; they are not
  artifact rows and are not counted in either D-ID set above.
- No D4 material exists anywhere searched: sibling
  `triage-d3-d5-context.md` §2.2 records `find <evidence dir> -iname '*d4*'`
  → rc=0, no hits (sibling-verified, command+rc recorded there; not re-run
  by this task — see Consent disclosure).
- A concurrent lane is actively producing D-row material in this directory
  (files landed at 13:45–13:48 while sibling lanes ran). The final artifact
  may yet be assembled; this report does not predict its shape and must be
  re-run against the real files once both exist.

## Consent-system disclosure

One supplementary read-only re-verification command (existence re-check +
`find -iname '*d4*'` + `rev-parse` + `ls` mtimes) was DENIED by the user
consent system at ~13:53 local. Per its terms and fleet convention it was
not retried, rephrased, or attempted by other means. The negative claims in
this report rest on the COMPLETED 13:51:32 command batch (items 1–6 above),
which already covers all three dispatch-named paths; the two facts not
re-captured first-hand (D4 absence; evidence dir not being a git repo) are
attributed to `triage-d3-d5-context.md` §2.2 / §4, which records its
commands and return codes.

## Disclosures

- Report, do not fix: honored. No edit was made to the runbook or the
  artifact (both absent); no trivial formatting repair was performed
  anywhere — there was nothing to repair. No file under the evidence dir
  other than this findings file was written.
- Hard constraint honored: no defects or IDs invented to force agreement;
  the "'Not present in runbook' is a correct artifact entry" rule never
  triggered because no artifact rows exist to evaluate.
- Commit: repo-side copy committed locally on pr-55 (docs-only; no source
  changes), not pushed (no push instructed). The manager-side evidence dir
  is itself not a git repository (sibling `triage-d3-d5-context.md` §4:
  `rev-parse --show-toplevel` → "fatal: not a git repository (or any of the
  parent directories): .git", rc=128, captured 2026-10-01T11:32:14Z),
  hence the repo-side copy as the commit vehicle, matching the convention
  of cc5f134 and ef30e7f.
- This findings file is the only file written by this task (both locations
  carry identical bytes).
