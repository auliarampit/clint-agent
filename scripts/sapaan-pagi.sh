#!/usr/bin/env bash
# Sapaan pagi: satu /clint:cek semua untuk seluruh project aktif (mode baca saja), lalu
# layar laporan terbuka + kalimat inti dibacakan + notifikasi, bersamaan saat laporan siap.
# Pakai: sapaan-pagi.sh [--uji]
root="$(cd "$(dirname "$0")/.." && pwd)"
claude="$(ls -d "$HOME"/.vscode/extensions/anthropic.claude-code-*-darwin-arm64 2>/dev/null | sort -V | tail -1)/resources/native-binary/claude"
[ -x "$claude" ] || claude="$(command -v claude)"
log="$HOME/Library/Logs/clint"; mkdir -p "$log"
json="$log/$(date +%F).json"; html="${json%.json}.html"
kabar="${TMPDIR:-/tmp}/clint-kabar.txt"; rm -f "$kabar" "$json"

proyek="$(bash "$root/scripts/proyek-aktif.sh" 3)"
[ -n "$proyek" ] || exit 0
kerja="$(echo "$proyek" | head -1)"
tambah=(--add-dir "$log"); while read -r p; do tambah+=(--add-dir "$p"); done <<< "$proyek"

if [ "$1" = "--uji" ]; then
  prompt="Tanpa memakai agent: tulis file $json berisi JSON contoh laporan pagi (format skill clint:cek mode semua) untuk project berikut, isi data contoh: $(echo $proyek). Tulis dengan tool Write."
else
  prompt="/clint:cek semua"
fi

( cd "$kerja" && "$claude" -p "$prompt" "${tambah[@]}" \
    --allowedTools Read Grep Glob Agent Task "Write(~/Library/Logs/clint/**)" "Edit(~/Library/Logs/clint/**)" "Bash(git fetch:*)" "Bash(git pull:*)" \
      "Bash(git log:*)" "Bash(git -C:*)" "Bash(git status:*)" "Bash(git rev-list:*)" \
      "Bash(git worktree list:*)" "Bash(git branch:*)" "Bash(glab:*)" "Bash(gh:*)" \
      "Bash(df:*)" "Bash(ls:*)" "Bash(grep:*)" "Bash(sed:*)" "Bash(jq:*)" "Bash(cat:*)" \
      "Bash(head:*)" "Bash(tail:*)" "Bash(wc:*)" "Bash(printf:*)" "Bash(date:*)" "Bash(bash:*)" "Bash(find:*)" \
    --disallowedTools "Bash(git push:*)" "Bash(git commit:*)" "Bash(git reset:*)" \
    < /dev/null > "$log/$(date +%F).log" 2>&1 )

if [ -s "$json" ] && python3 "$root/scripts/render-laporan.py" "$json" "$html"; then
  open "$html"
  [ -s "$kabar" ] || jq -r '.kalimat // empty' "$json" > "$kabar"
else
  printf '%s' "Sapaan pagi gagal membuat laporan. Lihat log clint." > "$kabar"
fi
CLAUDE_PROJECT_DIR="$kerja" bash "$root/hooks/kabar.sh"
