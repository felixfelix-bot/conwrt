# Triage row D2 — conwrt issue #32 evidence

Verification header (re-confirmed 2026-09-14, mid-session): branch `feat/vpn-provider-setup`,
HEAD `5275d60dc6159f7f21e76f6eb3214bd4f71105a7`. Branch DID move during this triage
(`c53ef72` → `5275d60`, another worker's docs-only commit adding
`state/conwrt-issue32-evidence/drafts/net4sats-raw-commands.md`; `git diff --stat
c53ef72..5275d60` touches no file cited below). All file:line citations re-resolved
against `5275d60` after that commit landed.

Note on recon context: `~/.hermes/profiles/manager/state/conwrt-issue32-evidence/recon.md`
does not exist (the directory is absent). The D2 definition used here is from
`~/.hermes/profiles/manager/state/conwrt-issue32-verification-runbook.md` (issue #32
defect table, row D2), which matches the issue body verbatim: *"Artifacts installed with
`apk add --allow-untrusted` and no sha256 verification (blossom.primal.net URLs) —
supply-chain exposure; AGENTS.md sha256 discipline applies."*

## Row

| ID | file:line | impact | blocks live run? | minimal fix |
|----|-----------|--------|------------------|-------------|
| D2 | Primary: `scripts/flows/render.py:71` (defect spans `render.py:71-74` — install command + unpinned curl/scp host block). Missing pins: `scripts/flows/_gateway.py:17-20` (TOLLGATE_ALPHA3_URLS, no sha256) and `scripts/flows/_gateway.py:22-25` (CONFIGURATIONWIZZARD_URL, no sha256 anywhere — GitHub filename carries no hash). Sibling same-flaw site on the live deploy path: `scripts/use_cases/tollgate.py:356`. Rendered output under test: `docs/wizard-bundle.json:352` (net4sats) and `docs/wizard-bundle.json:358` (tollgate). Test pinning current behaviour: `tests/test_flows_net4sats.py:49`. | The recipe generator emits, for every apk-based target (OpenWrt 25.12.x — incl. both CF-WR632AX recipes under test; 60 rendered `apk add --allow-untrusted` occurrences in the bundle): host-side `curl -L -o <file> <url>` (redirect-following, no hash pin), `scp -O` (blind transfer), then device-side `apk add --allow-untrusted /tmp/<file>` — apk's signature/trust checks are explicitly bypassed and no sha256 is ever computed on host or device. Concrete failure conditions: any corrupted, truncated, or substituted artifact en route or on the CDN (Blossom/GitHub compromise, `curl -L` redirect swap, partial download that still parses) is silently installed **as root** on the router. Nothing errors: `apk add --allow-untrusted` succeeds on any parseable bytes, `set -e` never trips, and every later step (nodogsplash config, hotplug, hostname, LAN-move, reboot persistence) then "verifies" on top of an unverified binary — so a whole green-looking evidence session can certify an unsafe flow. The Blossom URL filename happens to BE the blob's sha256 (content addressing), but nothing checks it client-side, so the pin value is already on record and merely unenforced. The net4sats-only configurationwizzard.ipk (GitHub) has no hash in its URL at all, so it is unguessable without an explicit pin. Violates AGENTS.md sha256 discipline (BusyBox `sha256sum` match; Python-side hash must match BusyBox). | **YES** — fix (or at minimum add the on-device guard) before/with the live SSH run. Reasoning tied to actual run behaviour: this is *not* a crash blocker — no command fails, and that is precisely the hazard (the defect is 100% silent; the run goes green). It is *not* an optional path: the tollgate-wrt install step is in the shared gateway head (`gateway_base_steps()`, `scripts/flows/_gateway.py:55-62`), so both the net4sats and tollgate CF-WR632AX runs execute it; only the configurationwizzard install is net4sats-specific. The silent unverified install happens at step 3, i.e. *before* the LAN-move step that can strand the operator off-subnet, so evidence collected on the unguarded recipe is untrustworthy exactly when the risk peaks. The runbook already ranks D2 first on device ("supply-chain is safety-critical → do first"). The fix needs no further research (exact hashes below), so a live worker applies the guard, then runs. | (1) Live-run guard, zero code change — before each `apk add`, on device run `echo '<sha>  /tmp/<file>' | sha256sum -c -` (two-space checksum format, BusyBox-compatible) with sha = `1fcc1635a7d94a005ff270c4a44f49fb9c56b05a7fbfe01eabcba40e8d31571d` for tollgate-wrt aarch64 (equals the 64-hex Blossom URL filename; **verified by real download + `sha256sum` 2026-09-14: file hashes to exactly this value**) and `9928e1f08dc1024c2ea8fbe4d9ca7ead59c8e7327b09916960b7797da557558f` for configurationwizzard.ipk (**measured by real download 2026-09-14**; mipsel tollgate artifact: `2fb588b10a445555923f1325d11c3cb28220cb32f078b283d71d4d3100e58286`, also == its Blossom filename, also download-verified). Abort on mismatch (set -e). (2) Repo fix — `scripts/flows/render.py:71`, replace: `install = f"apk add --allow-untrusted {remote}" if pm == "apk" else f"opkg install {remote}"` with: `sha = step.artifact_sha256 or (filename.rsplit(".", 1)[0] if len(filename) > 64 and filename[64] == "." else "")` / `verify = f"echo '{sha}  {remote}' | sha256sum -c - && " if sha else ""` / `install = f"{verify}apk add --allow-untrusted {remote}" if pm == "apk" else f"{verify}opkg install {remote}"` (Blossom URLs are content-addressed, so the 64-hex filename IS the pin source); add `artifact_sha256: str = ""` to the Step dataclass (`scripts/flows/__init__.py:30`, after `artifact_urls`) and pin `artifact_sha256="9928e1f08dc1024c2ea8fbe4d9ca7ead59c8e7327b09916960b7797da557558f"` on the configurationwizzard Step (`scripts/flows/net4sats.py:26`) since its GitHub filename has no hash; regenerate the bundle with `python3 scripts/generate_site.py` (edit modules, not the bundle); update `tests/test_flows_net4sats.py:49`, which asserts the current unguarded literal. Keep `--allow-untrusted` for now — tollgate releases are unsigned (`use_cases/tollgate.py:355` "TODO: sign releases"); the sha guard closes integrity until signing lands. Same guard applies at the sibling live-deploy site `use_cases/tollgate.py:354-358` (fix the class, not just the reported site). |

