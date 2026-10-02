# tollgate LAN-move ipv4 provenance — notes

Scope and source of truth: `docs/wizard-bundle.json` (READ-ONLY) in
`/home/c03rad0r/repos/conwrt`, branch `feat/vpn-provider-setup`, HEAD
`698b9b1aa029aaa36bc5a3d600bb2730796ad6dc`; `docs/wizard-bundle.json` sha256
`6fe93f952fe68a53facd7d0a3561865377ccdd15beb3801cb4432b23a507277e`. Every claim below was
re-derived first-hand by reading the JSON and the generator sources it names; the secondary lead
`state/conwrt-issue32-evidence/tollgate-lan-move.md` was NOT used as evidence.

Primary target: the **tollgate** flow's LAN-move step for the issue-32 device
`comfast-cf-wr632ax`, OpenWrt version `25.12.4`.

---

## (a) Entry-point locator

**The value that actually enters the emitted command block:**

> derived ipv4 enters at `docs/wizard-bundle.json:358` via JSON key path
> `rendered["comfast-cf-wr632ax"]["tollgate"]["25.12.4"].shell` (shell-string line 65), from the
> generator's `lan_gateway` (`scripts/flows/render.py:131`) — **not** from
> `derive_device_secret.py` output bound to any variable.

- **JSON key path:** `rendered["comfast-cf-wr632ax"]["tollgate"]["25.12.4"].shell` — physical JSON
  line **358** (the single line that carries the whole escaped `shell` string for this recipe; the
  sibling `.markdown` transport is line 359).
- Inside the unescaped shell string the address is written at **shell-string line 65**:
  `uci set network.lan.ipaddr='192.168.1.1'`. The whole LAN-move block is shell lines **62–69**.
- **Binding / substitution site (generation time):** `scripts/flows/render.py:137` —
  `UciSet(config="network", section="lan", values={"ipaddr": gw, "netmask": "255.255.255.0"}),`
  where `gw` is bound at `scripts/flows/render.py:131` — `gw = target.get("lan_gateway", "")`.
- Where `gw` is derived: `scripts/profile/target.py:117` —
  `lan_gateway = str(net.network_address + 1)`, from `scripts/profile/target.py:112` —
  `lan_subnet = model.get("lan_subnet", "")`, sourced from `models/comfast-cf-wr632ax.json:3` —
  `"lan_subnet": "192.168.1.0/24"`, exposed as `"lan_gateway": lan_gateway,` at
  `scripts/profile/target.py:130`.

**derive_device_secret.py: NO binding exists at this HEAD.**

- `scripts/derive_device_secret.py` does not exist at HEAD:
  `git ls-files | grep -i derive_device_secret` → empty;
  `git cat-file -e HEAD:scripts/derive_device_secret.py` → rc=128;
  `find . -name 'derive_device_secret*'` → empty.
- The string `derive_device_secret` occurs **0** times in `docs/wizard-bundle.json`.
- Therefore the task's expected locator form *"… from derive_device_secret.py output bound to
  `<var>`"* has **no referent at HEAD**: no variable in the emitted block is bound to that script's
  output, and the script is not even present.
- Cross-revision completeness (NOT this HEAD): the script exists on branches `pr-55`,
  `cf-wr632ax-recipe-v2`, `upstream/master` and at commit `17a7786` (same blob). There its output
  path is **stdout**: `--json` prints `json.dumps(derive_all(...))`, whose `ipv4` field is set at
  `pr-55:scripts/derive_device_secret.py:126` (`"ipv4": derive_ipv4(pub_x_hex),`) by `derive_ipv4`
  at `pr-55:scripts/derive_device_secret.py:93-95` (CGNAT `100.64.0.0/10`,
  `f"100.{64 + h[0] % 64}.{h[1]}.1"`). The variable name as referenced by the lead file is the dict
  key / helper name `ipv4` / `derive_ipv4`; the script writes no file.

---

## (b) Verdict

**Verdict: the LAN-move block uses a hardcoded literal ipv4 (the generate-time-rendered per-model
address `192.168.1.1`) and does NOT consume the derived value — nothing in the block is
`derive_device_secret.py` output or a variable bound to it.**

One plain sentence: the tollgate LAN-move block emits the per-model literal
`uci set network.lan.ipaddr='192.168.1.1'` (baked into the bundle at generate time from
`models/comfast-cf-wr632ax.json:3`), not a per-device value derived from `derive_device_secret.py`.

---

## (c) Supporting evidence

### c1. Emitted command text (verbatim, unescaped) — JSON line 358, shell lines 62–69

