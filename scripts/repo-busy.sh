#!/usr/bin/env bash
# repo-busy.sh <path di repo> [sid-sendiri] → "bebas" (exit 0) atau "dipakai: <alasan>" (exit 1).
# Repo utama dipakai bila: sesi clint lain bekerja di path repo utama, sesi Claude lain sedang aktif
# di folder repo itu, atau working tree-nya kotor.
dir="${1:-$PWD}"; own="$2"
common="$(git -C "$dir" rev-parse --path-format=absolute --git-common-dir 2>/dev/null)" || { echo "bukan repo git: $dir"; exit 2; }
repo="$(cd "$(dirname "$common")" && pwd -P)"
now="$(date +%s)"; sesi="$HOME/.config/clint/sesi"; kerja="$HOME/Library/Logs/clint/kerja"

if [ -n "$(git -C "$repo" status --porcelain --untracked-files=normal 2>/dev/null | head -1)" ]; then
  echo "dipakai: working tree repo utama tidak bersih"; exit 1
fi

for f in "$sesi"/*.json; do
  [ -f "$f" ] || continue
  sid="$(basename "$f" .json)"; [ "$sid" = "$own" ] && continue
  if [ -f "$kerja/$sid.json" ] && [ $(( now - $(stat -f %m "$kerja/$sid.json") )) -lt 10800 ]; then
    p="$(jq -r '.path // empty' "$kerja/$sid.json" 2>/dev/null)"
    [ -n "$p" ] && [ "$(cd "$p" 2>/dev/null && pwd -P)" = "$repo" ] && { echo "dipakai: sesi clint lain ($(jq -r '.label // .judul // "develop"' "$kerja/$sid.json"))"; exit 1; }
    continue
  fi
  read -r cwd st up < <(jq -r '[.cwd // "", .status // "", (.update // 0)] | @tsv' "$f" 2>/dev/null)
  cwd="$(cd "$cwd" 2>/dev/null && pwd -P)"
  case "$cwd/" in "$repo"/*) ;; *) continue ;; esac
  case "$st" in bekerja|menunggu|latar) [ $(( now - ${up%.*} )) -lt 900 ] && { echo "dipakai: sesi Claude lain sedang $st di repo ini"; exit 1; } ;; esac
done
echo "bebas"
