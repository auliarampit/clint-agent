#!/usr/bin/env bash
# Sapaan pagi: satu /clint:status all untuk seluruh project aktif (mode baca saja), lalu
# layar laporan terbuka + kalimat inti dibacakan + notifikasi, bersamaan saat laporan siap.
# Pakai: morning-greeting.sh [--uji] [<dir-project> ...]   (tanpa dir: semua project aktif)
# Log dibersihkan otomatis: laporan > 3 hari dihapus, log teknis hanya disimpan bila gagal.
root="$(cd "$(dirname "$0")/.." && pwd)"
lang="$(jq -r '.language // "en"' "$HOME/.config/clint/user.json" 2>/dev/null)"
t(){ if [ "$lang" = "id" ]; then printf '%s' "$1"; else printf '%s' "$2"; fi; }

cari_claude(){
  local c
  for c in "$(command -v claude)" "$HOME/.local/bin/claude" "$HOME/.claude/local/claude" \
           /opt/homebrew/bin/claude /usr/local/bin/claude; do
    [ -n "$c" ] && [ -x "$c" ] && { echo "$c"; return; }
  done
  c="$(ls -d "$HOME"/.vscode/extensions/anthropic.claude-code-*-darwin-{arm64,x64} \
             "$HOME"/.cursor/extensions/anthropic.claude-code-*-darwin-{arm64,x64} 2>/dev/null | sort -V | tail -1)"
  [ -n "$c" ] && [ -x "$c/resources/native-binary/claude" ] && echo "$c/resources/native-binary/claude"
}

