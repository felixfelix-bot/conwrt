# PR #55 — PIA / OpenVPN environment-variable secret audit

**Audit target:** `Amperstrand/conwrt` PR #55, head `ec5c60d9` ("feat(vpn): PIA OpenVPN use case + VPN setup library proposal")
**Merge base:** `8bbce153945af22f1988309c72e3435e475c7b7f` (diff = 143 files, 12,210 insertions)
**Audited surfaces:** every `openvpn` invocation and shell-out in the PIA module and the PR diff —
`scripts/use_cases/openvpn_pia.py` (511 lines, new), `ansible/playbooks/pia-openvpn.yml`,
`ansible/roles/pia_openvpn/**` (tasks, templates, handlers, 5 on-device scripts),
`conwrt-flash.sh`, `config.example.toml`, `scripts/profile/{ops,apply,target}.py`,
`scripts/flows/{render,net4sats,_gateway}.py`, `scripts/use_cases/{cashu_vpn_client,mptcp_bonding,pbr}.py`,
`scripts/derive_device_secret.py`, and the PR's docs.
**Method:** `git grep` over the pr-55 tree and over the diff's added *and* removed lines for
`export`/`env`/`os.environ`/`getenv`/`env=`/`environment:`/`OPENVPN_*`/`PIA_*`/`docker run -e`;
line-by-line reading of every shell-out; plus a live canary experiment against the installed
Ansible + SSH stack to measure what is actually readable in `/proc/<pid>/{cmdline,environ}`
(evidence in the appendix). No claim below is made without a file + line citation or captured output.

---

## Verdict

| # | Finding | Severity | Category |
|---|---------|----------|----------|
| F-1 | Ansible role interpolates `pia_password` into an `ansible.builtin.raw` heredoc → plaintext in controller-side `ssh` argv **and** remote shell argv | **medium** | argv (not env) |
| F-2 | Documented `ansible-playbook … -e pia_username=p1234567` puts a credential identifier in the controller's argv/shell history | **low** | argv (not env) |
| F-3 | ubus transport *would* ship the credential heredoc as an `exec` RPC parameter over plaintext HTTP — currently unreachable (`skip_fallback=True` default) | **low** (conditional) | transport |
| F-4 | Credentials file lives at `/etc/openvpn/pia-auth.txt` (persistent overlay), not `/run/...` (tmpfs) | **informational** | design tradeoff, not a defect |

**Environment-variable sub-category: NO ISSUE FOUND.** See the explicit statement in
"Sub-category assessments" below — no secret is passed through `OPENVPN_USER`, `OPENVPN_PASS`,
any custom `PIA_*` variable, an `env` prefix, an `export`, `subprocess.run(..., env=…)`,
`os.exec*`, `docker run -e`, or a Compose `environment:` key, anywhere in the PR diff or the
PIA module.

---

## Inventory — every `openvpn` invocation / shell-out in scope

Credentials handling (the only place a PIA secret is consumed):

| Site | Line ref | Mechanism |
|------|----------|-----------|
| `scripts/use_cases/openvpn_pia.py` | `69` | `AUTH_FILE = "/etc/openvpn/pia-auth.txt"` |
| `scripts/use_cases/openvpn_pia.py` | `331` | `WriteFile(path=AUTH_FILE, content=f"{r['username']}\n{r['password']}\n", mode="600")` |
| `scripts/use_cases/openvpn_pia.py` | `287`, `289` | profile lines `auth-nocache` + `auth-user-pass /etc/openvpn/pia-auth.txt` |
| `ansible/roles/pia_openvpn/tasks/main.yml` | `27–33` | `raw` heredoc → `cat > /etc/openvpn/pia-auth.txt`, `chmod 600`, `no_log: true` |
| `ansible/roles/pia_openvpn/templates/pia-auth.txt.j2` | `1–2` | `{{ pia_username }}` / `{{ pia_password }}` |
| `ansible/roles/pia_openvpn/templates/pia.ovpn.j2` | `20`, `22` | `auth-nocache`, `auth-user-pass /etc/openvpn/pia-auth.txt` |

`openvpn` process/service references (all UCI/service based — no CLI `openvpn … --config` invocation
anywhere in the PR, so no argv-borne credentials at the daemon level):

`openvpn_pia.py:341–349` (UCI instance), `:458` (`ServiceAction openvpn restart`),
`openvpn_pia.py:85` / role `files/pia-health:10` (`pgrep -f '/usr/sbin/openvpn'`),
`openvpn_pia.py:142,155` and role `files/pia-enforce` (`uci commit openvpn`),
`openvpn_pia.py:236` and role `files/pia-watchdog:87` (`/etc/init.d/openvpn restart`),
role `handlers/main.yml:17–18`, `openvpn.pia.status` read by `files/pia-status:18`.
None of these read or forward credentials.

