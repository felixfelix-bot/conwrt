# PR #55 — Credential persistence review

**PR:** `Amperstrand/conwrt#55` — *feat(vpn): PIA OpenVPN use case + VPN setup library proposal*
**Head reviewed:** `ec5c60d9` (pr-55 / pr55-review worktree, `git log -1` = `ec5c60d9`)
**Review focus:** how credentials persist across sessions/reboots — plaintext files,
file permissions, keychain/secret-store integration.
**Method:** static read at `ec5c60d9` + offline reproduction of the render / ASU-payload
paths (commands and observed output in "Reproduction" below). No live device was touched.

Adjacent reviews (different scope, same head): `docs/pr55-openvpn-module-logging-secrets-audit.md`
(logging/dry-run leakage), `docs/pr55-openvpn-env-secret-audit.md` (env-var leakage).
This document covers **at-rest persistence only**.

## Summary verdict

The PR consistently *intends* root-only credentials: every credential-bearing write
specifies `mode 600` (`openvpn_pia.py:331`, `ops.py:90-103`,
`ansible/roles/pia_openvpn/tasks/main.yml:32`). The failures are not in the intent, they are
in **(a) how the 600 is reached**, **(b) where else the same plaintext lands**, and
**(c) what happens to it afterwards**. Two findings need action before this is mergeable:

| id | severity | one line |
|----|----------|----------|
| CP-1 | **HIGH** | Enabling `openvpn-pia` puts the PIA password into the **ASU build payload sent to `sysupgrade.openwrt.org`** and bakes it into the firmware image. |
| CP-2 | **HIGH** | The controller-side plaintext copies: `config.toml` is **not** gitignored (despite the file claiming it is), and the raw defaults script is persisted into `build.metadata.json`. |
| CP-3 | MEDIUM | `mode 600` is applied **after** the content is written (`cat` then `chmod`) — if the script aborts in between, the credential stays world-readable in `/etc`, permanently. |
| CP-4 | MEDIUM | No removal/rotation path exists; the documented "rollback" leaves `/etc/openvpn/pia-auth.txt` in place and references a `/root/vpnbak` that exists nowhere in the tree. |
| CP-5 | MEDIUM | `/etc` backups sweep the credential off the device (fieldlab forensics `tar czf /etc`, stock `sysupgrade -b`); no exclusion is added. |
| CP-6 | MEDIUM | The TLS trust anchor (`ca.rsa.4096.crt`) is fetched with no checksum/pin — a swapped CA silently harvests the password. |
| CP-7 | LOW | `WriteFile` neither creates nor secures the parent directory (`/etc/openvpn`). |
| CP-8 | LOW | The design doc's credential table has no lifetime/at-rest/removal columns, so the provider model it proposes has no place to state any of this. |

No keychain/Bunker/TPM integration is attempted anywhere in the PR — see "Keychain
integration" below for why that is defensible today and what should still change.

## Credential inventory (at head ec5c60d9)

| Secret | Written at | Mode | Storage class | Survives reboot | Leaves the device |
|--------|-----------|------|---------------|-----------------|-------------------|
| PIA username + password | `/etc/openvpn/pia-auth.txt` (`openvpn_pia.py:69,331`; `tasks/main.yml:27-33`) | 600 (after `cat`) | persistent overlay (`/etc`) | yes | ASU build payload, `/etc` backups, forensics tarball |
| same pair, on the controller | `config.toml` `[use_cases.openvpn-pia]` (`config.py:291-299`) | umask default (0644/0664) | repo working tree | n/a | one `git add -A` away from being published |
| same pair, in build metadata | `images/<profile>/<hash>/build.metadata.json` (`firmware-manager.py:420,431`) | 0644/0664 (umask) | controller disk | n/a | if `images/` is ever copied/shared |
| PIA account password in Ansible run | `raw` heredoc → controller + device argv (`tasks/main.yml:28-33`) | n/a | process table / logs | no | see env/argv audit |
| TLS trust anchor | `/etc/openvpn/ca.rsa.4096.crt` (`openvpn_pia.py:333`, `tasks/main.yml:25`) | 0644 (public cert) | persistent overlay | yes | re-downloaded unverified each run |

`/tmp/pia*` state (`openvpn_pia.py:72`, `pia-watchdog:4-5`) is RAM-only and holds no
credentials — that part is correct.

## Findings

### CP-1 (HIGH) — the PIA password is uploaded to a third-party build server and baked into the image

`openvpn-pia` registers with the default `configure_via` of `"both"`
(`use_cases/__init__.py:48`; the `register(...)` call at `openvpn_pia.py:466-511` does not
override it). That makes the credential script eligible for the **first-boot** channel:

