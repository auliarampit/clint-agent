#!/usr/bin/env bash
# Sapaan pagi: satu /clint:cek semua untuk seluruh project aktif (mode baca saja), lalu
# layar laporan terbuka + kalimat inti dibacakan + notifikasi, bersamaan saat laporan siap.
# Pakai: sapaan-pagi.sh [--uji] [<dir-project> ...]   (tanpa dir: semua project aktif)
# Log dibersihkan otomatis: laporan > 3 hari dihapus, log teknis hanya disimpan bila gagal.
root="$(cd "$(dirname "$0")/.." && pwd)"
claude="$(ls -d "$HOME"/.vscode/extensions/anthropic.claude-code-*-darwin-arm64 2>/dev/null | sort -V | tail -1)/resources/native-binary/claude"
[ -x "$claude" ] || claude="$(command -v claude)"
log="$HOME/Library/Logs/clint"; mkdir -p "$log"
find "$log" -type f -mtime +3 -delete 2>/dev/null
[ -s "$log/launchd.err" ] || rm -f "$log/launchd.err"
uji=0; [ "$1" = "--uji" ] && { uji=1; shift; }
json="$log/$(date +%F-%H%M).json"; html="${json%.json}.html"
kabar="${TMPDIR:-/tmp}/clint-kabar.txt"; rm -f "$kabar" "$json"

if [ $# -gt 0 ]; then proyek="$(printf '%s\n' "$@")"; else proyek="$(bash "$root/scripts/proyek-aktif.sh" 3)"; fi
[ -n "$proyek" ] || exit 0
kerja="$(echo "$proyek" | head -1)"
# Status untuk menu bar selama pemeriksaan berjalan.
n="$(echo "$proyek" | wc -l | tr -d ' ')"; daftar="$(echo "$proyek" | xargs -n1 basename | paste -sd, - | sed 's/,/, /g')"
jq -n --arg n "$n" --arg d "$daftar" --arg m "$(date +%H.%M)" \
  '{judul:("cek " + $n + " project"), mulai:$m, label:("cek " + $n), tahap:("memeriksa " + $d), catatan:"laporan terbuka begitu selesai"}' > "$log/kerja.json"
trap 'rm -f "$log/kerja.json"' EXIT
tambah=(--add-dir "$log"); while read -r p; do tambah+=(--add-dir "$p"); done <<< "$proyek"

if [ "$uji" = 1 ]; then
  prompt="Tanpa memakai agent: tulis file $json berisi JSON contoh laporan pagi (format skill clint:cek mode semua) untuk project berikut, isi data contoh: $(echo $proyek). Tulis dengan tool Write."
else
  prompt="/clint:cek semua $(echo $proyek) --json $json --tanpa-layar"
fi

( cd "$kerja" && "$claude" -p "$prompt" "${tambah[@]}" \
    --allowedTools Read Grep Glob Agent Task "Edit(~/Library/Logs/clint/**)" "Bash(git fetch:*)" "Bash(git pull:*)" \
      "Bash(git log:*)" "Bash(git -C:*)" "Bash(git status:*)" "Bash(git rev-list:*)" \
      "Bash(git worktree list:*)" "Bash(git branch:*)" "Bash(glab:*)" "Bash(gh:*)" \
      "Bash(df:*)" "Bash(ls:*)" "Bash(grep:*)" "Bash(sed:*)" "Bash(jq:*)" "Bash(cat:*)" \
      "Bash(head:*)" "Bash(tail:*)" "Bash(wc:*)" "Bash(printf:*)" "Bash(date:*)" "Bash(bash:*)" "Bash(find:*)" \
    --disallowedTools "Bash(git push:*)" "Bash(git commit:*)" "Bash(git reset:*)" \
    < /dev/null > "${json%.json}.log" 2>&1 )

if [ -s "$json" ] && python3 "$root/scripts/render-laporan.py" "$json" "$html"; then
  open "$html"
  [ -s "$kabar" ] || jq -r '.kalimat // empty' "$json" > "$kabar"
  cp "$json" "$log/terakhir.json"
  rm -f "${json%.json}.log" "$json"
else
  printf '%s' "Sapaan pagi gagal membuat laporan. Lihat log clint." > "$kabar"
fi
CLAUDE_PROJECT_DIR="$kerja" bash "$root/hooks/kabar.sh"
