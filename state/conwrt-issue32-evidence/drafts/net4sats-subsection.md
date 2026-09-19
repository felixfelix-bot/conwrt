### net4sats LAN-move

**Recipe (b):** `docs/wizard-bundle.json -> $.rendered["asus-lyra-map-ac2200"]["net4sats"]["24.10.7"].shell` — JSON physical file line **330**
(a single-line JSON string; the sibling rendered variant `.markdown` is JSON physical file
line **331**). Source of record: conwrt @ HEAD `6415f213916881a9669435130f0f39841648db3f`,
`docs/wizard-bundle.json` sha256 `6fe93f952fe68a53facd7d0a3561865377ccdd15beb3801cb4432b23a507277e` (unmodified by this draft).

**LAN-move block (c.1) — verbatim, `$.rendered["asus-lyra-map-ac2200"]["net4sats"]["24.10.7"].shell`, shell-string lines 65-72 of 73 (the last
section emitted):**

```sh
# --- Move the LAN off 192.168.1.1 ---
ssh root@$IP sh <<'CONWRT_EOF'
# move LAN off 192.168.1.1 → 10.231.9.1 (10.231.9.0/24)
uci set network.lan.ipaddr='10.231.9.1'
uci set network.lan.netmask='255.255.255.0'
uci commit network
(/etc/init.d/network restart &) ; echo 'LAN moving to 10.231.9.1 — reconnect on that subnet'
CONWRT_EOF
```

**Read-back block (c.2) — verbatim, same key path: no read-back block exists (0 lines, 0 bytes;
there is nothing to quote):**

```text
(none — the recipe emits no read-back command)
```

Read-back absence evidence (counts over the parsed bundle, all 86 rendered
`rendered.<model>.<flow>.<version>` entries, `.shell` + `.markdown` = 172 strings): `uci get` 0,
`uci show` 0, `ip addr` 0, `ifconfig` 0, `ping ` 0, `curl -s` 0, `iw dev` 0, `ubus call` 0. The
generator has no read-back step kind either: `_set_lan_ip_ops()` (`scripts/flows/render.py:130-140`)
emits exactly `Comment` (:136), `UciSet` (:137), `UciCommit` (:138), `ShellCommand` (:139) — writes
plus one human-facing `echo`, no verification step. Commands emitted by the LAN-move block: **4**
(`uci set` x2, `uci commit` x1, network restart + `echo` x1). Commands emitted by the read-back
block: **0**.

**Where the derived ipv4 enters (d):** the token `10.231.9.1` enters the emitted block already
resolved, at `docs/wizard-bundle.json:330` (`$.rendered["asus-lyra-map-ac2200"]["net4sats"]["24.10.7"].shell`, shell-string lines 67, 68 and 71) — not
from `derive_device_secret.py`; it is the computed `lan_gateway`, bound via `models/asus-lyra-map-ac2200.json:13`
(`"lan_subnet": "10.231.9.0/24"`) -> `scripts/profile/target.py:112` -> `scripts/profile/target.py:116-117`
(`lan_gateway = str(net.network_address + 1)`) -> target dict `scripts/profile/target.py:130` ->
variable `gw` at `scripts/flows/render.py:131` -> emitted at `scripts/flows/render.py:136-139` ->
frozen into the bundle by `scripts/generate_site.py:113`.

