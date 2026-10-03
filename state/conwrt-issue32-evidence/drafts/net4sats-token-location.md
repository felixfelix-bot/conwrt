## Token observed (verbatim)

Scope: `docs/wizard-bundle.json` in `/home/c03rad0r/repos/conwrt`, branch `feat/vpn-provider-setup`, HEAD `143533519eb6c314e842e8a7efceaa4c1fd7d292`, file sha256 `6fe93f952fe68a53facd7d0a3561865377ccdd15beb3801cb4432b23a507277e`, 854 lines. The file is READ-ONLY for this report and was not modified.

The net4sats LAN-move recipe does NOT use a template placeholder or sigil at this revision. Its LAN address is an already-rendered literal. The IPv4 token in the net4sats LAN-move block (the first net4sats slot in the file) is, character for character:

`10.231.9.1`

Key path: `$.rendered["asus-lyra-map-ac2200"].net4sats["24.10.7"].shell`
Physical line: `docs/wizard-bundle.json:330`

It is consumed by exactly this command (decoded):

`uci set network.lan.ipaddr='10.231.9.1'`

The three substrings that carry the token on line 330, quoted verbatim exactly as the bytes appear in the file (JSON string escapes preserved here: `\u2192` is the escape for `→`, `\u2014` for `—`):

- `# move LAN off 192.168.1.1 \u2192 10.231.9.1 (10.231.9.0/24)`
- `uci set network.lan.ipaddr='10.231.9.1'`
- `(/etc/init.d/network restart &) ; echo 'LAN moving to 10.231.9.1 \u2014 reconnect on that subnet'`

Placeholder / sigil check over the whole bundle: `{{lan_ip}}` = 0 occurrences, `${lan_ip}` = 0, `%LAN_IP%` = 0, `LAN_IP` = 0, `lan-ip` = 0, `<lan_ip>` = 0, and the bare substring `lan_ip` = 0. The observed token is therefore a literal, not an unresolved template.

Per-model note (why this token and not "a" token): the recipe carries one literal per model — there is no single shared token. `$.rendered["dlink-covr-x1860-a1"].net4sats["24.10.7"].shell` carries `10.89.4.1`; `$.rendered["glinet-gl-ar150"].net4sats["24.10.7"].shell` carries `10.135.117.1`; `$.rendered["comfast-cf-wr632ax"].net4sats["25.12.4"].shell` carries `192.168.1.1`. `10.231.9.1` is the token of the first net4sats LAN-move block in the file (asus-lyra-map-ac2200), used as the reference block throughout this report.

## Occurrence sites (key paths)

Fixed-string (not regex) search for `10.231.9.1` over the entire bundle file: 24 character-level occurrences, on exactly 8 physical lines — 330, 331, 334, 335, 340, 341, 344, 345 — i.e. 3 occurrences per line (the `# move LAN off ...` comment line, the `uci set network.lan.ipaddr=` line, and the `echo 'LAN moving to ...'` line). Each of those 8 lines is one JSON string value; the file is `json.dumps(bundle, indent=2)` output (verified by round-trip: re-serialising the parsed JSON with `indent=2` reproduces the file byte-for-byte, after stripping the trailing newline), so every string value occupies exactly one physical line and the line-to-key-path mapping is 1:1.

| line | key path | count of `10.231.9.1` |
|------|----------|------------------------|
| 330 | `$.rendered["asus-lyra-map-ac2200"].net4sats["24.10.7"].shell` | 3 |
| 331 | `$.rendered["asus-lyra-map-ac2200"].net4sats["24.10.7"].markdown` | 3 |
| 334 | `$.rendered["asus-lyra-map-ac2200"].net4sats["25.12.4"].shell` | 3 |
| 335 | `$.rendered["asus-lyra-map-ac2200"].net4sats["25.12.4"].markdown` | 3 |
| 340 | `$.rendered["asus-lyra-map-ac2200"].tollgate["24.10.7"].shell` | 3 |
| 341 | `$.rendered["asus-lyra-map-ac2200"].tollgate["24.10.7"].markdown` | 3 |
| 344 | `$.rendered["asus-lyra-map-ac2200"].tollgate["25.12.4"].shell` | 3 |
| 345 | `$.rendered["asus-lyra-map-ac2200"].tollgate["25.12.4"].markdown` | 3 |

Is the LAN-move use the only occurrence, or does it appear elsewhere? It does appear elsewhere. The token is NOT confined to the net4sats flow: 12 of the 24 occurrences are in the sibling `tollgate` flow's LAN-move block for the same model — lines 340 and 341 (tollgate, 24.10.7) and lines 344 and 345 (tollgate, 25.12.4) — because both flows render the same LAN-finalize step for the model. Beyond those 8 lines the token occurs nowhere in the file: zero occurrences under `$.flows`, `$.versions`, `$.models`, `$.addons`, `$.generated_at`, and zero in any other model's rendered blocks (each model emits its own literal). The token occurs only as rendered literal text inside those 8 string values; it is not a key name, and no JSON key in the bundle contains that string.

## In-bundle binding (key path + value, or 'no in-bundle binding')

no in-bundle binding

No key anywhere in the bundle defines or supplies the token. The bundle has no `variables`, `secrets`, `defaults`, `inputs`, `env`, `params` or `config` map: its complete top-level key set is `models` (line 2), `flows` (line 260), `versions` (line 322), `rendered` (line 326), `addons` (line 804), `generated_at` (line 854). Every candidate map is negative:

