# Provenance verification — LAN-move and read-back, net4sats and tollgate flows

Independent audit. Audited artifact (read-only, byte-unchanged): `/home/c03rad0r/repos/conwrt/docs/wizard-bundle.json`, branch `feat/vpn-provider-setup`, HEAD `70efbbfe72e85f2a525f4c22da12eaddacbd05d7`, sha256 `6fe93f952fe68a53facd7d0a3561865377ccdd15beb3801cb4432b23a507277e`, 614953 bytes, 854 complete lines. The bundle was read FIRST and every verdict below is derived only from its bytes; the two worker notes were read afterwards and treated solely as claims.

Rule applied (from the audit card): a LAN-move block is SAFE only when it references `derive_device_secret.py` output or a variable bound to that output. It is UNSAFE if it instead uses a hardcoded literal IP, an unresolved placeholder such as `{lan_ip}`, a stale copy/pasted address, or an implicit/absent binding. Read-back is safe only when it re-reads the same source the LAN-move wrote.

Shape of the ground truth (read before any note):
- `flows` is a JSON **array** of 2 objects. `flows[0].name` = net4sats (physical line 262); `flows[1].name` = tollgate (physical line 292). Each flow object has exactly the keys name, description, params.
- `flows[0].params` and `flows[1].params` both carry ONLY `upstream_ssid`, `upstream_key`, `upstream_band`. There is **no** `lan_ip`, `lan_gateway`, `ipv4`, `steps[]` or `config` key anywhere in the file.
- The LAN-move text exists only inside `rendered["<model-id>"]["<flow-name>"]["<version>"]["shell"|"markdown"]`.
- The bundle's `models[]` objects carry only `id`, `vendor`, `description`, `target`, `version`, `capabilities` — **no** `lan_subnet` key (the string `lan_subnet` occurs only inside markdown prose, never as a JSON key).
- Whole-file fixed-string counts (re-run by this audit against the same bytes): `{{lan_ip}}` = 0, `LAN_IP` = 0, `derive_device_secret` = 0, `lan_gateway` = 0, `uci get` = 0, `grep -qxF` = 0, `read-back` (case-insensitive) = 0, `uci show` = 0, `ip addr` = 0, `ubus call` = 0. The only `{{...}}` placeholders in the file are `{{hostname}}`, `{{root_password}}`, `{{upstream_ssid}}`, `{{upstream_key}}`, `{{upstream_band}}`.
- `git ls-files scripts/derive_device_secret.py` = 0 lines; the file does not exist at HEAD, so no block in this bundle can reference its output.

Both flows render the SAME LAN-move block: across all 43 (model,version) slots per flow the LAN-move tail is 43/43 byte-identical between `net4sats` and `tollgate`. Per-model applied `network.lan.ipaddr` (identical for both flows):

```text
asus-lyra-map-ac2200         10.231.9.1
comfast-cf-wr632ax           192.168.1.1
dlink-covr-x1860-a1          10.89.4.1
extreme-networks-ws-ap3915i  10.47.217.1
glinet-gl-ar150              10.135.117.1
glinet-gl-ar300m-lite        10.193.202.1
glinet-gl-ar300m-nand        10.64.224.1
glinet-gl-ar300m-nor         10.107.186.1
glinet-mt3000                10.230.236.1
glinet-mt6000                10.230.237.1
linksys-mx4200-v1            10.36.125.1
linksys-whw03-v1             10.12.100.1
linksys-whw03-v2             10.61.168.1
ubnt-edgerouter-6p           10.141.185.1
ubnt-edgerouter-x            10.78.162.1
zyxel-ex5700-telenor         10.13.237.1
zyxel-gs1900-24e             10.44.172.1
zyxel-gs1900-8hp-a1          10.172.177.1
zyxel-gs1900-8hp-b1          10.47.149.1
zyxel-gs1920-24              10.213.244.1
zyxel-nr7101                 10.63.178.1
zyxel-wx5600-t0              10.220.129.1
```

---

## net4sats

Flow name: **net4sats** — `flows[0].name`, physical line 262:

```text
      "name": "net4sats",
```

JSON key path(s) inspected:
- `rendered["asus-lyra-map-ac2200"]["net4sats"]["24.10.7"]["shell"]` (physical line 330) — LAN-move block is the final section of this shell string.
- `rendered["comfast-cf-wr632ax"]["net4sats"]["25.12.4"]["shell"]` (physical line 352) — the no-op slot.
- `flows[0].params` — key set proved below.
- Sweep: all 43 net4sats slots / 86 shell+markdown strings.
- Read-back key path: **NONE / absent** — no read-back block exists for this flow anywhere in the bundle.

Verbatim quoted evidence (raw file bytes), key path `rendered["asus-lyra-map-ac2200"]["net4sats"]["24.10.7"]["shell"]`, physical line 330:

```text
# --- Move the LAN off 192.168.1.1 ---\nssh root@$IP sh <<'CONWRT_EOF'\n# move LAN off 192.168.1.1 \u2192 10.231.9.1 (10.231.9.0/24)\nuci set network.lan.ipaddr='10.231.9.1'\nuci set network.lan.netmask='255.255.255.0'\nuci commit network\n(/etc/init.d/network restart &) ; echo 'LAN moving to 10.231.9.1 \u2014 reconnect on that subnet'\nCONWRT_EOF\n
```

Verbatim quoted evidence, key path `rendered["comfast-cf-wr632ax"]["net4sats"]["25.12.4"]["shell"]`, physical line 352:

```text
# --- Move the LAN off 192.168.1.1 ---\nssh root@$IP sh <<'CONWRT_EOF'\n# move LAN off 192.168.1.1 \u2192 192.168.1.1 (192.168.1.0/24)\nuci set network.lan.ipaddr='192.168.1.1'\nuci set network.lan.netmask='255.255.255.0'\nuci commit network\n(/etc/init.d/network restart &) ; echo 'LAN moving to 192.168.1.1 \u2014 reconnect on that subnet'\nCONWRT_EOF\n
```

Verbatim quoted evidence, key path `flows[0].params` (physical lines 264-265), and the complete set of its descendant keys (physical lines 265/272/279) — no `lan_ip`:

```text
      "params": {
        "upstream_ssid": {
```

Complete descendant key lines of `flows[0].params` (physical lines 265/272/279 — each line is verbatim, but they are not contiguous in the file, so this block is a list, not a single quote):

```text
        "upstream_ssid": {
        "upstream_key": {
        "upstream_band": {
```

**LAN-move verdict: CORRECTED — UNSAFE.** Worker-note verdict was `APPLIES DERIVED VALUE` (SAFE-equivalent). The emitted `ipaddr` is a per-model **hardcoded literal string** baked into the bundle; it is neither a reference to `derive_device_secret.py` output (that file does not exist at this HEAD) nor a variable bound to such output (`lan_gateway`, `LAN_IP`, `{{lan_ip}}` each occur 0 times). The bundle contains no binding construct at all, so the binding is implicit/absent — both of the card's UNSAFE triggers.

```correction
CORRECTION: APPLIES DERIVED VALUE -> UNSAFE
```
  Key path: `rendered["comfast-cf-wr632ax"]["net4sats"]["25.12.4"]["shell"]` (physical line 352).
  Verbatim evidence:
```text
uci set network.lan.ipaddr='192.168.1.1'
```
  Key path: `rendered["asus-lyra-map-ac2200"]["net4sats"]["24.10.7"]["shell"]` (physical line 330).
  Verbatim evidence:
```text
uci set network.lan.ipaddr='10.231.9.1'
```

**Read-back verdict: CORRECTED — UNSAFE (absent binding).** The note records read-back as ABSENT but attaches no UNSAFE classification to that absence; under the card's rule an absent binding is itself the unsafe condition, and nothing re-reads the value the LAN-move wrote.

