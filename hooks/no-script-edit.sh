#!/usr/bin/env bash
# Menolak edit file lewat skrip python inline (`s.replace(...)` lalu `open(p,'w')`). Bila teks lama tidak
# ketemu, replace tidak berbuat apa-apa tanpa error, jadi "perbaikan" tidak pernah terpasang; edit seperti ini
# juga melewati format-after-edit dan meminta izin user di setiap panggilan. Tool Edit gagal keras bila teks
# tidak ketemu.
cmd="$(jq -r '.tool_input.command // empty' 2>/dev/null)"
[ -n "$cmd" ] || exit 0
grep -qE 'python3?( -I)? (-|-c)' <<<"$cmd" || exit 0
grep -q '\.replace(' <<<"$cmd" || exit 0
grep -qE "open\([^)]*['\"]w['\"]|write_text\(" <<<"$cmd" || exit 0
jq -n '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny",
  permissionDecisionReason: "clint: edit file pakai tool Edit (MultiEdit untuk banyak tempat), bukan python inline dengan .replace(): replace yang tidak menemukan teks lama diam saja, jadi perubahan bisa tidak terpasang tanpa ketahuan. Tulis file baru utuh dengan Write."}}'