- `profile/builder.py:146-156` (`_firstboot_for_mode`) returns the configure script for
  `configure_via in ("firstboot", "both")` when `mode in ("asu_build", "preview")`.
- `profile/builder.py:462` sets `include_in_asu=bool(fb or pkgs)` → `True` because the
  credential script is non-empty.
- `profile/plan.py:81-89` (`asu_defaults_script`) concatenates every step's
  `firstboot_script` into one payload.
- `firmware-manager.py:206-207` takes that payload; `:283` puts it into the build request
  (`build_request["defaults"] = defaults_script`); `:286` POSTs it to
  `ASU_BUILD_URL`, i.e. `ASU_BASE = "https://sysupgrade.openwrt.org"` (`:37`).
- `firmware-manager.py:420` also stores it verbatim in the local metadata JSON (`:431`).

Consequently, at `ec5c60d9` a user who enables `openvpn-pia` and builds via ASU ships
their PIA account password to a third party, into the image's `/etc/uci-defaults`, into
the built `.bin`, and into the controller's metadata file. The credential is then
persisted in a firmware file that is uploaded/flashed and archived.

**Actionable fix (pick one, minimal first):**
1. Set `configure_via="ssh"` on the `openvpn-pia` use case so credentials can never enter a
   first-boot/ASU payload. Cheapest, honest, and matches the stated posture (the module is
   documented as an SSH-applied use case).
2. Add an explicit secret declaration to the DSL — e.g. `ParamDef(secret=True)` or a
   `CredentialSpec(path=..., mode=...)` — and have `builder.py`+`plan.py` **refuse**
   `asu_build`/`preview` when a secret param would enter `asu_defaults_script()` unless the
   operator passes an explicit `--allow-secrets-in-image`.
3. Until then, make `print_plan`/`asu_defaults_script` print a loud warning when a defaults
   payload contains a `credential`-class WriteFile.

### CP-2 (HIGH) — controller-side plaintext: `config.toml` is not actually gitignored, and the raw defaults land in build metadata

The only supported way to fill the use case's required params is the conwrt config file
(`config.py:291-299` reads `[use_cases.<name>]`), and `config.example.toml:3` tells the
user:

```
# config.toml is gitignored — your keys and passwords stay local.
```

That is false at `ec5c60d9`. `.gitignore` (32 lines) contains no `config.toml` entry and
no `**/config.toml` pattern, and `git check-ignore -v config.toml` exits **1** (not
ignored). So the documented home for `password = "..."` sits untracked-but-unignored in the
repo working tree: one `git add -A` publishes a live VPN account password, on a repo that
is mirrored to GitHub and ngit.

Second copy, same class: `firmware-manager.py:420` writes `"defaults": defaults_script`
into `images/<profile>/<hash>/build.metadata.json` (`:431`), i.e. the plaintext credential
again, in a file with no explicit mode (observed 0644 with umask 022, 0664 with umask 002).
The metadata already records `defaults_lines` (`:228`) — enough for cache identity; the raw
content is not needed.

**Actionable fix:**
- Add `config.toml` to `.gitignore` (one line) — this is arguably a pre-existing bug, but
  PR #55 is the first use case that makes `config.toml` a *credential* store, so it is in
  scope here. Same for any `*.vault.yml`/inventory file the docs suggest.
- Replace the raw `defaults` in build metadata with `defaults_sha256` (+ `defaults_lines`),
  or write the metadata with an explicit `0600`.
- Add a pre-commit/secret-scan guard for a `password =` line inside a `[use_cases.*]`
  section (the repo already has secret-detection hooks on another branch —
  `fix/passwd-not-chpasswd`).

### CP-3 (MEDIUM) — `chmod 600` is applied *after* the file exists: race + abort window, persistent when it loses

`ops.py:183-195` renders a credential write as:

```sh
cat > '/etc/openvpn/pia-auth.txt' <<'OPENWRT_EOF'
p1234567
s3cret
OPENWRT_EOF
chmod 600 /etc/openvpn/pia-auth.txt
```

The file is created by `cat` **before** `chmod` runs. The mode on disk during that window is
whatever the shell's umask allows — on a stock OpenWrt/dropbear shell that is `022`, so the
file is momentarily `-rw-r--r--` (world-readable), and if the connection/script dies between
the two statements it stays that way **permanently** in `/etc` (i.e. across every reboot).
`apply.py:107-118` sends such scripts through `ssh sh -s` with `set -e`, so an abort in
that window is a realistic outcome, not a theoretical one: the credential file is written
inside a step that continues with a dozen more operations.