## Interaction with the lan_ip/guard work — explicit note

- **Same file, different function — no colliding fix.** D2's fix edits `_install_package`
  (`scripts/flows/render.py:60-81`); the lan_ip/guard work edits `_set_lan_ip_ops`
  (`scripts/flows/render.py:130-140` on this branch). No shared variables: D2 touches the
  `install`/`host`/`router` locals built from `step.artifact_url(s)`; the lan work touches
  `target["lan_gateway"]`/`target["lan_subnet"]`. No line overlap → no merge conflict.
- **Branch state caveat:** the identity-derived lan_ip guard (upstream `17a7786`,
  "CF-WR632AX LAN step — identity-derived CGNAT lan_ip replaces broken static assignment")
  is NOT on this branch — `feat/vpn-provider-setup` still carries the pre-fix static
  `_set_lan_ip_ops`, which renders the no-op "move LAN off 192.168.1.1 → 192.168.1.1"
  block visible in both extracted CF-WR632AX recipes. That is the lan worker's defect;
  D2 neither depends on nor conflicts with it.
- **Same rendered recipe, adjacent steps — complementary ordering.** The install step
  (3rd) renders strictly before the LAN-move step (last). The D2 sha guard makes `set -e`
  abort on a corrupted artifact BEFORE the LAN move can run, so the operator can never be
  stranded off-subnet by a bad-artifact run — the two fixes compose; the D2 guard actually
  hardens the lan step's preconditions.
- **One sequencing constraint:** both fixes regenerate `docs/wizard-bundle.json` via
  `python3 scripts/generate_site.py`. Land both render.py edits on the same branch and
  regenerate once, to avoid bundle churn/regen conflicts.
- **Docs-only neighbor:** commit `5275d60` (net4sats-raw-commands draft, GAP-noted) is
  pure documentation; no code interaction with D2.

## Evidence provenance

- All citations resolved against `5275d60dc6159f7f21e76f6eb3214bd4f71105a7` (current HEAD,
  re-checked after the mid-session branch move; `git diff --stat c53ef72..5275d60` = 1 new
  docs file only).
- Rendered recipes extracted live from `docs/wizard-bundle.json` via the runbook's
  extraction command — both CF-WR632AX recipes show the unguarded
  `apk add --allow-untrusted /tmp/<file>` install blocks (and the net4sats flow shows the
  separate ext-mismatch warning ".ipk but comfast-cf-wr632ax uses apk" — a different defect,
  not D2; the sha pin above applies to the artifact regardless of format).
- Hashes measured, not assumed: all three artifacts downloaded 2026-09-14 and hashed with
  `sha256sum`; both Blossom artifacts hash exactly to their URL filename; the GitHub
  configurationwizzard.ipk hashes to `9928e1f08dc1024c2ea8fbe4d9ca7ead59c8e7327b09916960b7797da557558f`.