# Bundle staleness decision — the 84 literal LAN-move recipes in `docs/wizard-bundle.json`

Task id `t_f644c1b9` (board conwrt), author worker-base, read-only audit, no repo edits.

**Bottom line:** `docs/wizard-bundle.json` is a **CI build artifact that got committed**, not a
frozen issue-#32 ground truth. It is already stale on upstream master and was already fixed
there by a commit that names this exact defect. **Recommended: option (d) — do NOT hand-patch
the 84; import upstream's regeneration + freshness gate.** Details in §5.

---

## 0. Corrections to this card's own framing (read this first)

The card's CONTEXT is accurate about the *bundle contents* but wrong about three load-bearing
identifiers. Every claim below is re-derived from the checkout, not copied from the summary.

**Corrected identifiers** (each row: what the card says, then the verified reality, then the
evidence):

- Card: "the PR #55 evidence checkout (~/repos/conwrt @ pr-55, **HEAD 4f169a2**)".
  Reality: HEAD of `pr-55` is **f0e2f9c**; 4f169a2 is merely an **ancestor**.
  Evidence: `git rev-parse HEAD` gives f0e2f9c1117912dc2da4aaa21daeacfccd705e7a;
  `git merge-base --is-ancestor 4f169a2 HEAD` returns YES;
  `git log --oneline 4f169a2..HEAD` lists f0e2f9c and 391bf77.

- Card: "cite the PR #55 commit/CI that produced it".
  Reality: **PR #55 did not produce it.** Upstream Amperstrand/conwrt PR #55 is
  *"feat(vpn): VPN setup library proposal + PIA OpenVPN (tested)"*, state **CLOSED**.
  The commit that wrote this bundle is **17a7786**, which came from **PR #30**.
  Evidence: `gh pr view 55 --repo Amperstrand/conwrt` yields that title;
  `gh api repos/Amperstrand/conwrt/commits/17a7786.../pulls` yields PR #30.

- Card: implies `pr-55` is a GitHub PR head.
  Reality: `pr-55` is a **locally assembled branch** (ec5c60d = upstream pr55head oid, then
  issue32 doc commits stacked on top). No GitHub PR has head f0e2f9c.
  Evidence: `git rev-list --left-right --count amperstrand/master...pr-55` gives `55  7`.

The correct provenance citation for §2(a) is therefore **PR #30**, not PR #55.

---

## 1. Independent re-verification of the counts

Method: `wizard-bundle.json` parsed as JSON; classifier =
guarded ⟺ `LAN_IP=` present **and** `case "$LAN_IP"` present; read-back ⟺
`uci get network.lan.ipaddr` present; literal ⟺ regex `uci set network\.lan\.ipaddr='([^']*)'`
matched **and** read-back absent. Scripts in the task workspace (`verify_bundle.py`,
`verify_literals.py`, `verify_vs_master.py`, `verify_regen.py`, `verify_three_bundles.py`).

Bundle identity — **matches the card exactly**:

```
path              : /home/c03rad0r/repos/conwrt/docs/wizard-bundle.json
sha256            : 3b1f047be5e7495f75c3af42c86bcfba2d3e0491ddf17f5ec670600d8ed25f39
bytes             : 619242
generated_at      : 2026-06-23 16:11 UTC
top-level keys    : ['addons', 'flows', 'generated_at', 'models', 'rendered', 'versions']
bundle['versions']: ['24.10.7', '25.12.4']
len(bundle['models']) : 22
len(bundle['flows'])  : 2          # ['net4sats', 'tollgate']
```

Recipe inventory — **every card number reproduced**:

```
total recipes                            : 86
recipes with LAN_IP='{{lan_ip}}' var     :  2
recipes with case ... exit 1 guard       :  2
recipes with uci get read-back           :  2
recipes with LITERAL set + NO read-back  : 84
```

The guarded 2 are exactly as stated:

```
  guarded: comfast-cf-wr632ax net4sats  25.12.4
  guarded: comfast-cf-wr632ax tollgate 25.12.4
```

**The 84 decompose as 21 models × 2 flows × 2 versions** (the card's "84" is right but the
structure is worth pinning, because it drives the blast radius in §4):

```
distinct models with literal recipes: 21
recipes per model: [4]        # 4 = {net4sats, tollgate} × {24.10.7, 25.12.4}
```

Literal == that model's `lan_subnet` network+1 — **21/21 OK, 0 mismatches, 0 missing model
files**:

