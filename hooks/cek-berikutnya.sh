#!/usr/bin/env bash
# Stop hook: blok "Berikutnya" tidak boleh menyarankan langkah yang sedang dikerjakan sesi lain
# (klaim di ~/Library/Logs/clint/kerja/). Aturannya ada di skill develop bagian 6; hook ini memeriksanya dengan mesin.
dir="${CLAUDE_PROJECT_DIR:-$PWD}"
[ -f "$dir/.claude/clint.json" ] || exit 0
input="$(cat)"
[ "$(jq -r '.stop_hook_active // false' <<<"$input")" = "true" ] && exit 0
sid="$(jq -r '.session_id // ""' <<<"$input")"
pesan="$(jq -r '.last_assistant_message // ""' <<<"$input")"
grep -q '/clint:' <<<"$pesan" || exit 0
root="$(cd "$(dirname "$0")/.." && pwd)"
kena="$(python3 "$root/scripts/update-report.py" cek-berikutnya --dir "$dir" --session "$sid" <<<"$pesan" 2>/dev/null)"
[ -n "$kena" ] || exit 0
jq -n --arg k "$kena" --arg r "python3 \"$root/scripts/update-report.py\" langkah --dir \"$dir\" --session $sid" \
  '{decision: "block", reason: ("Blok Berikutnya menyarankan langkah yang sedang dikerjakan sesi lain:\n" + $k +
    "\nTulis ulang blok Berikutnya dari keluaran `" + $r + "` (dan plan-status.py --session bila ada rencana): langkah itu cukup jadi baris info \"Sedang dikerjakan sesi lain: …\", bukan langkah siap ketik.")}'
