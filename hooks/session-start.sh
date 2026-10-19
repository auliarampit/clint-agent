#!/usr/bin/env bash
# Menyuntikkan 4 prinsip kerja, bahasa pribadi, dan status setup project ke awal setiap sesi.
ROOT="${CLAUDE_PLUGIN_ROOT}"
DIR="${CLAUDE_PROJECT_DIR:-$PWD}"
CFG="$HOME/.config/clint"

# Pindahkan konfigurasi pribadi lama (v1: saya.json berisi "nama") ke user.json, sekali.
if [ ! -f "$CFG/user.json" ] && [ -f "$CFG/saya.json" ]; then
  jq '{name: (.nama // []), language: "en"}' "$CFG/saya.json" > "$CFG/user.json" 2>/dev/null && rm -f "$CFG/saya.json"
fi

# Project yang sudah menyalin prinsip kerja ke .claude/rules/ memuatnya sendiri; jangan dobel.
ctx=""
[ -f "$DIR/.claude/rules/working-principles.md" ] || ctx="$(cat "$ROOT/kit/working-principles.md")"

lang="$(jq -r '.language // "en"' "$CFG/user.json" 2>/dev/null)"; [ -n "$lang" ] || lang="en"
[ "$lang" = "id" ] && nama="Bahasa Indonesia" || nama="English"
ctx+=$'\n\n'"Bahasa clint: ${nama} (\`${lang}\`, dari ~/.config/clint/user.json). Pakai bahasa ini untuk semua jawaban, laporan, kabar suara, dan file rencana, kecuali user meminta lain. Dokumen project lain mengikuti \`docs.language\` di .claude/clint.json. Ganti dengan \`/clint:setup language en|id\`."

if [ -f "$DIR/.claude/clint.json" ]; then
  ctx+=$'\n\nclint aktif (`.claude/clint.json`). Perintah: `/clint:status` (kondisi kerja), `/clint:develop` (kode sampai MR), `/clint:review` (tinjau), `/clint:test` (E2E), `/clint:docs` (dokumen), `/clint:release` (build/rilis), `/clint:setup` (pasang/sync/bahasa).'
else
  ctx+=$'\n\nclint belum disiapkan di project ini (`/clint:setup`).'
fi

jq -n --arg c "$ctx" '{hookSpecificOutput: {hookEventName: "SessionStart", additionalContext: $c}}'
