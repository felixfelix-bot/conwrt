# Raw command blocks extracted from net4sats-lan-move.md

Verbatim transcription of the two command blocks in `state/conwrt-issue32-evidence/net4sats-lan-move.md`. Nothing here is paraphrased, normalized, reflowed or re-derived.

Source provenance (read-only; the source file was not modified):
- path: `state/conwrt-issue32-evidence/net4sats-lan-move.md`
- sha256: `9451d9a44831f7ccadf5b63484f02f4b547eca81f46e491cf786499f4fe600a8`
- repo: `/home/c03rad0r/repos/conwrt`, branch `feat/vpn-provider-setup`, HEAD `9e098c07d36f02551fd075d4e758d1c01a886825`
- source file added by commit `93b2b30` and unchanged at HEAD (`git status --porcelain` / `git diff HEAD` for the path are both empty)
- 89 physical lines, UTF-8, LF endings, single final newline (8677 bytes)
- all line numbers below are 1-indexed physical line numbers of that file

## LAN-move command block — heading: `## net4sats flow`, lines: 6-15

Source label paragraph at line 5: `LAN-move commands (verbatim):`  
Fence-inclusive range 6-15 (opening fence line 6, command content lines 7-14, closing fence line 15). Source opening fence is ```` ```sh ````, preserved here because the source already labels the block `sh`.

```sh
# --- Move the LAN off 192.168.1.1 ---
ssh root@$IP sh <<'CONWRT_EOF'
# move LAN off 192.168.1.1 → 10.231.9.1 (10.231.9.0/24)
uci set network.lan.ipaddr='10.231.9.1'
uci set network.lan.netmask='255.255.255.0'
uci commit network
(/etc/init.d/network restart &) ; echo 'LAN moving to 10.231.9.1 — reconnect on that subnet'
CONWRT_EOF
```

## Read-back command block — heading: `## net4sats flow`, lines: 47-49

Source label paragraph at line 46: `Read-back commands (verbatim):`  
Fence-inclusive range 47-49 (opening fence line 47, content line 48, closing fence line 49). The source's opening fence for this block carries the info string `text` (line 47 is exactly ```` ```text ````); a bare fence is used below because the card permits only ```` ```sh ````/```` ```bash ```` info strings (when the source uses them) and otherwise a bare fence. Content bytes are unchanged either way; a composer that prefers the source's own info string can substitute it on the opening fence.

```
(none — the net4sats recipe emits no read-back/verification command; there is nothing to quote)
```

## Extraction notes

Fenced regions found in the source (scan for lines whose first three characters are backticks): {6, 15, 21, 44, 47, 49, 55, 81} — four blocks. Candidates considered:
- lines 6-15, info string `sh` — introduced by the label paragraph at line 5 `LAN-move commands (verbatim):`. The only sh-labelled fence and the only block of executable host/device commands. SELECTED as the LAN-move block.
- lines 21-44, bare fence — the per-model `network.lan.ipaddr` summary table; not a command block. Not selected.
- lines 47-49, info string `text` — introduced by the label paragraph at line 46 `Read-back commands (verbatim):`. The block the source itself designates as the read-back block. SELECTED as the read-back block.
- lines 55-81, info string `python` — the `render.py`/`target.py` emitter + binding snippet; source-code evidence, not a command the recipe emits. Not selected.

No ambiguity beyond the above: exactly one `sh`-labelled block and exactly one `text`-labelled block exist in the source, each introduced by an explicit label paragraph, so there is no competing candidate for either role.

Heading attribution: neither block sits under a markdown heading of its own. The only heading above both blocks — and the only markdown heading in the whole source file — is `## net4sats flow` at source line 1. Lines 5 and 46 are plain label paragraphs, not headings (they are recorded above for navigation only).

Read-back block: documented absence, NOT a transcription gap. The block EXISTS in the source and is transcribed above byte-for-byte; its entire content is the single parenthetical line 48. Because nothing is missing from the source, no `GAP:` line is emitted for it, and no GAP line applies anywhere in this file: the source exists, is readable, is non-empty, and both blocks were located and transcribed verbatim. If a consumer expected a command-bearing read-back block, the source asserts there is none — that is the source's finding, not a loss in transcription.

Byte fidelity (mechanically verified after writing this file):
- LAN-move block content == source physical lines 7-14, byte-for-byte (8 lines: step-title comment, the `ssh root@$IP sh <<'CONWRT_EOF'` heredoc opener, 2x `uci set`, `uci commit network`, the backgrounded network restart + `echo`, and the `CONWRT_EOF` heredoc terminator).
- Read-back block content == source physical line 48, byte-for-byte.
- Neither block contains a tab, a CR, a blank line or trailing whitespace. Both preserve the multi-byte UTF-8 characters used by the source: U+2192 RIGHTWARDS ARROW (source lines 9 and 63) and U+2014 EM DASH (source lines 9, 13 and 66).
- Shell quoting is untouched: `'10.231.9.1'`, `'255.255.255.0'`, the quoted heredoc delimiter `<<'CONWRT_EOF'` and the single-quoted `echo` argument all appear exactly as in the source.

Untouched by this task:
- `state/conwrt-issue32-evidence/net4sats-lan-move.md` — read only; sha256 still `9451d9a44831f7ccadf5b63484f02f4b547eca81f46e491cf786499f4fe600a8` and `git diff HEAD` for the path is empty.
- `state/conwrt-issue32-evidence/drafts/net4sats-raw-commands.md` is the only file written (this file).
- `state/conwrt-issue32-evidence/checklist.md` — neither read nor written; it does not exist in the working tree (`git ls-files` and a filesystem search over the conwrt tree both show no checklist.md).
- `docs/wizard-bundle.json` — not opened, not modified by this task.