```sh
# --- Move the LAN off 192.168.1.1 ---
ssh root@$IP sh <<'CONWRT_EOF'
# move LAN off 192.168.1.1 → 192.168.1.1 (192.168.1.0/24)
uci set network.lan.ipaddr='192.168.1.1'
uci set network.lan.netmask='255.255.255.0'
uci commit network
(/etc/init.d/network restart &) ; echo 'LAN moving to 192.168.1.1 — reconnect on that subnet'
CONWRT_EOF
```

The address appears **three** times inside this block (banner, comment, `uci set`, `echo`) — always
the same literal `192.168.1.1`. The only parameterized value in the block is the SSH target `$IP`
(bound at the top of the script: `IP=${IP:-192.168.1.1}`); the LAN address itself is a literal string.

### c2. Substitution / binding site (generate-time), verbatim

`scripts/flows/render.py:130-140` (step kind `set_lan_ip`, dispatched at `:158-159`):

```python
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
```

`scripts/profile/target.py:112-119` and `:129-130` (the derivation of `lan_gateway`):

```python
    lan_subnet = model.get("lan_subnet", "")
    lan_gateway = ""
    if lan_subnet:
        try:
            net = ipaddress.ip_network(lan_subnet, strict=False)
            lan_gateway = str(net.network_address + 1)
        except ValueError:
            lan_gateway = ""

        "lan_subnet": lan_subnet,
        "lan_gateway": lan_gateway,
```

`models/comfast-cf-wr632ax.json:3`:

```json
  "lan_subnet": "192.168.1.0/24",
```

Step definition `scripts/flows/_gateway.py:66-71` (`kind="set_lan_ip"` at `:68`), appended to *both*
the tollgate and net4sats flows. Emitted into the artifact by `scripts/generate_site.py:113`
(`out.write_text(json.dumps(bundle, indent=2))`).

So `192.168.1.0/24` → network address + 1 = `192.168.1.1` → `gw` → `ipaddr=gw` → the literal in the
bundle. It is a **generated** literal (not hand-written), but it is a literal in the emitted command
and it is **not** the `derive_device_secret.py`-derived per-device value.

### c3. No placeholder is reachable at HEAD

- `grep -c '{{lan_ip}}' docs/wizard-bundle.json` → **0**.
- The only `{{...}}` tokens anywhere in the bundle are
  `{{hostname}}`, `{{root_password}}`, `{{upstream_band}}`, `{{upstream_key}}`, `{{upstream_ssid}}`
  (none IP-related).
- `lan_ip` occurs **0** times in the bundle; `lan_gateway` occurs **0** times (the value is already
  rendered).
- `uci get` / `uci show` / `ip addr` / `ubus call` each occur **0** times bundle-wide → the recipe
  performs **no read-back**; `uci commit network` is unconditional.

### c4. Cross-model check (proves the value is per-model, and that comfast's is the no-op)

Every one of the 22 models' `rendered[<model>]["tollgate"]["25.12.4"].shell` writes an `ipaddr`
literal; comfast-cf-wr632ax is the **only** one that writes `192.168.1.1` (its own
`lan_subnet` == the OpenWrt default), so its "Move the LAN off 192.168.1.1" step is a no-op. The
other 21 each write a distinct `lan_subnet`+1 address:

```
asus-lyra-map-ac2200      10.231.9.1      glinet-mt3000          10.230.236.1
comfast-cf-wr632ax        192.168.1.1     glinet-mt6000          10.230.237.1
dlink-covr-x1860-a1       10.89.4.1       linksys-mx4200-v1      10.36.125.1
extreme-networks-ws-ap3915i 10.47.217.1   linksys-whw03-v1       10.12.100.1
glinet-gl-ar150           10.135.117.1    linksys-whw03-v2       10.61.168.1
glinet-gl-ar300m-lite     10.193.202.1    ubnt-edgerouter-6p     10.141.185.1
glinet-gl-ar300m-nand     10.64.224.1     ubnt-edgerouter-x      10.78.162.1
glinet-gl-ar300m-nor      10.107.186.1    zyxel-ex5700-telenor   10.13.237.1
zyxel-gs1900-24e          10.44.172.1     zyxel-gs1900-8hp-a1    10.172.177.1
zyxel-gs1900-8hp-b1       10.47.149.1     zyxel-gs1920-24        10.213.244.1
zyxel-nr7101              10.63.178.1     zyxel-wx5600-t0        10.220.129.1
```

### c5. Reproduce (read-only)

```bash
cd /home/c03rad0r/repos/conwrt
sha256sum docs/wizard-bundle.json                       # 6fe93f95…277e
python3 - <<'PY'
import json,re
b=json.load(open("docs/wizard-bundle.json"))
sh=b["rendered"]["comfast-cf-wr632ax"]["tollgate"]["25.12.4"]["shell"]
L=sh.split("\n"); s=next(i for i,l in enumerate(L) if l.startswith("# --- Move the LAN off"))
e=next(i for i,l in enumerate(L) if i>s and l.strip()=="CONWRT_EOF")
print("\n".join(L[s:e+1]))
print("ipaddr line:", s+4, "|", re.search(r"uci set network\.lan\.ipaddr='([^']*)'", sh).group(1))
PY
grep -c '{{lan_ip}}' docs/wizard-bundle.json              # 0
grep -n 'tollgate on comfast-cf-wr632ax' docs/wizard-bundle.json   # physical line 358
```

