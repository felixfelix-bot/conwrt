## tollgate

**Recipe:** `docs/wizard-bundle.json` — key path `rendered["comfast-cf-wr632ax"]["tollgate"]["25.12.4"]` (`.shell` = authoritative emission, `.markdown` = mirror). Raw JSON: `"shell"` at line 372, `"markdown"` at line 373 of the checked-out `pr-55` bundle (HEAD `4f169a2`).

**Where the LAN-move lives:** it is the final step of the flow. `flows[1]` is `{"name": "tollgate"}`; its LAN-move is the last step (`kind="set_lan_ip"`, built by `lan_finalize_step()`, `scripts/flows/tollgate.py:35` ← `scripts/flows/_gateway.py:75-80`). In the rendered shell it is the last block — script lines 62-72 of 73 — and nothing follows it but a trailing blank line.

**GAP (read this before quoting the input note):** the body names `state/conwrt-issue32-evidence/tollgate-lan-move.md` as INPUT. That file **does not exist on the checked-out branch** (`pr-55` @ `4f169a2`) — `find . -name 'tollgate-lan-move.md'` returns nothing outside `.git`, and `state/conwrt-issue32-evidence/` contains only `_frag-net4sats.md`, `drafts/`, `net4sats/`, `preflight-validation.md` and `workaround-did-structure-findings.md` (there is no `checklist.md` either). Both the recipe path and the JSON key path above were therefore **re-derived directly from `docs/wizard-bundle.json`** this run, and every line/offset citation below comes from that re-derivation, not from the missing note.

**Two render modes, one safety invariant** (`scripts/flows/render.py:149-200`, `_identity_lan_ops`): when `lan_ip` is still a `{{placeholder}}` the render is a self-guarding script; when it is a concrete address the render validates it as IPv4 up front and sets the literal. Both read the value back with `uci get` before committing. The `comfast-cf-wr632ax` tollgate cast below is the **derived-value** mode (`LAN_IP='{{lan_ip}}'`), i.e. the wizard fills `lan_ip` client-side; both blocks are given verbatim so a reviewer can see exactly what the checked-out recipe emits.

### (a) LAN-move block (verbatim)

```
# --- Move the LAN off 192.168.1.1 ---
ssh root@$IP sh <<'CONWRT_EOF'
# move LAN off 192.168.1.1 → identity-derived CGNAT address (100.64.0.0/10)
LAN_IP='{{lan_ip}}'
case "$LAN_IP" in ""|*"{"*) echo "ERROR: lan_ip was not filled in. Derive this device's CGNAT LAN address:" ; echo "  python3 scripts/derive_device_secret.py --mnemonic <fleet> --mac <mac>   (ipv4 field)" >&2 ; exit 1;; esac
uci set network.lan.ipaddr="$LAN_IP"
uci set network.lan.netmask='255.255.255.0'
uci get network.lan.ipaddr | grep -qxF "$LAN_IP" || { echo 'ERROR: uci read-back mismatch for network.lan.ipaddr' >&2 ; exit 1 ; }
uci commit network
(/etc/init.d/network restart &) ; echo "LAN moving to $LAN_IP — reconnect on that subnet"
CONWRT_EOF
```

The `→` and `—` are literal UTF-8 in the emitted script (JSON stores them as `\u2192` / `\u2014`). The three spaces in `--mac <mac>   (ipv4 field)` are verbatim.

### (b) Read-back block (verbatim)

```
uci get network.lan.ipaddr | grep -qxF "$LAN_IP" || { echo 'ERROR: uci read-back mismatch for network.lan.ipaddr' >&2 ; exit 1 ; }
```

Emitted **inside the same heredoc**, after the `uci set` pair (shell lines 67-68) and **before** `uci commit network` (shell line 70) — the AGENTS.md set/get/commit discipline. `grep -qxF` demands a full-line exact match against the bound value; on mismatch it writes `ERROR: uci read-back mismatch for network.lan.ipaddr` to stderr and exits 1, which fails the `ssh … sh` invocation and — the host script runs `set -e` (shell line 5) — aborts the recipe before the commit. Guard behaviour: with `lan_ip` empty or still `{{lan_ip}}`, the `case` pattern `""|*"{"*` fires **before any `uci set`** (exit 1, message on stdout, the derive hint on stderr), so an unfilled placeholder can never reach `uci set`.

**Where the derived ipv4 enters the block:** `LAN_IP='{{lan_ip}}'` — shell line 65 of `rendered["comfast-cf-wr632ax"]["tollgate"]["25.12.4"].shell`, i.e. raw JSON line 372 of `docs/wizard-bundle.json` (pr-55, char offset 3127) — binding flow param `flows[1].params.lan_ip` (raw JSON line 326, declaration at `scripts/flows/_gateway.py:36-44` via `gateway_params()`) through `scripts/flows/render.py` (`_identity_lan_ops`, line 166-169 `LAN_IP={sh_quote(lan_ip)}`); the wizard fills it with the `ipv4` field of `scripts/derive_device_secret.py --mnemonic <fleet> --mac <mac>`, and every later line (guard, `uci set` line 67, read-back line 69, echo line 71) consumes `$LAN_IP` — never a literal, never an unresolved `{{lan_ip}}`.

**Provenance verdict (tollgate, checked-out bundle):** APPLIES DERIVED VALUE. The block binds the flow's `lan_ip` param to `$LAN_IP` and applies exactly that value with `uci set network.lan.ipaddr="$LAN_IP"` (double-quoted, per the AGENTS.md expansion rule) plus a `uci get` read-back before commit, and its guard exits 1 before any write when the param is empty or still a placeholder — it cannot silently fall back to the literal `192.168.1.1`. This holds **only** for the CF-WR632AX cast: the other 32 device renders of the tollgate flow (and the 32 net4sats renders besides CF-WR632AX) still emit a baked literal `uci set network.lan.ipaddr='10.x.y.1'` with **no** `LAN_IP` binding, **no** guard and **no** read-back — verified by enumerating every `rendered[*][*][*].shell` this run (`LAN_IP=` present → derived+guard; absent → literal, no-guard). Each literal differs from the default `192.168.1.1` (e.g. `10.231.9.1` for asus-lyra-map-ac2200), so those variants do move the LAN, but silently and without the read-back guarantee; they come from the `_set_lan_ip_ops` fallback branch (`scripts/flows/render.py:208-219`) because their flow was rendered with no `lan_ip` value.