---

## Related audits (same PR head, complementary vectors)

* `state/pr55-pia-logging-audit/audit-findings.md` (commit 421a2be) — logging/stdout leakage, incl.
  the HIGH dry-run plaintext on the conwrt `configure --dry-run` path. Orthogonal to this audit:
  that report does not flag the environment variable sub-category, and its finding is stdout-based.

---

## Findings

### F-1 — `pia_password` is interpolated into a `raw` command string (argv exposure on both ends)

**Severity:** medium
**File:** `ansible/roles/pia_openvpn/tasks/main.yml:27–33` (PR-added), `ansible/roles/pia_openvpn/templates/pia-auth.txt.j2:1–2`

```yaml
- name: Write PIA credentials file
  ansible.builtin.raw: |
    cat > /etc/openvpn/pia-auth.txt <<'OPENWRT_EOF'
    {{ lookup('template', 'pia-auth.txt.j2') }}
    OPENWRT_EOF
    chmod 600 /etc/openvpn/pia-auth.txt
  no_log: true
```

**Why unsafe:** `ansible.builtin.raw` hands the fully-interpolated command text to the connection
plugin as one opaque string; the SSH connection plugin appends that string as an **argv element of
the local `ssh` process** (`/opt/miniconda/lib/python3.13/site-packages/ansible/plugins/connection/ssh.py`,
`exec_command`: `args = (self.host, cmd)` then `b_command += [to_bytes(a) for a in other_args]`).
The remote side then runs it as `$SHELL -c '<command>'`. Measured live (appendix, runs 2 and 4):
the plaintext secret was present in the controller `ssh` argv (`pid 2275326`) *and* in the remote
`bash -c …` argv (`pid 2275435`). `no_log: true` suppresses Ansible's *logging* of the task but
does nothing about argv. On the audited host `/proc/<pid>/cmdline` was readable for foreign-UID
processes while `/proc/<pid>/environ` was `Permission denied` — i.e. argv is the *weaker* channel.
The role's own README (`ansible/roles/pia_openvpn/README.md:17–20`) documents this streaming design
as an intentional dropbear/no-SFTP workaround, but does not note the argv consequence.

**Fix:** never let the secret into a `raw` command string. Keep the credential off argv on both
ends by streaming it over stdin, the way the Python path already does:

```yaml
- name: Stage credentials on the controller (mode 0600, no_log)
  ansible.builtin.copy:
    content: "{{ pia_username }}\n{{ pia_password }}\n"
    dest: "{{ ansible_ssh_common_args_local }}/pia-auth.txt"   # controller tmpfile, 0600
    mode: "0600"
  delegate_to: localhost
  no_log: true

- name: Upload credentials via scp (dropbear-safe -O; contents never in argv)
  ansible.builtin.command:
    argv: ["scp", "-O", "-i", "{{ pia_key }}", "/tmp/pia-auth.txt",
           "root@{{ inventory_hostname }}:/etc/openvpn/pia-auth.txt"]
  delegate_to: localhost
  no_log: true
```

Alternatively delete the credential task from the role entirely and defer that single step to the
conwrt path (`openvpn-pia` preset → `scripts/profile/apply.py` `_run_step_script`, which routes
heredoc scripts over SSH **stdin**: `ssh_cmd(ip, "sh -s")` + `input=payload`, `apply.py:115–117`).

---

### F-2 — Documented `-e pia_username=p1234567` exposes the account identifier in controller argv/history

**Severity:** low
**Files:** `ansible/README.md:27–28`, `ansible/roles/pia_openvpn/README.md:51–52`

```bash
ansible-playbook -i inventory.ini ansible/playbooks/pia-openvpn.yml \
  -e pia_username=p1234567 -e @vault.yml
```

**Why unsafe:** `-e KEY=VALUE` (Ansible *extra vars*) is passed through the `ansible-playbook`
command line, so the value lands in `/proc/<pid>/cmdline` and the operator's shell history. This is
**not** an environment-variable mechanism — extra vars are never exported into the target's
environment (confirmed: the live experiment showed task-var values in argv with zero `environ` hits).
The example is also correct in the important respect: only the *username* (p-number) is on the CLI —
`pia_password` stays in `@vault.yml`.

**Fix:** the password handling is already right. For parity, take the username from the vault as
well (`-e @vault.yml` only), or set `pia_username` in `group_vars`/`host_vars` instead of on the
command line. No code change required; docs-only hardening.

---

### F-3 — ubus transport would move the credential heredoc into a plaintext-HTTP RPC parameter

**Severity:** low (conditional — not reachable with current defaults)
**Files:** `scripts/profile/ops.py:331–336` (PR-added), `scripts/profile/apply.py:444,465,495–499` (PR-added)

