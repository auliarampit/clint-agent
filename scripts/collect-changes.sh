#!/usr/bin/env bash
# Kumpulkan bahan change-tracker dalam SATU panggilan (hemat token: tanpa puluhan putaran git/grep).
# Pakai: collect-changes.sh <dir-project> [sejak]   (sejak default: 3 hari; format git, mis. "2 days ago")
dir="$1"; sejak="${2:-3 days ago}"; cfg="$dir/.claude/clint.json"
[ -f "$cfg" ] || { echo "TIDAK ADA .claude/clint.json di $dir"; exit 0; }
cd "$dir" || exit 0
jq_() { jq -r "$1" "$cfg" 2>/dev/null; }
repo() {  # $1 nama, $2 path, $3 branch
  local p="$2" b="$3"; echo "### $1 ($p, $b)"
  [ -d "$p/.git" ] || git -C "$p" rev-parse --git-dir >/dev/null 2>&1 || { echo "(bukan repo git)"; return; }
  local sebelum; sebelum="$(git -C "$p" rev-parse HEAD 2>/dev/null)"
  git -C "$p" fetch -q origin "$b" 2>/dev/null
  if [ -z "$(git -C "$p" status --porcelain 2>/dev/null)" ] && [ "$(git -C "$p" branch --show-current)" = "$b" ]; then
    git -C "$p" pull -q --ff-only 2>/dev/null && echo "pull: ok" || echo "pull: gagal (lihat manual)"
  else
    echo "pull: dilewati (working tree tidak bersih atau bukan di $b; dibandingkan dengan origin/$b)"
  fi
  echo "-- commit sejak $sejak (maks 25):"
  git -C "$p" log "origin/$b" --since="$sejak" --format='%h %ad %an: %s' --date=format:'%d/%m %H:%M' -25 2>/dev/null
  echo "-- file berubah (maks 40):"
  local awal; awal="$(git -C "$p" log "origin/$b" --since="$sejak" --format=%H 2>/dev/null | tail -1)"
  [ -n "$awal" ] && git -C "$p" diff --stat=100 "$awal^" "origin/$b" 2>/dev/null | tail -41
}
repo "kerja" "." "$(jq_ '.baseBranch // "dev"')"
jq -c '.relatedRepos[]?' "$cfg" 2>/dev/null | while read -r r; do
  repo "$(jq -r .name <<<"$r")" "$(jq -r .path <<<"$r")" "$(jq -r '.branch // "main"' <<<"$r")"
done
fb="$(jq_ '.docs.feedback // empty')"
if [ -n "$fb" ] && [ "$fb" != "TIDAK ADA" ] && [ -d "$fb" ]; then
  echo "### feedback/bug masih open ($fb) — baris tabel saja, maks 60"
  grep -rn -i -E "\| *(open|belum|sebagian|reopen|ditolak|in progress)[^|]*\|" "$fb" --include='*.md' 2>/dev/null | cut -c1-260 | head -60
fi
pic="$(jq_ '.docs.pic // empty')"; nama="$(jq -r '.name[]?' "$HOME/.config/clint/user.json" 2>/dev/null | paste -sd'|' -)"
if [ -n "$pic" ] && [ "$pic" != "TIDAK ADA" ] && [ -e "$pic" ] && [ -n "$nama" ]; then
  if [ -f "$pic" ]; then f="$pic"; else
    f="$(grep -l -i -E '^status: *(active|aktif)' "$pic"/*.md 2>/dev/null | grep -E '/(s|sprint-?)[0-9]+[^/]*\.md$' | sort -V | tail -1)"
    [ -n "$f" ] || f="$(ls "$pic"/*.md 2>/dev/null | grep -E '/(s|sprint-?)[0-9]+[^/]*\.md$' | sort -V | tail -1)"
  fi
  base="$(jq_ '.baseBranch // "dev"')"
  echo "### Butir Anda yang belum selesai ($f)"
  echo "Format: ID | judul | kolom belum selesai | commit terakhir yang menyebut ID (seluruh histori origin/$base)"
  awk -F'|' -v nama="$nama" '
    function trim(s) { gsub(/^[ \t]+|[ \t]+$/, "", s); return s }
    /^\|[ :-]+\|/ { hdr = prev; next }
    /^\|/ {
      prev = $0
      if (tolower($0) !~ tolower(nama)) next
      split(hdr, h, "|"); sisa = ""
      for (i = 3; i < NF; i++) {
        c = trim($i)
        if (c ~ /^(⬜|🔄|🧪|🐞|🚫|Open|To Do|In Progress|Blocked|On QA|Scheduled)$/) sisa = sisa " " trim(h[i]) ":" c
      }
      judul = (tolower(trim($3)) ~ tolower(nama)) ? "(baris gerbang modul)" : substr(trim($4), 1, 70)
      if (sisa != "") print trim($2) "\t" judul "\t" sisa
    }' "$f" 2>/dev/null | head -60 | while IFS=$'\t' read -r id judul sisa; do
      c="$(git log "origin/$base" -E --grep="${id}([^0-9A-Za-z]|$)" --format='%h %ad %s' --date=format:'%d/%m' 2>/dev/null \
        | grep -v -E '^[0-9a-f]+ [0-9/]+ (docs|Merge)' | head -1 | cut -c1-90)"
      echo "$id | $judul |$sisa | commit kode: ${c:--}"
    done
fi