```correction
CORRECTION: READ-BACK "(none)" (absence recorded, verdict-neutral) -> UNSAFE (absent binding)
```
  Key path: `rendered["comfast-cf-wr632ax"]["net4sats"]["25.12.4"]["shell"]` (physical line 352); counterpart `rendered["asus-lyra-map-ac2200"]["net4sats"]["24.10.7"]["shell"]` (physical line 330).
  Verbatim evidence — unconditional commit, then only a hardcoded echo; no verification statement follows:
```text
uci commit network\n(/etc/init.d/network restart &) ; echo 'LAN moving to 192.168.1.1 \u2014 reconnect on that subnet'\nCONWRT_EOF\n
```

Flagged unsupported / overstated in the net4sats note:
- The phrase "not a hardcoded literal" does not follow from the audited artifact. In the bundle the value IS a literal string; the derivation the note cites (`scripts/flows/render.py:131` reading `target["lan_gateway"]`, itself computed in `scripts/profile/target.py:112-117` from `model["lan_subnet"]`) happens pre-emission in generator source and is not present, traceable or verifiable from `docs/wizard-bundle.json`. It is a generate-time static computation from `models/*.json`, not a device-identity derivation, so it does not satisfy the card's "derived ipv4" test.
- The note cites HEAD `d194b31ce0457d746127bb1fbe64c035fe64e082`; the actual HEAD is `70efbbfe72e85f2a525f4c22da12eaddacbd05d7`. The bundle sha256 is unchanged, so the audited bytes are identical, but the note's HEAD citation is stale.
- The note's "43 rendered slots" vs "172 rendered strings" bookkeeping is imprecise: 43 (model,version) slots per flow x 2 flows = 86 slots, each with a `.shell` and a `.markdown` string = 172 strings. The verdict is unaffected.

---

## tollgate

Flow name: **tollgate** — `flows[1].name`, physical line 292:

```text
      "name": "tollgate",
```

JSON key path(s) inspected:
- `rendered["comfast-cf-wr632ax"]["tollgate"]["25.12.4"]["shell"]` (physical line 358) — LAN-move block is the final section of this shell string.
- `rendered["asus-lyra-map-ac2200"]["tollgate"]["24.10.7"]["shell"]` (physical line 340).
- `flows[1].params`.
- Sweep: all 43 tollgate slots / 86 shell+markdown strings.
- Read-back key path: **NONE / absent**.

Verbatim quoted evidence (raw file bytes), key path `rendered["comfast-cf-wr632ax"]["tollgate"]["25.12.4"]["shell"]`, physical line 358:

```text
# --- Move the LAN off 192.168.1.1 ---\nssh root@$IP sh <<'CONWRT_EOF'\n# move LAN off 192.168.1.1 \u2192 192.168.1.1 (192.168.1.0/24)\nuci set network.lan.ipaddr='192.168.1.1'\nuci set network.lan.netmask='255.255.255.0'\nuci commit network\n(/etc/init.d/network restart &) ; echo 'LAN moving to 192.168.1.1 \u2014 reconnect on that subnet'\nCONWRT_EOF\n
```

Verbatim quoted evidence, key path `rendered["asus-lyra-map-ac2200"]["tollgate"]["24.10.7"]["shell"]`, physical line 340:

```text
# --- Move the LAN off 192.168.1.1 ---\nssh root@$IP sh <<'CONWRT_EOF'\n# move LAN off 192.168.1.1 \u2192 10.231.9.1 (10.231.9.0/24)\nuci set network.lan.ipaddr='10.231.9.1'\nuci set network.lan.netmask='255.255.255.0'\nuci commit network\n(/etc/init.d/network restart &) ; echo 'LAN moving to 10.231.9.1 \u2014 reconnect on that subnet'\nCONWRT_EOF\n
```

Verbatim quoted evidence, key path `flows[1].params` (physical lines 294-295), and the complete set of its descendant keys (physical lines 295/302/309) — no `lan_ip`:

```text
      "params": {
        "upstream_ssid": {
```

Complete descendant key lines of `flows[1].params` (physical lines 295/302/309 — each line is verbatim, but they are not contiguous in the file, so this block is a list, not a single quote):

```text
        "upstream_ssid": {
        "upstream_key": {
        "upstream_band": {
```

