#!/usr/bin/env bash
# Menjalankan formatter project pada file yang baru diedit.
# Perintahnya diambil dari surfaces[].formatFile di .claude/clint.json;
# kalau file itu tidak ada atau formatFile kosong, hook diam saja.
input="$(cat)"
IFS=$'\x1f' read -r file cwd < <(jq -r '[.tool_input.file_path // "", .cwd // ""] | join("\u001f")' <<<"$input")
dir="${CLAUDE_PROJECT_DIR:-$cwd}"
cfg="$dir/.claude/clint.json"

[ -n "$file" ] && [ -f "$file" ] && [ -f "$cfg" ] || exit 0
case "$file" in *.ts|*.tsx|*.js|*.jsx|*.json|*.css|*.md|*.yaml|*.yml|*.dart|*.kt|*.swift|*.py|*.go) ;; *) exit 0 ;; esac

fdir="$(cd "$(dirname "$file")" && pwd -P)" || exit 0
file="$fdir/$(basename "$file")"

common(){ ( cd "$1" 2>/dev/null && cd "$(git rev-parse --git-common-dir 2>/dev/null)" 2>/dev/null && pwd -P ); }
# Hanya file di repo project ini (repo utama atau worktree-nya); file di repo lain tidak disentuh.
c_file="$(common "$fdir")"; c_proj="$(common "$dir")"
[ -n "$c_file" ] && [ "$c_file" = "$c_proj" ] || exit 0
base="$(git -C "$fdir" rev-parse --show-toplevel 2>/dev/null)" || exit 0

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
cd "$best_root" && bash -c "$best_cmd \"\$1\"" _ "$file" >/dev/null 2>&1
exit 0