```python
elif isinstance(op, WriteFile):
    calls.append(RpcCall(
        object_name="exec",
        method="command",
        params={"command": render_writefile(op), "fallback": True},
    ))
```

**Why unsafe *if* enabled:** `render_writefile` emits the credential heredoc, and the ubus renderer
attaches it as the `command` parameter of an `exec` RPC. With `skip_fallback=False` that payload is
sent to the router's ubus-over-HTTP endpoint (plain HTTP on stock uhttpd) and re-enters argv when
rpcd executes it. The credential would cross the LAN in cleartext. **Current default is safe:**
`apply_ubus(..., skip_fallback: bool = True)` (`apply.py:444`) filters every `fallback=True` call,
logging `"… shell command(s) skipped"` (`apply.py:495–499`), so the PIA auth-file write is skipped
over ubus today.

**Fix:** make the guard explicit rather than incidental — when `skip_fallback=False`, refuse (or
hard-warn) if any step contains a `WriteFile` whose path matches a credential/secret sink, e.g.
`/etc/openvpn/*auth*`, `/etc/config/pia`; and require uhttpd TLS before enabling the exec fallback.
Suggested assertion in `apply_ubus` before the call loop:

```python
if not skip_fallback and any(
    isinstance(op, WriteFile) and "auth" in op.path for step in plan.steps for op in (step.ops or [])
):
    raise ValueError("refusing to send credential WriteFile over plaintext ubus exec fallback")
```

---

### F-4 — informational: credentials persist in the overlay rather than tmpfs

**Severity:** informational (not a defect)
**Files:** `scripts/use_cases/openvpn_pia.py:69`, `ansible/roles/pia_openvpn/tasks/main.yml:29`

A common hardening pattern is `--auth-user-pass /run/pia/auth.txt` with `/run` on tmpfs so the
secret never survives a reboot. Here the file is `/etc/openvpn/pia-auth.txt` at mode 0600
(and `/etc/openvpn/pia.ovpn` likewise). That is the correct choice for this design: the watchdog
(`openvpn_pia.py:236`, role `files/pia-watchdog:87`) restarts OpenVPN unattended after reboots and
endpoint rotation, which requires the credential to survive a power cycle; `auth-nocache` is already
set (`openvpn_pia.py:287`, `pia.ovpn.j2:20`) so nothing lingers in the daemon's memory. On a UBIFS
overlay device, recall that `uci commit`/file writes are permanent — documented in
`docs/vpn-setup-library.md` — so removal requires an explicit cleanup, and the role should keep the
`/root/vpnbak` rollback it advertises (`ansible/roles/pia_openvpn/README.md:63–65`).

---

## Sub-category assessments

### 1. Secret passed via environment variables — **NO ISSUE FOUND**

Every requested pattern was searched for across the PR diff (added *and* removed lines) and the
full pr-55 tree:

| Pattern | Result |
|---------|--------|
| `OPENVPN_USER`, `OPENVPN_PASS`, `OPENVPN_*_PASS` | 0 occurrences anywhere in the PR |
| Custom `PIA_*` env vars (`PIA_USER`, `PIA_PASS`, …) | 0 occurrences; `PIA_*` appears only as shell script *names*/constants, not env vars |
| `export <SECRET>` / `export` of any variable | 0 added lines contain `export` |
| `env` prefix on a command (`env VAR=… cmd`) | 0 occurrences |
| `os.environ` / `getenv` in added lines | 1 hit only: `tests/integration/conftest.py` — `ev = os.environ.get("CONWRT_EVIDENCE_DIR")` (a **directory path** for VM evidence capture, set by `scripts/local-tests.sh`; not a secret) |
| `subprocess.run(..., env=…)` in added lines | 0 hits |
| `os.execve` / `execve` | 0 hits |
| `docker run -e` | 0 hits; the only docker lines in the diff are prose `docker compose build` / `up -d` (`docs/europa-vpn-deployment.md`) |
| Compose `environment:` key | 0 hits |

The credential path is file-based end to end: operator `config.toml` → `WriteFile(mode="600")`
→ `auth-user-pass <file>` + `auth-nocache`. OpenVPN itself has no environment-variable credential
input; nothing in this PR invents one or wraps the daemon in a shell that exports one.

### 2. `/proc/<pid>/environ` readability — no secret is exposed by this vector

Measured on the audited host: for processes owned by another UID, `cat /proc/<pid>/environ`
returned `Permission denied` (kernel ptrace gate), while `/proc/<pid>/cmdline` was readable.
A full scan of every `/proc/*/{cmdline,environ}` during two live runs of the role's credential-task
pattern produced **zero `ENVIRON-HIT` lines** and did produce `CMDLINE-HIT` lines (appendix).
On the router itself everything runs as root, so environ and the 0600 file are equally accessible to
any root-level code execution — the environ vector adds nothing there. Conclusion: no process is
made more exposed by this PR through its environment, and `--auth-nocache` keeps credentials out of
the daemon's memory.

