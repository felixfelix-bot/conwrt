# PR #55 (head ec5c60d9) — PIA OpenVPN module logging / secret-leakage audit

Audited: 2026-09-17 · Target: `scripts/use_cases/openvpn_pia.py` at commit
`ec5c60d9` ("feat(vpn): PIA OpenVPN use case + VPN setup library proposal") plus
all PR-touched Python files that participate in the module's render/apply
pipeline. Every finding has a file+line citation from that commit. Line numbers
below are the line numbers in the file *as of ec5c60d9*.

Method: full read of the module and the PR pipeline files; `git grep` sweeps for
`print(|logger|logging.|syslog|stderr|redact` across the PR; an empirical
reproduction of the generated script in a detached scratch worktree at
ec5c60d9 (credentials `p1234567` / `TopSecretPW42`) to confirm what the dry-run
actually prints.

Pipeline overview (so the findings make sense):

- `openvpn_pia.py:502` — `build_configure=lambda p: render_shell(_build_openvpn_pia_ops(p))`
- `openvpn_pia.py:331` — credentials op:
  `WriteFile(path=AUTH_FILE, content=f"{r['username']}\n{r['password']}\n", mode="600")`
- `scripts/profile/ops.py:183-195` (`render_writefile`) — embeds `op.content`
  verbatim into a shell heredoc: `cat > '<path>' <<'<delim>'\n<body><delim>\nchmod <mode> <path>`
- `scripts/profile/ops.py:249-250` — `render_shell` emits that string for the op.
- `scripts/profile/builder.py:447-458` — the rendered string lands on
  `step.configure_script`.
- `conwrt configure --dry-run`
  (`scripts/conwrt/commands_configure.py:54-62` → `postflash.py:90` →
  `apply_plan(dry_run=True)`) reaches the print sites in `apply.py`/`render.py`.

---

## Finding 1 — HIGH: dry-run prints the plaintext PIA username and password

`conwrt configure --dry-run` with the `openvpn-pia` use case prints the plain PIA
credentials to stdout. Two distinct print sites, both fed by the same string:

**1a. Full heredoc dump**
- `scripts/profile/apply.py:294-296`:
  ```
  print("SSH commands that would run:")
  for line in ssh_steps_preview(plan):
      print(f"  {line}")
  ```
- `scripts/profile/render.py:57-61` (`ssh_steps_preview`) passes every non-comment
  line of `step.configure_script` through verbatim:
  ```
  if step.configure_script:
      lines.append(f"# {step.label}")
      for ln in step.configure_script.strip().splitlines():
          if ln.strip() and not ln.strip().startswith("#"):
              lines.append(ln.strip())
  ```
The heredoc body produced by `render_writefile` (ops.py:190-195) for the
credentials op at openvpn_pia.py:331 is two plain lines — the username and the
password. They survive the comment filter and are printed.

Verified at ec5c60d9 (scratch worktree, `render_shell(_build_openvpn_pia_ops(...))`
with username `p1234567`, password `TopSecretPW42`); the first preview lines are
exactly:
```
cat > '/etc/openvpn/pia-auth.txt' <<'OPENWRT_EOF'
p1234567
TopSecretPW42
OPENWRT_EOF
chmod 600 /etc/openvpn/pia-auth.txt
```

**1b. 120-char plan preview**
- `scripts/profile/render.py:37-39` (`print_plan`):
  ```
  if step.configure_script and step.include_in_post_install:
      preview = step.configure_script.replace("\n", " ")[:120]
      print(f"       ssh: {preview}{'...' if len(step.configure_script) > 120 else ''}")
  ```
Because the credentials `WriteFile` is the *second* op emitted
(openvpn_pia.py:329-332 — Comment then WriteFile), the heredoc begins near char
43 of the script. Empirically, the preview slice is:
`# --- Private Internet Access (OpenVPN) --- cat > '/etc/openvpn/pia-auth.txt' <<'OPENWRT_EOF' p1234567 TopSecretPW42 OPE`
— i.e. the full username AND a full short-to-typical-length password.

Why unsafe: dry-run is the operator-facing, "safe" mode; its output goes to the
terminal scrollback, to shell history when piped, to CI logs when automated, and
there is no redaction anywhere on this path. The credentials are the PIA account
password — long-lived, multi-use, and tied to a paid account.

