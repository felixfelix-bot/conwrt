### tollgate LAN-move

**Recipe:** `docs/wizard-bundle.json` — key path `rendered["comfast-cf-wr632ax"]["tollgate"]["25.12.4"]`,
sub-key `.shell` (the authoritative emission, raw JSON line 372) with `.markdown` (line 373) as its mirror.
The LAN move is the final step of the flow (`flows[1] = {"name": "tollgate"}`, param declaration raw JSON
line 326); in the emitted shell it is the last block — shell lines 62-72 of 73 — and nothing follows it but
a trailing blank line. Bundle identity: 868 lines, `generated_at` present; repo `conwrt`, branch `pr-55`,
HEAD `391bf7741c52e6f96c196d8a30c29fc263f0fdb8`. Both revisions available on this host (`391bf77` and the
review branch `ec5c60d`) carry a byte-identical `docs/wizard-bundle.json` — `git diff ec5c60d 391bf77 --
docs/wizard-bundle.json scripts/flows/` is empty — so every citation below holds for both.

#### (a) LAN-move block — verbatim (shell lines 62-72)

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

#### (b) Read-back block — verbatim (shell line 69)

```
uci get network.lan.ipaddr | grep -qxF "$LAN_IP" || { echo 'ERROR: uci read-back mismatch for network.lan.ipaddr' >&2 ; exit 1 ; }
```

It is not a second emission: it is line 69 of the same heredoc, i.e. line 8 of the block above, emitted after
both `uci set` lines (67-68) and **before** `uci commit network` (70) — the AGENTS.md set/get/commit discipline.
`grep -qxF` demands a whole-line fixed-string exact match against the bound value; on mismatch it writes
`ERROR: uci read-back mismatch for network.lan.ipaddr` to stderr and exits 1, which fails the `ssh … sh`
invocation, and the host script runs `set -e` (shell line 5) so the recipe aborts before the commit/reconnect.

**Byte-exactness:** both blocks above were re-extracted this run directly from the JSON string
(`rendered["comfast-cf-wr632ax"]["tollgate"]["25.12.4"].shell`, split on `\n`, taking indices 61-71 and 68)
and diffed clean against the tracked `state/conwrt-issue32-evidence/_frag-tollgate.md` blocks — zero diff,
no rewrap/re-indent/quote "fix". `→` (U+2192) and `—` (U+2014) are literal UTF-8 in the emitted script (the
JSON stores them as `\u2192`/`\u2014`); the three spaces in `--mac <mac>   (ipv4 field)` are verbatim; the
guard on shell line 66 is one physical line — do not wrap it.

#### Where the derived ipv4 enters, and the provenance verdict

**Derived ipv4 enters at `docs/wizard-bundle.json:372`** — `rendered["comfast-cf-wr632ax"]["tollgate"]["25.12.4"].shell`
line 65 (`LAN_IP='{{lan_ip}}'`), the param binding for `flows[1].params.lan_ip` (raw JSON line 326, declared
`scripts/flows/_gateway.py:36-44` via `gateway_params()`) rendered by `scripts/flows/render.py`
(`_identity_lan_ops`, `LAN_IP={sh_quote(lan_ip)}`). The wizard fills that param with the `ipv4` field of
`python3 scripts/derive_device_secret.py --mnemonic <fleet> --mac <mac>`.

**Provenance verdict: APPLIES THE DERIVED VALUE — it cannot silently fall back to a literal, and it cannot
reach a write with an unresolved placeholder.** Evidence: every line after the binding consumes `$LAN_IP`
(guard line 66, `uci set network.lan.ipaddr="$LAN_IP"` line 67, read-back line 69, echo line 71); there is no
hardcoded `192.168.1.1` write anywhere in the block — the only two occurrences of `192.168.1.1` are the
human-readable comment (line 62) and echo text (line 64). If the param is empty or still `{{lan_ip}}`, the
guard's `case` pattern `""|*"{"*` fires **before any `uci set`** (message on stdout, derive hint on stderr,
`exit 1`), so an unfilled placeholder can never be written to the device.

**Scope caveat — the opposite holds for every other render in the bundle.** The derived+guarded form is
CF-WR632AX-only. Enumerating every `rendered[*][*][*].shell` (85 renders) yields exactly **2** with a
`LAN_IP=` binding (the CF-WR632AX net4sats and tollgate casts) and **83** emitting a baked literal
`uci set network.lan.ipaddr='10.x.y.1'` with **no** `LAN_IP` binding, **no** guard and **no** read-back
(e.g. `10.231.9.1` for `asus-lyra-map-ac2200`), from the `_set_lan_ip_ops` fallback branch
(`scripts/flows/render.py:208-219`). Those variants do move the LAN off `192.168.1.1`, but silently and
without the read-back guarantee.

**GAP: the two inputs this draft was told to read do not exist.** `state/conwrt-issue32-evidence/drafts/tollgate-blocks.txt`
and `state/conwrt-issue32-evidence/drafts/tollgate-provenance-notes.md` are absent from the workspace, absent
from the repo at HEAD `391bf77` (`ls state/conwrt-issue32-evidence/drafts/` holds only `net4sats-verification.md`
and `provenance-verification.md`; none of the three is tracked by git), and absent anywhere on this host —
a `find /home/c03rad0r -maxdepth 8` for both names returns nothing. They were never produced: their producer
cards `t_7045c59a` (*Extract verbatim LAN-move + read-back command blocks into tollgate-blocks.txt*) and
`t_bf9f349a` (*Trace derived-ipv4 provenance in tollgate LAN-move recipe*) are still in `triage` on the board,
and the task body's other named input `state/conwrt-issue32-evidence/tollgate-lan-move.md` is likewise
untracked and non-existent (its own extract card `t_7a1d7cd0` is `blocked`). This draft was therefore
re-derived from the primary source instead: `docs/wizard-bundle.json` (read-only) plus the tracked fragment
`state/conwrt-issue32-evidence/_frag-tollgate.md` (committed at HEAD `391bf77`), which is the only surviving
copy of the block and is what the byte-exactness diff above was run against. All line/offset citations here
come from that re-derivation.

**GAP: the expected `lan_ip` value is not recorded anywhere in this evidence set.** Per the companion card
`t_bff496fe` (recorded in `state/conwrt-issue32-evidence/checklist.md`), the canonical CF-WR632AX `lan_ip`
could not be derived — the fleet mnemonic is absent from this host and the designated runbook does not exist —
so the value is `PENDING` and `100.110.24.1` (the public BIP39 test vector) is explicitly **not** the device
value. Everything above about the block's shape and provenance is unaffected; only a live worker holding the
mnemonic can print the concrete address.

**GAP: the `{{lan_ip}}` token quoted above is a FINDING, not draft placeholder text.** It is the verbatim
content of the recipe at raw JSON line 372 / shell line 65 and is unresolved *in the bundle by design* — the
wizard substitutes it client-side. It is reproduced here to document that the checked-out recipe contains an
unsubstituted token at that point, which is exactly what the guard on the next line defends against.
