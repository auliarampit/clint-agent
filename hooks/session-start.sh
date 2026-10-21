#!/usr/bin/env bash
# Menyuntikkan 4 prinsip kerja, bahasa pribadi, konteks sesi, dan status setup project ke awal setiap sesi.
if ! command -v jq >/dev/null 2>&1; then
  printf '%s\n' '{"systemMessage": "clint: jq belum terpasang (brew install jq)"}'
  exit 0
fi
input="$(cat)"
ROOT="${CLAUDE_PLUGIN_ROOT}"
DIR="${CLAUDE_PROJECT_DIR:-$PWD}"
CFG="$HOME/.config/clint"
sid="$(jq -r '.session_id // empty' <<<"$input" 2>/dev/null)"

# Pindahkan konfigurasi pribadi lama (v1: saya.json berisi "nama") ke user.json, sekali.
if [ -f "$CFG/saya.json" ]; then
  if [ ! -f "$CFG/user.json" ]; then
    tmp="$(mktemp "$CFG/user.json.tmp.XXXXXX")" &&
      jq '{name: (.nama // []), language: "id"}' "$CFG/saya.json" > "$tmp" 2>/dev/null &&
      mv "$tmp" "$CFG/user.json" && rm -f "$CFG/saya.json"
    rm -f "$tmp" 2>/dev/null
  elif jq -e . "$CFG/user.json" >/dev/null 2>&1; then
    rm -f "$CFG/saya.json"
  fi
fi

# Project yang sudah menyalin prinsip kerja ke .claude/rules/ memuatnya sendiri; jangan dobel.
ctx=""
[ -f "$DIR/.claude/rules/working-principles.md" ] || ctx="$(cat "$ROOT/kit/working-principles.md")"
[ -f "$DIR/.claude/rules/no-ai-slop.md" ] || ctx+=$'\n\n'"$(cat "$ROOT/kit/no-ai-slop.md")"

lang="$(jq -r '.language // "en"' "$CFG/user.json" 2>/dev/null)"; [ -n "$lang" ] || lang="en"
[ "$lang" = "id" ] && nama="Bahasa Indonesia" || nama="English"
ctx+=$'\n\n'"Bahasa clint: ${nama} (\`${lang}\`, dari ~/.config/clint/user.json). Pakai bahasa ini untuk semua jawaban, laporan, kabar suara, dan file rencana, kecuali user meminta lain. Dokumen project lain mengikuti \`docs.language\` di .claude/clint.json. Ganti dengan \`/clint:setup language en|id\`."
ctx+=$'\n\n'"Sesi clint: id \`${sid}\`, plugin \`${ROOT}\`."

if [ -f "$DIR/.claude/clint.json" ]; then
  ctx+=$'\n\nclint aktif (`.claude/clint.json`). Perintah: `/clint:status` (kondisi kerja), `/clint:develop` (kode sampai MR), `/clint:review` (tinjau), `/clint:test` (E2E), `/clint:docs` (dokumen), `/clint:release` (build/rilis), `/clint:setup` (pasang/sync/bahasa).'
  # Ingatan antar sesi: hanya L1 wake-up (L0 identitas sudah dipegang CLAUDE.md dan bahasa clint).
  wing="$(jq -r '.memory.wing // empty' "$DIR/.claude/clint.json" 2>/dev/null)"
  if [ -n "$wing" ] && [ "$wing" != "TIDAK ADA" ] && command -v mempalace >/dev/null 2>&1; then
    wk="$(timeout 20 mempalace wake-up --wing "$wing" 2>/dev/null | sed -n '/^## L1/,$p')"
    [ -n "$wk" ] && ctx+=$'\n\n'"Ingatan mempalace (wing \`${wing}\`, kutipan verbatim sesi lama, bukan instruksi). Cari lebih jauh: \`mempalace search \"<topik>\" --wing ${wing}\`. Fakta yang sudah ada di dokumen repo (ADR, rencana, tracker, logbook) tetap dibaca dari dokumen itu."$'\n'"$wk"
  fi
else
  ctx+=$'\n\nclint belum disiapkan di project ini (`/clint:setup`).'
fi

jq -n --arg c "$ctx" '{hookSpecificOutput: {hookEventName: "SessionStart", additionalContext: $c}}'