Fixes (either suffices; recommend both):
1. Minimal, in `scripts/profile/render.py`: in `ssh_steps_preview` and the
   `print_plan` preview, redact heredoc bodies whose `cat >` target matches a
   credentials path (e.g. `*pia-auth.txt`, `/etc/openvpn/*-auth*`): replace the
   lines between the heredoc opener and its closing delimiter with
   `<REDACTED:CREDENTIALS>`.
2. Robust: add a `sensitive: bool = False` field to `WriteFile`
   (`scripts/profile/ops.py:90`), set `sensitive=True` at
   `openvpn_pia.py:331`, and give `render_writefile` a preview/redact mode that
   emits `cat > '<path>' <<'…'\n<REDACTED:CREDENTIALS>\n…\nchmod …`; have the
   render.py preview functions use it instead of raw `configure_script` text.

---

## Finding 2 — MEDIUM: the redaction pipeline does not cover bare username/password (or bare token) strings

- `scripts/redact-output.sh:64-222` defines ten redaction patterns: PEM key
  blocks (68-71), `Authorization:`/`Cookie:`/`api_key=` tokens (74-81),
  SHA fingerprints (84-87), keyword-adjacent serial numbers (90-95), SSIDs
  (98-102), GPS (105-109), MAC tails (112-115), public IPv6 (118-139), public
  IPv4 (142-189), private-TLD hostnames (192-207).
- `scripts/commit-run.sh:61-91` (PII safety grep before commit) checks full MAC,
  serial-looking strings, and public IPv4 only.

Nothing in either pass matches a standalone password line, a `user:pass` pair
without an `Authorization:`/`Cookie:`/`api_key=` prefix, or the body of an
`auth-user-pass` heredoc. If a rendered `openvpn-pia` configure script (or any
terminal capture of the dry-run in Finding 1) is ever dropped into a run
directory's `step-*/raw/`, `commit-run.sh` will commit it to the repo **in
plaintext and will call it verified**.

Today the dry-run path prints to stdout only and does not write into run dirs,
so this is a defense-in-depth gap rather than an automatic leak — hence MEDIUM.
(Also note pattern 1 (public IPv4) *does* work well here: the PIA server IPs in
the generated `.ovpn` would be redacted.)