### 3. subprocess env inheritance — no credential leaks into child environments

The one full-environment inheritance site relevant to how these flows execute is
`scripts/conwrt/cmd_flow.py:90–93` (`env = {**os.environ, "IP": args.ip}` then
`subprocess.run(["sh", "-c", script], env=env)`). It is **pre-existing** (present in master and the
merge base; not touched by PR #55) and it forwards the operator's environment **downward to the
local interpreter only** — SSH does not propagate it to the router (no `SendEnv`/`AcceptEnv` is
configured in `scripts/ssh_utils.py:26–46`). Its real caveat is argv, not env: `sh -c <script>` puts
the rendered script (which can embed a credential heredoc) into the local process argv — the same
class as F-1, with the same stdin-based remedy already implemented for the apply path
(`apply.py:114–119`). Reported here for completeness; **not introduced by this PR**.

### 4. Docker / Compose — no issue found

No `docker run -e`, no Compose `environment:` block, and no container executes `openvpn` in this PR.
The PIA client runs in procd on the router, driven by UCI (`openvpn.pia`), where UCI values are not
placed into the daemon's environment.

---

## What the PR already gets right

* Credentials are written to a **mode-0600 file**, never to a command line, in the Python path
  (`openvpn_pia.py:331`) and to a chmod-600 file in the Ansible path
  (`tasks/main.yml:32`) — matching the brief's recommended remediation.
* `auth-nocache` is present in both profiles (`openvpn_pia.py:287`, `pia.ovpn.j2:20`), so the
  password is not retained in OpenVPN's memory.
* The apply path routes heredoc scripts (i.e. every credential write) over **SSH stdin**, not argv:
  `scripts/profile/apply.py:115–117` — `subprocess.run(ssh_cmd(ip, "sh -s"), input=payload, …)`.
  The `_HEREDOC_RE` branch (`apply.py:85`) is precisely what keeps the PIA secret out of argv on
  the conwrt path, and both lines are PR #55 additions.
* `no_log: true` on the Ansible credentials task (`tasks/main.yml:33`) keeps the secret out of
  Ansible output and logs.
* The ubus fallback that *would* leak the credential is off by default (`apply.py:444`).

---

## Appendix — canary evidence (reproducible)

Three canary secrets (`CANARY*_PIA_SECRET*`, inconsequential strings) were pushed through the exact
shapes used by the role and by the apply path while a scanner sampled every
`/proc/*/cmdline` and `/proc/*/environ` at 100 ms intervals. Working dir: `/tmp/ansible-argv-test`
(scratch, outside the repo; deleted after the run).

Run 2 — Ansible `raw` heredoc, the F-1 pattern (`playbook2.yml`, vars `pia_password:
"CANARY2_PIA_SECRET_91ab"`, `no_log: true`):

```
CMDLINE-HIT pid=2261170 cmd=ssh -C -o ControlMaster=auto -o ControlPersist=60s -o IdentityFile="…" …
CANARY2_PIA_SECRET_91ab
OPENWRT_EOF
chmod 600 /tmp/ansible-argv-canary2.txt
sleep 10
…
SCANNER_DONE hits=4          <-- 4 CMDLINE hits, 0 ENVIRON hits
```

Run 4 — bare `ssh host '<cmd>'`, to expose both ends of the channel:

```
CMDLINE-HIT pid=2275326 argv=ssh -o BatchMode=yes -o StrictHostKeyChecking=no localhost echo CANARY4_REMOTE_b3f1 >/dev/null; slee
CMDLINE-HIT pid=2275435 argv=bash -c echo CANARY4_REMOTE_b3f1 >/dev/null; sleep 6 & wait
SCANNER_DONE
```

`pid 2275326` = controller-side `ssh` argv; `pid 2275435` = remote-side shell argv. No `ENVIRON-HIT`
was observed in any run. The scanner read its canary from a file so its own argv could not
contaminate the results (`scan3.sh:3`: `CANARY=$(cat "$1")`).

Static evidence commands:

```bash
git diff 8bbce153945af22f1988309c72e3435e475c7b7f pr-55 > /tmp/pr55.diff
grep -n -E "^\+.*\bexport\b" /tmp/pr55.diff                                  # (no output)
grep -n -E "^\+.*(os\.environ|getenv)" /tmp/pr55.diff                        # 1 hit: CONWRT_EVIDENCE_DIR
grep -n -E "^\+.*\benv=" /tmp/pr55.diff                                      # (no output)
grep -n -E "^\+.*environment:" /tmp/pr55.diff                                # (no output)
git grep -n -E "OPENVPN_USER|OPENVPN_PASS|PIA_USER|PIA_PASS" pr-55           # (no output)
```
