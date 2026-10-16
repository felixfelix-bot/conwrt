# provenance-verification.md — independent audit of the LAN-move provenance verdicts

Auditor: manager (kanban t_a27f30d9). Method: the ground-truth bundle was decoded and quoted
**before** either worker note was read; the notes were then treated as claims only.

## 0. Ground truth, revisions, and what "checked-out" means here

Two revisions of the same file were inspected. This matters, because the two notes were written
against one of them and the card's `docs/wizard-bundle.json` resolves to the other.

| Ref | Revision | git blob | sha256 | bytes | JSON anchors (LAN-move region) |
|-----|----------|----------|--------|-------|-------------------------------|
| **A — checked-out bundle** (`docs/wizard-bundle.json` on `pr-55` @ `4f169a2`, PR #55 evidence checkout, in `/home/c03rad0r/repos/conwrt`) | `pr-55:docs/wizard-bundle.json` | `671492ed0e64cf0d0a96701a4643afbfe553a957` | `3b1f047be5e7495f75c3af42c86bcfba2d3e0491ddf17f5ec670600d8ed25f39` | 619242 | `net4sats` shell line **366**, `tollgate` shell line **372** |
| **B — note-time bundle** (`git master:docs/wizard-bundle.json`; the tree the two notes were authored against — both notes exist only on local `master`, commits `4eed9f4` / `117e56a`) | `master:docs/wizard-bundle.json` | `e2d8fd7afcfabee5d87c966e6feaa301f5d66ea5` | `6fe93f952fe68a53facd7d0a3561865377ccdd15beb3801cb4432b23a507277e` | 614953 | `net4sats` shell line **352**, `tollgate` shell line **358** |

Verdicts below are stated per revision so the note claims can be adjudicated against the tree they
audited **and** against the file the card names. Verdict scale for this audit:
`DERIVED-VALUE / FAIL-CLOSED` (consumes the identity-derived `lan_ip` binding; refuses to run on an
unfilled placeholder), `FALLS-BACK-TO-LITERAL` (bakes an address, no guard), `READ-BACK: PRESENT /
ABSENT`.

Mechanical facts about the checked-out bundle (A), counted, not paraphrased:
86 rendered recipes (21 models × 2 flows × 2 versions + CF-WR632AX × 2 flows × 1 version);
**84 write a literal IP**, **2 use the `{{lan_ip}}` placeholder with a guard**, **2 contain a
read-back**. Both non-conforming recipes are CF-WR632AX (the issue-#32 device under test).

---

## 1. Flow: `net4sats`

**Key paths inspected**
- `$.rendered["comfast-cf-wr632ax"]["net4sats"]["25.12.4"].shell` — docs/wizard-bundle.json JSON line 366 (checked-out bundle A)
- `$.rendered["comfast-cf-wr632ax"]["net4sats"]["25.12.4"].shell` — master JSON line 352 (note-time bundle B)
- `$.flows[0].params.lan_ip` — JSON line 289 (A); absent from B (no `lan_ip` entry anywhere in B's bundle)

**Verbatim evidence — A (checked-out), JSON line 366, escaped exactly as the JSON stores it**

```
# --- Move the LAN off 192.168.1.1 ---\nssh root@$IP sh <<'CONWRT_EOF'\n# move LAN off 192.168.1.1 \u2192 identity-derived CGNAT address (100.64.0.0/10)\nLAN_IP='{{lan_ip}}'\ncase \"$LAN_IP\" in \"\"|*\"{\"*) echo \"ERROR: lan_ip was not filled in. Derive this device's CGNAT LAN address:\" ; echo \"  python3 scripts/derive_device_secret.py --mnemonic <fleet> --mac <mac>   (ipv4 field)\" >&2 ; exit 1;; esac\nuci set network.lan.ipaddr=\"$LAN_IP\"\nuci set network.lan.netmask='255.255.255.0'\nuci get network.lan.ipaddr | grep -qxF \"$LAN_IP\" || { echo 'ERROR: uci read-back mismatch for network.lan.ipaddr' >&2 ; exit 1 ; }\nuci commit network\n(/etc/init.d/network restart &) ; echo \"LAN moving to $LAN_IP \u2014 reconnect on that subnet\"\nCONWRT_EOF\n
```

The binding the value comes from, `$.flows[0].params.lan_ip` (JSON line 289, decoded):
`"lan_ip": { "type": "string", "required": false, ... "description": "Identity-derived CGNAT LAN address for this device (100.64.0.0/10). Run `python3 scripts/derive_device_secret.py --mnemonic <fleet> --mac <mac>` and use its `ipv4` field ..."`.

**Verbatim evidence — B (note-time), JSON line 352, escaped exactly**

```
# --- Move the LAN off 192.168.1.1 ---\nssh root@$IP sh <<'CONWRT_EOF'\n# move LAN off 192.168.1.1 \u2192 192.168.1.1 (192.168.1.0/24)\nuci set network.lan.ipaddr='192.168.1.1'\nuci set network.lan.netmask='255.255.255.0'\nuci commit network\n(/etc/init.d/network restart &) ; echo 'LAN moving to 192.168.1.1 \u2014 reconnect on that subnet'\nCONWRT_EOF\n
```

**Verdicts**

- **LAN-move, bundle A (checked-out): CORRECTED.** My read of A does not support the note's
  checked-out-bundle verdict; the block consumes the flow param and is guarded.
- **Read-back, bundle A: CORRECTED.** A does contain a read-back in this recipe.
- **LAN-move, bundle B: CONFIRMED.** The note's `State A` description of the note-time bundle is
  exactly right.
- **Read-back, bundle B: CONFIRMED (ABSENT).** 0 of 86 recipes in B contain `uci get network.lan.ipaddr`.

```
CORRECTION: LAN-move "FALLS BACK TO LITERAL" (checked-out docs/wizard-bundle.json) -> "DERIVED VALUE, FAIL-CLOSED — consumes the lan_ip binding via LAN_IP='{{lan_ip}}' and exits 1 before any write when empty/placeholder; no literal fallback exists"
  key path: $.rendered["comfast-cf-wr632ax"]["net4sats"]["25.12.4"].shell  (docs/wizard-bundle.json line 366, sha256 3b1f047b…)
  evidence: "LAN_IP='{{lan_ip}}'\ncase \"$LAN_IP\" in \"\"|*\"{\"*) … exit 1;; esac\nuci set network.lan.ipaddr=\"$LAN_IP\""
            $.flows[0].params.lan_ip (line 289): "use its `ipv4` field"

CORRECTION: read-back "the fenced block above is intentionally empty: State A emits no read-back … Nothing confirms the value landed" (checked-out bundle) -> "READ-BACK PRESENT in this recipe"
  key path: $.rendered["comfast-cf-wr632ax"]["net4sats"]["25.12.4"].shell  (line 366)
  evidence: "uci get network.lan.ipaddr | grep -qxF \"$LAN_IP\" || { echo 'ERROR: uci read-back mismatch for network.lan.ipaddr' >&2 ; exit 1 ; }"

CORRECTION: "State B … is NOT what the checked-out docs/wizard-bundle.json contains" -> "the checked-out bundle DOES contain State B for the CF-WR632AX recipes (both flows)"
  key path: $.rendered["comfast-cf-wr632ax"]["net4sats"]["25.12.4"].shell  (line 366)
  evidence: the LAN-move region above is byte-identical to the current renderer's identity output:
            scripts/flows/render.py:166-184 (`_identity_lan_ops`, placeholder mode) reproduces it verbatim
            (verified by regeneration — see §3).

CONFIRMED: LAN-move "FALLS BACK TO LITERAL … 192.168.1.1 … silent no-op" for the note-time bundle
  key path: $.rendered["comfast-cf-wr632ax"]["net4sats"]["25.12.4"].shell  (master, line 352, sha256 6fe93f95…)
  evidence: "uci set network.lan.ipaddr='192.168.1.1'" + "# move LAN off 192.168.1.1 \u2192 192.168.1.1 (192.168.1.0/24)"

CONFIRMED: read-back ABSENT in the note-time bundle
  evidence: 0 of 86 recipes in master:docs/wizard-bundle.json match "uci get network.lan.ipaddr"

CONFIRMED: note caveat (a) — "only the two CF-WR632AX recipes were re-rendered …; the other models'
entries … still carry the old-style literal block with no guard and no read-back"
  evidence: committed bundle A — 84/86 recipes match "uci set network.lan.ipaddr='<literal>'" and 0 of those 84 contain a read-back.
```

---

## 2. Flow: `tollgate`

**Key paths inspected**
- `$.rendered["comfast-cf-wr632ax"]["tollgate"]["25.12.4"].shell` — JSON line 372 (checked-out bundle A)
- `$.rendered["comfast-cf-wr632ax"]["tollgate"]["25.12.4"].shell` — master JSON line 358 (note-time bundle B)
- `$.flows[1].params.lan_ip` — JSON line 326 (A); absent from B

**Verbatim evidence — A (checked-out), JSON line 372, escaped exactly**

```
# --- Move the LAN off 192.168.1.1 ---\nssh root@$IP sh <<'CONWRT_EOF'\n# move LAN off 192.168.1.1 \u2192 identity-derived CGNAT address (100.64.0.0/10)\nLAN_IP='{{lan_ip}}'\ncase \"$LAN_IP\" in \"\"|*\"{\"*) echo \"ERROR: lan_ip was not filled in. Derive this device's CGNAT LAN address:\" ; echo \"  python3 scripts/derive_device_secret.py --mnemonic <fleet> --mac <mac>   (ipv4 field)\" >&2 ; exit 1;; esac\nuci set network.lan.ipaddr=\"$LAN_IP\"\nuci set network.lan.netmask='255.255.255.0'\nuci get network.lan.ipaddr | grep -qxF \"$LAN_IP\" || { echo 'ERROR: uci read-back mismatch for network.lan.ipaddr' >&2 ; exit 1 ; }\nuci commit network\n(/etc/init.d/network restart &) ; echo \"LAN moving to $LAN_IP \u2014 reconnect on that subnet\"\nCONWRT_EOF\n
```

`$.flows[1].params.lan_ip` exists at JSON line 326 with the same `derive_device_secret.py` / `ipv4`
description as `flows[0]` (decoded line 329 is that description string).

**Verbatim evidence — B (note-time), JSON line 358, escaped exactly**

```
# --- Move the LAN off 192.168.1.1 ---\nssh root@$IP sh <<'CONWRT_EOF'\n# move LAN off 192.168.1.1 \u2192 192.168.1.1 (192.168.1.0/24)\nuci set network.lan.ipaddr='192.168.1.1'\nuci set network.lan.netmask='255.255.255.0'\nuci commit network\n(/etc/init.d/network restart &) ; echo 'LAN moving to 192.168.1.1 \u2014 reconnect on that subnet'\nCONWRT_EOF\n
```

**Verdicts**

- **LAN-move, bundle A (checked-out): CORRECTED.** Guarded placeholder path, not a literal.
- **Read-back, bundle A: CORRECTED.** Present in this recipe (and only in this one plus the net4sats twin).
- **LAN-move, bundle B: CONFIRMED** (literal `192.168.1.1`, silent no-op for this model).
- **Read-back, bundle B: CONFIRMED (ABSENT).**

```
CORRECTION: LAN-move "FALLS BACK TO LITERAL" (checked-out docs/wizard-bundle.json) -> "DERIVED VALUE, FAIL-CLOSED"
  key path: $.rendered["comfast-cf-wr632ax"]["tollgate"]["25.12.4"].shell  (docs/wizard-bundle.json line 372)
  evidence: "LAN_IP='{{lan_ip}}'\ncase \"$LAN_IP\" in \"\"|*\"{\"*) … exit 1;; esac\nuci set network.lan.ipaddr=\"$LAN_IP\""

CORRECTION: read-back "The tollgate recipe contains **no read-back block**." / "no `ubus` call anywhere after the LAN-move (or before it) in any of the 22 models' tollgate recipes" (checked-out bundle) -> "READ-BACK PRESENT in this recipe"
  key path: $.rendered["comfast-cf-wr632ax"]["tollgate"]["25.12.4"].shell  (line 372)
  evidence: "uci get network.lan.ipaddr | grep -qxF \"$LAN_IP\" || { echo 'ERROR: uci read-back mismatch for network.lan.ipaddr' >&2 ; exit 1 ; }"

CORRECTION: "There is no lan_ip param, so no {{lan_ip}} template can exist for the wizard to fill" -> "flows[1].params.lan_ip exists and the {{lan_ip}} template IS emitted in the tollgate shell"
  key path: $.flows[1].params.lan_ip (line 326) and $.rendered["comfast-cf-wr632ax"]["tollgate"]["25.12.4"].shell (line 372)
  evidence: line 326 "lan_ip": { … "description": "Identity-derived CGNAT LAN address for this device (100.64.0.0/10). Run `python3 scripts/derive_device_secret.py …` and use its `ipv4` field …"
            line 372 "LAN_IP='{{lan_ip}}'"

CORRECTION: "scripts/derive_device_secret.py does not exist anywhere in the repo (full-tree search, no matches)" -> "the file exists in the checked-out tree"
  key path: scripts/derive_device_secret.py (repo tree, not the bundle)
  evidence: scripts/derive_device_secret.py:93-94  def derive_ipv4(pub_key_hex): h = _derive_hash("tollgate-ipv4-v1:", pub_key_hex); return f"100.{64 + h[0] % 64}.{h[1]}.1"
            scripts/derive_device_secret.py:126  "ipv4": derive_ipv4(pub_x_hex),
            (the "no matches" search was valid for the note-time tree: `git cat-file -e master:scripts/derive_device_secret.py` -> missing on master)

CONFIRMED: LAN-move literal + "silent no-op" for the note-time bundle
  key path: $.rendered["comfast-cf-wr632ax"]["tollgate"]["25.12.4"].shell  (master, line 358)
  evidence: "uci set network.lan.ipaddr='192.168.1.1'"

CONFIRMED: no read-back in the note-time bundle, for tollgate or anywhere
  evidence: 0 of 86 master recipes contain "uci get network.lan.ipaddr"
```

---

## 3. What the 84 literal recipes actually contain (both flows, provenance check)

Rule applied from the card: `UNSAFE` if the LAN-move uses a hardcoded literal IP, an unresolved
placeholder, a stale copy/paste, or an absent binding.

- **84 of 86 recipes (all models except CF-WR632AX, both flows, both versions) are UNSAFE by that
  rule**: they emit `uci set network.lan.ipaddr='<literal>'` and then `uci commit network` with **no
  read-back**. Example key path `$.rendered["asus-lyra-map-ac2200"]["net4sats"]["24.10.7"].shell`, line 330:
  `uci set network.lan.ipaddr='10.231.9.1'`, preceded by `# move LAN off 192.168.1.1 \u2192 10.231.9.1 (10.231.9.0/24)`.
- **They are not stale copy/paste, though.** Each literal equals `network_address + 1` of that
  model's own `lan_subnet`: verified 84/84, e.g. `models/asus-lyra-map-ac2200.json` `"lan_subnet": "10.231.9.0/24"`
  -> `10.231.9.1`; `models/ubnt-edgerouter-x.json` -> `10.78.162.1`; no two models share a subnet
  (0 duplicate subnets across 23 model files). Derivation site: `scripts/profile/target.py:156-161`
  (`lan_gateway = str(net.network_address + 1)`), consumed by `scripts/flows/render.py:208-225`.
  So the literal is a generation-time constant of the *model table*, not of the device identity.
- **The residual silent-no-op risk is closed only for CF-WR632AX.** In the note-time tree that model
  carried `models/comfast-cf-wr632ax.json:3 "lan_subnet": "192.168.1.0/24"`, which equals its
  `default_ip`, i.e. gateway == default ⇒ the "move" re-set the address the device already had. In the
  checked-out tree that key is gone (grep for `lan_subnet` in `models/comfast-cf-wr632ax.json` → no
  match), and `scripts/flows/render.py:210-216` then emits a *skip* comment naming the derivation
  command instead of moving the LAN at all — so a CLI render can no longer reproduce the no-op.

**Regeneration does not reproduce the checked-out bundle (recorded command + result).**
`python3 scripts/generate_site.py <tmp>/regen-bundle.json` in the checked-out tree (sha256 of output
`7a537f83a561a7cc443b47b1de2d73efd7ffd553641dbc3846fc479b54e91486`) printed
`23 models × 2 flows = 46 rendered`, emitted version keys `['24','25']` (committed: `['24.10.7','25.12.4']`),
23 models (committed: 22), and **92 recipes with the read-back** (committed: 2) — in the regenerated
output *every* model takes the guarded placeholder path, e.g.
`$.rendered["asus-lyra-map-ac2200"]["net4sats"]["25"].shell`:
`LAN_IP='{{lan_ip}}'` / `case "$LAN_IP" in ""|*"{"*) … exit 1;; esac` / `uci get network.lan.ipaddr | grep -qxF "$LAN_IP" || … exit 1`.
Byte-level comparison of the committed bundle against `master`'s: **84 of 86 shell strings identical;
only `$.rendered["comfast-cf-wr632ax"]["net4sats"]["25.12.4"].shell` and
`$.rendered["comfast-cf-wr632ax"]["tollgate"]["25.12.4"].shell` differ.** Conclusion: the checked-out
bundle is a hybrid — the two CF-WR632AX recipes carry current-renderer output (verified byte-identical
to `_identity_lan_ops` placeholder output), the other 84 are master-era output retained verbatim.

---

## 4. Summary

For the issue-#32 device under test (CF-WR632AX) **neither flow risks a silent fallback** in the
checked-out `docs/wizard-bundle.json`: `$.rendered["comfast-cf-wr632ax"]["net4sats"]["25.12.4"].shell`
(line 366) and `$.rendered["comfast-cf-wr632ax"]["tollgate"]["25.12.4"].shell` (line 372) both bind
`LAN_IP='{{lan_ip}}'` from `$.flows[0].params.lan_ip` / `$.flows[1].params.lan_ip`, refuse to write
when the value is empty or still brace-delimited (`… exit 1;; esac`), apply exactly the bound variable
(`uci set network.lan.ipaddr="$LAN_IP"`), and read the value back with
`uci get network.lan.ipaddr | grep -qxF "$LAN_IP" || … exit 1` before `uci commit network` — so an
unfilled wizard param aborts loudly instead of falling back to an address. The silent-no-op risk the
two notes describe is real but has moved: it now lives in the **84 other recipes**, whose
`$.rendered["<model>"]["net4sats"|"tollgate"]["24.10.7"|"25.12.4"].shell` still contain
`uci set network.lan.ipaddr='<literal>'` with no guard and no read-back — a generation-time constant
derived from that model's `lan_subnet` (`scripts/profile/target.py:156-161` → `scripts/flows/render.py:208-225`),
not from the device identity, and therefore also not the address the device will actually be given.
The key path responsible for any future silent fallback is
`$.rendered.<model>.<flow>.<version>.shell` → the `uci set network.lan.ipaddr='<IP>'` line inside the
`# --- Move the LAN off 192.168.1.1 ---` heredoc; regenerating with the checked-out renderer rewrites
all of those to the guarded placeholder form (see §3), which is what a full, un-stale bundle
regeneration would fix.
