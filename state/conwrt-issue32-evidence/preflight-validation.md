FAIL

# conwrt issue #32 preflight — independent validation report

- Verdict: **FAIL** — the artifact under review (`run-log.md` in the manager
  evidence dir) does not exist; the preflight is a BLOCKED record split across
  three evidence files, and every device-evidence acceptance item (a)-(d) is
  uncaptured because the device (CF-WR632AX) was never reached. This FAIL is
  driven by an unreachable device, not by dishonest reporting: the BLOCKED
  record is complete and internally consistent, and no values were fabricated.
- Verifier run: 2026-10-01 ~13:50 local, workspace /home/c03rad0r/repos/conwrt,
  branch `pr-55`, working tree clean at start. Profile worker-reviewer-glm.
  Validation was read-only; the device was not contacted (the record itself
  shows every prior SSH attempt failed at connection level).

## Inputs examined

- `~/.hermes/profiles/manager/state/conwrt-issue32-evidence/preflight/`:
  - `reachability.txt` (attempt 1, 12:47) — BLOCKED, device powered off
  - `reachability-attempt2-20261001.txt` (attempt 2, ~13:05) — BLOCKED
  - `clock-sync.txt` (attempt 3, ~13:15-13:20) — NO-GO
  - `run-log.md` — ABSENT at validation time (created afterwards by the
    validator, at the task-designated path, solely to carry the VALIDATION
    section; its preamble states this provenance).
- Parent evidence dir: five D1-D5 defect-analysis files (different subtask,
  repo-side document work — no device interaction).
- conwrt repo: `git status --porcelain` empty; `runs/` and `captures/` hold
  only `.gitkeep`; sole commit of 2026-10-01 before validation: cc5f134.

## Checklist (a)-(e)

- (a) Reachability + OpenWrt 25.12.4 evidence — FAIL
  - No verbatim `cat /etc/openwrt_release` output in any evidence file.
  - No successful SSH capture: `ssh root@192.168.1.1` → "No route to host"
    rc 255 (attempts 2-3); `ssh root@192.168.8.1` → "Connection refused".
  - OpenWrt version never confirmed on hardware; "25.12.4" exists only as
    repo-side documentation, which is not device evidence.
- (b) Recovery procedure genuinely tested — FAIL
  - Nothing was tested; no observed recovery output, no revert-verification
    output anywhere. The numbered "TO UNBLOCK" lists are operator
    instructions (power-on, FritzBox lease lookup, re-dispatch), not
    copy-pasteable device recovery commands with expected output.
- (c) Baseline capture — FAIL
  - All four artifacts ABSENT: no uci export, no /proc/mtd, no
    installed-packages list, no /etc/config/network copy in the evidence dir.
  - LAN IP, hostname, nodogsplash installed/running, hotplug script: each
    explicitly "UNKNOWN / not observed" — commands named, no outputs.
- (d) Clock — FAIL (one element present)
  - PRESENT: explicit NO-GO statement (with rationale and flip conditions);
    host reference `date -u` = 2026-10-01 11:15:16 UTC.
  - MISSING: on-device `date -u`, NTP status (`sysntpd status` /
    `ps | grep ntp`), numeric drift ("could not be computed").
- (e) Negative check — PASS
  - No recipe/wizard work started (stated in all three reports; corroborated:
    clean tree, empty runs//captures/, only docs commit cc5f134 today, other
    evidence files are repo-side defect analysis).
  - No permanent config change left behind: no SSH session ever succeeded,
    no serial adapters on host, all probes read-only — no write path to the
    device was ever established.

## BLOCKED-report completeness (required statement)

- Attempts: substantively complete — every session probe documented with
  verbatim commands and observed results (ethtool/counters with RX 0, ping
  100% loss, tcpdump 0 packets, full 2.4+5 GHz scans with BSSID lists and no
  COMFAST OUI 40:a5:ef, SSH attempts with rc, USB/serial enumeration,
  netbird/ssh-config/known_hosts checks, runbook-absence check, 192.168.8.1
  single-host probe ruled out, consent denials without rephrased retries).
  Attempts cross-reference each other; prior blocked session
  20260912_052933_4d7e5b (2026-09-12) cited.
- Current hardware state: stated with evidence — CF-WR632AX powered OFF (or
  wizard STA-invisible on home WLAN, FritzBox-lease unblock documented);
  USB-C powered so no PoE path; dead bench far end; no host serial or power
  control; operator unblock actions listed.
- Residual gaps in the BLOCKED record: (1) `run-log.md` was never created —
  the record is fragmented across three files (now consolidated for
  validation purposes by the validator-created run-log.md); (2) the
  2026-09-12 session is characterized secondhand. Neither gap conceals an
  unreported attempt.

## One-line verdict

FAIL — preflight deliverable absent and (a)-(d) uncaptured because the device
was never reached; BLOCKED reports honest, complete, side-effect free (e
PASS); owner should re-issue preflight steps (a)-(d) only after the operator
performs the documented unblock (power-on + network path or FritzBox lease
lookup). Gaps reported, not fixed; device untouched by validator.