Reproduced locally (exact rendered snippet, umask 022):

```
-rw-r--r-- 1 user user 16 demo-auth.txt     # after the heredoc, before chmod
-rw------- 1 user user 16 demo-auth.txt     # after chmod 600
```

The same ordering is used by the Ansible role (`tasks/main.yml:28-33` for
`pia-auth.txt`, `:36-40` for `pia.ovpn`, `:117-126` for `/etc/config/pia`), where the
`chmod` is a separate `raw` task line that never runs if the play aborts mid-block.

**Actionable fix (in `render_writefile`, one line):**
```sh
umask 077
cat > '/etc/openvpn/pia-auth.txt' <<'OPENWRT_EOF'
...
OPENWRT_EOF
chmod 600 /etc/openvpn/pia-auth.txt
```
or, better, `install -m 600 /dev/stdin '/etc/openvpn/pia-auth.txt' <<'OPENWRT_EOF'`
(BusyBox `install` supports `-m`), or write `path.tmp` → `chmod` → `mv`. Apply the same
`umask 077` prefix to the three Ansible `raw` blocks.

**Test gap that will block the fix:** `tests/test_ops_writefile.py:23` asserts the exact
rendered string (`cat > ...\nhello\nOPENWRT_EOF\nchmod 600 /tmp/x`) and
`tests/test_openvpn_pia_ops.py:41-46` asserts only that *some* `chmod 600` line exists —
neither asserts ordering or umask, so the insecure shape is currently pinned as "spec".
Update both to assert the mode-setting statement **precedes** content creation.

### CP-4 (MEDIUM) — no removal or rotation path; the documented rollback keeps the credential

- There is no teardown/rollback op anywhere in the use case (`openvpn_pia.py:326-463` builds
  only "apply" ops) — nothing ever deletes `/etc/openvpn/pia-auth.txt` or the OVPN profile.
- `docs/vpn-setup-library.md:67` claims the shared model gives *"Reversibility — always back
  up the configs and provide a one-shot rollback"*, and `ansible/README.md:15` repeats it
  (*"Configuration steps keep a known-good backup"*). No backup or rollback code exists in
  the PR: `grep -rn "vpnbak\|rollback" ` matches **only** the README sentence below.
- `ansible/roles/pia_openvpn/README.md:63-72` ("Rollback") instructs `uci set
  openvpn.pia.enabled=0` + `uci commit openvpn`, then references *"`/root/vpnbak`"* — a path
  that appears nowhere in the repository. Following it removes the tunnel wiring while
  leaving the plaintext PIA password on the device indefinitely.

This matters for persistence specifically: a PIA password is account-wide, cannot be scoped
per device, and the only way to invalidate it after a router is sold/re-flashed/handed over
is the provider's account panel. The absence of a device-side removal step means the
credential outlives the reason it was written.

