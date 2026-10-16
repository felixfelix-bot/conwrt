FAIL

# net4sats-subsection.md — independent verification report

- Verdict: **FAIL** — the artifact under review could not be verified because it does
  not exist. This FAIL is driven by unresolvable inputs (missing draft, missing
  checklist, blocked JSON read), NOT by any detected content mismatch: no byte-level
  command-block diff was possible, so no mismatches were found and none are claimed.
- Verifier run: 2026-10-01, workspace /home/c03rad0r/repos/conwrt, branch `pr-55`,
  working tree clean at start (`git status --porcelain=v1` → empty).

## Findings

- `state/conwrt-issue32-evidence/drafts/net4sats-subsection.md` (the draft under
  review) is ABSENT:
  - not in the working tree: `ls state/` → `ls: cannot access 'state/': No such file or directory`
  - not anywhere on disk under the repo: `find . -name '*net4sats*' -print` matches only
    `scripts/flows/net4sats.py` and `tests/test_flows_net4sats.py`
  - not in any commit on any local or remote ref:
    `git log --all --name-only --format='C:%h' | grep -iE 'subsection|checklist|drafts'` → no output
  - not a dangling object: `git fsck --unreachable --no-progress` → no output
  - not on the remote: `git ls-remote --heads origin` lists 9 heads; none adds the draft
- `state/conwrt-issue32-evidence/net4sats-lan-move.md` (the diff source) is ABSENT on
  this branch; it exists only on local `master`, added by commit `4eed9f4`
  ("docs(issue32): net4sats LAN-move evidence — master bakes 192.168.1.1 literal
  no-op, no read-back; derived-ipv4 guard + uci-get read-back exists only on
  cf-wr632ax-recipe-v2 (17a7786, PR #31)", 214 insertions, 1 file).
  `git branch -a --contains 4eed9f4` → `master` only.
- `state/conwrt-issue32-evidence/checklist.md` is ABSENT from the working tree and
  from all git history (same name-only grep as above → no match). The evidence tree
  on `master` contains only `net4sats-lan-move.md` and `tollgate-lan-move.md`
  (`git ls-tree -r --name-only master -- state/`).
- `docs/wizard-bundle.json` exists and is tracked on `pr-55`, but its contents were
  NOT inspected during this run: the operator denied the read command. No claim is
  made about its internals; recipe-key and provenance checks could not be executed.
- Context: `/tmp/issue32-comments.json` (GitHub issue #32 comment thread, mtime
  2026-10-01 13:00) shows issue-32 evidence work is in flight, but the composed
  draft never landed in this workspace. The composition step evidently did not
  complete or its output was not committed here.
- No content mismatches were found — because there is no draft content to compare.
  Explicitly: zero command-block diffs were executed, zero key paths resolved,
  zero provenance verdicts assessed.

## Check-by-check reproduction

1. Command-block byte diff (draft vs net4sats-lan-move.md / wizard-bundle.json)
   - Run: `ls state/conwrt-issue32-evidence/drafts/net4sats-subsection.md`
   - Observed: `No such file or directory` (exit 2). Check NOT EXECUTABLE.
   - Correct output looks like: both files exist; then extract each fenced block,
     e.g. `awk '/^```(bash|sh|shell)?/{f=!f;next} f' <file> | sha256sum` per block
     (or split blocks and `cmp` pairwise) — identical hashes/`cmp` silent for every
     block pair.
2. Recipe key path resolution (draft section (b) vs docs/wizard-bundle.json)
   - Run: `jq -e '<cited-path>' docs/wizard-bundle.json`
   - Observed: NOT RUN twice over — the draft (which cites the path) is absent, and
     the JSON read was operator-denied this run.
   - Correct output looks like: `jq -e` prints the object and exits 0.
3. Provenance verdict consistency (draft section (e) vs JSON raw value)
   - Run: `jq '<cited-path>' docs/wizard-bundle.json` then classify literal /
     derived / unresolved placeholder against the draft's wording.
   - Observed: NOT RUN (draft absent; JSON read denied).
   - Correct output looks like: the raw JSON excerpt at the cited key path matches
     the draft's classification.
4. Derived-ipv4 citation (draft "derived ipv4 enters at ..." line)
   - Run: `sed -n '<cited-line>p' <cited-file>` (or `jq -e '<cited-key>'`) on the
     location the draft names.
   - Observed: NOT RUN (draft absent, so no citation exists to verify).
   - Correct output looks like: the quoted file:line / key path exists and contains
     the derived-ipv4 code/value the draft claims.
5. Checklist independence
   - Run: `git status --porcelain=v1`; `test -f state/conwrt-issue32-evidence/checklist.md; echo $?`;
     `git log --all --name-only | grep -i checklist`
   - Observed: porcelain empty (nothing modified); `test -f` → 1 (file absent);
     grep → no match. checklist.md was not modified by this run — it does not exist.
   - Correct output looks like: checklist.md present and unmodified (clean status,
     unchanged mtime), and the draft containing no reference to it. Here the check
     is vacuously satisfied: a nonexistent draft cannot modify or depend on a
     nonexistent checklist.

## Run integrity

- Files modified by this run: NONE. The only artifact produced is this new file,
  `state/conwrt-issue32-evidence/drafts/net4sats-verification.md`, committed locally.
- The draft, the source md, docs/wizard-bundle.json, and checklist.md were not
  modified (the first, second, and fourth do not exist; the third is tracked and
  `git status` remains clean for it).
- Not pushed, per task instructions.

## Recommendation

Re-run this verification once the composer step lands
`drafts/net4sats-subsection.md` (and ideally `checklist.md`) in this workspace —
for example on top of `master`, where the diff source `net4sats-lan-move.md`
already lives at `4eed9f4` — and after the operator permits reading
`docs/wizard-bundle.json`. All five checks above are then executable as written.
