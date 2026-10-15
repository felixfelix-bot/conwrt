# CF-WR632AX — preflight recovery plan (conwrt issue #32)

- Kanban task: `t_f948b651` — Preflight recovery check + pre-run baseline snapshot
- Worker: profile `worker-tollgate`, host `c03rad0r-DQ05proplus`
- Captured: 2026-10-15T09:34Z (2026-10-15 11:34 CEST)
- Mode: **read-only**. No `uci set`, no `uci commit`, no reboot, no config write of
  any kind was issued against any device.

## VERDICT — device NOT reached; recovery paths cannot be confirmed on hardware

The card asks for each recovery mechanism to be *"confirmed reachable on this
device"*. **That confirmation could not be obtained**, because the CF-WR632AX is
not reachable from this host by any documented path. Raw probe output:
`preflight-reachability.txt` (same directory). Summary of the blocking facts:

| Documented path | Probe | Result |
|---|---|---|
| SSH `root@192.168.1.1` | `ssh -o ConnectTimeout=8 root@192.168.1.1 'cat /etc/openwrt_release'` | timeout, no route (`192.168.1.0/24` is not on-link; route is via the home FritzBox) |
| ICMP `192.168.1.1` | `ping -c3 -W2 192.168.1.1` | 100% packet loss |
| TCP `192.168.1.1` :22/:80/:443/:53 | `/dev/tcp` connect | all closed / unreachable |
| ARP for COMFAST OUI `40:a5:ef` | `ip neigh \| grep -i 40:a5:ef` | no match, before and after a full LAN sweep |
| LAN sweep (host's own LAN) | `192.168.2.1-254` ICMP sweep | 17 hosts answered, none with a COMFAST OUI |
| WiFi beacon (2.4 + 5 GHz) | `iw dev wlp2s0 scan` | no `40:a5:ef` BSSID |
| Serial console | `ls /dev/ttyUSB* /dev/ttyACM*` | none on this host; `lsusb` shows no USB-serial adapter |

Consequence for the acceptance criteria: **`pre-run-uci-export.txt` and
`clock-sync-pre.txt` carry no device-side data** — that data does not exist. Those
two files ship with an explicit `BLOCKED` record plus the host-side reference
values, rather than invented device output. No fabricated snapshot was created.

**Operator action required before this card can pass:** power the CF-WR632AX
(USB-C 5V/3A) *and* attach its LAN port to a path this host can see — either
directly on `192.168.1.0/24`, or onto the host's LAN (`192.168.2.0/24`) with the
resulting IP reported to the worker, or attach a 3.3V USB-serial adapter to the
UART header (see §1). Then re-dispatch `t_f948b651`.

## 0. Device identity and documented connection details (from the repo)

Source: `models/comfast-cf-wr632ax.json`, `AGENTS.md`, `docs/gotchas.md`.

| Fact | Value |
|---|---|
| Model id / OpenWrt device | `comfast-cf-wr632ax` / `comfast,cf-wr632ax` |
| Target / profile | `mediatek/filogic` / `comfast_cf-wr632ax` |
| SoC | MT7981B (Filogic 830) |
| Documented LAN IP (stock **and** wizard default) | `192.168.1.1` |
| MAC OUI (ground truth for finding the unit) | `40:A5:EF` |
| UART | `3.3V 115200 8N1` |
| Power | USB-C 5V/3A (**not** PoE — a GS1900-8HP PoE port cannot power it) |
| Recovery HTTP (U-Boot) | reset held while powering on, release on 5 green LED flashes → `192.168.1.1`, client `192.168.1.2/24`, upload `/upload` field `firmware`, trigger `/result` |
| U-Boot TFTP | reset held >7 s → `192.168.1.1`, client `192.168.1.254/24` |
| Advanced UART recovery | `mtk_uartboot` with `bl2` + `fip` |
| Known trap | firmware randomises the LAN IP after factory reset (marker `/etc/config/95-random-lan-ip.done`) |
| Known trap | no specimen inventory was ever recorded and **no SSH key was ever installed** — see `AGENTS.md` "Inventory and Access Hardening After First Access" |

## 1. Recovery mechanism (a) — serial console

**Status on this device: NOT confirmed reachable.** No USB-serial adapter is
attached to this host (`ls /dev/ttyUSB* /dev/ttyACM* /dev/serial` → all missing;
`lsusb` lists only hubs, a Bluetooth radio, a Lexar ES4 stick and a USB audio/HID
device). The device's UART header has never been probed in this session and the
device is not powered/reachable, so neither end of the link can be verified.

### Exact steps to invoke (copy-pasteable, once an adapter is attached)

Per `AGENTS.md` "Serial Wiring: Verify Before Connecting" — **loopback test first**,
and **never connect VCC** (the device is USB-C powered):

```bash
# 1. adapter present?
ls -l /dev/ttyUSB*                     # note the port, e.g. /dev/ttyUSB0
python3 scripts/serial-console.py --diagnose

# 2. loopback: bridge adapter TX->RX, must echo 4 test patterns
python3 scripts/serial-console.py /dev/ttyUSB0 --loopback

# 3. wire: adapter TX -> device RX, adapter RX -> device TX, GND -> GND. NO VCC.
#    3.3V levels only (model JSON: hardware.uart = 3.3V 115200 8N1)

# 4. monitor (baud confirmed from the model JSON; AGENTS.md says re-verify from
#    the OpenWrt DTS chosen/stdout-path before trusting it)
python3 scripts/serial-console.py /dev/ttyUSB0 --baud 115200 --monitor \
    --session cf-wr632ax-preflight
# logs land in serial/cf-wr632ax-preflight/{console.log,console.raw,session.json}

# 5. while the console is open, power-cycle the device (USB-C) and watch for the
#    U-Boot prompt; a booted OpenWrt gives:  root@OpenWrt:~#
```

Expected observable proof of reachability: U-Boot boot messages followed by
`root@OpenWrt:~#` on the console (per `AGENTS.md` "Serial Console as
Configuration Interface"). Recorded as *confirmed* only when that prompt is
captured in `serial/<session>/console.log`.

### Commands usable from that root shell (recovery itself)

```bash
cat /etc/openwrt_release                 # firmware identity
uci show network                         # current LAN config
uci revert network ; uci commit network ; /etc/init.d/network restart
firstboot -y && reboot                   # full factory reset (destroys overlay!)
```

Pitfall (`AGENTS.md`): long pasted keys can wrap and drop the shell into
continuation mode (`>`); send Ctrl-C to break out.

## 2. Recovery mechanism (b) — OpenWrt failsafe-mode boot

**Status on this device: NOT confirmed reachable.** Failsafe needs the device
powered and its LAN port on a path the host can capture. Both are absent, so the
UDP-4919 broadcast could not be observed. The mechanism itself is implemented in
this repo and is the documented recovery for exactly the failure mode this issue
cares about (`docs/gotchas.md` §"Shell variable expansion in uci commands": restore
is *"Physical failsafe mode (hold reset during power cycle → boots at 192.168.1.1
ignoring overlay) → `firstboot -y && reboot` → re-run `conwrt configure`"*).

### Exact steps to invoke

Two supported forms. Preferred: the repo tool (it does the tcpdump detection and
the reset-button prompt for you).

```bash
# A. repo tool — full firstboot via failsafe (destructive; run only when intended)
python3 scripts/conwrt.py reset --ip 192.168.1.1 --interface <host-nic>
#   generates: sudo tcpdump -i <host-nic> -n -A --immediate-mode -l port 4919 and udp
#   on "Please press button now to enter failsafe" it prompts:
#     PRESS AND HOLD THE RESET BUTTON NOW. Hold for 2 seconds then release.
#   then waits 10 s, pings 192.168.1.1, sets <host-nic> to 192.168.1.2/24 and
#   runs: ssh root@192.168.1.1 'firstboot -y && reboot'
python3 scripts/conwrt.py reset --ip 192.168.1.1 --interface <host-nic> --dry-run
#   dry-run prints the exact commands without touching the device

# B. manual, no repo tooling
sudo tcpdump -Ani <host-nic> -c 1 -t 'port 4919 and udp'   # watch for the broadcast
# power-cycle the device; at the failsafe prompt press+hold reset ~2 s, release
sudo ip addr add 192.168.1.2/24 dev <host-nic>
ping -c3 192.168.1.1
ssh root@192.168.1.1                       # failsafe root shell (no password)
```

Expected observable proof of reachability: the literal tcpdump payload line
`Please press button now to enter failsafe` (matched verbatim by
`scripts/router-probe.py:174` and `scripts/conwrt/monitors.py:264`), followed by a
successful `ping` and an SSH login. Non-destructive probe of the same signal:
`python3 scripts/router-probe.py <iface> --probe failsafe_broadcast`.

**Warning:** failsafe gives a root shell *without* the overlay, but option (b) as
implemented above escalates to `firstboot -y` — that erases the overlay and the
randomised-LAN-IP marker. If the goal is only to undo one bad `uci` change, use
mechanism (c) instead, or stop at the failsafe shell and `uci revert`.

## 3. Recovery mechanism (c) — `uci revert` / config-backup restore

**Status on this device: NOT confirmed reachable** (no SSH, no serial, so the
on-device commands could not be executed or observed). This is the mechanism to
prefer for the net4sats run, because it is the only one that is **non-destructive**
— it undoes a bad `uci` change without erasing the overlay.

### Exact steps to invoke

Pre-flight (do this **before** any recipe step, while the device is still good):

```bash
# snapshot the whole config, keep it off-device
ssh root@<ip> 'uci export' > pre-run-uci-export.txt
ssh root@<ip> 'cp /etc/config/network /tmp/network.bak'
ssh root@<ip> 'cp -a /etc/config /tmp/config-bak-$(date -u +%Y%m%dT%H%M%SZ)'
```

Undo a change that has **not** been committed:

```bash
ssh root@<ip> 'uci revert network'            # single package
ssh root@<ip> 'uci revert network system'     # or several
ssh root@<ip> 'uci changes'                   # what is staged-but-uncommitted
```

Undo a change that **has** been committed (restore the snapshot, then re-read it):

```bash
ssh root@<ip> 'cp /tmp/network.bak /etc/config/network && uci commit network'
ssh root@<ip> '/etc/init.d/network restart'
ssh root@<ip> 'uci get network.lan.ipaddr'    # read-back MUST equal the pre-run value
```

Revert without a reboot (documented in `docs/fieldlab.md:253`):

```bash
ssh root@<ip> 'uci revert network; ifup wan'
```

**Critical caveat from `AGENTS.md`:** *"For UBIFS overlay devices: `uci commit` is
permanent after reboot — there is no 'undo' after reboot."* So `uci revert` only
helps **before** the commit or before the reboot. After a reboot the only in-band
undo is restoring a saved config file; after that, failsafe (§2) or serial (§1).
`docs/gotchas.md:340` records a real incident where a `network restart` lost the
SSH key and password because UBIFS write-back had not been committed — keep an
off-device snapshot and an installed SSH key (which this specimen does **not**
have, per `AGENTS.md`).

### Ordering recommendation for the net4sats run

1. Snapshot (above) — mandatory, and re-taken by `t_28198bdb` step 1.
2. Run the guard/negative test (`lan_ip` left as `{{lan_ip}}`) — non-destructive.
3. Move the LAN, then immediately read back `uci get network.lan.ipaddr`.
4. If the read-back is wrong: `uci revert network` **before** any commit/reboot.
5. If the device is lost anyway: failsafe (§2) → `uci revert` or snapshot restore
   → `firstboot` only as the last resort.

## 4. What was and was not confirmed (honest acceptance ledger)

| Acceptance item | Result |
|---|---|
| recovery-plan.md lists each recovery mechanism with exact commands | **DONE** — §1, §2, §3, each with copy-pasteable commands and the exact prompt/broadcast to expect |
| …and a statement that it was confirmed reachable **on this device** | **NOT SATISFIED** — all three are recorded as *not confirmed*; the device is unreachable by every documented path (see the verdict table at the top). Confirming any of them requires the operator action in the verdict section |
| pre-run-uci-export.txt exists, non-empty, carries a timestamp | **exists + timestamped + non-empty, but BLOCKED** — no `uci export` output could be produced (no device); the file states this explicitly and contains the host-side reference instead |
| clock-sync-pre.txt exists with date, NTP status, synchronized/drift note | **exists, but BLOCKED** — no on-device `date -u` / NTP status / drift could be produced; the file carries the host reference clock and an explicit NO-GO |
| No config was modified | **PASS** — no `uci` write, no reboot, no config write reached any device; every command in `preflight-reachability.txt` is read-only |

**Bottom line for the run task (`t_28198bdb`) and the persistence task
(`t_8602bc75`): NO-GO until the device is reachable.** Do not start the recipe.


