#!/usr/bin/env bash
# Stop hook: minta tinjauan otomatis bila sesi meninggalkan perubahan kode yang cukup besar
# dan belum ditinjau. `--mark` (alias lama `--tandai`) mencatat perubahan saat ini sebagai sudah ditinjau.
dir="${CLAUDE_PROJECT_DIR:-$PWD}"
cfg="$dir/.claude/clint.json"
[ -f "$cfg" ] || exit 0
cd "$dir" && git rev-parse --git-dir >/dev/null 2>&1 || exit 0

min="$(jq -r 'if .autoReview == false then 0 else (.autoReviewMinLines // 40) end' "$cfg")"
[ "${min:-0}" -gt 0 ] || exit 0

mark_mode=0
case "$1" in --mark|--tandai) mark_mode=1 ;; esac

if [ "$mark_mode" = 0 ]; then
  [ "${CLINT_HEADLESS:-0}" = "1" ] && exit 0
  input="$(cat)"
  IFS=$'\x1f' read -r active sid tanya < <(jq -r '[(.stop_hook_active // false | tostring), (.session_id // ""),
    ((.last_assistant_message // "") | sub("\\s+$"; "") | endswith("?") | tostring)] | join("\u001f")' <<<"$input")
  [ "$active" = "true" ] && exit 0
  [ "$tanya" = "true" ] && exit 0
  kerja="$HOME/Library/Logs/clint/kerja/$sid.json"
  [ -n "$sid" ] && [ -n "$(find "$kerja" -maxdepth 0 -mmin -180 2>/dev/null)" ] && exit 0
fi

code='\.(ts|tsx|js|jsx|mjs|cjs|dart|kt|swift|java|go|py|rb|php|cs|vue|svelte)$'
tracked=(); untracked=()
while IFS= read -r -d '' f; do [[ $f =~ $code ]] && tracked+=("$f"); done < <(git diff HEAD --name-only -z 2>/dev/null)
while IFS= read -r -d '' f; do [[ $f =~ $code ]] && untracked+=("$f"); done < <(git ls-files --others --exclude-standard -z)
mark="$(git rev-parse --git-dir)/clint-reviewed"

hash="$( { [ ${#tracked[@]} -gt 0 ] && git diff HEAD -- "${tracked[@]}"; [ ${#untracked[@]} -gt 0 ] && cat -- "${untracked[@]}"; } 2>/dev/null | shasum | cut -c1-40)"
lines="$( { [ ${#tracked[@]} -gt 0 ] && git diff HEAD --numstat -- "${tracked[@]}" | awk '{print $1+$2}'; [ ${#untracked[@]} -gt 0 ] && cat -- "${untracked[@]}" | wc -l; } 2>/dev/null | awk '{s+=$1} END {print s+0}')"

if [ "$mark_mode" = 1 ]; then echo "$hash $lines" > "$mark"; exit 0; fi

[ $(( ${#tracked[@]} + ${#untracked[@]} )) -gt 0 ] || exit 0

last_hash=""; last_lines=0
[ -f "$mark" ] && read -r last_hash last_lines < "$mark"
[ "$last_hash" = "$hash" ] && exit 0
# Sesudah tinjauan, hanya tambahan sejak tinjauan terakhir yang dihitung, supaya edit kecil
# tidak memicu tinjauan penuh lagi. Perubahan mengecil = sudah di-commit → hitung dari nol.
if [ "$lines" -ge "$last_lines" ]; then delta=$(( lines - last_lines )); else delta=$lines; fi
[ "$delta" -ge "$min" ] || exit 0

self="$(cd "$(dirname "$0")" && pwd)/stop-review.sh"
jq -n --arg r "Ada $lines baris perubahan kode yang belum ditinjau. Jalankan skill /clint:review (tanpa argumen) untuk meninjau dan memperbaikinya, lalu tandai dengan: CLAUDE_PROJECT_DIR=\"$dir\" bash \"$self\" --mark" \
  '{decision: "block", reason: $r}'
