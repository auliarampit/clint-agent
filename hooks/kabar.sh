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
cfg="$HOME/.config/clint"
[ -f "$cfg/diam" ] && suara=0
# "Bisukan sampai besok": tanpa suara dan tanpa notifikasi sampai tanggal itu
if [ -z "$CLINT_PAKSA" ] && [ -f "$cfg/bisu-sampai" ]; then
  [[ "$(date +%F)" < "$(cat "$cfg/bisu-sampai")" ]] && exit 0 || rm -f "$cfg/bisu-sampai"
fi

judul="clint · $(basename "$dir")"
osascript -e "display notification \"${teks//\"/\\\"}\" with title \"${judul}\"" >/dev/null 2>&1
[ "$suara" = 1 ] && command -v say >/dev/null && (say -v Damayanti "$teks" >/dev/null 2>&1 &)
exit 0
