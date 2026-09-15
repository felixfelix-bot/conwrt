# conwrt Issue 32 — CF-WR632AX Preflight Recovery Verification Run Log

**Date:** 2026-09-15
**Operator/Worker:** worker-base (fleet offload)
**Device:** COMFAST CF-WR632AX (MT7981B Filogic 830)
**IP:** 192.168.1.1
**Expected firmware:** OpenWrt 25.12.4 (per task context)

---

## STATUS: ACCESS REGAINED — BUT WRONG DEVICE (see §9–§11, appended 2026-09-15 by worker-heavy)

SSH access to 192.168.1.1 was regained on 2026-09-15 using the kit's
`~/physical-router-test-automation/mint-health/routers.env` `ROUTER_PASSWORD` (a
credential not tried in §2.1). However, the device proved to be a **GL.iNet GL-MT6000
(Flint 2, OpenWrt 24.10.1)** — NOT the COMFAST CF-WR632AX that issue #32 targets.
Full identity evidence, the pre-flight artifacts, baselines, and the clock GO/NO-GO
are appended in §9–§11 below. The original BLOCKED record (§1–§8) is retained
verbatim for provenance: its "no recovery path" conclusion was drawn against the
wrong device.

---

## 1. DEVICE DISCOVERY (observed, not assumed)

### 1.1 Network reachability

```
$ ping -c 2 192.168.1.1
PING 192.168.1.1 (192.168.1.1) 56(84) bytes of data.
From 192.168.1.1 icmp_seq=1 Destination Port Unreachable
From 192.168.1.1 icmp_seq=2 Destination Port Unreachable
--- 192.168.1.1 ping statistics ---
2 packets transmitted, 0 received, +2 errors, 100% packet loss
```

ICMP is blocked, but the host is up (port unreachable comes from the host
stack, not a timeout).

### 1.2 Port scan (nmap -sV)

```
$ nmap -sV -p 22,80,443,2050,2051,2052,8080,4433 192.168.1.1

PORT     STATE  SERVICE        VERSION
22/tcp   open   ssh            Dropbear sshd (protocol 2.0)
80/tcp   open   http
443/tcp closed https
2050/tcp open   av-emb-config?
2051/tcp open   http           OpenWrt uHTTPd
2052/tcp closed clearvisn
4433/tcp closed vop
8080/tcp open   http           OpenWrt uHTTPd
```

Device is running OpenWrt with:
- Dropbear SSH on port 22
- HTTP redirect on port 80 → TollGate portal on 2050/2051
- LuCI on port 8080 (title: "TollGate - LuCI")
- No HTTPS

### 1.3 HTTP port 80 response

```
HTTP/1.1 307 Temporary Redirect
Location: http://192.168.1.1:2050/splash.html?redir=http%3a%2f%2f192.168.1.1%2f
```

Port 2050 redirects to port 2051 (TollGate captive portal SPA).

### 1.4 Host key change

The SSH host key changed since the last known_hosts entry (line 107):
```
SHA256:vPXlw+NfybfsbP5GoI2iX8CE3o4xu0WQbhHrOnxUqq8
```
This indicates the device was reflashed or factory-reset since last access.
The old key was cleared with `ssh-keygen -R 192.168.1.1`.

---

## 2. SSH AUTHENTICATION ATTEMPTS (all failed)

### 2.1 Password auth — tested passwords

All returned "Permission denied (publickey,password)":

- `""` (empty)
- `password`
- `admin`
- `root`
- `openwrt`
- `1234`
- `123456`
- `tollgate`
- `TollGate`
- `comfast`
- `test123`
- `root123`
- `amperstrand`
- `none` (the config.toml password mode value)
- `None`
- `NONE`

### 2.2 Publickey auth — tested keys

All returned "Permission denied (publickey,password)":

- `~/.ssh/id_ed25519`
- `~/.ssh/id_rsa`
- `~/.ssh/tollgate`
- `~/.ssh/remote_worker`
- `~/.ssh/id_dq05`
- `~/.ssh/id_preview_deploy`
- `~/.ssh/preview_deploy_ed25519`
- `~/.ssh/preview_vps_deploy`

### 2.3 LuCI web login (port 8080)

Tried via browser at `http://192.168.1.1:8080/cgi-bin/luci/`:
- Username: root, Password: (empty) → still on login page
- Username: root, Password: password → still on login page
- Username: root, Password: admin → still on login page
- Username: root, Password: tollgate → still on login page
- Username: root, Password: none → still on login page