**Actionable fix:**
- Add a `build_rollback_ops`/teardown for the use case: `rm -f /etc/openvpn/pia-auth.txt
  /etc/openvpn/pia.ovpn /etc/openvpn/ca.rsa.4096.crt` + `uci set openvpn.pia.enabled=0`
  (this is what the README's "disable" already does, plus the secret removal).
- Fix the README: either implement `/root/vpnbak` or delete the sentence; state explicitly
  that disabling the tunnel does **not** erase the stored credential, and give the rotation
  command (re-run the use case with a new password, then rotate in the PIA panel).
- Consider a `secret_lifetime`/`rotate_after` field on the credential spec so operators are
  prompted.

### CP-5 (MEDIUM) — `/etc` backups pull the credential off the device

Once `/etc/openvpn/pia-auth.txt` exists, every whole-`/etc` capture collects it. In-tree
today: `scripts/fieldlab/forensics_cmd.py:191-197` runs `tar czf /tmp/etc-backup.tar.gz /etc`
on the router and `scp`s the tarball to the controller as
`<device-dir>/<mac>.tar.gz`, then deletes only the device-side copy. Stock
`sysupgrade -b backup.tar.gz` (and any "back up my router before flashing" instruction,
which this repo's own workflows encourage) has the same effect. PR #55 adds no exclusion.

**Actionable fix:**
- Give the credential a machine-readable path list (`CredentialSpec.paths`) and have
  tooling that tars `/etc` (fieldlab forensics, backups, `sysupgrade -b` helpers) filter
  those paths out, or pack only the explicit allow-list (`/etc/config/*`, not `/etc/*`).
- Document the required `/etc/sysupgrade.conf` exclusion (`- /etc/openvpn/pia-auth.txt`) in
  the role README and the use-case notes, next to the existing backup guidance.

### CP-6 (MEDIUM) — the trust anchor is fetched unverified and re-fetched every run

`openvpn_pia.py:333` renders `wget -q -O /etc/openvpn/ca.rsa.4096.crt '<ca_url>'` with
`DEFAULT_CA_URL` pointing at `raw.githubusercontent.com` (`pia-foss/manual-connections`),
and `ansible/roles/pia_openvpn/tasks/main.yml:25` does the same. There is no sha256 pin and
no verification step before the file is wired into `pia.ovpn` as `ca`
(`openvpn_pia.py:292`).

`wget -q` on a stock OpenWrt image depends on `ca-bundle` being present for TLS validation
(`openvpn-openssl` does not necessarily pull it); if it is missing, BusyBox `wget` either
fails or the fetch is unauthenticated depending on the build. Either way PR #55 does not
verify what it downloaded. A substituted CA file means the client accepts an attacker's
OpenVPN server, and the `auth-user-pass` credentials are then handed to it — the password
is disclosed and persisted at the attacker.

**Actionable fix:**
- Pin the expected digest (`sha256`) of `ca.rsa.4096.crt` as a constant and verify with
  `sha256sum -c` (BusyBox `sha256sum` is guaranteed per `AGENTS.md`) before configuring, or
  ship the CA in-tree and only allow a URL override with an explicit digest.
- Fail loudly if the CA file is missing/unchanged-and-unverified; do not proceed to write
  the credential file first (order the ops: CA verified → then credentials).

### CP-7 (LOW) — `WriteFile` does not create or secure the parent directory

`openvpn_pia.py:331` writes `/etc/openvpn/pia-auth.txt` assuming the directory exists (it
comes from the `openvpn-openssl` package) with no `mkdir`/mode assertion. If the directory
is missing the step fails loudly (acceptable), but the DSL has no way to express "this
directory is a secret store" either: nothing enforces `0700` on it, and no check confirms
the path is not a symlink to a world-readable location (`ops.py:158-163` validates only
absolute-ness and characters).

**Actionable fix:** add a `CreateDir(path, mode="700")` op (or auto-emit `mkdir -p -m 700`
+ `[ ! -L path ]` guard inside `render_writefile` for credential-class paths) so the
secret's parent is created with explicit permissions.

### CP-8 (LOW) — the provider-agnostic model has nowhere to record at-rest facts

`docs/vpn-setup-library.md:20-26` is the design core of the PR: a `CredentialSpec` per login
method with a "What OpenWrt stores" column. For `username_password` it says
`auth-user-pass file (mode 600)` (`:22`) — correct for the file, silent on the fact that it
is plaintext on the overlay, survives reboots, is included in `/etc` backups, and can be
baked into an ASU image. The `token`, `api_key`, `keypair` and `oauth_device` rows (`:23-26`)
give no at-rest detail at all, yet the model is meant to be reused for providers whose
tokens are long-lived (Mullvad account key, IVPN account number).

**Actionable fix:** extend the model with the missing fields and make them mandatory for any
use case that writes a secret:

| field | purpose |
|-------|---------|
| `paths` | exact files/dirs holding the secret (used by backup/forensics exclusion) |
| `mode` / `owner` | as today, but enforced, not just documented |
| `lifetime` | operator-visible retention; drives rotation prompts |
| `teardown` | op list that removes the secret |
| `backup_policy` | `exclude` / `include` — so `/etc` captures are explicit, not accidental |

Then update the table's `username_password` row to say "plaintext `auth-user-pass` file on
the persistent overlay (mode 600 after write; survives reboot, sysupgrade backup and — if
enabled — ASU image build)".

## Keychain integration

There is no keychain, TPM, Bunker or OS-keyring integration in PR #55, and none is
realistically available on the target (stock OpenWrt, BusyBox, no `libsecret`, no
`gpg-agent` by default, no TPM driver assumed). So "improper keychain integration" is not
the failure mode here — the honest options are:

1. **Accept root-only plaintext at rest**, and make the consequences explicit: exact path,
   mode, reboot survival, backup/image exposure, removal procedure. That is the current
   *behaviour*, but it is not the current *documentation* — CP-1/CP-2/CP-4/CP-8 fix that.
2. **Per-boot tmpfs provisioning** (`/tmp/openvpn/auth`) written by an operator-held secret
   injected over SSH at connect time (creds never on the overlay). Viable for the Ansible
   path and for a future "operator secret store" mode, but it needs a reconnect hook so the
   tunnel survives watchdog restarts — more moving parts, and it trades reboot-survival for
   at-rest exposure.
3. **Encrypted-at-rest is not worth it here**: anything that decrypts unattended needs the
   key on the same device, so it adds ceremony without changing the trust boundary.

Recommendation: ship option 1 with the documentation and lifecycle gaps closed (CP-4/CP-5/
CP-8), and treat option 2 as an explicit opt-in mode for the "enforced" posture.

## What is done right

- `mode 600` is specified on every credential/write artifact, including the OVPN profile
  (no secrets inside) and `/etc/config/pia`.
- `auth-nocache` (`openvpn_pia.py:287`) keeps the password out of long-lived process memory,
  and `persist-key` (`:278`) avoids re-reading keys on `SIGUSR1`; the password is re-read
  from the file only on (re)connect — the correct pairing for a file-based credential.
- Watchdog state and logs stay in `/tmp` (`:72`, `pia-watchdog:4-5`), i.e. RAM-only.
- The Ansible credential task carries `no_log: true` (`tasks/main.yml:33`), so the password
  never enters Ansible output.
- `runs/` and `images/` are gitignored (`.gitignore`), so the run-dir reproduction paths do
  not publish anything — the leak surface is `config.toml` and the ASU payload, not the run
  dirs.

## Reproduction

All commands run in the PR-head worktree at `ec5c60d9` (`/home/c03rad0r/worktrees/t_a1c8c7ee/pr55`).

1. `config.toml` ignore status:
   ```
   $ git check-ignore -v config.toml ; echo "rc=$?"
   rc=1                     # not ignored, while config.example.toml:3 claims it is
   ```
2. Credential in the ASU defaults payload (offline, no build submitted) — a minimal config
   enabling the use case, then `build_plan(..., mode="asu_build")`:
   ```
   ASU defaults script: 300 lines
   plaintext password 's3cret' inside ASU payload: True
   plaintext username 'p1234567' inside ASU payload: True
   --- credential-bearing lines in the ASU defaults payload ---
       cat > '/etc/openvpn/pia-auth.txt' <<'OPENWRT_EOF'
       p1234567
       s3cret
       chmod 600 /etc/openvpn/pia-auth.txt
   ```
   Same payload is what `firmware-manager.py:283` assigns to `build_request["defaults"]`
   and `:286` POSTs to `https://sysupgrade.openwrt.org`.
3. Write-then-chmod window (umask 022, exact rendered snippet from `ops.py:191-195`):
   ```
   -rw-r--r-- ... demo-auth.txt    # after `cat`, before `chmod`
   -rw------- ... demo-auth.txt    # after `chmod 600`
   ```
4. Metadata mode: `write_text` with no explicit mode → `0o664` (umask 002), `0o644`
   (umask 022) — `firmware-manager.py:431`.
5. `/root/vpnbak`:
   ```
   $ grep -rn "vpnbak" . | grep -v '^./.git'
   ./ansible/roles/pia_openvpn/README.md:65:The role keeps the previous UCI files in `/root/vpnbak` ...
   ```
   (documentation only — nothing creates it).

## Prioritised recommendations

1. **Block credentials from the ASU/first-boot path** (`configure_via="ssh"` now; a
   secret-aware builder gate properly) — CP-1.
2. **Add `config.toml` to `.gitignore`; stop storing raw defaults in build metadata** — CP-2.
3. **`umask 077` (or `install -m 600`) in `render_writefile` and the three Ansible writes;
   fix the two tests that pin the insecure ordering** — CP-3.
4. **Add a teardown/rotation path and correct the rollback docs** (remove the `/root/vpnbak`
   claim or implement it; state that disabling the tunnel does not erase the credential) — CP-4.
5. **Exclude credential paths from `/etc` backups/forensics; document the `sysupgrade.conf`
   exclusion** — CP-5.
6. **Pin the CA digest before writing any credential** — CP-6.
7. **Extend `CredentialSpec` with paths/lifetime/teardown/backup policy and fill the design
   table** — CP-7, CP-8.

## Verdict

**Request changes.** The on-device `600` intent is right and consistently written, and the
OpenVPN-side credential handling (`auth-nocache` + file-based `auth-user-pass`) is the
correct pattern for this platform. But at `ec5c60d9` the same plaintext is (a) uploaded to a
third-party build service and baked into firmware when the ASU path is used, (b) left
unignored in `config.toml` and copied into build metadata on the controller, (c) briefly —
or permanently, if the step aborts — world-readable on the device, and (d) never removed,
even by the documented rollback. Fix CP-1 and CP-2 before merge; CP-3/CP-4/CP-5 are
small follow-ups in the same PR.
