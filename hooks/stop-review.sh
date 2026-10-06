#!/usr/bin/env bash
# Stop hook: minta tinjauan otomatis bila sesi meninggalkan perubahan kode yang cukup besar
# dan belum ditinjau. `--tandai` mencatat perubahan saat ini sebagai sudah ditinjau.
dir="${CLAUDE_PROJECT_DIR:-$PWD}"
cfg="$dir/.claude/clint.json"
[ -f "$cfg" ] || exit 0
cd "$dir" && git rev-parse --git-dir >/dev/null 2>&1 || exit 0

min="$(jq -r 'if .autoReview == false then 0 else (.autoReviewMinLines // 40) end' "$cfg")"
[ "$min" -gt 0 ] || exit 0

code='\.(ts|tsx|js|jsx|mjs|cjs|dart|kt|swift|java|go|py|rb|php|cs|vue|svelte)$'
tracked="$(git diff HEAD --name-only | grep -E "$code")"
untracked="$(git ls-files --others --exclude-standard | grep -E "$code")"
mark="$(git rev-parse --git-dir)/clint-reviewed"

hash="$( { [ -n "$tracked" ] && git diff HEAD -- $tracked; for f in $untracked; do cat "$f"; done; } 2>/dev/null | shasum | cut -c1-40)"
lines="$( { [ -n "$tracked" ] && git diff HEAD --numstat -- $tracked | awk '{print $1+$2}'; for f in $untracked; do wc -l < "$f"; done; } | awk '{s+=$1} END {print s+0}')"

if [ "$1" = "--tandai" ]; then echo "$hash $lines" > "$mark"; exit 0; fi

input="$(cat)"
[ "$(jq -r '.stop_hook_active // false' <<<"$input")" = "true" ] && exit 0
[ -n "$tracked$untracked" ] || exit 0

last_hash=""; last_lines=0
[ -f "$mark" ] && read -r last_hash last_lines < "$mark"
[ "$last_hash" = "$hash" ] && exit 0
# Sesudah tinjauan, hanya tambahan sejak tinjauan terakhir yang dihitung, supaya edit kecil
# tidak memicu tinjauan penuh lagi. Perubahan mengecil = sudah di-commit → hitung dari nol.
if [ "$lines" -ge "$last_lines" ]; then delta=$(( lines - last_lines )); else delta=$lines; fi
[ "$delta" -ge "$min" ] || exit 0

self="$(cd "$(dirname "$0")" && pwd)/stop-review.sh"
jq -n --arg r "Ada $lines baris perubahan kode yang belum ditinjau. Jalankan skill /clint:tinjau (tanpa argumen) untuk meninjau dan memperbaikinya, lalu tandai dengan: bash \"$self\" --tandai" \
  '{decision: "block", reason: $r}'
