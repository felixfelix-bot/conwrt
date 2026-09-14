# Triage row D1 — conwrt issue #32 evidence

Verification header (written 2026-09-15, live fleet re-check): branch `feat/vpn-provider-setup`,
HEAD `f6a91329c583d13550a3791015aed124230a3758` — re-measured with
`git -C /home/c03rad0r/repos/conwrt rev-parse HEAD` and `--abbrev-ref HEAD` immediately
before writing this row.

**Input gap — reported, not guessed around:** the task's designated input
`~/.hermes/profiles/manager/state/conwrt-issue32-evidence/recon.md` DOES NOT EXIST.
Negative-verified before declaring the gap: absent at the exact path;
`find ~/.hermes -name 'recon.md'` → no hits anywhere in the Hermes tree; no `recon` content
under the evidence dir. The evidence directory contains only `row-d2.md` and
`.scratch-defect-quotes.md`, and BOTH already record this same gap (row-d2.md "Note on recon
context"; .scratch §0) and establish the canonical fallback for a missing defects/recon file:
`~/.hermes/profiles/manager/state/conwrt-issue32-verification-runbook.md`
(sha256 `d3231a1d36a9592c199912f5758c6ff51eb949b657f09c771c9b1afaf294c907`, defect table
line 30). The D1 definition taken from there was re-verified byte-exact against the LIVE
issue #32 body (`gh issue view 32 --repo Amperstrand/conwrt --json body`, state OPEN, fetched
2026-09-15, body line 16):

> `scp` lines hardcode `root@192.168.1.1` while `ssh` honors `$IP` — breaks if the operator sets a non-default `IP`

Branch state: the branch has moved once since the prior evidence stamp
(`b303744` → `f6a9132`); `git diff --stat b303744..f6a9132` touches only
`state/conwrt-issue32-evidence/.scratch-defect-quotes.md` and
`state/conwrt-issue32-evidence/row-d2.md` — no file cited in this row is affected. Every
citation below was re-resolved live at `f6a9132` with `sed -n '<line>p'` byte-checks;
nothing is carried over from a stale source. `checklist.md` and `triage-d1-d2.md` do not
exist anywhere under the manager state tree or the repo `state/` dir (verified by find);
neither was created or touched.

## Row

| ID | file:line | impact | blocks live run? | minimal fix |
|----|-----------|--------|------------------|-------------|
| D1 | Primary: `scripts/flows/render.py:74` — `f"scp -O {sh_quote(filename)} root@{target['default_ip']}:{remote}"` — the ONLY scp emitter in the recipe render path (inside `_install_package`, `render.py:60-81`; host block `render.py:72-75`). Split-brain in the same renderer: `render.py:173` emits the operator-overridable preamble `IP=${IP:-192.168.1.1}` and `render.py:186` emits `ssh root@$IP sh <<'CONWRT_EOF'` for every device-side block. Value source: `models/comfast-cf-wr632ax.json:9` (`"default_ip": "192.168.1.1"`) via `scripts/profile/target.py:128`. Rendered recipes under test: `docs/wizard-bundle.json:352` (net4sats shell — hardcoded scp at rendered lines 33 AND 41) and `:358` (tollgate shell — rendered line 33); markdown twins `:353`/`:359` carry the same scp lines. Bundle-wide scope: 56 rendered recipe shells carry the hardcoded scp destination (142 `root@192.168.1.1` occurrences on 112 bundle lines). Locator correction for the live worker: the runbook's fix-direction names `scripts/flows/_gateway.py`, but that module emits no scp — `rg 'scp' scripts/flows/` resolves only to `render.py:74`; don't hunt in `_gateway.py`. | When the operator runs a recipe with a non-default IP (`IP=<real> sh <recipe>` — the documented contingency in runbook §6: this unit may randomize its LAN IP after factory reset, and this specimen was previously LOST to exactly that), every device block (`ssh root@$IP`) hits the right router while every host-side scp dials literal 192.168.1.1. Under `set -e` (recipe line 5) the recipe then dies at the FIRST install step: (a) if 192.168.1.1 is dead — scp times out / connection refused, aborting right after the WiFi-STA step has already committed `wireless.default_radio1.disabled='1'` (default AP off) plus the STA config — leaving a half-configured device whose default AP no longer broadcasts, recoverable only by hand; (b) if a DIFFERENT OpenWrt box sits at 192.168.1.1 — the artifact is silently scp'd to the wrong device and the right device's subsequent `apk add /tmp/<file>` fails "file not found", an error far from the root cause. At the default IP (no override) scp and ssh agree and nothing fails. | no — runbook §6's primary path expects the device AT 192.168.1.1 (`default_ip` = `stock_default_ip` = 192.168.1.1, `models/comfast-cf-wr632ax.json:9`/`:28`), where the hardcoded scp destination coincides with `$IP` and both CF-WR632AX recipes (net4sats + tollgate, 25.12.4) run end-to-end; the CF-WR632AX LAN-move step is also a 192.168.1.1→192.168.1.1 no-op, so the device never changes IP mid-run. D1 bites only §6's fallback contingency (device comes up on a randomized IP after the flash step, forcing `IP=<other>`), where it hard-blocks the run at the first scp — the live worker should carry the one-line patch below (or hand-fix the two scp lines) if that materializes. Runbook PR B row 1 additionally requires the non-default-IP evidence (`IP=<newip> sh <recipe>` runs clean) as this fix's acceptance proof. | One line at `render.py:74`: `- f"scp -O {sh_quote(filename)} root@{target['default_ip']}:{remote}",` → `+ f"scp -O {sh_quote(filename)} root@$IP:{remote}",` — `$IP` is defined by the recipe preamble at `render.py:173`, giving the single source of truth the runbook's fix direction asks for. Replacement provenance: upstream commit `d54eba91b4f1718300ac2377632350b8f26cd930` applied this exact one-liner (commit message: "scp hardcoded root@192.168.1.1 instead of $IP (#32 defect class)"); it is in upstream/master but NOT an ancestor of this branch — confirm with `git show d54eba91 -- scripts/flows/render.py`. THEN regenerate: `python3 scripts/generate_site.py` — mandatory, because the live run executes the BUNDLE's rendered shell (`wizard-bundle.json:352`/`:358`), not render.py; without the regen the operator-facing recipe still dials 192.168.1.1. Do NOT cherry-pick all of `d54eba91` for D1: it additionally rewrites password ops (`chpasswd`→`printf|passwd`), the bundle, and adds `tests/integration/test_wizard_recipes.py` — the D1-minimal change is the single line + regen. No test pins the old string: the render-path tests assert only `ssh root@$IP` (`tests/test_flows_net4sats.py:40`, `tests/test_flows_tollgate_password.py:50`) and `tests/test_generate_site.py` has no scp/root@ assertion — the fix lands green with no test edit. |

