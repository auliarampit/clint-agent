#!/usr/bin/env bash
# Menjalankan formatter project pada file yang baru diedit.
# Perintahnya diambil dari surfaces[].formatFile di .claude/clint.json;
# kalau file itu tidak ada atau formatFile kosong, hook diam saja.
input="$(cat)"
file="$(jq -r '.tool_input.file_path // empty' <<<"$input")"
dir="${CLAUDE_PROJECT_DIR:-$(jq -r '.cwd // empty' <<<"$input")}"
cfg="$dir/.claude/clint.json"

[ -n "$file" ] && [ -f "$file" ] && [ -f "$cfg" ] || exit 0

file="$(cd "$(dirname "$file")" && pwd -P)/$(basename "$file")"

# File bisa berada di worktree di luar folder project: root surface dihitung
# dari repo git tempat file itu berada, bukan dari folder project.
base="$(git -C "$(dirname "$file")" rev-parse --show-toplevel 2>/dev/null || echo "$dir")"
case "$file" in *.ts|*.tsx|*.js|*.jsx|*.json|*.css|*.md|*.yaml|*.yml) ;; *) exit 0 ;; esac

# Pilih surface dengan root terpanjang yang menjadi prefix path file.
best_root=""; best_cmd=""
while IFS=$'\t' read -r root cmd; do
  [ -n "$cmd" ] || continue
  abs="$(cd "$base/$root" 2>/dev/null && pwd -P)" || continue
  case "$file" in "$abs"/*)
    if [ ${#abs} -gt ${#best_root} ]; then best_root="$abs"; best_cmd="$cmd"; fi ;;
  esac
done < <(jq -r '.surfaces[]? | [.root, (.formatFile // "")] | @tsv' "$cfg")

[ -n "$best_cmd" ] || exit 0
cd "$best_root" && $best_cmd "$file" >/dev/null 2>&1
exit 0