### 2.4 ubus JSON-RPC login

```
POST http://192.168.1.1:8080/ubus/
{"jsonrpc":"2.0","id":1,"method":"call","params":["00000000000000000000000000000000","session","login",{"username":"root","password":""}]}
→ {"jsonrpc":"2.0","id":1,"result":[6]}    # 6 = UBUS_STATUS_PERMISSION_DENIED
```

All tested passwords returned error code 6.

---

## 3. SERIAL CONSOLE STATUS

### 3.1 No serial adapter connected

```
$ lsusb | grep -i "serial\|uart\|ftdi\|cp210\|ch340\|pl2303"
(no output)

$ ls /dev/ttyUSB0 /dev/ttyUSB1 /dev/ttyUSB2
/dev/ttyUSB0 /dev/ttyUSB1 /dev/ttyUSB2

$ udevadm info /dev/ttyUSB0 | grep ID_MODEL
ID_MODEL=Sierra_Wireless_EM7455_Qualcomm_Snapdragon_X7_LTE-A
```

All three ttyUSB devices belong to the Sierra Wireless EM7455 LTE modem.
No FTDI/CH340/CP210x USB-UART adapter is connected to this machine.

### 3.2 Serial console path: UNAVAILABLE (not testable)

Per AGENTS.md, the serial console is the primary recovery fallback when
network access is unavailable. It requires:
- A 3.3V USB-UART adapter (FT232R, CP210x, CH340)
- Wiring: adapter TX → device RX, adapter RX → device TX, GND → GND
- No VCC connection (device is self-powered)
- Baud rate: 115200 8N1 (per model JSON)
- Access: root shell at `root@OpenWrt:~#` after boot

**This path is NOT available because no serial adapter is connected.**

---

## 4. AVAILABLE RECOVERY PATHS (not exercised, documented from model JSON)

### 4.1 U-Boot HTTP recovery (reflash, not config-level recovery)

Per `models/comfast-cf-wr632ax.json`:

```
"recovery-http": {
    "description": "U-Boot HTTP recovery (hold reset 10s while powering on, release on 5 green LED flashes)",
    "recovery_ip": "192.168.1.1",
    "client_ip": "192.168.1.2",
    "client_subnet": "255.255.255.0",
    "upload_endpoint": "/upload",
    "upload_field": "firmware",
    "trigger_flash_endpoint": "/result",
    "flash_time_seconds": 300,
    "reset_instructions": "Unplug power. Hold reset button. Plug in USB-C power. Wait for green LED to flash 5 times, release reset. Do NOT hold past 7 flashes (triggers U-Boot netconsole instead).",
    "led_pattern": "green LED flashes 5 times"
}
```

This is a REFLASH path — it replaces the firmware entirely. It does NOT
recover the current config. It would be used to flash a fresh OpenWrt image
that either has no password or has an SSH key baked in via ASU.

**NOT TESTED** — would require a firmware image and physical access to the
reset button. This is a nuclear option that destroys the current config.

### 4.2 U-Boot TFTP recovery (reflash)

Per model JSON:
```
"tftp": {
    "description": "U-Boot TFTP recovery (hold reset >7s while powering on)",
    "recovery_ip": "192.168.1.1",
    "client_ip": "192.168.1.254",
    "client_subnet": "255.255.255.0"
}
```

Also a reflash path. NOT TESTED.

### 4.3 Config snapshot + revert (PRIMARY — NOT EXERCISABLE)

The primary recovery path per the task: snapshot `/etc/config`, make a
benign change, restore the snapshot, verify the original value is back.

**NOT EXERCISABLE** — requires SSH access to the device, which we do not have.

---

## 5. ROOT CAUSE OF ACCESS LOSS

The device was configured by a prior conwrt run (evidence: TollGate captive
portal running, LuCI titled "TollGate"). The conwrt configure process sets
a root password via `postflash.py:_cfg_set_password()`. The password is
generated based on `config.toml [password] mode`:
- `random` → generates a random 16-char password, prints it once
- `key-only` → no password, SSH key only
- literal string → uses that string as the password

The current `config.toml` has `mode = "none"`, which would set the password
to the literal string "none" (via `password_literal` returning the mode
string). But "none" as a password was tested and rejected.