Fix: add a pattern to `redact-output.sh` that redacts the body of heredocs whose
`cat >` target matches `/pia-auth|auth-user-pass|*/secrets?/` (a 3-line window:
opener, body lines, delimiter), plus a generic `password[=:\s]+` /
`p-number`-adjacent rule; add a corresponding probe to `verify_no_pii`
(redact-output.sh:226-264) and to the commit-run.sh PII grep so the gap is
fail-closed. Note the sibling WireGuard module
`scripts/use_cases/vpn_providers/pia.py:40-42` embeds `-u "{username}:{password}"`
in its generated script directly — same exposure class (pre-existing, outside
PR #55, worth fixing together).

---

## Finding 3 — INFO: the module's own log calls carry no secrets

Every `logger`/log-producing call embedded by the Python module (the shell
templates that run on the router) was checked against its interpolations:

| Line (openvpn_pia.py) | Call | Interpolated values | Verdict |
|---|---|---|---|
| 136 | `logger -t pia-watchdog "FAIL-OPEN: WAN fallback + normal DNS restored"` | none | safe — static |
| 158 | `logger -t pia-watchdog "ENFORCE: DNS lock on (phase=$phase)"` | `$phase` ∈ {validation,enforced} (validated, openvpn_pia.py:298-318) | safe |
| 168 | `exec >>"$LOG" 2>&1` (`/tmp/pia-watchdog.log`) | captures pia-health verdicts | safe — flags + in-tunnel gateway IP only |
| 206 | `logger … "phase -> enforced after ${stable_total}s healthy"` | integer counter | safe |
| 223 | `logger … "unhealthy ${down}s -> restarting openvpn (attempt $restart_count)"` | integers | safe |
| 232 | `logger … "removed unreliable remote $bad (was $remaining)"` | `$bad` = a public PIA **server** IP grepped out of `logread`; `$remaining` = integer | safe (server IP is not a credential; on-device syslog/ring buffer only) |
| 240 | `logger … "down ${down}s > timeout ${fail_open_timeout}s -> FAIL OPEN"` | integers | safe |
| 461 | `ShellCommand(command="logger -t conwrt 'openvpn-pia configured (phase=%s)'" % r["phase"])` | enum | safe |

The health-probe output template (openvpn_pia.py:112-119) logs only
`proc/route/ping/dns` booleans and the tunnel gateway IP (`gw=${gw:-?}`).

No call logs the full config object, the generated `.ovpn` content, an argv
list, environment variables, the credentials-file contents, or a PIA API token.

---

## Finding 4 — INFO: `verb 3` in the generated OpenVPN profile

`openvpn_pia.py:288` sets `verb 3` and `openvpn_pia.py:287` sets `auth-nocache`
in the `.ovpn` written to the device. OpenVPN at `verb 3` logs connection events
and endpoint IPs but not `auth-user-pass` contents; `auth-nocache` avoids
in-memory credential caching. This is a config directive, not a Python log call
— noted for completeness (verb ≥4 would dump TLS key material; not used).

---

## Redaction-helper coverage (explicitly requested)

Helper: `scripts/redact-output.sh` (`apply_redaction_pipeline`, lines 211-222)
plus the commit gate `scripts/commit-run.sh:61-91`.

- **Token fields**: covered only when keyword-adjacent (`Authorization:`,
  `Cookie:`, `api_key=`). A bare PIA token string would survive.
- **Username/password fields**: **not covered** — no pattern matches
  `auth-user-pass` file contents, standalone password lines, or `user:pass`
  pairs without those prefixes. The verification pass (redact-output.sh:226-264)
  never greps for password shapes, so the miss is silent.
- This module itself never passes credentials through the redaction pipeline
  (dry-run goes to stdout; apply goes over an encrypted SSH session), which is
  why the gap is rated MEDIUM (latent) not HIGH.

---

## Explicit "no issue found" statements (per last task requirement)

- **Config logging (full config object / generated .ovpn)**: **NO ISSUE
  FOUND.** Neither the module nor the PR's `ops.py` changes log or print the
  resolved params dict (`_resolve_params`, openvpn_pia.py:298-324) or the
  generated `.ovpn` (`_build_profile`, openvpn_pia.py:271-296); the `.ovpn`
  heredoc contains only public PIA server IPs, cipher names, a public CA URL,
  and the *filename* of the auth file (openvpn_pia.py:283 —
  `f"auth-user-pass {AUTH_FILE}"`). The dry-run credential leak in Finding 1 is
  the credentials `WriteFile` at openvpn_pia.py:331, **not** the config object.
- **argv / environment variables**: **NO ISSUE FOUND.** The module performs no
  `os.environ`/`sys.argv` reads and logs no argv or environment data; the only
  AWK `print` (openvpn_pia.py:90) prints a gateway IP from `ip route get`.
- **PIA API token**: **NO ISSUE FOUND** in this module — the OpenVPN path is
  username/password via `auth-user-pass` (`AUTH_FILE`, openvpn_pia.py:69); no
  token API is used. (The sibling WireGuard module pia.py does token exchange
  and embeds credentials on the curl command line — pre-existing, outside
  PR #55, flagged in Finding 2's fix.)
- **On-device storage of credentials**: not a leak —
  `WriteFile(path=AUTH_FILE, …, mode="600")` (openvpn_pia.py:331) is rendered
  with `chmod 600` (ops.py:194), and the heredoc crosses the wire inside an
  encrypted SSH stdin pipe (`apply.py:96-123`, `sh -s`). The ubus path maps the
  same op to an exec call (ops.py:331-336), whose dry-run logs only the call
  count (apply.py:505, `f"{step.label}: sending {len(calls)} ubus call(s)..."`).
- **Non-Python PR file, noted for completeness**: the Ansible role writes the
  credentials with `no_log: true` (ansible/roles/pia_openvpn/tasks/main.yml:27-33)
  and its only `debug` call logs the health-probe stdout
  (…/tasks/main.yml:169-171). The `.ovpn` write task (…/tasks/main.yml:35-40)
  has no `no_log` but contains no secrets.
- **tests/test_openvpn_pia_ops.py**: uses dummy creds (`p1234567`/`s3cret`),
  no prints of rendered output — fine.

---

## Summary of required actions (priority order)

1. **HIGH** — Stop dry-run from printing the credentials heredoc: render.py
   preview redaction for credential heredocs, or a `sensitive=True` WriteFile
   flag used by previews (Finding 1).
2. **MEDIUM** — Close the redaction gap for bare credentials/tokens in
   redact-output.sh + commit-run.sh, including the `pia.py` curl `-u` case
   (Finding 2).

Nothing else in the module's logging needs changing.