**LAN-move verdict: CORRECTED — UNSAFE.** Worker-note verdict was `APPLIES DERIVED VALUE`. Same evidence as net4sats: the block writes a per-model hardcoded literal (`uci set network.lan.ipaddr='192.168.1.1'` for comfast-cf-wr632ax), with no reference to `derive_device_secret.py` output and no variable bound to it. Worst case: for comfast-cf-wr632ax that literal equals the OpenWrt default, so the step titled "Move the LAN off 192.168.1.1" moves the LAN to 192.168.1.1 and the echo falsely announces "LAN moving to 192.168.1.1" — a silent no-op, undetected because no read-back exists.

```correction
CORRECTION: APPLIES DERIVED VALUE -> UNSAFE
```
  Key path: `rendered["comfast-cf-wr632ax"]["tollgate"]["25.12.4"]["shell"]` (physical line 358).
  Verbatim evidence:
```text
uci set network.lan.ipaddr='192.168.1.1'
```

**Read-back verdict: CORRECTED — UNSAFE (absent binding).** The note states read-back is absent but declares the absence a caveat that does not change its verdict; under the card's rule the absence IS the unsafe condition.

```correction
CORRECTION: READ-BACK "(none)" (absence recorded, verdict-neutral) -> UNSAFE (absent binding)
```
  Key path: `rendered["comfast-cf-wr632ax"]["tollgate"]["25.12.4"]["shell"]` (physical line 358).
  Verbatim evidence — unconditional commit, then only a hardcoded echo; no verification statement:
```text
uci commit network\n(/etc/init.d/network restart &) ; echo 'LAN moving to 192.168.1.1 \u2014 reconnect on that subnet'\nCONWRT_EOF\n
```

Flagged unsupported / overstated in the tollgate note:
- "the two transports are rendered from the same op list, so they cannot diverge" is a generator-internal claim, not quotable from `docs/wizard-bundle.json`; the bundle only shows the two rendered strings.
- The note cites HEAD `34413b132b67fcdbbb54a3c500051dc2484ade36`; the actual HEAD is `70efbbfe72e85f2a525f4c22da12eaddacbd05d7` (bundle sha unchanged, so the artifact is identical; the HEAD citation is stale).
- Both notes reference a PR#55 divergence carrying `LAN_IP='{{lan_ip}}'` plus a `grep -qxF` read-back. That is a different artifact (branch `pr-55`, head `ec5c60d9`); it is NOT part of the artifact audited here, where `{{lan_ip}}` and `grep -qxF` both occur 0 times.

---

## Summary

Both flows expose the same provenance defect and neither is safe. The LAN-move in `docs/wizard-bundle.json` at HEAD `70efbbfe72e85f2a525f4c22da12eaddacbd05d7` (sha256 `6fe93f952fe68a53facd7d0a3561865377ccdd15beb3801cb4432b23a507277e`) does not reference `derive_device_secret.py` output and is not bound to any variable derived from it — the file does not exist at this HEAD and the tokens `{{lan_ip}}`, `LAN_IP`, `lan_gateway` and `derive_device_secret` each occur 0 times. Instead, every one of the 43 net4sats and 43 tollgate slots writes a per-model hardcoded literal (`uci set network.lan.ipaddr='<ip>'`) baked into the bundle, so the binding is implicit/absent — UNSAFE under the card's rule — and no read-back exists anywhere, so the written value is never verified. The concrete silent-fallback-to-hardcoded-literal case is `rendered["comfast-cf-wr632ax"]["net4sats"]["25.12.4"]["shell"]` (physical line 352) and its byte-identical sibling `rendered["comfast-cf-wr632ax"]["tollgate"]["25.12.4"]["shell"]` (physical line 358), where the literal equals the OpenWrt default 192.168.1.1: the "Move the LAN off 192.168.1.1" step is a no-op that the recipe silently reports as a successful move. The JSON key path responsible for any silent literal/placeholder fallback is therefore that LAN-move text under `rendered["<model-id>"]["net4sats"|"tollgate"]["<version>"]["shell"|"markdown"]` — no other candidate binding key exists in the bundle.
