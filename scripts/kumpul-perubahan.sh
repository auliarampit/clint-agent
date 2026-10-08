#!/usr/bin/env bash
# Kumpulkan bahan pelacak-perubahan dalam SATU panggilan (hemat token: tanpa puluhan putaran git/grep).
# Pakai: kumpul-perubahan.sh <dir-project> [sejak]   (sejak default: 3 hari; format git, mis. "2 days ago")
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
pic="$(jq_ '.docs.pic // empty')"; nama="$(jq -r '.nama[]?' "$HOME/.config/clint/saya.json" 2>/dev/null | paste -sd'|' -)"
if [ -n "$pic" ] && [ "$pic" != "TIDAK ADA" ] && [ -e "$pic" ] && [ -n "$nama" ]; then
  f="$(ls -t "$pic"/*.md 2>/dev/null | head -1)"; [ -f "$pic" ] && f="$pic"
  echo "### PIC — baris yang menyebut nama Anda ($f, maks 40)"
  grep -n -i -E "$nama" "$f" 2>/dev/null | cut -c1-220 | head -40
fi
