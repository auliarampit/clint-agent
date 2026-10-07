#!/usr/bin/env bash
# Cari folder project ber-clint yang namanya cocok dengan teks bebas (mis. "toko online").
# Mengembalikan path terbaik, atau kosong. Pakai: cari-proyek.sh "<teks>"
norm(){ tr '[:upper:]' '[:lower:]' | tr -cd 'a-z0-9\n'; }
teks="$(printf '%s' "$1" | norm)"; [ -n "$teks" ] || exit 0
for base in "$HOME/Desktop" "$HOME/Projects" "$HOME/Developer" "$HOME/code"; do
  [ -d "$base" ] && find "$base" -maxdepth 5 -path '*/.claude/clint.json' -not -path '*/node_modules/*' 2>/dev/null
done | while read -r f; do
  dir="$(dirname "$(dirname "$f")")"
  rel="$(printf '%s' "${dir#$HOME/}" | norm)"
  # skor = panjang potongan path (folder project + induknya) yang muncul di teks
  skor=0
  for seg in "$(basename "$dir")" "$(basename "$(dirname "$dir")")"; do
    s="$(printf '%s' "$seg" | norm)"; [ -n "$s" ] && case "$teks" in *"$s"*) skor=$((skor+${#s}));; esac
  done
  [ "$skor" -gt 0 ] && echo "$skor $dir"
done | sort -rn | head -1 | cut -d' ' -f2-
