# Structure Findings (partial) — conwrt issue #32

**Scope:** Verify the structural integrity of the verification runbook:
section numbering, table header/column consistency, and cross-reference
completeness.  Check that every D-ID in the defects table has a
corresponding row in the PR B stacking plan (and vice versa), and that the
runbook's headline counts match the actual content.

**Source examined:**
`~/.hermes/profiles/manager/state/conwrt-issue32-verification-runbook.md`
(16084 bytes, 235 lines, sha256
`d3231a1d36a9592c199912f5758c6ff51eb949b657f09c771c9b1afaf294c907`).

## 1. Section structure

The runbook has 7 numbered sections:

- §1 (line 9): "Issue #32 — Exact Verification Checklist"
- §2 (line 47): "AGENTS.md Verification Sequence (extract from upstream master `bb2ee6e`)"
- §3 (line 76): "The Two Recipe Files Under Test (exact paths, upstream master)"
- §4 (line 109): "Evidence Format for `tested_hardware` Entries"
- §5 (line 139): "PR A Draft Body Outline (data-only, \"Fixes #32\")"
- §6 (line 186): "SSH Connection Details"
- §7 (line 219): "Staging Status & Fork State (as of 2026-09-01)"

Section numbering is contiguous 1–7 with no gaps or duplicates.

## 2. Table header consistency

### Defects table (§1, lines 28–35)

Header (verbatim, runbook line 28):

```text
| # | Defect | Evidence command on device | Fix direction |
```

All 6 data rows (D1, D2, D2b, D3, D4, D5) have exactly 4 columns matching
this header.  No malformed rows, no missing cells.

### PR B Stacking Plan table (§5, lines 174–180)

Header (verbatim, runbook line 174):

```text
| Commit | Defect | Change | SSH evidence line (template) |
```

All 5 data rows (commits 1–5) have exactly 4 columns matching this header.
No malformed rows, no missing cells.

## 3. Cross-reference completeness

### Defects table → PR B plan

Every base D-ID in the defects table (D1, D2, D3, D4, D5) has a
corresponding commit row in the PR B plan (commits 1–5).  D2b has no
separate PR B row — this is by design (D2b is a sub-check of D2, folded
into commit 2).  The PR B commit-2 row's SSH evidence template includes
"corrupted-artifact test → guard exits 1", which is D2b's subject.

### PR B plan → Defects table

Every D-ID in the PR B plan (D1, D2, D3, D4, D5) has a defining row in the
defects table.  No orphan references.

### Order rationale (runbook line 182, verbatim):

```text
Order rationale: D2 (supply-chain) is safety-critical → do first on device; D1/D3/D4/D5 are functional correctness.
```

This line references D1, D2, D3, D4, D5 — all five base D-IDs.  It does NOT
reference D2b, consistent with D2b being a sub-check.

## 4. Headline count vs actual content

- Runbook line 25 (verbatim): "### The 5 known open defects (both PR
  versions) — check while in there"
  - Actual base D-IDs in the table: 5 (D1, D2, D3, D4, D5) ✓
  - Plus D2b sub-identifier: 6 total rows ✓ (the headline says "5 known
    open defects"; D2b is a sub-check, not a separate defect)

- Runbook line 169 (verbatim): "## PR B Stacking Plan (5 defect fixes,
  each with SSH evidence line)"
  - Actual commits in the plan: 5 (commits 1–5) ✓

## 5. Issue #32 body bullets vs defects table

The runbook includes a "verbatim" section (lines 37–43) reproducing the
five defect bullets from the issue #32 body.  These correspond to D1–D5.

Two minor wording differences between the issue-body bullets and the table
cells (both noted in runbook-inventory.md):

- D1: table cell says "breaks if operator sets non-default `IP`" vs issue
  bullet says "breaks if the operator sets a non-default `IP`" (table omits
  "the" and "a").
- D3: table cell says "verify `tollgate-wrt` apk" vs issue bullet says
  "verify the `tollgate-wrt` apk" (table omits "the").

These are not structural defects — they are minor editorial differences
between two representations of the same defect, both preserved verbatim in
the runbook.  The runbook-inventory.md documents both differences
explicitly in the D1 and D3 blocks.

## Verdict

**PASS — runbook structure is complete and internally consistent.**

Justification: 7 numbered sections are contiguous (1–7, no gaps).  Both
tables (defects table and PR B plan) have consistent 4-column headers with
all rows matching.  Every base D-ID (D1–D5) in the defects table has a
corresponding PR B commit row; D2b is correctly folded into D2's commit.
Every PR B D-ID has a defining table row.  Headline counts ("5 known open
defects", "5 defect fixes") match the actual content.  The two minor
wording differences between issue-body bullets and table cells (D1: "the"/"a"
omission; D3: "the" omission) are documented in runbook-inventory.md and
are not structural defects.