**Provenance verdict (e):** **consumes a derived value — the derived ipv4 (`lan_gateway`, the
model's `lan_subnet` network address + 1) held in the variable `gw`; it is NOT `derive_device_secret.py`
output (that file does not exist at this HEAD — `git cat-file -e HEAD:scripts/derive_device_secret.py`
-> rc=128), NOT a hardcoded literal (`grep -rn '10.231.9.1' scripts/ models/` = 0 hits; the
`network.lan.ipaddr` token takes 22 distinct values across the 22 rendered models:
`asus-lyra-map-ac2200` -> `10.231.9.1`, `glinet-mt6000` -> `10.230.237.1`, `comfast-cf-wr632ax` ->
`192.168.1.1` (a deliberate no-op move)), and NOT an unresolved `{{lan_ip}}` placeholder (`{{lan_ip}}` count in
`docs/wizard-bundle.json` = 0 at this HEAD; single-braced `{lan_ip}` count = 0).** No silent literal
fallback is possible: the literal `192.168.1.1` occurs in the block only inside fixed comment/echo
prose and as the ssh-target default `IP=${IP:-192.168.1.1}` on shell-string line 6 (not the new LAN
address); if `lan_subnet` is absent or unparseable, `lan_gateway` stays `""` and the recipe emits no
LAN-move commands at all (`scripts/flows/render.py:133-134` -> `Comment("skip LAN move — model has
no lan_subnet defined")`), so the address applied is either the derived one or none — never a
literal.

GAP: `state/conwrt-issue32-evidence/net4sats-lan-move.md` — the primary source cited at
`state/conwrt-issue32-evidence/drafts/net4sats-raw-commands.md:3` — does not exist in this repo's
working tree at this HEAD (confirmed absent; no such path under `state/`), and
`drafts/net4sats-raw-commands.md` is a pure GAP note carrying no command bytes. The LAN-move block
above was therefore re-derived directly from the READ-ONLY `docs/wizard-bundle.json` by slicing the
decoded `$.rendered["asus-lyra-map-ac2200"]["net4sats"]["24.10.7"].shell` string at shell-string lines 65-72 and re-verifying byte-equality against the
file after writing (bundle sha256 unchanged at `6fe93f952fe68a53facd7d0a3561865377ccdd15beb3801cb4432b23a507277e`).

Discrepancy (stated, not silently resolved): `drafts/net4sats-derivation-notes.md:150-155` records
the revision divergence as "at `ec5c60d9` ... **the same slot** ... carries **6** occurrences of the
unresolved `{lan_ip}` placeholder". Re-measured directly on `ec5c60d9:docs/wizard-bundle.json`: that
revision contains **4** occurrences of the placeholder (double-braced `{{lan_ip}}`; the nested
single-braced substring `{lan_ip}` also counts 4), and they sit in the **`comfast-cf-wr632ax` `25.12.4`**
net4sats and tollgate entries — **not** in the `asus-lyra-map-ac2200` `net4sats` `24.10.7` slot, which
at `ec5c60d9` already carries the resolved `10.231.9.1` (that revision's shell-string line 68). Per
the card rule the verbatim block with the cited key path is preferred: `docs/wizard-bundle.json:330`
at HEAD `6415f213916881a9669435130f0f39841648db3f`, where both placeholder spellings count 0.
Placeholder spelling, also not collapsed: the marker is stored double-braced, `{{lan_ip}}` (this
card's wording); the input draft's body writes it single-braced at
`drafts/net4sats-derivation-notes.md:143` and `:153`, while that same task's completion metadata
writes `{{lan_ip}}`; the on-disk byte form at `ec5c60d9` is `{{lan_ip}}`, 4 times.

Discrepancy (stated, not silently resolved): `drafts/net4sats-commands.fragment.md:6-9` quotes the
same four commands against token `10.230.237.1`, i.e. model `glinet-mt6000`, not
`asus-lyra-map-ac2200` (`10.231.9.1`). Both are correct for their own model — the token is per-model
(22 distinct values across 22 models) — so a token is only meaningful when quoted with its model id;
this draft is scoped to `asus-lyra-map-ac2200`, and a reviewer diffing against that fragment will see
an expected, not a real, mismatch.

Citation corrections to the input draft (line numbers re-checked against HEAD; no command bytes
differ): `scripts/profile/target.py` — `lan_subnet` at **:112** (input agrees), the
`ipaddress.ip_network` / `network_address + 1` pair at **:116-117** (input said :114-117, which are
the `if`/`try` lines), returned `"lan_gateway"` entry at **:130** (input agrees);
`scripts/flows/render.py:136-139` emits **four** ops, not the three the input enumerates — the
input's list omits `UciCommit(config="network")` at `:138`. Neither correction changes the verdict.

Not touched: `state/conwrt-issue32-evidence/checklist.md` (owned by a later merge task; absent from
the working tree and neither read nor written by this draft) and `docs/wizard-bundle.json`
(READ-ONLY; sha256 `6fe93f952fe68a53facd7d0a3561865377ccdd15beb3801cb4432b23a507277e`).
