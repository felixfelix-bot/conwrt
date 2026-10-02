## net4sats flow

Recipe: docs/wizard-bundle.json | key path: flows[0] (the net4sats flow definition; JSON physical line 262 for the `"name": "net4sats"` string) — this bundle has no `recipes[]` array, so the "recipe" is the flow definition plus its per-model rendered shell. The verbatim commands below are quoted from the emitted recipe slot rendered["asus-lyra-map-ac2200"]["net4sats"]["24.10.7"].shell, JSON physical line 330 (sibling rendered variant .markdown is physical line 331). Source of record: /home/c03rad0r/repos/conwrt @ HEAD d194b31ce0457d746127bb1fbe64c035fe64e082 (branch feat/vpn-provider-setup), docs/wizard-bundle.json sha256 6fe93f952fe68a53facd7d0a3561865377ccdd15beb3801cb4432b23a507277e — READ-ONLY, unmodified by this note.

LAN-move commands (verbatim):
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

This is the net4sats flow's `set_lan_ip` step — the LAST step of the recipe (title `Move the LAN off 192.168.1.1`, defined at scripts/flows/_gateway.py:66-71 via `lan_finalize_step()`, dispatched by `scripts/flows/render.py:158-159` to `_set_lan_ip_ops()`, `scripts/flows/render.py:130-140`). Commands emitted by this block: 5 shell lines in emission order — 1 host-side wrapper (`ssh root@$IP sh <<'CONWRT_EOF'`) + 4 device-side (`uci set` x2, `uci commit` x1, backgrounded network restart + `echo` x1) + the closing `CONWRT_EOF`. The leading `# --- ... ---` line is the step-title comment.

Per-model scope: the block is generated once per rendered slot and is byte-identical in structure across all 43 net4sats slots (22 models × up to 2 OpenWrt versions: 24.10.7 and 25.12.4) — only the derived LAN address/subnet tokens change. The whole block is quoted above for asus-lyra-map-ac2200; every other model emits the same 8 lines with its own IP substituted. The applied `network.lan.ipaddr` per model (all 22, from the parsed bundle):

```
asus-lyra-map-ac2200        10.231.9.1    (10.231.9.0/24)
comfast-cf-wr632ax          192.168.1.1   (192.168.1.0/24)   <- no-op: equals the OpenWrt default
dlink-covr-x1860-a1         10.89.4.1     (10.89.4.0/24)
extreme-networks-ws-ap3915i 10.47.217.1   (10.47.217.0/24)
glinet-gl-ar150             10.135.117.1  (10.135.117.0/24)
glinet-gl-ar300m-lite       10.193.202.1  (10.193.202.0/24)
glinet-gl-ar300m-nand       10.64.224.1   (10.64.224.0/24)
glinet-gl-ar300m-nor        10.107.186.1  (10.107.186.0/24)
glinet-mt3000               10.230.236.1  (10.230.236.0/24)
glinet-mt6000               10.230.237.1  (10.230.237.0/24)
linksys-mx4200-v1           10.36.125.1   (10.36.125.0/24)
linksys-whw03-v1            10.12.100.1   (10.12.100.0/24)
linksys-whw03-v2            10.61.168.1   (10.61.168.0/24)
ubnt-edgerouter-6p          10.141.185.1  (10.141.185.0/24)
ubnt-edgerouter-x           10.78.162.1   (10.78.162.0/24)
zyxel-ex5700-telenor        10.13.237.1   (10.13.237.0/24)
zyxel-gs1900-24e            10.44.172.1   (10.44.172.0/24)
zyxel-gs1900-8hp-a1         10.172.177.1  (10.172.177.0/24)
zyxel-gs1900-8hp-b1         10.47.149.1   (10.47.149.0/24)
zyxel-gs1920-24             10.213.244.1  (10.213.244.0/24)
zyxel-nr7101                10.63.178.1   (10.63.178.0/24)
zyxel-wx5600-t0             10.220.129.1  (10.220.129.0/24)
```

Read-back commands (verbatim):
```text
(none — the net4sats recipe emits no read-back/verification command; there is nothing to quote)
```

Read-back absence evidence: over the parsed bundle (all 43 net4sats rendered slots; all 172 rendered strings counting .shell + .markdown), the verification tokens `uci get`, `uci show`, `ip addr`, `ifconfig`, `ubus call`, `grep -qxF`, `LAN_IP=`, `read-back` each occur 0 times. The generator has no verification op either: `_set_lan_ip_ops()` (`scripts/flows/render.py:130-140`) emits exactly `Comment` (:136), `UciSet` (:137), `UciCommit` (:138), `ShellCommand` (:139) — two writes, one commit, one human-facing `echo`, no post-write check; `_step_parts()` (`scripts/flows/render.py:143-160`) maps no step kind to a read-back op. `uci commit network` is therefore unconditional and nothing verifies the value landed before it is made permanent.

