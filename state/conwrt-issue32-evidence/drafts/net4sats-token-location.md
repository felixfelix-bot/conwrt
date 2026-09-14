## Token observed (verbatim)

The net4sats LAN-move recipe does NOT use a template placeholder (no `{{lan_ip}}`, `%LAN_IP%`, or similar sigil). The IPv4 value is a literal, hardcoded per model. The first net4sats LAN-move block (asus-lyra-map-ac2200, 24.10.7, shell) uses the literal IPv4 address:

`10.231.9.1`

Observed verbatim in the shell heredoc comment (JSON-escaped `\u2192` = `→`):

`# move LAN off 192.168.1.1 \u2192 10.231.9.1 (10.231.9.0/24)`

and in the uci command body:

`uci set network.lan.ipaddr='10.231.9.1'`

## Occurrence sites (key paths)

The exact token string `10.231.9.1` appears ONLY in the asus-lyra-map-ac2200 model's net4sats blocks (both firmware versions, in both the `shell` and `markdown` fields). It does NOT appear in any other model's net4sats block, nor in any tollgate block, nor in the flows/addons/params maps.

- `$.rendered["asus-lyra-map-ac2200"].net4sats["24.10.7"].shell` — line 330 — comment `# move LAN off 192.168.1.1 \u2192 10.231.9.1 (10.231.9.0/24)` and `uci set network.lan.ipaddr='10.231.9.1'`
- `$.rendered["asus-lyra-map-ac2200"].net4sats["24.10.7"].markdown` — line 331 — heading `### move LAN off 192.168.1.1 → 10.231.9.1 (10.231.9.0/24)` and `uci set network.lan.ipaddr='10.231.9.1'`
- `$.rendered["asus-lyra-map-ac2200"].net4sats["25.12.4"].shell` — line 334 — comment `# move LAN off 192.168.1.1 \u2192 10.231.9.1 (10.231.9.0/24)` and `uci set network.lan.ipaddr='10.231.9.1'`
- `$.rendered["asus-lyra-map-ac2200"].net4sats["25.12.4"].markdown` — line 335 — heading `### move LAN off 192.168.1.1 → 10.231.9.1 (10.231.9.0/24)` and `uci set network.lan.ipaddr='10.231.9.1'`

The LAN-move use is the only occurrence of `10.231.9.1` in the bundle. It does not appear elsewhere.

Note: each other model uses a different literal IP (e.g. dlink-covr-x1860-a1 uses `10.89.4.1`, glinet-gl-ar150 uses `10.135.117.1`, comfast-cf-wr632ax uses `192.168.1.1` — i.e. no move). There is no single shared token; the value is baked per-model.

## In-bundle binding (key path + value, or 'no in-bundle binding')

no in-bundle binding

The bundle has no variables/defaults/inputs/secrets/env/params map that defines or supplies `10.231.9.1` (or any `lan_ip` / `lan_subnet` key). The top-level keys are: `models`, `flows`, `versions`, `rendered`, `addons`, `generated_at`.

- `$.flows[0].params` (the net4sats flow) defines only: `upstream_ssid`, `upstream_key`, `upstream_band` — no LAN IP parameter.
- `$.flows[1].params` (the tollgate flow) defines the same three — no LAN IP parameter.
- `$.addons[*].params` defines only `root_password` (set-password addon) and `hostname` (hostname addon) — no LAN IP parameter.
- `$.models[*]` entries carry only `id`, `vendor`, `description`, `target`, `version`, `capabilities` — no `lan_subnet` or IP field, despite the markdown prose saying "this model's lan_subnet".

The only template tokens (`{{...}}`) present anywhere in the bundle are: `{{upstream_ssid}}`, `{{upstream_key}}`, `{{upstream_band}}`, `{{root_password}}`, `{{hostname}}`. There is no `{{lan_ip}}` or `{{lan_subnet}}`.

## Quoted evidence

1. Shell heredoc comment (verbatim, JSON-escaped) — `$.rendered["asus-lyra-map-ac2200"].net4sats["24.10.7"].shell`, line 330:
   `# move LAN off 192.168.1.1 \u2192 10.231.9.1 (10.231.9.0/24)`

2. Shell uci command (verbatim) — same key path, line 330:
   `uci set network.lan.ipaddr='10.231.9.1'`

3. Shell netmask + restart (verbatim) — same key path, line 330:
   `uci set network.lan.netmask='255.255.255.0'`
   `uci commit network`
   `(/etc/init.d/network restart &) ; echo 'LAN moving to 10.231.9.1 \u2014 reconnect on that subnet'`

4. Markdown heading (verbatim, decoded) — `$.rendered["asus-lyra-map-ac2200"].net4sats["24.10.7"].markdown`, line 331:
   `### move LAN off 192.168.1.1 → 10.231.9.1 (10.231.9.0/24)`

5. Markdown prose referencing an undefined key (verbatim, decoded) — same key path, line 331:
   `Sets the router LAN to this model's lan_subnet so it doesn't collide with neighbour devices that default to 192.168.1.1 (e.g. a peer router sitting in U-Boot recovery). Runs last; reconnect on the new subnet afterwards.`

6. Markdown uci block (verbatim, decoded) — same key path, line 331:
   `uci set network.lan.ipaddr='10.231.9.1'`
   `uci set network.lan.netmask='255.255.255.0'`
   `uci commit network`
   `(/etc/init.d/network restart &) ; echo 'LAN moving to 10.231.9.1 — reconnect on that subnet'`

7. Net4sats flow params (verbatim) — `$.flows[0].params`, lines 264-289:
   `upstream_ssid`, `upstream_key`, `upstream_band` — no LAN IP key present.

8. Addons params (verbatim) — `$.addons[*].params`:
   - random-password: `{}`
   - set-password: `{"root_password": {...}}`
   - hostname: `{"hostname": {...}}`
   - wan-ssh: `{}`
   No LAN IP key present in any addon.

9. Full set of template tokens found in the entire bundle (verbatim):
   `{{hostname}}`, `{{root_password}}`, `{{upstream_band}}`, `{{upstream_key}}`, `{{upstream_ssid}}`
   No `{{lan_ip}}` or `{{lan_subnet}}` token exists.