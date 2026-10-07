#!/usr/bin/env bash
# Menyampaikan kabar singkat (notifikasi Mac + suara) yang ditulis skill ke file kabar.
# Dipanggil hook Stop, atau langsung: kabar.sh "kalimat".
file="${TMPDIR:-/tmp}/clint-kabar.txt"
if [ -n "$1" ]; then teks="$1"; else
  [ -s "$file" ] || exit 0
  teks="$(head -c 300 "$file")"; rm -f "$file"
fi
dir="${CLAUDE_PROJECT_DIR:-$PWD}"
[ "$(jq -r '.suara // true' "$dir/.claude/clint.json" 2>/dev/null)" = "false" ] && suara=0 || suara=1
[ "${CLINT_SUARA:-1}" = "0" ] && suara=0

judul="clint · $(basename "$dir")"
osascript -e "display notification \"${teks//\"/\\\"}\" with title \"${judul}\"" >/dev/null 2>&1
[ "$suara" = 1 ] && command -v say >/dev/null && (say -v Damayanti "$teks" >/dev/null 2>&1 &)
exit 0