Derived ipv4 entry point: docs/wizard-bundle.json:330 -> rendered["asus-lyra-map-ac2200"]["net4sats"]["24.10.7"].shell (shell-string lines 67, 68 and 71). Generator binding chain: scripts/flows/render.py:131 (`gw = target.get("lan_gateway", "")`) <- scripts/profile/target.py:130 (`"lan_gateway": lan_gateway`) <- scripts/profile/target.py:117 (`lan_gateway = str(net.network_address + 1)`) <- scripts/profile/target.py:116 (`net = ipaddress.ip_network(lan_subnet, strict=False)`) <- scripts/profile/target.py:112 (`lan_subnet = model.get("lan_subnet", "")`) <- models/asus-lyra-map-ac2200.json:13 (`"lan_subnet": "10.231.9.0/24"`). Verbatim binding snippet (the emitter that consumes the value and the code that binds it):

```python
# scripts/flows/render.py:130-140  (the LAN-move emitter that consumes the value)
def _set_lan_ip_ops(target: dict[str, Any]) -> list[Op]:
    gw = target.get("lan_gateway", "")
    subnet = target.get("lan_subnet", "")
    if not gw:
        return [Comment("skip LAN move — model has no lan_subnet defined")]
    return [
        Comment(f"move LAN off 192.168.1.1 → {gw} ({subnet})"),
        UciSet(config="network", section="lan", values={"ipaddr": gw, "netmask": "255.255.255.0"}),
        UciCommit(config="network"),
        ShellCommand(command=f"(/etc/init.d/network restart &) ; echo 'LAN moving to {gw} — reconnect on that subnet'"),
    ]

# scripts/profile/target.py:112-119,129-130  (where the derived ipv4 is computed and bound)
    lan_subnet = model.get("lan_subnet", "")
    lan_gateway = ""
    if lan_subnet:
        try:
            net = ipaddress.ip_network(lan_subnet, strict=False)
            lan_gateway = str(net.network_address + 1)
        except ValueError:
            lan_gateway = ""
    ...
        "lan_subnet": lan_subnet,
        "lan_gateway": lan_gateway,
```

Verdict: APPLIES DERIVED VALUE — the address the LAN-move block writes is the generator-derived `lan_gateway` (the model's `lan_subnet` network address + 1, bound into `gw` at scripts/flows/render.py:131 and emitted at :137/:139), not a hardcoded literal and not an unresolved template: `{{lan_ip}}` and `{lan_ip}` each occur 0 times in this bundle, `derive_device_secret` / `derive_device_secret.py` occur 0 times and the file does not exist at this HEAD (`git ls-files scripts/derive_device_secret.py` = 0 lines), and the applied ipaddr takes 22 distinct per-model values (see table). If a model lacked a parseable `lan_subnet`, `lan_gateway` stays `""` and the recipe emits no LAN-move commands at all (`scripts/flows/render.py:133-134` -> `Comment("skip LAN move — model has no lan_subnet defined")`) — so the block either applies the derived value or emits nothing, never a literal fallback. There is no read-back, so the applied value is never verified on-device.

Caveats (do not change the verdict, but matter for the live run):
- comfast-cf-wr632ax is the one model whose derived gateway is `192.168.1.1` — identical to the OpenWrt default (`models/comfast-cf-wr632ax.json` openwrt.default_ip), so its "Move the LAN off 192.168.1.1" step is a runtime no-op. With no read-back, nothing in the recipe detects this.
- The applied value is frozen into the bundle at generate time (per-model static computation from `models/*.json`), not derived at runtime from device identity; at this HEAD there is no `derive_device_secret.py`.
- Revision divergence (verified, context only): at PR #55 head `ec5c60d9458b4ee7ce86a0ce86993c078409e116` the bundle instead carries the unresolved placeholder `{{lan_ip}}` 4 times — in the `comfast-cf-wr632ax` `net4sats` `25.12.4` shell+markdown (physical lines 366-367) and `tollgate` `25.12.4` shell+markdown (physical lines 372-373). That revision is not an ancestor of this HEAD; this note is cited against HEAD d194b31, where the placeholder count is 0.
- Verification: the quoted LAN-move block was sliced programmatically from the decoded `docs/wizard-bundle.json` string (not hand-transcribed) and the bundle sha256 is unchanged at 6fe93f952fe68a53facd7d0a3561865377ccdd15beb3801cb4432b23a507277e. Nothing required is unresolvable: the read-back block is determined ABSENT, not unknown. `state/conwrt-issue32-evidence/checklist.md` was not read or written.
