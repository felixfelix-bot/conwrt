# Provenance verification — LAN-move and read-back, net4sats and tollgate

Synthesis of (a) the completion note of the evidence-extraction task t_d12347f6, (b) the tollgate per-flow audit task t_6896af59 and its audit chain (t_960feef0 -> t_c3a46b44 -> t_3f7d705a -> {t_7c40904e, t_fb6e57f0} -> t_c5842c60), and (c) the net4sats per-flow audit task t_0db786fa (see DISCLOSURE below), tested against the two worker notes
state/conwrt-issue32-evidence/net4sats-lan-move.md and state/conwrt-issue32-evidence/tollgate-lan-move.md (claims only).

Evidence base (read-only, unmodified by this task): `/home/c03rad0r/repos/conwrt`, branch `feat/vpn-provider-setup`, HEAD `9c8282d84f47036e009c9c0a31bf3932e32526aa`; `docs/wizard-bundle.json` sha256 `6fe93f952fe68a53facd7d0a3561865377ccdd15beb3801cb4432b23a507277e` (614953 bytes, 854 physical lines).

Every quoted line below is copied byte-identically from the raw bytes of `docs/wizard-bundle.json`. The backslash sequences (`\n`, `\u2192`, `\u2014`) are literal JSON string escapes present in the file; none of them is whitespace or punctuation added by this document. Whole-file fixed-string counts used below were re-run against the same file: `{{lan_ip}}` = 0, `uci get` = 0, `uci show` = 0, `ip addr` = 0, `ubus call` = 0, `derive_device_secret` = 0, `lan_gateway` = 0, `"lan_subnet"` (as a JSON key) = 0.

**DISCLOSURE — the designated net4sats audit produced no note.** The sibling audit task t_0db786fa ("Audit net4sats LAN-move and read-back provenance claims") never produced a completion note; its last runs are `blocked`. No net4sats-authored `CORRECTION:` line exists to carry over. Where a net4sats CORRECTION line appears below it is quoted verbatim from the auditor of the identical shared LAN-move step (t_7c40904e, which records "Both flows render the identical LAN-move step"), and the two `comfast-cf-wr632ax` slots were re-verified byte-identical by direct extraction (LAN-move tail sha256 `2001e0470860ca02c09386af40ec098af7c0631a6f34fc4cdf13a13de34c481a`, 337 characters, in both flows). No verdict text has been reworded, softened or strengthened.

---

## net4sats

Flow name: **net4sats** — `flows[0].name`, physical line 262:

```text
      "name": "net4sats",
```

JSON key path(s) inspected:

- `rendered["asus-lyra-map-ac2200"]["net4sats"]["24.10.7"].shell` (physical line 330) — the LAN-move block is the final section of this shell string.
- `rendered["asus-lyra-map-ac2200"]["net4sats"]["24.10.7"].markdown` (physical line 331) — markdown transport of the same slot.
- `rendered["comfast-cf-wr632ax"]["net4sats"]["25.12.4"].shell` (physical line 352) — byte-identical LAN-move tail to the tollgate slot corrected below.
- Read-back key path: **NONE**. No read-back block exists for this flow anywhere in the bundle.

Verbatim quoted evidence — LAN-move tail of physical line 330, key path `rendered["asus-lyra-map-ac2200"]["net4sats"]["24.10.7"].shell` (raw file bytes):

```text
# --- Move the LAN off 192.168.1.1 ---\nssh root@$IP sh <<'CONWRT_EOF'\n# move LAN off 192.168.1.1 \u2192 10.231.9.1 (10.231.9.0/24)\nuci set network.lan.ipaddr='10.231.9.1'\nuci set network.lan.netmask='255.255.255.0'\nuci commit network\n(/etc/init.d/network restart &) ; echo 'LAN moving to 10.231.9.1 \u2014 reconnect on that subnet'\nCONWRT_EOF\n
```

Verbatim quoted evidence — LAN-move tail of physical line 352, key path `rendered["comfast-cf-wr632ax"]["net4sats"]["25.12.4"].shell` (raw file bytes):

```text
# --- Move the LAN off 192.168.1.1 ---\nssh root@$IP sh <<'CONWRT_EOF'\n# move LAN off 192.168.1.1 \u2192 192.168.1.1 (192.168.1.0/24)\nuci set network.lan.ipaddr='192.168.1.1'\nuci set network.lan.netmask='255.255.255.0'\nuci commit network\n(/etc/init.d/network restart &) ; echo 'LAN moving to 192.168.1.1 \u2014 reconnect on that subnet'\nCONWRT_EOF\n
```

Verbatim quoted evidence — the applied-value line, byte-identical in both key paths above:

```text
uci set network.lan.ipaddr='10.231.9.1'
```

Read-back quoted evidence: **none exists**. The shell string quoted above terminates immediately after `CONWRT_EOF\n`; there is no read-back statement to quote for this flow. Absence evidence over the whole bundle: `uci get` = 0, `uci show` = 0, `ip addr` = 0, `ubus call` = 0.

**LAN-move verdict: CORRECTED** (auditor verdict: UNSAFE). The net4sats note's label is "APPLIES DERIVED VALUE". Under the auditors' rule — SAFE only when the binding to `derive_device_secret.py` output is explicit and traceable — the LAN-move text is a generate-time per-model literal frozen into the bundle, so the label is superseded by UNSAFE. Correction carried over verbatim (same text the auditor emitted for the byte-identical shared step; no net4sats-authored correction line exists — see DISCLOSURE):

```correction
CORRECTION: APPLIES DERIVED VALUE -> UNSAFE
```

  Key path: `rendered["comfast-cf-wr632ax"]["net4sats"]["25.12.4"].shell` (physical line 352).
  Verbatim evidence:

```text
uci set network.lan.ipaddr='192.168.1.1'
```

**Read-back verdict: CORRECTED** (auditor verdict: UNSAFE, absent binding). The net4sats note determines read-back to be ABSENT but attaches no verdict to that absence; under the read-back rule the absence *is* the UNSAFE condition. Correction carried over verbatim (same text the auditor emitted for the byte-identical shared step):

```correction
CORRECTION: READ-BACK NONE (no read-back command; unlabeled) -> UNSAFE (absent binding)
```

  Key path: `rendered["comfast-cf-wr632ax"]["net4sats"]["25.12.4"].shell` (physical line 352); inspected counterpart `rendered["asus-lyra-map-ac2200"]["net4sats"]["24.10.7"].shell` (physical line 330).
  Verbatim evidence: the block quoted above writes the address and commits unconditionally;
  the only later repetition of the address is the hardcoded echo inside the same shell string:

```text
(/etc/init.d/network restart &) ; echo 'LAN moving to 192.168.1.1 \u2014 reconnect on that subnet'
```

---

## tollgate

Flow name: **tollgate** — `flows[1].name`, physical line 292:

```text
      "name": "tollgate",
```

JSON key path(s) inspected:

- `rendered["comfast-cf-wr632ax"]["tollgate"]["25.12.4"].shell` (physical line 358) — the LAN-move block is the final section of this shell string.
- `rendered["comfast-cf-wr632ax"]["tollgate"]["25.12.4"].markdown` (physical line 359) — markdown transport of the same slot.
- Read-back key path: **NONE**. No read-back block exists for this flow anywhere in the bundle.

Verbatim quoted evidence — LAN-move tail of physical line 358, key path `rendered["comfast-cf-wr632ax"]["tollgate"]["25.12.4"].shell` (raw file bytes):

```text
# --- Move the LAN off 192.168.1.1 ---\nssh root@$IP sh <<'CONWRT_EOF'\n# move LAN off 192.168.1.1 \u2192 192.168.1.1 (192.168.1.0/24)\nuci set network.lan.ipaddr='192.168.1.1'\nuci set network.lan.netmask='255.255.255.0'\nuci commit network\n(/etc/init.d/network restart &) ; echo 'LAN moving to 192.168.1.1 \u2014 reconnect on that subnet'\nCONWRT_EOF\n
```

Verbatim quoted evidence — the applied-value line, same key path, physical line 358:

```text
uci set network.lan.ipaddr='192.168.1.1'
```

Read-back quoted evidence: **none exists**. The shell string quoted above terminates immediately after `CONWRT_EOF\n`; there is no read-back statement to quote for this flow. Absence evidence over the whole bundle: `uci get` = 0, `uci show` = 0, `ip addr` = 0, `ubus call` = 0.

**LAN-move verdict: CORRECTED** (auditor verdict: UNSAFE). The note's label "APPLIES DERIVED VALUE" is a provenance label, not a SAFE/UNSAFE verdict; under the audit rule it is superseded by UNSAFE. Correction carried over verbatim:

```correction
CORRECTION: APPLIES DERIVED VALUE -> UNSAFE
```

  Key path: `rendered["comfast-cf-wr632ax"]["tollgate"]["25.12.4"].shell` (physical line 358; shell-string line 65).
  Verbatim evidence:

```text
uci set network.lan.ipaddr='192.168.1.1'
```

**Read-back verdict: CORRECTED** (auditor verdict: UNSAFE, mismatch class = absent binding). The note states read-back is absent but declares the absence a caveat that does not change its verdict; the auditor corrects that framing. Correction carried over verbatim:

```correction
CORRECTION: READ-BACK NONE (no read-back command; unlabeled) -> UNSAFE (absent binding)
```

  Key path: `rendered["comfast-cf-wr632ax"]["tollgate"]["25.12.4"].shell` (physical line 358).
  Verbatim evidence: the block quoted above writes the address and commits unconditionally; the only later repetition of the address is the hardcoded echo inside the same shell string:

```text
(/etc/init.d/network restart &) ; echo 'LAN moving to 192.168.1.1 \u2014 reconnect on that subnet'
```

---

## Summary

Neither flow risks a silent fallback to an unresolved placeholder at this revision: the whole-file count of `{{lan_ip}}` in `docs/wizard-bundle.json` is 0, and the address each flow applies is a generate-time per-model value (the model's `lan_subnet` network address + 1), not a hand-written literal — so there is no unresolved-placeholder fallback and no hardcoded-literal fallback either; the silent-failure mode the auditors identified is instead the total absence of any read-back (`uci get`, `uci show`, `ip addr`, `ubus call` each occur 0 times in the whole bundle), meaning neither flow ever verifies that the value it wrote took effect. The JSON key path responsible, if a silent fallback were to occur, is the LAN-move text inside `rendered["comfast-cf-wr632ax"]["net4sats"]["25.12.4"].shell` (physical line 352) and its byte-identical sibling `rendered["comfast-cf-wr632ax"]["tollgate"]["25.12.4"].shell` (physical line 358): for that model the written value is `192.168.1.1`, which equals the OpenWrt default, so the "Move the LAN off 192.168.1.1" step is a no-op that no read-back detects; the same key path carries `10.231.9.1`-class values for the other 21 models. The one revision where this key path does carry an unresolved placeholder is pr-55 (`ec5c60d9`), where, per the auditor record (not re-verified in this task), `{{lan_ip}}` occurs 4 times on bundle lines 366/367/372/373; that revision is not an ancestor of this HEAD.