Interaction: with the lan_ip/guard work — same file, different function, NO colliding fix: D1 edits `_install_package` (`scripts/flows/render.py:60-81`, host block `:72-75`), the lan work edits `_set_lan_ip_ops` (`render.py:130-140` on this branch); no shared variables (D1: filename/remote/host built from `step.artifact_url`; lan: `target["lan_gateway"]`/`target["lan_subnet"]`), no line overlap, and ordering is safe because every scp step renders before the (last) LAN-move step. One shared constraint: both fixes regenerate `docs/wizard-bundle.json` via `python3 scripts/generate_site.py` — land both render.py edits on the same branch and regenerate ONCE; upstream proofs: D1 fix `d54eba91` does not touch `_set_lan_ip_ops` (verified: `git show d54eba91 -- scripts/flows/render.py | grep -c set_lan_ip` = 0), and the upstream lan guard `17a7786` is in upstream/master but NOT on this branch.

## Provenance / re-verification

- Branch/HEAD re-measured before any citation: `git rev-parse HEAD` →
  `f6a91329c583d13550a3791015aed124230a3758`, `git rev-parse --abbrev-ref HEAD` →
  `feat/vpn-provider-setup` (matches the session-start workspace snapshot).
- Every cited line byte-checked at HEAD with `sed -n '<line>p'`: `render.py:74` (scp
  emitter), `:166` (`ip = target["default_ip"]`), `:173` (IP preamble), `:186`
  (ssh root@$IP), `render.py:130-140` (`_set_lan_ip_ops`, read in full),
  `models/comfast-cf-wr632ax.json:9`/`:28`, `scripts/profile/target.py:128`,
  `tests/test_flows_net4sats.py:40`, `tests/test_flows_tollgate_password.py:50`.
- Rendered recipes extracted live from the committed bundle (json → line-numbered shell):
  net4sats line 6 `IP=${IP:-192.168.1.1}`, line 13 `ssh root@$IP`, line 33 + 41
  `scp -O ... root@192.168.1.1:/tmp/...`; tollgate line 33 same. Hardcoded scp confirmed
  on bundle lines 352/353/358/359 by grep of those exact lines.
- Sole-emitter claim measured: `rg -n 'scp' scripts/flows/` → only `render.py:4,5` (module
  docstring), `:74` (the emitter), `:186` is the ssh heredoc line (`ssh`, not scp).
  Runtime apply-path scp emitters (`scripts/use_cases/tollgate.py:340-352`,
  `ssl.py:165-181`, `configurationwizzard.py:90-115`) build `f"root@{ip}:{...}"` from a
  runtime `ip` argument — parameterized, not hardcoded, and not part of the rendered
  recipes; the conwrt/extreme/fieldlab scp call sites are device-recovery code, unrelated
  to the wizard recipes.
- Upstream fix provenance measured: `git show d54eba91 -- scripts/flows/render.py` shows
  the byte-identical `-`/`+` pair quoted in the fix cell; `git merge-base --is-ancestor
  d54eba91 upstream/master` passes; `git merge-base --is-ancestor d54eba91 HEAD` fails
  (D1 open on this branch). Upstream lan guard `17a7786` likewise verified: in
  upstream/master, not an ancestor of HEAD.
- D1 definition verified against the live issue (2026-09-15): `gh issue view 32 --repo
  Amperstrand/conwrt --json state,body` → state OPEN; body line 16 contains the D1 bullet
  verbatim (live body sha256
  `985afdf4cf8bf286c4a5a07f68a9782c1599d62bc97062ff6179e54b6b8b4d7a`).
- Forbidden files: `checklist.md`, `triage-d1-d2.md` — no hits by find under
  `~/.hermes/profiles/manager/state/` or the repo `state/` dir; not created, not touched.