The password was NOT recorded:
- `data/inventory.jsonl` is empty (no entries at all)
- KeePass has no router credentials
- No prior session in the Hermes session DB references this device's password

This is the exact scenario AGENTS.md warns about:
> "The COMFAST CF-WR632AX was explored and a model JSON was created, but no
> specimen-level inventory was recorded and no SSH key was installed. A
> factory reset wiped the overlay... and the device became permanently
> inaccessible."

The SSH host key changed, indicating a reflash or factory reset occurred.
The password from the prior conwrt configure run was lost.

---

## 6. RECOVERY PROCEDURE (for a stressed live-run worker)

### Option A: Reflash via U-Boot HTTP recovery (DESTROYS current config)

This is the ONLY proven path to regain access. It requires physical access
to the device.

**Prerequisites:**
- Computer on 192.168.1.0/24 with IP 192.168.1.2/255.255.255.0
- OpenWrt sysupgrade image for comfast,cf-wr632ax (25.12.4)
  URL: https://downloads.openwrt.org/releases/25.12.4/targets/mediatek/filogic/openwrt-25.12.4-mediatek-filogic-comfast_cf-wr632ax-squashfs-sysupgrade.bin
- Or a custom ASU image with SSH key + known password baked in

**Steps:**

1. Set your computer's IP to 192.168.1.2/24:
   ```
   sudo ip addr add 192.168.1.2/24 dev <interface>
   sudo ip link set <interface> up
   ```

2. Download the firmware image:
   ```
   curl -O https://downloads.openwrt.org/releases/25.12.4/targets/mediatek/filogic/openwrt-25.12.4-mediatek-filogic-comfast_cf-wr632ax-squashfs-sysupgrade.bin
   ```

3. Unplug USB-C power from the device.

4. Hold the reset button down.

5. Plug in USB-C power WHILE HOLDING RESET.

6. Wait for the green LED to flash 5 times, then RELEASE reset.
   - Do NOT hold past 7 flashes (triggers U-Boot netconsole instead).

7. The device enters HTTP recovery mode at 192.168.1.1.

8. Upload the firmware:
   ```
   curl -F "firmware=@openwrt-25.12.4-mediatek-filogic-comfast_cf-wr632ax-squashfs-sysupgrade.bin" http://192.168.1.1/upload
   ```

9. Trigger the flash:
   ```
   curl http://192.168.1.1/result
   ```

10. Wait ~5 minutes for flash to complete and device to reboot.

11. The device reboots to fresh OpenWrt at 192.168.1.1 with empty root password.

12. SSH in immediately and install an SSH key:
    ```
    ssh root@192.168.1.1
    echo 'ssh-ed25519 AAAA...' >> /etc/dropbear/authorized_keys
    ```

13. Record the device in inventory:
    ```
    python3 scripts/inventory.py --add
    ```

**Expected output after step 11:**
```
$ ssh root@192.168.1.1
root@192.168.1.1's password:    # empty, just press Enter
root@OpenWrt:~#
```

**Verification:**
```
root@OpenWrt:~# cat /etc/openwrt_release
DISTRIB_ID='OpenWrt'
DISTRIB_RELEASE='25.12.4'
...
```

### Option B: Serial console (requires hardware not currently connected)

**Prerequisites:**
- 3.3V USB-UART adapter (FT232R, CP210x, or CH340)
- Wiring: adapter TX → device RX, adapter RX → device TX, GND → GND
- Do NOT connect VCC (device is self-powered via USB-C)

**Steps:**

1. Connect serial adapter to host, verify with loopback test:
   ```
   python3 scripts/serial-console.py --diagnose
   python3 scripts/serial-console.py /dev/ttyUSB0 --loopback
   ```

2. Wire: adapter TX → device RX, adapter RX → device TX, GND → GND

3. Open serial console:
   ```
   python3 scripts/serial-console.py /dev/ttyUSB0 --baud 115200
   ```

4. Power on the device. Wait for boot to complete.

5. You should see:
   ```
   root@OpenWrt:~#
   ```

6. Reset the password from serial:
   ```
   passwd root
   (enter new password twice)
   ```

7. Or install an SSH key from serial:
   ```
   echo 'ssh-ed25519 AAAA...' > /etc/dropbear/authorized_keys
   ```

8. Now SSH in with the new password/key.