---

## (d) Hardcoded literal / unresolved placeholder, and the fallback branch

### d1. Hardcoded literal — FOUND (this is what ships)

- **Locator:** `docs/wizard-bundle.json:358` via JSON key path
  `rendered["comfast-cf-wr632ax"]["tollgate"]["25.12.4"].shell`, shell-string line 65.
- **Text:** `uci set network.lan.ipaddr='192.168.1.1'`
- **Provenance:** generator-bound, generate-time (`scripts/flows/render.py:131/137` ←
  `scripts/profile/target.py:117` ← `models/comfast-cf-wr632ax.json:3`); a literal in the emitted
  artifact, with no runtime binding and no runtime substitution.

### d2. Unresolved placeholder — NOT reachable at HEAD (0 occurrences)

There is no `{{lan_ip}}`-style placeholder in this HEAD's bundle. The placeholder form exists only on
**other revisions** (reported here for contrast, quoted as a FINDING — it is not in this branch's
artifact):

- `pr-55` (`ec5c60d9…`) / `17a7786` / `upstream/master`, key path
  `rendered["comfast-cf-wr632ax"]["tollgate"]["25.12.4"].shell`, physical line **372** on `pr-55`
  (`{{lan_ip}}` count on `pr-55` = 4; on `upstream/master` = 184):

  ```sh
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

  There the placeholder is bound to the `lan_ip` flow param (`pr-55:scripts/flows/_gateway.py:36`),
  whose description directs the operator to `derive_device_secret.py`'s `ipv4` field
  (`pr-55:scripts/flows/_gateway.py:41`), and consumed at `pr-55:scripts/flows/render.py:205`
  (`lan_ip = str(params.get("lan_ip") or "").strip()`); the placeholder branch is
  `pr-55:scripts/flows/render.py:166` (`if "{{" in lan_ip:`). That branch's guard refuses to run if
  the value is still a brace token, so it is *guarded*, not silently emitted. **None of this exists
  at this HEAD**; on this branch the wizard-bundle renderer (`_set_lan_ip_ops`, `render.py:130-140`)
  has no placeholder code path at all.

### d3. Fallback / error branch — present, but emits no address at all

Success path (`gw` non-empty): emits the literal `uci set network.lan.ipaddr='<gw>'` shown in (c1).

Fallback path (`gw` empty — model has no `lan_subnet`, or an unparseable one so
`scripts/profile/target.py:118-119` sets `lan_gateway = ""`):

- `scripts/flows/render.py:133-134`:
  ```python
    if not gw:
        return [Comment("skip LAN move — model has no lan_subnet defined")]
  ```
- Behaviour: the block emits **only a comment** — no `uci set network.lan.ipaddr` line, no literal
  IPv4, and no placeholder. Nothing is substituted and nothing is verified.
- Reachability: **not reached in the shipped bundle.** `grep -c 'skip LAN move' docs/wizard-bundle.json`
  → 0; every one of the 22 models has a `lan_subnet` (`models/*.json`) and all 22 tollgate recipes
  emit an `ipaddr` literal (c4).
- **Flag (defect, silent-mode):** when reachable, the fallback *silently omits* the LAN move — the
  step renders as a bare comment, the script still exits 0, and the "Move the LAN off 192.168.1.1"
  safety step does not happen. With no read-back (`uci get` = 0 bundle-wide), nothing detects either
  this or the comfast no-op.
- **Flag (defect, hardcoded netmask):** the netmask is a constant `'255.255.255.0'`
  (`render.py:137`) regardless of the model's `lan_subnet` prefix. Correct for the current all-`/24`
  models, but a model whose `lan_subnet` is not `/24` would get a mismatched netmask written
  alongside its derived gateway.

---

## Read-only attestation (git status)

`docs/wizard-bundle.json` was never opened for write: its sha256 is
`6fe93f952fe68a53facd7d0a3561865377ccdd15beb3801cb4432b23a507277e` before and after, and
`git status --porcelain -- docs/wizard-bundle.json` is empty.
`state/conwrt-issue32-evidence/checklist.md` was not created or touched (it does not exist in the
tree). `state/conwrt-issue32-evidence/drafts/tollgate-subsection.md` was not written by this task.
The only file this task created is
`state/conwrt-issue32-evidence/drafts/tollgate-provenance-notes.md`.