```
  asus-lyra-map-ac2200        lan_subnet=10.231.9.0/24   expected_gw=10.231.9.1   bundle_literals=['10.231.9.1'] OK
  dlink-covr-x1860-a1         lan_subnet=10.89.4.0/24    expected_gw=10.89.4.1    bundle_literals=['10.89.4.1']  OK
  glinet-mt3000               lan_subnet=10.230.236.0/24 expected_gw=10.230.236.1 bundle_literals=['10.230.236.1'] OK
  ... (21 rows, 21 OK)
mismatches: 0 missing model files: 0
```

21 distinct literals, each appearing 4× — consistent with the 21×2×2 decomposition.

### The reproduction failure reproduces exactly

```
$ python3 scripts/generate_site.py <tmp>/regen-bundle.json
Generated /dev/shm/regen-2999650/regen-bundle.json (23 models × 2 flows = 46 rendered)
  EXIT=0

regenerated: versions=['24','25']  models=23  recipes=92  guarded=92  readback=92  literal=0
committed  : versions=['24.10.7','25.12.4'] models=22 recipes=86 guarded=2 readback=2 literal=84
```

A model present in the regen but **absent** from the committed bundle: `virtual-x86-64`.

### The divergence is NOT nondeterminism

Two consecutive generator runs are byte-identical modulo `generated_at`:

```
two regen runs identical (modulo generated_at): True
```

So the committed bundle is not "a slightly older but valid generator output". It is a
**hybrid that no single generator run could ever produce**: 84 of 86 shell strings are
**byte-identical to master's bundle**, while only the two CF-WR632AX recipes differ, and those
two are byte-identical to the current renderer's `_identity_lan_ops` output
(`scripts/flows/render.py:159-209`).

```
pr-55 recipes: 86   master recipes: 86
keys only in pr-55 : []
keys only in master: []
byte-identical shell strings: 84
differing shell strings     :  2
   DIFFERS: ('comfast-cf-wr632ax', 'net4sats', '25.12.4')
   DIFFERS: ('comfast-cf-wr632ax', 'tollgate', '25.12.4')

=== the 84 literal recipes: identical to master? ===
literal recipes in pr-55: 84
of those, byte-identical to master: 84
```

`84 + 2 = 86` ⇒ the committed bundle is `master_bundle` with exactly two entries surgically
swapped. Confirmed by the commit's own diff stat.

---

## 2. Question (a): frozen ground truth, or build artifact?

**Answer: it is a build artifact — and specifically, a hand-edited build artifact. It was never
a frozen issue-#32 ground truth.**

### (a1) The producing commit says so in its own words

```
commit 17a7786f0cceb5e0e4f658b80bc0d71dd5c5d552
Author: Felix <301398501+felixfelix-bot@users.noreply.github.com>
Date:   Sun Aug 30 20:09:18 2026 +0530
Subject: fix(wizard): CF-WR632AX LAN step — identity-derived CGNAT lan_ip replaces
         broken static assignment
...
    - wizard-bundle.json: CF-WR632AX entries regenerated with the real
      renderers on fresh master (also picks up umdns, apk portal artifact,
      hostname step); still pinned to 25.12.4 only
...
 docs/wizard-bundle.json        | 24 ++++++++++---
 models/comfast-cf-wr632ax.json |  1 -
 scripts/flows/_gateway.py      | 11 +++++-
 scripts/flows/render.py        | 77 ++++++++++++++++++++++++++++++++++++++++---
 4 files changed, 101 insertions(+), 12 deletions(-)
```

"**CF-WR632AX entries** regenerated" — two entries, 24 changed lines (`+19/-5`). A full
generator run would have rewritten all 86. The author knew the bundle was hand-patched.

### (a2) The real producing PR, and its CI