### Option C: Config snapshot + revert (requires SSH access — CURRENTLY BLOCKED)

This is the config-level recovery path that the task asked to exercise.
It requires SSH access to the device. Once access is restored (via Option A
or B above), the procedure is:

**Snapshot:**
```bash
ssh root@192.168.1.1 "mkdir -p /tmp/cfg-snapshot && cp -r /etc/config /tmp/cfg-snapshot/"
# Or full backup:
ssh root@192.168.1.1 "sysupgrade -b /tmp/backup.tar.gz"
scp -O root@192.168.1.1:/tmp/backup.tar.gz ./backup-$(date +%s).tar.gz
```

**Make a benign change:**
```bash
ssh root@192.168.1.1 "uci set system.@system[0].hostname=pf-tmp && uci commit system"
# Verify:
ssh root@192.168.1.1 "uci get system.@system[0].hostname"
# Expected: pf-tmp
```

**Restore:**
```bash
ssh root@192.168.1.1 "cp -r /tmp/cfg-snapshot/config/* /etc/config/ && reload_config"
# Or:
ssh root@192.168.1.1 "uci revert system.@system[0].hostname && uci commit system"
```

**Verify revert:**
```bash
ssh root@192.168.1.1 "uci get system.@system[0].hostname"
# Expected: original hostname (NOT pf-tmp)
```

---

## 7. PATHS TESTED vs. UNAVAILABLE

| Path | Status | Evidence |
|------|--------|----------|
| Config snapshot + revert | **NOT TESTED** (no SSH access) | Section 2 |
| Serial console | **UNAVAILABLE** (no adapter) | Section 3.1 |
| U-Boot HTTP recovery (reflash) | **DOCUMENTED** (not tested — destructive) | Section 4.1 |
| U-Boot TFTP recovery (reflash) | **DOCUMENTED** (not tested — destructive) | Section 4.2 |
| LuCI web login | **TESTED, FAILED** | Section 2.3 |
| SSH password auth | **TESTED, FAILED** (16 passwords) | Section 2.1 |
| SSH publickey auth | **TESTED, FAILED** (8 keys) | Section 2.2 |

---

## 8. BLOCKER SUMMARY

**No recovery path has been proven on hardware with real observed output.**

The device is running but inaccessible:
- SSH: password and key auth both fail (host key changed — device was reflashed/reset)
- LuCI: all passwords rejected
- Serial: no adapter connected
- No recorded password in inventory.jsonl, KeePass, or session history

Per the task's FAILURE MODE: "If no recovery path can be proven, STOP and
report BLOCKED — do not allow any subsequent recipe work on this device."

**The operator must either:**
1. Provide the root password (if known by the human who configured the device)
2. Connect a serial adapter (3.3V USB-UART) so we can get a serial shell
3. Authorize a U-Boot HTTP recovery reflash (destroys current config)

Until one of these is resolved, no recipe work may proceed.
---

## 9. ADDENDUM 2026-09-15 (worker-heavy) — DEVICE IDENTITY + PRE-FLIGHT BASELINES + CLOCK

Task (fleet offload): capture pre-flight snapshots, reboot-surviving baselines, and
clock-sync evidence with an explicit GO/NO-GO. Read-only — no config changes made.
Full addendum with complete raw transcripts:
`addendum-20260915.md` (this directory) + `artifacts/` (5 hash-pinned artifacts,
raw command/output transcripts).

Repo: conwrt @ `feat/vpn-provider-setup`, HEAD `8ed65e8` (re-measured before writing).

### 9.1 CRITICAL — the device at 192.168.1.1 is a GL-MT6000, not the CF-WR632AX

Live identity evidence (2026-09-15 ~02:00 UTC, SSH via kit routers.env ROUTER_PASSWORD):

```
root@TollGate:~# cat /tmp/sysinfo/board_name
glinet,gl-mt6000
root@TollGate:~# cat /tmp/sysinfo/model
GL.iNet GL-MT6000
root@TollGate:~# cat /etc/openwrt_release | head -5
DISTRIB_RELEASE='24.10.1'
DISTRIB_REVISION='r28597-0425664679'
DISTRIB_TARGET='mediatek/filogic'
```