- `$.flows[0].params` (the net4sats flow, `$.flows[0].name` = `"net4sats"` at line 262; params opens at line 264) — only keys `upstream_ssid` (line 265), `upstream_key` (line 272), `upstream_band` (line 279). No LAN/IP key.
- `$.flows[1].params` (the tollgate flow) — the same three keys: `upstream_ssid` (line 295), `upstream_key` (line 302), `upstream_band` (line 309). No LAN/IP key.
- `$.addons[*].params` — `$.addons[0].params` = `{}` (random-password, line 806); `$.addons[1].params` = `{"root_password": {"type": "string", "required": true, "description": "The root password to set", "default": null, "choices": []}}` (set-password, line 814); `$.addons[2].params` = `{"hostname": {"type": "string", "required": true, "description": "The hostname to set", "default": null, "choices": []}}` (hostname, line 830); `$.addons[3].params` = `{}` (wan-ssh, line 846). No LAN/IP key in any addon.
- `$.models[*]` — the union of model-object keys is `id`, `vendor`, `description`, `target`, `version`, `capabilities` (e.g. `$.models[0].id` = `"asus-lyra-map-ac2200"` at line 4). 0 models carry any key containing `lan`, and there is no address/subnet field.

A structural scan of every JSON key in the bundle for names matching `lan|subnet|gateway|ipv4|ip` returned zero keys. The only place the word `lan_subnet` occurs in the bundle is as prose inside rendered markdown (86 lines, one per rendered markdown string: 43 net4sats slots + 43 tollgate slots) — a dangling textual reference to a key that does not exist in the bundle, not a binding.

## Quoted evidence

1. Token and its comment, verbatim — `$.rendered["asus-lyra-map-ac2200"].net4sats["24.10.7"].shell`, line 330.
   file-verbatim (as the bytes appear; JSON escapes intact): `# move LAN off 192.168.1.1 \u2192 10.231.9.1 (10.231.9.0/24)`
   decoded: `# move LAN off 192.168.1.1 → 10.231.9.1 (10.231.9.0/24)`

2. The applied value, verbatim — same key path, line 330:
   `uci set network.lan.ipaddr='10.231.9.1'`

3. The human-facing echo, verbatim — same key path, line 330:
   file-verbatim: `(/etc/init.d/network restart &) ; echo 'LAN moving to 10.231.9.1 \u2014 reconnect on that subnet'`
   decoded: `(/etc/init.d/network restart &) ; echo 'LAN moving to 10.231.9.1 — reconnect on that subnet'`

4. Markdown sibling of the same net4sats block — `$.rendered["asus-lyra-map-ac2200"].net4sats["24.10.7"].markdown`, line 331:
   `### move LAN off 192.168.1.1 → 10.231.9.1 (10.231.9.0/24)`
   `uci set network.lan.ipaddr='10.231.9.1'`

5. Same token in the sibling tollgate flow (evidence that the LAN-move use is not the only occurrence) — `$.rendered["asus-lyra-map-ac2200"].tollgate["24.10.7"].shell`, line 340:
   `# move LAN off 192.168.1.1 → 10.231.9.1 (10.231.9.0/24)`
   `uci set network.lan.ipaddr='10.231.9.1'`
   and `$.rendered["asus-lyra-map-ac2200"].tollgate["25.12.4"].shell`, line 344, carries the same two lines; the corresponding `.markdown` strings at lines 341 and 345 carry the heading and the uci line.

6. Verification that the token is not a template — whole-file fixed-string counts:
   `{{lan_ip}}` = 0, `${lan_ip}` = 0, `%LAN_IP%` = 0, `LAN_IP` = 0, `lan-ip` = 0, `<lan_ip>` = 0.
   The only `{{...}}` tokens present anywhere in the bundle are `{{upstream_band}}` (172), `{{upstream_key}}` (172), `{{upstream_ssid}}` (172), `{{hostname}}` (6), `{{root_password}}` (2) — no LAN-IP template exists that the token could be bound to.

7. No in-bundle definition key — top-level keys and their lines, verbatim:
   line 2 `"models": [`, line 260 `"flows": [`, line 322 `"versions": [`, line 326 `"rendered": {`, line 804 `"addons": [`, line 854 `"generated_at": "2026-06-23 16:11 UTC"`.
   There is no `variables` / `secrets` / `defaults` / `inputs` / `env` / `config` key, and no key whose name or value supplies `10.231.9.1`.

8. Dangling prose reference to a non-existent binding key — `$.rendered["asus-lyra-map-ac2200"].net4sats["24.10.7"].markdown`, line 331, verbatim:
   `Sets the router LAN to this model's lan_subnet so it doesn't collide with neighbour devices that default to 192.168.1.1 (e.g. a peer router sitting in U-Boot recovery). Runs last; reconnect on the new subnet afterwards.`
   Identical prose occurs in all 86 rendered markdown strings (43 net4sats + 43 tollgate), while 0 JSON keys named `lan_subnet` (or any `lan*` key) exist in the bundle.

9. Read-only proof for this report: nothing under `docs/` was modified and `state/conwrt-issue32-evidence/checklist.md` was neither read nor written — `git status --porcelain docs state/conwrt-issue32-evidence/checklist.md` returns empty, and `docs/wizard-bundle.json` sha256 is still `6fe93f952fe68a53facd7d0a3561865377ccdd15beb3801cb4432b23a507277e`.
