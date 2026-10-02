## tollgate flow

Recipe: docs/wizard-bundle.json | key path: rendered["comfast-cf-wr632ax"]["tollgate"]["25.12.4"].shell (JSON physical file line 358; the sibling rendered variant .markdown is physical line 359; the owning flow definition is flows[1], name="tollgate", description "Generic TollGate Bitcoin/Lightning payment gateway. Flashes stock OpenWrt, joins upstream WiFi, installs the tollgate backend, and configures the nodogsplash captive portal."). Source of record: /home/c03rad0r/repos/conwrt @ HEAD 34413b132b67fcdbbb54a3c500051dc2484ade36 (branch feat/vpn-provider-setup), docs/wizard-bundle.json sha256 6fe93f952fe68a53facd7d0a3561865377ccdd15beb3801cb4432b23a507277e — READ-ONLY, unmodified by this note.

LAN-move commands (verbatim):
```sh
# --- Move the LAN off 192.168.1.1 ---
ssh root@$IP sh <<'CONWRT_EOF'
# move LAN off 192.168.1.1 → 192.168.1.1 (192.168.1.0/24)
uci set network.lan.ipaddr='192.168.1.1'
uci set network.lan.netmask='255.255.255.0'
uci commit network
(/etc/init.d/network restart &) ; echo 'LAN moving to 192.168.1.1 — reconnect on that subnet'
CONWRT_EOF
```

This is the tollgate flow's `set_lan_ip` step — the last step of the recipe (`scripts/flows/render.py:158-159` dispatches `step.kind == "set_lan_ip"` to `_set_lan_ip_ops()`, `scripts/flows/render.py:130-140`). The block is shell-string lines 62-69 of 69. The markdown transport carries the same four device-side commands (without the `ssh root@$IP sh <<'CONWRT_EOF'` wrapper) under the heading `### move LAN off 192.168.1.1 → 192.168.1.1 (192.168.1.0/24)`; the two transports are rendered from the same op list, so they cannot diverge. Commands emitted by the LAN-move block: 5 (1 host-side `ssh ... sh <<'CONWRT_EOF'` wrapper + 4 device-side: `uci set` x2, `uci commit` x1, backgrounded network restart + `echo` x1). Nothing else.

Read-back commands (verbatim):
```text
(none — the tollgate recipe emits no read-back command; there is nothing to quote)
```

Read-back absence evidence: `uci get` occurs 0 times in the entire bundle (all 86 rendered `rendered.<model>.<flow>.<version>` entries, `.shell` + `.markdown` = 172 strings; `uci show` 0, `ip addr` 0, `ubus call` 0). The generator has no verification op either: `_set_lan_ip_ops()` (`scripts/flows/render.py:130-140`) emits exactly `Comment` (:136), `UciSet` (:137), `UciCommit` (:138), `ShellCommand` (:139) — two writes, one commit, one human-facing `echo`, no post-write check. `uci commit network` is therefore unconditional: nothing verifies the value before it is made permanent, and the commit is followed only by a backgrounded network restart.

Derived ipv4 entry point: scripts/flows/render.py:131 (`gw = target.get("lan_gateway", "")`) <- scripts/profile/target.py:130 (`"lan_gateway": lan_gateway`) <- scripts/profile/target.py:117 (`lan_gateway = str(net.network_address + 1)`) <- models/comfast-cf-wr632ax.json:3 (`"lan_subnet": "192.168.1.0/24"`), emitted into the bundle at scripts/flows/render.py:137 -> rendered["comfast-cf-wr632ax"]["tollgate"]["25.12.4"].shell, shell-string line 65. Verbatim binding snippet (only the `#`-prefixed locator line is added by this note; every other line is byte-identical to the named file):

```python
    gw = target.get("lan_gateway", "")

    # scripts/profile/target.py:112-117, :129-130
    lan_subnet = model.get("lan_subnet", "")
    lan_gateway = ""
    if lan_subnet:
        try:
            net = ipaddress.ip_network(lan_subnet, strict=False)
            lan_gateway = str(net.network_address + 1)
        except ValueError:
            lan_gateway = ""

        "lan_subnet": lan_subnet,
        "lan_gateway": lan_gateway,
```

Verdict: APPLIES DERIVED VALUE — the address the block writes is the flow-bound derived `lan_gateway` (`scripts/flows/render.py:131` <- `scripts/profile/target.py:117`/`:130`, i.e. the model's `lan_subnet` network address + 1), not a hardcoded literal (the emitted `network.lan.ipaddr` takes a distinct per-model value in every one of the 43 rendered net4sats/tollgate slots) and not an unresolved `{{lan_ip}}` template (0 occurrences in this bundle), so the flow does apply the value it derived.

Notes and caveats (do not change the verdict, but they matter for the live run):

- Runtime no-op for this model. For comfast-cf-wr632ax the derived gateway is `192.168.1.1`, which is the OpenWrt default and identical to the model's own `openwrt.default_ip` (`models/comfast-cf-wr632ax.json:9`). The step therefore announces "LAN moving to 192.168.1.1" and reconnects to the same address — the "Move the LAN off 192.168.1.1" step moves nothing. comfast-cf-wr632ax is the only one of the 22 models whose tollgate LAN-move writes `192.168.1.1`; every other model writes its own derived gateway (e.g. asus-lyra-map-ac2200 -> `10.231.9.1`, glinet-mt6000 -> `10.230.237.1`). With no read-back and no guard, nothing in the recipe can detect this.
- Not device-identity-derived at this revision. `scripts/derive_device_secret.py` does not exist here (`git ls-files scripts/derive_device_secret.py` = empty) and the string `derive_device_secret` occurs 0 times in `docs/wizard-bundle.json`. The applied value is a static per-model computation frozen into the bundle at generate time (`scripts/generate_site.py`), not a runtime identity derivation; a live run cannot obtain a per-device CGNAT address from this bundle.
- Revision divergence (context, for the PR #55 lane). At `ec5c60d9458b4ee7ce86a0ce86993c078409e116` (branch `pr-55`, PR #55 head; not an ancestor of this HEAD) the same slot `rendered["comfast-cf-wr632ax"]["tollgate"]["25.12.4"].shell` (bundle sha256 3b1f047be5e7495f75c3af42c86bcfba2d3e0491ddf17f5ec670600d8ed25f39) instead carries the unresolved template `LAN_IP='{{lan_ip}}'` plus a `case`-guard against an unfilled placeholder and a read-back `uci get network.lan.ipaddr | grep -qxF "$LAN_IP"` — byte-identical to upstream `17a7786` (also not an ancestor of this HEAD). That is the revision where the value is an unresolved placeholder; this note is cited against the working tree at HEAD `34413b132b67fcdbbb54a3c500051dc2484ade36`, where `{{lan_ip}}` occurs 0 times.
- Nothing above is UNRESOLVED: every required field was determined from reading. The read-back block is determined to be absent (not unresolvable).
- Verification: the quoted LAN-move block was sliced programmatically from `docs/wizard-bundle.json` (not hand-transcribed) and re-checked against the raw file bytes after writing (the escaped-newline form of the slice is present in the file); the bundle sha256 is unchanged at `6fe93f952fe68a53facd7d0a3561865377ccdd15beb3801cb4432b23a507277e`.