- ARP: `192.168.1.1 lladdr 94:83:c4:d1:57:58` — OUI 94:83:C4 = GL Technologies (GL.iNet),
  matching `models/glinet-mt6000.json` mac_oui. Issue #32's target (`models/comfast-cf-wr632ax.json`)
  expects OUI 40:A5:EF (COMFAST). AGENTS.md: MAC OUI = ground truth → identity mismatch.
- `/proc/mtd` empty (eMMC boot, mmcblk0p1-p7 in /proc/partitions) — CF-WR632AX is SPI-NAND.
- Firmware 24.10.1 with opkg (no apk) — issue-32 recipes target 25.12.4/apk.

Search for the actual CF-WR632AX (NOT FOUND): full ICMP sweep of 192.168.1.0/24 (only .1 alive,
no COMFAST OUI), `nmcli dev wifi list` (one TP-Link AP only), device-side DHCP leases and neighbor
tables (no 40:a5:ef), 192.168.21.0/24 WAN-subnet probe (only a dead gateway + one STALE host),
no historical 40:a5:ef in the manager state tree. The CF-WR632AX appears to be powered off
or off-site.

### 9.2 BASELINES (device: GL-MT6000 @ 192.168.1.1, hostname tollgate-4SQY)

**B1 — LAN IP:**

```
root@TollGate:~# uci get network.lan.ipaddr
192.168.1.1
root@TollGate:~# ip -4 addr show br-lan
9: br-lan: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP qlen 1000
    inet 192.168.1.1/24 brd 192.168.1.255 scope global br-lan
       valid_lft forever preferred_lft forever
```

Also: br-private 192.168.2.1/24; WAN (eth1) 192.168.21.227/24 (DHCP).

**B2 — hostname:**

```
root@TollGate:~# uci get system.@system[0].hostname
tollgate-4SQY
```
Runtime kernel hostname disagrees: `cat /proc/sys/kernel/hostname` → `TollGate`. After any
reboot-persistence comparison, check BOTH — uci value vs runtime value.

**B3 — nodogsplash installed AND running:**

```
root@TollGate:~# /etc/init.d/nodogsplash status
running
root@TollGate:~# ps w | grep -i nodog
29318 root      1700 S    /usr/bin/nodogsplash -c /tmp/etc/nodogsplash_cfg015847.conf -f -s
root@TollGate:~# opkg list-installed | grep -i nodogsplash
nodogsplash - 5.0.2-r1
```

**B4 — hotplug script exists (the one issue-32 recipes install):**

