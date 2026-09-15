## Recipe key path
rendered["glinet-mt6000"]["net4sats"]["24.10.7"]["shell"] — lines 70-77 (the "# --- Move the LAN off 192.168.1.1 ---" section, the last heredoc block in the shell script). Parent keys: rendered is a top-level key in docs/wizard-bundle.json; the nesting is rendered.<model-id>.<flow-name>.<version>.shell. The net4sats flow is flows[0] (name="net4sats"). The LAN-move block is not a separate JSON "recipe" or "step" object — the bundle has no steps/recipe/commands keys at all; the command strings exist only inside the pre-rendered shell strings under the rendered key. The same block appears identically (modulo the per-model lan_subnet IP) in every rendered.<model>.net4sats.<version>.shell entry (86 net4sats locations total).

## LAN-move commands (verbatim)
```
uci set network.lan.ipaddr='10.230.237.1'
uci set network.lan.netmask='255.255.255.0'
uci commit network
(/etc/init.d/network restart &) ; echo 'LAN moving to 10.230.237.1 — reconnect on that subnet'
```

## Read-back commands (verbatim)
```
(none — no uci get, ifconfig, ip addr, or any verification/read-back command appears in this block or anywhere in the net4sats rendered shells)
```

## IP token observed
`10.230.237.1` — hardcoded literal (no placeholder or variable name used for the new LAN IP; the value is baked into the rendered shell string). The shell variable `$IP` (defined as `IP=${IP:-192.168.1.1}` at line 5) is used only as the SSH target address in `ssh root@$IP`, not as the new LAN address.