`gh api .../commits/17a7786.../pulls` → **PR #30**, *"fix(wizard): CF-WR632AX recipes v2 —
identity-derived CGNAT lan_ip (successor of #28)"*, head `c03rad0r:cf-wr632ax-recipe-v2`,
base `Amperstrand:master`.

```
state       : MERGED
mergedAt    : 2026-08-31T11:21:27Z
mergeCommit : 3b5fb4462b9c6198cb9b803d9f053a850cec58c9
  check: test (3.10) -> SUCCESS     check: test (3.11) -> SUCCESS
  check: test (3.12) -> SUCCESS     check: test (3.13) -> SUCCESS
```

Check-runs on the merge commit `3b5fb44` — note `build` and `deploy`:

```
total_count: 6
   deploy    -> success   .../runs/33386580447/job/99470502144
   test (3.10)-> success  .../runs/33386580470/job/99470459546
   test (3.11)-> success  .../runs/33386580470/job/99470459566
   test (3.12)-> success  .../runs/33386580470/job/99470459642
   test (3.13)-> success  .../runs/33386580470/job/99470459361
   build     -> success   .../runs/33386580447/job/99470458973
```

### (a3) The repository *treats* it as a build artifact

`.github/workflows/device-matrix.yml` runs the generator with **no argv**, which — per
`scripts/generate_site.py:112` (`out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT/"docs"/"wizard-bundle.json`)
— writes `docs/wizard-bundle.json` in the CI workspace, then publishes `path: docs` to Pages:

```yaml
      - name: Generate matrix page
        run: |
          python3 scripts/generate_matrix.py docs/index.html
          python3 scripts/generate_site.py
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: docs
```

Corroborating facts:

- `docs/wizard-bundle.json` is **not** in `.gitignore` (`git check-ignore -v` → not ignored) —
  so the committed copy is a *published snapshot*, not a local-only artifact.
- `make ci` does **not** regenerate it (`Makefile:97-100`: `lint`, `typecheck`, `validate-schemas`
  only) — so nothing in CI keeps the committed copy honest. That is the root cause of this whole
  card.
- The generator's own docstring calls the file derived output: *"Emits `docs/wizard-bundle.json`:
  the models + flows + per-(model, flow) rendered shell/markdown templates"* — and asserts
  *"Python remains the sole renderer and the published site can never drift from the CLI"*.
  The published snapshot violated precisely that guarantee.

### (a4) Its staleness is not unique to `pr-55` — it is stale on upstream too (already fixed there)

Three bundles, same classifier:

```
committed(pr-55 HEAD)        sha=3b1f047be5e7495f models=22 versions=['24.10.7','25.12.4']
                             recipes=86 guarded=2  readback=2  literal=84
                             model version values=['24.10.7','25','25.12.4','snapshot']
origin/master                sha=6fe93f952fe68a53 models=22 versions=['24.10.7','25.12.4']
                             recipes=86 guarded=0  readback=0  literal=86
                             model version values=['24.10.7','25.12.2','25.12.4','snapshot']
upstream amperstrand/master  sha=514f1da50e546ddc models=23 versions=['24','25']
                             recipes=92 guarded=92 readback=92 literal=0
                             model version values=['24','25','snapshot']
```

Read the third row carefully: **upstream master's committed bundle is already fully correct** —
92 recipes, 92 guarded, 0 literals, versions `['24','25']` — i.e. byte-equivalent in shape to
what `generate_site.py` emits here. Upstream did the regeneration work; this checkout predates it.

Note also the fourth column: the committed bundle carries a **model `version` value of `"25"`**
for `comfast-cf-wr632ax`, while `bundle['versions']` says `["24.10.7","25.12.4"]`. That
inconsistency is visible in the producing commit's own diff:

```
@@ -18,7 +18,7 @@
       "target": "mediatek/filogic",
-      "version": "25.12.4",
+      "version": "25",
```

— and it is a **regression introduced by `17a7786` itself**, which also dropped `lan_subnet`
from `models/comfast-cf-wr632ax.json` (`git show HEAD:models/comfast-cf-wr632ax.json` → no
`lan_subnet` key). Losing the literal is what makes the two surviving recipes *correct*; the
stray `"25"` is collateral damage.

### (a5) Upstream already has a freshness gate — and it names this defect class

`d54eba9` — *"test(wizard): recipe apply-on-VM + bundle freshness checks — catches recipe rot"*
(merged before `4df9415`, closes **#42** *"Wizard-recipe apply-on-VM: catch recipe rot before
users do"*):

```
Layer 1 (CI-safe): bundle regenerates from code, every render substitutes and
parses (sh -n), no hardcoded router IPs outside IP= default, pinned blossom
artifacts download + sha256-match their filename.
...
Recipe rot caught and fixed en route:
- scp hardcoded root@192.168.1.1 instead of $IP (#32 defect class)
- password addons used chpasswd, which OpenWrt BusyBox lacks — now
  printf|passwd (empirically verified on the VM)
- committed bundle was stale (new virtual-x86-64 model + version scheme)
```

**"committed bundle was stale (new virtual-x86-64 model + version scheme)"** — that sentence
describes exactly the symptom on this card (the regen's extra model is `virtual-x86-64`; the
regen's version scheme is `['24','25']`). The freshness assertion upstream is
`tests/test_wizard_recipes.py:96`:

```python
    def test_committed_bundle_matches_code(self):
        ...
        from generate_site import build_bundle
        regenerated = build_bundle()
        regenerated.pop("generated_at", None)
        assert committed == regenerated, (
            "docs/wizard-bundle.json is stale — run: python3 scripts/generate_site.py"
        )
```

**That gate does not exist on the local `pr-55` branch** (`tests/test_wizard_recipes.py` absent;
local `tests/test_generate_site.py` imports `build_bundle` but never compares against the
committed file), and that is why the staleness survived here undetected. The 84-literal bundle
would **fail** that assertion; upstream's current bundle **passes** it.

---

## 3. Question (b): the remediation options and their blast radius

Notation: "the 84" always means the 21×2×2 literal LAN-move recipes in `docs/wizard-bundle.json`.

### Option A — regenerate via `scripts/generate_site.py`

```
$ python3 scripts/generate_site.py            # no argv → docs/wizard-bundle.json
```

Effect on the 84: every one is rewritten from the literal+no-guard form to the guarded
`{{lan_ip}}` placeholder form (`LAN_IP='{{lan_ip}}'` + `case … exit 1` + `uci get … grep -qxF`
read-back), because `params` in the bundle generator are placeholders
(`_placeholder_params`, `scripts/generate_site.py:41-42`) and `_set_lan_ip_ops` with an unset
`lan_ip` returns the **skip** comment (`scripts/flows/render.py:217-222`), while a
`{{…}}` value routes into `_identity_lan_ops` (`render.py:176`).

Blast radius — **the whole file, not just the 84**:

- All 86 shell + 86 markdown strings: full rewrite; the 84 literal recipes change form **and**
  every recipe's markdown (heading + prose) is re-rendered.
- `bundle['versions']`: `['24.10.7','25.12.4']` becomes `['24','25']`.
- `len(bundle['models'])`: 22 becomes 23 (adds `virtual-x86-64`).
- `bundle['rendered']`: 86 becomes 92 recipes (23×2×2).
- model entries: per-model version values become `'24'`/`'25'`; `snapshot` retained.
- `addons`: re-rendered (`random-password` upstream now uses `passwd root`, not `chpasswd`).
- `generated_at`: bumped.

Per the measured regen: guarded 2 to 92; literal 84 to 0. One file changes
(`docs/wizard-bundle.json`, 619 KB). No source, model, or test file changes.

**Cards' verdicts that would need redoing:** every issue-#32-audit-family card whose evidence
is a *quote from the committed bundle* — the LAN-move fragment/draft cards, the net4sats and
tollgate recipe-verification cards, and the quote-location extraction cards, because the
quoted text no longer exists in the post-regen file. (Concretely: the family that produced
`_frag-lan-move-recipe.md`, `_frag-lan-ip-derivation.md`, `_frag-guard.md`, the net4sats and
tollgate drafts, and the D1–D5 defect rows.) Anything citing a **line number or byte offset**
into the current bundle is invalidated; anything citing the **sha256** is invalidated outright.

### Option B — hand-patch the 84 to the literal+read-back gateway form

Target form is the `_set_lan_ip_ops` fallback (`scripts/flows/render.py:223-232`): keep the
model-derived literal, drop the guard, **add** the `uci get … grep -qxF` read-back before
`uci commit`:

```
# move LAN off 192.168.1.1 → <gw> (<subnet>)
uci set network.lan.ipaddr='<gw>'
uci set network.lan.netmask='255.255.255.0'
uci get network.lan.ipaddr | grep -qxF '<gw>' || { echo 'ERROR: uci read-back mismatch …' >&2 ; exit 1 ; }
uci commit network
(/etc/init.d/network restart &) ; echo 'LAN moving to <gw> — reconnect on that subnet'
```

Blast radius: **the same 84 recipes, in `shell` and in `markdown`** (both must stay in sync, or
the wizard page and the CLI silently disagree — the very drift the generator docstring forbids).
Still one file. But the patch is **not reproducible**: the next `generate_site.py` run discards
it entirely, because this form is not what the generator emits for a placeholder render (the
generator emits the guarded form; the literal+read-back form is only reachable via a *concrete*
`lan_ip` on the CLI path). So this option buys a correct-looking bundle that is **still stale**,
trading one staleness class for a subtler one.

Advantages: the bundle keeps `versions ['24.10.7','25.12.4']` and 22 models, so audit-family
verdicts keyed to *those* facts survive. `generated_at` untouched (or bumped deliberately).

**Cards' verdicts that would need redoing:** only the cards whose evidence is the *exact bytes
of the LAN-move block* — the LAN-move fragment and its draft, the guard-related fragments, and
any D-row about the missing read-back (the defect the patch fixes). Bundle-wide quotes
(version keys, model count) still hold. Strictly smaller than Option A.

### Option C — leave frozen, file an upstream issue

Effect: `docs/wizard-bundle.json` in this checkout is untouched; a new issue describes the
hybrid/stale state and asks upstream to regenerate + add the freshness gate.

Blast radius: **zero files change here.** But: the artifact the audit family quotes remains
knowably wrong (84 recipes that write a model-table constant with no guard and no read-back),
and it stays un-reproducible from its own generator. Any downstream card that reads the bundle
as ground truth keeps inheriting the defect. Invalidation: none — and that is the problem.

### Option D — import upstream's already-merged fix (regenerate **and** add the freshness gate)

Not in the card's list, but it is the option the evidence actually supports. Upstream has
**already** regenerated the bundle (92/92/0, versions `['24','25']`) in `d54eba9` and
`4df9415`, and already added `test_committed_bundle_matches_code`
(`tests/test_wizard_recipes.py:96`), plus Layer-1 CI-safe + Layer-2 VM checks.

Blast radius: same file-level cost as Option A (one file), **plus** `tests/test_wizard_recipes.py`
and the `render.py`/`_gateway.py` changes those commits carry. The decisive difference: after
this, a stale bundle **cannot be committed again** — the freshness assertion fails CI. The
defect class is closed rather than re-fixed.

**Cards' verdicts that would need redoing:** the same set as Option A (bundle quotes are
invalidated), plus any card whose verdict rests on *the current bundle being stale* — that
finding becomes "known upstream defect, already fixed upstream", which is exactly the
re-framing this decision document supplies.

### Cross-cutting: why not regenerate inside this audit checkout?

Because `pr-55` is an **evidence branch**, not a development branch (its top two commits are
`391bf77`/`f0e2f9c`, both `docs(issue32):` evidence work), and the card forbids editing
`docs/wizard-bundle.json` in `~/repos/conwrt`. Any regeneration must land on a **separate
fix branch** as a normal PR, where the freshness gate can run.

---

## 4. Question (c): recommendation

**Recommend Option D — do not hand-patch the 84; adopt upstream's regeneration *together with*
`test_committed_bundle_matches_code`, on a dedicated fix branch.**

One-line justification: hand-patching (B) produces a second hand-edited build artifact that the
next generator run destroys and that nothing guards, while regenerating *without* the freshness
gate (A) guarantees this same card recurs — upstream has already shipped both the correct bundle
and the CI assertion that makes staleness impossible, so importing that pair (D) is the only
option that closes the defect class instead of re-arranging it.

### Support

1. **The artifact is derived, and the repo already says so** (§2a1, §2a3): "CF-WR632AX entries
   regenerated with the real renderers" + `device-matrix.yml` generating it for Pages +
   generator docstring "Python remains the sole renderer and the published site can never drift".
   Hand-patching a derived file re-creates the exact drift the design forbids.
2. **Option B is not reproducible.** `_set_lan_ip_ops` emits the literal+read-back form only for
   a *concrete* `lan_ip`; for the bundle's placeholder render it emits the guarded form
   (`render.py:176` vs `render.py:223`). So B's output is un-producible by the generator ⇒
   `test_committed_bundle_matches_code` would still fail ⇒ B is worse than A on the one axis
   that matters (reproducibility) while looking safer.
3. **Option A alone is insufficient.** Upstream's `d54eba9` message records that this staleness
   class *already recurred* ("committed bundle was stale (new virtual-x86-64 model + version
   scheme)") and closes #42 by adding the gate. Regenerating without the gate just resets the
   clock.
4. **The fix is already written and merged upstream** — lowest-risk possible remediation: we
   port a reviewed, CI-green change rather than authoring a novel one. PR #30's CI was green
   (`test 3.10–3.13 SUCCESS`), and the freshness commit's own message documents the VM
   verification (`test_lan_readback_holds`, `test_unfilled_placeholder_refused_on_device`).
5. **It preserves the audit family's purpose.** The audit's value is a *true* record of the
   recipes; regenerating from the authoritative renderer plus a gate that keeps them true makes
   every downstream quote true by construction, whereas Option C leaves 84 quoted recipes
   deliberately known-wrong.

### What to do with the frozen copies (does not conflict with "do not edit")

The card's "frozen evidence artifact" constraint is **satisfied by not editing it here**. If a
truly immutable ground truth is wanted for the audit family, the correct move is to **copy** the
current bytes (sha256 `3b1f047b…`) to an explicitly-named frozen path *outside the generator's
output path* — e.g. `state/conwrt-issue32-evidence/frozen/wizard-bundle.pr55.json` — and have the
audit family cite that path. Then `docs/wizard-bundle.json` is free to be the derived artifact it
is designed to be. That copy is an *addition*, not an edit, and is out of scope for this
read-only card; it is item 1 of the handoff below.

---

## 5. PR-branch line (required if a code change is recommended)

Recommended code change: **yes — option D**, to be carried on a dedicated branch, **not** on
`pr-55` and **not** in this audit checkout.

```
branch:  fix/wizard-bundle-regenerate-and-freshness-gate
base:    Amperstrand/conwrt @ master
carries: docs/wizard-bundle.json            (regenerated: 23 models, 92 recipes, 0 literals,
                                             versions ['24','25'])
         tests/test_wizard_recipes.py       (new; incl. test_committed_bundle_matches_code)
         scripts/flows/render.py            (the 2 commits' render deltas, if not already in base)
         scripts/flows/_gateway.py          (ditto)
proof:   python3 scripts/generate_site.py  → then `git status --porcelain docs/` is EMPTY
         pytest tests/test_wizard_recipes.py::...::test_committed_bundle_matches_code → PASS
note:    upstream already ships this as d54eba9 + 4df9415; port/cherry-pick rather than re-author
```

If the reviewer prefers **not** to touch the renderer, the minimal variant is:
regenerate `docs/wizard-bundle.json` and add **only** `test_committed_bundle_matches_code` — that
alone converts this defect class from "audited after the fact" to "blocks CI".

---

## 6. Verification-command index (for the reviewer)

All read-only; run from the checkout root. Scripts live in the task workspace and take no args.

All read-only; run from the checkout root. Scripts live in the task workspace and take no args.
Format: command, then what it proves.

1. `sha256sum docs/wizard-bundle.json` — proves the hash is 3b1f047be5e7495f75c3af42c86bcfba2d3e0491ddf17f5ec670600d8ed25f39.
2. `python3 verify_bundle.py` — 86 recipes; 2 guarded; 84 literal+no-readback; sha + keys.
3. `python3 verify_literals.py` — 84 equals 21x2x2; literal equals `lan_subnet` network+1 for 21/21.
4. `python3 verify_vs_master.py` — 84 shell strings byte-identical to master; exactly 2 differ.
5. `python3 scripts/generate_site.py /tmp/x.json` — prints "23 models × 2 flows = 46 rendered" (the reproduction).
6. `python3 verify_regen.py` — committed 2/2/84 vs regen 92/92/0.
7. `python3 verify_determinism.py` — two regen runs identical modulo `generated_at`.
8. `python3 verify_three_bundles.py` — pr-55 2/2/84, origin/master 0/0/86, upstream 92/92/0.
9. `git log --oneline -5 -- docs/wizard-bundle.json` — producing commit `17a7786`.
10. `git show 17a7786 -- docs/wizard-bundle.json` — the `"version": "25.12.4"` to `"25"` regression.
11. `gh api repos/Amperstrand/conwrt/commits/17a7786.../pulls` — PR **#30**, MERGED 2026-08-31, merge `3b5fb44`.
12. `gh pr view 55 --repo Amperstrand/conwrt` — PR #55 is the closed PIA/VPN PR, not this bundle.
13. `git show amperstrand/master:tests/test_wizard_recipes.py` — `test_committed_bundle_matches_code`.

## 7. Card-constraint compliance

- `docs/wizard-bundle.json` in `~/repos/conwrt` was **not** edited: `git status --porcelain docs/`
  is empty; the file's sha256 is unchanged at `3b1f047b…` (read-only: `read_bytes`, `json.loads`,
  `git show`). The generator was run only with an explicit output path under `/dev/shm`.
- The two LAN-move notes under `state/conwrt-issue32-evidence/` were **not** edited
  (`provenance-verification.md`, `tollgate-subsection.md`, `net4sats-verification.md`, and the
  untracked fragment files are all byte-unchanged; only a new file was added alongside them).
- This decision document was written to the task workspace, not into the repo.