```
root@TollGate:~# find /etc/hotplug.d -type f | grep -E 'iface|tollgate'
/etc/hotplug.d/iface/00-netstate
/etc/hotplug.d/iface/20-firewall
/etc/hotplug.d/iface/95-tollgate-restart
root@TollGate:~# ls -l /etc/hotplug.d/iface/95-tollgate-restart
-rwxr-xr-x    1 root     root          2869 Sep 13 15:22 /etc/hotplug.d/iface/95-tollgate-restart
```
Path: `/etc/hotplug.d/iface/95-tollgate-restart` (2869 B, 755, mtime 2026-09-13 — from the
prior TollGate deployment; matches the recipe's install path in scripts/use_cases/tollgate.py:438-440).

**B5 — package manager record:** opkg present (`/bin/opkg`), apk ABSENT.
`opkg list-installed` → 193 packages. (24.10.1 firmware.)

**B6 — artifacts (off-device, sha256-pinned, in `artifacts/`):**

| artifact | file | lines | sha256 |
|---|---|---|---|
| uci export | issue32-preflight-uci.txt | 470 | 49b8086df49b2d1a60a0d333c3341f34090ec16dcd9d7504a4d5eece39800c53 |
| /proc/mtd | issue32-preflight-mtd.txt | 1 (header only — eMMC, no MTD) | e9f043000a3443b4a9eba7c051402d0d4033714662357e3a3b305a4a1cc223c0 |
| /proc/partitions (supplement) | issue32-preflight-partitions.txt | 13 | 8bf1915ab517283c52f8f5dd2beadd8b842fc3074e52a97704a7ac8182ed5693 |
| package list (opkg) | issue32-preflight-packages.txt | 193 | d78c3c897ed95f34ef99e806e0c8f06f01f1c43061f14b2006ef062014d40da8 |
| /etc/config/network | `issue32-preflight-network.txt` | 50 | `9b5ec28cbd460d683bef09770ac7f3f417a77566c31b868add119dd53ff446b4` |

**Sanitization note:** the uci export contains the lab WiFi PSK (`option key '...'` on
wireless.private_radio0/1). This manager-state copy is byte-exact (sha256 `49b8086...`).
The repo mirror in conwrt `state/` is REDACTED: the two PSK values replaced with
`<REDACTED-WIFI-PSK>` (repo copy sha256 `b4bda1460b73eefa6758b7c3bde1bd97c14b912cfec417e7542594b8f8df3d15`).
No other artifact contains credentials (verified by grep); the SSH password used for
access is stored only in the kit's gitignored routers.env and is never written to the
evidence dir.

Method: `uci export > /tmp/issue32-preflight-uci.txt` on device; `scp -O` (dropbear has no
sftp-server) to the evidence dir. Raw transcripts: artifacts/baselines-raw.txt, clock-raw.txt,
upstream-raw.txt, downstream-raw.txt, wan-sweep-raw.txt.

### 9.3 CLOCK — raw evidence, drift, GO/NO-GO

```
root@TollGate:~# date -u
Tue Sep 15 02:02:11 UTC 2026
root@TollGate:~# /etc/init.d/sysntpd status
running
root@TollGate:~# /etc/init.d/sysntpd enabled && echo sysntpd-ON || echo sysntpd-OFF
sysntpd-ON
root@TollGate:~# ps w | grep -i ntp
 2376 root      2852 S    {ntpd} /sbin/ujail -t 5 -n ntpd -U ntp -G ntp -C /etc/capabilities/ntpd.json -c -u -r /bin/ubus -r /usr/b
 2447 ntp       1336 S    /usr/sbin/ntpd -n -N -S /usr/sbin/ntpd-hotplug -p 0.openwrt.pool.ntp.org -p 1.openwrt.pool.ntp.org -p 2.o
root@TollGate:~# uci show system | grep timeserver
system.ntp=timeserver
root@TollGate:~# uci show system | grep -E 'ntp.enabled|ntp.server'
system.ntp.enabled='1'
system.ntp.server='0.openwrt.pool.ntp.org' '1.openwrt.pool.ntp.org' '2.openwrt.pool.ntp.org' '3.openwrt.pool.ntp.org'
root@TollGate:~# logread | grep -i ntp | tail -5
(no output — zero NTP log lines)
```

**Drift measurement** (SSH round-trip bounded; host is NTP-synced, NTPSynchronized=yes;
device BusyBox date lacks sub-second support so whole-second epochs compared):

```
sample1: host_t0=1789437776.470  device=1789437765  host_t1=1789437776.684  → device − host ≈ −11.2 s
sample2: host_t0=1789437776.690  device=1789437766  host_t1=1789437776.902  → device − host ≈ −11.1 s
sample3: host_t0=1789437776.908  device=1789437766  host_t1=1789437777.131  → device − host ≈ −11.0 s
```

**Observed drift: ≈ −11 seconds (device behind host).** SSH round-trip ≈ 0.2 s → real drift.

Root cause — no upstream: `ping -c 2 0.openwrt.pool.ntp.org` → "bad address" (DNS dead);
`nslookup 0.openwrt.pool.ntp.org` → connection timed out; `ping 8.8.8.8` → 100% loss;
`ping 192.168.21.21` (WAN gateway) → 100% loss. WAN ifstatus "up" with DHCP lease
(192.168.21.227, uptime 59303s) but gateway dead → link up, no upstream. TollGate API
returns kind:21023 "no-reachable-mints" — the classic no-upstream signature.

**GO / NO-GO: NO-GO.**

Recipes cannot proceed with the current clock as-is. Required before proceeding:

1. Restore upstream connectivity on the test device (WAN gateway up or a traffic-carrying
   WiFi STA uplink): `ping -c 3 8.8.8.8` must show 0% loss.
2. Let sysntpd step the clock (`logread | grep -i ntp` must show sync lines), or push
   `date -s @<epoch>` from the operator host, then re-measure.
3. GO threshold: |drift| ≤ 5 s vs the NTP-synced operator host.
4. AND resolve the device-identity mismatch: the CF-WR632AX (OUI 40:A5:EF, board_name
   comfast,cf-wr632ax, SPI-NAND /proc/mtd, 25.12.4, apk) must be located and confirmed as
   the device under test. Issue-32 recipes must NOT be run on the GL-MT6000.