log="$HOME/Library/Logs/clint"; mkdir -p "$log/kerja"
find "$log" -type f -mtime +3 -delete 2>/dev/null
[ -s "$log/launchd.err" ] || rm -f "$log/launchd.err"
uji=0; [ "$1" = "--uji" ] && { uji=1; shift; }
satu=0; [ $# -gt 0 ] && satu=1
json="$log/$(date +%F-%H%M).json"; html="${json%.json}.html"
kabar="${TMPDIR:-/tmp}/clint-kabar.txt"; rm -f "$kabar" "$json"

if [ "$satu" = 1 ]; then proyek="$(printf '%s\n' "$@")"; else proyek="$(bash "$root/scripts/active-projects.sh" 3)"; fi
[ -n "$proyek" ] || exit 0
kerja="$(echo "$proyek" | head -1)"
lapor(){ CLAUDE_PROJECT_DIR="$kerja" bash "$root/hooks/notify.sh" "$1"; }

claude="$(cari_claude)"
[ -n "$claude" ] || { lapor "$(t "claude tidak ditemukan. Pasang Claude Code atau tambahkan ke PATH." "claude not found. Install Claude Code or add it to PATH.")"; exit 0; }

# Satu pemeriksaan pada satu waktu (tombol terklik dua kali, sapaan pagi + klik manual).
kunci="$HOME/.config/clint/cek.lock"; mkdir -p "$HOME/.config/clint"
if ! mkdir "$kunci" 2>/dev/null; then
  if [ -n "$(find "$kunci" -maxdepth 0 -mmin -30 2>/dev/null)" ]; then
    lapor "$(t "Pemeriksaan lain masih berjalan. Laporannya menyusul." "Another check is still running. The report will follow.")"; exit 0
  fi
  rm -rf "$kunci"; mkdir "$kunci"   # kunci basi (> 30 menit) dibuang
fi
# Status untuk menu bar: file per proses, klaim develop di kerja/<sid>.json tidak disentuh.
cekf="$log/kerja/cek-$$.json"
n="$(echo "$proyek" | wc -l | tr -d ' ')"; daftar="$(echo "$proyek" | xargs -n1 basename | paste -sd, - | sed 's/,/, /g')"
jq -n --arg n "$n" --arg d "$daftar" --arg m "$(date +%H.%M)" \
  '{judul:("cek " + $n + " project"), mulai:$m, label:("cek " + $n), tahap:("memeriksa " + $d), catatan:"laporan terbuka begitu selesai"}' > "$cekf"
trap 'rm -f "$cekf"; rmdir "$kunci" 2>/dev/null' EXIT
tambah=(--add-dir "$log"); while read -r p; do tambah+=(--add-dir "$p"); done <<< "$proyek"

if [ "$uji" = 1 ]; then
  prompt="Tanpa memakai agent: tulis file $json berisi JSON contoh laporan pagi (format skill clint:status mode all) untuk project berikut, isi data contoh: $(echo $proyek). Tulis dengan tool Write."
else
  prompt="/clint:status all $(echo $proyek) --json $json --no-screen"
fi

skrip=()
cache="$(ls -d ~/.claude/plugins/cache/clint/clint/*/ 2>/dev/null | sort -V | tail -1)"
for r in "$root" "${cache%/}"; do
  [ -n "$r" ] || continue
  for s in sync-repos.sh collect-status.sh collect-changes.sh active-projects.sh; do
    skrip+=("Bash(bash $r/scripts/$s:*)" "Bash(bash \"$r/scripts/$s\":*)")
  done
  skrip+=("Bash(python3 $r/scripts/plan-status.py:*)" "Bash(python3 \"$r/scripts/plan-status.py\":*)")
done

jalan() {
  ( cd "$kerja" && CLINT_HEADLESS=1 "$claude" -p "$prompt" "${tambah[@]}" \
      --allowedTools Read Grep Glob Agent Task "Edit(~/Library/Logs/clint/**)" "Bash(git fetch:*)" "Bash(git pull:*)" \
        "Bash(git log:*)" "Bash(git -C:*)" "Bash(git status:*)" "Bash(git rev-list:*)" \
        "Bash(git worktree list:*)" "Bash(git branch:*)" "Bash(glab:*)" "Bash(gh:*)" \
        "Bash(df:*)" "Bash(ls:*)" "Bash(grep:*)" "Bash(sed:*)" "Bash(jq:*)" "Bash(cat:*)" \
        "Bash(head:*)" "Bash(tail:*)" "Bash(wc:*)" "Bash(printf:*)" "Bash(date:*)" "${skrip[@]}" \
      --disallowedTools "Bash(git push:*)" "Bash(git commit:*)" "Bash(git reset:*)" \
      < /dev/null > "${json%.json}.log" 2>&1 )
}

jalan
# Login kedaluwarsa sering pulih sendiri setelah token disegarkan: coba sekali lagi.
if [ ! -s "$json" ] && grep -qi "authenticate\|oauth\|login" "${json%.json}.log" 2>/dev/null; then
  sleep 20; jalan
fi

[ -s "$json" ] && python3 "$root/scripts/update-report.py" saring "$json" >/dev/null
if [ -s "$json" ] && python3 "$root/scripts/render-report.py" "$json" "$html"; then
  open "$html"
  if [ -s "$kabar" ]; then teks="$(head -c 300 "$kabar")"; else teks="$(jq -r '.kalimat // empty' "$json")"; fi
  if [ "$satu" = 1 ]; then python3 "$root/scripts/update-report.py" merge "$json"; else cp "$json" "$log/terakhir.json"; fi
  rm -f "${json%.json}.log" "$json"
elif grep -qi "authenticate\|oauth\|login" "${json%.json}.log" 2>/dev/null; then
  teks="$(t "Pemeriksaan gagal karena login Claude perlu diperbarui. Buka Claude Code sekali, lalu coba lagi." "The check failed because the Claude login needs refreshing. Open Claude Code once, then try again.")"
else
  teks="$(t "Pemeriksaan gagal membuat laporan. Rinciannya ada di log clint." "The check could not produce a report. Details are in the clint log.")"
fi
rm -f "$kabar"
[ -n "$teks" ] && lapor "$teks"
