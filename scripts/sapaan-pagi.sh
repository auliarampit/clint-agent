#!/usr/bin/env bash
# Sapaan pagi: jalankan /clint:cek tanpa layar di tiap project, simpan laporannya,
# lalu sampaikan kalimat inti lewat notifikasi + suara. Mode baca saja.
# Pakai: sapaan-pagi.sh [--uji] <dir-project> [<dir-project> ...]
root="$(cd "$(dirname "$0")/.." && pwd)"
claude="$(ls -d "$HOME"/.vscode/extensions/anthropic.claude-code-*-darwin-arm64 2>/dev/null | sort -V | tail -1)/resources/native-binary/claude"
[ -x "$claude" ] || claude="$(command -v claude)"
log="$HOME/Library/Logs/clint"; mkdir -p "$log"

prompt="/clint:cek"
if [ "$1" = "--uji" ]; then shift; prompt="Tanpa memakai tool, tulis tepat satu kalimat: Tes sapaan pagi berhasil."; fi

for dir in "$@"; do
  [ -d "$dir" ] || continue
  out="$log/$(date +%F)-$(basename "$dir").md"
  rm -f "${TMPDIR:-/tmp}/clint-kabar.txt"
  ( cd "$dir" && "$claude" -p "$prompt" \
      --allowedTools Read Grep Glob Agent Task "Bash(git fetch:*)" "Bash(git pull:*)" \
        "Bash(git log:*)" "Bash(git -C:*)" "Bash(git status:*)" "Bash(git rev-list:*)" \
        "Bash(git worktree list:*)" "Bash(git branch:*)" "Bash(glab:*)" "Bash(gh:*)" \
        "Bash(df:*)" "Bash(ls:*)" "Bash(grep:*)" "Bash(sed:*)" "Bash(jq:*)" "Bash(cat:*)" \
        "Bash(head:*)" "Bash(tail:*)" "Bash(wc:*)" "Bash(printf:*)" \
      --disallowedTools Edit Write "Bash(git push:*)" "Bash(git commit:*)" "Bash(git reset:*)" \
      < /dev/null \
    > "$out" 2>&1 )
  if [ -s "${TMPDIR:-/tmp}/clint-kabar.txt" ]; then
    CLAUDE_PROJECT_DIR="$dir" bash "$root/hooks/kabar.sh"
  else
    CLAUDE_PROJECT_DIR="$dir" bash "$root/hooks/kabar.sh" "$(head -c 200 "$out" | tr '\n' ' ')"
  fi
done
