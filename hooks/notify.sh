#!/usr/bin/env bash
# Menyampaikan kabar singkat (notifikasi Mac + suara) yang ditulis skill ke file kabar.
# Dipanggil hook Stop, atau langsung: notify.sh "kalimat".
if [ -n "$1" ]; then teks="$1"; else
  sid=""
  if [ ! -t 0 ]; then sid="$(jq -r '.session_id // empty' 2>/dev/null)"; fi
  file=""
  for f in ${sid:+"${TMPDIR:-/tmp}/clint-kabar-$sid.txt"} "${TMPDIR:-/tmp}/clint-kabar.txt"; do
    [ -s "$f" ] && { file="$f"; break; }
  done
  [ -n "$file" ] || exit 0
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
osascript -e 'on run a' -e 'display notification (item 1 of a) with title (item 2 of a)' -e 'end run' \
  "$teks" "$judul" >/dev/null 2>&1
# Suara mengikuti bahasa pribadi (~/.config/clint/user.json); English memakai suara bawaan sistem.
[ "$(jq -r '.language // "en"' "$cfg/user.json" 2>/dev/null)" = "id" ] && vo=(-v Damayanti) || vo=()
[ "$suara" = 1 ] && command -v say >/dev/null && (say "${vo[@]}" "$teks" >/dev/null 2>&1 &)
exit 0
