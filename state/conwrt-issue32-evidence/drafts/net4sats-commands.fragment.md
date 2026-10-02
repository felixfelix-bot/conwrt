## Recipe key path
rendered["asus-lyra-map-ac2200"]["net4sats"]["24.10.7"]["shell"]

(this bundle has no recipes[]/steps[]/commands[] structure — top-level keys are models, flows, versions, rendered, addons, generated_at. The "recipe" is the net4sats flow definition at flows[0] (its `name` field is the literal string "net4sats"); the dot-path above is the rendered shell string for that flow, which is where the LAN-move step's emitted commands actually live. Parent keys needed to disambiguate: top-level `rendered` -> model id `asus-lyra-map-ac2200` -> flow name `net4sats` -> OpenWrt version `24.10.7` -> artifact kind `shell`. The LAN-move block is the last step of the recipe and is byte-identical in shape across all 43 net4sats `shell` slots (and their sibling `.markdown` slots), differing only in the per-model IPv4 literal.)

## LAN-move commands (verbatim)
```
# --- Move the LAN off 192.168.1.1 ---
ssh root@$IP sh <<'CONWRT_EOF'
# move LAN off 192.168.1.1 → 10.231.9.1 (10.231.9.0/24)
uci set network.lan.ipaddr='10.231.9.1'
uci set network.lan.netmask='255.255.255.0'
uci commit network
(/etc/init.d/network restart &) ; echo 'LAN moving to 10.231.9.1 — reconnect on that subnet'
CONWRT_EOF
```

## Read-back commands (verbatim)
```
(none — the net4sats recipe emits no read-back/verification command; there is nothing to quote. Verified over the parsed bundle: `uci get`, `uci show`, `ip addr`, `ifconfig`, `ubus call`, `grep -qxF`, `read-back` each occur 0 times across all 86 net4sats rendered slots, and no net4sats markdown heading contains verify/confirm/check/read-back.)
```

## IP token observed
`none observed` — no placeholder (no `{{lan_ip}}`, `%LAN_IP%`, or similar sigil) and no variable name is used for the new LAN IPv4; it is emitted as a per-model hardcoded literal. In the quoted slot the literal is `10.231.9.1`. The only IP-valued variable token in the block is `$IP` (defined earlier in the same shell as `IP=${IP:-192.168.1.1}`), used solely as the ssh target in `ssh root@$IP`, not as the new LAN address.
